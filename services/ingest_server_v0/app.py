from __future__ import annotations

import glob
import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    # Stable JSON for hashing/idempotency comparisons
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _db_path() -> Path:
    # Default local capture authority file; override via IAM_DB_PATH.
    return Path(os.environ.get("IAM_DB_PATH", "./iam.db")).expanduser().resolve()


def _migrations_dir() -> Path:
    # Default; override via IAM_MIGRATIONS_DIR if you keep migrations elsewhere.
    return Path(os.environ.get("IAM_MIGRATIONS_DIR", "./Migrations")).expanduser().resolve()


@dataclass(frozen=True)
class CaptureTable:
    name: str
    has_seq: bool
    has_envelope_json: bool
    has_envelope_hash: bool
    has_received_at: bool
    has_created_at: bool


def _connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn


def _apply_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> None:
    """
    Best-effort bootstrap: if migrations exist, apply them in lexical order.
    Safe to re-run if migrations are idempotent / guarded with IF NOT EXISTS.
    """
    if not migrations_dir.exists():
        return

    files = sorted(glob.glob(str(migrations_dir / "*.sql")))
    if not files:
        return

    for fp in files:
        sql = Path(fp).read_text(encoding="utf-8")
        if sql.strip():
            conn.executescript(sql)


def _table_columns(conn: sqlite3.Connection, table: str) -> Dict[str, str]:
    cols: Dict[str, str] = {}
    for r in conn.execute(f"PRAGMA table_info({table});").fetchall():
        cols[str(r["name"])] = str(r["type"] or "")
    return cols


def _discover_capture_table(conn: sqlite3.Connection) -> CaptureTable:
    """
    Discover the capture table by schema inspection.

    Preference order:
      1) capture_events
      2) capture
      3) first table containing a 'client_lui_id' column

    This avoids hardcoding your schema name while still honoring
    LI/ingest invariants (append-only, idempotent, ordered).
    """
    tables = [str(r["name"]) for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()]

    def score(table: str) -> int:
        cols = _table_columns(conn, table)
        if "client_lui_id" not in cols:
            return -10_000
        s = 0
        if table == "capture_events":
            s += 1000
        if table == "capture":
            s += 900
        if "seq" in cols:
            s += 50
        if "envelope_json" in cols:
            s += 50
        if "envelope_hash" in cols:
            s += 20
        return s

    candidates = sorted(tables, key=score, reverse=True)
    if not candidates or score(candidates[0]) < 0:
        # No usable table exists: create a minimal capture table that matches
        # your LI invariants and can be migrated later.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS capture_events (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              client_lui_id TEXT NOT NULL UNIQUE,
              captured_at TEXT NOT NULL,
              envelope_json TEXT NOT NULL,
              envelope_hash TEXT NOT NULL,
              received_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_capture_events_captured_at
              ON capture_events(captured_at);
            """
        )
        return CaptureTable(
            name="capture_events",
            has_seq=True,
            has_envelope_json=True,
            has_envelope_hash=True,
            has_received_at=True,
            has_created_at=False,
        )

    table = candidates[0]
    cols = _table_columns(conn, table)
    return CaptureTable(
        name=table,
        has_seq=("seq" in cols) or ("id" in cols),
        has_envelope_json=("envelope_json" in cols),
        has_envelope_hash=("envelope_hash" in cols),
        has_received_at=("received_at" in cols),
        has_created_at=("created_at" in cols),
    )


def _select_existing(conn: sqlite3.Connection, t: CaptureTable, client_lui_id: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        f"SELECT * FROM {t.name} WHERE client_lui_id = ?;",
        (client_lui_id,),
    ).fetchone()


def _capture_id_from_row(row: sqlite3.Row) -> Tuple[str, int]:
    # Prefer seq, fallback to id/rowid.
    if "seq" in row.keys():
        return "seq", int(row["seq"])
    if "id" in row.keys():
        return "id", int(row["id"])
    # SQLite rowid always exists for ordinary tables; best-effort
    return "rowid", int(row["rowid"])  # type: ignore[index]


def _insert_capture(
    conn: sqlite3.Connection,
    t: CaptureTable,
    *,
    client_lui_id: str,
    captured_at: str,
    envelope_json: str,
    envelope_hash: str,
    received_at: str,
) -> None:
    """
    Append-only insert. No updates.
    We use INSERT OR IGNORE and then check existence to enforce replay semantics.
    """
    cols = _table_columns(conn, t.name)

    # Build a safe INSERT for only the columns that exist.
    fields = []
    values = []
    params = []

    def add(field: str, value: Any) -> None:
        if field in cols:
            fields.append(field)
            values.append("?")
            params.append(value)

    add("client_lui_id", client_lui_id)
    add("captured_at", captured_at)
    add("envelope_json", envelope_json)
    add("envelope_hash", envelope_hash)
    add("received_at", received_at)
    add("created_at", received_at)  # fallback if schema uses created_at

    if not fields:
        raise RuntimeError(f"Capture table {t.name} has no writable columns")

    sql = f"INSERT OR IGNORE INTO {t.name} ({', '.join(fields)}) VALUES ({', '.join(values)});"
    conn.execute(sql, tuple(params))


# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------

app = FastAPI(
    title="IAM Ingest Server v0 (iam.db writer)",
    version="0.1",
    description=(
        "Minimal ingest boundary that appends LUIs into capture authority (iam.db).\n"
        "Implements append-only + idempotent replay semantics.\n"
        "Bootstrap: missing/empty iam.db is valid."
    ),
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/luis")
async def ingest_lui(request: Request):
    """
    Accept a single canonical LUI envelope and append it to iam.db.

    Behavior (LI/ingest invariants):
      - Append-only: never rewrite existing capture rows
      - Idempotent: replay w/ same client_lui_id + same content => 200
      - Conflict: replay w/ same client_lui_id + different content => 409
      - Ordering surface: autoincrement seq (or equivalent) establishes monotonic order
      - Bootstrap: if iam.db missing/empty, initialize schema and accept first record
    """
    try:
        envelope = await request.json()
        if not isinstance(envelope, dict):
            raise ValueError("JSON object required")
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_JSON", "message": "Request must be a JSON object"}},
        )

    client_lui_id = envelope.get("client_lui_id")
    captured_at = envelope.get("captured_at")

    if not isinstance(client_lui_id, str) or not client_lui_id.strip():
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "MISSING_CLIENT_LUI_ID", "message": "client_lui_id is required"}},
        )
    if not isinstance(captured_at, str) or not captured_at.strip():
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "MISSING_CAPTURED_AT", "message": "captured_at is required"}},
        )

    received_at = _utc_now_iso()

    # Canonicalize for stable replay comparison
    envelope_json = _canonical_json(envelope)
    envelope_hash = _sha256_hex(envelope_json)

    db = _db_path()
    mig_dir = _migrations_dir()

    conn = _connect(db)
    try:
        # Bootstrap: apply migrations if present; otherwise create minimal capture table on demand
        _apply_migrations(conn, mig_dir)
        t = _discover_capture_table(conn)

        conn.execute("BEGIN;")
        try:
            _insert_capture(
                conn,
                t,
                client_lui_id=client_lui_id,
                captured_at=captured_at,
                envelope_json=envelope_json,
                envelope_hash=envelope_hash,
                received_at=received_at,
            )
            conn.execute("COMMIT;")
        except Exception:
            conn.execute("ROLLBACK;")
            raise

        existing = _select_existing(conn, t, client_lui_id)
        if existing is None:
            return JSONResponse(
                status_code=500,
                content={"error": {"code": "INGEST_FAILED", "message": "capture row not found after insert"}},
            )

        # Replay/Conflict logic
        existing_hash = None
        if "envelope_hash" in existing.keys() and existing["envelope_hash"] is not None:
            existing_hash = str(existing["envelope_hash"])
        elif "envelope_json" in existing.keys() and existing["envelope_json"] is not None:
            existing_hash = _sha256_hex(str(existing["envelope_json"]))

        if existing_hash != envelope_hash:
            # Conflict: same key, different content. No rewrite.
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "code": "CONFLICT",
                        "message": "client_lui_id replay content differs from stored capture record",
                    },
                    "client_lui_id": client_lui_id,
                },
            )

        id_field, cap_id = _capture_id_from_row(existing)
        return {
            "status": "ok",
            "client_lui_id": client_lui_id,
            "capture_id_field": id_field,
            "capture_id": cap_id,
            "received_at": received_at,
        }

    finally:
        conn.close()
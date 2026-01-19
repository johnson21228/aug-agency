# services/spooler_v0/outbox.py

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class OutboxItem:
    id: int
    client_lui_id: str
    envelope_json: str
    envelope_bytes: int


class OutboxError(Exception):
    pass


class CapacityError(OutboxError):
    pass


class ConflictError(OutboxError):
    pass


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_outbox(db_path: Path) -> None:
    conn = _connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS outbox_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              client_lui_id TEXT NOT NULL UNIQUE,
              envelope_json TEXT NOT NULL,
              envelope_bytes INTEGER NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              last_attempt_at TEXT,
              attempt_count INTEGER NOT NULL DEFAULT 0,
              last_error TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_outbox_status_id ON outbox_events(status, id);
            """
        )
        conn.commit()
    finally:
        conn.close()


def _stats(conn: sqlite3.Connection) -> Tuple[int, int]:
    row = conn.execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(envelope_bytes),0) AS b FROM outbox_events WHERE status='queued';"
    ).fetchone()
    return int(row["n"]), int(row["b"])


def enqueue(
    db_path: Path,
    *,
    envelope: Dict[str, Any],
    envelope_json: str,
    envelope_bytes: int,
    max_envelope_bytes: int,
    outbox_max_items: int,
    outbox_max_bytes: int,
) -> None:
    if envelope_bytes > max_envelope_bytes:
        raise CapacityError(f"Envelope too large: {envelope_bytes} > {max_envelope_bytes}")

    client_lui_id = envelope.get("client_lui_id")
    if not client_lui_id:
        raise OutboxError("client_lui_id required")

    conn = _connect(db_path)
    try:
        n, b = _stats(conn)
        if n >= outbox_max_items:
            raise CapacityError(f"Outbox item capacity reached: {n} >= {outbox_max_items}")
        if b + envelope_bytes > outbox_max_bytes:
            raise CapacityError(f"Outbox byte capacity reached: {b}+{envelope_bytes} > {outbox_max_bytes}")

        conn.execute("BEGIN;")
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO outbox_events
                  (client_lui_id, envelope_json, envelope_bytes, status, created_at)
                VALUES (?, ?, ?, 'queued', ?);
                """,
                (client_lui_id, envelope_json, envelope_bytes, _utc_now_iso()),
            )

            row = conn.execute(
                "SELECT envelope_json FROM outbox_events WHERE client_lui_id=?;",
                (client_lui_id,),
            ).fetchone()
            if not row:
                raise OutboxError("Failed to enqueue or locate outbox item")

            stored = str(row["envelope_json"])
            if stored != envelope_json:
                conn.execute(
                    "UPDATE outbox_events SET status='conflict', last_error=? WHERE client_lui_id=?;",
                    ("client_lui_id replay content differs", client_lui_id),
                )
                conn.execute("COMMIT;")
                raise ConflictError("client_lui_id replay content differs from stored envelope")

            conn.execute("COMMIT;")
        except Exception:
            # Conflict path commits before raising; after COMMIT there is no active txn.
            try:
                conn.execute("ROLLBACK;")
            except sqlite3.OperationalError:
                pass
            raise
    finally:
        conn.close()


def fetch_batch(db_path: Path, batch_size: int) -> List[OutboxItem]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, client_lui_id, envelope_json, envelope_bytes
            FROM outbox_events
            WHERE status='queued'
            ORDER BY id ASC
            LIMIT ?;
            """,
            (batch_size,),
        ).fetchall()
        return [
            OutboxItem(
                id=int(r["id"]),
                client_lui_id=str(r["client_lui_id"]),
                envelope_json=str(r["envelope_json"]),
                envelope_bytes=int(r["envelope_bytes"]),
            )
            for r in rows
        ]
    finally:
        conn.close()


def mark_attempt(db_path: Path, ids: List[int], err: Optional[str] = None) -> None:
    if not ids:
        return
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN;")
        for _id in ids:
            conn.execute(
                """
                UPDATE outbox_events
                SET last_attempt_at=?, attempt_count=attempt_count+1, last_error=?
                WHERE id=?;
                """,
                (_utc_now_iso(), err, _id),
            )
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise
    finally:
        conn.close()


def ack(db_path: Path, ids: List[int]) -> int:
    if not ids:
        return 0
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN;")
        q = ",".join(["?"] * len(ids))
        cur = conn.execute(f"DELETE FROM outbox_events WHERE id IN ({q});", tuple(ids))
        conn.execute("COMMIT;")
        return int(cur.rowcount)
    except Exception:
        conn.execute("ROLLBACK;")
        raise
    finally:
        conn.close()


def queued_count(db_path: Path) -> int:
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) FROM outbox_events WHERE status='queued';").fetchone()
        return int(row[0])
    finally:
        conn.close()


def peek_queued(
    db_path: Path,
    *,
    limit: int = 10,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Read-only inspection of queued items. Does not mutate state.
    Returns metadata plus the stored envelope_json for each item.
    """
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    if offset < 0:
        offset = 0

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
              id,
              client_lui_id,
              envelope_json,
              envelope_bytes,
              status,
              created_at,
              last_attempt_at,
              attempt_count,
              last_error
            FROM outbox_events
            WHERE status='queued'
            ORDER BY id ASC
            LIMIT ? OFFSET ?;
            """,
            (limit, offset),
        ).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "id": int(r["id"]),
                    "client_lui_id": str(r["client_lui_id"]),
                    "envelope_json": str(r["envelope_json"]),
                    "envelope_bytes": int(r["envelope_bytes"]),
                    "status": str(r["status"]),
                    "created_at": str(r["created_at"]),
                    "last_attempt_at": r["last_attempt_at"],
                    "attempt_count": int(r["attempt_count"]),
                    "last_error": r["last_error"],
                }
            )
        return out
    finally:
        conn.close()
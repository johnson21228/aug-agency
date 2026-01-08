#!/usr/bin/env python3
"""
ingest_chatgpt_export.py

ChatGPT Export → IAM Capture Adapter

GOVERNING BEHAVIOR
------------------
- Raw ChatGPT exports are treated as *inputs*, not repo artifacts.
- The authoritative record is iam.db (capture tables).
- Raw exports MUST NOT be committed to the repo.

REPO CONVENTION
---------------
By default, this adapter looks for ChatGPT export zips in:

    data/inbox/chatGPT/

This directory is expected to be gitignored.
Users may simply drop their export zip there and run the script.

INPUT RESOLUTION ORDER
----------------------
1) If --in is provided:
     - Use that file or directory explicitly.
2) Else:
     - Scan --inbox (default: data/inbox/chatGPT/)
     - Select the newest *.zip (mtime, tie-break by name)

This keeps ingestion deterministic while avoiding hard-coded personal paths.

CAPTURE INVARIANTS
------------------
- Append-only writes to iam.db
- Idempotent ingestion (no duplicates on re-run)
- No semantic processing
- Full raw payload preserved (opaque JSON)
"""

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SOURCE_TYPE = "chatgpt_export"
DEFAULT_INBOX = Path("data/inbox/chatGPT")


# ---------- Utilities ----------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    """
    Deterministic JSON bytes for hashing + storage.
    Sorting keys + compact separators ensures stability.
    """
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


# ---------- Input resolution ----------

def resolve_input(inp: Optional[Path], inbox: Path) -> Path:
    """
    Resolve the ChatGPT export source according to the rules:

    1) Explicit --in wins
    2) Else: pick newest *.zip from inbox
    """
    if inp is not None:
        if not inp.exists():
            raise FileNotFoundError(f"--in path does not exist: {inp}")
        return inp

    if not inbox.exists():
        raise FileNotFoundError(
            f"No --in provided and inbox does not exist: {inbox}"
        )

    zips = sorted(
        inbox.glob("*.zip"),
        key=lambda p: (p.stat().st_mtime, p.name),
        reverse=True,
    )

    if not zips:
        raise FileNotFoundError(
            f"No ChatGPT export zip found in inbox: {inbox}"
        )

    return zips[0]


def extract_if_zip(src: Path) -> Path:
    """
    If src is a zip, extract to a temp directory and return that path.
    If src is a directory, return it unchanged.
    """
    if src.is_dir():
        return src

    if src.suffix.lower() == ".zip":
        tmp = Path(tempfile.mkdtemp(prefix="chatgpt_export_"))
        with zipfile.ZipFile(src, "r") as z:
            z.extractall(tmp)
        return tmp

    raise ValueError(f"Unsupported input type: {src}")


def find_conversations_json(root: Path) -> Path:
    """
    Locate conversations.json within the extracted export.
    """
    candidates = sorted(root.rglob("conversations.json"), key=lambda p: len(p.parts))
    if not candidates:
        raise FileNotFoundError("Could not find conversations.json in export")
    return candidates[0]


# ---------- ChatGPT parsing helpers ----------

def role_to_actor_type(role: str) -> str:
    r = (role or "").lower()
    if r == "user":
        return "human"
    if r == "assistant":
        return "assistant"
    if r in ("system", "tool"):
        return "system"
    return "system"


def observed_ts_from_message(msg: Dict[str, Any]) -> Optional[str]:
    ct = msg.get("create_time")
    if ct is None:
        return None
    try:
        return datetime.fromtimestamp(float(ct), tz=timezone.utc).isoformat(
            timespec="seconds"
        )
    except Exception:
        return None


def message_text_parts(message: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Extract non-authoritative text parts for convenience.
    Raw payload is stored separately and remains authoritative.
    """
    content = (message or {}).get("content") or {}
    parts = content.get("parts")

    out: List[Tuple[str, str]] = []

    if isinstance(parts, list):
        for p in parts:
            if p is not None:
                out.append(("text/plain", str(p)))
        return out

    if isinstance(content, str):
        return [("text/plain", content)]

    # Unknown structure: preserve as JSON
    return [("application/json", json.dumps(content, ensure_ascii=False, sort_keys=True))]


def iter_message_nodes(conversation: Dict[str, Any]):
    mapping = conversation.get("mapping") or {}
    for node_id, node in mapping.items():
        msg = (node or {}).get("message")
        if msg:
            yield str(node_id), node


# ---------- Database helpers ----------

def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_capture_schema(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    tables = {r[0] for r in rows}
    required = {"capture_events", "capture_payload_parts"}
    missing = required - tables
    if missing:
        raise RuntimeError(
            f"iam.db missing capture schema tables: {sorted(missing)}. "
            "Apply Migrations/0001_capture_contract.sql first."
        )


def insert_capture_event(
    conn: sqlite3.Connection,
    *,
    source_ref: str,
    source_event_key: Optional[str],
    actor_type: str,
    observed_ts: Optional[str],
    payload_kind: str,
    payload_hash: Optional[str],
) -> Optional[int]:
    """
    Insert capture event idempotently.
    Returns capture_id (existing or inserted).
    """
    conn.execute(
        """
        INSERT OR IGNORE INTO capture_events
          (source_type, source_ref, source_event_key,
           actor_type, observed_ts, ingested_ts,
           payload_kind, payload_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            SOURCE_TYPE,
            source_ref,
            source_event_key,
            actor_type,
            observed_ts,
            utc_now_iso(),
            payload_kind,
            payload_hash,
        ),
    )

    if source_event_key is not None:
        row = conn.execute(
            """
            SELECT capture_id FROM capture_events
            WHERE source_type=? AND source_ref=? AND source_event_key=?
            """,
            (SOURCE_TYPE, source_ref, source_event_key),
        ).fetchone()
        return int(row[0]) if row else None

    if payload_hash is None:
        return None

    row = conn.execute(
        """
        SELECT capture_id FROM capture_events
        WHERE source_type=? AND source_ref=? AND source_event_key IS NULL
          AND payload_hash=? AND observed_ts IS ?
        """,
        (SOURCE_TYPE, source_ref, payload_hash, observed_ts),
    ).fetchone()
    return int(row[0]) if row else None


def insert_payload_parts(
    conn: sqlite3.Connection,
    capture_id: int,
    parts: List[Tuple[str, str]],
) -> None:
    for idx, (mime, text) in enumerate(parts):
        conn.execute(
            """
            INSERT OR IGNORE INTO capture_payload_parts
              (capture_id, part_index, mime_type, text)
            VALUES (?, ?, ?, ?)
            """,
            (capture_id, idx, mime, text),
        )


# ---------- Main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to iam.db")
    ap.add_argument("--in", dest="inp", help="Explicit path to ChatGPT export zip or directory")
    ap.add_argument(
        "--inbox",
        help=f"Directory inbox for ChatGPT exports (default: {DEFAULT_INBOX})",
        default=str(DEFAULT_INBOX),
    )
    args = ap.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    inbox = Path(args.inbox).expanduser().resolve()
    inp = Path(args.inp).expanduser().resolve() if args.inp else None

    src = resolve_input(inp, inbox)
    root = extract_if_zip(src)

    conversations_path = find_conversations_json(root)
    conversations = json.loads(conversations_path.read_text(encoding="utf-8"))

    conn = open_db(db_path)
    ensure_capture_schema(conn)

    ingested = 0

    for conv in conversations:
        conv_id = conv.get("id") or conv.get("conversation_id")
        if not conv_id:
            continue

        source_ref = str(conv_id)

        nodes = []
        for node_id, node in iter_message_nodes(conv):
            msg = (node or {}).get("message") or {}
            ots = observed_ts_from_message(msg)
            nodes.append((ots, node_id, node))

        nodes.sort(key=lambda t: ((t[0] is None), (t[0] or ""), t[1]))

        for observed_ts, node_id, node in nodes:
            msg = (node or {}).get("message") or {}
            role = (msg.get("author") or {}).get("role") or ""
            actor_type = role_to_actor_type(role)

            raw_bytes = canonical_json_bytes(msg)
            payload_hash = sha256_hex(raw_bytes)

            parts = [("application/json", raw_bytes.decode("utf-8"))]
            parts.extend(message_text_parts(msg))

            capture_id = insert_capture_event(
                conn=conn,
                source_ref=source_ref,
                source_event_key=node_id,
                actor_type=actor_type,
                observed_ts=observed_ts,
                payload_kind="multipart",
                payload_hash=payload_hash,
            )
            if capture_id is None:
                continue

            insert_payload_parts(conn, capture_id, parts)
            ingested += 1

    conn.commit()
    conn.close()

    print(f"Ingested (idempotent) events: {ingested}")


if __name__ == "__main__":
    main()

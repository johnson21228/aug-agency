#!/usr/bin/env python3
"""
ingest_chatgpt_export.py (Capture Adapter)

Ingest a ChatGPT export (zip or directory) into iam.db capture schema:

- capture_events
- capture_payload_parts

Append-only + idempotent by (source_type, source_ref, source_event_key).
No semantic processing.
No derived tables.
"""

import argparse
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SOURCE_TYPE = "chatgpt_export"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find_conversations_json(root: Path) -> Path:
    # Typical export has conversations.json at root; allow nested.
    candidates = []
    for p in root.rglob("conversations.json"):
        candidates.append(p)
    if not candidates:
        raise FileNotFoundError("Could not find conversations.json in export.")
    # Prefer the shallowest path
    candidates.sort(key=lambda p: len(p.parts))
    return candidates[0]


def extract_if_zip(src: Path) -> Path:
    if src.is_dir():
        return src
    if src.suffix.lower() == ".zip":
        tmp = Path(tempfile.mkdtemp(prefix="chatgpt_export_"))
        with zipfile.ZipFile(src, "r") as z:
            z.extractall(tmp)
        return tmp
    raise ValueError("Input must be a directory or a .zip file")


def role_to_actor_type(role: str) -> str:
    r = (role or "").lower()
    if r == "user":
        return "human"
    if r == "assistant":
        return "assistant"
    # chat exports may contain "system"/"tool"
    if r in ("system", "tool"):
        return "system"
    return "system"


def message_text_parts(message: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Returns list of (mime_type, text) parts in stable order.
    """
    content = (message or {}).get("content") or {}
    ctype = content.get("content_type")
    parts = content.get("parts")

    out: List[Tuple[str, str]] = []
    if isinstance(parts, list):
        # Most common: parts is list of strings
        for s in parts:
            if s is None:
                continue
            out.append(("text/plain", str(s)))
        return out

    # Fallback: if content is string-like
    if isinstance(content, str):
        out.append(("text/plain", content))
        return out

    # Unknown structure: store JSON
    out.append(("application/json", json.dumps(content, ensure_ascii=False)))
    return out


def iter_nodes(conversation: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    mapping = conversation.get("mapping") or {}
    for node_id, node in mapping.items():
        yield node_id, node


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_capture_schema(conn: sqlite3.Connection) -> None:
    # Fail fast if schema missing (migration not applied)
    required = {"capture_events", "capture_payload_parts"}
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    existing = {r[0] for r in rows}
    missing = required - existing
    if missing:
        raise RuntimeError(
            f"iam.db missing capture schema tables: {sorted(missing)}. "
            "Apply migrations/0001_capture_contract.sql first."
        )


def insert_capture_event(
    conn: sqlite3.Connection,
    source_ref: str,
    source_event_key: str,
    actor_type: str,
    observed_ts: Optional[str],
    payload_kind: str = "multipart",
) -> Optional[int]:
    """
    Insert capture event idempotently. Returns capture_id if inserted or existing.
    """
    # Insert (idempotent)
    conn.execute(
        """
        INSERT OR IGNORE INTO capture_events
          (source_type, source_ref, source_event_key, actor_type, observed_ts, ingested_ts, payload_kind)
        VALUES
          (?, ?, ?, ?, ?, ?, ?)
        """,
        (SOURCE_TYPE, source_ref, source_event_key, actor_type, observed_ts, utc_now_iso(), payload_kind),
    )
    # Fetch capture_id (existing or inserted)
    row = conn.execute(
        """
        SELECT capture_id FROM capture_events
        WHERE source_type=? AND source_ref=? AND source_event_key=?
        """,
        (SOURCE_TYPE, source_ref, source_event_key),
    ).fetchone()
    return int(row[0]) if row else None


def insert_payload_parts(conn: sqlite3.Connection, capture_id: int, parts: List[Tuple[str, str]]) -> None:
    for idx, (mime, text) in enumerate(parts):
        conn.execute(
            """
            INSERT OR IGNORE INTO capture_payload_parts
              (capture_id, part_index, mime_type, text)
            VALUES
              (?, ?, ?, ?)
            """,
            (capture_id, idx, mime, text),
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Path to ChatGPT export (.zip or directory)")
    ap.add_argument("--db", dest="db", required=True, help="Path to iam.db")
    args = ap.parse_args()

    src = Path(args.inp).expanduser().resolve()
    db_path = Path(args.db).expanduser().resolve()

    root = extract_if_zip(src)
    conversations_path = find_conversations_json(root)

    conversations = json.loads(conversations_path.read_text(encoding="utf-8"))

    conn = open_db(db_path)
    ensure_capture_schema(conn)

    # conversations.json is typically a list
    if not isinstance(conversations, list):
        raise ValueError("Unexpected conversations.json structure (expected list).")

    ingested = 0
    for conv in conversations:
        conv_id = conv.get("id") or conv.get("conversation_id")
        if not conv_id:
            continue

        for node_id, node in iter_nodes(conv):
            msg = node.get("message")
            if not msg:
                continue

            author = msg.get("author") or {}
            role = author.get("role") or ""
            actor_type = role_to_actor_type(role)

            # observed timestamp: best-effort
            observed_ts = None
            # exports can include create_time as float seconds
            ct = msg.get("create_time")
            try:
                if ct is not None:
                    observed_ts = datetime.fromtimestamp(float(ct), tz=timezone.utc).isoformat(timespec="seconds")
            except Exception:
                observed_ts = None

            capture_id = insert_capture_event(
                conn=conn,
                source_ref=str(conv_id),
                source_event_key=str(node_id),
                actor_type=actor_type,
                observed_ts=observed_ts,
                payload_kind="multipart",
            )
            if capture_id is None:
                continue

            parts = message_text_parts(msg)
            insert_payload_parts(conn, capture_id, parts)
            ingested += 1

    conn.commit()
    conn.close()
    print(f"Ingested (idempotent) messages processed: {ingested}")


if __name__ == "__main__":
    main()

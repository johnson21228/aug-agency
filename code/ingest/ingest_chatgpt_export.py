#!/usr/bin/env python3
"""
ingest_chatgpt_export.py (Capture Adapter)

Ingest a ChatGPT export (zip or directory) into iam.db capture schema:

- capture_events
- capture_payload_parts

Append-only + idempotent:
- Preferred: (source_type, source_ref, source_event_key)
- Fallback: (source_type, source_ref, payload_hash, observed_ts) when source_event_key is absent

No semantic processing.
No derived tables.
Preserve raw payloads (opaque) + extracted text parts as non-authoritative convenience.
"""

import argparse
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SOURCE_TYPE = "chatgpt_export"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    # Deterministic bytes for hashing + storage
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def find_conversations_json(root: Path) -> Path:
    candidates = sorted(root.rglob("conversations.json"), key=lambda p: len(p.parts))
    if not candidates:
        raise FileNotFoundError("Could not find conversations.json in export.")
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
    if r in ("system", "tool"):
        return "system"
    return "system"


def observed_ts_from_message(msg: Dict[str, Any]) -> Optional[str]:
    ct = msg.get("create_time")
    if ct is None:
        return None
    try:
        return datetime.fromtimestamp(float(ct), tz=timezone.utc).isoformat(timespec="seconds")
    except Exception:
        return None


def message_text_parts(message: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Non-authoritative extraction of text-bearing parts in stable order.
    Raw payload is stored separately and remains authoritative.
    """
    content = (message or {}).get("content") or {}
    parts = content.get("parts")

    out: List[Tuple[str, str]] = []
    if isinstance(parts, list):
        for s in parts:
            if s is None:
                continue
            out.append(("text/plain", str(s)))
        return out

    if isinstance(content, str):
        return [("text/plain", content)]

    # Unknown structure: preserve content as JSON (still non-authoritative vs raw msg)
    return [("application/json", json.dumps(content, ensure_ascii=False, sort_keys=True))]


def iter_message_nodes(conversation: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    mapping = conversation.get("mapping") or {}
    for node_id, node in mapping.items():
        msg = (node or {}).get("message")
        if msg:
            yield str(node_id), node


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_capture_schema(conn: sqlite3.Connection) -> None:
    required = {"capture_events", "capture_payload_parts"}
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    existing = {r[0] for r in rows}
    missing = required - existing
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
    Insert capture event idempotently. Returns capture_id for existing or inserted row.
    """
    conn.execute(
        """
        INSERT OR IGNORE INTO capture_events
          (source_type, source_ref, source_event_key, actor_type, observed_ts, ingested_ts, payload_kind, payload_hash)
        VALUES
          (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (SOURCE_TYPE, source_ref, source_event_key, actor_type, observed_ts, utc_now_iso(), payload_kind, payload_hash),
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

    # Fallback lookup (matches ux_capture_events_fallback_hash)
    if payload_hash is None:
        return None
    row = conn.execute(
        """
        SELECT capture_id FROM capture_events
        WHERE source_type=? AND source_ref=? AND source_event_key IS NULL AND payload_hash=? AND observed_ts IS ?
        """,
        (SOURCE_TYPE, source_ref, payload_hash, observed_ts),
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

    if not isinstance(conversations, list):
        raise ValueError("Unexpected conversations.json structure (expected list).")

    inserted_or_existing = 0

    for conv in conversations:
        conv_id = conv.get("id") or conv.get("conversation_id")
        if not conv_id:
            continue
        source_ref = str(conv_id)

        # Deterministic ordering for initial capture_id assignment:
        # 1) observed_ts (nulls last)
        # 2) node_id lex
        nodes: List[Tuple[Optional[str], str, Dict[str, Any]]] = []
        for node_id, node in iter_message_nodes(conv):
            msg = (node or {}).get("message") or {}
            ots = observed_ts_from_message(msg)
            nodes.append((ots, node_id, node))
        nodes.sort(key=lambda t: ((t[0] is None), (t[0] or ""), t[1]))

        for observed_ts, node_id, node in nodes:
            msg = (node or {}).get("message") or {}
            author = msg.get("author") or {}
            role = author.get("role") or ""
            actor_type = role_to_actor_type(role)

            raw_msg_bytes = canonical_json_bytes(msg)
            payload_hash = sha256_hex(raw_msg_bytes)

            # Authoritative raw payload as part 0 (opaque)
            # Non-authoritative extracted text parts follow.
            parts: List[Tuple[str, str]] = [
                ("application/json", raw_msg_bytes.decode("utf-8")),
            ]
            parts.extend(message_text_parts(msg))

            capture_id = insert_capture_event(
                conn=conn,
                source_ref=source_ref,
                source_event_key=str(node_id) if node_id else None,
                actor_type=actor_type,
                observed_ts=observed_ts,
                payload_kind="multipart",
                payload_hash=payload_hash,
            )
            if capture_id is None:
                continue

            insert_payload_parts(conn, capture_id, parts)
            inserted_or_existing += 1

    conn.commit()
    conn.close()
    print(f"Ingested (idempotent) messages (inserted or already present): {inserted_or_existing}")


if __name__ == "__main__":
    main()

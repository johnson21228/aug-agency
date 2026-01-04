#!/usr/bin/env python3
"""
ingest_chatgpt_export.py

Purpose
-------
Ingest a ChatGPT data export (zip OR unzipped folder) into a SQLite database.

Design
------
- Inbox can be messy (zip or folder). Script normalizes into a deterministic staging dir.
- Ingestion always reads from staging.
- Writes an export_manifest.json capturing provenance + schema signature.
- Idempotent by default: messages are upserted using a stable uniqueness key.

Default paths (repo-root relative)
---------------------------------
INPUT : data/inbox/chatgpt_export/
STAGE : data/staging/chatgpt_export_latest/
OUTPUT: data/artifacts/iam.db

Usage
-----
# simplest (assumes you're running from repo root)
python code/ingest/ingest_chatgpt_export.py

# explicit
python code/ingest/ingest_chatgpt_export.py \
  --inbox data/inbox/chatgpt_export \
  --staging data/staging/chatgpt_export_latest \
  --db data/artifacts/iam.db

# specify a particular export file/folder (zip or dir)
python code/ingest/ingest_chatgpt_export.py --source data/inbox/chatgpt_export/2026-01-03.zip

Notes
-----
This targets the common ChatGPT export shape where conversations live in conversations.json,
and each conversation has a "mapping" dict of nodes (message tree).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

Json = Union[dict, list, str, int, float, bool, None]


# ----------------------------
# Helpers: time, hashing, IO
# ----------------------------

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def utc_iso_from_export_ts(ts: Any) -> Optional[str]:
    """Convert export timestamps (often seconds since epoch) into ISO8601."""
    if ts is None:
        return None
    try:
        # most common: float seconds
        t = float(ts)
        return datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
    except Exception:
        pass
    if isinstance(ts, str):
        return ts
    return None

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def sha256_file(p: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def read_json(path: Path) -> Json:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def ensure_clean_dir(dirpath: Path) -> None:
    """Remove & recreate dir to guarantee deterministic staging."""
    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)

def iter_files_recursive(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            yield p


# ----------------------------
# Export discovery
# ----------------------------

_DATE_RE = re.compile(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)")

@dataclass(frozen=True)
class ExportCandidate:
    path: Path
    kind: str  # "zip" or "dir"
    date_hint: Optional[str]  # YYYY-MM-DD if parsed
    mtime: float

def parse_date_hint_from_name(name: str) -> Optional[str]:
    m = _DATE_RE.search(name)
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2), m.group(3)
    return f"{y}-{mo}-{d}"

def is_chatgpt_export_dir(p: Path) -> bool:
    """A candidate directory if it contains conversations.json somewhere within."""
    if not p.is_dir():
        return False
    # typically conversations.json is at root of export folder, but allow nested.
    return any(fp.name == "conversations.json" for fp in p.rglob("conversations.json"))

def find_conversations_json_in_dir(p: Path) -> Optional[Path]:
    # prefer top-level
    top = p / "conversations.json"
    if top.exists():
        return top
    for fp in p.rglob("conversations.json"):
        return fp
    return None

def discover_candidates(inbox_dir: Path) -> List[ExportCandidate]:
    if not inbox_dir.exists():
        return []

    candidates: List[ExportCandidate] = []
    for child in inbox_dir.iterdir():
        try:
            st = child.stat()
        except FileNotFoundError:
            continue

        if child.is_file() and child.suffix.lower() == ".zip":
            date_hint = parse_date_hint_from_name(child.name)
            candidates.append(ExportCandidate(child, "zip", date_hint, st.st_mtime))
        elif child.is_dir() and is_chatgpt_export_dir(child):
            date_hint = parse_date_hint_from_name(child.name)
            candidates.append(ExportCandidate(child, "dir", date_hint, st.st_mtime))

    return candidates

def pick_latest_candidate(candidates: List[ExportCandidate]) -> Optional[ExportCandidate]:
    if not candidates:
        return None

    def key(c: ExportCandidate):
        # Prefer parsed date; fallback to mtime
        # date sorts lexicographically as YYYY-MM-DD.
        return (c.date_hint or "", c.mtime)

    # We want the max; but date_hint "" should be lowest.
    return max(candidates, key=key)


# ----------------------------
# Normalization (zip/folder -> staging)
# ----------------------------

def normalize_to_staging(source: Path, staging_dir: Path) -> Dict[str, Any]:
    """
    Normalize the export into staging_dir.
    Returns basic provenance info (source path, type, extracted file list stats).
    """
    ensure_clean_dir(staging_dir)

    provenance: Dict[str, Any] = {
        "source_path": str(source),
        "source_kind": "zip" if source.is_file() and source.suffix.lower() == ".zip" else "dir",
        "normalized_at": now_utc_iso(),
    }

    if provenance["source_kind"] == "zip":
        with zipfile.ZipFile(source, "r") as zf:
            zf.extractall(staging_dir)
            provenance["zip_namelist_count"] = len(zf.namelist())
    else:
        shutil.copytree(source, staging_dir, dirs_exist_ok=True)

    # Locate conversations.json within staging
    conv = find_conversations_json_in_dir(staging_dir)
    if not conv:
        raise SystemExit(f"Normalization succeeded but conversations.json not found in staging: {staging_dir}")

    # If conversations.json is nested, copy it up to root for deterministic contract
    if conv.parent != staging_dir:
        shutil.copy2(conv, staging_dir / "conversations.json")
        provenance["conversations_json_copied_from"] = str(conv)

    # Optional: bring chat.html up too, if present
    chat_html = next((p for p in staging_dir.rglob("chat.html") if p.is_file()), None)
    if chat_html and chat_html.parent != staging_dir:
        shutil.copy2(chat_html, staging_dir / "chat.html")
        provenance["chat_html_copied_from"] = str(chat_html)

    # Hash conversations.json
    conv_root = staging_dir / "conversations.json"
    provenance["conversations_json_sha256"] = sha256_file(conv_root)
    provenance["staging_file_count"] = sum(1 for _ in iter_files_recursive(staging_dir))

    return provenance


# ----------------------------
# Parsing conversations.json
# ----------------------------

def normalize_conversations_root(obj: Json) -> List[dict]:
    """
    Exports vary:
      - list[conversation]
      - dict with keys like "conversations" / "data" / "items"
    """
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for k in ("conversations", "data", "items"):
            v = obj.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        return [obj]
    return []

def extract_author(message_obj: dict) -> Tuple[Optional[str], Optional[str]]:
    author = message_obj.get("author") or {}
    if not isinstance(author, dict):
        return None, None
    role = author.get("role") or author.get("type")
    name = author.get("name")
    return role, name

def extract_message_text(message_obj: dict) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Returns content_type, joined_text, parts list.
    Handles common text shapes in exports. Non-text content stays None.
    """
    content = message_obj.get("content") or {}
    if not isinstance(content, dict):
        return None, None, []

    ctype = content.get("content_type") or content.get("type")
    parts: List[str] = []

    raw_parts = content.get("parts")
    if isinstance(raw_parts, list):
        for p in raw_parts:
            if p is None:
                continue
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                t = p.get("text")
                if isinstance(t, str):
                    parts.append(t)

    if not parts:
        t = content.get("text")
        if isinstance(t, str):
            parts = [t]

    joined = "\n".join(parts) if parts else None
    return ctype, joined, parts

def extract_conversation_core(conv: dict) -> dict:
    return {
        "conversation_id": conv.get("id") or conv.get("conversation_id"),
        "title": conv.get("title"),
        "create_time": utc_iso_from_export_ts(conv.get("create_time")),
        "update_time": utc_iso_from_export_ts(conv.get("update_time")),
        "current_node": conv.get("current_node"),
        "metadata": conv.get("metadata") if isinstance(conv.get("metadata"), dict) else None,
    }

def flatten_messages_from_mapping(conv: dict) -> List[dict]:
    """
    Flatten nodes with non-null "message" from the mapping tree.
    """
    mapping = conv.get("mapping")
    if not isinstance(mapping, dict):
        return []

    out: List[dict] = []
    for node_id, node in mapping.items():
        if not isinstance(node, dict):
            continue
        msg = node.get("message")
        if not isinstance(msg, dict):
            continue

        role, name = extract_author(msg)
        ctype, joined, parts = extract_message_text(msg)

        out.append({
            "node_id": node_id,
            "message_id": msg.get("id") or node_id,
            "parent_id": node.get("parent"),
            "role": role,
            "author_name": name,
            "create_time": utc_iso_from_export_ts(msg.get("create_time") or node.get("create_time")),
            "update_time": utc_iso_from_export_ts(msg.get("update_time") or node.get("update_time")),
            "content_type": ctype,
            "text": joined,
            "parts": parts,
            "status": msg.get("status"),
            "metadata": msg.get("metadata") if isinstance(msg.get("metadata"), dict) else None,
        })

    def sort_key(m: dict):
        return (m.get("create_time") or "", m.get("message_id") or "")

    out.sort(key=sort_key)
    return out


# ----------------------------
# Schema signature (drift detection)
# ----------------------------

def build_schema_signature(conversations: List[dict], max_convs: int = 50) -> Dict[str, Any]:
    conv_keys = set()
    content_types = set()
    content_keys = set()
    author_keys = set()

    for conv in conversations[:max_convs]:
        conv_keys.update(conv.keys())
        mapping = conv.get("mapping")
        if not isinstance(mapping, dict):
            continue
        for _, node in list(mapping.items())[:200]:
            if not isinstance(node, dict):
                continue
            msg = node.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if isinstance(content, dict):
                content_types.add(content.get("content_type") or content.get("type"))
                content_keys.update(content.keys())
            author = msg.get("author")
            if isinstance(author, dict):
                author_keys.update(author.keys())

    def norm_set(s: set) -> List[str]:
        return sorted([x for x in s if isinstance(x, str) and x])

    return {
        "conversation_keys": sorted(list(conv_keys)),
        "message_content_types": norm_set(content_types),
        "message_content_keys": sorted(list(content_keys)),
        "message_author_keys": sorted(list(author_keys)),
    }


# ----------------------------
# SQLite DB
# ----------------------------

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY,
  title TEXT,
  create_time TEXT,
  update_time TEXT,
  current_node TEXT,
  metadata_json TEXT
);

-- Uniqueness: within a conversation, node_id should be stable across exports.
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  node_id TEXT NOT NULL,
  message_id TEXT,
  parent_id TEXT,
  role TEXT,
  author_name TEXT,
  create_time TEXT,
  update_time TEXT,
  content_type TEXT,
  text TEXT,
  status TEXT,
  metadata_json TEXT,
  UNIQUE(conversation_id, node_id),
  FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_messages_conv_time
ON messages(conversation_id, create_time);

CREATE TABLE IF NOT EXISTS message_content_parts (
  message_row_id INTEGER NOT NULL,
  part_index INTEGER NOT NULL,
  part_text TEXT,
  PRIMARY KEY(message_row_id, part_index),
  FOREIGN KEY(message_row_id) REFERENCES messages(id)
);
"""

def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    return conn

def upsert_conversation(conn: sqlite3.Connection, c: dict) -> None:
    conn.execute(
        """
        INSERT INTO conversations(conversation_id, title, create_time, update_time, current_node, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(conversation_id) DO UPDATE SET
          title=excluded.title,
          create_time=excluded.create_time,
          update_time=excluded.update_time,
          current_node=excluded.current_node,
          metadata_json=excluded.metadata_json
        """,
        (
            c["conversation_id"],
            c.get("title"),
            c.get("create_time"),
            c.get("update_time"),
            c.get("current_node"),
            json.dumps(c.get("metadata")) if c.get("metadata") is not None else None,
        ),
    )

def upsert_message(conn: sqlite3.Connection, conversation_id: str, m: dict) -> int:
    """
    Upsert by (conversation_id, node_id). Returns row id.
    """
    conn.execute(
        """
        INSERT INTO messages(
          conversation_id, node_id, message_id, parent_id, role, author_name,
          create_time, update_time, content_type, text, status, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(conversation_id, node_id) DO UPDATE SET
          message_id=excluded.message_id,
          parent_id=excluded.parent_id,
          role=excluded.role,
          author_name=excluded.author_name,
          create_time=excluded.create_time,
          update_time=excluded.update_time,
          content_type=excluded.content_type,
          text=excluded.text,
          status=excluded.status,
          metadata_json=excluded.metadata_json
        """,
        (
            conversation_id,
            m.get("node_id"),
            m.get("message_id"),
            m.get("parent_id"),
            m.get("role"),
            m.get("author_name"),
            m.get("create_time"),
            m.get("update_time"),
            m.get("content_type"),
            m.get("text"),
            m.get("status"),
            json.dumps(m.get("metadata")) if m.get("metadata") is not None else None,
        ),
    )

    # Fetch row id
    cur = conn.execute(
        "SELECT id FROM messages WHERE conversation_id=? AND node_id=?",
        (conversation_id, m.get("node_id")),
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError("Failed to retrieve upserted message row id.")
    return int(row[0])

def replace_parts(conn: sqlite3.Connection, message_row_id: int, parts: List[str]) -> None:
    # Replace deterministically
    conn.execute("DELETE FROM message_content_parts WHERE message_row_id=?", (message_row_id,))
    for i, p in enumerate(parts):
        conn.execute(
            "INSERT INTO message_content_parts(message_row_id, part_index, part_text) VALUES (?, ?, ?)",
            (message_row_id, i, p),
        )


# ----------------------------
# Ingestion pipeline
# ----------------------------

def ingest_conversations_json(
    conn: sqlite3.Connection,
    conversations_obj: Json,
) -> Tuple[int, int]:
    conversations = normalize_conversations_root(conversations_obj)

    conv_count = 0
    msg_count = 0

    for conv in conversations:
        ccore = extract_conversation_core(conv)
        cid = ccore.get("conversation_id")
        if not cid:
            continue

        upsert_conversation(conn, ccore)
        conv_count += 1

        msgs = flatten_messages_from_mapping(conv)
        for m in msgs:
            row_id = upsert_message(conn, cid, m)
            msg_count += 1
            parts = m.get("parts") or []
            if parts:
                replace_parts(conn, row_id, parts)

    conn.commit()
    return conv_count, msg_count


# ----------------------------
# CLI
# ----------------------------

def repo_root_from_script_location() -> Path:
    # script is expected at code/ingest/ingest_chatgpt_export.py
    return Path(__file__).resolve().parents[2]

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ChatGPT export into SQLite DB (zip or folder).")

    parser.add_argument("--repo-root", type=str, default=None, help="Repo root (defaults to script-derived).")
    parser.add_argument("--inbox", type=str, default=None, help="Inbox directory holding zips/folders.")
    parser.add_argument("--source", type=str, default=None, help="Specific zip or folder to ingest (overrides discovery).")
    parser.add_argument("--staging", type=str, default=None, help="Staging directory (normalized export).")
    parser.add_argument("--db", type=str, default=None, help="Output SQLite DB path.")
    parser.add_argument("--keep-staging", action="store_true", help="Do not delete staging dir after ingest.")
    parser.add_argument("--dry-run", action="store_true", help="Normalize + validate only; do not ingest to DB.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else repo_root_from_script_location()

    inbox_dir = Path(args.inbox).resolve() if args.inbox else (repo_root / "data" / "inbox" / "chatgpt_export")
    staging_dir = Path(args.staging).resolve() if args.staging else (repo_root / "data" / "staging" / "chatgpt_export_latest")
    db_path = Path(args.db).resolve() if args.db else (repo_root / "data" / "artifacts" / "iam.db")

    # Choose source
    source: Optional[Path] = None
    if args.source:
        source = Path(args.source).resolve()
        if not source.exists():
            raise SystemExit(f"--source not found: {source}")
    else:
        candidates = discover_candidates(inbox_dir)
        chosen = pick_latest_candidate(candidates)
        if not chosen:
            raise SystemExit(f"No export candidates found in inbox: {inbox_dir}\n"
                             f"Put a .zip or an export folder containing conversations.json there, or pass --source.")
        source = chosen.path

    # Normalize
    provenance = normalize_to_staging(source, staging_dir)
    conv_path = staging_dir / "conversations.json"
    conversations_obj = read_json(conv_path)
    conversations = normalize_conversations_root(conversations_obj)

    schema_sig = build_schema_signature(conversations)
    # Basic counts (best-effort)
    conv_count_est = len(conversations)
    msg_count_est = 0
    for conv in conversations[:200]:
        mapping = conv.get("mapping")
        if isinstance(mapping, dict):
            for _, node in mapping.items():
                if isinstance(node, dict) and isinstance(node.get("message"), dict):
                    msg_count_est += 1

    manifest = {
        "source": "chatgpt_export",
        "repo_root": str(repo_root),
        "inbox_dir": str(inbox_dir),
        "staging_dir": str(staging_dir),
        "db_path": str(db_path),
        "provenance": provenance,
        "counts_estimate": {
            "conversations": conv_count_est,
            "messages_sampled": msg_count_est,
        },
        "schema_signature": schema_sig,
        "validated_at": now_utc_iso(),
    }
    write_json(staging_dir / "export_manifest.json", manifest)

    # Validate minimum invariant
    if not conv_path.exists():
        raise SystemExit("Invariant failed: staging/conversations.json missing.")
    if conv_count_est == 0:
        raise SystemExit("Invariant failed: conversations.json parsed but yielded 0 conversations (schema mismatch?).")

    if args.dry_run:
        print("Dry run OK.")
        print(f"Source:   {source}")
        print(f"Staging:  {staging_dir}")
        print(f"DB:       {db_path} (not written)")
        print(f"Convs:    {conv_count_est:,}  (estimated messages sampled: {msg_count_est:,})")
        return

    # Ingest
    conn = connect_db(db_path)
    conv_count, msg_count = ingest_conversations_json(conn, conversations_obj)
    conn.close()

    print("Ingest complete.")
    print(f"Source:   {source}")
    print(f"Staging:  {staging_dir}")
    print(f"DB:       {db_path}")
    print(f"Inserted/Upserted conversations: {conv_count:,}")
    print(f"Inserted/Upserted messages:      {msg_count:,}")

    if not args.keep_staging:
        # Keep only manifest + conversations.json by default? Here: delete staging entirely for privacy.
        # If you prefer to keep staging, use --keep-staging.
        shutil.rmtree(staging_dir, ignore_errors=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
export_lui_packets_stage1.py

Export "LUI packets" (JSONL) from iam.db using deterministic message_canonical text.

Inputs:
- SQLite DB containing:
  - conversations
  - messages
  - message_canonical view (built during ingest/canonicalize)

Output:
- JSONL file where each line is a packet sized for Foundation Models prompt ingestion.

Design goals:
- Deterministic ordering (conversation_id, create_time, message_row_id)
- Deterministic text source (message_canonical.text, may be NULL)
- Chunked into packets limited by --max-chars (rough char budget)
- Optional inclusion of conversation titles (--include-titles)

Usage:
  python3 code/export/export_lui_packets_stage1.py \
    --db data/artifacts/iam.db \
    --out data/artifacts/lui_packets.jsonl \
    --mode final-human \
    --max-chars 24000 \
    --include-titles
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class Row:
    conversation_id: str
    message_row_id: int
    role: str
    create_time: Optional[str]
    text: Optional[str]
    text_source: str
    content_type: Optional[str]


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_view_exists(conn: sqlite3.Connection) -> None:
    # Fail fast if canonical view is missing.
    cur = conn.execute(
        "SELECT name, type FROM sqlite_master WHERE name='message_canonical' AND type IN ('view','table')"
    )
    if cur.fetchone() is None:
        raise SystemExit(
            "ERROR: message_canonical not found. Run your canonicalize step (or ingest) to build it."
        )


def iter_messages(conn: sqlite3.Connection) -> Iterable[Row]:
    # Deterministic ordering: conversation_id, create_time, message_row_id
    # create_time can be NULL; SQLite sorts NULLs first, but message_row_id remains stable.
    sql = """
    SELECT
      mc.conversation_id,
      mc.message_row_id,
      mc.role,
      mc.create_time,
      mc.text,
      mc.text_source,
      mc.content_type
    FROM message_canonical mc
    ORDER BY
      mc.conversation_id ASC,
      mc.create_time ASC,
      mc.message_row_id ASC
    """
    for r in conn.execute(sql):
        yield Row(
            conversation_id=r["conversation_id"],
            message_row_id=int(r["message_row_id"]),
            role=r["role"] or "",
            create_time=r["create_time"],
            text=r["text"],
            text_source=r["text_source"] or "none",
            content_type=r["content_type"],
        )


def get_conversation_titles(conn: sqlite3.Connection) -> Dict[str, Optional[str]]:
    titles: Dict[str, Optional[str]] = {}
    # Adjust column name if your conversations table differs.
    # Common patterns: (id, title) or (conversation_id, title)
    cols = [c["name"] for c in conn.execute("PRAGMA table_info(conversations)")]
    if "id" in cols:
        id_col = "id"
    elif "conversation_id" in cols:
        id_col = "conversation_id"
    else:
        return titles  # can't resolve; just omit titles

    title_col = "title" if "title" in cols else None
    if not title_col:
        return titles

    for r in conn.execute(f"SELECT {id_col} AS cid, {title_col} AS title FROM conversations"):
        titles[str(r["cid"])] = r["title"]
    return titles


def render_turn(mode: str, row: Row) -> str:
    """
    Convert one message row to a text turn.
    mode:
      - final-human: readable with role labels
      - raw: only text (role not included)
    """
    text = row.text
    if not text:
        return ""  # omit empty turns deterministically

    if mode == "raw":
        return text

    # final-human
    return f"{row.role}: {text}"


def pack_packets(
    rows: Iterable[Row],
    *,
    mode: str,
    max_chars: int,
    include_titles: bool,
    title_map: Dict[str, Optional[str]],
) -> Iterable[Dict[str, Any]]:
    """
    Group messages by conversation_id and chunk into packets up to max_chars.
    Packet format is intentionally simple & stable.
    """
    current_conv: Optional[str] = None
    current_title: Optional[str] = None
    buf: List[Dict[str, Any]] = []
    buf_chars = 0
    packet_index = 0

    def emit_packet(conv_id: str) -> Optional[Dict[str, Any]]:
        nonlocal buf, buf_chars, packet_index, current_title
        if not buf:
            return None
        pkt = {
            "schema": "lui.packet.stage1",
            "mode": mode,
            "conversation_id": conv_id,
            "conversation_title": current_title if include_titles else None,
            "packet_index": packet_index,
            "max_chars": max_chars,
            "turns": buf,
        }
        packet_index += 1
        buf = []
        buf_chars = 0
        return pkt

    for row in rows:
        if current_conv is None:
            current_conv = row.conversation_id
            current_title = title_map.get(current_conv)

        # Conversation boundary => flush packet buffer and reset packet counter
        if row.conversation_id != current_conv:
            pkt = emit_packet(current_conv)
            if pkt:
                yield pkt
            current_conv = row.conversation_id
            current_title = title_map.get(current_conv)
            packet_index = 0

        turn_text = render_turn(mode, row)
        if not turn_text:
            continue

        turn_obj = {
            "message_row_id": row.message_row_id,
            "role": row.role,
            "create_time": row.create_time,
            "text_source": row.text_source,
            "content_type": row.content_type,
            "text": turn_text,
        }

        # Estimate cost (very rough but deterministic)
        turn_cost = len(turn_text) + 64

        # If adding would exceed budget, flush current packet first.
        if buf and (buf_chars + turn_cost) > max_chars:
            pkt = emit_packet(current_conv)
            if pkt:
                yield pkt

        buf.append(turn_obj)
        buf_chars += turn_cost

        # If a single turn is gigantic, it will exceed max_chars; we still emit it alone.
        if buf and buf_chars > max_chars:
            pkt = emit_packet(current_conv)
            if pkt:
                yield pkt

    # flush at end
    if current_conv is not None:
        pkt = emit_packet(current_conv)
        if pkt:
            yield pkt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to iam.db")
    ap.add_argument("--out", required=True, help="Output JSONL path")
    ap.add_argument("--mode", default="final-human", choices=["final-human", "raw"])
    ap.add_argument("--max-chars", type=int, default=24000)
    ap.add_argument("--include-titles", action="store_true")
    args = ap.parse_args()

    db_path = args.db
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    conn = connect(db_path)
    try:
        ensure_view_exists(conn)
        title_map = get_conversation_titles(conn) if args.include_titles else {}
        rows = iter_messages(conn)

        n_packets = 0
        n_turns = 0
        with out_path.open("w", encoding="utf-8") as f:
            for pkt in pack_packets(
                rows,
                mode=args.mode,
                max_chars=args.max_chars,
                include_titles=args.include_titles,
                title_map=title_map,
            ):
                # Drop conversation_title if not included (keep schema stable)
                if not args.include_titles:
                    pkt.pop("conversation_title", None)
                f.write(json.dumps(pkt, ensure_ascii=False) + "\n")
                n_packets += 1
                n_turns += len(pkt["turns"])

        print("Wrote LUI packets:")
        print(f"  out: {out_path}")
        print(f"  packets: {n_packets}")
        print(f"  turns:   {n_turns}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

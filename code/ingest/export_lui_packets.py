#!/usr/bin/env python3
"""
export_lui_packets.py

Purpose
-------
Project iam.db (Stage-0 capture) into a *final-human* sequenced LUI event stream,
then pack events into prompt-sized packets suitable for Apple Foundation Models.

Key behavior
------------
- Default mode: final-human
  - Reconstructs the chosen transcript path per conversation using conversations.current_node
  - Filters to roles: user, assistant
- Fallback: if current_node is missing/unusable, falls back to all-human for that conversation
- Packs events into JSONL packets using a character budget proxy (max-chars)

Inputs
------
- SQLite DB created by ingest_chatgpt_export.py (default: data/artifacts/iam.db)

Outputs
-------
- JSONL packets file: each line is one packet:
    {"packet_id": "...", "char_budget": N, "events": [ ... ]}

Optional outputs
----------------
- Raw events JSONL (one event per line)

Usage
-----
python3 code/export/export_lui_packets.py \
  --db data/artifacts/iam.db \
  --out data/artifacts/lui_packets.jsonl \
  --mode final-human \
  --max-chars 24000 \
  --include-titles

Recommended Makefile target
---------------------------
lui-packets:
    $(PYTHON) code/export/export_lui_packets.py \
      --db data/artifacts/iam.db \
      --out data/artifacts/lui_packets.jsonl \
      --mode final-human \
      --max-chars 24000 \
      --include-titles
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HUMAN_ROLES: Tuple[str, str] = ("user", "assistant")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


@dataclass
class LuiEvent:
    lui_id: str
    conversation_id: str
    turn_index: int
    timestamp: Optional[str]
    role: str
    text: str
    title: Optional[str] = None
    # provenance (optional)
    node_id: Optional[str] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict:
        d: Dict[str, object] = {
            "lui_id": self.lui_id,
            "conversation_id": self.conversation_id,
            "turn_index": self.turn_index,
            "timestamp": self.timestamp,
            "role": self.role,
            "text": self.text,
        }
        if self.title is not None:
            d["title"] = self.title
        if self.node_id is not None:
            d["node_id"] = self.node_id
        if self.parent_id is not None:
            d["parent_id"] = self.parent_id
        return d


# ----------------------------
# Conversation + message fetch
# ----------------------------

def fetch_conversations(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT conversation_id, title, create_time, current_node
            FROM conversations
            ORDER BY create_time
            """
        )
    )


def fetch_message_row(conn: sqlite3.Connection, conversation_id: str, node_id: str) -> Optional[sqlite3.Row]:
    # node_id is unique within (conversation_id, node_id)
    return conn.execute(
        """
        SELECT id, node_id, parent_id, create_time, role, text
        FROM messages
        WHERE conversation_id = ?
          AND node_id = ?
        LIMIT 1
        """,
        (conversation_id, node_id),
    ).fetchone()


def fetch_all_human_messages(conn: sqlite3.Connection, conversation_id: str) -> List[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT id, node_id, parent_id, create_time, role, text
            FROM messages
            WHERE conversation_id = ?
              AND role IN ('user','assistant')
              AND text IS NOT NULL AND text != ''
            ORDER BY create_time, id
            """,
            (conversation_id,),
        )
    )


# ----------------------------
# Final-path reconstruction
# ----------------------------

def build_final_node_path(conn: sqlite3.Connection, conversation_id: str, current_node: str, max_hops: int = 20000) -> List[str]:
    """
    Walk parents from current_node to root using messages.parent_id, then return root->leaf node_id list.

    Notes:
    - current_node should correspond to a node_id in messages, but sometimes it may not.
    - If any step can't be resolved, we stop and return what we have.
    """
    path: List[str] = []
    seen = set()
    node = current_node
    hops = 0

    while node and node not in seen and hops < max_hops:
        seen.add(node)
        path.append(node)

        row = fetch_message_row(conn, conversation_id, node)
        if row is None:
            # current_node (or an ancestor) might not be present as a message row
            break

        node = row["parent_id"]
        hops += 1

    path.reverse()
    return path


def fetch_final_human_messages(conn: sqlite3.Connection, conversation_id: str, current_node: str) -> List[sqlite3.Row]:
    """
    Reconstruct the final path (root->current_node), then filter to human roles with non-empty text.
    """
    node_path = build_final_node_path(conn, conversation_id, current_node)
    rows: List[sqlite3.Row] = []

    for nid in node_path:
        r = fetch_message_row(conn, conversation_id, nid)
        if r is None:
            continue
        if r["role"] in HUMAN_ROLES and r["text"] and str(r["text"]).strip():
            rows.append(r)

    # Ensure stable chronological ordering
    rows.sort(key=lambda r: (r["create_time"] or "", r["id"]))
    return rows


# ----------------------------
# Event creation
# ----------------------------

def make_lui_id(conversation_id: str, node_id: str, role: str, text: str) -> str:
    # Deterministic ID. Uses a stable prefix of text to reduce collisions while keeping deterministic behavior.
    basis = f"{conversation_id}|{node_id}|{role}|{text[:250]}"
    return sha1_hex(basis)


def rows_to_events(
    rows: Sequence[sqlite3.Row],
    conversation_id: str,
    title: Optional[str],
    include_titles: bool,
    include_provenance: bool,
) -> List[LuiEvent]:
    events: List[LuiEvent] = []
    turn = 0

    for r in rows:
        text = (r["text"] or "").strip()
        if not text:
            continue

        node_id = r["node_id"]
        role = r["role"]
        lui_id = make_lui_id(conversation_id, node_id, role, text)

        events.append(
            LuiEvent(
                lui_id=lui_id,
                conversation_id=conversation_id,
                turn_index=turn,
                timestamp=r["create_time"],
                role=role,
                text=text,
                title=title if include_titles else None,
                node_id=node_id if include_provenance else None,
                parent_id=r["parent_id"] if include_provenance else None,
            )
        )
        turn += 1

    return events


def events_for_conversation(
    conn: sqlite3.Connection,
    conversation_id: str,
    title: Optional[str],
    current_node: Optional[str],
    mode: str,
    include_titles: bool,
    include_provenance: bool,
) -> List[LuiEvent]:
    if mode == "all-human":
        rows = fetch_all_human_messages(conn, conversation_id)
        return rows_to_events(rows, conversation_id, title, include_titles, include_provenance)

    if mode == "final-human":
        if current_node:
            final_rows = fetch_final_human_messages(conn, conversation_id, current_node)
            if final_rows:
                return rows_to_events(final_rows, conversation_id, title, include_titles, include_provenance)

        # Fallback (deterministic): if current_node missing/unusable -> all-human
        rows = fetch_all_human_messages(conn, conversation_id)
        return rows_to_events(rows, conversation_id, title, include_titles, include_provenance)

    raise ValueError(f"Unknown mode: {mode}")


# ----------------------------
# Packing (prompt-sized)
# ----------------------------

def estimate_event_chars(e: LuiEvent) -> int:
    # proxy for prompt size; includes metadata overhead and JSON framing
    return len(e.text) + 140


def pack_events(
    events: Iterable[LuiEvent],
    max_chars: int,
    max_events: Optional[int],
) -> List[Dict]:
    packets: List[Dict] = []
    cur_events: List[Dict] = []
    cur_chars = 0
    idx = 0

    for e in events:
        e_dict = e.to_dict()
        e_chars = estimate_event_chars(e)

        hit_char_limit = cur_events and (cur_chars + e_chars > max_chars)
        hit_event_limit = (max_events is not None) and cur_events and (len(cur_events) >= max_events)

        if hit_char_limit or hit_event_limit:
            packets.append(
                {
                    "packet_id": f"pkt_{idx:05d}",
                    "created_at": now_utc_iso(),
                    "char_budget": max_chars,
                    "events": cur_events,
                }
            )
            idx += 1
            cur_events = []
            cur_chars = 0

        cur_events.append(e_dict)
        cur_chars += e_chars

    if cur_events:
        packets.append(
            {
                "packet_id": f"pkt_{idx:05d}",
                "created_at": now_utc_iso(),
                "char_budget": max_chars,
                "events": cur_events,
            }
        )

    return packets


def write_jsonl(path: Path, records: Iterable[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ----------------------------
# CLI
# ----------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Export final-human LUI packets from iam.db for Foundation Models.")
    ap.add_argument("--db", required=True, help="Path to iam.db (e.g., data/artifacts/iam.db)")
    ap.add_argument("--out", required=True, help="Output JSONL packets file (e.g., data/artifacts/lui_packets.jsonl)")
    ap.add_argument("--mode", default="final-human", choices=["final-human", "all-human"])
    ap.add_argument("--max-chars", type=int, default=24000, help="Character budget per packet (proxy for tokens).")
    ap.add_argument("--max-events", type=int, default=None, help="Optional max events per packet.")
    ap.add_argument("--include-titles", action="store_true", help="Include conversation title in each event.")
    ap.add_argument("--include-provenance", action="store_true", help="Include node_id/parent_id in each event.")
    ap.add_argument("--events-out", default=None, help="Optional raw events JSONL output (one event per line).")

    args = ap.parse_args()

    db_path = Path(args.db).resolve()
    out_path = Path(args.out).resolve()
    events_out_path = Path(args.events_out).resolve() if args.events_out else None

    conn = connect(db_path)
    convs = fetch_conversations(conn)

    all_events: List[LuiEvent] = []
    for c in convs:
        cid = c["conversation_id"]
        title = c["title"]
        current_node = c["current_node"]

        ev = events_for_conversation(
            conn=conn,
            conversation_id=cid,
            title=title,
            current_node=current_node,
            mode=args.mode,
            include_titles=args.include_titles,
            include_provenance=args.include_provenance,
        )
        all_events.extend(ev)

    conn.close()

    if events_out_path:
        write_jsonl(events_out_path, (e.to_dict() for e in all_events))

    packets = pack_events(all_events, max_chars=args.max_chars, max_events=args.max_events)
    write_jsonl(out_path, packets)

    print(f"Wrote events:  {len(all_events):,}")
    print(f"Wrote packets: {len(packets):,} -> {out_path}")
    if events_out_path:
        print(f"Wrote raw events -> {events_out_path}")


if __name__ == "__main__":
    main()

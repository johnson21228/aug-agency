#!/usr/bin/env python3
"""
build_provdb_nodes_prp_v1.py

Materialize PRP nodes as a node layer over provdb_core events.

- Nodes are derived, rebuildable, and non-authoritative.
- Node IDs are stable numeric:
    node_id = hash64(layer_key | stream_id | node_index)
- Membership is lossless via ordered event_id list.
- No semantic inference; policy is explicit and versioned by layer_key.

Policy (prp_v1_turn_pairing):
- stream := (source_type, source_ref)  => stream_id = hash64(source_type|source_ref)
- order events within stream by:
    observed_ts (NULLS LAST), observed_ts ASC, capture_id ASC
- start a new node on each human event
- include subsequent non-human events until the next human event (exclusive)
  - assistant => response
  - system/tool/other => context
- ignore pre-human non-human events (explicit policy)
"""

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

LAYER_KEY = "prp_v1_turn_pairing"

POLICY_JSON = {
  "layer_key": LAYER_KEY,
  "stream": "u64(source_type|source_ref)",
  "event_order": [
    "CASE WHEN observed_ts IS NULL THEN 1 ELSE 0 END",
    "observed_ts ASC",
    "capture_id ASC"
  ],
  "start_node_on": {"actor_type": "human"},
  "member_roles": {
    "human": "prompt",
    "assistant": "response",
    "system": "context",
    "tool": "context",
    "other": "context"
  },
  "pre_human_events": "ignore"
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def u64(s: str) -> int:
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big", signed=False)

def node_id(layer_key: str, stream_id: int, node_index: int) -> int:
    return u64(f"{layer_key}|{stream_id}|{node_index}")

def ensure_schema(db: sqlite3.Connection) -> None:
    db.executescript((Path(__file__).parent / "provdb_nodes.sql").read_text(encoding="utf-8"))

def ensure_layer(db: sqlite3.Connection) -> None:
    db.execute(
        "INSERT OR IGNORE INTO node_layers(layer_key, policy_json, created_ts) VALUES(?,?,?)",
        (LAYER_KEY, json.dumps(POLICY_JSON, sort_keys=True), now_iso()),
    )

def stream_list(db: sqlite3.Connection):
    return db.execute(
        "SELECT DISTINCT source_type, source_ref FROM events ORDER BY source_type, source_ref"
    ).fetchall()

def ordered_events(db: sqlite3.Connection, source_type: str, source_ref: str):
    return db.execute(
        """
        SELECT event_id, actor_type, observed_ts, capture_id
        FROM events
        WHERE source_type=? AND source_ref=?
        ORDER BY
          CASE WHEN observed_ts IS NULL THEN 1 ELSE 0 END,
          observed_ts ASC,
          capture_id ASC
        """,
        (source_type, source_ref),
    ).fetchall()

def write_node(db: sqlite3.Connection,
               stream_id: int,
               node_index: int,
               members: List[Tuple[int,str,Optional[str]]]) -> None:
    nid = node_id(LAYER_KEY, stream_id, node_index)

    ts = [m[2] for m in members if m[2] is not None]
    ts_min = min(ts) if ts else None
    ts_max = max(ts) if ts else None

    db.execute(
        """
        INSERT OR IGNORE INTO nodes(node_id, layer_key, stream_id, node_index, observed_ts_min, observed_ts_max)
        VALUES(?,?,?,?,?,?)
        """,
        (nid, LAYER_KEY, stream_id, node_index, ts_min, ts_max),
    )

    for idx, (event_id, role, _) in enumerate(members):
        db.execute(
            """
            INSERT OR IGNORE INTO node_members(node_id, member_index, event_id, member_role)
            VALUES(?,?,?,?)
            """,
            (nid, idx, event_id, role),
        )

def build(db: sqlite3.Connection) -> None:
    ensure_schema(db)
    ensure_layer(db)

    for s in stream_list(db):
        stype = s["source_type"]
        sref = s["source_ref"]
        sid = u64(f"{stype}|{sref}")

        evs = ordered_events(db, stype, sref)

        node_index = -1
        current: List[Tuple[int,str,Optional[str]]] = []
        started = False

        for ev in evs:
            actor = ev["actor_type"]
            ots = ev["observed_ts"]
            eid = int(ev["event_id"])

            if actor == "human":
                if started and current:
                    node_index += 1
                    write_node(db, sid, node_index, current)
                    current = []
                started = True
                current.append((eid, "prompt", ots))
            else:
                if not started:
                    # explicit policy: ignore pre-human events
                    continue
                role = "response" if actor == "assistant" else "context"
                current.append((eid, role, ots))

        if started and current:
            node_index += 1
            write_node(db, sid, node_index, current)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provdb", required=True, help="Path to provdb_core.db")
    args = ap.parse_args()

    db = sqlite3.connect(args.provdb)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON;")
    build(db)
    db.commit()
    db.close()
    print(f"Materialized node layer {LAYER_KEY} into: {args.provdb}")

if __name__ == "__main__":
    main()

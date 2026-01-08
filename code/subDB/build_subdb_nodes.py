#!/usr/bin/env python3
"""
build_subdb_nodes.py

Build a semantic-free SubDB over provdb nodes for a given node layer.

Inputs:
- provdb_core.db containing:
  - events (atomic)
  - nodes / node_members for the selected layer_key (derived)
Outputs:
- subdb_nodes.db with:
  - node_coords(stream_id, node_index, node_id)
  - edges adjacency between consecutive node_index within each stream

No semantic inference; geometry is purely structural.
"""

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provdb", required=True)
    ap.add_argument("--layer", required=True, help="layer_key in provdb.nodes")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    prov = sqlite3.connect(args.provdb)
    prov.row_factory = sqlite3.Row

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = sqlite3.connect(str(out_path))
    out.row_factory = sqlite3.Row
    out.execute("PRAGMA foreign_keys=ON;")

    out.executescript((Path(__file__).parent / "subdb_nodes.sql").read_text(encoding="utf-8"))
    out.execute("INSERT OR REPLACE INTO layer_meta(layer_key, built_ts) VALUES(?,?)", (args.layer, now_iso()))

    streams = prov.execute(
        "SELECT DISTINCT stream_id FROM nodes WHERE layer_key=? ORDER BY stream_id",
        (args.layer,),
    ).fetchall()

    for s in streams:
        sid = int(s["stream_id"])
        nodes = prov.execute(
            """
            SELECT node_id, node_index, observed_ts_min, observed_ts_max
            FROM nodes
            WHERE layer_key=? AND stream_id=?
            ORDER BY node_index ASC
            """,
            (args.layer, sid),
        ).fetchall()

        out.execute("INSERT OR REPLACE INTO streams(stream_id, node_count) VALUES(?,?)", (sid, len(nodes)))

        prev_node_id = None
        for row in nodes:
            nid = int(row["node_id"])
            idx = int(row["node_index"])
            out.execute(
                """
                INSERT OR REPLACE INTO node_coords(node_id, stream_id, node_index, observed_ts_min, observed_ts_max)
                VALUES(?,?,?,?,?)
                """,
                (nid, sid, idx, row["observed_ts_min"], row["observed_ts_max"]),
            )
            if prev_node_id is not None:
                out.execute(
                    "INSERT OR IGNORE INTO edges(src_node_id, dst_node_id, edge_type) VALUES(?,?,?)",
                    (prev_node_id, nid, "adjacent"),
                )
                out.execute(
                    "INSERT OR IGNORE INTO edges(src_node_id, dst_node_id, edge_type) VALUES(?,?,?)",
                    (nid, prev_node_id, "adjacent"),
                )
            prev_node_id = nid

    out.commit()
    out.close()
    prov.close()
    print(f"Wrote subdb nodes: {out_path}")

if __name__ == "__main__":
    main()

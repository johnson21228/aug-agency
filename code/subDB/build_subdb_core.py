#!/usr/bin/env python3
"""
build_subdb_core.py

Build subdb_core.db from provdb_core.db.

- SubDB is semantic-free continuity geometry.
- stream_id derived from (source_type, source_ref).
- event order is deterministic within each stream.
- adjacency edges are stored as structural relations.
"""

import argparse
import hashlib
import sqlite3
from pathlib import Path


def u64(s: str) -> int:
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big", signed=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provdb", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    prov = sqlite3.connect(args.provdb)
    prov.row_factory = sqlite3.Row

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = sqlite3.connect(str(out_path))
    out.execute("PRAGMA foreign_keys=ON;")

    out.executescript(
        """
        CREATE TABLE IF NOT EXISTS streams(
          stream_id INTEGER PRIMARY KEY,
          source_type TEXT NOT NULL,
          source_ref TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS event_coords(
          event_id INTEGER PRIMARY KEY,
          stream_id INTEGER NOT NULL,
          turn_index INTEGER NOT NULL,
          observed_ts TEXT,
          FOREIGN KEY(stream_id) REFERENCES streams(stream_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS edges(
          src_event_id INTEGER NOT NULL,
          dst_event_id INTEGER NOT NULL,
          edge_type TEXT NOT NULL,
          PRIMARY KEY(src_event_id, dst_event_id, edge_type)
        );
        """
    )

    streams = prov.execute(
        """
        SELECT DISTINCT source_type, source_ref
        FROM events
        ORDER BY source_type, source_ref
        """
    ).fetchall()

    for s in streams:
        stream_id = u64(f"{s['source_type']}|{s['source_ref']}")
        out.execute(
            "INSERT OR IGNORE INTO streams(stream_id, source_type, source_ref) VALUES(?,?,?)",
            (stream_id, s["source_type"], s["source_ref"]),
        )

        evs = prov.execute(
            """
            SELECT event_id, observed_ts, capture_id
            FROM events
            WHERE source_type=? AND source_ref=?
            ORDER BY
              CASE WHEN observed_ts IS NULL THEN 1 ELSE 0 END,
              observed_ts ASC,
              capture_id ASC
            """,
            (s["source_type"], s["source_ref"]),
        ).fetchall()

        prev = None
        for idx, ev in enumerate(evs):
            out.execute(
                """
                INSERT OR IGNORE INTO event_coords(event_id, stream_id, turn_index, observed_ts)
                VALUES(?,?,?,?)
                """,
                (ev["event_id"], stream_id, idx, ev["observed_ts"]),
            )
            if prev is not None:
                out.execute(
                    """
                    INSERT OR IGNORE INTO edges(src_event_id, dst_event_id, edge_type)
                    VALUES(?,?,?)
                    """,
                    (prev, ev["event_id"], "adjacent"),
                )
            prev = ev["event_id"]

    out.commit()
    out.close()
    prov.close()
    print(f"Wrote subdb core: {out_path}")


if __name__ == "__main__":
    main()

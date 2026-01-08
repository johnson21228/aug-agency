#!/usr/bin/env python3
"""
build_provdb_core.py

Build provdb_core.db from iam.db capture tables.

- Deterministic stable event_id derived from capture provenance.
- event_text is a deterministic rehydration of capture_payload_parts.
- No semantic inference.
"""

import argparse
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Optional


def u64_from_key(s: str) -> int:
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big", signed=False)


def join_text(parts: List[Optional[str]]) -> str:
    return "\n".join([p for p in parts if p is not None]).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iam-db", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    iam = sqlite3.connect(args.iam_db)
    iam.row_factory = sqlite3.Row

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = sqlite3.connect(str(out_path))
    out.execute("PRAGMA foreign_keys=ON;")

    out.executescript(
        """
        CREATE TABLE IF NOT EXISTS events(
          event_id INTEGER PRIMARY KEY,
          capture_id INTEGER UNIQUE,
          source_type TEXT NOT NULL,
          source_ref TEXT NOT NULL,
          source_event_key TEXT,
          actor_type TEXT NOT NULL,
          observed_ts TEXT,
          ingested_ts TEXT
        );

        CREATE TABLE IF NOT EXISTS event_text(
          event_id INTEGER PRIMARY KEY,
          text TEXT NOT NULL
        );
        """
    )

    rows = iam.execute(
        """
        SELECT capture_id, source_type, source_ref, source_event_key, actor_type, observed_ts, ingested_ts
        FROM capture_events
        ORDER BY capture_id ASC
        """
    ).fetchall()

    for r in rows:
        key = f"{r['source_type']}|{r['source_ref']}|{r['source_event_key'] or ''}"
        event_id = u64_from_key(key)

        parts = iam.execute(
            """
            SELECT text FROM capture_payload_parts
            WHERE capture_id = ?
            ORDER BY part_index ASC
            """,
            (r["capture_id"],),
        ).fetchall()

        text = join_text([p["text"] for p in parts])

        out.execute(
            """
            INSERT OR IGNORE INTO events(event_id, capture_id, source_type, source_ref, source_event_key,
                                         actor_type, observed_ts, ingested_ts)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                event_id,
                r["capture_id"],
                r["source_type"],
                r["source_ref"],
                r["source_event_key"],
                r["actor_type"],
                r["observed_ts"],
                r["ingested_ts"],
            ),
        )

        out.execute(
            """
            INSERT OR IGNORE INTO event_text(event_id, text)
            VALUES(?,?)
            """,
            (event_id, text),
        )

    out.commit()
    out.close()
    iam.close()
    print(f"Wrote provdb core: {out_path}")


if __name__ == "__main__":
    main()

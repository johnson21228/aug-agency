#!/usr/bin/env python3
"""canonicalize_messages.py

Rebuild deterministic per-message text and a canonical view.

This is useful when:
- you've already ingested and want to (re)generate message_text + message_canonical
- you changed ingest logic and want to normalize an existing iam.db

It is SAFE to re-run; it drops/recreates message_text and message_canonical.

Usage:
  python3 tools/canonicalize_messages.py --db data/artifacts/iam.db
"""

from __future__ import annotations

import argparse
import sqlite3


SQL = """
DROP VIEW IF EXISTS message_canonical;
DROP TABLE IF EXISTS message_text;

CREATE TABLE message_text (
  message_row_id INTEGER PRIMARY KEY,
  text           TEXT,
  source         TEXT NOT NULL,   -- 'parts' | 'none'
  char_count     INTEGER NOT NULL,
  FOREIGN KEY(message_row_id) REFERENCES messages(id)
);

INSERT INTO message_text (message_row_id, text, source, char_count)
SELECT
  message_row_id,
  GROUP_CONCAT(part_text, '') AS text,
  'parts' AS source,
  LENGTH(GROUP_CONCAT(part_text, '')) AS char_count
FROM (
  SELECT message_row_id, part_index, part_text
  FROM message_content_parts
  ORDER BY message_row_id, part_index
)
GROUP BY message_row_id;

INSERT INTO message_text (message_row_id, text, source, char_count)
SELECT
  m.id AS message_row_id,
  NULL AS text,
  'none' AS source,
  0 AS char_count
FROM messages m
WHERE NOT EXISTS (
  SELECT 1 FROM message_text mt WHERE mt.message_row_id = m.id
);

CREATE VIEW message_canonical AS
SELECT
  m.id                AS message_row_id,
  m.conversation_id,
  m.node_id,
  m.message_id,
  m.parent_id,
  m.role,
  m.author_name,
  m.create_time,
  m.update_time,
  m.content_type,
  mt.text             AS text,
  mt.source           AS text_source,
  mt.char_count       AS text_char_count,
  m.status,
  m.metadata_json
FROM messages m
JOIN message_text mt
  ON mt.message_row_id = m.id;
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/artifacts/iam.db", help="Path to iam.db")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        conn.executescript(SQL)
        conn.commit()

        total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        mt = conn.execute("SELECT COUNT(*) FROM message_text").fetchone()[0]
        none = conn.execute("SELECT COUNT(*) FROM message_text WHERE source='none'").fetchone()[0]
        parts = conn.execute("SELECT COUNT(*) FROM message_text WHERE source='parts'").fetchone()[0]

        print("Canonicalization complete:")
        print(f"  DB: {args.db}")
        print(f"  messages:     {total}")
        print(f"  message_text: {mt} (parts={parts}, none={none})")
        print("  view: message_canonical")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
code/stage1/build_turn_index.py

Stage-1 deterministic sequencing layer for IAM.

Creates:
- message_turn_index (table): stable per-conversation turn ordering
- message_seq (view): canonical, sequenced message rows for downstream stages

Assumes Stage-0 has already created:
- message_text (table) covering all messages
- message_canonical (view) joining messages + message_text

Idempotent:
- Rebuilding will DROP/CREATE the view and DROP/CREATE the table.

Usage:
  python3 code/stage1/build_turn_index.py --db data/artifacts/iam.db
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


DDL = """
PRAGMA foreign_keys=ON;

DROP VIEW IF EXISTS message_seq;
DROP TABLE IF EXISTS message_turn_index;

CREATE TABLE message_turn_index (
  message_row_id  INTEGER PRIMARY KEY,
  conversation_id TEXT    NOT NULL,
  turn_index      INTEGER NOT NULL,
  FOREIGN KEY(message_row_id) REFERENCES messages(id)
);

-- Deterministic per-conversation sequencing.
-- Rule:
--   1) order by create_time ASC (lexical ISO8601 works)
--   2) tie-break on message_row_id ASC (stable)
INSERT INTO message_turn_index (message_row_id, conversation_id, turn_index)
WITH ranked AS (
  SELECT
    mc.message_row_id,
    mc.conversation_id,
    ROW_NUMBER() OVER (
      PARTITION BY mc.conversation_id
      ORDER BY
        COALESCE(mc.create_time, '') ASC,
        mc.message_row_id ASC
    ) - 1 AS turn_index
  FROM message_canonical mc
)
SELECT message_row_id, conversation_id, turn_index
FROM ranked;

CREATE INDEX idx_message_turn_index_conv_turn
  ON message_turn_index(conversation_id, turn_index);

CREATE VIEW message_seq AS
SELECT
  mti.turn_index,
  mc.*
FROM message_turn_index mti
JOIN message_canonical mc
  ON mc.message_row_id = mti.message_row_id;
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/artifacts/iam.db", help="Path to iam.db")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.executescript(DDL)
        con.commit()
    finally:
        con.close()

    print("Stage-1 turn index built.")
    print(f"DB: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

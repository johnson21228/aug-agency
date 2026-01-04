# Inspecting iam.db — Cheat Sheet

This document explains how to inspect the ChatGPT ingestion database.

Database location:
    data/artifacts/iam.db

All commands assume you are running from the repo root.

============================================================
1. Open the database
============================================================

Open an interactive SQLite session:

    sqlite3 data/artifacts/iam.db

Exit anytime with:

    .exit

============================================================
2. Schema overview (what exists)
============================================================

List tables:

    .tables

Show table definitions:

    .schema conversations
    .schema messages
    .schema message_content_parts

Key facts:
- conversations = one row per chat
- messages = flattened message nodes from ChatGPT mapping tree
- message_content_parts = ordered text fragments per message
- Messages are unique by (conversation_id, node_id)
- Ingest is idempotent (re-runs update, not duplicate)

============================================================
3. High-level sanity checks
============================================================

Conversation count:

    SELECT COUNT(*) FROM conversations;

Message count:

    SELECT COUNT(*) FROM messages;

Messages by role:

    SELECT role, COUNT(*) FROM messages GROUP BY role;

============================================================
4. List conversations
============================================================

Titles and creation times:

    SELECT title, create_time
    FROM conversations
    ORDER BY create_time
    LIMIT 20;

Find conversations by keyword:

    SELECT conversation_id, title
    FROM conversations
    WHERE title LIKE '%Xcode%'
    LIMIT 10;

============================================================
5. Read a conversation transcript (all nodes)
============================================================

1) Copy a conversation_id
2) Then run:

    SELECT
      create_time,
      role,
      substr(text, 1, 200) AS preview
    FROM messages
    WHERE conversation_id = 'PASTE_CONVERSATION_ID'
    ORDER BY create_time;

Notes:
- Includes all branches/regenerations
- Includes system and tool messages

============================================================
6. Human-only transcript (user + assistant)
============================================================

    SELECT
      create_time,
      role,
      text
    FROM messages
    WHERE conversation_id = 'PASTE_CONVERSATION_ID'
      AND role IN ('user','assistant')
    ORDER BY create_time;

============================================================
7. Detect branching (regenerations / forks)
============================================================

Branch points = parents with multiple children:

    SELECT parent_id, COUNT(*) AS children
    FROM messages
    WHERE conversation_id = 'PASTE_CONVERSATION_ID'
    GROUP BY parent_id
    HAVING COUNT(*) > 1;

If rows appear, the conversation has branching.

============================================================
8. Final-path anchor (current_node)
============================================================

Check which conversations expose a final chosen node:

    SELECT title, current_node
    FROM conversations
    WHERE current_node IS NOT NULL
    LIMIT 10;

current_node can later be used to reconstruct the chosen transcript path.

============================================================
9. Text integrity checks
============================================================

Messages missing text:

    SELECT role, COUNT(*)
    FROM messages
    WHERE text IS NULL OR text = ''
    GROUP BY role;

Longest messages:

    SELECT LENGTH(text) AS len, role
    FROM messages
    ORDER BY len DESC
    LIMIT 10;

============================================================
10. Inspect normalized message parts
============================================================

    SELECT
      m.role,
      p.part_index,
      substr(p.part_text, 1, 100)
    FROM message_content_parts p
    JOIN messages m ON m.id = p.message_row_id
    LIMIT 20;

Confirms:
- text parts preserved
- ordering correct
- suitable for FTS or embeddings

============================================================
Interpretation notes
============================================================

- iam.db is a Stage-0 capture layer:
  - all message nodes
  - all branches
  - minimal semantic filtering
- “Human transcript” and “final transcript” should be views or derived tables
- Ingest script should remain stable; analysis layers evolve separately

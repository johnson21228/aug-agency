-- 0001_capture_contract.sql
-- Authoritative schema for iam.db Capture Store (Stage 1).
-- Append-only, adapter-agnostic capture contract.

PRAGMA foreign_keys = ON;

-- Optional: record schema version inside the DB (in addition to git).
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', '1');

-- One row per captured LUI/event. Append-only: never UPDATE/DELETE in normal operation.
CREATE TABLE IF NOT EXISTS capture_events (
  capture_id      INTEGER PRIMARY KEY,
  source_type     TEXT NOT NULL,          -- e.g. 'chatgpt_export', 'iam_app', 'repo_file', 'voice', 'tool'
  source_ref      TEXT NOT NULL,          -- e.g. conversation_id, file path, device/session id
  source_event_key TEXT,                  -- e.g. node_id/message_id/offset-id (preferred when available)
  actor_type      TEXT NOT NULL,          -- 'human'|'assistant'|'agent'|'system'
  observed_ts     TEXT,                   -- timestamp from source (nullable)
  ingested_ts     TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),  -- when inserted here
  payload_kind    TEXT NOT NULL,          -- 'text'|'multipart'|'json'|'binary_ref'
  payload_hash    TEXT,                   -- hash for idempotence fallback when no stable source_event_key
  schema_version  INTEGER NOT NULL DEFAULT 1,

  CHECK (actor_type IN ('human','assistant','agent','system')),
  CHECK (payload_kind IN ('text','multipart','json','binary_ref'))
);

-- Raw payload parts for each event (lossless, multipart-safe).
CREATE TABLE IF NOT EXISTS capture_payload_parts (
  capture_id  INTEGER NOT NULL,
  part_index  INTEGER NOT NULL,
  mime_type   TEXT NOT NULL,     -- e.g. 'text/plain', 'application/json'
  text        TEXT,              -- nullable
  blob_ref    TEXT,              -- nullable (path/object key if storing large/binary outside SQLite)

  PRIMARY KEY (capture_id, part_index),
  FOREIGN KEY (capture_id) REFERENCES capture_events(capture_id) ON DELETE RESTRICT
);

-- Optional: structural (non-semantic) relations (reply-to, parent, attachment-of, etc.).
CREATE TABLE IF NOT EXISTS capture_relations (
  capture_id            INTEGER NOT NULL,
  rel_type              TEXT NOT NULL,   -- e.g. 'parent','reply_to','attachment_of'
  target_source_event_key TEXT,          -- if target not yet mapped to capture_id
  target_capture_id     INTEGER,         -- if known
  created_ts            TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),

  PRIMARY KEY (capture_id, rel_type, target_source_event_key, target_capture_id),
  FOREIGN KEY (capture_id) REFERENCES capture_events(capture_id) ON DELETE RESTRICT,
  FOREIGN KEY (target_capture_id) REFERENCES capture_events(capture_id) ON DELETE RESTRICT
);

-- Idempotence: prefer stable source keys when present.
CREATE UNIQUE INDEX IF NOT EXISTS ux_capture_events_source_key
ON capture_events(source_type, source_ref, source_event_key)
WHERE source_event_key IS NOT NULL;

-- Fallback idempotence when source_event_key is unavailable.
CREATE UNIQUE INDEX IF NOT EXISTS ux_capture_events_fallback_hash
ON capture_events(source_type, source_ref, payload_hash, observed_ts)
WHERE source_event_key IS NULL AND payload_hash IS NOT NULL;

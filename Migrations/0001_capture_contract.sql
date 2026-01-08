PRAGMA foreign_keys = ON;

-- Stage-1 Capture Store contract for iam.db (append-only source-of-record)

CREATE TABLE IF NOT EXISTS capture_events (
  capture_id        INTEGER PRIMARY KEY,
  source_type       TEXT NOT NULL,
  source_ref        TEXT NOT NULL,
  source_event_key  TEXT,
  actor_type        TEXT NOT NULL,
  observed_ts       TEXT,
  ingested_ts       TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  payload_kind      TEXT NOT NULL,
  payload_hash      TEXT,
  schema_version    INTEGER NOT NULL DEFAULT 1,

  CHECK (actor_type IN ('human','assistant','agent','system')),
  CHECK (payload_kind IN ('text','multipart','json','binary_ref'))
);

CREATE TABLE IF NOT EXISTS capture_payload_parts (
  capture_id  INTEGER NOT NULL,
  part_index  INTEGER NOT NULL,
  mime_type   TEXT NOT NULL,
  text        TEXT,
  blob_ref    TEXT,
  PRIMARY KEY (capture_id, part_index),
  FOREIGN KEY (capture_id) REFERENCES capture_events(capture_id) ON DELETE RESTRICT
);

-- Idempotence (preferred): stable source key
CREATE UNIQUE INDEX IF NOT EXISTS ux_capture_events_source_key
ON capture_events(source_type, source_ref, source_event_key)
WHERE source_event_key IS NOT NULL;

-- Fallback idempotence when source_event_key is absent
CREATE UNIQUE INDEX IF NOT EXISTS ux_capture_events_fallback_hash
ON capture_events(source_type, source_ref, payload_hash, observed_ts)
WHERE source_event_key IS NULL AND payload_hash IS NOT NULL;

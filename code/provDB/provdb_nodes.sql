-- provdb_nodes.sql
-- Node projection layers over atomic events.
-- Derived, rebuildable, non-authoritative.
-- Lossless via membership pointers to events.event_id.

CREATE TABLE IF NOT EXISTS node_layers (
  layer_key       TEXT PRIMARY KEY,     -- e.g. "prp_v1_turn_pairing"
  policy_json     TEXT NOT NULL,        -- explicit, canonical json for the layer policy
  created_ts      TEXT NOT NULL
);

-- Canonical node registry within a layer.
-- node_id is stable numeric derived from (layer_key, stream_id, node_index).
CREATE TABLE IF NOT EXISTS nodes (
  node_id         INTEGER PRIMARY KEY,  -- uint64 stored as INTEGER
  layer_key       TEXT NOT NULL REFERENCES node_layers(layer_key) ON DELETE RESTRICT,
  stream_id       INTEGER NOT NULL,      -- uint64
  node_index      INTEGER NOT NULL,      -- 0..n within stream for this layer
  observed_ts_min TEXT,
  observed_ts_max TEXT,
  UNIQUE(layer_key, stream_id, node_index)
);

-- Lossless membership: node -> ordered event list.
CREATE TABLE IF NOT EXISTS node_members (
  node_id         INTEGER NOT NULL REFERENCES nodes(node_id) ON DELETE RESTRICT,
  member_index    INTEGER NOT NULL,
  event_id        INTEGER NOT NULL,      -- references events.event_id (not enforced cross-db)
  member_role     TEXT NOT NULL,         -- "prompt"|"response"|"context"|"event"
  PRIMARY KEY(node_id, member_index),
  UNIQUE(node_id, event_id)
);

CREATE INDEX IF NOT EXISTS ix_nodes_layer_stream ON nodes(layer_key, stream_id, node_index);
CREATE INDEX IF NOT EXISTS ix_node_members_event ON node_members(event_id);

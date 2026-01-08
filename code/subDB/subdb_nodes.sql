-- subdb_nodes.sql
-- Semantic-free continuity geometry over canonical node_id for a given node layer.

CREATE TABLE IF NOT EXISTS layer_meta (
  layer_key       TEXT PRIMARY KEY,
  built_ts        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS streams (
  stream_id       INTEGER PRIMARY KEY,  -- uint64
  node_count      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS node_coords (
  node_id         INTEGER PRIMARY KEY,  -- canonical node_id (uint64)
  stream_id       INTEGER NOT NULL,
  node_index      INTEGER NOT NULL,
  observed_ts_min TEXT,
  observed_ts_max TEXT,
  UNIQUE(stream_id, node_index),
  FOREIGN KEY(stream_id) REFERENCES streams(stream_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS edges (
  src_node_id     INTEGER NOT NULL,
  dst_node_id     INTEGER NOT NULL,
  edge_type       TEXT NOT NULL,
  PRIMARY KEY(src_node_id, dst_node_id, edge_type)
);

CREATE INDEX IF NOT EXISTS ix_node_coords_stream ON node_coords(stream_id, node_index);
CREATE INDEX IF NOT EXISTS ix_edges_src ON edges(src_node_id, edge_type);

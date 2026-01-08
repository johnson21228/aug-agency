# Node Projections and Parallel Pairings

This document defines how multiple node granularities (e.g. PRP, chunking, sessions)
can coexist as derived projections over the same captured event stream, while preserving
IAM invariants:

- stable identity is event-level
- derived structures are rebuildable and non-authoritative
- correctness does not depend on semantics
- composition happens by stable IDs

## Definitions

### Event (Durable Identity)
An event is a captured fact. Durable identity is assigned only at the event level.

- Capture anchor: `iam.db.capture_events.capture_id`
- Provenance identity: `(source_type, source_ref, source_event_key)` (preferred)
- Stable numeric event identity (ProvDB): `event_id` derived solely from capture provenance

Events are the only durable referents for annotations, links, and long-horizon continuity.

### Node (Projection)
A node is a derived grouping of one or more events intended for navigation, re-entry,
and continuity geometry.

Nodes are *projections*, not identities.

Nodes must be:
- deterministic from events
- policy-versioned (explicitly named)
- rebuildable (non-authoritative)
- lossless via event membership pointers

## Parallel Pairings (Node Layers)

A node layer is defined by a `layer_key` (policy identity), such as:
- `event_v1` (1:1 event nodes)
- `prp_v1_turn_pairing` (prompt/response pairing policy)
- `ian_v1_chunking_8k_chars` (alternative chunking policy)

A single `iam.db` capture can produce many node layers in parallel.

### Layer identity
Each layer MUST be explicitly named and versioned:
- `layer_key` (string, stable)
- `layer_policy_json` (explicit policy contract; may change only by creating a new layer_key)
- optional `layer_hash` (hash of canonical policy json)

## Node Interface (SQL Contract)

Every layer materializes nodes using the same interface:

- `node_id` : stable numeric identifier within the layer
- `stream_id` : stable stream identity
- `node_index` : sequential coordinate within the stream for this layer
- `node_members[]` : ordered membership pointing to atomic `event_id`s

### Required determinism
Node ID derivation MUST include the layer identity:

`node_id = hash64(layer_key | stream_id | node_index)`

This prevents collisions across layers and makes rebuildability explicit.

### Lossless membership requirement
Every node MUST be lossless via membership:

`node_members(node_id -> ordered event_id list)`

Every member event MUST rehydrate back to capture raw payload:
`event_id -> capture_id -> capture_payload_parts(part_index=0, raw json)`

This is the continuity correctness guarantee.

## SubDB: One Node Type, Many Materializations

SubDB is semantic-free continuity geometry over `node_id`.

There is only one SubDB "node" concept: `node_id` with coordinates in a stream.

For each layer, SubDB may be materialized as:
- a separate `subdb/<layer_key>.db`, or
- a shared SubDB with all rows keyed by `layer_key`

SubDB correctness depends only on:
- `(layer_key, stream_id, node_index)` ordering
- adjacency derived from ordering

SubDB must remain valid if all semantic overlays are removed.

## CAP (Read-Only Orchestration)

CAP selects a layer at runtime and composes ephemerally:
- SubDB provides structural neighborhoods over `node_id`
- ProvDB provides rehydration via `node_members -> event_id -> capture`

CAP may present:
- PRP views
- chunk views
- mixed views

No layer composition is persisted into substrate stores.

## Status

This document is governing architecture: code must conform.

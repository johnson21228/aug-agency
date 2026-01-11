# SubDB Contract (IAMApp)

This document defines IAMApp’s obligations for sub materialization.
It is a local mirror of the authoritative architecture contract:

- `architecture/cmp/contracts/subdb_contract.md`

If this document conflicts with the architecture contract, this document is wrong.

---

## Purpose

IAMApp must materialize subDB as a derived store from provDB.

subDB holds continuity geometry:
- ordering,
- adjacency,
- stitching,
- path structure across time.

subDB must be semantic-free for correctness.
subDB is rebuildable and non-authoritative.

---

## Inputs

- provDB `prov_event` records
- incremental execution under:
  - `architecture/cmp/contracts/materialization_queue.md`

---

## Required Guarantees (IAMApp)

### G1. Semantic-Free Correctness
subDB must be computable from prov identities and ordering/provenance alone.
No embeddings, summarization, or semantic joins are required.

### G2. Deterministic Geometry
Given the same prov inputs and stage_version, subDB produces the same geometry.

### G3. Rebuildability
subDB may be deleted and regenerated from provDB.

### G4. Addressable Paths
subDB must provide stable references to:
- streams/paths,
- nodes within paths,
- adjacency relations,
so the app can support re-entry and legibility.

---

## Minimum Entities (IAMApp)

IAMApp subDB must support:

### `sub_stream` (required)
Fields (minimum):
- `stream_id`
- `stream_type`
- `created_at`

### `sub_node` (required)
Fields (minimum):
- `node_id`
- `prov_event_id`
- `stream_id`
- `t_index` (monotonic order)
- `created_at`
- `supersedes_prov_event_id` (nullable)

### `sub_edge` (required)
Fields (minimum):
- `edge_id`
- `edge_type` (at minimum: `next`)
- `from_node_id`
- `to_node_id`

At minimum, each stream must have a deterministic ordering expressed by:
- `t_index`, and/or
- `next` edges forming a chain.

---

## Meaning Boundary

Meaning is read by clients, not stored as correctness within subDB.

Semantic overlays may be applied above subDB geometry as optional views.
Re-entry and correctness must remain valid without them.

---

## Photos Pattern Alignment

subDB is local by default.
Any sharing/export produces copies and is user-initiated.
No sync requirement defines correctness.

# CMP Contract — subDB
## Continuity Geometry Materialization (Semantic-Free)

This contract defines the minimum required structure and guarantees of subDB.

subDB is a derived store produced from provDB.
subDB exists to hold continuity geometry:
- ordering,
- adjacency,
- stitching,
- path structure across time.

subDB must be semantic-free for correctness.
It must not require semantic joins, embeddings, or inference.

subDB is rebuildable. It must not become authoritative over capture.

---

## Inputs

- Upstream derived store: provDB as defined in `contracts/provdb_contract.md`
- Core unit: `prov_event` records and their stable identities

sub materialization must be able to operate incrementally using:
`contracts/materialization_queue.md`.

---

## Core Guarantees

### G1. Semantic-Free Correctness
subDB MUST be computable from prov identities and ordering/provenance alone.

No semantic overlays, embeddings, or meaning extraction is required.

### G2. Deterministic Geometry
Given the same prov inputs and stage_version, subDB MUST produce the same geometry.

### G3. Rebuildability
subDB must be safe to delete and regenerate from provDB.

### G4. Addressable Paths
subDB MUST support stable references to:
- paths/streams,
- nodes/events within paths,
- adjacency relations.

This is required for re-entry and legibility.

---

## Minimum Data Model

subDB MUST be able to represent the following entities.

### 1) `sub_stream`
A stream is an ordered continuity container.

Required fields:
- `stream_id` (primary key)
- `stream_type` (e.g., `conversation`, `journal`, `import_batch`, `free_form`)
- `created_at`
- `source` (optional; provenance reference)

Streams are structural and may be derived from provenance context.
Stream formation rules must be deterministic for a given stage_version.

### 2) `sub_node`
A node represents a positioned event in continuity geometry.

Required fields:
- `node_id` (primary key)
- `prov_event_id` (stable reference to provDB)
- `stream_id`
- `t_index` (monotonic integer position within stream)
- `created_at` (copied from prov/capture)
- `supersedes_prov_event_id` (nullable)
- `node_kind` (optional structural label; e.g., `utterance`, `note`, `edit`)

Notes:
- `t_index` is the canonical ordering coordinate within a stream.
- Node identity must remain stable for the same prov_event_id and stage_version.

### 3) `sub_edge` (adjacency / stitching)
Edges encode structural relations in geometry.

Required fields:
- `edge_id` (primary key)
- `edge_type` (e.g., `next`, `reply_to`, `supersedes`, `stitch`, `branch`)
- `from_node_id`
- `to_node_id`
- `stream_id` (nullable if cross-stream)
- `weight` (optional; default 1.0)
- `created_at` (optional)

At minimum, subDB MUST represent `next` edges within each stream.

Other edge types may be added, but must remain structural and deterministic.

---

## Geometry Rules (Strict)

### Ordering
Within a stream, nodes must have a deterministic total order.
This is expressed by:
- `t_index`, and/or
- `next` edges forming a chain.

### Stitching
If stitching across streams exists, it must:
- be deterministic,
- be based on provenance or explicit linkage,
- not depend on semantic similarity for correctness.

### Branching
Branches may exist (forks, edits, alternative continuations), but:
- branch structure must remain addressable,
- re-entry must not require semantic interpretation.

---

## Relationship to Meaning

Meaning is read by clients, not stored as correctness within subDB.

Clients may overlay semantic coordinates on top of subDB geometry,
but subDB remains valid and usable without them.

This separation is decisive:
- subDB holds shape,
- meaning is given by client-defined coordinates and metric.

---

## Export / Interop

subDB must support deterministic export for:
- fixture generation (scripts),
- parity testing (Swift vs Python),
- optional server acceleration.

Exports must preserve:
- stable node IDs,
- stream membership and ordering,
- edge relations.

---

## Non-Goals

subDB is NOT:
- a semantic search index,
- an embedding database,
- a summarization layer,
- a coherence engine.

subDB holds continuity geometry as a semantic-free substrate for re-entry and legibility.

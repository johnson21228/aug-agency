# ProvDB Contract (IAMApp)

This document defines IAMApp’s obligations for prov materialization.
It is a local mirror of the authoritative architecture contract:

- `architecture/cmp/contracts/provdb_contract.md`

If this document conflicts with the architecture contract, this document is wrong.

---

## Purpose

IAMApp must materialize provDB as a derived store from the authoritative capture store (`iam.db`).

provDB exists to:
- preserve stable identity mappings from capture events,
- preserve provenance and verbatim text rehydration,
- optionally carry coordinate/metric definitions and overlays (never required for correctness),
- provide deterministic inputs for subDB geometry materialization.

provDB is rebuildable and non-authoritative.

---

## Inputs

- `iam.db` capture events (append-only LUIs)
- LUI packet contract:
  - `architecture/cmp/contracts/lui_packet.md`

Materialization must support incremental execution under:
- `architecture/cmp/contracts/materialization_queue.md`

---

## Required Guarantees (IAMApp)

### G1. Deterministic Identity
For each capture `event_id`, IAMApp produces a stable `prov_event_id`.
Reruns must not create duplicate prov identities for the same capture event.

### G2. Verbatim Rehydration
provDB must preserve or reference verbatim capture text.
No summarization or rewriting occurs at this stage.

### G3. Provenance Preservation
provDB must preserve source/actor and adapter context without interpretation.

### G4. Rebuildability
provDB may be deleted and regenerated from `iam.db` without changing capture authority.

---

## Minimum Entities (IAMApp)

IAMApp provDB must support:

### `prov_event` (required)
Fields (minimum):
- `prov_event_id`
- `capture_event_id`
- `created_at`
- `body_ref` (verbatim text or stable reference)
- `source`
- `actor`
- `supersedes_capture_event_id` (nullable)
- `context_json` (nullable)
- `attachments_json` (nullable)
- `tags_json` (nullable)

### `prov_definition` (optional)
Coordinate/metric definition records may exist.
Definitions are optional and must be replaceable.

### `prov_overlay` (optional)
Optional coordinate assignments to events.
Overlays must never be required for correctness.

---

## Semantics Boundary

Semantic overlays may be present, but:
- they are optional,
- derived,
- replaceable,
- not required for continuity correctness.

No prov materialization step may require external inference.

---

## Photos Pattern Alignment

provDB is local by default.
Any sharing/export produces copies and is user-initiated.
No sync requirement defines correctness.

# CMP Contract — provDB
## Provenance Materialization and Coordinate Definitions

This contract defines the minimum required structure and guarantees of provDB.

provDB is a derived store produced from the authoritative capture store (`iam.db`).
provDB exists to:
- preserve stable identity mappings,
- preserve provenance and verbatim text rehydration,
- define coordinate systems and metrics used to read semantic space (optional overlays),
- provide deterministic inputs for subDB geometry materialization.

provDB is rebuildable. It must not become authoritative over capture.

---

## Inputs

- Authoritative upstream store: `iam.db`
- Canonical event unit: LUI packet as defined in `contracts/lui_packet.md`

prov materialization must be able to operate incrementally using the queue rules in:
`contracts/materialization_queue.md`.

---

## Core Guarantees

### G1. Deterministic Identity Mapping
For every capture event `event_id`, provDB MUST produce a stable mapping to a prov identity.

At minimum:
- `prov_event_id` MUST be stable for a given `event_id` and `stage_version`.
- reruns must not create duplicate prov identities for the same capture event.

### G2. Verbatim Rehydration
provDB MUST preserve or reference the verbatim capture text.

Meaning:
- text is not summarized or rewritten at this stage,
- any derived representation must retain a stable pointer back to verbatim text.

### G3. Provenance Preservation
provDB MUST preserve provenance fields (source, actor, adapter context).

Provenance is stored, not interpreted.

### G4. Rebuildability
provDB must be safe to delete and regenerate from `iam.db` without loss of authoritative history.

---

## Minimum Data Model

provDB MUST be able to represent the following entities.

### 1) `prov_event`
A prov_event corresponds 1:1 with a capture event.

Required fields:
- `prov_event_id` (primary key)
- `capture_event_id` (foreign key or stable reference to `iam.db.event_id`)
- `created_at` (copied from capture)
- `body_ref` (reference or copy of verbatim text)
- `source`
- `actor`
- `supersedes_capture_event_id` (nullable)
- `context_json` (nullable)
- `attachments_json` (nullable)
- `tags_json` (nullable)

Notes:
- `body_ref` may be a string copy or a reference into a shared text table.
- provDB must not require semantic processing to populate these fields.

### 2) `prov_definition` (coordinate / metric definitions)
provDB MAY include definitions that specify how semantic space is read.

Required fields (if present):
- `definition_id` (primary key)
- `definition_type` (e.g., `coordinate_system`, `metric`, `projection`, `labeling_rule`)
- `definition_version`
- `definition_json` (opaque; human-authored or tool-authored)

Definitions are optional and may evolve.

### 3) `prov_overlay` (optional derived coordinate assignments)
provDB MAY include optional overlays that assign coordinates to events.

If present, required fields:
- `overlay_id`
- `definition_id` (points to a coordinate_system + metric definition)
- `prov_event_id`
- `coords_json` (opaque vector/structure)
- `generated_at`
- `generator` (e.g., `foundation_models_local`, `external_llm_one_shot`, `manual`)
- `confidence` (optional)

Overlays must not be required for correctness of provDB or for subDB geometry correctness.

---

## Semantics Boundary (Strict)

provDB may carry semantic coordinate overlays, but:

- semantic overlays are optional,
- must be derived and replaceable,
- must not overwrite or substitute for verbatim capture,
- must not be required for continuity correctness.

Meaning is introduced by clients through definitions and overlays.
provDB stores the material; it does not impose interpretation.

---

## Export / Interop

provDB must support deterministic export for:
- fixture generation (scripts),
- parity testing (Swift vs Python),
- optional server acceleration.

Exports must preserve:
- stable IDs,
- provenance,
- verbatim text references.

---

## Non-Goals

provDB is NOT:
- a summarization database,
- a narrative reconstruction layer,
- a model-centric explainability store.

provDB is a provenance and definition layer that supports continuity and materialization.

# Migrations and Reprocessing Policy (Photos Rule)

This file defines **how IAM evolves without invalidating a user’s corpus**.

The guiding model is “Photos”: originals are preserved; derived structures can be regenerated.

---


## Scope

Applies to all on-device data stores:

- **Capture Store** (e.g., `iam.db`): append-only source-of-record for raw LUIs/events.
- **Provenance Store Family** (e.g., `provdb/*`): ID↔language mapping and numeric semantic coordinate overlays.
- **Substrate Store Family** (e.g., `subdb/*`): semantic-free continuity geometry and Atlas structures.

---

## Core Invariants

### 1) Preserve Originals
- Raw captured events are never deleted or overwritten.
- Any correction or refinement is represented as a **new** event or **new** versioned overlay.

### 2) Reflexive Capture (Artifacts Become Inputs)
- Outputs produced during IAM use (annotations, return points, links, decisions—“gold”) are treated as **first-class inputs**.
- These artifacts are captured **append-only** in the Capture Store (`iam.db`) as new capture events (data), never as operational rules.
- Durable references created by a human must anchor to **capture-stable addresses** (e.g., `capture_id` and optional spans), not to ephemeral build/run IDs.

### 3) Stable Identity
- `capture_id` is stable within the Capture Store.
- Downstream stable IDs (e.g., `event_id`, `continuon_id`) must remain stable once published to other layers.
- Cross-layer composition is always by stable IDs.

### 4) Additive Schema Evolution
- Migrations are forward-only and additive:
  - `CREATE TABLE IF NOT EXISTS ...`
  - `ALTER TABLE ... ADD COLUMN ...`
  - `CREATE INDEX IF NOT EXISTS ...`
- Avoid destructive operations (DROP / DELETE / UPDATE of canonical records).

### 5) Reprocessing Is Versioned
- Derived outputs (canonical text variants, chunking, embeddings, clustering, stitching) are stored as **versioned overlays**:
  - keyed by `run_id`, `space_id`, and/or `substrate_id`
- Multiple generations may coexist.
- “Active” overlays are selected by configuration pointers, not by rewriting history.

### 6) Correctness Does Not Depend on Semantics
- Substrate correctness must not depend on presence of semantic overlays.
- Numeric semantic coordinates may be replicated into SubDB only as **optional overlays**, always namespaced and versioned.

---

## Versioning Mechanism

Each SQLite DB must maintain a schema version using one of:

- `PRAGMA user_version`, or
- a `meta` table containing:
  - `schema_version`
  - `created_at`
  - `app_build`
  - optional `notes`

All migrations must be deterministic and idempotent.

---

## Migration Types

### A) Schema Migration (Additive)
Used for:
- adding columns/tables/indexes
- introducing new adapter support fields
- adding new overlay tables

Constraints:
- no row rewrites in the Capture Store
- no destructive rebuild of authoritative mappings

### B) Reprocessing / Rebuild (Derived Overlays)
Used for:
- new canonicalization rules
- new chunking strategy (FM constraints change)
- new embedding models / dimensions
- new Atlas stitching algorithms

Constraints:
- old overlays remain valid and queryable
- new overlays are appended under new version identifiers
- switching “active” overlay is a pointer update

### C) Compaction / Pruning (Optional, Controlled)
Used to manage growth.

Constraints:
- must never delete capture originals
- may delete *derived* overlays only if:
  - the app can regenerate them, and
  - the user has opted in (or policy explicitly permits), and
  - required “active” overlays are preserved

---

## Operational Requirements

### Idempotence
Running a migration or reprocessing step twice must not corrupt data or duplicate authoritative records.

### Crash Safety
- Use transactions for each migration step.
- Write new overlays fully before switching “active” pointers.
- Prefer “write-new then flip pointer” over in-place modification.

### Auditability
- Overlay tables should record:
  - `space_id` / `run_id`
  - creation time
  - build parameters (JSON)
  - upstream fingerprints (optional)

---

## What This File Must Not Contain

- No volatile implementation details (exact file paths, UI flows, or per-feature code behavior).
- No “one true schema” for future layers beyond stable invariants and versioning rules.
- No semantic algorithms (embedding methods, clustering heuristics, prompt templates).
- No product promises or timelines.
- No secrets, tokens, account identifiers, or user-specific data.

---

## Definition of Done for a Safe Upgrade

An upgrade is safe when:

- Capture originals remain intact and addressable.
- Schema version increases without destructive operations.
- New overlays are written as new versions without overwriting old ones.
- The app can fall back to previous overlays if reprocessing fails.

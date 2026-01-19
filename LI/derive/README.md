# LI.derive — Functional Append-only Derivation Layer

This scope defines the contract for background derivation that transforms
append-only captured LUIs in `iam.db` into derived artifacts (chunks, semantic
coordinates, continuity nodes) suitable for storage in `SubDB`.

## Core Invariant: Append-only Functional Style

1) Capture is immutable:
- `iam.db` is append-only and authoritative for raw LUIs.

2) Derivation is functional:
- Derivation is a pure function of:
  - referenced source LUIs (by stable IDs)
  - a versioned derivation recipe/policy
  - an engine descriptor/version (Apple Foundation Models, local LLM, etc.)
  - declared budgets (token/bytes/latency)

3) Outputs are appended, not updated:
- Derived artifacts are written as new records.
- Existing derived artifacts are never overwritten.

4) Supersession is referential:
- Replacement occurs by appending a new artifact record and referencing the prior
  record(s) via `supersedes[]`, plus setting `status="superseded"` (or equivalent)
  without deleting history.

## Engine Boundary

This scope does not bind to any specific inference engine API. It requires:
- provenance and determinism metadata on all derived artifacts
- budget compliance (work must fit bounded-context inference)
- recomputability and auditability (no “magic” untraceable embeddings)

See:
- `ContinuityNodeContract.md`
- `ChunkingContract.md`
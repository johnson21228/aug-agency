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

## Pipeline Execution Invariant: Restartable Chew Loop

The entire pipeline is a restartable chew-loop system.

- Work proceeds by repeatedly reading append-only data and appending derived artifacts.
- Continuous uptime is not assumed. Stages may stop and resume arbitrarily.
- “Always chewing” is achieved by restart + replay safety, not by holding mutable state.

A stage operating under this invariant MUST satisfy:

1) Append-only inputs:
- The stage consumes immutable upstream records (e.g., `iam.db` capture LUIs, chunk records).

2) Durable monotonic progress:
- The stage maintains a durable checkpoint (cursor) representing progress.
- The checkpoint MUST be persisted and monotonic.
- The stage MUST tolerate re-reading previously seen inputs.

3) Idempotent outputs:
- Reprocessing the same input range MUST NOT create duplicate effective outputs.
- If outputs differ due to recipe/engine/version changes, new outputs are appended and
  linked by supersession or version references; history is not rewritten.

4) Provenance completeness:
- Every derived artifact MUST record sufficient provenance to explain:
  - which inputs were used
  - which recipe/policy was applied
  - which engine/version produced the result
  - when it was derived

## Insight is read-time, not write-time

The system does not require “final meaning” to be produced at ingest. Insight is produced by
reading raw capture and derived artifacts as they are:

- raw capture (iam.db)
- derived artifacts (chunks, semantic coordinates, continuity nodes)
- composed views at query time

Capture remains raw and truthful; derivations remain replaceable; insight can evolve without
rewriting history.

## Engine Boundary

This scope does not bind to any specific inference engine API. It requires:
- provenance and determinism metadata on all derived artifacts
- budget compliance (work must fit bounded-context inference)
- recomputability and auditability (no “magic” untraceable embeddings)

See:
- `ContinuityNodeContract.md`
- `ChunkingContract.md`
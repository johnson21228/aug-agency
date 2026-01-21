# LI/ingest/invariants.md

## Scope

These invariants define the **ingest boundary**: external input must enter IAM only as LUIs and must append into the capture authority (`iam.db`) without rewriting history.

This document is canonical for LI.ingest. If code or contracts diverge from these invariants, the divergence must be treated as an error.

---

## Definitions (Terms used in this scope)

### LUI (Language Use Input)
An LUI is the admissible unit of external input at the ingest boundary. LUIs are accepted only through declared ingest interfaces and are recorded into the capture authority.

### Capture Authority (`iam.db`)
The append-only store that records accepted LUIs in a durable, replay-safe way and provides a stable ordering surface for downstream derivation.

### Block-canonical capture (this scope)
For sources capable of emitting a maximal “experience block” (e.g., an entire ChatGPT conversation main-branch transcript), ingest MUST treat the block as the canonical capture unit. Any segmentation into smaller nodes (turns/chunks/macroturns) is downstream/derived (“chewing artifacts”).

### Turn / Node (derived, not canonical)
A “turn” or “node” is a derived segmentation of a captured block. Multiple segmentations may exist simultaneously and must be reproducible from canonical capture.

### Export replay (snapshot re-run)
A repeated run of an offline/export adaptor over overlapping historical data. Replay is expected and must not duplicate capture.

---

## Invariants

### I0 — Bootstrap state validity (empty or missing capture store)

The system MUST treat an empty or non-existent `iam.db` as a valid initial condition.

- The absence of `iam.db` or the absence of capture rows denotes “no captured history,” not an error.
- Ingest MUST be able to initialize the capture store schema and begin accepting LUIs from this state.
- Append-only, idempotency, and replay-safety invariants apply from the first accepted record onward.

---

### I1 — LUI-only input
No data enters IAM except as an LUI (or batch of LUIs) expressed through a declared ingest interface.

### I2 — Append-only capture authority
Ingest operations must only append new capture events to `iam.db`. Existing capture events must not be rewritten, merged, or deleted as part of ingest.

### I3 — Immutability after commit (or equivalent append finalization)
After an ingest operation is accepted as committed (or appended), the stored capture record must be treated as immutable.

### I4 — Idempotent ingest
A stable client-side idempotency key (e.g., `client_lui_id`) must prevent duplicate capture records when requests are retried or replayed.

### I5 — Conflict detection on replay
If the same idempotency key is replayed with materially different content, the ingest boundary must reject the replay (e.g., 409 CONFLICT) rather than silently accepting drift.

### I6 — Deterministic ordering surface
Ingested LUIs must be associated with a stable deterministic order suitable for downstream processing. The ordering surface must not be user-curated narrative order.

### I7 — No reconstruction implication at ingest boundary
The ingest boundary must not imply reconstruction of past cognition from summaries or snapshots. It accepts capture and provides bounded retrieval consistent with contract.

### I8 — Capture schema authority
The capture schema (migrations) is authoritative. Ingest implementations must conform to it rather than invent parallel capture stores.

---

### I9 — Block-canonical capture (maximal breadth preserved)

For sources that can provide a maximal experience block, ingest MUST accept and store the **block** as the canonical capture unit in `iam.db`.

- Canonical capture MUST preserve full breadth losslessly (no segmentation required for correctness).
- Any segmentation into smaller nodes (turns, chunks, macroturns, topic blocks) MUST be treated as derived output and MUST NOT be required at ingest time.
- Derived segmentations MAY exist in multiple concurrent versions (e.g., `turns.v1`, `macroturns.v1`) and MUST be reproducible from canonical blocks without rewriting canonical capture.

---

### I10 — Export replay semantics (snapshot re-run safety)

Offline/export adaptors may be re-run against overlapping snapshots (e.g., multiple ChatGPT exports over time). Ingest MUST remain replay-safe under such replays.

- Replay MUST NOT create duplicate capture rows for already-ingested canonical blocks (idempotency).
- If a replay attempts to ingest a block for the same source identity but with different content, that difference MUST be represented as a new canonical block version (new idempotency key), not as an overwrite.

---

### I11 — Block identity versioning (append without overwrite)

If a source’s “block” can evolve by append (e.g., a conversation grows), then canonical block identity MUST be versioned such that:

- each distinct block content corresponds to a distinct idempotency key, and
- previously captured block versions remain immutable and preserved.

A conforming implementation MUST support at least one stable versioning strategy for block identity (e.g., a hash of normalized block content incorporated into `client_lui_id`).

---

## Minimal Executable Test Surface (Conformance)

Any ingest implementation claiming conformance must pass tests that demonstrate:

1. **Append:** a new canonical block ingest request increases canonical capture count by one.
2. **Replay:** the same canonical block request replayed does not increase canonical capture count.
3. **Stable identity:** replay returns the same capture identifier (or equivalent).
4. **Conflict:** replay with same idempotency key but different content is rejected.
5. **Ordering:** a sequence of new ingests yields a monotonic capture identifier or equivalent stable ordering surface.
6. **Block-canonical:** canonical capture is valid without any pre-segmentation into turns.
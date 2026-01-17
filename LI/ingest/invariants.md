# LI/ingest/invariants.md

## Scope

These invariants define the **ingest boundary**: external input must enter IAM only as LUIs and must append into the capture authority (`iam.db`) without rewriting history.

This document is canonical for LI.ingest. If code or contracts diverge from these invariants, the divergence must be treated as an error.

---

## Invariants

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

## Minimal Executable Test Surface (Conformance)

Any ingest implementation claiming conformance must pass tests that demonstrate:

1. **Append:** a new ingest request increases capture-event count by one.
2. **Replay:** the same request replayed does not increase capture-event count.
3. **Stable identity:** replay returns the same capture identifier (or equivalent).
4. **Conflict:** replay with same idempotency key but different content is rejected.
5. **Ordering:** a sequence of new ingests yields a monotonic capture identifier or equivalent stable ordering surface.

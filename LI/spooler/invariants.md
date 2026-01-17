# LI/spooler/invariants.md

## Scope

These invariants define the **durable outbox semantics** for the spooler.

## Invariants

### S1 — No capture authority
The spooler MUST never write to `iam.db` or claim capture authority.

### S2 — Durable enqueue
Accepted requests MUST be persisted to stable storage before acknowledgement.

### S3 — Immutability after enqueue
Once an LUI envelope is enqueued, it MUST not be modified.

### S4 — Idempotent enqueue
A stable idempotency key (`client_lui_id`) MUST prevent duplicate outbox entries.

### S5 — Retry without loss
Failed delivery MUST NOT drop or mutate queued LUIs.

### S6 — Explicit acknowledgment
LUIs may be removed from the outbox only after ingest-server acceptance.

### S7 — Conflict visibility
If ingest-server returns a conflict, the spooler MUST surface the error and
halt or mark conflict per policy (no silent skipping).

## Minimal Executable Test Surface

1. Enqueue persists an LUI.
2. Replay enqueue does not duplicate.
3. Conflicting replay returns 409 and does not mutate stored envelope.
4. Drain success removes LUI from outbox.
5. Drain failure leaves LUI intact.
6. Capacity limits reject intake explicitly.

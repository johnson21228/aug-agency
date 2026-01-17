# LI/spooler/invariants.md

## Scope

These invariants define the **durable outbox semantics** for the spooler.

## Invariants

### S1 — No capture authority
The spooler must never write to `iam.db` or claim capture authority.

### S2 — Durable enqueue
Accepted requests must be persisted to stable storage before acknowledgement.

### S3 — Immutability after enqueue
Once an LUI envelope is enqueued, it must not be modified.

### S4 — Idempotent enqueue
A stable idempotency key must prevent duplicate outbox entries.

### S5 — Retry without loss
Failed delivery attempts must not drop or mutate queued LUIs.

### S6 — Explicit acknowledgment
LUIs may be removed from the outbox only after ingest-server acceptance.

### S7 — Conflict visibility
If ingest-server returns a conflict, the spooler must surface the error and
halt or skip per operator policy.

## Minimal Executable Test Surface

1. Enqueue persists an LUI.
2. Replay enqueue does not duplicate.
3. Drain success removes LUI from outbox.
4. Drain failure leaves LUI intact.

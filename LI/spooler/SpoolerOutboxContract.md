# LI/spooler/SpoolerOutboxContract.md

Version: 0.2
Status: Canonical

## Purpose

The spooler provides an **always-available intake surface** that decouples
external capture from ingest-server availability.

It accepts REST input, normalizes it into LUIs, and durably queues them
until successful delivery to the ingest server.

## Scope

The spooler:
- accepts REST intake
- emits only LUI envelopes
- persists LUIs durably
- retries delivery safely

The spooler does **not**:
- write to `iam.db`
- infer meaning
- claim canonical sequencing

## Interface (v0)

- `POST /v1/spool` (enqueue one LUI envelope)
- `POST /v1/drain` (attempt delivery to ingest server)
- `GET /health`
- `GET /v1/status` (queued counts only)

## Output Contract

All outbound traffic from the spooler MUST conform to:
- `architecture/ingestion-server/IngestServerContract.md` (LUI envelope shape)

## Authority Boundary

Capture authority begins only after successful ingest-server acceptance.

---

## Resource Envelope (v0)

The spooler must operate correctly on constrained, always-on hardware.

### Target Platform Class
- Architecture: ARM64
- Reference device: Raspberry Pi 5 (≤16 GB RAM)
- Storage: persistent local storage (SSD preferred; SD card permitted)

### Memory Discipline
- Correctness MUST NOT require queued LUIs to be resident in memory.
- All durable state MUST be streamable from disk.

### Intake Limits
- Maximum request body size: **256 KB**
- Maximum serialized LUI envelope at rest: **512 KB**
- Oversized requests MUST be rejected before enqueue.

### Outbox Capacity
- Capacity is disk-bounded, not RAM-bounded.
- Default limits:
  - `OUTBOX_MAX_ITEMS`: 2,000,000
  - `OUTBOX_MAX_BYTES`: 20 GB
- Limits MUST be configurable but enforced.

### Backpressure Semantics
- When capacity limits are reached:
  - New intake MUST be rejected explicitly.
  - The spooler MUST NOT accept and later drop data.

### Drain Semantics
- Drain MUST occur in bounded batches.
- Network failure MUST NOT drop or mutate queued items.
- Conflicts from ingest server MUST be recorded and surfaced.

### Durability Requirement
- Enqueue acknowledgment MUST occur only after durable write.

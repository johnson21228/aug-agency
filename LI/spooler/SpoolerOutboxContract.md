# LI/spooler/SpoolerOutboxContract.md

Version: 0.1
Status: Canonical

## Purpose

The spooler provides an **always-available intake surface** that decouples
external capture from ingest-server availability.

It accepts REST input, normalizes it into LUIs, and durably queues them
until successful delivery to the ingest server.

## Scope

The spooler:
- accepts any REST payload
- emits only LUI envelopes
- persists LUIs durably
- retries delivery safely

The spooler does **not**:
- write to `iam.db`
- infer meaning
- reorder history beyond arrival order
- claim canonical sequencing

## Interface (v0)

- `POST /v1/spool`
- `POST /v1/drain`
- `GET /health`

## Output Contract

All outbound traffic from the spooler **must conform** to
`IngestServerContract.md`.

## Authority Boundary

Capture authority begins only after successful ingest-server acceptance.

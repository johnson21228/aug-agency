# LI/ingest/README.md

This LI scope defines the **ingestion boundary** for IAM:

- What constitutes admissible capture input (LUIs)
- What must be append-only and immutable
- What ordering and idempotency guarantees are required
- What schema surfaces are authoritative
- What tests define executable conformance

This scope is intended to be packed and audited as part of the repository’s canonical language infrastructure.

See `index.source.yaml` / `index.source.json` for the authoritative source list.

---

## Pipeline execution model

Ingest participates in a restartable chew-loop pipeline.

- Ingest may be down or restarted; upstream spooler capture must continue.
- When ingest returns, backlog is drained and appended without rewriting history.
- Downstream derivation consumes append-only capture using durable monotonic checkpoints.

The canonical execution invariant is defined in `LI/derive/README.md`.
# LI/spooler/README.md

This LI scope defines the **spooler / outbox boundary** for IAM.

The spooler is an **always-on intake surface** that:
- Accepts REST input **only when a stable idempotency key (`client_lui_id`) is present**
- Normalizes input into LUI envelopes
- Persists LUIs durably in a local outbox
- Pushes LUIs to the ingest server when available

“Accepts REST input” means:
- The payload shape may be arbitrary JSON
- Replay-safety requires an explicit idempotency key (`client_lui_id`)

The spooler **is not capture authority**.
It must never write to `iam.db`.

The spooler exists to decouple capture availability from capture authority uptime.
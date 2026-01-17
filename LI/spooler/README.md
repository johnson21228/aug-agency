# LI/spooler/README.md

This LI scope defines the **spooler / outbox boundary** for IAM.

The spooler is an **always-on intake surface** that:
- Accepts arbitrary REST input
- Normalizes input into LUI envelopes
- Persists LUIs durably in a local outbox
- Pushes LUIs to the ingest server when available

The spooler **is not capture authority**.
It must never write to `iam.db`.

The spooler exists to decouple capture availability from capture authority uptime.

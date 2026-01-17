# LI/sources/README.md

## Scope

This scope defines **Language Use Instance (LUI) sources**.

Sources:
- originate language-use artifacts
- normalize artifacts into LUIs
- emit LUIs to the spooler boundary

Sources do **not**:
- write to iam.db
- infer meaning
- assign canonical ordering

## Shared Invariants

- Deterministic LUI generation
- Stable `client_lui_id` per source artifact
- Idempotent replay safety
- Lossless payload preservation
- Explicit handoff to spooler via REST

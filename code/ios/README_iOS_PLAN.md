# IAM iOS App — Deferred Implementation Plan

## Status
**INTENTIONALLY DEFERRED**

The iOS app work is intentionally paused while the desktop / script-based
ingestion pipeline is stabilized and finalized.

Do **not** modify the existing Apple sample app or introduce IAM-specific
changes until the ingestion invariants described below are complete and
repeatable.

This file exists to:
- Preserve design intent
- Prevent premature UI or storage decisions
- Ensure the iOS app mirrors the ingestion substrate correctly

---

## Current iOS Context

- `IAMApp` (Apple Foundation Models sample) lives under:

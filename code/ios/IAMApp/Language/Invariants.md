# IAMApp Invariants

These invariants constrain all implementation choices for the IAM iOS app.
They must not conflict with repository-level architecture invariants.

If code and language disagree, code is wrong.

---

## I1. Append-Only Capture

All captured LUIs are append-only.
No LUI event is modified or deleted in place.

Corrections or reinterpretations appear as new events.

---

## I2. Stable Event Identity

Each LUI event has a stable identifier.
Identity is not derived from semantic content.

Identifiers persist across sessions, rebuilds, and upgrades.

---

## I3. No Semantics Required for Correctness

The app must not require embeddings, summaries, clustering, or inference to:

- capture LUIs,
- preserve continuity,
- re-enter a path.

Semantic layers are optional, derived, and rebuildable.

---

## I4. Conversational Surface, Continuity First

The primary interaction surface is conversational.

Conversation is a view over continuity, not the continuity itself.
Conversation history must not become the authoritative store.

---

## I5. Perspective Reversibility

Any perspective change (along-path, neighborhood, global) must allow
return to a specific continuity position without reconstruction.

Zooming out must not erase re-entry.

---

## I6. Local Data Residency by Default

Substrate and derived stores reside locally by default.

Sharing and export:
- are explicit,
- are user-initiated,
- produce copies.

No background upload is required for correctness.

---

## I7. Pipeline Parity with Repo Scripts

Processing stages implemented in IAMApp must match the stage boundaries
and patterns established by the repo’s desktop scripts.

If IAMApp deviates, the deviation must be written as a local decision
record in `Language/Decisions/`.

---

## I8. Multi-Source LUI Capture

The ingest layer must accept multiple LUI sources, including:

- direct text entry,
- share sheet input,
- clipboard capture (user-triggered),
- imported files or transcripts,
- app-internal captures.

All sources normalize into a common LUI event format without interpretation.

---

## I9. Optional One-Shot External Inference

External LLM calls, when used:

- are one-shot,
- are credential-gated,
- are not required for correctness.

External inference may only enrich derived views.

---

## I10. Photos Pattern: Authoritative Local Library

The app MUST treat local storage as the authoritative library.

- The app must function correctly offline for capture and re-entry.
- Sharing and export must be explicit and user-controlled.
- Sync must be optional and must not define correctness.
- Export produces copies; it does not relocate authority.

---

## I11. Authority and Workflow

Language specifications are authoritative.

- Design changes originate in `Language/`.
- Swift code implements language-defined intent.
- Xcode is used for editing, debugging, previews, and deployment.

Xcode is not a source of system intent.

---

## I12. Small Files and Spec Traceability

Swift implementation must prefer small, concept-scoped files.

Every Swift file MUST include a governing spec reference:

```swift
// Governed by: Language/Specs/<NNN_Name>/Spec.md

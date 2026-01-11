# IAMApp Invariants

These invariants constrain all implementation choices for the IAM iOS app.

They apply regardless of:
- runtime (foreground, background),
- execution environment (device, optional server),
- availability of models or network access.

If code and language disagree, code is wrong.

---

## I1. Continuity Is Primary

The app exists to preserve and support a single human’s continuity over time.

Continuity is defined as:
- ordered personal language-use events,
- preserved across time,
- addressable for re-entry.

No feature may compromise continuity preservation.

---

## I2. Append-Only Capture

All captured LUIs are append-only.

- No LUI event is modified or deleted in place.
- Corrections, reinterpretations, or edits appear as new events.
- History is preserved, not rewritten.

---

## I3. Stable Event Identity

Each LUI event has a stable identifier.

- Identity is not derived from semantic content.
- Identifiers persist across:
  - sessions,
  - rebuilds,
  - app upgrades,
  - materialization runs.

---

## I4. No Semantics Required for Correctness

The app must not require:
- embeddings,
- summaries,
- clustering,
- inference,
- external services,

to:
- capture LUIs,
- preserve continuity,
- support re-entry.

Semantic layers are optional, derived, and rebuildable.

---

## I5. Authoritative vs Derived Stores

The following authority boundaries are strict:

### Authoritative
- `iam.db` (capture store)

### Derived (Rebuildable)
- provDB
- subDB
- all views, indexes, overlays, projections

Derived stores may be deleted and regenerated without loss of continuity.

---

## I6. Conversational Surface Is a View

The primary interaction surface is conversational.

Conversation is:
- a view over continuity,
- not the continuity itself.

Conversation history must never become the authoritative store.

---

## I7. Re-entry Without Reconstruction

The app must support re-entry into continuity without requiring:
- summaries,
- recomputation of meaning,
- reinterpretation of past events.

A user must be able to return to a position in continuity
using structural references alone.

---

## I8. Perspective Reversibility

All perspective changes must be reversible.

This includes:
- moving along a path,
- zooming out to neighborhoods or global views,
- switching between views.

Zooming out must not erase the ability to return.

---

## I9. Continuity Materialization Pipeline (CMP) Parity

Processing stages in IAMApp must follow the same stage boundaries
defined by the Continuity Materialization Pipeline (CMP):

- Stage 0: Capture (`iam.db`)
- Stage 1: Derived views
- Stage 2: prov materialization
- Stage 3: sub materialization

IAMApp must not collapse stages or introduce hidden dependencies.

---

## I10. Deterministic, Idempotent Materialization

All materialization stages must be:
- deterministic for a given input and stage version,
- safe to rerun without corrupting upstream stores,
- cursor- or range-based.

Failures must not corrupt authoritative data.

---

## I11. Semantic-Free Geometry Correctness

subDB correctness must not depend on semantics.

Geometry is defined by:
- ordering,
- adjacency,
- stitching,
- path structure.

Meaning is applied by clients, not required for geometry correctness.

---

## I12. Multi-Source LUI Capture

The app must support multiple LUI sources, including:
- direct text entry,
- share sheet input,
- user-triggered clipboard capture,
- imported files or transcripts,
- app-internal captures.

All sources normalize into the same LUI event model.

---

## I13. Optional External Inference

External inference (when enabled):

- is one-shot,
- is credential-gated,
- is optional,
- must not define correctness.

External results may enrich derived views only.
They must never overwrite capture content.

---

## I14. Photos Pattern: Local Library Authority

IAMApp follows the Photos pattern:

- the on-device library is authoritative by default,
- sharing and export are explicit and user-initiated,
- exports produce copies,
- sync is optional and must not define correctness.

If a server exists, it is an accelerator only.
It must not become authoritative.

---

## I15. Offline Correctness

The app must function correctly offline for:
- capture,
- continuity preservation,
- re-entry.

Network access may enhance derived views but must not be required.

---

## I16. Language Governs Implementation

Language specifications are authoritative.

- Design changes originate in `Language/`.
- Swift code implements written intent.
- Xcode is used for editing, debugging, previews, and deployment.

Xcode is not a source of system intent.

---

## I17. Small Files and Traceability

Implementation must prefer small, concept-scoped Swift files.

Every Swift file MUST include a governing spec reference:

```swift
// Governed by: Language/Specs/<NNN_Name>/Spec.md

# Runtime Behavior — Attention Capture and Breadcrumb Formation

## Purpose

This document specifies the runtime behavioral contracts governing how IAM
captures experienced language events and incorporates them into continuity
storage.

This file defines *what MUST occur* when language crosses an attention boundary.
It does not define UI, platform APIs, or embedding implementations.

---

## 1. Attention Boundary Events

An attention boundary event occurs when a user explicitly acts to bring language
into focus.

Examples include (but are not limited to):
- pasting language from the system clipboard
- explicitly capturing selected text
- importing conversational history
- invoking an explicit “anchor” or “capture” action

Attention boundary events are **explicit** and **user-controlled**.
Passive or silent capture is prohibited.

An attention boundary event signifies that language has been *experienced* rather
than merely observed.

---

## 2. Breadcrumb Formation

Upon an attention boundary event, IAM MUST perform the following steps:

1. Capture the language payload, or a stable hash thereof
2. Record the time of capture
3. Compute a numeric representation using a configured embedding instrument
4. Append a new breadcrumb record to SubDB

This operation MUST be append-only.

Breadcrumbs are measurements, not interpretations.

---

## 3. SubDB Append Semantics

Each breadcrumb append MUST include:

- a monotonically increasing sequence identifier
- a timestamp (capture time)
- a reference to the numeric embedding vector
- optional provenance metadata (e.g., source type, import identifier)

SubDB records MUST remain immutable once written.

---

## 4. Non-Interpretation Invariant

Runtime behavior MUST NOT:

- summarize language
- infer meaning
- classify topics
- assert correctness or importance
- collapse multiple language events into a single breadcrumb

IAM captures *that* a language event occurred, not *what it means*.

---

## 5. Bulk Import Behavior

Bulk import operations (e.g., ChatGPT history export) are treated as
user-initiated attention boundary events.

During import, IAM MUST:

1. Parse the source archive into ordered language events
2. Preserve original timestamps when available
3. Apply deterministic ordering when timestamps are absent
4. Compute breadcrumbs for each event
5. Append each event as a distinct SubDB record

Imports MUST be idempotent.
Re-importing the same source MUST NOT produce duplicate records.

---

## 6. Privacy and Agency Constraints

Attention boundary capture MUST satisfy the following:

- capture MUST be explicit
- capture MUST be user-initiated
- capture MUST be visible or intentional in UX
- capture MUST be locally controlled

IAM MUST NOT silently capture language outside an attention boundary.

---

## 7. Failure Handling

If embedding computation fails:

- the language payload MAY still be recorded
- the breadcrumb record MUST indicate missing or deferred embedding
- no retroactive modification of SubDB records is permitted

Deferred embeddings MAY be computed later, but MUST result in a new append or
explicit linkage, not mutation.

---

## 8. Relationship to Runtime Navigation

Breadcrumbs produced by this behavior layer:

- serve as inputs to anchoring
- support adjacency and path projection
- enable revisiting and re-orientation

Breadcrumbs do not encode meaning or navigation decisions.

---

## Summary

When language crosses an attention boundary:

- a breadcrumb is formed
- a numeric coordinate is computed
- a time-ordered append to SubDB occurs

Runtime behavior preserves continuity of experience.
Meaning remains human.
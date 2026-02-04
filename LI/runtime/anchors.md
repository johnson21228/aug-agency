# Runtime Anchors — Language Infrastructure (LI)

## Purpose
This document specifies anchor semantics for the IAM runtime layer.
Anchors define the local origin from which charts are constructed and semantic navigation occurs.

Anchors are runtime constructs derived from events recorded in iam.db.
They are not substrate authority unless explicitly written back as user-authored annotations.

---

## 1. Definitions

### 1.1 Anchor
An anchor is a reference to a specific, experienced event (or short contiguous segment) recorded in iam.db.

Formal definition:
anchor := { event_id [, segment_window] }

Anchors MUST resolve to concrete substrate events.
Anchors MUST NOT reference abstractions, inferred concepts, summaries, or centroids.

---

### 1.2 Anchor Types
Two anchor types are defined. Their semantics and persistence rules are distinct.

Ephemeral Anchor (last_anchor):
- Automatically updated
- Freely overwritable
- Non-semantic
- Defines the current runtime origin

The ephemeral anchor represents where the user last stood.

Declared Anchor:
- Explicitly created by the user
- Durable across sessions
- May be named and/or annotated
- Represents user judgment

Declared anchors encode human-recognized significance.

---

## 2. Grounding Invariant

Invariant A1 — Event Grounding  
All anchors MUST reference one or more concrete events in iam.db via event_id.

The system MUST NOT create anchors that are not traceable to experienced substrate events.

---

## 3. Default Anchor Rule

Invariant A2 — Continuity Default  
After ingestion of a new user-authored LUI:
last_anchor := event_id

This rule establishes a deterministic runtime origin without asserting semantic importance.

Assistant-authored LUIs MUST NOT update last_anchor unless explicitly configured.

---

## 4. Persistence Semantics

### 4.1 Ephemeral Anchor Persistence

Invariant A3 — Runtime-Only Authority  
last_anchor MAY be persisted as runtime state to support session resume (“Last here”).

last_anchor:
- is non-authoritative
- MUST be overwritable
- MUST be reconstructible from substrate plus runtime state

last_anchor MUST NOT be written to iam.db as semantic content.

---

### 4.2 Declared Anchor Persistence

Declared anchors MAY be persisted:
1. as runtime state, or
2. as user-authored annotation events referencing event_id

Invariant A4 — Human Authorship Only  
If persisted to substrate, declared anchors MUST be written as user-authored LUIs.
The system MUST NOT author or infer declared anchors.

---

## 5. Anchor Suggestion Policy

The system MAY suggest candidate anchors.

Invariant A5 — Structural Justification Only  
Anchor suggestions MUST be justified exclusively by structural signals, including:
- revisit frequency
- branch or divergence points
- phase transitions
- local curvature density

The system MUST NOT:
- auto-select anchors
- promote suggestions without confirmation
- present semantic conclusions as justification

Each suggestion MUST include an explicit structural reason.

---

## 6. Anchor Authority Boundaries

Invariant A6 — No Silent Re-Anchoring  
The system MUST NOT change the active anchor without explicit user action,
except for updates to last_anchor per Invariant A2.

Anchor changes MUST be observable.

---

## 7. Relationship to Charts and Manifold

Anchors:
- define the origin for chart construction
- bound the validity of local tangent spaces
- constrain neighborhood selection

Anchors do NOT:
- define global semantic structure
- impose meaning
- collapse alternative interpretations

---

## 8. Example (Non-Normative)

Scenario: Runtime Anchor Lifecycle

1. User enters a new LUI (event_id = E42).
2. Ingest appends E42 to iam.db.
3. Runtime updates last_anchor := E42.
4. A local chart is constructed around E42.
5. The system suggests E17 as a candidate anchor, citing multiple revisits and branch divergence.
6. The user explicitly declares E17 as a named anchor: “Idea crystallization.”
7. E17 is persisted as a user-authored annotation event.

At no point does the system infer or assign semantic importance.

---

## 9. Non-Goals

This specification explicitly excludes:
- UI gesture definitions
- visualization requirements
- global semantic metrics
- automated importance ranking

---

## Summary

Anchors establish the human-supplied origin of the IAM runtime.

They preserve continuity, constrain semantics locally, and prevent system-imposed meaning.

No anchor → no chart.
No chart → no tangent space.
No tangent space → no navigable meaning.
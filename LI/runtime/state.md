# Runtime State — Language Infrastructure (LI)

## Purpose
This document specifies what runtime state the IAM system may persist and how that state relates to the authoritative substrate (iam.db).

Runtime state exists to preserve continuity of attention, not to assert semantic authority.

---

## 1. Authority Boundary

Invariant S1 — Substrate Authority  
iam.db is the sole authoritative record of experienced events.

Runtime state MUST be:
- derived from substrate events and user-authored annotations
- rebuildable from substrate plus runtime state files
- non-authoritative with respect to meaning

Runtime state MUST NOT replace, mutate, reinterpret, or reorder substrate history.

---

## 2. Permitted Runtime State

### 2.1 Ephemeral Anchor State

last_anchor := { event_id [, segment_window] }

Invariant S2 — Ephemeral Continuity  
last_anchor MAY be persisted to support session resume (“Last here”).

Properties:
- overwritable
- non-semantic
- reflects the most recent experiential position

last_anchor MUST NOT encode inferred meaning, importance, or semantic labels.

---

### 2.2 Declared Anchors

declared_anchors := [
  { event_id, label?, note?, created_at }
]

Declared anchors MAY be persisted as:
- runtime state, and/or
- user-authored annotation events in iam.db

Declared anchors represent user judgment, not system inference.

---

### 2.3 Optional Session Hints

The runtime MAY persist lightweight session hints, such as:
- last active chart identifier
- preferred neighborhood radius
- last traversal mode

Invariant S3 — No Semantic Caching  
Session hints MUST NOT encode semantic conclusions, rankings, embeddings, or inferred importance.

---

## 3. Prohibited Runtime State

The runtime MUST NOT persist:
- inferred semantic labels
- global embeddings or vector representations
- automated importance rankings
- cached chart coordinates as authority
- system-generated summaries treated as ground truth

All derived semantic structure MUST be recomputable on demand.

---

## 4. Rebuild Guarantee

Invariant S4 — Reconstructibility  
Given:
- iam.db
- runtime state files (if present)

The runtime MUST be able to reconstruct:
- the current anchor position
- declared anchors
- navigable charts and manifold projections

Loss or corruption of runtime state MUST NOT corrupt substrate integrity or experiential continuity.

---

## 5. Session Resume Semantics

On startup or resume:
1. If last_anchor exists, resume at that anchor.
2. Otherwise, select the most recent user-authored event in iam.db.

This rule preserves continuity without asserting semantic importance.

---

## 6. Write-Back Constraints

Invariant S5 — Human Authorship Only  
Only explicitly user-authored actions may result in runtime state being written back to substrate.

The system MUST NOT write inferred runtime state, rankings, or semantic interpretations to iam.db.

---

## Summary

Runtime state preserves where the user is, not what it means.

It exists to support continuity of attention, safe navigation, and rebuildable semantics, while keeping authority anchored in lived experience.
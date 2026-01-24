# Runtime Charts — Language Infrastructure (LI)

## Purpose
This document specifies charts as the local semantic coordinate systems used by the IAM runtime.

Charts enable differential semantic navigation relative to an anchor without asserting global meaning or semantic authority.

---

## 1. Definition

A chart is a local, anchor-scoped projection constructed from a neighborhood of experienced events.

Formal definition:
chart := {
  anchor_event_id,
  neighborhood,
  basis_axes,
  local_coordinates
}

Charts are:
- local
- derived
- ephemeral
- rebuildable

Charts MUST NOT be treated as authoritative representations of meaning.

---

## 2. Chart Scope

Invariant C1 — Anchor Scope  
Each chart MUST be constructed relative to a single active anchor.

Charts MUST NOT span unrelated anchors or assert global semantic continuity.

---

## 3. Neighborhood Construction

A chart neighborhood is a bounded set of events selected relative to the anchor.

Neighborhood selection MAY combine:
- temporal proximity
- experiential adjacency
- prior traversal paths

Invariant C2 — Locality  
Neighborhoods MUST be small enough that local approximation remains valid.

Neighborhood boundaries MUST be adjustable but explicit.

---

## 4. Tangent Space and Basis Axes

Each chart defines a local tangent space via a finite set of interpretable basis axes.

Basis axes SHOULD correspond to experienced variation, such as:
- topic shift
- intent or agency phase
- artifact type (thought → draft → action)
- temporal progression
- interaction mode (exploration → decision → execution)

Invariant C3 — Interpretability  
Basis axes MUST be interpretable and describable to the user.

Basis axes MUST NOT be raw embedding dimensions or opaque latent vectors.

---

## 5. Differential Navigation

Charts support differential moves of the form:
step(axis_i, ±δ)

A differential move returns nearby events that vary incrementally along the selected axis.

Invariant C4 — Incrementality  
Differential navigation MUST surface small, local changes rather than semantic jumps or teleportation.

All differential moves MUST resolve to concrete substrate events or contiguous segments.

---

## 6. Chart Lifecycle

Charts are:
- constructed on demand
- invalidated when the active anchor changes
- discardable without loss of continuity

Charts MAY be cached transiently but MUST be recomputable from substrate events and runtime state.

Charts MUST NOT accumulate authority across sessions.

---

## 7. Relationship to Manifold

Charts constitute the local coordinate patches of the continuity manifold.

No single chart defines the manifold.

Charts MAY overlap in neighborhood membership but remain anchor-scoped.

Overlap enables navigation, not semantic identity.

---

## 8. Non-Goals

Charts do NOT:
- encode global semantics
- collapse ambiguity
- impose meaning
- replace user judgment
- define correctness or importance

They exist solely to make local semantic motion legible and navigable.

---

## Summary

Charts provide the local geometry of meaning around an anchor.

They enable exploration through small semantic differentials while preserving human grounding, rebuildability, and non-authority of derived semantics.
# Continuity Manifold — Language Infrastructure (LI)

## Purpose
This document specifies the continuity manifold as the runtime navigation structure derived from iam.db.

The continuity manifold enables traversal across experienced trajectories by stitching together local charts, without asserting global semantic authority or coherence.

---

## 1. Definition

A continuity manifold is a runtime structure formed by:
- a set of anchor-scoped charts, and
- explicit, user-observable transitions between charts.

Formal definition:
manifold := {
  charts: { chart_id → chart },
  transitions: { (chart_id_a, chart_id_b) → transition_rule }
}

The manifold is:
- derived
- rebuildable
- non-authoritative with respect to meaning

---

## 2. Authority Boundary

Invariant M1 — Projection Only  
The continuity manifold MUST be treated strictly as a projection derived from substrate events.

The manifold MUST NOT replace, reinterpret, summarize, or supersede iam.db.

---

## 3. Atlas Construction

Invariant M2 — Local Patches  
The manifold MUST be composed of local charts (patches).

No single chart defines the manifold.
Global semantic space MUST NOT be assumed.

Charts MAY overlap in neighborhood membership.

---

## 4. Overlap and Continuity

Charts overlap when their neighborhoods share one or more substrate events or contiguous segments.

Invariant M3 — Overlap Is Evidence, Not Meaning  
Overlap MAY be used to propose navigational adjacency (“nearby”, “related in experience”).

Overlap MUST NOT be interpreted as semantic identity, equivalence, or conceptual sameness.

---

## 5. Transitions Between Charts

Transitions occur when:
- the user explicitly changes anchors, or
- the runtime proposes a chart handoff due to locality limits being reached.

Invariant M4 — Explicit Handoff  
All chart transitions MUST be explicit and observable to the user.

The system MUST NOT silently move the user across charts or anchors.

---

## 6. Branching and Divergence

The manifold MUST support explicit representation of experienced branching, including:
- diverging trajectories
- decision points
- abandoned or paused paths

Invariant M5 — Branch Legibility  
Branch points MUST correspond to concrete substrate events or short contiguous segments where trajectories diverge.

The system MUST NOT infer a single “correct” path or collapse divergence into coherence.

---

## 7. Traversal Operations

Permitted traversal operations include:
- reanchor(event_id) — explicit change of anchor
- step(axis_i, ±δ) — differential navigation within a chart
- trace(path_id | time_window) — follow an experienced trajectory
- jump(via_overlap) — explicit navigation via chart overlap

Invariant M6 — Event-Resolved Navigation  
All traversal operations MUST resolve to concrete substrate events or contiguous segments.

Traversal MUST remain grounded in experienced history.

---

## 8. Suggested Transitions and Candidate Anchors

The runtime MAY suggest:
- chart handoffs
- candidate anchors
- alternative traversal paths

Invariant M7 — Structural Justification Only  
Suggestions MUST be justified using structural signals only, including:
- overlap density
- revisit frequency
- divergence points
- temporal or experiential transitions

Suggestions MUST NOT be presented as semantic conclusions.

User confirmation is REQUIRED for:
- re-anchoring
- accepting chart transitions

---

## 9. Persistence Constraints

Invariant M8 — No Manifold Authority in Storage  
The continuity manifold MUST NOT be persisted as authoritative structure.

Transient caching is permitted, but the manifold MUST be fully recomputable from:
- iam.db
- runtime state permitted by LI/runtime/state.md

---

## 10. Non-Goals

This specification explicitly excludes:
- UI rendering or visualization requirements
- global semantic ontologies
- automated correctness judgments
- enterprise-wide coherence constraints

---

## Summary

The continuity manifold is an atlas of local charts connected by explicit, user-controlled transitions.

It exists to make experienced trajectories navigable while preserving:
- event grounding
- user control of anchors
- local semantic motion
- rebuildability
- non-authority of derived semantics
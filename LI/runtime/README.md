Rules in this directory MUST NOT:
- modify substrate history
- assert global semantics
- infer importance or correctness

---

## Files in This Directory

### `anchors.md`
Defines **where the user stands**.
- anchor semantics
- ephemeral vs declared anchors
- default anchor rule
- anchor suggestion constraints

Anchors provide grounding and local origin.

---

### `state.md`
Defines **what runtime state may persist**.
- last known anchor (“Last here”)
- declared anchors
- rebuild guarantees
- write-back constraints

State preserves continuity of attention, not meaning.

---

### `charts.md`
Defines **local semantic coordinate systems**.
- anchor-scoped charts
- neighborhoods
- tangent spaces
- differential navigation

Charts enable small, interpretable semantic motion.

---

### `manifold.md`
Defines **how charts stitch together**.
- atlas construction
- overlap and transitions
- branching and divergence
- traversal operations

The manifold enables navigation across experience without global coherence.

---

## Authority Invariant
No file in this directory is authoritative over meaning.

All runtime structures:
- must resolve to concrete events in `iam.db`
- must be discardable and recomputable
- must preserve explicit human control

---

## Design Principle
Meaning emerges through **anchored navigation of experienced trajectories**, not through automated semantic collapse.

The runtime layer exists to make that navigation possible.

---

## Non-Goals
This directory intentionally excludes:
- UI definitions
- visualization rules
- embedding strategies
- global semantic models
- enterprise coherence frameworks

Those belong to higher layers.

---

## Summary
The runtime continuity layer translates captured experience into a **navigable semantic manifold** while preserving:
- event grounding
- human agency
- local interpretation
- rebuildability
- non-authority of derived structures


## Runtime Behavior

Behavioral contracts governing attention capture, breadcrumb formation,
and SubDB append semantics are defined in:

- `behavior.md`

These contracts specify what MUST occur when language crosses an attention
boundary, independent of platform or implementation.
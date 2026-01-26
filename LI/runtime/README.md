# Runtime Continuity Layer

## Canonical Definition

The authoritative definition of IAM runtime behavior is specified in:

**`LI/runtime/core_loop.md`**

That document defines:
- the minimal continuity loop
- the role of continuons and SubDB
- the boundary between persistence and runtime
- the non-authority of derived semantics

All files in this directory MUST be consistent with the core loop.
No file in this directory may expand, reinterpret, or supersede it.

---

## Authority Boundary

Files in this directory MUST NOT:
- modify substrate history
- assert global semantics
- infer meaning, importance, or correctness
- persist derived structures as authoritative

All runtime structures are:
- derived
- discardable
- rebuildable from SubDB

---

## Files in This Directory

### `core_loop.md`
Defines the **canonical continuity loop**.
- compression of language-use into continuons
- SubDB sufficiency
- runtime anchoring and probing
- re-entry without reconstruction

This file is the compression spine of the runtime layer.

---

### `behavior.md`
Defines **when and how continuons are formed**.
- attention boundary events
- capture rules
- embedding as measurement
- SubDB append semantics

This file specifies the ingest contract at runtime.

---

### `anchors.md`
Defines **where the user stands**.
- anchor semantics
- implicit vs declared anchors
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
- must resolve to concrete continuons in SubDB
- must be discardable and recomputable
- must preserve explicit human control

---

## Design Principle

Meaning emerges through **anchored navigation of experienced trajectories**,
not through automated semantic collapse.

The runtime layer exists to make that navigation possible.

---

## Non-Goals

This directory intentionally excludes:
- UI definitions
- visualization rules
- embedding strategies
- model selection
- global semantic ontologies
- enterprise coherence frameworks

Those belong to higher layers.

---

## Summary

The runtime continuity layer translates captured experience into a
**navigable semantic manifold** while preserving:

- continuity of attention
- human agency
- local interpretation
- rebuildability
- non-authority of derived semantics

The canonical loop is defined in `core_loop.md`.
Everything here refines it.
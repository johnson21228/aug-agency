# Continuity Manifold — Design Constraints and Goals

## Purpose

This document defines the minimal structure, invariants, and non-goals of the
Continuity Manifold used by IAM.

The Continuity Manifold exists to support long-horizon human thinking by
preserving continuity of thought over time without introducing optimization,
automation, or agentic substitution.

---

## Core Ontology

The Continuity Manifold consists of:

1. A space S (semantic + auxiliary coordinates)
2. A set of paths γ(t) traced through S

A path represents a recorded trajectory of human thought through the space.
Paths are authoritative. All higher-order structures are derived.

---

## Primary Invariant (Path-First)

Continuity is persisted as trajectories, not as inferred dynamics.

• Paths are immutable once recorded
• No process may rewrite, correct, or optimize a path
• Any abstraction must be non-authoritative relative to the path

The system preserves what happened, not what should have happened.

---

## What the Manifold Provides

From paths alone, the manifold supports:

• Temporal continuity
• Return-with-difference
• Persistence of unresolved problems
• Salience via dwell and revisitation
• Reflection across time and context

The manifold does not answer questions.
It preserves the conditions under which good answers may form.

---

## Allowed Structures (Derivable Only)

The following are permitted because they do not override paths:

### Measurements of Paths
• arc length
• curvature
• dwell density
• revisitation count
• proximity to prior regions

### Relations Between Paths
• shape similarity
• shared neighborhoods
• divergence and convergence points

### Annotations
• human-authored notes
• markers of importance, error, or uncertainty
• explicit judgments (non-binding)

Annotations decorate paths; they do not bend them.

---

## Explicit Non-Goals

The Continuity Manifold must NOT:

• define goals
• assign rewards or scores
• generate next actions
• close open questions automatically
• substitute for human judgment
• optimize trajectories
• behave as an agent

Any component requiring these properties is out of scope by definition.

---

## Embeddings Policy

Embeddings (and other latent-space vectors) may be attached to continuity IDs as **numeric, versioned overlays**.

- Embeddings provide *coordinates*, not meaning.
- They do not define importance or value.
- They may not override continuity ordering, adjacency, or stitching.
- Continuity correctness must not depend on their presence.

### Authority and placement

- The authoritative definition of any embedding space is externalized as metadata (e.g., `space_id`, model/version, dimension, normalization).
- Multiple spaces may coexist simultaneously.
- Substrate implementations may replicate vectors for performance/portability, but only as overlays that remain attributable to `space_id` and build/version.

Continuity remains primary; embeddings are a chart, not the terrain.


## Human Authority

Judgment, intention, value, and closure remain human responsibilities.

The system’s role is to preserve history in a legible form that supports
reflection and decision over time.

---

## Design Test

Any proposed addition must satisfy:

1. Is it derivable from paths?
2. Does it preserve path authority?
3. Does it avoid optimization or prescription?
4. Does it increase legibility without imposing values?

If not, it must be rejected.

---

## Summary

The Continuity Manifold is intentionally minimal.

Its power comes not from intelligence or automation,
but from disciplined preservation of human continuity.

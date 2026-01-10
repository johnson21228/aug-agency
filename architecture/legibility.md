# Legibility Specification
## Continuity Maps and Re-Entry

This document defines legibility as an architectural requirement.
It is not a user interface description and does not prescribe visual design.
It specifies what must be exposed for continuity to be usable.

## Purpose

Legibility exists to make preserved continuity usable without reconstruction.

A system may preserve continuity correctly and still fail if a human cannot:
- locate themselves within an unfinished path,
- shift perspective without losing position,
- re-enter work as continuation rather than observation.

Legibility addresses this failure mode.

## Definitions

- **Continuity**
  Preservation of a single human’s personal language use as a path through time.

- **Path**
  A time-extended trajectory defined by attention, return, judgment, and constraint.

- **Personal Semantic Space**
  The semantic space shaped by a single human’s language use over time.

- **Shape**
  The global geometry that emerges when a path unfolds in semantic space.

- **Map**
  A representation that preserves and exposes enough structure of continuity
  to support re-entry, navigation, and perspective change without reconstruction.

## Core Requirements

### R1. Re-Entry Without Reconstruction

A legible system MUST allow a human to re-enter an unfinished path as continuation,
not as retrospective explanation.

Re-entry must restore:
- positional orientation,
- unresolved constraints,
- forward pressure.

Summaries, explanations, or coherence alone do not satisfy this requirement.

### R2. Perspective Mobility Without Rupture

A legible system MUST support multiple perspectives over the same continuity
without breaking identity or forcing reconstruction.

At minimum, the map MUST support:
- **Along-path perspective** (participant stance; continuation)
- **Local neighborhood perspective** (nearby branches, revisits, alternatives)
- **Global perspective** (folded structure; long-range relations)

Perspective change MUST be reversible.

### R3. Shape Preservation

The map MUST expose the global shape that emerges from continuity in semantic space.
This includes:
- non-local proximity,
- convergence and divergence,
- revisitation collapse across time.

Linear timelines alone are insufficient.

### R4. Substrate / Meaning Separation

The substrate MUST hold shape independently of interpretation.
Meaning MUST be supplied by the human through client-defined coordinates and metric.

Legibility MUST NOT require:
- fixed semantic dimensions,
- canonical distance functions,
- model-centric explanations.

### R5. Personal Scope

Legibility is scoped to a single human’s continuity.
Maps MUST NOT aggregate, average, or generalize across users.

Transferability is explicitly out of scope.

## Non-Goals

Legibility is NOT:
- explanation,
- summarization,
- reasoning transparency,
- model interpretability,
- dashboards or analytics.

Legibility does not exist to explain thought,
but to support being-in-time with ongoing work.

## Failure Modes (Explicit)

A system fails legibility if:
- returning users must restate problems,
- position must be inferred from artifacts,
- zooming out loses re-entry,
- global views erase local constraint,
- interpretation alters continuity.

These failures indicate reconstruction has replaced continuation.

## Evaluation Criteria

A system satisfies legibility if a returning human can:
- resume work without re-explaining it,
- step back to gain perspective without losing position,
- recognize global structure formed by their own history,
- continue forward without summarization.

## Relationship to Other Specifications

- This document depends on `architecture/continuity-manifold-model.md`
- This document constrains projections described in `architecture/node-projections.md`
- This document operationalizes premises stated in `writing/overview.md`

Legibility does not introduce new primitives.
It specifies how existing continuity must be made usable.

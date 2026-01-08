# Continuity Manifold Model

## Status
GOVERNING — code and architecture must conform.

## Core Statement

The continuity manifold is stored in SubDB.

Paths are traced in the coordinate space defined in ProvDB and
materialized in SubDB.

Semantic meaning interprets nodes, regions, and paths in this manifold,
but does not define the manifold itself.

---

## 1. ProvDB — Coordinate and Metric Definition

ProvDB defines the formal continuity system.

ProvDB is responsible for defining:

- stable node identity (`node_id`)
- coordinate schemas for continuity, including:
  - time / ordering
  - adjacency / topology
  - latent numeric dimensions
- metric definitions governing geometry, including:
  - distance
  - curvature
  - differential operators
- node construction policies (e.g. PRP)
- references back to capture (`iam.db`)

ProvDB does NOT store a manifold and does NOT execute geometry.

ProvDB answers:

> “What coordinate space exists, and how is geometry defined within it?”

---

## 2. SubDB — Materialized Continuity Manifold

SubDB stores the continuity manifold.

SubDB materializes nodes into the coordinate space defined by ProvDB
by storing numeric coordinate values for each `node_id`.

SubDB is responsible for:

- storing numeric coordinate values
- materializing adjacency and neighborhoods
- storing the continuity manifold
- executing path traversal
- executing differential geometry using ProvDB-defined metrics

A path is a curve or ordered sequence through SubDB in node coordinate space.

SubDB answers:

> “Where are nodes located in continuity space, and how do paths behave?”

---

## 3. Semantic DB — Interpretation Layer

The Semantic DB interprets the continuity manifold.

It assigns meaning to:

- nodes
- regions
- paths

Semantic interpretation:

- is layered on top of SubDB structure
- may evolve independently
- must not redefine coordinates, metrics, or paths

Semantic DB answers:

> “What does this node, region, or path mean?”

---

## 4. Mapping Contract

The mapping between layers is explicit and identity-based.

The manifold exists only in SubDB.

---

## 5. IAM Orchestration

IAM, via CAP:

- queries SubDB for paths and regions
- consults ProvDB for coordinate and metric definitions
- optionally consults Semantic DB for interpretation
- composes results ephemerally

This separation is architecture law.

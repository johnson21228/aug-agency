# Continuity Ingestion Pipeline

This document describes how inputs enter the continuity architecture.

The Continuity Ingestion Pipeline is the workflow by which explicit human-generated language inputs (LUIs) and other events are transformed into a continuity-preserving structure suitable for longitudinal re-entry.

This pipeline forms continuity.  
It does not interpret meaning.

---

## Input Sources

Inputs may originate from:
- human language acts (LUIs)
- tools
- agents
- sensors
- systems

All inputs are treated as explicit events, not semantic content.

---

## Ingestion Principles

The pipeline operates under the following constraints:

- no semantic interpretation at ingress
- no goal inference
- no optimization
- no summarization

Ingress converts inputs into non-semantic traces that preserve ordering and identity without extracting meaning.

---

## First Output: LUI Capture Layer (Source-of-Record)

The first invariant output of ingestion is the **LUI Capture Layer**: a persistent, addressable record of explicit events suitable for longitudinal reference.

This layer is the source-of-record over which CAP forms regions, return points, adjacency, and stitching.

See: `architecture/lui-capture-layer.md`.

---

## Pipeline Stages

1. **Capture** — explicit event recorded
2. **Time-indexing** — temporal ordering preserved
3. **Structural anchoring** — trace placed within continuity
4. **Optional interface exposure** — via IAM or other interfaces

Meaning is not processed at any stage.  
Meaning re-emerges only through human re-entry.

---

## Architectural Boundary

Ingestion is a one-way boundary:

- semantics do not pass downward
- continuity does not infer upward

This boundary is enforced structurally, not by policy.

---

## Relationship to IAM

The Continuity Ingestion Pipeline is not IAM.

- IAM is the conversational interface and thinking support tool.
- The ingestion pipeline operates beneath IAM to provide structural assurance for trust.

IAM relies on continuity formed by this pipeline, but does not expose or foreground it as a user-facing feature.

---

## Optional Overlays

Chunking, summaries, and semantic assistance may be computed as overlays, but they are not required for continuity correctness and must remain separable from the LUI Capture Layer.

---

## Atlas Stitching (Internal Name)

Internally, this process may be referred to as **Atlas Stitching**, reflecting the assembly of local continuity charts into a coherent atlas without collapsing meaning.

This name is conceptual and does not imply semantic interpretation.

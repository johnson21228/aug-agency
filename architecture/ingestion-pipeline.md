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

These records populate the **Continuity Atlas**, which stores continuity structures such as ordering, regions, return points, adjacency, and stitching.

CAP (Continuity Access Protocol) defines the interface and protocol by which these Atlas structures are accessed and navigated.

See: `architecture/lui-capture-layer.md`.

---

## Pipeline Stages

1. **Capture** — explicit event recorded
2. **Time-indexing** — temporal ordering preserved
3. **Structural anchoring** — trace placed into the Atlas
4. **Optional interface exposure** — via IAM using CAP

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

IAM relies on continuity preserved in the Atlas and accessed via CAP, but does not expose the substrate or protocol as user-facing features.

---

## Optional Overlays

Chunking, summaries, and semantic assistance may be computed as overlays, but they are not required for continuity correctness and must remain separable from the LUI Capture Layer and Atlas.

---

## Atlas Stitching (Internal Name)

Internally, this process may be referred to as **Atlas Stitching**, reflecting the assembly of local continuity records into a coherent Atlas without collapsing meaning.

This name is conceptual and does not imply semantic interpretation.

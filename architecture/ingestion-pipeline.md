# Continuity Ingestion Pipeline

This document describes how inputs enter the continuity architecture.

The Continuity Ingestion Pipeline is the workflow by which explicit language-use inputs (LUIs) and other events are transformed into a continuity-preserving structure suitable for longitudinal re-entry.

This pipeline forms continuity. It does not interpret meaning.

## Input Sources

Inputs may originate from:
- human language acts (LUIs)
- tools
- agents
- sensors
- systems
- reflective artifacts produced during IAM use (“gold”)

All inputs are treated as explicit events, not semantic content.

## Ingestion Principles

- no semantic interpretation at ingress
- no goal inference
- no optimization
- no summarization

Ingress converts inputs into non-semantic traces that preserve ordering and identity without extracting meaning.

## Data Stores and Boundaries

Ingestion is realized as a three-store architecture with strict ownership boundaries:

1) Capture Store (`iam.db`) — Source-of-Record  
- Append-only capture of raw LUIs/events (plus provenance pointers).  
- Adapter-shaped (today: ChatGPT exports; later: other adapters).  
- Authoritative for what was captured.

2) Provenance Store Family (`provdb/*`) — ID ↔ Language + Semantic Coordinates  
- Contracts captured inputs into a uniform event record keyed by stable numeric IDs.  
- Owns the mapping: ID → source language (or span) + provenance.  
- May store numeric semantic coordinates as versioned overlays keyed by `(space_id, id)`.

3) Substrate Store Family (`subdb/*`) — Continuity Geometry + Atlas Structures  
- Semantic-free continuity substrate: ordering coordinates, adjacency, regions, return points, stitching edges.  
- May replicate numeric semantic coordinates only as versioned overlays.  
- Substrate correctness must not depend on semantic overlays.

Join key: composition happens by stable event IDs. Derived node projections
(PRPs, chunkings, sessions) may also be used as build-scoped node IDs when
explicitly named and versioned as layers. These projections must remain
rebuildable, non-authoritative, and lossless via membership back to event IDs.

## Append-Only and Concurrency Contract

- Append-only facts: capture and provenance mappings are never rewritten or deleted.
- Idempotent builders: each stage can be re-run without changing existing results.
- Derived materialization must be versioned/append-only or explicitly rebuildable and non-authoritative.

## Pipeline Stages

1. Capture — adapters write append-only events into `iam.db`.  
2. Normalize + stable event ID assignment — `iam.db` is contracted into `provdb/core`.  
3. Optional overlays — semantic coordinates may be computed as versioned overlays in `provdb`.  
4. Structural anchoring — continuity geometry is written to `subdb`.  
5. IAM orchestration — ProvDB and SubDB are jointly consulted ephemerally for re-entry.

Meaning is not processed at any stage. Meaning re-emerges only through human re-entry.

## Parallel Node Layers (Pairings)

From the same `iam.db` capture and the same `provdb/core` event identities,
multiple node layers may be derived in parallel (e.g. PRP pairing, alternative
chunking). Each layer is policy-versioned and maps to semantic-free SubDB
geometry over layer-scoped `node_id`s.

## Reflexive Ingress

Artifacts generated during IAM use re-enter the pipeline as explicit capture events through the same capture interface as external inputs. They are treated strictly as data and must never rewrite prior capture.


## Sequencing policy

Adapters do not impose or require human sequencing.

Capture records:
- `observed_ts` when available (source-provided)
- `capture_id` as append-only insertion order

Builders derive deterministic stream order from capture:
- `observed_ts NULLS LAST, observed_ts ASC, capture_id ASC`

No semantic sequencing is performed at capture.

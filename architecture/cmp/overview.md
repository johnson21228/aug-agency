# Continuity Materialization Pipeline (CMP)
## Overview and Authority

This document defines the Continuity Materialization Pipeline (CMP) as an architectural commitment.

CMP specifies:
- stage boundaries,
- authoritative vs derived stores,
- contracts for data evolution,
- runtime modes (scripts, app, optional server).

CMP does not prescribe implementation language or platform.

---

## Core Premise

Continuity is preserved as a single human’s personal language use over time.
CMP materializes derived forms that support re-entry and legibility without requiring semantic interpretation for correctness.

---

## Stage Model

CMP is defined as a sequence of materialization stages.

### Stage 0 — Capture (Authoritative)
Input: LUI packets (append-only personal language-use events)
Output: `iam.db` (capture store)

Properties:
- append-only
- stable event identity
- idempotent ingestion
- no semantic interpretation required for correctness

### Stage 1 — Derived Structural Views (Rebuildable)
Input: `iam.db`
Output: derived views (e.g., turn index, packet exports)

Properties:
- rebuildable
- non-authoritative
- may be regenerated at any time without changing `iam.db`

### Stage 2 — Provenance Materialization (Rebuildable)
Input: `iam.db`
Output: provDB (provenance and coordinate definitions)

Properties:
- stable identifiers
- provenance, text rehydration, definitions
- coordinate/metric definitions may exist, but do not define correctness of capture

### Stage 3 — Substrate Geometry Materialization (Rebuildable)
Input: provDB
Output: subDB (semantic-free continuity geometry)

Properties:
- ordering, adjacency, stitching
- geometry is held independently of interpretation
- semantic joins are not required for correctness

---

## Store Authority

- `iam.db` is authoritative for capture (Stage 0).
- provDB and subDB are derived and rebuildable.
- derived stores may be deleted and regenerated without loss of capture authority.

---

## Runtime Modes

CMP may be implemented in multiple runtimes:

### A) Desktop Scripts (Reference Implementation)
Python scripts may implement CMP stages for development, testing, and fixture generation.

### B) IAMApp (Production Implementation)
IAMApp may implement CMP stages locally (on-device) within the Apple privacy boundary.

### C) Optional Server Accelerator (Non-Authoritative)
A server may materialize derived stores asynchronously as an accelerator.
A server must not be required for correctness.
A server must not become authoritative for the user’s library.

---

## Required Contracts

CMP depends on these contracts:

- `contracts/lui_packet.md` — canonical LUI packet schema and ingestion rules
- `contracts/materialization_queue.md` — idempotent, cursor-based stage execution rules

Other contracts may be added (provDB, subDB) once schemas stabilize.

---

## Non-Goals

CMP is not:
- a semantic interpretation system,
- a summarization pipeline,
- a model-centric explainability system.

CMP is a structural pipeline that preserves continuity and materializes derived forms that can be re-entered.

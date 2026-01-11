# CMP Contract (IAMApp)
## Continuity Materialization Pipeline — App Integration

This document defines IAMApp’s obligations to implement the Continuity Materialization Pipeline (CMP) locally.

It is a local integration contract that references authoritative architecture contracts:

- `architecture/cmp/overview.md`
- `architecture/cmp/contracts/lui_packet.md`
- `architecture/cmp/contracts/materialization_queue.md`
- `architecture/cmp/contracts/provdb_contract.md`
- `architecture/cmp/contracts/subdb_contract.md`

If this document conflicts with the architecture contracts, this document is wrong.

---

## Purpose

IAMApp must:
- capture personal LUIs into an authoritative local substrate (`iam.db`),
- materialize derived stores (provDB, subDB) according to CMP contracts,
- expose continuity through a conversational surface and a continuity map,
- preserve re-entry without reconstruction.

CMP is a structural pipeline.
No semantic interpretation is required for correctness.

---

## Authority and Store Roles

### Authoritative
- `iam.db` (capture store)
  - append-only LUI events
  - stable event identity
  - idempotent ingestion

### Derived (Rebuildable)
- provDB (provenance materialization)
- subDB (continuity geometry materialization)
- any semantic overlays or coordinate assignments

Derived stores may be deleted and regenerated without loss of capture authority.

---

## CMP Stages (IAMApp)

### Stage 0 — Capture
Input: LUI packets (per `lui_packet.md`)  
Output: `iam.db`

Obligations:
- append-only ingestion
- stable identity
- offline correctness
- no semantic requirements

### Stage 1 — Derived Views (Optional but Recommended)
Input: `iam.db`  
Output: derived views (e.g., turn index, export packets)

Obligations:
- rebuildable views only
- must not mutate `iam.db`
- must not be required for correctness of capture or re-entry

### Stage 2 — prov Materialization
Input: `iam.db`  
Output: provDB (per `ProvDBContract.md` + architecture provDB contract)

Obligations:
- deterministic identity mapping
- verbatim text rehydration
- provenance preservation
- semantic overlays are optional and non-authoritative

### Stage 3 — sub Materialization
Input: provDB  
Output: subDB (per `SubDBContract.md` + architecture subDB contract)

Obligations:
- semantic-free correctness
- deterministic geometry
- addressable paths (streams, nodes, edges)

---

## Scheduling and Background Processing

IAMApp may materialize stages:
- immediately (foreground),
- lazily (on demand),
- asynchronously (background).

The app must maintain correctness even if:
- background processing is delayed,
- derived stores are missing,
- external inference is disabled.

Derived stages are best-effort and rebuildable.

---

## Optional External Inference (Non-Authoritative)

IAMApp may issue one-shot external inference requests when:
- the user enables it,
- credentials are configured.

External inference:
- must not be required for correctness,
- may only enrich derived views (prov overlays, labels, optional coordinates),
- must never overwrite capture content.

---

## Photos Pattern Alignment

IAMApp behaves like Photos:
- the on-device library is authoritative by default,
- sharing/export is explicit and user-initiated,
- export produces copies,
- sync is optional and does not define correctness.

CMP must function correctly offline for capture and re-entry.

---

## Compliance Requirements

IAMApp is CMP-compliant if:
- Stage 0 capture is correct and append-only,
- Stages 2–3 can be regenerated deterministically from upstream stores,
- re-entry is possible without summaries or external inference,
- perspective changes do not break the ability to return to a position.

---

## Implementation Notes (Non-Normative)

- Swift modules should correspond to CMP stages.
- Each module should be governed by a spec under `Language/Specs/`.
- Xcode is used for editing/debugging; language is authoritative.

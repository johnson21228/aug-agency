# IAM — Intelligent Augmented Memory

IAM is a system for preserving **cognitive continuity over time**.

It is not a note-taking system, a retrieval engine, or an agent framework.
It is an infrastructure for capturing language-use events and deriving
time-extended continuity structures without collapsing them into snapshots,
graphs, or reconstructed coherence.

This repository defines IAM as a **Language-Infrastructure (LI)** project.
Its primary obligation is internal consistency, invariants, and auditability.

---

## What This Repository Is

This Language Infrastructure **cannot be compiled away**.  
It exists precisely because **humans reason in time**.

For that reason, the repository intentionally includes **human-facing,
interpretive artifacts** alongside **machine-facing contracts and invariants**.
Both are required to preserve continuity, judgment, and auditability across
time. Any system that attempts to reduce this infrastructure to executable
code alone will necessarily lose essential structure.

This repository is:

- An **authoritative specification** of IAM’s invariants and architecture
- A **language-level infrastructure** that constrains tools, prompts, and code
- A **solid-state representation** of the project that must stand on its own

The repo is designed so that a technically sophisticated reader can:

- Understand the system without prior conversations
- Audit its claims against its architecture
- Extend it without violating core invariants

---

## What This Repository Is Not

This repository is **not**:

- A marketing site
- A product pitch
- A model-centric AI system
- A dashboard or visualization framework
- A claim that judgment can be automated or reconstructed

Any artifact that implies these properties is incorrect.

---

## Core Commitments

IAM is built on the following commitments:

- Cognition unfolds as a **time-extended trajectory**, not as points or states
- Judgment is **formed through continuity**, not computed from snapshots
- Capture is authoritative; derived artifacts are **non-authoritative**
- Semantic meaning is optional and must never be correctness-critical
- Continuity must remain valid even if all semantics are removed

These commitments are enforced through explicit invariants and contracts.

---

## Authority Structure (Critical)

If documents conflict, authority resolves **in this order**:

1. `architecture/continuity-operating-contract.md`
2. `architecture/invariants.md`
3. `core-ontology/glossary.md`
4. `core-ontology/continuity.md`
5. Specific contracts (ProvDB, SubDB, CAP)
6. Architecture overviews and essays
7. Tools, scripts, prompts

Anything lower must conform to anything higher.

---

## Authoritative Documents

The following files are **normative**:

- `architecture/continuity-operating-contract.md`  
  Defines what continuity means operationally and what must never be violated.

- `architecture/invariants.md`  
  Enumerates non-negotiable system invariants.

- `core-ontology/glossary.md`  
  Canonical definitions of core terms (LUI, continuity, substrate, etc.).

- `core-ontology/continuity.md`  
  Formal description of continuity as a time-extended structure.

---

## Architectural Structure

### Capture Layer

- **LUIs (Language Use Instances)** are captured events.
- Capture is append-only and authoritative.
- Events may arrive in any order.
- Corrections appear as new events, not edits.

Relevant files:
- `architecture/cmp/lui_packet.md`
- `architecture/Migrations.md`
- `Migrations/0001_capture_contract.sql`

---

### Derived Layers

Derived layers are rebuildable and non-authoritative.

- **ProvDB**  
  Provenance-rich, may include semantics.

- **SubDB**  
  Numeric / structural continuity substrate.
  Must be semantic-free for correctness.

Relevant contracts:
- `architecture/cmp/contracts/provdb_contract.md`
- `architecture/cmp/contracts/subdb_contract.md`

---

### Continuity Access

- **CAP (Continuity Access Protocol)** provides read access.
- CAP must remain correct without semantic overlays.
- Semantic views are optional and non-authoritative.

Relevant files:
- `architecture/continuity-operating-contract.md`
- `architecture/invariants.md`

---

## Semantics and Meaning

- Embeddings, summaries, classifications, and models are **overlays**
- Overlays may be replaced, removed, or regenerated
- Continuity correctness must not depend on any semantic overlay

If removing all semantics breaks continuity, the system is incorrect.

---

## Canonical Packing and Audits

To avoid oral tradition, IAM defines canonical packed representations.

Authoritative definition:
- `architecture/pack-canonical-artifacts.md`

Current state:
- `Tools/pack_md_repo.py` produces a deterministic ZIP of curated artifacts
- This ZIP is the current canonical audit input

Boot prompts and audits **must specify** which canonical pack they expect.

---

## Essays and Conceptual Texts

Essays in this repo:

- Support architectural claims
- Clarify judgment, continuity, and agency
- Do not define invariants or authority

Essays must never contradict:
- `architecture/continuity-operating-contract.md`
- `architecture/invariants.md`

---

## Tools and Scripts

Tools exist to:
- Capture data
- Pack repo state
- Build derived artifacts
- Generate site outputs

Tools must conform to architecture and invariants.
Tools do not define meaning or authority.

Relevant tools:
- `Tools/pack_md_repo.py`
- `Tools/pack_writings.py`
- `Tools/update_writing_index.py`
- `Tools/build_site.py`

---

## How to Read This Repo (Suggested Order)

1. `architecture/continuity-operating-contract.md`
2. `architecture/invariants.md`
3. `core-ontology/glossary.md`
4. `core-ontology/continuity.md`
5. `architecture/CONTINUITY_MANIFOLD.md`
6. `architecture/continuity-manifold-model.md`
7. CMP contracts (ProvDB, SubDB)
8. Essays and comparison documents

---

## Non-Goals (Explicit)

IAM does not attempt to:

- Automate judgment
- Replace human agency
- Reconstruct cognition from outputs
- Optimize for model interpretability
- Provide dashboards as truth instruments

Any such claims are out of scope.

---

## Solid-State Requirement

This repository must remain:

- Internally consistent
- Auditable without conversation
- Free of hidden assumptions
- Governed by explicit invariants

If understanding the system requires asking the author,
the repository is incomplete.

---

## License / Status

This repository is an active architectural and conceptual system.
Refer to licensing files for usage constraints.


### Executable Conformance Artifacts

In addition to tools and scripts, the repository may include **executable
conformance implementations** that exist solely to *implement* and *test*
Language Infrastructure (LI) boundaries.

These artifacts are **not authoritative**. They are disposable and replaceable.

They appear under two root directories:

- `services/`  
  Long-running processes that conform to LI contracts  
  (e.g. ingestion boundaries, durable spoolers, protocol adapters).

- `sources/`  
  Executable adapters that emit Language Use Instances (LUIs) from
  external artifacts or protocols  
  (e.g. export importers, protocol listeners).

All such artifacts must conform to:
- LI contracts
- LI invariants
- canonical schemas

If an executable conflicts with Language Infrastructure, the executable
is wrong — never the LI.

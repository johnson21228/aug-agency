# Repository Authority Map

This document defines **authority boundaries** within the repository.
No file or layer may contradict a layer above it.

## Authority ordering (highest → lowest)

1. **Writings (`writing/`)**
2. **Architecture (`architecture/`, `core-ontology/`)**
3. **Patent materials (`patent/`)**
4. **Embodiments (`embodiments/`)**
5. **Code (`code/`)**
6. **Data and artifacts (`data/`, local only)**

## Layer definitions

### 1. Writings (authoritative, upstream)
The writings articulate the core problem, stakes, and normative claims of the project.
They define what the system is *for* and what outcomes matter.

All downstream layers must remain consistent with the claims made in the writings.

### 2. Architecture and ontology (technical truth layer)
Architecture translates the writings into system invariants, levels, and protocols.
The core ontology defines primitives and constraints used throughout the system.

Architecture may operationalize the writings, but may not weaken or reinterpret them.

### 3. Patent materials (legal crystallization)
Patent drafts express the same ideas in legal form.
They must be traceable to both the writings and the architecture.

### 4. Embodiments (reduction to practice)
Embodiments demonstrate how the architecture can be realized.
They are illustrative, not exhaustive, and are not authoritative.

### 5. Code (non-authoritative)
Code exists only as a proof of feasibility or exploration.
It may be incomplete, experimental, or intentionally constrained.

If code contradicts architecture or writings, the code is wrong.

### 6. Data and artifacts
Data is local, sensitive, and never authoritative.
No committed data should be treated as normative or stable.

## Non-contradiction rule

Any contradiction must be resolved **upward**.
Lower layers must adapt to higher layers, never the reverse.

# Architecture Overview

This directory describes the architectural structure of the augmented-agency system.

The architecture is organized around a **continuity-first stack** that separates:
- non-semantic structural substrates
- semantic and reasoning layers
- agent and interface layers
- governance and autonomy constraints

The system is intentionally layered to ensure that:
- continuity precedes semantics
- agency precedes execution
- privacy is structural, not policy-based

Continuity is realized in a persisted non-semantic substrate (the **Continuity Atlas**) and accessed through a defined interface and protocol (**CAP — Continuity Access Protocol**).

The architecture supports multiple interfaces and applications, including IAM, without embedding application logic into the substrate.

## Design Principles

- Continuity before intelligence
- Explicit input over inferred state
- Re-entry over retrieval
- Human agency over agent optimization
- Layer separation over monolithic models

## Structure

- `levels/` — vertical architecture from numeric continuity to human autonomy
- `comparison/` — contrasts with alternative AI architectures
- `ingestion-pipeline.md` — how inputs enter the system
- `lui-capture-layer.md` — source-of-record for explicit language inputs

This architecture is designed to evolve without collapsing layers.

# Ingestion Pipeline

This document describes how inputs enter the continuity architecture.

## Input Sources

Inputs may originate from:
- human language acts (LUI)
- tools
- agents
- sensors
- systems

All inputs are treated as **explicit events**.

## Ingestion Principles

- No semantic interpretation at ingress
- No goal inference
- No optimization
- No summarization

Ingress converts inputs into **non-semantic traces**.

## Pipeline Stages

1. Capture — explicit event recorded
2. Time-indexing — ordering preserved
3. Structural anchoring — trace placed within continuity
4. Optional interface exposure — via IAM or other interfaces

Meaning is not processed.
Meaning re-emerges through re-entry.

## Architectural Boundary

Ingress is a one-way boundary:
- semantics do not pass downward
- continuity does not infer upward

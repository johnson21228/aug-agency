# Architecture Overview

The IAM architecture exists to operationalize the claims made in the writings.
It is not an independent source of truth.

This architecture translates normative goals—preserving human reasoning continuity,
judgment, and agency over time—into concrete system invariants and layers.

## Architectural stance

The system is designed around continuity, not optimization.

- Continuity is treated as a first-class invariant.
- Human judgment is preserved by maintaining temporal coherence of meaning.
- The system resists flattening human thought into static embeddings or summaries.

## Relationship to writings

All architectural decisions are downstream of the writings found in `writing/`.

The writings define:
- What problems matter
- What tradeoffs are acceptable
- What outcomes are explicitly rejected

The architecture answers only:
- How those claims can be made operational
- What invariants must hold for the system to remain aligned

## Layered structure

The architecture is organized into levels, beginning with a numeric continuity substrate
and extending through ingestion, temporal binding, and higher-order reasoning support.

Each level:
- Introduces constraints, not features
- Preserves append-only semantics
- Avoids rewriting or collapsing prior human expression

## Non-goals

This architecture is not intended to:
- Maximize predictive accuracy
- Replace human judgment
- Serve as a general-purpose agent framework

Any embodiment or code suggesting otherwise is misaligned.

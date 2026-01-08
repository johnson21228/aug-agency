# Architecture Overview

## What kind of system is this

This document establishes the identity of the system before any implementation details appear.

IAM is presented not as a tool for producing answers, nor as an agent that acts autonomously, but as a system designed to preserve and extend **human continuity of thought over time**. Its core claim is that human judgment, reflection, and meaning do not arise from isolated inference, but from sustained engagement with one’s own prior reasoning.

IAM is explicitly reflexive: outputs created through use of the system—annotations, links, decisions, moments of recognition—are allowed to re-enter the system as inputs. This reflexivity is structural rather than behavioral. Artifacts re-enter the system as captured history, not as changes to how the system operates.

This repository preserves continuity as lived structure—being-in-time—in the sense that language use remains situated in temporal sequence and re-entry remains possible without reconstructing meaning from scratch.

The IAM architecture exists to operationalize the claims made in the writings. It is not an independent source of truth. The architecture translates normative goals—preserving human reasoning continuity, judgment, and agency over time—into concrete system invariants and layers.

## Architectural stance

IAM is oriented toward **continuity rather than optimization**, and therefore resists reducing lived thought to static embeddings or fixed representations.

- Continuity is treated as a first-class invariant.
- Human judgment is preserved by maintaining temporal coherence of meaning.

Optimization, compression, and summarization may appear in derived layers, but they are never allowed to define identity or truth.

## What IAM is not

IAM is not an agent, a retrieval system, or a memory plugin layered onto a language model. It does not act autonomously or pursue outcomes on behalf of the user. Unlike retrieval-based systems, IAM does not treat memory as a corpus to be flattened into embeddings for answer production, nor does it treat retrieval as a substitute for continuity. Unlike note-taking or archival tools, IAM does not externalize thought as static artifacts detached from temporal context.

IAM preserves continuity by capturing language use and reflective acts as they occur, allowing meaning to re-emerge through re-entry rather than being inferred, summarized, or optimized in advance.

## Reflexive system with invariant structure

IAM permits artifacts produced through human interaction within the system—annotations, return points, links, decisions (“gold”)—to re-enter the system as first-class inputs.

These artifacts are captured append-only as data and incorporated into the system’s history. The governing structure remains invariant; growth occurs exclusively through accumulated capture and rebuildable derived views.

All derived structures may be rebuilt or replaced without invalidating captured history.

## Layered structure

The architecture is organized into layers, beginning with a numeric continuity substrate and extending through ingestion, temporal binding, and higher-order reasoning support.

Each layer:
- Introduces constraints, not features
- Preserves append-only semantics
- Avoids rewriting, collapsing, or flattening prior human expression

Later layers may add structure or utility, but never authority over earlier ones.

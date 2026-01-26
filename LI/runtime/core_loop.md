# Core Loop — Continuity Compression and Re-Entry

## Purpose

This document defines the **minimal, canonical loop** of IAM.

All runtime behavior, storage, UX affordances, and future application
implementations MUST be reducible to this loop without loss of function.

This file is the **compression spine** of the system.

---

## The Core Loop

IAM consists of a single repeating loop:

1. A **language-use input (LUI)** crosses an attention boundary
2. The LUI is **measured** via an embedding instrument
3. A **continuon** is formed
4. The continuon is **appended** to SubDB
5. Runtime establishes or updates a **current anchor**
6. Runtime **probes** the language field near the anchor
7. The user **grazes** generated continuations
8. A new LUI is produced, returning to (1)

This loop is continuous, append-only, and human-driven.

---

## Continuons

A **continuon** is the minimal persisted artifact of experience.

Each continuon consists of:
- a monotonically increasing sequence identifier
- a timestamp
- a numeric coordinate (embedding vector)
- optional light provenance metadata

Continuons are:
- measurements, not interpretations
- immutable once written
- sufficient for re-entry

Continuons MUST NOT:
- store meaning
- assert truth
- preserve original text
- enable reconstruction of prior language

---

## SubDB

SubDB is the only authoritative persistent store required by IAM.

SubDB is:
- append-only
- time-ordered
- private to the user
- rebuildable only by replay of continuons

No other durable semantic store is required.

---

## Runtime Role

Runtime exists solely to make continuons **usable**.

Runtime responsibilities include:
- establishing a current anchor
- maintaining minimal runtime state
- probing nearby regions of the language field
- presenting navigable options to the user

Runtime MUST NOT:
- modify SubDB history
- infer meaning
- collapse semantics
- assert correctness

All runtime structures are derived and discardable.

---

## Anchoring and Re-Entry

An **anchor** represents “where the user currently stands” in the continuity
of their experience.

Anchors may be:
- implicit (e.g., last continuon or centroid of recent continuons)
- explicit (user-declared)

Revisiting is achieved by:
- re-anchoring
- probing adjacent continuations
- recognizing resonance in generated language

Meaning is not retrieved.
Meaning is **re-encountered**.

---

## Probing and Grazing

Probing is the act of generating language from a numeric neighborhood
around an anchor.

Grazing is the human act of reading, selecting, rejecting, or extending
those generated continuations.

Recognition is performed by the human, not the system.

---

## Authority Invariants

- SubDB is authoritative over history
- Runtime is non-authoritative
- Generated language is suggestive only
- Meaning remains human

No component of IAM may supersede lived experience.

---

## Non-Goals

IAM explicitly does not attempt to:
- preserve truth
- reconstruct prior language
- guarantee semantic equivalence across models
- enforce global coherence
- externalize meaning

---

## Summary

IAM compresses experience into continuons and enables re-entry through
anchored probing.

The system preserves:
- continuity of attention
- navigability of thought
- privacy of experience
- human authority over meaning

Everything else is implementation detail.
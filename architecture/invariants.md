# Architecture Invariants

This document enumerates the non-negotiable invariants of the IAM architecture.
These invariants define what must remain true across all implementations, migrations,
optimizations, and future evolutions of the system.

They exist to ensure continuity of thought, durability of human judgment,
and long-horizon rebuildability in the presence of changing models, tools, and techniques.

---

## 1. Preserve Originals

All captured language-use events (LUIs) are preserved append-only.

Once recorded in the Capture Store (`iam.db`), no event may be deleted, rewritten,
or semantically reinterpreted in place. Corrections, annotations, or reinterpretations
must be captured as new events.

Originals are the sole irreducible ground truth of the system.

---

## 2. Reflexive Capture (Artifacts Become Inputs)

Artifacts produced during IAM use—annotations, return points, links, decisions,
and other reflective acts (“gold”)—are treated as first-class inputs.

These artifacts are captured append-only as data, using the same capture interface
as external inputs. They must never modify prior capture, overwrite history,
or alter operational rules.

IAM is reflexive but not self-modifying.

---

## 3. Stable Identity Is Derived Solely from Capture

Durable identity is assigned only at the event level and is derived solely
from capture provenance.

No identifier whose stability depends on semantic interpretation,
model behavior, embeddings, or segmentation may be treated as durable.

Continuon identifiers, chunk identifiers, and run-local indices are projections,
not identities.

Event identity is the only durable identity. However, the system may build
policy-versioned, rebuildable *node projections* (e.g. PRPs, chunkings) as
non-authoritative layers over events.

Such projections must:
- be explicitly named/versioned (layer_key)
- be lossless via ordered membership pointers to event identities
- never be used as durable referents for annotations or long-horizon identity

---

## 4. No Durable Feature May Depend on Ephemeral IDs

No durable reference, annotation, or structural feature may depend on
build-scoped or run-scoped identifiers.

All durable references must anchor to capture-stable addresses
(e.g., event identity and optional spans within captured language).

This ensures that all derived structures may be deleted and rebuilt safely.

---

## 5. Meaning and Continuity Are Deliberately Separated

Semantic interpretation and continuity structure are intentionally decoupled.

- Meaning may evolve.
- Embeddings may be replaced.
- Segmentation may change.
- Models may be upgraded or removed.

Continuity survives because it is grounded in capture, not semantics.

---

## 6. Derived Structures Are Non-Authoritative

All structures beyond the Capture Store—including provenance projections,
semantic overlays, substrates, slices, and indices—are derived and non-authoritative.

They exist to support navigation, retrieval, and re-entry, but they do not
define truth or identity.

Any derived structure may be discarded and rebuilt from capture at any time.

---

## 7. Correctness Must Not Depend on Semantics

System correctness—ordering, navigability, re-entry, and referential integrity—
must not depend on embeddings, clustering, topic models, or other semantic techniques.

Semantic overlays may enhance utility, but their absence must not break the system.

---

## 8. Rebuildability Is a First-Class Guarantee

It must always be possible to:

- delete all derived databases,
- change segmentation or models,
- upgrade software or schemas,

and fully reconstruct all non-authoritative structures from the Capture Store.

Rebuildability is not an operational convenience; it is a core architectural guarantee.

---

## 9. Human Judgment Is the Source of Curvature

IAM does not learn, optimize, or adapt its governing logic autonomously.

Continuity gains meaning through human judgment expressed over time,
captured as language-use events.

The system preserves and re-presents judgment; it does not replace it.

---

## Status

These invariants constrain all future work.
Any proposed change that violates an invariant must be rejected or redesigned.

They are enforced not by convention, but by architecture.

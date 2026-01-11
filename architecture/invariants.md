# IAM Invariants

This document enumerates invariants that are **non-negotiable** for IAM.
These invariants are **authoritative**.

If any other document, tool, prompt, or code conflicts with these invariants:
- These invariants win.
- The conflicting artifact must be changed or removed.

Related authoritative documents:
- `architecture/continuity-operating-contract.md` (COC)
- `core-ontology/glossary.md`
- `core-ontology/continuity.md`

---

## Invariant 1 — Capture Is Append-Only and Authoritative

1.1 The capture record is append-only.
- Events are never overwritten or deleted.
- Corrections appear as additional events, not edits.

1.2 Capture is the only authoritative history.
- Derived stores are never treated as authoritative.

---

## Invariant 2 — Derived Artifacts Are Rebuildable and Non-Authoritative

2.1 ProvDB and SubDB are derived from capture.
- They may be deleted and rebuilt from capture.

2.2 If derived artifacts are removed, the system must still be able to rebuild them.
- No correctness property may rely on persistence of derived artifacts.

---

## Invariant 3 — Durable Referents Are Event Identities

3.1 Durable referents must be event identities, not semantic labels.
- Stable IDs must exist for captured events.
- Derived IDs must trace back to capture.

3.2 Joins must rely on stable identifiers.
- No semantic similarity join may be required for correctness.

---

## Invariant 4 — Semantic Overlays Are Optional

4.1 Semantic overlays (embeddings, summaries, classifications) are overlays.
- They may be present, absent, or replaced.

4.2 If semantic overlays are removed:
- Continuity geometry must remain valid.
- SubDB correctness must remain valid.

---

## Invariant 5 — SubDB Correctness Is Semantic-Free

5.1 SubDB must not require semantics for correctness.
- No semantic joins, embeddings, or inference are required to satisfy SubDB guarantees.
- SubDB may store numeric/time/structural relations.

---

## Invariant 6 — CAP Correctness Must Not Depend on Semantic Joins

6.1 CAP must remain correct without semantic overlays.
- CAP may expose semantic views, but they are non-authoritative overlays.
- CAP must define behavior when overlays are missing.

---

## Invariant 7 — Arrival Order Is Not User-Enforced

7.1 Adaptors may receive LUIs in any order.
- Users are not required to sequence events manually.

7.2 Any ordering used downstream must be derived and labeled as derived.
- Observed timestamps must be preserved as observed.

---

## Canonical Definition Anchor Rule

To prevent semantic drift:

- Canonical definitions of core terms live in:
  - `core-ontology/glossary.md`
  - `core-ontology/continuity.md`

Other documents may:
- reference those definitions
- extend with examples

Other documents must not:
- redefine core terms in conflicting ways

---

## Canonical Pack Artifact Rule

To prevent “oral tradition” about what constitutes the repo’s packed representation:

- The repo must define and maintain a canonical “packed representation” document:
  - `architecture/pack-canonical-artifacts.md`

Audits and boot prompts must refer to that canonical definition.

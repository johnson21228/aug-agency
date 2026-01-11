# Continuity Operating Contract (COC)

This document defines the operating contract for IAM continuity.
It is **authoritative** and **normative**.

- If any other document conflicts with this one, this document wins.
- Code and tools must be consistent with this contract.
- This contract does not describe implementation choices; it describes required behavior.

---

## 0. Definitions (Minimal)

- **LUI**: Language Use Instance. An observed event of language use captured by an adaptor.
- **Capture store**: The append-only record of LUIs as observed.
- **ProvDB**: A derived, provenance-rich database built from capture (may contain semantics).
- **SubDB**: A derived continuity substrate built from capture (must be semantic-free for correctness).
- **CAP**: Continuity Access Protocol. A read interface over derived structures that must preserve invariants.

Canonical definitions are maintained in:
- `core-ontology/glossary.md`
- `core-ontology/continuity.md`

This contract uses terms as defined there.

---

## 1. Authority Boundary

### 1.1 Capture Authority
The capture store is the **only authoritative historical record**.

- Capture is append-only.
- Corrections are represented as additional events, not overwrites.
- Deleting or modifying capture invalidates continuity claims.

### 1.2 Derived Non-Authority
All derived artifacts (ProvDB, SubDB, embeddings, summaries) are **non-authoritative** and rebuildable.

- Derived state may be deleted and rebuilt from capture.
- No correctness property of continuity may depend on the persistence of derived artifacts.

---

## 2. Ordering and Time

### 2.1 Arrival Order vs Derived Order
Adaptors may receive LUIs in any order.

- The system must not require users to submit LUIs in a curated sequence.
- The system must record whatever timestamps are observed and preserve them as observed.
- Any derived ordering must be explicitly labeled as derived and reproducible.

### 2.2 Irreversibility
Continuity is time-extended and irreversible in the sense that:

- Once captured, an event remains part of history.
- Later interpretation may change, but the underlying capture record does not.

---

## 3. Continuity Invariants (Normative)

### 3.1 Durable Referents
Durable referents must be **event identities**, not semantic labels.

- Joins across layers must rely on stable identifiers, not text similarity or embedding proximity.

### 3.2 Semantic Independence of Correctness
Continuity correctness must not depend on semantic overlays.

- Embeddings, summaries, classifications, and model outputs are overlays.
- If all semantic overlays are removed, continuity geometry and SubDB correctness must remain valid.

### 3.3 SubDB Semantic-Free Requirement
SubDB must be semantic-free for correctness.

- SubDB may store numeric/time/structural relations.
- SubDB must not require semantic joins, embeddings, or inference to satisfy its correctness guarantees.

### 3.4 CAP Correctness Requirement
CAP must not require semantic joins for correctness.

- CAP may expose semantic views, but must remain correct without them.
- CAP must have a defined behavior when semantic overlays are missing.

---

## 4. Contracts and Interfaces (Normative)

The following documents define additional contract surface area:

- `architecture/cmp/contracts/provdb_contract.md`
- `architecture/cmp/contracts/subdb_contract.md`

If conflict exists:
1) This Continuity Operating Contract wins.
2) Then `architecture/invariants.md` wins.
3) Then the more specific contract wins.

---

## 5. Compliance Expectations

A repo state is “continuity-compliant” only if:

- Capture is append-only and authoritative
- Derived artifacts are rebuildable and non-authoritative
- SubDB correctness is semantic-free
- CAP correctness is semantic-free
- Ordering assumptions are explicit and derived (not user-enforced)

---

## 6. Non-Goals (Explicit)

This contract does not require:

- A specific embedding model
- Any visualization or dashboard
- Model-centric explainability of LLM internals
- Reconstructing continuity from end-state artifacts

Those may exist as overlays but are not contractually required.

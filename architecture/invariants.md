# IAM Invariants

These invariants are non-negotiable.
If code or prompts conflict with these invariants, the invariants override.

## 1) Language is infrastructure
Language in this repo is not documentation. It is executable constraint.

- Invariants declared in the repo override inferred intent.
- Prompts are interpreters over the corpus, not authors of new authority.
- Architecture text constrains code; code does not redefine architecture.

## 2) Append-only capture
Capture is mandatory and append-only.

- Ingestion writes only append-only facts.
- No updates or deletes of captured facts.
- Idempotence is required for repeated ingestion.

## 3) Stable identity is event-level
Stable identity is assigned at the event level.

- Durable referents for continuity, annotation, and long-horizon linkage must be event identities.
- Derived identifiers must be traceable to capture provenance.

### Clarification: Node projections are permitted
Event identity is the only durable identity. However, the system may build
policy-versioned, rebuildable node projections (e.g., PRPs, chunkings, sessions)
as non-authoritative layers over events.

Such projections must:
- be explicitly named/versioned (`layer_key`)
- be deterministic and rebuildable from events
- be lossless via ordered membership pointers to event identities
- never be used as durable referents for annotation or long-horizon identity

## 4) Derived structures are rebuildable and non-authoritative
Derived structures (ProvDB, SubDB, overlays) must be rebuildable and replaceable.

- Derived tables are not authoritative; they can be deleted and rebuilt.
- Version overlays explicitly; never overwrite capture.

## 5) Semantic interpretation must never be required for correctness
Continuity correctness must not require semantic interpretation.

- Embeddings, similarity, summaries, and meaning-coordinates are overlays.
- If semantic overlays are removed, continuity geometry must still be valid.

## 6) CAP never performs semantic joins inside the substrate
CAP is read-only orchestration over derived stores.

- Join only by stable IDs.
- Composition is ephemeral and must not be persisted.
- CAP must not depend on semantic joins for correctness.

## 7) Provenance is always preserved
Every derived item must be traceable back to capture.

- Preserve provenance pointers and stable identifiers.
- Preserve raw payloads as opaque ground truth.

## 8) Determinism over cleverness
Builders must be deterministic and traceable.

- Prefer clarity and rebuildability.
- Prefer explicit policies over implicit heuristics.

## 9) Continuity manifold and paths

The continuity manifold is stored in SubDB.

- ProvDB defines coordinate schemas and metric definitions.
- SubDB materializes those coordinates into a manifold.
- Paths exist as curves or sequences within SubDB.
- Semantic meaning interprets nodes and paths but does not define them.

Continuity correctness depends only on SubDB geometry
and ProvDB definitions, not on semantic interpretation.

## 10) Adapters must not require user sequencing

Adapters capture facts and must not require the user to pre-sequence LUIs.

- Adapters must accept LUIs in any arrival order.
- Adapters must not invent semantic sequencing fields or require user-supplied ordering.
- If the source provides an observed time, record it as `observed_ts`.
- If observed time is missing, leave `observed_ts` NULL.

Deterministic ordering is derived downstream using capture facts:
- per stream: `ORDER BY observed_ts NULLS LAST, observed_ts ASC, capture_id ASC`

This ensures continuity can be built without forcing the human to curate sequence.

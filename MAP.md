# MAP

This repository uses language as infrastructure.
If a file is not in this map, it is either supporting material or non-authoritative.

## Authority order (highest → lowest)

1) `writing/` — normative and conceptual foundation  
2) `architecture/` — structural invariants, boundaries, pipelines  
3) `patent/` — legal formalization (claims/disclosure)  
4) `embodiments/` — reductions to practice  
5) `core-ontology/` — shared vocabulary  
6) `residue/` — supporting artifacts  
7) `code/` — non-authoritative prototypes

If contradictions exist, higher authority wins.

## Governing texts

- `architecture/invariants.md` — non-negotiable invariants
- `architecture/continuity-operating-contract.md` — operational guardrails
- `architecture/continuity-strata.md` — dependency strata (replaces “levels as folder” ambiguity)
- `architecture/ingestion-pipeline.md` — adapter → iam.db → provdb → subdb narrative
- `architecture/Migrations.md` — evolution policy
- `Migrations/*.sql` — executable schema law (capture contract)
- `architecture/node-projections.md` — node layers, parallel pairings, SubDB node contract
- `architecture/decisions/node-layer-canonical.md` — canonical layer selection for IAM re-entry

## Evolution rule

- Capture/originals are append-only.
- Derived artifacts are rebuildable and versioned.
- Prompts are interpreters over the corpus, not authors of authority.
- CAP composes ephemerally and never persists composition.

## Working expectation

All changes should be traceable to the governing texts above.

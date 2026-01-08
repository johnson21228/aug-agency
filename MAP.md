# MAP — Repository Authority and Alignment

This document defines the structural map of the repository: how its components relate, where authority resides, and how contradictions are resolved.

## Unifying concern

The unifying concern is preservation of human continuity of thought over time (being-in-time as preserved temporal intelligibility), in environments increasingly mediated by automation.

## Authority order (highest → lowest)

1) `writing/` — normative and conceptual foundation  
2) `architecture/` — structural invariants, boundaries, pipelines  
3) `patent/` — legal formalization (claims/disclosure)  
4) `embodiments/` — reductions to practice  
5) `core-ontology/` — shared vocabulary  
6) `residue/` — supporting artifacts  
7) `code/` — non-authoritative prototypes

If contradictions exist, resolve upward. Lower layers adapt to higher layers.

## Key governing documents

- `language-as-infrastructure.md` — repo-level continuity discipline
- `architecture/invariants.md` — non-negotiable invariants
- `architecture/overview.md` — system identity
- `architecture/continuity-strata.md` — dependency strata (replaces “levels as folder” ambiguity)
- `architecture/ingestion-pipeline.md` — adapter → iam.db → provdb → subdb narrative
- `architecture/migrations.md` — evolution policy
- `migrations/*.sql` — executable schema law (capture contract)

## Evolution rule

- Capture/originals are append-only.
- Derived artifacts are rebuildable and versioned.
- Prompts are interpreters over the corpus, not authorities.

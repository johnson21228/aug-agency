# IAM Core

This repository is structured as a **writings → architecture → embodiment → optional code** system.

The unifying goal of this work is not to build a better AI system, but to preserve and extend **human reasoning continuity** in an environment increasingly shaped by automated and agentic systems.

## How to read this repository

This repository is designed to be read, not executed.

1. **Begin with the introductory essay**
   Start with:

   - `writing/from-task-displacement-to-judgment-scarcity.md`

   This essay provides a neutral, economic framing of the problem space, grounding the project in widely accepted analyses of labor-market polarization and the increasing economic importance of judgment.

2. **Proceed to the core writings**
   Continue with the remaining essays in `writing/`, which develop the concepts of agency, judgment, and continuity that motivate the system.

3. **Move to architecture**
   Read `architecture/` to see how the claims made in the writings are translated into system invariants, layers, and pipelines.

4. **Consult patent materials**
   Use `patent/` for legal crystallization, traceability, and protection of the same ideas.

5. **Review embodiments and code last**
   Treat `embodiments/` and `code/` strictly as optional reductions to practice and feasibility demonstrations.

Code is not authoritative. Architecture does not supersede the writings.

## Repository structure and authority

- `writing/` — normative and conceptual foundation; upstream design constraints and explanatory essays
- `patent/` — provisional drafts, claims, and traceability
- `architecture/` — system invariants and technical truth layer (levels, pipelines, comparisons)
- `embodiments/` — worked examples and reduction-to-practice artifacts
- `core-ontology/` — primitives, invariants, and shared glossary
- `residue/` — prompts, schemas, and samples (redacted)
- `code/` — non-authoritative prototypes (e.g., iOS ingestion app)

## Authority and non-contradiction

All downstream layers—architecture, patents, embodiments, and code—must remain consistent
with the claims made in the writings.

If a contradiction exists, it must be resolved **upward**.
Lower layers adapt to higher layers, never the reverse.

See `MAP.md` for explicit authority boundaries and evolution rules.

# IAM Core

This repository is structured as a **writings → architecture → patent → embodiment → optional code** system.

The unifying goal of this work is not to build a better AI system, but to preserve and extend **human continuity of thought over time** in an environment increasingly shaped by automated and agentic systems. The concern is continuity as lived structure—being-in-time—rather than performance, optimization, or automation.

## How to read this repository

This repository is designed to be read, not executed.

1. **Begin with the introductory essay**

   Start with:

   - `writing/from-task-displacement-to-judgment-scarcity.md`

   This essay provides a neutral, economic framing of the problem space, grounding the project in widely accepted analyses of labor-market polarization and the increasing importance of judgment and continuity in human work.

2. **Proceed to the core writings**

   Continue with the remaining essays in `writing/`, which develop the concepts of agency, judgment, continuity, and temporal coherence that motivate the system. These writings articulate *why* continuity matters and *what is lost* when it is absent. They do not prescribe implementation details.

3. **Move to architecture**

   Read `architecture/` to see how the claims made in the writings are translated into system invariants, layers, and pipelines. The architecture formalizes constraints and structure without reintroducing semantic interpretation or agentic control.

4. **Consult patent materials**

   Use `patent/` for legal crystallization, traceability, and protection of the same ideas. Patent documents and architecture operate in parallel: both express structural commitments, but in different formal languages.

5. **Review embodiments and code last**

   Treat `embodiments/` and `code/` strictly as optional reductions to practice and feasibility demonstrations.

Code is not authoritative. Architecture does not supersede the writings.

## Repository structure and authority

- `writing/` — normative and conceptual foundation; orientation, problem framing, and motivating constraints
- `architecture/` — system invariants and technical truth layer (pipelines, substrates, boundaries)
- `patent/` — legal formalization, claims, and traceability
- `embodiments/` — worked examples and reduction-to-practice artifacts
- `core-ontology/` — primitives, invariants, and shared glossary
- `residue/` — prompts, schemas, and samples (redacted)
- `code/` — non-authoritative prototypes (e.g., ingestion or tooling experiments)

## Authority and non-contradiction

All downstream layers—architecture, patents, embodiments, and code—must remain consistent
with the orientation and claims articulated in the writings.

If a contradiction exists, it must be resolved **upward**.
Lower layers adapt to higher layers, never the reverse.

See `MAP.md` for explicit authority boundaries and evolution rules.

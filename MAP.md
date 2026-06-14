# MAP

This repository uses **language as infrastructure**.  
If a file is not referenced in this map, it is either supporting material or non-authoritative.

MAP defines **authority, governance, and integrity requirements**.  
Narrative explanation belongs elsewhere.

---

## Authority order (highest → lowest)

1) `writing/` — normative and conceptual foundation  
2) `architecture/` — structural invariants, boundaries, pipelines  
3) `LI/` — language-infrastructure contracts and validation surfaces  
4) `patent/` — legal formalization (claims / disclosure)  
5) `embodiments/` — reductions to practice  
6) `core-ontology/` — shared vocabulary  
7) `residue/` — supporting artifacts  
8) `code/` — non-authoritative prototypes  

If contradictions exist, **higher authority wins**.

---

## Governing texts

The following files are **normative**:

- `architecture/invariants.md` — non-negotiable invariants  
- `architecture/continuity-operating-contract.md` — operational guardrails  
- `architecture/continuity-strata.md` — dependency strata (replaces “levels as folder” ambiguity)  
- `architecture/ingestion-pipeline.md` — adapter → iam.db → provdb → subdb narrative  
- `architecture/Migrations.md` — evolution policy  
- `Migrations/*.sql` — executable schema law (capture contract)  
- `architecture/node-projections.md` — node layers, parallel pairings, SubDB node contract  
- `architecture/decisions/node-layer-canonical.md` — canonical layer selection for IAM re-entry  
- `architecture/continuity-manifold-model.md` — continuity manifold storage, paths, and semantic interpretation  

Any document that contradicts these is incorrect.

---

## Evolution rule

- Capture / originals are **append-only**.  
- Derived artifacts are **rebuildable** and versioned.  
- Prompts are **interpreters over the corpus**, not authors of authority.  
- CAP composes ephemerally and **never persists composition**.  

---

## Repository Integrity Gates (Required)

This repository contains structured **Language Infrastructure (LI)** artifacts that must remain **machine-parseable**.

Silent corruption (tabs, malformed YAML/JSON, indentation drift) is considered a structural failure.

To prevent this, the repo defines a **mandatory validation command** and a **recommended pre-commit gate**.

---

### LI Validation Command

The canonical validation command is:

- `make li-validate`

This command must succeed before committing any changes to:

- `LI/**`
- any structured `index.source.{yaml,json}` files within LI scopes

Failure indicates the repository is not in a solid-state, auditable condition.

---

### Pre-Commit Hook (Recommended)

To automatically enforce `make li-validate` on every commit, configure this repository to use the provided hooks:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

---

## Workbench Template Operating Layer

This repo has been updated to carry the current Workbench LI template operating surface.

The existing IAM authority order above remains the domain authority for Augmented Agency / IAM substance. The lowercase `li/` layer governs Workbench operating process: repo loop, source truth, generated-artifact status, Capture Back, packaging, verification, and handoff.

### Required read-first files for Workbench operation

```text
LLM_READ_FIRST.md
HOW_LI_RULES.md
SPINE.md
li/workflow/workbench_build_loop.md
li/workflow/visible_workflow_outcome_contract.md
tools/verify_li_governance.py
```

### Core Workbench operating LI

```text
li/core/workbench_principles.md
li/core/human_custody.md
li/core/llm_role.md
li/core/generated_artifacts_are_evidence.md
li/source/source_truth.md
li/source/source_context_map.md
li/source/authority_levels.md
li/repo/history_pattern.md
li/repo/overlay_workflow.md
li/repo/packaging_contract.md
li/repo/verification_contract.md
```

### Compatibility rule

When IAM domain authority and Workbench operating authority appear to conflict, report the conflict and defer to human/domain owner judgment. Do not silently merge or overwrite authority.

### Generated artifact boundary

Generated artifacts are evidence only. They do not govern the repo.

Examples:

```text
dist/**
outputs/history/repo_history_for_llm_*.md
artifacts/workbench_repo_inventory_*.md
generated diagrams
exported packs
```

### Expected Makefile targets

```text
make verify
make verify-li
make history
make clean-li
make pack
make read-first
make inventory
```


# LLM_READ_FIRST — Augmented Agency / IAM Workbench

Read this before answering from this repository.

This repo is an Augmented Agency / IAM Language Infrastructure repository that now carries the current Workbench LI template operating surface.

## Required first move

Before answering, editing, generating, summarizing, or recommending changes:

1. Open `MAP.md`.
2. Identify whether the task is about IAM domain authority or Workbench operating process.
3. Identify the task-specific governing files.
4. Separate authority from evidence.
5. Make changes at the governing layer first.
6. Regenerate generated artifacts from the governing layer.
7. Verify before claiming success.

## Authority order

Use this repo-specific authority order:

1. Human/domain owner judgment.
2. `MAP.md` and existing IAM domain authority (`writing/`, `architecture/`, uppercase `LI/`, `core-ontology/`, `patent/`, `embodiments/`).
3. Workbench operating LI (`li/`, `HOW_LI_RULES.md`, `SPINE.md`, tools, Makefile, prompts, cards).
4. Git history.
5. Tests, verifiers, generators, and Makefile targets.
6. Continuity cards and source-context maps.
7. Generated artifacts as evidence only.
8. LLM interpretation.

## Compatibility rule

Do not collapse this repo into a generic template.

The lowercase `li/` layer governs the Workbench loop, Capture Back, packing, verification, handoff, and LLM/repo discipline. The existing IAM corpus governs the Augmented Agency thesis, ontology, architecture, and patent-sensitive claims.

If the two surfaces appear to conflict, stop and report the conflict.

## Generated artifacts are evidence only

Generated artifacts do not govern the repo. Examples include `dist/**`, `outputs/**`, generated packs, generated repo-history artifacts, generated summaries, generated diagrams, exported HTML/PDF/slides, and inventories.

If generated evidence is wrong, repair the governing source, LI, prompt, tool, Makefile target, verifier, or test, then regenerate.

## Sensitive material rule

Patent/provisional material and private conversation exports require explicit human approval before broad commit or sharing.

## Handoff rule

When finished, report:

- governing files read
- governing files changed
- generated artifacts regenerated
- commands/verifiers run
- remaining conflicts or handoff notes

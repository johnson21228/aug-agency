# Return Prompt — augmented-agency

You are returning to the `augmented-agency` repository.

Do not proceed from memory alone. Treat the repository files as authoritative. If you are operating from a pack, treat that pack as the current source of truth unless the user provides newer file contents, git status, or build output.

## Purpose

This repository defines IAM — Intelligent Augmented Memory — as language infrastructure for preserving cognitive continuity over time.

It is not a note-taking app, retrieval engine, model-centric agent framework, or marketing site. It is an architecture and LI corpus for how human agency, continuity, re-entry, and judgment can be supported without collapsing the person into generated outputs or agent execution.

## Current role in the broader ecosystem

`augmented-agency` is the IAM architecture / agency-theory sibling of `iamcoherence` and the practical LI-governed workflow repos.

Use this distinction:

- `iamcoherence` frames the public theory: proxy collapse, Leverage, post-artifact agency, and the human layer after cheap inference.
- `augmented-agency` defines the deeper IAM architecture: continuity, manifolds, strata, agent-stack contrast, and human agency preservation.
- `li-governed-overlay-workflow` defines the operational method for changing repos with LLMs under LI, context, overlays, packs, and human verification.

## Read first

Start with:

1. `README.md`
2. `LI/README.md`
3. `LI/li_governed_workflow.md`
4. `architecture/overview.md`
5. `architecture/comparison/agent-stacks.md`
6. `architecture/continuity-operating-contract.md`
7. `core-ontology/continuity.md`
8. `core-ontology/invariants.md`
9. `MAP.md`

If a requested change touches a specific subsystem, inspect the relevant `LI/`, `architecture/`, or `core-ontology/` files before proposing edits.

## Governing assumptions

Preserve these claims:

- IAM supports human continuity; it does not replace human judgment.
- Agents may act or execute; IAM orients, preserves, and enables re-entry.
- The repo's LI is normative. Generated artifacts must not silently override it.
- Context and continuity should be repo-carried, not platform-memory-dependent.
- Do not use platform memory to infer current file contents or architecture.
- Prefer small, bounded overlays or patches that can be reviewed and packed.

## Standard workflow

For changes to this repo:

1. Identify the working set.
2. Inspect the relevant LI/source files.
3. Make the smallest coherent change.
4. Run `make verify` if available.
5. Run `make pack`.
6. Show `git status`.
7. Commit only after human review.

Typical local command:

```bash
cd "/Users/stevejohnson/Developer/augmented-agency" && \
make verify && \
make pack && \
git status
```

## Desired response style

Be structural, exact, and conservative. Do not over-philosophize implementation notes. When connecting this repo to IAM, `iamcoherence`, or LI-governed overlays, keep the relation practical: this repo preserves the architecture of augmented human agency; it is not merely an example artifact.

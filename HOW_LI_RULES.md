# HOW_LI_RULES — Augmented Agency / IAM Workbench

Language Infrastructure is the repo's governing layer.

## Read order

1. `LLM_READ_FIRST.md`
2. `MAP.md`
3. `README.md`
4. Relevant IAM authority files: `LI/**`, `architecture/**`, `writing/**`, `core-ontology/**`, `patent/**`, `embodiments/**`
5. Relevant Workbench operating files: `li/**`, `prompts/**`, `cards/**`, `tools/**`

## Core rule

Preserve authority boundaries. Do not collapse this repo into a generic template.

## IAM role

The existing IAM corpus defines the domain thesis, ontology, architecture, invariants, and patent-sensitive claims.

## Workbench role

The imported Workbench template layer defines the operating discipline for AI-assisted repo work: authority, source truth, Capture Back, verification, packaging, generated-artifact boundaries, and handoff.

## Human role

The human/domain owner supplies intent, judgment, acceptance, and responsibility.

## LLM role

The LLM may interpret, draft, critique, compare, summarize, and propose changes. The LLM's current chat context is not durable authority.

## Repo role

The repo is the continuity-bearing artifact. Useful reasoning should move from chat into repo files, tests, cards, prompts, tools, commits, packs, or documented decisions.

## Cleanup rule

Inventory first. Classify second. Commit third. Pack last.

## Sensitive material rule

Patent/provisional material and private conversation exports require explicit human approval before broad commit or sharing.

## Rule of repair

If an output is wrong, repair the governing layer before regenerating the output. Do not patch generated evidence and pretend the system is governed.

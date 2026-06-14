# Workbench Template Alignment Bridge — Augmented Agency / IAM

This repository has been updated to carry the current Workbench LI template operating surface while preserving its existing Augmented Agency / IAM authority.

## What changed

- Added the current lowercase `li/` Workbench governance layer from the template.
- Added current Workbench prompts, notes, docs, Makefile targets, and verification tools.
- Preserved existing IAM domain authority in `writing/`, `architecture/`, uppercase `LI/`, `core-ontology/`, `patent/`, and `embodiments/`.
- Added a compatibility rule: Workbench template files govern the repo loop; IAM files govern the domain thesis.

## Authority compatibility

The current repo now has two complementary surfaces:

1. **IAM domain authority** — what Augmented Agency / IAM means and claims.
2. **Workbench operating authority** — how AI-assisted repo work is captured, verified, packed, and handed forward.

When these conflict, do not silently merge them. Report the conflict and ask for human judgment.

## Practical workflow

Use the template workflow for repo work:

```text
latest pack -> LLM reasoning -> overlay / file changes -> local execution -> verify -> commit -> pack -> repeat
```

Use the IAM authority files for substance:

```text
MAP.md
README.md
architecture/**
LI/**
writing/**
core-ontology/**
```

Use the Workbench governance files for process:

```text
LLM_READ_FIRST.md
HOW_LI_RULES.md
SPINE.md
li/**
tools/verify_li_governance.py
tools/check_template_integrity.py
Makefile
```

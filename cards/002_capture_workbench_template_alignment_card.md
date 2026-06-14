# Card 002 — Capture Workbench Template Alignment

## Status

Accepted.

## Context

The Augmented Agency / IAM repo needed to be updated so it carries the current Workbench LI template operating surface without losing its existing IAM authority.

## Decision

Preserve existing domain authority in `MAP.md`, `README.md`, uppercase `LI/`, `architecture/`, `core-ontology/`, `patent/`, and `embodiments/`.

Import the current template operating layer under lowercase `li/`, plus current Workbench prompts, docs, notes, tools, Makefile targets, and verification behavior.

## Acceptance rule

The update is acceptable only if both are true:

1. The repo can pass Workbench template/governance verification.
2. The repo-specific IAM authority remains explicit and is not replaced by generic template language.

## Verification

Run:

```bash
make verify
make pack
```

## Handoff

Future changes should identify whether they modify IAM domain authority or Workbench operating process before editing files.

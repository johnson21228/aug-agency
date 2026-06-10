# Template Update Without Authority Collision

## Rule

When importing from `workbench-li-template` into `augmented-agency`, do not mistake template structure for repo authority.

This repo's authority surface is already defined by `MAP.md` and uppercase `LI/`.

Template updates should be adapted into the current repo structure unless a separate migration explicitly decides to adopt the template's lowercase `li/` tree.

## Why

The template is a source of reusable workflow intelligence. It is not automatically higher authority than this repo's existing IAM / Augmented Agency architecture.

## Import policy

Promote from template:

- Capture Back discipline
- Workbench Experiential Intelligence
- clean pack / history / cleanup habits
- read-first governance
- human custody and source authority habits
- root inventory discipline

Demote / avoid by default:

- wholesale replacement of `MAP.md`
- duplicate lowercase `li/` authority tree
- template README overwrites
- generic Workbench wording that weakens IAM-specific meaning

## Preferred mapping

```text
workbench-li-template/li/workflow/*  ->  augmented-agency/LI/workflow/*, when conceptually accepted
workbench-li-template/cards/*        ->  augmented-agency/cards/*, when accepted as continuity card
workbench-li-template/prompts/*      ->  augmented-agency/prompts/*, if useful as operator prompt
workbench-li-template/tools/*        ->  augmented-agency/tools/*, adapted to this repo's structure
```

## Practical guard

Before applying a template update, ask:

1. Is this a reusable governance pattern or a template-specific file layout?
2. Does it strengthen the Augmented Agency repo's authority surface?
3. Does it collide with existing `MAP.md`, `README.md`, or `LI/` semantics?
4. Should it be a card first rather than a governing file?

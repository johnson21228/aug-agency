# Language as Infrastructure: Repository Discipline for IAM

## Overview

This repository is structured around a deliberate principle:

**language is not just documentation of the system — it is part of the system’s infrastructure.**

Every major invariant, architectural commitment, and process boundary is expressed in text, versioned alongside code, and made available for ingestion by both humans and language models. This discipline is what allows IAM to be built coherently across time, tools, and collaborators without collapsing into ad hoc prompts, implicit assumptions, or model-specific behaviors.

The `pack_md_repo.py` output is not merely a convenience artifact. It is a continuity bundle: a structured, canonical snapshot of the system’s declared meaning, constraints, and intent at a given point in time.

## The Role of `pack_md_repo.py`

At a mechanical level, `pack_md_repo.py` gathers markdown (and selected code) files into a single ingestible artifact suitable for a large language model.

At a conceptual level, it does something more important:

- It makes the repository legible as a single continuity surface.
- It ensures that prompts operate against declared invariants, not latent assumptions.
- It allows the same body of text to support multiple purposes:
  - design reasoning
  - code generation
  - review and critique
  - translation
  - continuity stitching

The packed output is intentionally neutral: it does not tell a model what to do. Instead, it ensures a model cannot ignore what has already been decided.

## Embedded Invariants as First-Class Artifacts

Files such as:

- `architecture/invariants.md`
- `architecture/overview.md`
- `architecture/ingestion-pipeline.md`
- `architecture/continuity-strata.md`
- `architecture/migrations.md`
- `MAP.md`

are not explanatory afterthoughts. They are structural constraints expressed in language.

By embedding these directly in the repo and including them in the packed artifact:

- Every generation task is conditioned on the same invariants.
- Human review and model output share the same reference frame.
- Drift becomes visible because it contradicts text rather than memory.

This mirrors the architectural stance of IAM itself: continuity is preserved not by inference, but by re-entry into prior structure.

## Prompts as Interpreters, Not Authorities

Within this discipline, prompts are treated as interpreters over a stable corpus, not as creative authorities.

A single packed repository snapshot can be paired with different prompts to:

- generate code
- propose refactors
- translate content
- summarize deltas
- construct schemas
- emit migration steps

The power does not live in the prompt alone. It lives in the combination of:

- a stable language corpus
- explicitly declared constraints
- narrowly scoped prompts that operate within those bounds

This separation is what allows multiple LLMs, copilots, or tooling generations to be used over time without re-litigating fundamentals.

## Language Discipline Across Code and Process

The same discipline applies to code and schemas:

- the capture schema is introduced via numbered migration files (`migrations/0001_capture_contract.sql`)
- builders (`iam.db → provdb → subdb`) are deterministic and rebuildable
- continuity identifiers, breadcrumbs, and capture contracts are described before they are implemented

As a result, code generation is constrained synthesis against a declared architecture.

This is essential for IAM, whose core stance is that meaning and judgment remain human while computation preserves structure.

## Supporting IAM Through to App Store Release

This repository discipline directly supports the long arc from concept to shipped application:

- Early design decisions remain accessible and enforceable.
- New contributors (human or model) can be onboarded via text, not tribal knowledge.
- iOS, backend, and tooling code can be generated or reviewed against the same invariants.
- Privacy and architectural claims remain traceable to first principles.

Most importantly, it prevents a common failure mode: gradual erosion of intent as implementation details accumulate.

By insisting that every level of the system is described in language, versioned, and packable, IAM maintains continuity of thought across its own construction — the same continuity it is designed to preserve for its users.

## Summary

`pack_md_repo.py` is not a build step; it is a continuity mechanism.

Embedding architecture, invariants, and process as language ensures that:

- humans and models reason from the same ground
- prompts remain interpreters, not authors
- the system can evolve without losing itself

This is not incidental to IAM. It is how IAM can be built at all.

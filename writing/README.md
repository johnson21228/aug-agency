# Writings

This directory contains the **conceptual and normative foundation** of the IAM project.

The writings are not commentary, documentation, or marketing material.
They articulate the core problems, stakes, and claims that the rest of the repository
exists to operationalize.

All downstream layers—architecture, patents, embodiments, and code—must remain
consistent with the claims made here.

## Purpose of the writings

The essays in this directory serve three roles:

1. **Problem definition**
   They describe the structural pressures facing human judgment, agency, and continuity
   in an environment increasingly shaped by automated and agentic systems.

2. **Normative constraints**
   They define what outcomes are desirable, what tradeoffs are unacceptable,
   and what the system explicitly should *not* become.

3. **Conceptual grounding**
   They introduce concepts—continuity, judgment, temporal coherence, asymmetry—that
   later appear in architectural invariants and system design.

If a downstream artifact contradicts a claim made in these writings,
the downstream artifact is wrong.

## How to read the writings

Readers new to the project should:

1. Begin with the primary orientation essay(s), which frame the overall concern
   around agency, judgment, and continuity.
2. Proceed to essays that connect those concerns to inference, memory, and system design.
3. Treat economic or structural essays as context-setting rather than implementation guides.

The writings are intended to be read slowly and independently of the code.

## Relationship to other layers

- **Architecture (`architecture/`)**
  Translates the claims in these writings into system invariants, layers, and protocols.

- **Patent materials (`patent/`)**
  Express the same ideas in legal form, with traceability to both writings and architecture.

- **Embodiments and code (`embodiments/`, `code/`)**
  Demonstrate feasibility only. They are not authoritative.

## Drafts and evolution

If a `drafts/` subdirectory is present, it contains working material that may be incomplete
or exploratory. Drafts do not supersede finalized essays unless explicitly promoted.

No writing should be removed or rewritten to accommodate a downstream implementation.
Evolution proceeds by addition, clarification, or explicit revision.

## Scope and non-goals

The writings do not attempt to:
- Propose a general theory of intelligence
- Compete with existing AI model architectures
- Optimize for predictive accuracy or automation

They are concerned specifically with the preservation and extension of **human reasoning
continuity over time**.

For repository-wide authority rules, see `MAP.md`.

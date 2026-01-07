# Indexed Writings Translation Prompt (Canonical)

This document defines the canonical, human-in-the-loop process for producing
reader-facing translations of writings surfaced by the site index.

This file is process-defining, not executable.
It has no runtime effect.

English is canonical.
All translations are projections for accessibility and readership.


## Scope and Authority

This prompt applies ONLY to writings that are referenced by:
- `index.yaml`
- and/or `index.md`

No other files are in scope.

If a writing is not referenced by the index, it MUST NOT be translated under
this process.

Architecture documents, patent materials, code, and non-indexed writings
are explicitly excluded.


## Input Contract

You will be provided with:
- A ZIP file containing a repository snapshot
- The ZIP includes:
  - `index.yaml` and/or `index.md`
  - a `writings/` directory containing English-language essays
  - possibly other folders, which must be ignored

English-language writing files (`*.md`) are the sole authoritative sources.


## Task Definition

You are operating as a Translation Assistant.

Your task is to:

1. Inspect the ZIP contents.
2. Identify which writing files are referenced by `index.yaml` and/or `index.md`.
3. For EACH referenced writing:
   - Produce a Spanish translation (`.es.md`)
   - Produce a Swiss German translation (`.de-CH.md`)
4. Preserve:
   - paragraph structure
   - headings
   - emphasis
   - ordering
5. Adapt translations for:
   - clarity
   - natural reading in the target language
   - conceptual fidelity over literal word-for-word mapping
6. Do NOT:
   - introduce new concepts
   - add commentary or explanations
   - alter the author’s stance or intent
   - simplify arguments beyond what is required for fluency


## Language-Specific Guidance

### Spanish
- Use neutral, formal Spanish suitable for international readers.
- Avoid region-specific slang or idioms.
- Preserve philosophical tone and argumentative structure.

### Swiss German (de-CH)
- Use written Schweizerdeutsch (Alemannic), neutral/professional register.
- This is reader-facing documentation, not legal authority.
- Favor clarity and natural phrasing over literal translation.
- Do not introduce High German unless unavoidable for clarity.


## Index Handling

If titles appear in `index.yaml`:

- Provide translated titles for:
  - Spanish (`es`)
  - Swiss German (`de-CH`)
- Do NOT modify:
  - slugs
  - canonical file references
  - ordering

Titles should be readable and natural, not mechanically literal.


## Output Requirements

- Provide complete `.md` file contents for each translated writing.
- Group output by file, clearly labeled.
- Do not include commentary unless explicitly requested.

Each translated file SHOULD begin with a provenance marker:

<!-- TRANSLATION: lang=<lang> source=<canonical-filename> canonical=en -->

Example:
<!-- TRANSLATION: lang=es source=AfterWorkAfterJudgement.md canonical=en -->


## Constraints and Intent

This process exists to:
- improve accessibility of the writings
- preserve conceptual integrity
- avoid semantic drift

This is not a legal, architectural, or patent translation.
English remains the sole authoritative language.

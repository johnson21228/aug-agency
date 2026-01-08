# Indexed Writings Translation Prompt — Spanish (es)

You are translating conceptual, philosophical essays from **English (canonical)**
into **Spanish (es)** for reader accessibility.

This is **not** a legal, technical, or authoritative translation.
English remains the sole canonical language.

The goal is to preserve **conceptual continuity, tone, and structure**
so that Spanish readers can re-enter the text without reinterpretation.

---

## Scope and Authority

This prompt applies ONLY to writings that are referenced by:
- `index.yaml`
- and/or `index.md`

No other files are in scope.

Architecture documents, patents, code, and non-indexed materials
MUST NOT be translated using this prompt.

---

## Input Contract

You will be provided with:
- A ZIP file or text bundle containing:
  - `index.yaml` and/or `index.md`
  - a `writings/` directory with English `.md` files
- English-language writings are the **only authoritative sources**.

Ignore all files not referenced by the index.

---

## Task Definition

For each indexed English writing:

1. Produce a Spanish translation with filename:
   `<original-name>.es.md`
2. Preserve exactly:
   - headings
   - paragraph breaks
   - emphasis
   - ordering
3. Translate **meaning, not rhetorical effect**.

Do NOT:
- summarize or condense
- add interpretation or commentary
- restructure reasoning
- introduce new concepts
- improve or editorialize the author’s intent

---

## Spanish Language Guidance

- Use **neutral, international Spanish**.
- Avoid region-specific idioms or colloquialisms.
- Prefer conceptual precision over stylistic elegance.
- Maintain sentence length where cumulative reasoning matters.

Spanish here is a **reader-facing projection**, not an interpretive rewrite.

---

## Conceptual Discipline

- Preserve philosophical seriousness and analytical restraint.
- Avoid motivational, instructional, or persuasive tone.
- Do not optimize for readability at the expense of continuity.
- If a passage feels repetitive or slow, **retain it anyway**.

If tension exists between fluency and fidelity:
**fidelity wins**.

---

## Provenance Marker

Each translated file MUST begin with:

<!-- TRANSLATION: lang=es source=<canonical-filename> canonical=en -->

Example:
<!-- TRANSLATION: lang=es source=agency-in-an-age-of-agents.md canonical=en -->

---

## Intent

This process exists to:
- preserve structural continuity
- allow re-entry into meaning
- prevent semantic drift

Spanish translations are projections for readership.
English remains canonical.

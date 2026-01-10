## Relationship to Root Repository Language

This `Language/` folder is a local instantiation of the repo’s “Language as Infrastructure” pattern.
It exists to govern the IAM iOS embodiment only.

### Root authority (upstream)

The following are upstream and authoritative over this app:

- `README.md` (root) — method and authority ordering
- `writing/overview.md` and `writing/essays/` — normative claims and consequences
- `architecture/` — system invariants and architectural constraints
- `core-ontology/` — stable primitives and shared terminology

### Local authority (this folder)

This folder may:
- specialize upstream goals into iOS-scoped requirements,
- define app-local interface contracts,
- define feature specs and acceptance criteria,
- constrain LLM-generated code and patches for this app.

This folder must NOT:
- contradict upstream premises or invariants,
- redefine core terms in incompatible ways,
- treat app implementation as the source of truth.

### Rule of precedence

If a local spec conflicts with upstream language, the local spec is wrong.
Update local language to conform to root, or revise upstream only if the intent of the repository has changed.

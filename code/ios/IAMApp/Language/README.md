# IAMApp — Language as Infrastructure

This folder is the governing language layer for the IAM iOS app.

It defines:
- goals and non-goals,
- invariants and constraints,
- interface expectations,
- feature specifications,
- development workflow rules.

This folder is authoritative for the app.
If code and language disagree, code is wrong.

---

## Relationship to Root Repository Language

This `Language/` folder is a local instantiation of the repository’s
“Language as Infrastructure” pattern.

### Upstream authority

The following are authoritative over this app:

- root `README.md`
- `writing/overview.md`
- `architecture/`
- `architecture/legibility.md`
- `core-ontology/`

Local language must not contradict upstream premises or invariants.

---

## Local Authority Order

1. `Language/Goals.md`
2. `Language/Invariants.md`
3. `Language/Interfaces/`
4. `Language/Specs/`
5. Swift code (implementation)

If a lower layer conflicts with a higher layer, the lower layer is wrong.

---

## Workflow Rule

- Language defines intent.
- Code implements intent.
- Xcode debugs intent.

Design changes originate in language.
Xcode is an instrument, not a source of authority.

---

## Platform Scaffold Note

An Apple sample project may exist under a scaffold directory.
That scaffold is non-authoritative and must conform to this language layer.

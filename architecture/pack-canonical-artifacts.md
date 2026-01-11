# Canonical Pack Artifacts

This document defines what “packed repo output” means for IAM audits and boot prompts.
It exists to prevent ambiguity and oral tradition.

This document is **authoritative**.

---

## 1. Current State (As Implemented)

The tool `Tools/pack_md_repo.py` produces a ZIP bundle (e.g., `augmented-agency-ingest-md-py.zip`)
containing a curated subset of the repository artifacts.

This output is a *packaged file set*, not a single consolidated Markdown artifact.

---

## 2. Canonical Packed Representation for LLM Audits

IAM LI audits require one of the following as canonical packed representation:

### Option A — Single Consolidated Markdown (Preferred)
A single Markdown document that concatenates the authoritative text corpus:
- architecture docs
- ontology docs
- contracts
- README + MAP/index material
- selected essays (as configured)

This artifact is considered the “audit pack”.

### Option B — Deterministic ZIP + Manifest (Acceptable)
A deterministic ZIP output plus a manifest listing:
- included files
- excluded files
- deterministic ordering
- hash for each included file

This approach is acceptable if the audit process operates directly on the ZIP contents.

---

## 3. Required Action (Repo-Wide Consistency)

All boot prompts must specify which canonical pack form they expect:
- A single consolidated Markdown audit pack (Option A), or
- The deterministic ZIP + manifest (Option B)

Until Option A exists, audits should treat the ZIP + manifest as canonical.

---

## 4. Minimal Requirements for Pack Canonicality

Any canonical pack must:
- be reproducible from the repo state
- enumerate included/excluded artifacts
- avoid silently changing scope between runs

---

## 5. References

- Tool: `Tools/pack_md_repo.py`
- Tool: `Tools/pack_writings.py`
- Tool: `Tools/update_writing_index.py`
- Authority: `architecture/continuity-operating-contract.md`
- Authority: `architecture/invariants.md`

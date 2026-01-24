# Runtime Anchors — Language Infrastructure (LI)

## Purpose
This document specifies **anchor semantics** for the IAM runtime layer.
Anchors define the *local origin* from which charts are constructed and semantic navigation occurs.

Anchors are **runtime constructs** derived from events recorded in `iam.db`. They are not substrate authority unless explicitly written back as user-authored annotations.

---

## 1. Definitions

### 1.1 Anchor
An **anchor** is a reference to a specific, experienced event (or short contiguous segment) recorded in `iam.db`.

Formal definition:
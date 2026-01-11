# IAMApp Goals

This document defines what the IAM iOS app exists to do.

---

## App Scope (iOS)

IAMApp provides a conversational interface for interacting with a single
user’s continuity over time.

The app is responsible for the full local Continuity Materialization Pipeline (CMP):

- capture LUIs from multiple sources,
- persist substrate data locally (`iam.db` and downstream stores),
- materialize derived stores using the same stage boundaries as repo scripts,
- present continuity through a conversational interface that supports re-entry.

---

## Data Boundary (“Apple Moat”)

All substrate data and derived stores live locally on Apple devices by default.

Sharing and export are:
- explicit,
- user-controlled,
- copy-producing.

No background upload or cloud dependency defines correctness.

---

## Model Usage

The app may use Apple Foundation Models for local inference as an optional
implementation detail.

No framework, model, or inference system defines correctness.

The app may issue one-shot inference requests to external LLM endpoints
only when:
- credentials are explicitly configured,
- the user enables such usage.

External inference must remain optional and non-authoritative.

---

## Photos Pattern (Library + Explicit Sharing)

IAMApp behaves like Photos:

- the on-device library is authoritative,
- sharing and export are explicit and user-initiated,
- sync is optional and never defines correctness,
- imports append or create namespaces; they do not overwrite continuity.

This is a structural pattern, not an API requirement.

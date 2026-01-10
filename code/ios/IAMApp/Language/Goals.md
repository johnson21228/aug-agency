## App Scope (iOS)

The app provides a conversational UI for interacting with a single user’s continuity.

The app is responsible for the full local pipeline:
- capture LUIs from multiple sources,
- persist substrate data locally (iam.db and downstream stores),
- run the same processing stages defined in this repo’s desktop scripts,
- present continuity through a conversational interface that supports re-entry.

## Data Boundary (“Apple moat”)

All substrate data and derived stores live locally on Apple devices by default.
Sharing is explicit and user-controlled, using OS-level sharing mechanisms comparable to Photos sharing.

## Model Usage

The app may use Apple Foundation Models for local inference.
The app may also issue one-shot inference requests to external LLM endpoints when credentials are present and explicitly configured.
External inference must remain optional and must not be required for substrate correctness.

# Continuity Node Contract

Continuity nodes are derived artifacts produced from one or more source LUIs.
They are suitable for storage in `SubDB` and represent a geometric, time-anchored
continuity substrate.

Continuity nodes are **derived** and therefore non-authoritative. They MUST
carry provenance sufficient to recompute or supersede them.

## Required invariants

A continuity node MUST:
1) Link to one or more source LUIs (`source_lui_ids[]`).
2) Provide a stable `node_id` suitable for SubDB storage.
3) Provide an explicit time anchor.
4) Provide semantic space coordinates (numeric).
5) Provide derivation provenance (engine + recipe hash).
6) Be append-only: updates occur via supersession, not mutation.

## Minimal required schema (YAML form)

```yaml
continuity_node:
  node_id: string                # REQUIRED (stable)
  node_kind: string              # REQUIRED (e.g. "continuity")

  source_lui_ids:                # REQUIRED (one or more client_lui_id from iam.db)
    - string

  derivation:                    # REQUIRED
    engine: string               # e.g. "apple_fm_ondevice", "local_llm", "openai"
    engine_version: string
    recipe_hash: string          # hash of the derivation recipe/policy/prompt
    derived_at: string           # RFC3339

  time:                          # REQUIRED
    captured_at: string          # RFC3339 (primary time anchor)
    span:                        # OPTIONAL
      start: string
      end: string

  semantic_coordinates:          # REQUIRED
    space_id: string             # identifies the semantic manifold / basis
    vector:                      # numeric coordinates; dimension defined by space_id
      - number

  status: string                 # REQUIRED: "active" | "superseded" | "deprecated"
  supersedes:                    # OPTIONAL: prior node_id(s)
    - string
## Add: `LI/derive/ChunkingContract.md` (canonical)

```markdown
# Chunking Contract (Bounded Inference Constraint)

Semantic coordinate derivation requires bounded-context inference (e.g. on-device
models). Therefore, LUIs MUST be segmentable into bite-sized chunks while
preserving continuity.

## Required invariants

A chunking pipeline MUST satisfy:

1) Coverage: every source LUI is representable as one or more chunks.
2) Order: chunks are totally ordered within their parent LUI.
3) Traceability: each chunk links back to the source LUI and declares its span.
4) Continuity preservation: boundaries must preserve re-entry/trajectory.
5) Budget compliance: each chunk fits a declared inference budget.
6) Recomposability: chunks recombine losslessly into the original LUI text.

## Minimal required schema (YAML form)

```yaml
lui_chunk:
  chunk_id: string               # REQUIRED (stable)
  source_lui_id: string          # REQUIRED (client_lui_id from iam.db)

  order:
    index: integer               # REQUIRED (0..n-1)
    total: integer               # REQUIRED (n)

  span:
    kind: string                 # REQUIRED ("text"|"bytes"|"tokens"|"time")
    start: integer               # REQUIRED
    end: integer                 # REQUIRED

  time:
    captured_at: string          # REQUIRED (RFC3339)
    source_timestamp: string     # OPTIONAL (adapter-provided)

  content:
    text: string                 # REQUIRED (lossless chunk text)

  continuity:
    left_context: string         # OPTIONAL (small prefix carry-over)
    right_context: string        # OPTIONAL (small suffix carry-over)
    boundary_hint: string        # OPTIONAL ("sentence","paragraph","turn",...)

  inference_budget:
    max_tokens: integer          # OPTIONAL
    max_bytes: integer           # OPTIONAL
    max_latency_ms: integer      # OPTIONAL

  derivation:
    chunker_version: string      # REQUIRED
    policy_hash: string          # REQUIRED
## Embodiment: On-Device ChatGPT History Ingestion (Apple Moat)

One pipeline path ingests ChatGPT conversation history into a persistent on-device Atlas store (inside the Apple boundary).

The invariant is not chunking. The invariant is that explicit human-generated language inputs (LUIs) are captured as durable, addressable events so CAP can form continuity structures and IAM can provide re-entry services without semantic inference.

### Source-of-Record Capture (LUIs)

ChatGPT export data is parsed into a stream of LUI event records. Each event is stored as an opaque trace with stable identifiers and ordering.

Minimum fields:
- `lui_id` (stable id)
- `t` (timestamp)
- `seq` (monotonic within conversation)
- `actor` (`user | assistant | tool | system`)
- `text` (raw, exact)
- `source.*` provenance (below)

### Provenance (Structural Traceability)

The semantic source is identified structurally, not interpretively, using provenance fields such as:
- `source.system = "chatgpt"`
- `source.conversation_id`
- `source.message_id`
- `source.export_id` (file hash / export identifier)
- `source.capture_method` (`import | share | copy`)

This enables auditability, deterministic re-ingest, and stitching without requiring semantic interpretation.

### CAP Construction Over IDs

CAP structures are constructed over LUI identifiers, for example:
- return points (pointers to `lui_id` or ranges)
- regions/charts (sets or intervals of LUIs)
- adjacency and stitching edges

These structures support re-entry and longitudinal navigation even with no semantic overlays.

### Optional Overlays (Non-Authoritative)

Chunking, topic boundaries, summaries, or Foundation Model assistance may be computed as overlays to improve usability. Overlays must remain:
- separable from the LUI source-of-record,
- versioned and replaceable,
- non-authoritative for continuity correctness.

Continuity remains valid if overlays are removed.

## Embodiment: On-Device ChatGPT History Ingestion (Apple Moat)

One pipeline path ingests ChatGPT conversation history into a persistent on-device Atlas store (inside the Apple boundary).

The invariant is not chunking.  
The invariant is that explicit language acts (LUIs) are captured as durable, addressable events so CAP can preserve continuity and IAM can provide re-entry services without semantic inference.

---

### Source-of-Record Capture (LUIs)

ChatGPT export data is parsed into a stream of LUI event records. Each event is stored as an opaque trace with stable identifiers and ordering.

LUIs may include human-authored language acts and system or assistant responses retained as contextual traces. No meaning is inferred from content at ingest.

Minimum fields:
- `lui_id` — stable identifier
- `t` — timestamp
- `seq` — monotonic sequence within the source stream
- `actor` — `user | assistant | tool | system`
- `text` — exact raw text (opaque payload)
- `source.*` — provenance (below)

---

### Provenance (Structural Traceability)

The semantic source is identified structurally, not interpretively, using provenance fields such as:
- `source.system = "chatgpt"`
- `source.conversation_id`
- `source.message_id`
- `source.export_id` — file hash or export identifier
- `source.capture_method` — `import | share | copy`

This enables auditability, deterministic re-ingest, and continuity stitching without requiring semantic interpretation.

---

### CAP Continuity Over Identifiers

CAP operates over LUI identifiers rather than content meaning.

Continuity structures may include:
- return points (pointers to `lui_id` or identifier ranges),
- regions or charts (sets or intervals of LUIs),
- adjacency links (temporal ordering),
- stitching edges (links between regions).

These structures support re-entry and longitudinal navigation even when no semantic overlays are present.

---

### Optional Overlays (Non-Authoritative)

Chunking, topic boundaries, summaries, or Foundation Model assistance may be computed as optional overlays to improve usability.

Overlays MUST remain:
- separable from the LUI source-of-record,
- versioned and replaceable,
- non-authoritative for continuity correctness.

Continuity remains valid if overlays are removed.

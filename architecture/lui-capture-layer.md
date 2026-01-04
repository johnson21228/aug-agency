# LUI Capture Layer (Source-of-Record)

This document defines the LUI Capture Layer: the persistent, addressable record of explicit language–user inputs (LUIs) and related events.

This layer is the non-optional foundation that enables the Continuity Atlas (substrate), the CAP (Continuity Access Protocol), and IAM services.

Chunking and semantic assistance are optional overlays and are not required for continuity correctness.

---

## Purpose

The LUI Capture Layer exists to:

- preserve explicit language acts as durable events,
- assign stable identifiers suitable for longitudinal reference,
- maintain ordering without semantic interpretation,
- retain provenance so sources can be audited and re-entered,
- provide structural assurance for trust.

This layer does not infer meaning, intent, or goals.

---

## LUI Event Record (Minimum Fields)

Each captured event SHOULD include:

- `lui_id` — stable identifier (UUID or deterministic hash)
- `t` — timestamp
- `seq` — monotonic sequence within a conversation/source stream
- `actor` — `user | assistant | tool | system`
- `text` — exact raw text (opaque payload)
- `source` — provenance object (below)
- `integrity` — optional hash for tamper evidence

The record may include links to attachments or non-text artifacts, but remains an event of record.

---

## Provenance (Source Identification)

Provenance identifies the origin of the event without interpreting content.

Recommended provenance fields:

- `source.system` — e.g., `chatgpt`
- `source.conversation_id` — upstream conversation identifier
- `source.message_id` — upstream message identifier
- `source.export_id` — file hash or export identifier
- `source.capture_method` — `import | share | copy`
- `source.role_original` — if relevant

This is not semantics. It is structural traceability.

---

## Relationship to CAP (Continuity Access Protocol)

CAP defines the **interface and protocol** by which continuity structures in the Atlas are accessed, navigated, and referenced.

CAP operates over LUI identifiers and Atlas metadata. It does not store data and does not infer meaning.

Through CAP, permitted operations may include:

- referencing LUI identifiers or ranges,
- navigating temporal adjacency,
- resolving return points,
- traversing regions or charts,
- following stitching links.

CAP governs access.  
The Atlas stores continuity.  
Meaning emerges only through human re-entry.

---

## Relationship to IAM

IAM is the user-facing interface and thinking support layer.

IAM services depend on the LUI Capture Layer, the Atlas, and CAP to enable:

- re-entry into prior activity without reconstruction,
- user-authored return points and regions,
- longitudinal navigation across sessions.

IAM does not expose the substrate or protocol as primary features; they exist to provide structural assurance that the space can be trusted.

---

## Optional Overlays (Non-Authoritative)

Chunking, topic boundaries, summaries, and other semantic constructs may be computed as overlays.

Overlays MUST be:

- separable from the LUI Capture Layer and Atlas,
- versioned and replaceable,
- non-authoritative for continuity correctness.

Continuity remains valid even if overlays are removed.

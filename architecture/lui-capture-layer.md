# LUI Capture Layer (Source-of-Record)

This document defines the LUI Capture Layer: the persistent, addressable record of explicit human-generated language inputs (LUIs) and related events.

This layer is the non-optional foundation that enables CAP (Continuity Atlas / Continuity Assurance Plane) and IAM services.

Chunking and semantic assistance are optional overlays and are not required for continuity correctness.

---

## Purpose

The LUI Capture Layer exists to:

- preserve explicit human language acts as durable events,
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

## Relationship to CAP

CAP operates over LUI event identifiers.

CAP constructs continuity structures such as:

- return points (pointers to `lui_id` or ranges),
- regions/charts (sets or intervals of LUIs),
- adjacency links (prev/next in time),
- stitching edges (links between regions).

CAP does not require meaning to preserve continuity. It requires stable, addressable events.

---

## Relationship to IAM

IAM is the user-facing interface and thinking support layer.

IAM services depend on the LUI Capture Layer and CAP to enable:

- re-entry into prior activity without reconstruction,
- user-authored return points and regions,
- longitudinal navigation across sessions.

IAM does not expose the substrate as a primary feature; the substrate exists to provide structural assurance that the space can be trusted.

---

## Optional Overlays (Non-Authoritative)

Chunking, topic boundaries, summaries, and other semantic constructs may be computed as overlays.

Overlays MUST be:

- separable from the LUI Capture Layer,
- versioned and replaceable,
- non-authoritative for continuity correctness.

Continuity remains valid even if overlays are removed.

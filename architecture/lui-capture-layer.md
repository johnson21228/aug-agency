# LUI Capture Layer (Source-of-Record)

This document defines the LUI Capture Layer: the persistent, addressable record of explicit language–user inputs (LUIs) and related events.

This layer is the non-optional foundation that enables the continuity substrate, CAP, and IAM services.

Chunking and semantic assistance are optional overlays and are not required for continuity correctness.

## Purpose

The LUI Capture Layer exists to:

- preserve explicit language acts as durable events,
- assign stable capture identifiers suitable for longitudinal reference,
- maintain ordering without semantic interpretation,
- retain provenance so sources can be audited and re-entered,
- provide structural assurance for trust,
- capture reflective, human-generated artifacts produced during IAM use as first-class language events.

This layer does not infer meaning, intent, or goals.

## LUI Event Record (Minimum Fields)

Each captured event SHOULD include:

- `capture_id` (or `lui_id`) — stable identifier in the capture store
- `t` — timestamp (if available)
- `seq` — monotonic sequence within a source stream (if available)
- `actor` — `human | assistant | tool | system`
- `payload` — exact raw payload (opaque)
- `source` — provenance object
- `integrity` — optional hash for tamper evidence

## Store Realization and ID Ownership

The Capture Layer is the source-of-record for raw LUIs/events and is implemented as `iam.db` (capture store) governed by `migrations/0001_capture_contract.sql`.

- Capture identifiers may be source-scoped at capture time (adapter keys).
- The Provenance layer assigns stable numeric identifiers (e.g., `event_id`) derived solely from capture provenance.
- Continuon identifiers, if present, are build-scoped projections and must not be treated as durable references.
- Substrate structures reference stable IDs; source language is rehydrated through provenance mapping.

## Provenance (Source Identification)

Provenance identifies the origin of the event without interpreting content.

Recommended provenance fields:

- `source.system` (e.g., `chatgpt_export`)
- `source.stream_id` or `source.conversation_id`
- `source.event_key` (e.g., message/node id)
- `source.export_id` (hash or export identifier)
- `source.capture_method` (`import | share | copy`)
- `source.role_original` (if relevant)

This is not semantics. It is structural traceability.

## Optional Overlays (Non-Authoritative)

Chunking, summaries, and semantic assistance may be computed as overlays.

Overlays MUST be:

- separable from the Capture Layer and substrate,
- versioned and replaceable,
- non-authoritative for continuity correctness.

Continuity remains valid even if overlays are removed.

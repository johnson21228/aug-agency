# CMP Contract — LUI Packet
## Canonical Capture Event Format

This contract defines the canonical format for a single LUI packet.
A LUI packet is the unit of ingestion into the capture store (`iam.db`).

This contract is authoritative over:
- ingestion scripts,
- IAMApp ingest adapters,
- optional server ingest endpoints.

---

## LUI Packet (Required Fields)

A LUI packet MUST contain:

- `event_id` (string)  
  Stable identifier for the event. Must be stable across retries and replays.

- `created_at` (ISO8601 string)  
  Timestamp of capture. Device time is acceptable.

- `body` (string)  
  Raw text content. Stored verbatim.

- `source` (string)  
  Adapter/source label (e.g., `chatgpt_export`, `share_sheet`, `manual_entry`).

- `actor` (string)  
  Must identify the single human locus. Default: `user`.

---

## LUI Packet (Optional Fields)

- `supersedes_event_id` (string)  
  If this event is a correction/override of a prior event, reference it here.
  The superseded event is not deleted.

- `attachments` (array)  
  References to attachments. Attachments are referenced, not embedded.

- `tags` (array of strings)  
  User-supplied only.

- `context` (object)  
  Adapter-provided context fields (e.g., conversation_id, message_id, file name).
  Context must not be interpreted as authoritative continuity.

---

## Ingestion Rules (Stage 0)

### Append-Only
Ingestion MUST be append-only.
No event may be modified or deleted in place.

### Idempotency
Ingestion MUST be idempotent.
Re-ingesting the same `event_id` MUST NOT create duplicates.

### No Semantics Required
Ingestion MUST NOT require:
- embedding,
- summarization,
- clustering,
- inference.

### Provenance Preservation
All adapter-provided context fields should be preserved verbatim as provenance.
Interpretation is deferred.

---

## `iam.db` Capture Store Minimum Schema

The capture store MUST be able to represent:

- `event_id` (primary key)
- `created_at`
- `body`
- `source`
- `actor`
- `supersedes_event_id` (nullable)
- `context_json` (nullable)
- `attachments_json` (nullable)
- `tags_json` (nullable)

Exact table names are implementation details.

---

## Notes on Personal Scope

This contract is scoped to a single human’s continuity.
Multi-user aggregation is out of scope for CMP.

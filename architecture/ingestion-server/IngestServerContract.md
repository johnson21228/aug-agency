# IngestServerContract.md
Version: 0.1  
Status: Canonical contract for LUI ingest over REST (capture authority).

---

## 0. Purpose

This contract defines a REST ingest server that:

1. Accepts **LUIs (Language-Use Instances)** as the only admissible capture input  
2. Persists them **append-only** into `iam.db` (capture authority)  
3. Supports a **Photos-like capture model** (timeline feed, metadata, collections, idempotent import) for **language-use data**  
4. Emits deterministic sequencing for downstream processing (ProvDB → SubDB → CAP)

This contract is a **boundary**: it specifies what the ingest server must do and must not do.

---

## 1. Definitions

### 1.1 LUI (Language-Use Instance)

An LUI is the atomic unit of IAM ingestion: a single captured event with a capture time, source identity, and payload.  
The payload is **language-use data** (e.g., text, transcript, structured language events).

LUIs are append-only and immutable after commit.  
All derived structures are built from ordered LUIs.

---

### 1.2 Capture Record vs Derived Meaning

The ingest server stores capture records (LUIs) and minimal metadata required for integrity and retrieval.

Any semantic enrichment, embeddings, clustering, topics, judgments, or interpretations are **derived artifacts** and must not be treated as capture truth.

---

### 1.3 Ordering

The ingest server assigns a monotonic sequence number (`seq`) to committed LUIs.  
This sequence defines the **canonical processing order** for all downstream builders.

Client-supplied narrative order must not override `seq`.

---

### 1.4 “Photos-like” Capture Model (Non-Media-Specific)

“Photos-like” refers to the **operating model**, not the payload type:

- capture-first events
- timeline ordering
- stable identifiers
- metadata (title, notes, tags)
- collections / albums (as metadata only)
- favorites (as metadata only)
- idempotent import and retry-safe delivery

The payload remains **language-use data**.  
Attachments (if present) are optional and do not define the model.

---

## 2. Invariants (Non-Negotiable)

**I1 — LUI-only input**  
No data enters IAM except as an LUI (or batch of LUIs).

**I2 — Append-only**  
The ingest server never rewrites, merges, or deletes committed LUIs.

**I3 — Immutability after commit**  
After commit, an LUI’s envelope (and any optional attachment references) is immutable.

**I4 — Idempotency**  
Replays or retries must not create duplicate LUIs or duplicate attachments.

**I5 — Deterministic ordering**  
Committed LUIs receive a stable, monotonic `seq`.

**I6 — No reconstruction claims**  
The ingest API must not expose endpoints that imply reconstruction of past cognition from summaries or snapshots.

**I7 — Privacy mode respected**  
If payload is declared ciphertext, the server stores opaque bytes and must not inspect content.

---

## 3. Authentication & Transport

- TLS is required for all requests.
- Authentication is implementation-specific (e.g., bearer token, mTLS), but must provide:
  - device/app identity for `source.*`
  - authorization for write/read operations
- The server must tolerate reasonable clock skew in `captured_at`.

---

## 4. Data Model (Logical)

### 4.1 LUI Envelope (JSON)

All endpoints that accept LUIs use this envelope.

```json
{
  "client_lui_id": "string (required, unique per device)",
  "captured_at": "RFC3339 timestamp (required)",
  "received_at": "RFC3339 timestamp (server-set, response only)",
  "source": {
    "client": "string (required; e.g. 'ios')",
    "device_id": "string (required)",
    "app_build": "string (optional)",
    "user_id": "string (optional)"
  },
  "kind": "string (required; e.g. 'text','note','message','transcript','event')",
  "title": "string (optional)",
  "notes": "string (optional)",
  "tags": ["string (optional)"],
  "collection_ids": ["string (optional)"],
  "favorite": "boolean (optional)",
  "payload": {
    "text": "string (optional)",
    "transcript": "string (optional)",
    "json": { "any": "optional structured language event payload" }
  },
  "attachments": [
    {
      "role": "string (required; e.g. 'raw','aux')",
      "mime": "string (required)",
      "byte_size": 123,
      "sha256": "string (optional but recommended)"
    }
  ],
  "privacy": {
    "payload_mode": "string (required: 'plaintext' | 'ciphertext' | 'hybrid')",
    "encryption": {
      "scheme": "string (optional)",
      "key_id": "string (optional)"
    },
    "redactions": ["string (optional)"]
  }
}

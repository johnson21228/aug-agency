# ChatGPT Export → LUI Mapping

This document defines a deterministic mapping from ChatGPT export artifacts
to canonical LUI envelopes suitable for spooler intake.

## Source material

Typical export includes conversation/message structures with:
- conversation ID
- message ID
- author role ("user", "assistant", "system", "tool")
- message text parts
- create_time (epoch seconds) or ISO timestamps (if present)

## Canonical LUI envelope fields

Each exported message maps to one LUI envelope:

- client_lui_id (REQUIRED)
  Deterministic:
  `chatgpt:<conversation_id>:<message_id>`

- captured_at (REQUIRED)
  From export create_time; RFC3339 in UTC.

- source (REQUIRED)
  - client: "chatgpt"
  - conversation_id: <conversation_id>
  - message_id: <message_id>
  - role: <author role>
  - transport: "chatgpt_export"

- kind (REQUIRED)
  "chatgpt.turn"

- payload (REQUIRED)
  - text: concatenated message text
  - role: author role
  - conversation_id
  - message_id

- privacy (REQUIRED)
  - payload_mode: "plaintext"
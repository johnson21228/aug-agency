# LI/sources/openai_actions/CapturePolicy.md

Status: Canonical
Version: 0.1

## Goal

Enable the ChatGPT surface to function as a **volitional LUI source** whose outputs
are durably enqueued to the spooler boundary (`POST /v1/spool`), without granting
ChatGPT capture authority or semantic authority.

This policy exists to serve the goals expressed in the writings:
- continuity is preserved by **re-entry into one’s own language-use**
- capture must not collapse the path into summary or coherence-at-capture
- the human remains the agent that decides what crosses the boundary

## Capture Triggers

Capture MUST be user-volitional by default.

### Trigger grammar (recommended)

- `iam:` capture the remainder of the user message as the LUI payload text (verbatim)
- `iam+ctx:` capture the remainder of the user message verbatim AND include minimal local context

No other implicit triggers are permitted under this policy.

## Payload Rules

### Verbatim capture (hard invariant)

For capture events:
- the text after the prefix MUST be preserved verbatim as `payload.text`
- no paraphrase, summary, cleanup, or rewriting is allowed at capture time

### Context capture (only for iam+ctx:)

For `iam+ctx:` events only, include:
- `payload.context.previous_user_message` (immediately preceding user message, if available)
- `payload.context.assistant_last_reply` (immediately preceding assistant reply, if available)

Do NOT include full transcripts by default.

## Envelope Rules

All captured items MUST be emitted as an LUI envelope and sent to the spooler via REST.
The Action client MUST supply a replay-safe idempotency key:

- `client_lui_id` REQUIRED

`source` MUST identify the capture surface as ChatGPT Actions, e.g.:

- `source.client = "chatgpt"`
- `source.agent = "chatgpt-actions"`

`kind` SHOULD be stable and simple, e.g. `"message"` or `"note"`.

## Non-goals

- Automatic capture of unmarked conversation
- Semantic interpretation, scoring, or truth-claims at capture time
- Summarization at capture time
- Writing to iam.db (out of scope for sources)
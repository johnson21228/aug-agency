## I6. Conversational Surface, Continuity First

The primary interaction surface is conversational.
Conversation is a view over continuity, not the continuity itself.
Conversation history must not become the authoritative store for continuity.

## I7. Local Data Residency by Default

Substrate and derived stores reside locally by default (on-device).
Sharing/export is explicit, user-initiated, and produces copies.
No background upload is required for correctness.

## I8. Pipeline Parity with Repo Scripts

Processing stages implemented in iOS must match the patterns and stage boundaries established by the repo’s desktop scripts.
If iOS deviates, the deviation must be written as a local decision record in `Language/Decisions/`.

## I9. Multi-Source LUI Capture

The ingest layer must accept multiple LUI sources (text entry, share sheet, clipboard, files, transcripts, etc.).
Adapters must normalize into a common LUI event format without semantic interpretation.

## I10. One-Shot External Inference is Optional

External LLM calls, when used, must be one-shot and credential-gated.
No external inference is required for:
- capture,
- identity,
- ordering,
- re-entry.

External inference may only enrich derived views.

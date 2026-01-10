## Sources (Non-Exhaustive)

The ingest system must be prepared to accept LUIs from:
- direct text entry
- iOS share sheet (text, URLs, files)
- clipboard capture (user-triggered)
- imported transcripts (structured text)
- app-internal captures (conversation turns, notes)

All sources normalize into the same LUI event shape.

## Adapter Rule

Adapters transform input format into LUI events.
Adapters must not summarize, embed, or interpret content.

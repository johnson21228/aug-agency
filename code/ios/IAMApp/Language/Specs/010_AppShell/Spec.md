# Spec 010 — App Shell

## Goal
Provide an app shell with a ChatGPT-like conversational layout as a view over continuity.

## Non-Goals
- Do not implement semantic enrichment in this spec.
- Do not require external inference.

## Requirements
- Conversation screen exists and is primary.
- Conversation is bound to a selected continuity position (current thread / current path position).
- UI provides a way to choose or change the continuity position used for the next message (re-entry control).

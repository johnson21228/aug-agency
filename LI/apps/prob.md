# LI/apps/ios/probe.md

## Purpose

Defines how the iOS app produces **readable language** from an anchor when SubDB
does not store plaintext.

Probing generates semantics at runtime. It does not recover past text.

## Invariants

### P1 — Probe is runtime-only
Probe outputs MUST NOT be written into SubDB as authoritative meaning.

If probe outputs are captured, they MUST enter SubDB only via explicit attention
boundary capture (paste/capture action), producing new records.

### P2 — Probe is anchored
Probe requests MUST be conditioned on:
- current anchor vector (or composite anchor)
- optional direction vector (momentum)
- optional neighborhood context (top N nearest SubDB vectors)

### P3 — Probe outputs are options
Probe outputs MUST be framed as alternative continuations or adjacent framings,
not as summaries of truth.

## Probe output contract

A probe SHOULD return a list of candidate texts:
- `continue_forward`
- `alternative_framing_1`
- `alternative_framing_2`
- `divergent_option`

Each item SHOULD include a short “reason” string that is structural
(e.g., “forward momentum”, “near revisit cluster”), not semantic.

## Implementation freedom

Probing MAY be implemented using:
- on-device generation (if available), or
- remote model API calls

Embedding computation and SubDB persistence remain local.
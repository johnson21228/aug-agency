# ChatGPT-derived LUI Invariants

## Determinism
For a given export file and mapping policy:
- `client_lui_id` MUST be stable.
- Canonical JSON serialization MUST be stable (field ordering, normalized times).

## Ordering
Adapters SHOULD emit LUIs in a stable order:
- by captured_at ascending, then by message_id as a tiebreaker if needed.

## Replay safety
Replaying the same export against spooler MUST be safe:
- identical `client_lui_id` with identical envelope => no duplicate enqueue
- identical `client_lui_id` with differing envelope => conflict

## Losslessness (text)
The message text used for payload MUST preserve original content (concatenate
parts without semantic alteration).
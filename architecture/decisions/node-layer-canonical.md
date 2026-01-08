# Decision: Canonical Node Layer for IAM

## Status
GOVERNING (code must conform)

## Context
IAM capture is append-only and authoritative (`iam.db`).
Derived structures (ProvDB, SubDB) are rebuildable and non-authoritative.

Continuity access requires a canonical node granularity for:
- SubDB geometry (ordering, adjacency, neighborhoods)
- CAP re-entry packets (windowing over nodes)

## Decision
IAM SHALL define a canonical node layer ("canonical layer") used by default for:
- ProvDB node materialization
- SubDB node geometry
- CAP default re-entry

The canonical layer is identified by a stable `layer_key`.

## Current Canonical Layer
`layer_key = prp_v1_turn_pairing`

## Requirements for Canonical Layer
The canonical layer MUST:
- be deterministic from atomic events
- be policy-versioned and explicitly named (`layer_key`)
- be rebuildable and non-authoritative
- be lossless via ordered membership pointers to event identities
- not require semantics for correctness

## Non-Canonical Layers
Other layers MAY exist in parallel (e.g., alternative chunking policies),
but they are non-canonical and MUST NOT be required for continuity correctness.

## Change Control
Changing the canonical layer MUST be done by:
1) introducing a new `layer_key`
2) documenting the policy in a new decision record
3) rebuilding derived stores
Canonical changes do not modify capture.

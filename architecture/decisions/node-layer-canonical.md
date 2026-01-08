# Decision: Canonical Node Layer for IAM

## Status
GOVERNING (code must conform)

## Context
IAM capture is append-only and authoritative (`iam.db`).
Derived structures (ProvDB, SubDB) are rebuildable and non-authoritative.

Continuity access requires a canonical node granularity for:
- SubDB geometry (ordering, adjacency, neighborhoods)
- CAP re-entry packets (windowing over nodes)

Multiple node granularities may coexist as parallel layers (e.g., PRP pairing, alternative chunking).
However, IAM must choose one canonical layer as the default substrate for re-entry.

## Decision
IAM SHALL define a canonical node layer ("canonical layer") used by default for:
- ProvDB node materialization (nodes + membership)
- SubDB node geometry (structural continuity)
- CAP default re-entry behavior

The canonical layer is identified by a stable `layer_key`.

## Current Canonical Layer
`layer_key = prp_v1_turn_pairing`

## Requirements for Canonical Layer
The canonical layer MUST:
- be deterministic from atomic events
- be policy-versioned and explicitly named (`layer_key`)
- be rebuildable and non-authoritative (derived from capture)
- be lossless via ordered membership pointers to event identities
- not require semantics for correctness (no embeddings, similarity, meaning-joins)

## Non-Canonical Layers
Other layers MAY exist in parallel (e.g., alternative chunking policies),
but they are non-canonical and MUST NOT be required for continuity correctness.

Non-canonical layers remain permissible as:
- alternate navigation views
- alternate CAP entry points
- experimental or personal chunking regimes

## Change Control
Changing the canonical layer MUST be done by:
1) introducing a new `layer_key` (policy identity)
2) recording the policy contract for that layer in repo language
3) rebuilding derived stores (ProvDB/SubDB)

Canonical changes do not modify capture.

# Local Store Contract

## Purpose
Provide local persistence for substrate and derived stores within the iOS app boundary.

## Stores
- `iam.db` (or equivalent local substrate store)
- downstream stores (ProvDB/SubDB or local equivalents as defined by the repo pipeline)

## Guarantees
- local-first correctness
- append-only substrate capture
- stable event identity
- no semantic processing required for correctness

## Sharing / Export
Exports produce explicit, user-initiated copies.
Imports do not overwrite substrate history; they append new events or create separate namespaces.

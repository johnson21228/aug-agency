# Chewing for the Current Chart

## Purpose

Chewing exists to make the user **anchored in a chart that is useful now**.

The chart is the user-facing contract:
- semantic-first
- anchored in raw language
- always resolvable to raw events (LUIs)
- geometry is permitted only as an organizing aid

Chewing improves views; it does not change truth.

---

## Definitions

### Raw Authority (iam.db)
- `iam.db` is the authoritative append-only capture authority.
- Raw events live in `capture_events`.
- Raw events are addressed by stable identifiers (e.g., `seq`, `event_id`, `client_lui_id`).

### Derived Store (SubDB)
- `subdb.sqlite` contains derived, discardable projections.
- SubDB may be deleted at any time; the system must rebuild derived projections from raw authority.

### Anchor
- An anchor is a specific raw event (by `seq` and/or `event_id`).
- "Current anchor" is the anchor corresponding to the user's current position.

### Chart
- A chart is a local view around an anchor.
- A chart specifies a semantic window (typically a seq range):
  - `start_seq … end_seq`
- A chart may include local coordinates, but coordinates never replace raw language.

---

## Hard Invariants

### I1 — CAP Authority
All semantic grounding ultimately resolves through CAP to raw events in `iam.db`.

Derived data may accelerate lookup, but must not become required for:
- determining the current anchor
- assembling the chart window
- revealing raw text

### I2 — Semantic-First Charts
A chart is invalid unless it can present:
- the anchor’s raw text (or a direct path to it), AND
- the raw text (or direct path) for any event in its semantic window.

### I3 — Derived-Only Enhancements
SubDB may contain:
- event indices (previews, roles, kinds, timestamps)
- window membership and chart caches
- local coordinates and ordering metadata
- fit/alignment metadata

SubDB must never contain semantics that replace raw text.

### I4 — Discardability Test
Deleting derived storage must:
- reduce performance and convenience
- but not lose experience
- and not prevent reconstruction of charts from raw authority

### I5 — Visibility of Progress
When chewing runs, the system must be able to answer:
- which chart it is improving (anchor + window)
- what is missing for that chart to be “ready”
- what it just improved (coverage delta)

---

## Chart Readiness (Operational)

Given a current anchor and chart window `[start_seq…end_seq]`, define:

### R0 — Unindexed
- Chart can be assembled only via CAP calls (slow).
- Derived index coverage is low or unknown.

### R1 — Indexed
- `event_index` coverage for the window is ~100%.
- The chart list renders from SubDB, with CAP for full raw text on demand.

### R2 — Structured (Optional)
- Local ordering aids exist (gaps/density cues, local coords).
- Still semantic-first; raw reveal path remains primary.

### R3 — Fit (Optional)
- Chart alignment to neighboring charts is bounded by a residual metric.
- Fit changes coordinates only; never semantics or membership.

---

## Chewing Order (Must)

Chewing MUST prioritize the **current chart**.

### Step 1 — Identify Current Anchor
- Determine `anchor_seq` (and/or `anchor_event_id`).
- Establish chart window parameters: `window_before`, `window_after`.

### Step 2 — Define the Current Chart Window
- `start_seq = max(1, anchor_seq - window_before)`
- `end_seq = anchor_seq + window_after`

### Step 3 — Close Index Gaps in the Window (Highest Priority)
For each seq in `[start_seq…end_seq]`, ensure SubDB has a row in:

- `event_index(seq PRIMARY KEY, event_id, captured_at_ms, role, kind, is_empty, preview)`

Chewing MUST compute and store:
- stable identifiers (seq, event_id)
- timestamps
- role/kind (derived from envelope)
- preview (derived, bounded)
- empty flags

### Step 4 — Optional: Improve Local Structure
After Step 3 is complete, chewing MAY add:
- gap/density markers
- local coordinate aids
- lightweight ordering metadata

### Step 5 — Optional: Fit to Neighbors
After semantic window readiness is achieved, chewing MAY:
- compute overlap alignment transforms
- measure residual
- store fit metadata

Fit may adjust coordinates only.

---

## Required Interfaces (Code Contracts)

### CAP
- `listEvents(beforeSeq, limit)` for paging
- `getEvent(eventID)` for raw envelope resolution

### SubDB
Minimum for the "Indexed" phase:

- `event_index` table (derived)
- `chew_state` table (derived)
  - must record progress, last run, and (optionally) the chart window being served

---

## Acceptance Tests

### A1 — Delete Derived, Still Works
1. Delete `subdb.sqlite` and caches.
2. Relaunch.
3. Current chart must still render (possibly slower) using CAP only.
4. Raw text must remain revealable (tap → raw).

### A2 — Chart Remains Semantic-First
If the chart list uses previews, it must still support:
- tap-to-raw for every event
- copying/exporting a chart pack grounded in raw IDs

### A3 — Chewing Improves the Current Chart
During chewing, for the current chart window:
- indexed coverage should move monotonically toward 100%
- the system should report "what's missing" (counts / seq ranges)

---

## Notes on “Meaning Fun”
Charts may be “meaning fun” (tempo/gap cues, density, ordering), but:
- cues must be honest derived signals (timestamps, adjacency, local coords)
- cues must never replace language
- cues must never assert interpretation

The user’s relation to the chart must remain grounded in the raw language.
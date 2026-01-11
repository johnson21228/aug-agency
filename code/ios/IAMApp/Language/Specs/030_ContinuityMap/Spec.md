# Spec 030 — Continuity Map

## Goal
Expose continuity as a usable resource through a map that supports re-entry and perspective mobility.

## Requirements
- Along-path view: show current position and allow re-entry.
- Local neighborhood view: show nearby revisits/branches without requiring semantic interpretation.
- Global view: show long-range shape (folded structure) while preserving re-entry to specific positions.
- All perspective changes are reversible without reconstruction.

## Meaning Layer
Semantic meaning may be overlaid using client-defined coordinates and metric.
Meaning is optional and must not be required for correctness.

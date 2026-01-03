# Primitives

This document defines the minimal primitives required to support continuity.

These primitives are structural, not semantic.

## Primitive: Trace

A trace is a non-semantic structural record produced by activity.

Properties:
- Time-indexed
- Non-interpreted
- Immutable once recorded

## Primitive: Region

A region is a bounded area of continuity.

Regions:
- Group traces
- Establish locality
- Enable focused re-entry

## Primitive: Return Point

A return point marks a location suitable for re-entry.

Return points:
- Do not summarize
- Do not interpret
- Provide orientation only

## Primitive: Boundary

Boundaries separate regions and prevent uncontrolled collapse of context.

## Primitive: Manifold

A manifold is the structured space formed by regions, traces, and return points.

It enables continuity without meaning.

## Relationship to IAM

IAM exposes these primitives through a human-facing interface.
Humans supply meaning through engagement, not storage.

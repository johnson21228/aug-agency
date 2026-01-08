# Continuity Strata

## Why strata are necessary

Most computational systems collapse continuity, identity, and meaning into a single representational layer. Time becomes metadata, memory becomes storage, and meaning becomes an inferred property of data.

IAM rejects this collapse.

Preserving human continuity of thought over time requires introducing constraints in a specific order, where each constraint depends on the previous one holding. These are not implementation stages, maturity levels, or feature tiers. They are conceptual strata.

Each stratum answers:

What must already be true for higher-order continuity to remain intelligible?

If a lower stratum fails, higher strata do not merely degrade; they become incoherent. What follows is a dependency ladder, not a pipeline.

## Stratum 0: Numeric Continuity

What exists before language, meaning, or interpretation?

At the base is numeric continuity: ordering, adjacency, and identity expressed without semantics. This stratum establishes that there is a before and after, a next and a previous, without asserting what any element means.

If continuity is encoded semantically at this level, rebuildability becomes impossible. Any change in interpretation would rewrite time itself.

## Stratum 1: Capture and Provenance

What are the irreducible facts of language use?

At this stratum, language-use events (LUIs) are captured as append-only facts. Each event records that something was said, written, or produced, by a source, at a moment in time.

This is the first point at which digital language use acquires a temporal character. Language is not treated as timeless content, but as something that occurred. This preserves the conditions of intelligibility over time (being-in-time as structural preservation, not metaphysics).

If capture is lossy, mutable, or overwritten, higher continuity collapses into reconstruction and inference.

## Stratum 2: Stable Identity and Referential Integrity

What can be pointed to over time?

Continuity requires return — not to similar content, but to the same event. This stratum establishes stable identity grounded solely in capture provenance.

Identity here is not semantic. It does not depend on embeddings, clustering, or interpretation. Without this stratum, reflexive artifacts (return points, links, annotations) cannot survive rebuild.

## Stratum 3: Continuity Geometry

How can time be navigated without interpretation?

This stratum introduces structure over events without introducing meaning: adjacency, neighborhoods, return paths, and regions. “Return” becomes operational without semantic authority.

If semantic interpretation enters here, navigation turns into inference and rebuildability is lost.

## Stratum 4: Provenance Overlays

How does language reattach to continuity?

Here, language spans and optional semantic coordinates are associated with stable identifiers. Meaning appears only as overlay: versioned, replaceable, non-authoritative.

If overlays define identity, semantic drift corrupts continuity.

## Stratum 5: Slices and Task-Oriented Views

How can continuity be made usable without collapsing it?

Slices are derived selections assembled for tasks (prompting, review, reflection). They trade completeness for usability while retaining stable references back to capture and continuity geometry.

If slices become authoritative, the system devolves into a workspace tool rather than a continuity-preserving system.

## Stratum 6: Human-Oriented Orchestration

How does a human live inside this system without losing themselves?

IAM coordinates continuity geometry (SubDB) and provenance overlays (ProvDB) to support re-entry and reflection. It introduces no new truth. It arranges what already exists so humans can resume thought, not merely retrieve information.

Continuity gains meaning only through human judgment expressed over time and captured again as language-use events.

## Relationship to other documents

- `architecture/overview.md` defines what kind of system IAM is.
- `architecture/invariants.md` lists non-negotiable constraints.
- `architecture/ingestion-pipeline.md` describes data movement through time.
- This document explains why constraints must appear in this order.

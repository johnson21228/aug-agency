Architecture Overview

What kind of system is this

This document establishes the identity of the system before any implementation details appear.

IAM is presented not as a tool for producing answers, nor as an agent that acts autonomously, but as a system designed to preserve and extend human continuity of thought over time. Its core claim is that human judgment, reflection, and meaning do not arise from isolated inference, but from sustained engagement with one’s own prior reasoning.

IAM is explicitly reflexive: outputs created through use of the system—annotations, links, decisions, moments of recognition—are allowed to re-enter the system as inputs. However, this reflexivity is tightly constrained. The system does not learn, adapt, or modify its operational rules as a result of those inputs. Reflexivity is permitted only at the level of memory and structure, never at the level of control logic.

This distinction matters. It positions IAM clearly away from agentic or self-modifying AI systems. IAM does not attempt to replace human judgment; it preserves it by making reflective acts durable without turning them into rules. Rebuildability is treated as a feature, not a limitation: derived structures may change, but captured history does not. That principle underwrites the entire architecture.

The IAM architecture exists to operationalize the claims made in the writings.
It is not an independent source of truth.

The architecture translates normative goals—preserving human reasoning continuity, judgment, and agency over time—into concrete system invariants and layers.

⸻

Architectural stance

IAM is oriented toward continuity rather than optimization, and therefore resists reducing lived thought to static embeddings or fixed representations.
	•	Continuity is treated as a first-class invariant.
	•	Human judgment is preserved by maintaining temporal coherence of meaning.

Optimization, compression, and summarization may appear in derived layers, but they are never allowed to define identity or truth.

⸻

What IAM is not

IAM is not an agent, a retrieval system, or a memory plugin layered onto a language model. It does not act autonomously, pursue goals, optimize rewards, or modify its own behavior over time. Unlike RAG systems, IAM does not treat memory as a searchable corpus to be flattened into embeddings for answer production, nor does it treat retrieval as a substitute for continuity. Unlike note-taking or memory tools, IAM does not externalize thought as static artifacts detached from temporal context. IAM preserves continuity by capturing language use and reflective acts as they occur, allowing meaning to re-emerge through re-entry rather than being inferred, summarized, or optimized in advance.

⸻

Reflexive but Non-Self-Modifying System

IAM permits artifacts produced through human interaction within the system—annotations, return points, links, decisions (“gold”)—to re-enter the system as first-class inputs.

These artifacts are captured append-only as data and never as operational rules.
The system does not learn, retrain, or modify its governing logic as a result of such inputs.

All derived structures may be rebuilt or replaced without invalidating captured history.

⸻

Relationship to writings

All architectural decisions are downstream of the writings found in writing/.

The writings define:
	•	What problems matter
	•	What tradeoffs are acceptable
	•	What outcomes are explicitly rejected

The architecture answers only:
	•	How those claims can be made operational
	•	What invariants must hold for the system to remain aligned over time

⸻

Layered structure

The architecture is organized into layers, beginning with a numeric continuity substrate and extending through ingestion, temporal binding, and higher-order reasoning support.

Each layer:
	•	Introduces constraints, not features
	•	Preserves append-only semantics
	•	Avoids rewriting, collapsing, or flattening prior human expression

Later layers may add structure or utility, but never authority over earlier ones.

⸻

Non-goals

This architecture is not intended to:
	•	Maximize predictive accuracy
	•	Replace human judgment
	•	Serve as a general-purpose agent framework
	•	Optimize outcomes at the expense of continuity

Any embodiment or code suggesting otherwise is misaligned.

⸻

Status

This document defines what IAM is, before describing how it is built.
All other architectural documents elaborate consequences of the commitments made here.

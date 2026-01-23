# interface_constraints.md
## Discovered Interface Constraints (Exploratory)

---

## Status of this document

This document records **interface-related constraints as they are being discovered,
articulated, and tested against the existing Language Infrastructure (LI).**

It is intentionally **unprefixed**.

The absence of a numeric prefix signals that:
- these constraints are *derivative*, but
- their precise layer designation has not yet been canonized
- semantic coherence takes precedence over structural labeling

If these constraints remain stable under re-reading and do not leak downward into
substrate, language, or ontology layers, this document may later be promoted to a
numbered derivation file.

---

## Purpose

The purpose of this document is **not** to define a user interface,
nor to prescribe UI elements, layouts, or product behavior.

Instead, it captures **necessary constraints** on any interface that
claims to faithfully expose and interact with the IAM continuity substrate.

These constraints follow from:
- time-indexed continuity
- append-only registration
- preservation of human agency
- explicit treatment of external inference as service invocation

They are recorded here as *discoveries*, not assumptions.

---

## Constraint 1: The interface is derivative, not constitutive

The IAM interface does not define cognition, memory, or meaning.

Those properties already exist in the substrate as:
- time-sequenced registrations
- irreversible traces
- human-originated Language-Use Inputs (LUIs)

**Constraint**
- The interface must remain thin.
- It must not become an interpretive authority.
- It must not narrate or explain continuity on behalf of the human.

The interface exposes structure; it does not replace judgment.

---

## Constraint 2: Time must remain legible

Time is a structural dimension of IAM, not metadata.

Every interaction:
- occurs at a specific moment
- is registered irreversibly
- constrains future interpretation

**Constraint**
- The interface must never obscure temporal ordering.
- Past interactions must not silently collapse into “current context.”
- Hidden rewrites, overwrites, or auto-summarizations violate continuity.

A user must always be able to tell:
- what happened
- when it happened
- and what followed

---

## Constraint 3: Typing is a first-class Language-Use Input

Time-sequenced typing is a primary mechanism by which humans externalize thought.

Typing:
- unfolds over time
- reflects attention, hesitation, revision, and intent
- naturally produces continuity traces

**Constraint**
- The interface must support uninterrupted typing as a primary modality.
- Typed input is not a “chat message”; it is a continuity event.
- Other modalities (voice, capture, automation) are secondary and derivative.

Typing-first is a continuity capture strategy, not a UX preference.

---

## Captured Insight: Typing-Centered Interfaces as Cognitive Service Boundaries

### Observation

Typing-centered systems commonly described as “chat interfaces” succeed not because
they simulate conversation, but because they establish a **clear and legible boundary
between the human and external inference services**.

Their effectiveness arises from three structural properties:

1. Typing is the dominant human action
2. External models are treated as callable services
3. The interface remains thin and immediate

This insight is structural, not aesthetic.

---

### Typing as a boundary of agency

Typing is not merely an input modality.

It is:
- time-sequenced
- effortful
- intentional
- owned by the human

Typing establishes a cognitively legible boundary:
- what is typed is human-originated
- what is returned is externally generated

This boundary is naturally trusted because it mirrors how humans already distinguish
their own thinking from reference material, tools, or consultation.

The effectiveness of typing-centered systems comes from respecting this boundary,
not from simulating dialogue.

---

### External inference as service, not interlocutor

Typing-centered systems implicitly manage **service contracts** with large language models.

They:
- invoke inference engines intentionally
- route prompts explicitly
- expose model choice and cost
- treat outputs as artifacts

The system does not “think with” the human.
It responds to typed intent.

This prevents collapse of agency and avoids false continuity.

---

### Familiarity without metaphysics

Typing-centered interfaces may resemble chat tools, but do not require chat assumptions.

Critically, they do not:
- claim memory
- assert shared context
- narrate history
- imply companionship

Familiarity reduces friction.
Metaphysics is intentionally absent.

---

### Implication for IAM

IAM inherits this structural advantage while extending it.

Where typing-centered tools manage access to inference services,
IAM additionally **registers the consequences of invocation into a time-bound
continuity substrate owned by the human**.

Typing remains the invariant human-side act:
- the primary generator of continuity
- the anchor of agency
- the boundary of ownership

External inference remains subordinate.

---

### Constraint derived from this insight

Any IAM interface that claims to preserve agency and continuity must:

- center typing as the primary act
- treat inference as explicit service invocation
- preserve a legible boundary between human input and external output
- avoid collapsing interaction into simulated dialogue

The success of typing-centered systems demonstrates that these constraints
are enabling, not limiting.

---

## Constraint 4: Familiarity may be borrowed; metaphysics may not

The interface may resemble familiar tools if doing so reduces cognitive friction.

However, familiarity must not import incompatible assumptions.

**Constraint**
- Chat-like affordances may exist.
- Chat metaphysics must not.

Specifically:
- Threads are not memory.
- Messages are not dialogue.
- Responses are not interlocutors.

The interface must not imply shared consciousness, companionship, or co-agency.

---

## Constraint 5: External inference systems are services, not participants

Large language models and other inference engines are invoked as
**external cognitive services under explicit service contracts**.

They do not:
- own continuity
- remember history
- participate in agency

**Constraint**
- Invocation must be intentional.
- Invocation must be attributable.
- Invocation must be registrable as a discrete event.

The interface must preserve the distinction between:
- human-originated LUIs
- externally generated outputs

Inference produces artifacts, not experience.

---

## Constraint 6: Cost and constraint must remain visible

External inference has:
- economic cost
- energy cost
- opportunity cost

These costs shape judgment and must not be abstracted away.

**Constraint**
- The interface must not conceal when external services are used.
- Automatic invocation must be visible or explicitly enabled.
- Users must retain awareness of cost-bearing actions.

Opacity erodes agency.

---

## Constraint 7: The interface must not collapse ambiguity

IAM preserves human judgment as a defining curvature in the continuity manifold.

The interface must not:
- prematurely resolve ambiguity
- enforce narrative coherence
- pressure thinking toward closure

**Constraint**
- Unfinished thinking must be allowed to persist.
- Open questions may remain open.
- Contradictions may coexist without forced resolution.

The interface supports thinking-in-progress, not answers.

---

## Constraint 8: Continuity must be inspectable without reinterpretation

Users must be able to:
- traverse prior interactions
- re-enter earlier moments
- inspect the sequence of reasoning

**Constraint**
- Inspection must expose the record itself.
- Interpretation may be layered later, but never substituted.

Continuity should be legible by structure alone.

---

## Constraint 9: No assistant persona or proxy agency

IAM does not speak.

External systems may generate text, but IAM itself must not
adopt a voice, personality, or narrative authority.

**Constraint**
- No assistant identity.
- No implied companionship.
- No proxy agency.

The human remains the sole agent whose continuity is being preserved.

---

## Provisional summary invariant

Any interface to IAM must satisfy the following:

- time remains visible
- cost remains legible
- agency remains grounded
- continuity remains irreversible

Any interface element that violates these properties
is incompatible with the Language Infrastructure.

---

## Notes on future promotion

This document is expected to evolve.

Promotion to a numbered LI layer (e.g. a `40_` derivation)
should occur only if:
- these constraints remain stable
- no lower-layer leakage is discovered
- dependencies are clearly downstream of substrate and language layers

Until then, semantic coherence is the enforcement mechanism.
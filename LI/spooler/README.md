## Role: Intake Boundary (Spooler Service)

The spooler service implements the **Intake Boundary** role in the system.

This role is defined as an **always-on, durable entry point** for external events
(Language-Use Inputs, or LUIs), decoupled from downstream ingestion and processing.

The Intake Boundary has the following invariants:

- Persistence occurs **before acknowledgment**.
- Replay safety is enforced via a stable idempotency key (`client_lui_id`).
- Downstream ingest services may be unavailable without blocking intake.
- Deployment substrate is not semantically relevant (edge device, workstation, cloud).

The current implementation of this role is the `spooler` service.

---

## API Planes

The spooler service exposes several API planes, each with a distinct purpose.
These planes are layered and should not be conflated.

### 1. Schema / Control Plane

Endpoints used for **schema discovery and tooling integration**.

- `GET /openai.json`  
  Returns an OpenAPI document suitable for GPT Actions import.

- `GET /openapi.json`  
  Default FastAPI OpenAPI endpoint.

These endpoints do not participate in data capture.

---

### 2. Adapter Plane (External Call Shapes)

Endpoints that accept **source-specific or agent-specific payloads** and adapt them
into the canonical intake contract.

Adapters may:
- validate minimally
- derive canonical fields (e.g., `client_lui_id`)
- attach source metadata

Adapters must:
- terminate in a durable enqueue equivalent to the canonical intake
- preserve Intake Boundary invariants

Examples:
- `POST /spool` (GPT Actions adapter)
- future adapters for webhooks, CLI tools, on-device clients

---

### 3. Canonical Intake Plane

The canonical, invariant-preserving intake API.

- `POST /v1/spool`

This endpoint:
- requires a stable idempotency key
- enforces replay and capacity semantics
- persists before acknowledgment

Adapters must converge to this contract either directly or in-process.

---

### 4. Delivery / Drain Plane

Endpoints concerned with downstream delivery, not capture.

- `POST /v1/drain`
- `GET /v1/status`

These endpoints do not affect intake correctness and may be invoked opportunistically.

---

## Pipeline execution model

The spooler participates in a restartable chew-loop pipeline: upstream intake continues
while downstream systems are unavailable, and delivery is retried without losing history.
The canonical execution invariant is defined in `LI/derive/README.md`.
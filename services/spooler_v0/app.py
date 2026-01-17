# services/spooler_v0/app.py

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import load_config
from .drain import drain_once
from .lui_normalize import canonical_json, normalize_any_rest_payload_to_lui
from .outbox import CapacityError, ConflictError, OutboxError, enqueue, init_outbox, queued_count

cfg = load_config()
init_outbox(cfg.outbox_db_path)

app = FastAPI(title="IAM Spooler v0", version="0.1")


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/v1/status")
def status():
	return {"queued": queued_count(cfg.outbox_db_path)}


@app.post("/v1/spool")
async def spool(request: Request):
	raw = await request.body()
	if len(raw) > cfg.max_request_bytes:
		return JSONResponse(
			status_code=413,
			content={"error": {"code": "REQUEST_TOO_LARGE", "message": "max_request_bytes exceeded"}},
		)

	try:
		payload = await request.json()
		if not isinstance(payload, dict):
			raise ValueError("JSON object required")
	except Exception:
		return JSONResponse(
			status_code=400,
			content={"error": {"code": "INVALID_JSON", "message": "Request must be a JSON object"}},
		)

	try:
		lui = normalize_any_rest_payload_to_lui(payload)
		envelope_json = canonical_json(lui)
		envelope_bytes = len(envelope_json.encode("utf-8"))

		enqueue(
			cfg.outbox_db_path,
			envelope=lui,
			envelope_json=envelope_json,
			envelope_bytes=envelope_bytes,
			max_envelope_bytes=cfg.max_envelope_bytes,
			outbox_max_items=cfg.outbox_max_items,
			outbox_max_bytes=cfg.outbox_max_bytes,
		)
		return {"status": "queued", "client_lui_id": lui.get("client_lui_id")}
	except CapacityError as e:
		return JSONResponse(status_code=507, content={"error": {"code": "OUTBOX_CAPACITY", "message": str(e)}})
	except ConflictError as e:
		return JSONResponse(status_code=409, content={"error": {"code": "CONFLICT", "message": str(e)}})
	except (ValueError, OutboxError) as e:
		return JSONResponse(status_code=400, content={"error": {"code": "INVALID_LUI", "message": str(e)}})


@app.post("/v1/drain")
def drain():
	res = drain_once(
		db_path=cfg.outbox_db_path,
		ingest_url=cfg.ingest_url,
		batch_size=cfg.drain_batch_size,
		timeout_seconds=cfg.drain_timeout_seconds,
	)
	return {"attempted": res.attempted, "acked": res.acked, "failed": res.failed, "conflicts": res.conflicts}

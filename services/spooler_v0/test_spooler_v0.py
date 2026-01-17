# services/spooler_v0/test_spooler_v0.py

from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest
from fastapi.testclient import TestClient

import services.spooler_v0.app as app_mod
import services.spooler_v0.drain as drain_mod
from services.spooler_v0.config import load_config
from services.spooler_v0.lui_normalize import canonical_json
from services.spooler_v0.outbox import init_outbox, queued_count


@pytest.fixture()
def client_tmpdb(monkeypatch, tmp_path: Path):
	"""
	Deterministic fixture:
	- sets env
	- loads cfg from env
	- forces app module to use this cfg (app.py loads cfg at import-time otherwise)
	- initializes outbox db at the temp location
	"""
	db_path = tmp_path / "outbox.db"
	monkeypatch.setenv("OUTBOX_DB_PATH", str(db_path))
	monkeypatch.setenv("INGEST_URL", "http://example.invalid/v1/luis")
	monkeypatch.setenv("SPOOLER_MAX_REQUEST_BYTES", "262144")
	monkeypatch.setenv("SPOOLER_MAX_ENVELOPE_BYTES", "524288")
	monkeypatch.setenv("OUTBOX_MAX_ITEMS", "10")
	monkeypatch.setenv("OUTBOX_MAX_BYTES", str(1024 * 1024))  # 1MB
	monkeypatch.setenv("DRAIN_BATCH_SIZE", "5")
	monkeypatch.setenv("DRAIN_TIMEOUT_SECONDS", "2")

	cfg = load_config()

	# Force the running app to use the fixture config (app.py loads cfg at import time).
	app_mod.cfg = cfg
	init_outbox(cfg.outbox_db_path)

	with TestClient(app_mod.app) as client:
		yield client, cfg.outbox_db_path


def _lui(i: int, text: str = "hello"):
	return {
		"client_lui_id": f"test:{i}",
		"captured_at": "2026-01-12T19:22:11Z",
		"source": {"client": "test", "device_id": "DEV"},
		"kind": "message",
		"payload": {"text": text, "json": {"role": "user"}},
		"privacy": {"payload_mode": "plaintext"},
	}


def _fetch_row(db_path: Path, client_lui_id: str):
	conn = sqlite3.connect(str(db_path))
	try:
		conn.row_factory = sqlite3.Row
		return conn.execute(
			"SELECT envelope_json, status FROM outbox_events WHERE client_lui_id=?;",
			(client_lui_id,),
		).fetchone()
	finally:
		conn.close()


def test_enqueue_persists(client_tmpdb):
	client, db_path = client_tmpdb
	before = queued_count(db_path)
	r = client.post("/v1/spool", json=_lui(1))
	assert r.status_code == 200
	assert queued_count(db_path) == before + 1


def test_idempotent_enqueue_no_duplicate(client_tmpdb):
	client, db_path = client_tmpdb
	r1 = client.post("/v1/spool", json=_lui(2))
	assert r1.status_code == 200
	c1 = queued_count(db_path)
	r2 = client.post("/v1/spool", json=_lui(2))
	assert r2.status_code == 200
	assert queued_count(db_path) == c1


def test_conflicting_replay_returns_409(client_tmpdb):
	"""
	LI requirement: conflicting replay returns 409 and does not mutate stored envelope.
	Note: implementation may mark status='conflict', so queued_count may drop.
	"""
	client, db_path = client_tmpdb

	orig = _lui(3, text="A")
	orig_json = canonical_json(orig)

	r1 = client.post("/v1/spool", json=orig)
	assert r1.status_code == 200

	# Conflicting replay (same client_lui_id, different content)
	r2 = client.post("/v1/spool", json=_lui(3, text="B"))
	assert r2.status_code == 409

	row = _fetch_row(db_path, "test:3")
	assert row is not None, "Outbox row must remain present after conflict replay"
	assert str(row["envelope_json"]) == orig_json, "Stored envelope must be immutable after enqueue"


def test_drain_success_acks_and_removes(client_tmpdb, monkeypatch):
	"""
	Invariant: drain success removes items (acked items no longer queued).
	"""
	client, db_path = client_tmpdb
	client.post("/v1/spool", json=_lui(10))
	client.post("/v1/spool", json=_lui(11))
	assert queued_count(db_path) == 2

	def fake_post(_ingest_url: str, _envelope_json: str, _timeout_seconds: int):
		return 200, "ok"

	monkeypatch.setattr(drain_mod, "_post", fake_post)

	r = client.post("/v1/drain")
	assert r.status_code == 200
	body = r.json()
	assert body["acked"] == 2
	assert body["failed"] == 0
	assert body["conflicts"] == 0
	assert queued_count(db_path) == 0


def test_drain_failure_leaves_items_queued(client_tmpdb, monkeypatch):
	"""
	Invariant: drain failure leaves items intact (not acked/removed).
	"""
	client, db_path = client_tmpdb
	client.post("/v1/spool", json=_lui(20))
	client.post("/v1/spool", json=_lui(21))
	assert queued_count(db_path) == 2

	def fake_post(_ingest_url: str, _envelope_json: str, _timeout_seconds: int):
		return 500, "nope"

	monkeypatch.setattr(drain_mod, "_post", fake_post)

	r = client.post("/v1/drain")
	assert r.status_code == 200
	body = r.json()
	assert body["acked"] == 0
	assert body["failed"] == 2
	assert body["conflicts"] == 0
	assert queued_count(db_path) == 2


def test_capacity_limit_rejects_with_507(client_tmpdb, monkeypatch):
	"""
	Invariant: capacity limits reject intake explicitly.
	We enforce OUTBOX_MAX_ITEMS=1 by config reload (SpoolerConfig is frozen).
	"""
	client, db_path = client_tmpdb

	monkeypatch.setenv("OUTBOX_MAX_ITEMS", "1")
	cfg = load_config()
	app_mod.cfg = cfg
	init_outbox(cfg.outbox_db_path)

	r1 = client.post("/v1/spool", json=_lui(30))
	assert r1.status_code == 200
	assert queued_count(db_path) == 1

	r2 = client.post("/v1/spool", json=_lui(31))
	assert r2.status_code == 507
	assert queued_count(db_path) == 1
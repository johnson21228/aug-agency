# services/spooler_v0/tests/test_spooler_v0.py

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.spooler_v0.app import app
from services.spooler_v0.config import load_config
from services.spooler_v0.outbox import init_outbox, queued_count


@pytest.fixture()
def client_tmpdb(monkeypatch, tmp_path: Path):
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
    init_outbox(cfg.outbox_db_path)

    with TestClient(app) as client:
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
    client, db_path = client_tmpdb
    r1 = client.post("/v1/spool", json=_lui(3, text="A"))
    assert r1.status_code == 200
    c1 = queued_count(db_path)
    r2 = client.post("/v1/spool", json=_lui(3, text="B"))
    assert r2.status_code == 409
    assert queued_count(db_path) == c1

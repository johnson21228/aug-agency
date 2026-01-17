# services/spooler_v0/config.py

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpoolerConfig:
    outbox_db_path: Path
    ingest_url: str

    max_request_bytes: int
    max_envelope_bytes: int
    outbox_max_items: int
    outbox_max_bytes: int

    drain_batch_size: int
    drain_timeout_seconds: int


def load_config() -> SpoolerConfig:
    return SpoolerConfig(
        outbox_db_path=Path(os.environ.get("OUTBOX_DB_PATH", "./spooler_outbox.db")).expanduser().resolve(),
        ingest_url=os.environ.get("INGEST_URL", "http://localhost:8000/v1/luis"),
        max_request_bytes=int(os.environ.get("SPOOLER_MAX_REQUEST_BYTES", "262144")),     # 256 KB
        max_envelope_bytes=int(os.environ.get("SPOOLER_MAX_ENVELOPE_BYTES", "524288")),   # 512 KB
        outbox_max_items=int(os.environ.get("OUTBOX_MAX_ITEMS", "2000000")),
        outbox_max_bytes=int(os.environ.get("OUTBOX_MAX_BYTES", str(20 * 1024 * 1024 * 1024))),  # 20 GB
        drain_batch_size=int(os.environ.get("DRAIN_BATCH_SIZE", "200")),
        drain_timeout_seconds=int(os.environ.get("DRAIN_TIMEOUT_SECONDS", "20")),
    )

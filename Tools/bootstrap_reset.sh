#!/usr/bin/env bash
set -euo pipefail

# Guard: must run from repo root
if [[ ! -d "services" || ! -d "LI" ]]; then
  echo "ERROR: run this from repo root (expected ./services and ./LI)."
  exit 1
fi

echo "[bootstrap_reset] removing local artifacts (outbox + iam db + caches)"

rm -f \
  data/outbox/spooler_outbox.db data/outbox/spooler_outbox.db-wal data/outbox/spooler_outbox.db-shm \
  data/iam/iam.db data/iam/iam.db-wal data/iam/iam.db-shm \
  data/iam/iam.dev.db data/iam/iam.dev.db-wal data/iam/iam.dev.db-shm \
  data/outbox/chatgpt_import.ndjson data/outbox/chatgpt_import.ndjson.gz

find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

mkdir -p data/outbox data/iam

echo "[bootstrap_reset] done"

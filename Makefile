# =============================================================================
# augmented-agency — Makefile
# =============================================================================

# -----------------------------------------------------------------------------
# Tooling
# -----------------------------------------------------------------------------

PYTHON ?= python3

# -----------------------------------------------------------------------------
# Existing / legacy targets (unchanged semantics)
# -----------------------------------------------------------------------------

.PHONY: ingest spooler clean-data

ingest:
	$(PYTHON) -m uvicorn services.ingest_server_v0.app:app --host 127.0.0.1 --port 7001

spooler:
	$(PYTHON) -m uvicorn services.spooler_v0.app:app --host 127.0.0.1 --port 7000

clean-data:
	rm -rf data/inbox data/staging data/artifacts

# =============================================================================
# BOOTSTRAP HARNESS (rebuild-from-scratch)
#
# Purpose:
#   - deterministic, repeatable bootstrap from ChatGPT exports
#   - clear separation from legacy / always-on services
#   - safe to delete everything and start again
#
# Philosophy:
#   - iam.db captures FULL block-canonical LUI records
#   - segmentation / chewing happens downstream
#   - spooler + ingest are explicitly orchestrated
#
# Ports:
#   - spooler  :8000
#   - ingest   :8001
# =============================================================================

.PHONY: \
	bootstrap-reset \
	bootstrap-ingest \
	bootstrap-spooler \
	bootstrap-spool \
	bootstrap-drain-once \
	bootstrap-drain-loop \
	bootstrap-status

BOOT_HOST ?= 127.0.0.1
BOOT_SPOOLER_PORT ?= 8000
BOOT_INGEST_PORT ?= 8001

BOOT_OUTBOX_DB ?= ./data/outbox/spooler_outbox.db
BOOT_IAM_DB ?= ./data/iam/iam.db

# Must be provided for bootstrap-spool
EXPORT_JSON ?=

# -----------------------------------------------------------------------------
# Reset everything to zero (authoritative)
# -----------------------------------------------------------------------------

bootstrap-reset:
	./tools/bootstrap_reset.sh

# -----------------------------------------------------------------------------
# Start ingest server (writes iam.db)
# -----------------------------------------------------------------------------

bootstrap-ingest:
	@mkdir -p data/iam
	@echo "Starting ingest server on $(BOOT_HOST):$(BOOT_INGEST_PORT)"
	@echo "IAM_DB_PATH=$(BOOT_IAM_DB)"
	@IAM_DB_PATH="$(BOOT_IAM_DB)" \
	$(PYTHON) -m uvicorn services.ingest_server_v0.app:app \
	  --host $(BOOT_HOST) --port $(BOOT_INGEST_PORT)

# -----------------------------------------------------------------------------
# Start spooler (outbox + drain endpoint)
# -----------------------------------------------------------------------------

bootstrap-spooler:
	@mkdir -p data/outbox
	@echo "Starting spooler on $(BOOT_HOST):$(BOOT_SPOOLER_PORT)"
	@echo "OUTBOX_DB_PATH=$(BOOT_OUTBOX_DB)"
	@OUTBOX_DB_PATH="$(BOOT_OUTBOX_DB)" \
	INGEST_URL="http://$(BOOT_HOST):$(BOOT_INGEST_PORT)/v1/luis" \
	$(PYTHON) -m uvicorn services.spooler_v0.app:app \
	  --host $(BOOT_HOST) --port $(BOOT_SPOOLER_PORT)

# -----------------------------------------------------------------------------
# Feed ChatGPT export into spooler
# -----------------------------------------------------------------------------

bootstrap-spool:
	@if [ -z "$(EXPORT_JSON)" ]; then \
	  echo "ERROR: set EXPORT_JSON=../path/to/conversations.json"; exit 2; \
	fi
	@echo "Spooling export: $(EXPORT_JSON)"
	$(PYTHON) sources/chatgpt_export_v0/spool_chatgpt_export.py "$(EXPORT_JSON)" \
	  --spooler "http://$(BOOT_HOST):$(BOOT_SPOOLER_PORT)/v1/spool"

# -----------------------------------------------------------------------------
# Drain controls
# -----------------------------------------------------------------------------

bootstrap-drain-once:
	curl -s -X POST "http://$(BOOT_HOST):$(BOOT_SPOOLER_PORT)/v1/drain" || true
	@echo

bootstrap-drain-loop:
	@echo "Draining outbox until queued=0 (Ctrl+C to stop)"
	@while true; do \
	  curl -s -X POST "http://$(BOOT_HOST):$(BOOT_SPOOLER_PORT)/v1/drain" >/dev/null || true; \
	  sqlite3 "$(BOOT_OUTBOX_DB)" \
	    "SELECT status, COUNT(*) FROM outbox_events GROUP BY status;" || true; \
	  sleep 0.2; \
	done

# -----------------------------------------------------------------------------
# Status / inspection
# -----------------------------------------------------------------------------

bootstrap-status:
	@echo "Outbox status:"
	@sqlite3 "$(BOOT_OUTBOX_DB)" \
	  "SELECT status, COUNT(*) FROM outbox_events GROUP BY status;" || true
	@echo
	@echo "Outbox errors:"
	@sqlite3 "$(BOOT_OUTBOX_DB)" \
	  "SELECT COUNT(*) FROM outbox_events WHERE last_error IS NOT NULL;" || true
	@echo
	@echo "iam.db:"
	@ls -lh "$(BOOT_IAM_DB)" 2>/dev/null || echo "(missing)"



.PHONY: li-validate
li-validate:
	$(PYTHON) tools/li_validate.py

	
# =============================================================================
# End of Makefile
# =============================================================================


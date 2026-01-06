# ======================================================
# IAM / Augmented Agency — Makefile
#
# Usage (from repo root):
#
#   make            # show this help
#   make ingest     # ingest latest ChatGPT export
#   make ingest-dry # validate export only (no DB write)
#
# ======================================================

.PHONY: help ingest ingest-dry clean-data

PYTHON := python3

# ------------------------------------------------------
# Help (default)
# ------------------------------------------------------

help:
	@echo ""
	@echo "IAM / Augmented Agency"
	@echo ""
	@echo "Common commands:"
	@echo "  make ingest        Ingest latest ChatGPT export into iam.db"
	@echo "  make ingest-dry    Normalize + validate export only (no DB write)\n  make canonicalize  Rebuild message_canonical view"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean-data    Remove all local data artifacts (DANGEROUS)"
	@echo ""

# ------------------------------------------------------
# Ingest ChatGPT export
# ------------------------------------------------------

ingest:
	$(PYTHON) code/ingest/ingest_chatgpt_export.py

ingest-dry:
	$(PYTHON) code/ingest/ingest_chatgpt_export.py --dry-run
	
ingest-keep:
	$(PYTHON) code/ingest/ingest_chatgpt_export.py --keep-staging
	
.PHONY: lui-packets

.PHONY: lui-packets

lui-packets:
	$(PYTHON) code/export/export_lui_packets_stage1.py --db data/artifacts/iam.db --out data/artifacts/lui_packets.jsonl --mode final-human --max-chars 24000 --include-titles

.PHONY: fm-chunks
fm-chunks:
	$(PYTHON) code/export/chunk_lui_packets_for_fm.py \
	  --in data/artifacts/lui_packets.jsonl \
	  --out data/artifacts/fm_chunks \
	  --target-chars 16000 \
	  --reserve-chars 2000 \
	  --include-titles \
	  --clean
	  
# ------------------------------------------------------
# Cleanup (local only, gitignored)
# ------------------------------------------------------

clean-data:
	@echo "WARNING: This will delete ALL local data artifacts:"
	@echo "  data/inbox/"
	@echo "  data/staging/"
	@echo "  data/artifacts/"
	@echo ""
	@read -p "Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	rm -rf data/inbox data/staging data/artifacts
	@echo "Local data artifacts removed."

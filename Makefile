# Makefile
# ======================================================
# IAM / Augmented Agency — Makefile
#
# Usage (from repo root):
#
#   make                 # show this help
#   make ingest          # ingest latest ChatGPT export
#   make ingest-dry      # validate export only (no DB write)
#
# ======================================================

.PHONY: help ingest ingest-dry clean-data ingest-keep canonicalize
.PHONY: lui-packets fm-chunks
.PHONY: pack-writings pack-writings-src
.PHONY: pack-all pack-repo verify-pack-repo unpack-repo update-writings build-site
.PHONY: venv site docs dist clean
.PHONY: update-writing-index
.PHONY: publish-site publish-site-fast publish-site-open
.PHONY: spooler test-spooler
.PHONY: li-validate

PYTHON := python3

# Ensure repo-root import resolution for services/* and sources/*
export PYTHONPATH := $(CURDIR)

# ------------------------------------------------------
# Help (default)
# ------------------------------------------------------

help:
	@echo ""
	@echo "IAM / Augmented Agency"
	@echo ""
	@echo "Common commands:"
	@echo "  make ingest            Ingest latest ChatGPT export into iam.db"
	@echo "  make ingest-dry        Normalize + validate export only (no DB write)"
	@echo "  make canonicalize      Rebuild message_canonical view"
	@echo ""
	@echo "Canonical repo pack (ChatGPT upload):"
	@echo "  make pack-repo         Build canonical repo ZIP -> dist/"
	@echo "  make verify-pack-repo  Verify ZIP integrity"
	@echo "  make unpack-repo       Unpack ZIP into dist/ for inspection"
	@echo ""
	@echo "Derived outputs:"
	@echo "  make pack-writings     Create pack-writings.zip (English-only writings) + PDF"
	@echo "  make docs              Build GitHub Pages site (./docs)"
	@echo "  make pack-all          Run: pack repo + update writings index + build docs site"
	@echo ""
	@echo "Services:"
	@echo "  make spooler           Run spooler v0 on :7000"
	@echo "  make test-spooler      Run spooler v0 tests"
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

canonicalize:
	$(PYTHON) code/db/rebuild_message_canonical.py

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

# ------------------------------------------------------
# Dist directory
# ------------------------------------------------------

dist:
	@mkdir -p dist

# ------------------------------------------------------
# Canonical repo pack (ChatGPT-safe)
# ------------------------------------------------------

PACK_REPO_ZIP := dist/augmented-agency-pack-repo.zip
PACK_REPO_DIR := dist/augmented-agency-pack-repo.unpacked

pack-repo: dist
	@echo "Building canonical repo pack ..."
	$(PYTHON) Tools/pack_md_repo.py
	@if [ -f "augmented-agency-pack-repo.zip" ]; then \
		mv -f "augmented-agency-pack-repo.zip" "$(PACK_REPO_ZIP)"; \
	elif [ -f "augmented-agency-ingest-md-py.zip" ]; then \
		mv -f "augmented-agency-ingest-md-py.zip" "$(PACK_REPO_ZIP)"; \
	else \
		echo "ERROR: Tools/pack_md_repo.py did not produce expected zip"; \
		exit 1; \
	fi
	@shasum -a 256 "$(PACK_REPO_ZIP)" > "$(PACK_REPO_ZIP).sha256"
	@unzip -tq "$(PACK_REPO_ZIP)" >/dev/null
	@echo "OK: $(PACK_REPO_ZIP)"

verify-pack-repo:
	@if [ ! -f "$(PACK_REPO_ZIP)" ]; then \
		echo "ERROR: missing $(PACK_REPO_ZIP). Run: make pack-repo"; \
		exit 1; \
	fi
	@unzip -tq "$(PACK_REPO_ZIP)" >/dev/null
	@echo "OK: zip integrity verified"

unpack-repo: verify-pack-repo
	@rm -rf "$(PACK_REPO_DIR)"
	@mkdir -p "$(PACK_REPO_DIR)"
	@unzip -q "$(PACK_REPO_ZIP)" -d "$(PACK_REPO_DIR)"
	@echo "OK: unpacked to $(PACK_REPO_DIR)"
	@ls -la "$(PACK_REPO_DIR)" | sed -n '1,200p'

# ------------------------------------------------------
# Site builder / docs / publishing
# (unchanged from your previous version)
# ------------------------------------------------------

# … remaining sections unchanged …

# ------------------------------------------------------
# Language Infrastructure validation
# ------------------------------------------------------

li-validate:
	$(PYTHON) Tools/li_validate.py

# ------------------------------------------------------
# Services (conformance implementations)
# ------------------------------------------------------

spooler:
	@echo "Starting spooler v0 on :7000"
	$(PYTHON) -m uvicorn services.spooler_v0.app:app --host 0.0.0.0 --port 7000 --reload

test-spooler:
	$(PYTHON) -m pytest -q services/spooler_v0/tests/test_spooler_v0.py
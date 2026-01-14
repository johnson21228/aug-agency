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

.PHONY: help ingest ingest-dry clean-data ingest-keep canonicalize
.PHONY: lui-packets fm-chunks
.PHONY: pack-md-py pack-writings pack-writings-src
.PHONY: pack-all pack-repo update-writings build-site
.PHONY: venv site docs dist clean
.PHONY: update-writing-index
.PHONY: publish-site publish-site-fast publish-site-open

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
	@echo "  make ingest-dry    Normalize + validate export only (no DB write)"
	@echo "  make canonicalize  Rebuild message_canonical view"
	@echo ""
	@echo "Derived outputs:"
	@echo "  make pack-md-py    Create canonical repo pack ZIP (Tools/pack_md_repo.py)"
	@echo "  make pack-writings Create pack-writings.zip (English-only writings) + PDF"
	@echo "  make docs          Build GitHub Pages site (./docs)"
	@echo "  make pack-all      Run: pack repo + update writings index + build docs site"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean-data    Remove all local data artifacts (DANGEROUS)"
	@echo ""
	@echo "Site:"
	@echo "  make venv          Create/refresh .venv for site builder"
	@echo "  make site          Build local preview site (alias of docs; build output is ./docs)"
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
# Exports
# ------------------------------------------------------

lui-packets:
	$(PYTHON) code/export/export_lui_packets_stage1.py --db data/artifacts/iam.db --out data/artifacts/lui_packets.jsonl --mode final-human --max-chars 24000 --include-titles

fm-chunks:
	$(PYTHON) code/export/chunk_lui_packets_for_fm.py --in data/artifacts/lui_packets.jsonl --out data/artifacts/fm_chunks --target-chars 16000 --reserve-chars 2000 --include-titles --clean

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
# Canonical repo pack
# ------------------------------------------------------

pack-md-py:
	$(PYTHON) Tools/pack_md_repo.py

# ------------------------------------------------------
# Site builder venv (project-local)
# ------------------------------------------------------

VENV        := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
SITE_REQS   := Tools/requirements.txt

venv: $(VENV_PYTHON)
	@echo "OK: venv ready at $(VENV)"

$(VENV_PYTHON):
	@echo "Creating venv at $(VENV) ..."
	python3 -m venv $(VENV)
	@echo "Upgrading pip ..."
	$(VENV_PIP) install --upgrade pip
	@echo "Installing site builder deps ..."
	@if [ -f "$(SITE_REQS)" ]; then \
		$(VENV_PIP) install -r "$(SITE_REQS)"; \
	else \
		$(VENV_PIP) install pyyaml; \
	fi

# Build local preview site (alias of docs; Tools/build_site.py writes to ./docs)
site: $(VENV_PYTHON)
	$(VENV_PYTHON) Tools/build_site.py

# Build GitHub Pages site (committed output in ./docs)
docs: $(VENV_PYTHON)
	$(VENV_PYTHON) Tools/build_site.py

# ------------------------------------------------------
# Writings pack (dist)
# ------------------------------------------------------

dist:
	@mkdir -p dist

pack-writings: dist venv
	@.venv/bin/python Tools/pack_writings.py --out dist/pack-writings.zip --pdf

pack-writings-src: dist venv
	@.venv/bin/python Tools/pack_writings.py --out dist/pack-writings-src.zip --no-pdf

clean:
	@rm -rf dist docs

# ------------------------------------------------------
# Writing index updater
# ------------------------------------------------------

update-writing-index:
	@echo "Updating writing/index.yaml from writing/essays/"
	$(PYTHON) Tools/update_writing_index.py

# ------------------------------------------------------
# Pack-all (repo + writings index + docs site)
# ------------------------------------------------------

pack-repo:
	$(PYTHON) Tools/pack_md_repo.py

update-writings:
	$(PYTHON) Tools/update_writing_index.py

build-site: $(VENV_PYTHON)
	$(VENV_PYTHON) Tools/build_site.py

pack-all: pack-repo update-writings build-site

# ------------------------------------------------------
# Publish docs -> public site repo (sibling checkout)
#
# IMPORTANT:
# Run `make publish-site*` from the root of the private
# `augmented-agency` repo.
#
# Assumes the public site repo exists at:
#   ../augmented-agency-site
# ------------------------------------------------------

PUBLIC_SITE_DIR := ../augmented-agency-site

publish-site: docs
	@if [ ! -d "$(PUBLIC_SITE_DIR)" ]; then \
		echo "ERROR: public site repo not found at $(PUBLIC_SITE_DIR)"; \
		exit 1; \
	fi
	@echo "Syncing ./docs -> $(PUBLIC_SITE_DIR)/docs ..."
	rsync -av --delete docs/ "$(PUBLIC_SITE_DIR)/docs/"
	@echo "Done."

publish-site-fast: docs
	@if [ ! -d "$(PUBLIC_SITE_DIR)" ]; then \
		echo "ERROR: public site repo not found at $(PUBLIC_SITE_DIR)"; \
		exit 1; \
	fi
	@echo "Syncing ./docs -> $(PUBLIC_SITE_DIR)/docs (fast) ..."
	rsync -a docs/ "$(PUBLIC_SITE_DIR)/docs/"
	@echo "Done."

publish-site-open: publish-site
	@echo "Opening public site repo ..."
	cd "$(PUBLIC_SITE_DIR)" && git status

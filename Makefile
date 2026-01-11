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
	@echo "Site:"
	@echo "  make site          Build local preview site (./site, not committed)"
	@echo "  make docs          Build GitHub Pages site (./docs, committed)"
	@echo "  make venv          Create/refresh .venv for site builder"
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

.PHONY: pack-md-py

pack-md-py:
	$(PYTHON) Tools/pack_md_repo.py


# ======================================================
# Site builder: project-local venv (so you don't need to
# install PyYAML globally or activate anything manually)
# ======================================================

VENV        := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
SITE_REQS   := tools/requirements.txt

.PHONY: venv
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


.PHONY: site
# Build local preview site (not committed)
site: $(VENV_PYTHON)
	$(VENV_PYTHON) tools/build_site.py --out site

.PHONY: site docs

# Build GitHub Pages site (committed)
docs: $(VENV_PYTHON)
	$(VENV_PYTHON) tools/build_site.py --out docs


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

SITE_REPO ?= ../augmented-agency-site
SITE_BRANCH ?= main
MSG ?= "Publish site updates"

.PHONY: publish-site-status sync-site commit-site push-site publish publish-site publish-site-commit

publish-site-status:
	@test -d "$(SITE_REPO)" || (echo "ERROR: SITE_REPO not found: $(SITE_REPO)"; exit 1)
	@test -d "$(SITE_REPO)/.git" || (echo "ERROR: SITE_REPO is not a git repo (missing .git): $(SITE_REPO)"; exit 1)
	@echo "OK: public site repo found at $(SITE_REPO)"

# Sync only (NO git operations)
sync-site: docs publish-site-status
	rsync -av --delete --exclude .git docs/ "$(SITE_REPO)/"
	@echo "Synced ./docs -> $(SITE_REPO)"

# Commit in public repo (no-op if nothing changed)
commit-site: sync-site
	@cd "$(SITE_REPO)" && \
	  git checkout "$(SITE_BRANCH)" >/dev/null 2>&1 || true && \
	  if git status --porcelain | grep -q . ; then \
	    git add -A && \
	    git commit -m $(MSG) ; \
	  else \
	    echo "No changes to commit in site repo."; \
	  fi

# Push public repo (updates GitHub Pages)
push-site: commit-site
	@cd "$(SITE_REPO)" && git push origin "$(SITE_BRANCH)"
	@echo "Published (GitHub Pages will update automatically)."

# One-command publish: build -> sync -> commit -> push
publish: push-site
	@echo "Done."

# Backwards-compatible target names
publish-site: sync-site
publish-site-commit: publish


# -------- Paths --------
IAM_DB := iam.db
PROVDB := provdb_core.db
SUBDB := subdb_nodes.db

CAPTURE_SCHEMA := Migrations/0001_capture_contract.sql

# -------- Init targets --------

.PHONY: init-iam-db
init-iam-db:
	@if [ -f $(IAM_DB) ]; then \
		echo "$(IAM_DB) already exists"; \
	else \
		echo "Creating $(IAM_DB)"; \
		sqlite3 $(IAM_DB) < $(CAPTURE_SCHEMA); \
	fi

.PHONY: init-provdb
init-provdb: init-iam-db
	@if [ -f $(PROVDB) ]; then \
		echo "$(PROVDB) already exists"; \
	else \
		echo "Creating empty $(PROVDB)"; \
		python3 code/provDB/build_provdb_core.py --iam-db $(IAM_DB) --out $(PROVDB); \
	fi

# -------- Build targets --------

.PHONY: build-provdb
build-provdb:
	@if [ ! -f $(IAM_DB) ]; then \
		echo "ERROR: $(IAM_DB) missing. Run 'make init-iam-db' first."; \
		exit 1; \
	fi
	python3 code/provDB/build_provdb_core.py --iam-db $(IAM_DB) --out $(PROVDB)

.PHONY: build-prp-nodes
build-prp-nodes:
	@if [ ! -f $(PROVDB) ]; then \
		echo "ERROR: $(PROVDB) missing. Run 'make build-provdb' first."; \
		exit 1; \
	fi
	python3 code/provDB/build_provdb_nodes_prp_v1.py --provdb $(PROVDB)

.PHONY: build-subdb
build-subdb:
	@if [ ! -f $(PROVDB) ]; then \
		echo "ERROR: $(PROVDB) missing. Run 'make build-provdb' first."; \
		exit 1; \
	fi
	python3 code/subDB/build_subdb_nodes.py \
		--provdb $(PROVDB) \
		--layer prp_v1_turn_pairing \
		--out $(SUBDB)

# -------- One-shot --------

.PHONY: init-all
init-all: init-iam-db build-provdb build-prp-nodes build-subdb


.PHONY: pack-writings pack-writings-src

pack-writings:
	@mkdir -p dist
	@.venv/bin/python tools/pack_writings.py --out dist/pack-writings.zip --pdf

pack-writings-src:
	@mkdir -p dist
	@.venv/bin/python tools/pack_writings.py --out dist/pack-writings-src.zip --no-pdf



SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv venv-pdf build-site pack-writings pack-writings-src clean

help:
	@echo "Targets:"
	@echo "  make venv               - create .venv and install requirements.txt"
	@echo "  make venv-pdf           - install PDF requirements (reportlab)"
	@echo "  make build-site         - build docs/ from writing/index.yaml"
	@echo "  make pack-writings-src  - zip writings (source-only, no PDFs)"
	@echo "  make pack-writings      - zip writings + PDFs (requires venv-pdf)"
	@echo "  make clean              - remove dist/ and docs/"

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt

venv-pdf: venv
	@$(PIP) install -r requirements-pdf.txt

build-site: venv
	@$(PYTHON) Tools/build_site.py

pack-writings-src: venv
	@mkdir -p dist
	@$(PYTHON) Tools/pack_writings.py --out dist/pack-writings-src.zip --no-pdf

pack-writings: venv-pdf
	@mkdir -p dist
	@$(PYTHON) Tools/pack_writings.py --out dist/pack-writings.zip --pdf

clean:
	@rm -rf dist docs

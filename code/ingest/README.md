# Ingest — ChatGPT Export

This module ingests ChatGPT data exports into the IAM database.

Pipeline:
1. Discover newest export in `data/inbox/chatgpt_export/`
2. Normalize into `data/staging/chatgpt_export_latest/`
3. Ingest into `data/artifacts/iam.db`

No data in `data/` is ever committed.

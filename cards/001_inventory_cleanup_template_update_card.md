# Card 001 — Inventory, Cleanup, and Template Update

## Intent

Separate the current mixed worktree into coherent streams and import the useful Workbench template update without colliding with the existing Augmented Agency / IAM authority structure.

## Context

The worktree showed one staged CB file plus multiple modified/untracked files across README, Makefile, writings, LI, prompts, tools, and patent/provisional areas.

The uploaded Workbench template includes newer Workbench governance patterns, including the Workbench Experiential Intelligence capture-back.

## Decision

Do not sweep the whole worktree into one commit.

Do import the template insight as adapted repo-specific continuity under uppercase `LI/` and `cards/`.

Do treat patent/provisional files as review-sensitive until explicitly accepted for commit/share.

## Commit strategy

Recommended commits:

1. `Capture workbench experiential intelligence`
2. `Inventory augmented agency cleanup and template update`
3. `Add LI tooling and pack workflow` if tools are reviewed
4. `Update README and writing essay` if content changes are intentional
5. Patent/provisional commit only after explicit review

## Follow-up

Run the inventory script and inspect generated output before committing broad changes.

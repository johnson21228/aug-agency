# Inventory Cleanup After Template Update

Use this prompt after uploading the latest `augmented-agency` pack and, if relevant, the latest `workbench-li-template` pack.

```text
You are helping me clean up the augmented-agency repo.

First identify the active purpose: inventory and cleanup, not new ideation.

Read:
- MAP.md
- README.md
- LI/README.md
- docs/root_inventory_cleanup_plan.md if present
- LI/workflow/template_update_without_authority_collision.md if present

Then answer:
1. What files are likely intentional source changes?
2. What files are likely generated/build artifacts?
3. What files are sensitive and should not be packed/shared casually?
4. What template updates are appropriate to adapt into this repo?
5. What should be committed first, second, and later?
6. What should not be committed yet?

Do not recommend `git add -A` unless all untracked and modified files have been classified.
```

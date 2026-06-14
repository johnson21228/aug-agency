# Capture Back — Augmented Agency Template Alignment

This overlay updates the Augmented Agency / IAM repo to match the current Workbench LI template operating surface while preserving existing IAM authority.

## Apply

```bash
unzip -o ~/Downloads/augmented-agency-wb-template-alignment-overlay.zip -d .
make verify
make pack
git status --short
```

## Expected verification

```text
Workbench LI template integrity check passed.
Workbench LI governance verification passed.
```

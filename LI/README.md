# Language Infrastructure (LI)

This directory contains human-authored, normative Language Infrastructure artifacts.

- Do not write generated artifacts into `LI/`.
- Derived, machine-consumed artifacts belong in `Derived/`.
- Published site output belongs in `docs/`.

This repo uses a repeated pattern:
Authoritative LI → Derived (compiled) artifacts → Executors → Output.

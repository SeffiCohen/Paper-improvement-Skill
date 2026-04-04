# Paper Improvement Skill

This repository contains the Paper Improvement skill — a structured system for diagnosing, revising, and preparing academic manuscripts for submission, with embedded support for **NeurIPS 2026**.

## Skill location

All skill files live under `paper-improvement/`:
- `paper-improvement/SKILL.md` — Main operational guide and workflow
- `paper-improvement/references/` — Reviewer lens, statistics, venue rules, schemas
- `paper-improvement/assets/` — Checklists, templates, boilerplate starters
- `paper-improvement/scripts/` — Python analysis tools (lint, evidence matrix, results analysis, repro gate, etc.)

## Custom slash commands

The skill is available via these slash commands:

- `/project:neurips-2026` — Full NeurIPS 2026 submission preparation workflow
- `/project:paper-diagnose` — Draft diagnosis and manuscript critique
- `/project:paper-review-response` — Review response and rebuttal planning
- `/project:paper-evidence-audit` — Evidence audit with claim-to-evidence mapping

## Key references

When working on a NeurIPS 2026 submission, always load `paper-improvement/references/neurips-2026.md` for concrete venue rules. Do not rely on memory for venue requirements — use the embedded references.

## Python scripts

Scripts are in `paper-improvement/scripts/` and require Python 3. They share utilities from `common.py`. Key scripts:
- `build_paper_spec.py` — Build normalized paper spec (supports `--venue neurips2026`)
- `paper_lint.py` — Lint manuscript (supports `--venue neurips2026` for NeurIPS-specific checks)
- `evidence_matrix.py` — Map claims to experimental evidence
- `analyze_results.py` — Multi-seed aggregation and paired comparisons
- `repro_gate.py` — Reproducibility verdict
- `propose_improvements.py` — Prioritized revision queue
- `rebuttal_planner.py` — Structured rebuttal plan from reviews
- `lit_refresh.py` — Literature refresh from arXiv and Crossref

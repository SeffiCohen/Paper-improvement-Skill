---
name: paper-improvement
description: improve academic papers, especially empirical and computational papers in machine learning, ai, nlp, and adjacent fields. use when chatgpt needs to diagnose or revise a manuscript, map claims to evidence, audit experiments and statistics, compare result tables from csv files, refresh related work with current sources, prepare reviewer-style critiques or rebuttals, or assemble submission-ready reproducibility and artifact materials.
---

# Paper Improvement

Run this skill in the mode that matches the available inputs.

## Pick the operating mode

1. **Draft diagnosis**
- Use when the user has a draft, PDF, LaTeX, markdown, or section text and wants stronger writing, framing, structure, or positioning.

2. **Evidence audit**
- Use when the paper makes empirical or computational claims and the user also has results tables, CSVs, configs, logs, or a code repository.

3. **Review response**
- Use when the user has reviewer comments, a meta-review, or rebuttal constraints and needs a response plan plus manuscript changes.

4. **Submission readiness**
- Use when the user names a venue or deadline and wants a final pass for checklist, formatting, reproducibility, artifacts, and acceptance risk.
- **NeurIPS 2026**: When the user specifies NeurIPS 2026 as the target venue, use `references/neurips-2026.md` for concrete venue rules instead of browsing. Run the NeurIPS-specific submission checklist (`assets/neurips_2026_submission_checklist.md`). Verify paper checklist compliance using `assets/neurips_2026_checklist.md`. Score the paper against the NeurIPS 2026 6-point scale and early AC meta-review criteria in `references/reviewer-lens.md`.

## Build a working record before changing the paper

1. Collect what is available.
- Manuscript: PDF, DOCX, LaTeX, markdown, or pasted text.
- Structured evidence: result tables, CSVs, ablations, logs, configs, repository metadata.
- Context: venue, deadline, paper type, stage, review comments, compute limits.

2. Create a structured spec if one does not exist.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/build_paper_spec.py \
  --paper paper/paper.pdf \
  --title "Target Paper" \
  --paper-type empirical \
  --stage draft \
  --venue neurips2026 \
  --target-method "method_name" \
  --datasets cifar10 \
  --metrics accuracy,f1 \
  --primary-metric accuracy \
  --primary-dataset cifar10 \
  --output paper/paper_spec.json
```
- Fill unresolved fields before giving strong publication advice.
- Keep every headline claim anchored to a table, figure, theorem, or appendix location.

3. Diagnose the manuscript before rewriting.
- If manuscript text is available as `.tex`, `.md`, or `.txt`, run:
```bash
python /home/oai/skills/paper-improvement/scripts/paper_lint.py \
  --input manuscript/main.tex \
  --paper-type empirical \
  --venue neurips2026 \
  --output-json analysis/paper_lint.json \
  --output-md analysis/paper_lint.md
```
- Use the lint report to distinguish blocking scientific issues from polish.
- Do not stop at style feedback. Tie recommendations to specific missing evidence, weak framing, or unclear section responsibilities.

4. Build a claim-evidence table.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/evidence_matrix.py \
  --paper-spec paper/paper_spec.json \
  --runs-csv runs/results.csv \
  --output-json analysis/evidence_matrix.json \
  --output-md analysis/evidence_matrix.md \
  --output-csv analysis/evidence_matrix.csv
```
- Refuse to strengthen a claim if the evidence table marks it as unsupported, unmatched, or manual-review only.

5. Analyze results when CSVs are available.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/analyze_results.py \
  --runs-csv runs/results.csv \
  --baseline baseline \
  --output-json analysis/results_summary.json \
  --output-md analysis/results_summary.md
```
- Prefer multi-seed paired comparisons for claim-facing conclusions.
- Treat point estimates without uncertainty as weak support.

6. Gate reproducibility before endorsing strong empirical claims.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/repro_gate.py \
  --paper-spec paper/paper_spec.json \
  --paper-lint-json analysis/paper_lint.json \
  --evidence-matrix-json analysis/evidence_matrix.json \
  --output-json analysis/repro_status.json \
  --output-md analysis/repro_status.md
```
- Treat `FAIL_BLOCKED` and `FAIL_MISMATCH` as reasons to weaken claims, add caveats, or demand more evidence.

7. Generate a revision queue.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/propose_improvements.py \
  --paper-spec paper/paper_spec.json \
  --paper-lint-json analysis/paper_lint.json \
  --evidence-matrix-json analysis/evidence_matrix.json \
  --repro-status analysis/repro_status.json \
  --effort-budget-hours 24 \
  --output-jsonl analysis/proposals.jsonl \
  --output-md analysis/proposals.md
```
- Keep the queue prioritized by acceptance impact, not by convenience.

8. Plan rebuttals when reviews exist.
- Run:
```bash
python /home/oai/skills/paper-improvement/scripts/rebuttal_planner.py \
  --reviews-json reviews/reviews.json \
  --output-json analysis/rebuttal_plan.json \
  --output-md analysis/rebuttal_plan.md
```
- Answer the most decision-relevant reviewer points first.
- Pair each response with either manuscript edits, new evidence, or an explicit limitation.

## How to reason about paper quality

Use these priorities in order:

1. **Claim support**
- Check whether the main claims are actually supported by experiments, proofs, analyses, or citations.
- Downgrade novelty or performance language when support is thin.

2. **Reviewer-facing risk**
- Score the paper through the lenses in `references/reviewer-lens.md`.
- Focus on soundness, clarity, significance, originality, reproducibility, and responsible research.

3. **Narrative fit**
- Make the paper easy to summarize in one paragraph.
- Tighten the problem, gap, method, evidence, and takeaway chain.
- Remove generic hype, repeated novelty claims, and unsupported adjectives.

4. **Empirical rigor**
- Use `references/statistics.md` for comparison defaults.
- Ask for uncertainty, paired analysis, failure cases, ablations, and strong baselines before recommending stronger conclusions.

5. **Venue compliance**
- Use `references/venue-guidance.md`.
- For NeurIPS 2026, use `references/neurips-2026.md` directly — it contains embedded deadlines, formatting rules, checklist requirements, anonymization rules, and review criteria.
- For other venues, browse the official venue pages instead of relying on memory.

## Default outputs

Unless the user asks for something narrower, produce these deliverables:

1. One-paragraph verdict on the paper's current state.
2. Prioritized issues split into `blocking`, `important`, and `polish`.
3. A revision plan with concrete manuscript changes.
4. A claim-evidence table.
5. For empirical papers: an experiment and statistics plan.
6. For reviewed papers: a point-by-point rebuttal matrix.
7. For near-submission papers: a readiness checklist.

Use the exact structures in `references/output-templates.md`.

## Resource map

- `references/workflow.md`: multi-step operational flow and triage.
- `references/reviewer-lens.md`: reviewer-style scoring dimensions and failure modes.
- `references/manuscript-checklist.md`: section-by-section quality checklist.
- `references/statistics.md`: reporting and comparison defaults.
- `references/output-templates.md`: report, revision-plan, and rebuttal templates.
- `references/schemas.md`: file contracts for scripts and artifacts.
- `references/venue-guidance.md`: how to verify current venue rules.
- `assets/reproducibility_checklist.md`: final reproducibility pass.
- `assets/submission_readiness_checklist.md`: final pre-submit pass.
- `assets/reviewer_response_template.md`: response letter structure.
- `assets/data_availability_statement_template.md`: manuscript boilerplate starter.
- `assets/limitations_statement_template.md`: limitations section starter.
- `assets/artifact_manifest_template.yaml`: artifact inventory starter.
- `assets/claim_evidence_table_template.csv`: manual evidence ledger starter.
- `assets/experiment.yaml`: empirical experiment template.
- `references/neurips-2026.md`: NeurIPS 2026 venue rules, deadlines, review process, and checklist requirements.
- `assets/neurips_2026_checklist.md`: NeurIPS 2026 mandatory paper checklist template.
- `assets/neurips_2026_submission_checklist.md`: NeurIPS 2026 submission readiness checklist.

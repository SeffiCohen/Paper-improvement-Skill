#!/usr/bin/env python3
"""Generate a prioritized paper-improvement queue from diagnostics and evidence artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import load_json, write_text


def add_proposal(
    proposals: list[dict[str, Any]],
    proposal_type: str,
    title: str,
    rationale: str,
    required_changes: list[str],
    success_metric: str,
    estimated_effort_hours: float,
    risk: str,
    stop_condition: str,
    impact: float,
) -> None:
    proposals.append(
        {
            "id": f"P{len(proposals) + 1:03d}",
            "type": proposal_type,
            "title": title,
            "rationale": rationale,
            "required_changes": required_changes,
            "success_metric": success_metric,
            "estimated_effort_hours": estimated_effort_hours,
            "risk": risk,
            "stop_condition": stop_condition,
            "impact": impact,
        }
    )


def prioritize(proposals: list[dict[str, Any]], effort_budget_hours: float) -> list[dict[str, Any]]:
    for proposal in proposals:
        effort = max(float(proposal["estimated_effort_hours"]), 0.25)
        proposal["priority"] = round(float(proposal["impact"]) / effort, 3)
    proposals.sort(key=lambda item: item["priority"], reverse=True)

    cumulative = 0.0
    for proposal in proposals:
        cumulative += float(proposal["estimated_effort_hours"])
        proposal["selected_in_budget"] = cumulative <= effort_budget_hours
    return proposals


def write_jsonl(path: Path, proposals: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for proposal in proposals:
            clean = {k: v for k, v in proposal.items() if k != "impact"}
            handle.write(json.dumps(clean, ensure_ascii=True) + "\n")


def to_markdown(proposals: list[dict[str, Any]], budget: float) -> str:
    lines = [
        "# Improvement Proposals",
        "",
        f"- Effort budget (hours): {budget}",
        "",
        "| id | type | title | hours | priority | in_budget | success_metric |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for proposal in proposals:
        lines.append(
            "| {id} | {type} | {title} | {estimated_effort_hours} | {priority} | {selected_in_budget} | {success_metric} |".format(
                **proposal
            )
        )
    lines.extend([
        "",
        "## Notes",
        "- Priorities combine expected acceptance impact and estimated effort.",
        "- Fix claim support, reviewer risk, and compliance before stylistic polish.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-spec", required=True)
    parser.add_argument("--paper-lint-json", default="")
    parser.add_argument("--repro-status", default="")
    parser.add_argument("--evidence-matrix-json", default="")
    parser.add_argument("--analysis-json", default="")
    parser.add_argument("--effort-budget-hours", type=float, default=24.0)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    spec = load_json(args.paper_spec, dict)
    lint = load_json(args.paper_lint_json, dict) if args.paper_lint_json else {}
    repro = load_json(args.repro_status, dict) if args.repro_status else {}
    evidence = load_json(args.evidence_matrix_json, dict) if args.evidence_matrix_json else {}
    analysis = load_json(args.analysis_json, dict) if args.analysis_json else {}

    paper_type = str(spec.get("metadata", {}).get("paper_type", "other"))
    stage = str(spec.get("metadata", {}).get("stage", "draft"))
    baselines = spec.get("extraction", {}).get("baselines", []) or []
    signals = lint.get("signals", {})
    sections = set(lint.get("detected_sections", []))
    flags = set(repro.get("risk_flags", []))
    evidence_summary = evidence.get("summary", {})
    comparisons = analysis.get("comparisons", []) or []

    proposals: list[dict[str, Any]] = []

    if stage in {"draft", "submission", "camera-ready"} and (
        not signals.get("has_contributions_list", False) or "introduction" not in sections or signals.get("overclaim_count", 0) > 0
    ):
        add_proposal(
            proposals,
            "writing",
            "Rewrite the abstract and introduction around one clear claim chain",
            "Reviewers must be able to summarize the problem, gap, method, and evidence after one read.",
            [
                "State the problem and gap explicitly in the first paragraph of the introduction.",
                "List contributions once and keep them aligned with the results section.",
                "Scope or weaken any headline claim not directly supported by evidence.",
            ],
            "A skeptical reviewer can summarize the paper in one paragraph without guessing the contribution.",
            4.0,
            "low",
            "Stop once the abstract and introduction no longer introduce claims that the body cannot defend.",
            0.92,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and (
        evidence_summary.get("outside_tolerance", 0) > 0 or "claim_outside_tolerance" in flags
    ):
        add_proposal(
            proposals,
            "statistics",
            "Resolve or qualify claims that fall outside reproduced tolerance",
            "Claims outside tolerance threaten soundness and often dominate reviewer decisions.",
            [
                "Identify the claims whose reproduced values do not match the paper values.",
                "Either rerun the analysis, change the claim wording, or move the result to a caveated discussion.",
                "Update the abstract, introduction, and conclusions to match the defended evidence only.",
            ],
            "All numeric headline claims are either supported or explicitly qualified.",
            3.0,
            "medium",
            "Stop when no unsupported numeric claim remains in the abstract or contribution list.",
            1.0,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_statistics_language", False):
        add_proposal(
            proposals,
            "statistics",
            "Add uncertainty, paired comparisons, and robustness reporting",
            "Point estimates alone are weak support for strong empirical claims.",
            [
                "Compute intervals for the main metrics.",
                "Use paired comparisons against the strongest baseline where shared seeds exist.",
                "Report seed count and practical significance, not only p-values.",
            ],
            "The main empirical table includes intervals, seed counts, and a defensible comparison narrative.",
            3.0,
            "low",
            "Stop when the paper can justify why the main claim is robust instead of accidental.",
            0.95,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and len(baselines) < 2:
        add_proposal(
            proposals,
            "baseline",
            "Upgrade baseline coverage and justify baseline choice",
            "Weak or sparse baselines make even accurate results look unconvincing.",
            [
                "Add the strongest reproducible baseline family that a reviewer would expect.",
                "Match training budget and evaluation protocol fairly.",
                "Explain in related work and experiments why each baseline is included.",
            ],
            "The strongest nearby baseline no longer appears to be missing from the comparison.",
            6.0,
            "medium",
            "Stop if an added baseline overturns the headline claim or if additional baselines are clearly marginal.",
            0.9,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_availability_statement", False):
        add_proposal(
            proposals,
            "artifact",
            "Prepare reproducibility artifacts and availability statements",
            "Availability and artifact readiness directly affect reviewer trust and compliance risk.",
            [
                "Draft code and data availability statements.",
                "Create an artifact manifest and supplement index.",
                "Add enough appendix detail to rerun the main table or figure.",
            ],
            "A reviewer can tell where the data, code, and main-result instructions live.",
            2.0,
            "low",
            "Stop when the paper and supplement clearly explain how to access or request the artifacts.",
            0.88,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_limitations", False):
        add_proposal(
            proposals,
            "writing",
            "Write a concrete limitations section",
            "A paper that hides limitations looks less credible than one that scopes them honestly.",
            [
                "Name the strongest external-validity or evidence boundary.",
                "State at least one failure condition or dataset caveat.",
                "Tie each limitation to a future test or mitigation where possible.",
            ],
            "The limitations section reduces reviewer skepticism instead of sounding like boilerplate.",
            1.5,
            "low",
            "Stop when the limitations section names concrete boundaries rather than generic future work.",
            0.75,
        )

    if "related_work" not in sections or signals.get("citation_count", 0) < 10:
        add_proposal(
            proposals,
            "literature",
            "Refresh related work and sharpen differentiation against nearest papers",
            "Originality scores often hinge on whether the closest comparison points are acknowledged and scoped.",
            [
                "Add the most threatening recent comparison papers.",
                "Reorganize related work by comparison axes instead of chronology.",
                "Explain exactly what is different in method, setting, or evidence.",
            ],
            "The related-work section preempts the most obvious novelty objection.",
            3.5,
            "medium",
            "Stop when the reviewer can no longer ask 'How is this different from X?' as the first question.",
            0.84,
        )

    if paper_type in {"empirical", "benchmark", "resource"} and signals.get("figure_mentions", 0) + signals.get("table_mentions", 0) < 2:
        add_proposal(
            proposals,
            "figures",
            "Rebuild result presentation around question-answering tables and captions",
            "Results that are hard to read are often judged weaker than they are.",
            [
                "Ensure each table answers one specific claim or comparison question.",
                "Write self-contained captions with dataset, metric, and key takeaway.",
                "Move less important detail to appendix if the venue permits it.",
            ],
            "A reviewer can inspect the main tables and understand the claim without rereading the text.",
            2.0,
            "low",
            "Stop when every main figure or table has a clear question and takeaway.",
            0.7,
        )

    if stage == "rebuttal":
        add_proposal(
            proposals,
            "rebuttal",
            "Convert reviewer comments into a response matrix and paper diff plan",
            "Rebuttals work best when every answer points to evidence or a manuscript change.",
            [
                "Bucket reviewer issues into soundness, clarity, novelty, reproducibility, and limitations.",
                "Answer decision-relevant points first.",
                "Map each response to a concrete manuscript change.",
            ],
            "Every reviewer issue has a direct response strategy and a matching paper change or limitation statement.",
            2.5,
            "low",
            "Stop when no critical reviewer point is left without either evidence, a change, or a justified concession.",
            0.9,
        )

    if not proposals:
        add_proposal(
            proposals,
            "writing",
            "Run a final coherence and submission-readiness pass",
            "No major automated gaps were detected, so the highest-value remaining work is tightening the full manuscript story.",
            [
                "Check claim consistency across abstract, introduction, results, and conclusion.",
                "Verify venue requirements against official sources.",
                "Run the final readiness checklist and remove redundant wording.",
            ],
            "The final manuscript is internally consistent and submission-ready.",
            2.0,
            "low",
            "Stop when the submission checklist is fully satisfied.",
            0.6,
        )

    proposals = prioritize(proposals, args.effort_budget_hours)
    write_jsonl(Path(args.output_jsonl), proposals)
    write_text(args.output_md, to_markdown(proposals, args.effort_budget_hours))
    print(f"Wrote {args.output_jsonl}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Combine paper metadata, lint signals, and claim-evidence findings into a reproducibility gate verdict."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import dump_json, iso_now, load_json, write_text


def get_path(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for segment in dotted.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def is_missing(value: Any) -> bool:
    return value in (None, "", [], {})


def critical_paths_for(paper_type: str) -> list[str]:
    base = [
        "metadata.title",
        "metadata.paper_path",
        "metadata.paper_type",
        "metadata.stage",
        "extraction.problem_statement",
    ]
    if paper_type in {"empirical", "benchmark", "resource"}:
        base.extend(
            [
                "extraction.datasets",
                "extraction.metrics",
                "extraction.claims",
                "extraction.evaluation.primary_metric",
                "extraction.evaluation.primary_dataset",
                "extraction.evaluation.seed_policy",
            ]
        )
    elif paper_type == "theory":
        base.extend(["extraction.claims", "extraction.method_summary"])
    return base


def recommended_paths_for(paper_type: str) -> list[str]:
    base = ["metadata.target_method"]
    if paper_type in {"empirical", "benchmark", "resource"}:
        base.extend(
            [
                "extraction.training.optimizer",
                "extraction.training.learning_rate",
                "extraction.training.batch_size",
                "extraction.training.epochs",
                "extraction.evaluation.splits",
            ]
        )
    return base


def build_risk_flags(paper_type: str, lint: dict[str, Any] | None, evidence: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    if lint:
        signals = lint.get("signals", {})
        if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_statistics_language", False):
            flags.append("no_statistical_language_detected")
        if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_availability_statement", False):
            flags.append("no_availability_statement_detected")
        if paper_type in {"empirical", "benchmark", "resource"} and not signals.get("has_limitations", False):
            flags.append("no_limitations_detected")
        if signals.get("overclaim_count", 0) > 0:
            flags.append("potential_overclaiming_language")
    if evidence:
        summary = evidence.get("summary", {})
        if summary.get("outside_tolerance", 0) > 0:
            flags.append("claim_outside_tolerance")
        if summary.get("no_match", 0) > 0:
            flags.append("claims_without_matching_runs")
    return flags


def build_questions(missing_critical: list[str], flags: list[str], evidence: dict[str, Any] | None) -> list[str]:
    questions: list[str] = []
    for field in missing_critical:
        questions.append(f"Provide missing critical field: {field}")
    if "claim_outside_tolerance" in flags:
        questions.append("Which main claim should be weakened, repeated, or rerun because reproduced values fall outside tolerance?")
    if "claims_without_matching_runs" in flags:
        questions.append("Which claims lack direct matching runs, and what evidence source should support them instead?")
    if "no_statistical_language_detected" in flags:
        questions.append("What uncertainty or robustness analysis will support the headline empirical claims?")
    if "no_availability_statement_detected" in flags:
        questions.append("What data, code, or artifact availability statement will appear in the paper or supplement?")
    if "no_limitations_detected" in flags:
        questions.append("What concrete limitations should the paper acknowledge before submission?")
    if not questions:
        questions.append("No blocking questions. Proceed with targeted revisions and venue checks.")
    return questions


def recommended_actions(flags: list[str]) -> list[str]:
    actions: list[str] = []
    if "claim_outside_tolerance" in flags:
        actions.append("Downgrade or rerun claims outside tolerance before strengthening the abstract or introduction.")
    if "claims_without_matching_runs" in flags:
        actions.append("Add a claim-evidence mapping for claims that are qualitative or unsupported by the current result files.")
    if "no_statistical_language_detected" in flags:
        actions.append("Add multi-seed uncertainty reporting or justify why it is unnecessary for this paper.")
    if "no_availability_statement_detected" in flags:
        actions.append("Draft code and data availability statements and point to appendix or supplement artifacts.")
    if "no_limitations_detected" in flags:
        actions.append("Add a concrete limitations section tied to evidence boundaries and failure cases.")
    if "potential_overclaiming_language" in flags:
        actions.append("Replace hype-heavy novelty or performance language with scoped statements tied to explicit evidence.")
    return actions


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Reproducibility Gate Report",
        "",
        f"- Verdict: {report.get('verdict', '')}",
        "",
        "## Missing critical fields",
    ]
    lines.extend([f"- {field}" for field in report.get("missing_critical", [])] or ["- None"])
    lines.extend(["", "## Missing recommended fields"])
    lines.extend([f"- {field}" for field in report.get("missing_recommended", [])] or ["- None"])
    lines.extend(["", "## Risk flags"])
    lines.extend([f"- {flag}" for flag in report.get("risk_flags", [])] or ["- None"])
    lines.extend(["", "## Questions for human review"])
    lines.extend([f"- {item}" for item in report.get("questions_for_human", [])] or ["- None"])
    lines.extend(["", "## Recommended before submission"])
    lines.extend([f"- {item}" for item in report.get("recommended_before_submission", [])] or ["- None"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-spec", required=True)
    parser.add_argument("--paper-lint-json", default="")
    parser.add_argument("--evidence-matrix-json", default="")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    spec = load_json(args.paper_spec, dict)
    paper_type = str(spec.get("metadata", {}).get("paper_type", "other"))
    lint = load_json(args.paper_lint_json, dict) if args.paper_lint_json else None
    evidence = load_json(args.evidence_matrix_json, dict) if args.evidence_matrix_json else None

    missing_critical = [path for path in critical_paths_for(paper_type) if is_missing(get_path(spec, path))]
    missing_recommended = [path for path in recommended_paths_for(paper_type) if is_missing(get_path(spec, path))]
    flags = build_risk_flags(paper_type, lint, evidence)

    if missing_critical:
        verdict = "FAIL_BLOCKED"
    elif evidence and evidence.get("summary", {}).get("outside_tolerance", 0) > 0:
        verdict = "FAIL_MISMATCH"
    elif paper_type in {"empirical", "benchmark", "resource"} and not flags:
        verdict = "PASS_BASELINE_TOLERANCE"
    else:
        verdict = "PASS_SMOKE"

    report = {
        "verdict": verdict,
        "missing_critical": missing_critical,
        "missing_recommended": missing_recommended,
        "risk_flags": flags,
        "metric_comparison": evidence.get("summary", {}) if evidence else {},
        "questions_for_human": build_questions(missing_critical, flags, evidence),
        "recommended_before_submission": recommended_actions(flags),
        "generated_at": iso_now(),
    }

    dump_json(args.output_json, report)
    write_text(args.output_md, to_markdown(report))
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()

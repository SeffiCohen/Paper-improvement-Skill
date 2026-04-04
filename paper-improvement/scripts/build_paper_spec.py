#!/usr/bin/env python3
"""Build a normalized paper_spec.json for paper diagnosis, evidence audit, and revision planning."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import deep_merge, dump_json, iso_now, load_json, parse_csv_list, write_text

PAPER_TYPES = {"empirical", "theory", "survey", "resource", "benchmark", "other"}
STAGES = {"draft", "submission", "rebuttal", "camera-ready", "published"}

VENUE_DEFAULTS: dict[str, dict[str, Any]] = {
    "neurips2026": {
        "venue": "NeurIPS 2026",
        "deadline": "2026-05-06T23:59:00-12:00",
        "venue_config": {
            "page_limit": 9,
            "style_file": "neurips_2026.sty",
            "style_option": "default",
            "anonymized": True,
            "checklist_required": True,
            "supplementary_max_mb": 100,
            "pdf_max_mb": 50,
            "review_format": "double_blind",
            "appendix_counts_toward_limit": False,
        },
    },
}


def parse_seed_values(raw: str | None) -> list[int]:
    if not raw:
        return []
    values: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    return values


def load_list(path: str | None) -> list[Any]:
    if not path:
        return []
    data = load_json(path, list)
    return list(data)


def normalize_contributions(items: list[Any]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for idx, item in enumerate(items, start=1):
        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            cid = str(item.get("id", f"C{idx}"))
        else:
            text = str(item).strip()
            cid = f"C{idx}"
        if text:
            output.append({"id": cid, "text": text})
    return output


def normalize_claims(items: list[Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            item = {"claim_text": str(item)}
        claim = {
            "id": str(item.get("id", f"CL{idx}")),
            "claim_text": str(item.get("claim_text", "")).strip(),
            "metric": str(item.get("metric", "")).strip(),
            "dataset": str(item.get("dataset", "")).strip(),
            "reported_value": item.get("reported_value", ""),
            "anchor": str(item.get("anchor", "")).strip(),
            "claim_type": str(item.get("claim_type", "other")).strip() or "other",
            "evidence_needed": str(item.get("evidence_needed", "")).strip(),
        }
        if claim["claim_text"]:
            output.append(claim)
    return output


def normalize_string_list(items: list[Any]) -> list[str]:
    return [str(item).strip() for item in items if str(item).strip()]


def unresolved_fields(spec: dict[str, Any]) -> list[str]:
    metadata = spec.get("metadata", {})
    extraction = spec.get("extraction", {})
    training = extraction.get("training", {})
    evaluation = extraction.get("evaluation", {})
    paper_type = metadata.get("paper_type", "other")

    missing: list[str] = []

    def require(path: str, value: Any) -> None:
        if value in (None, "", [], {}):
            missing.append(path)

    require("metadata.title", metadata.get("title"))
    require("metadata.paper_path", metadata.get("paper_path"))
    require("metadata.paper_type", metadata.get("paper_type"))
    require("metadata.stage", metadata.get("stage"))
    require("extraction.problem_statement", extraction.get("problem_statement"))

    if paper_type in {"empirical", "benchmark", "resource"}:
        require("extraction.datasets", extraction.get("datasets"))
        require("extraction.metrics", extraction.get("metrics"))
        require("extraction.claims", extraction.get("claims"))
        require("extraction.evaluation.primary_metric", evaluation.get("primary_metric"))
        require("extraction.evaluation.primary_dataset", evaluation.get("primary_dataset"))
        require("extraction.evaluation.seed_policy", evaluation.get("seed_policy"))
        require("extraction.evaluation.splits", evaluation.get("splits"))
    elif paper_type == "theory":
        require("extraction.claims", extraction.get("claims"))
        require("extraction.method_summary", extraction.get("method_summary"))
    elif paper_type == "survey":
        require("extraction.contributions", extraction.get("contributions"))

    for claim in extraction.get("claims", []):
        if not claim.get("anchor"):
            missing.append(f"claim.{claim.get('id', 'unknown')}.anchor")

    for key, value in [
        ("extraction.training.optimizer", training.get("optimizer")),
        ("extraction.training.learning_rate", training.get("learning_rate")),
        ("metadata.target_method", metadata.get("target_method")),
    ]:
        if value in (None, "", [], {}):
            missing.append(key)

    # NeurIPS 2026 specific unresolved fields
    venue = metadata.get("venue", "")
    if "neurips" in venue.lower() and "2026" in venue:
        venue_config = metadata.get("venue_config", {})
        if not venue_config:
            missing.append("metadata.venue_config")
        if not metadata.get("deadline"):
            missing.append("metadata.deadline")

    seen: set[str] = set()
    ordered: list[str] = []
    for item in missing:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def build_markdown(spec: dict[str, Any]) -> str:
    metadata = spec.get("metadata", {})
    extraction = spec.get("extraction", {})
    evaluation = extraction.get("evaluation", {})
    contributions = extraction.get("contributions", [])
    claims = extraction.get("claims", [])
    unresolved = spec.get("unresolved_fields", [])
    reviewer_concerns = extraction.get("reviewer_concerns", [])

    lines = [
        "# Paper Spec Summary",
        "",
        "## Metadata",
        f"- Title: {metadata.get('title', '')}",
        f"- Paper path: {metadata.get('paper_path', '')}",
        f"- Venue: {metadata.get('venue', '')}",
        f"- Deadline: {metadata.get('deadline', '')}",
        f"- Paper type: {metadata.get('paper_type', '')}",
        f"- Stage: {metadata.get('stage', '')}",
        f"- Target method: {metadata.get('target_method', '')}",
        f"- arXiv ID: {metadata.get('arxiv_id', '')}",
        f"- DOI: {metadata.get('doi', '')}",
        f"- Code URL: {metadata.get('code_url', '')}",
        f"- Data URL: {metadata.get('data_url', '')}",
        "",
        "## Problem and method",
        f"- Problem statement: {extraction.get('problem_statement', '')}",
        f"- Method summary: {extraction.get('method_summary', '')}",
        f"- Datasets: {', '.join(extraction.get('datasets', []))}",
        f"- Metrics: {', '.join(extraction.get('metrics', []))}",
        f"- Baselines: {', '.join(extraction.get('baselines', []))}",
        f"- Primary metric: {evaluation.get('primary_metric', '')}",
        f"- Primary dataset: {evaluation.get('primary_dataset', '')}",
        "",
        "## Contributions",
    ]

    if contributions:
        lines.extend(f"- {item.get('id', '')}: {item.get('text', '')}" for item in contributions)
    else:
        lines.append("- None")

    lines.extend(["", "## Claims"])
    if claims:
        for claim in claims:
            lines.append(
                f"- {claim.get('id', '')}: {claim.get('claim_text', '')} | metric={claim.get('metric', '')} | dataset={claim.get('dataset', '')} | value={claim.get('reported_value', '')} | anchor={claim.get('anchor', '')}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Reviewer concerns"])
    if reviewer_concerns:
        lines.extend(f"- {item}" for item in reviewer_concerns)
    else:
        lines.append("- None")

    lines.extend(["", "## Unresolved fields"])
    if unresolved:
        lines.extend(f"- {item}" for item in unresolved)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Lineage",
            f"- Generated at: {spec.get('lineage', {}).get('generated_at', '')}",
            f"- Generator: {spec.get('lineage', {}).get('generator', '')}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True, help="Path to source paper or manuscript")
    parser.add_argument("--title", default="")
    parser.add_argument("--paper-id", default="")
    parser.add_argument("--arxiv-id", default="")
    parser.add_argument("--doi", default="")
    parser.add_argument("--venue", default="")
    parser.add_argument("--deadline", default="")
    parser.add_argument("--paper-type", default="empirical")
    parser.add_argument("--stage", default="draft")
    parser.add_argument("--target-method", default="")
    parser.add_argument("--code-url", default="")
    parser.add_argument("--data-url", default="")
    parser.add_argument("--problem", default="")
    parser.add_argument("--method-summary", default="")
    parser.add_argument("--datasets", default="")
    parser.add_argument("--metrics", default="")
    parser.add_argument("--baselines", default="")
    parser.add_argument("--primary-metric", default="")
    parser.add_argument("--primary-dataset", default="")
    parser.add_argument("--seed-policy", default="")
    parser.add_argument("--seed-values", default="")
    parser.add_argument("--splits", default="")
    parser.add_argument("--contributions-json", default="")
    parser.add_argument("--claims-json", default="")
    parser.add_argument("--reviewer-concerns-json", default="")
    parser.add_argument("--merge-json", action="append", default=[])
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", default="")
    args = parser.parse_args()

    paper_type = args.paper_type.strip().lower() or "other"
    stage = args.stage.strip().lower() or "draft"
    if paper_type not in PAPER_TYPES:
        raise ValueError(f"Unsupported --paper-type: {paper_type}")
    if stage not in STAGES:
        raise ValueError(f"Unsupported --stage: {stage}")

    spec: dict[str, Any] = {
        "metadata": {
            "title": args.title,
            "paper_path": str(Path(args.paper)),
            "paper_id": args.paper_id,
            "arxiv_id": args.arxiv_id,
            "doi": args.doi,
            "venue": args.venue,
            "deadline": args.deadline,
            "paper_type": paper_type,
            "stage": stage,
            "target_method": args.target_method,
            "code_url": args.code_url,
            "data_url": args.data_url,
        },
        "extraction": {
            "problem_statement": args.problem,
            "method_summary": args.method_summary,
            "contributions": normalize_contributions(load_list(args.contributions_json)),
            "datasets": parse_csv_list(args.datasets),
            "metrics": parse_csv_list(args.metrics),
            "baselines": parse_csv_list(args.baselines),
            "claims": normalize_claims(load_list(args.claims_json)),
            "training": {
                "optimizer": "",
                "learning_rate": "",
                "batch_size": "",
                "epochs": "",
                "scheduler": "",
            },
            "evaluation": {
                "primary_metric": args.primary_metric,
                "primary_dataset": args.primary_dataset,
                "seed_policy": args.seed_policy,
                "seed_values": parse_seed_values(args.seed_values),
                "splits": parse_csv_list(args.splits),
            },
            "writing_risks": [],
            "reviewer_concerns": normalize_string_list(load_list(args.reviewer_concerns_json)),
        },
        "unresolved_fields": [],
        "lineage": {"generated_at": iso_now(), "generator": "build_paper_spec.py"},
    }

    # Apply venue defaults if a known venue is specified
    venue_key = args.venue.strip().lower().replace(" ", "").replace("-", "")
    if venue_key in VENUE_DEFAULTS:
        venue_conf = VENUE_DEFAULTS[venue_key]
        if not spec["metadata"]["venue"]:
            spec["metadata"]["venue"] = venue_conf["venue"]
        if not spec["metadata"]["deadline"]:
            spec["metadata"]["deadline"] = venue_conf["deadline"]
        spec["metadata"]["venue_config"] = venue_conf.get("venue_config", {})

    for merge_file in args.merge_json:
        spec = deep_merge(spec, load_json(merge_file, dict))

    spec["unresolved_fields"] = unresolved_fields(spec)
    dump_json(args.output, spec)
    markdown_output = args.markdown_output or str(Path(args.output).with_suffix(".md"))
    write_text(markdown_output, build_markdown(spec))

    print(f"Wrote {args.output}")
    print(f"Wrote {markdown_output}")


if __name__ == "__main__":
    main()

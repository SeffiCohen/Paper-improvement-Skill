#!/usr/bin/env python3
"""Convert structured reviews into a rebuttal plan and response matrix."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import dump_json, load_json, normalize_space, write_text

CATEGORY_KEYWORDS = {
    "soundness": ["sound", "proof", "unsupported", "methodology", "unclear claim", "assumption", "validity"],
    "clarity": ["unclear", "confusing", "hard to follow", "presentation", "writing", "notation"],
    "novelty": ["novel", "original", "incremental", "prior work", "difference from", "same as"],
    "experiments": ["baseline", "experiment", "ablation", "dataset", "benchmark", "result", "evaluation"],
    "statistics": ["significant", "p-value", "interval", "variance", "seed", "robust"],
    "reproducibility": ["reproduce", "code", "data", "artifact", "availability", "details"],
    "limitations": ["limitation", "scope", "bias", "ethic", "risk", "misuse", "failure"],
}

CATEGORY_PRIORITY = {
    "soundness": 1.0,
    "experiments": 0.95,
    "statistics": 0.9,
    "novelty": 0.82,
    "reproducibility": 0.8,
    "clarity": 0.72,
    "limitations": 0.68,
    "other": 0.55,
}


def classify_issue(text: str) -> str:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "other"


def infer_needed_evidence(category: str) -> str:
    return {
        "soundness": "direct methodological clarification, proof detail, or claim weakening",
        "experiments": "new baseline, ablation, or analysis table",
        "statistics": "uncertainty or paired-comparison analysis",
        "novelty": "closest-paper comparison paragraph",
        "reproducibility": "code, data, artifact, or appendix details",
        "clarity": "rewritten section, notation cleanup, or figure/table caption revision",
        "limitations": "limitation or ethics paragraph",
        "other": "manual response",
    }[category]


def infer_action(category: str) -> str:
    return {
        "soundness": "answer directly and change the manuscript if the current text leaves room for doubt",
        "experiments": "map the issue to a concrete added experiment or explain why the current evidence is enough",
        "statistics": "add intervals, seed details, or practical-significance language",
        "novelty": "differentiate against the nearest prior work in related work and introduction",
        "reproducibility": "add availability and appendix details",
        "clarity": "rewrite the affected passage and mention the exact section changed",
        "limitations": "acknowledge the limitation explicitly and scope the claim",
        "other": "respond briefly and decide whether a paper change is needed",
    }[category]


def extract_reviews(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        reviews = payload.get("reviews", [])
        if isinstance(reviews, list):
            return [item for item in reviews if isinstance(item, dict)]
    raise ValueError("reviews json must be a list of review objects or an object with a 'reviews' list")


def extract_issue_texts(review: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in ["questions", "weaknesses"]:
        value = review.get(key, [])
        if isinstance(value, list):
            issues.extend(normalize_space(str(item)) for item in value if normalize_space(str(item)))
    if issues:
        return issues

    text = normalize_space(str(review.get("text", "") or review.get("summary", "")))
    if not text:
        return []
    parts = [normalize_space(part) for part in text.split(".")]
    return [part for part in parts if len(part.split()) >= 5][:5]


def build_plan(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    issue_index = 1
    for review in reviews:
        reviewer = str(review.get("reviewer", f"reviewer-{issue_index}"))
        score = review.get("score", "")
        for issue_text in extract_issue_texts(review):
            category = classify_issue(issue_text)
            counts[category] += 1
            rows.append(
                {
                    "issue_id": f"R{issue_index:03d}",
                    "reviewer": reviewer,
                    "score": score,
                    "category": category,
                    "priority": CATEGORY_PRIORITY[category],
                    "issue_text": issue_text,
                    "evidence_needed": infer_needed_evidence(category),
                    "recommended_action": infer_action(category),
                    "response_status": "todo",
                }
            )
            issue_index += 1
    rows.sort(key=lambda item: item["priority"], reverse=True)
    return {"rows": rows, "category_counts": dict(counts)}


def to_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Rebuttal Plan", "", "## Category counts"]
    if not payload.get("category_counts"):
        lines.append("- None")
    else:
        for category, count in payload["category_counts"].items():
            lines.append(f"- {category}: {count}")
    lines.extend(["", "## Response matrix"])
    rows = payload.get("rows", [])
    if not rows:
        lines.append("- No issues extracted.")
    else:
        lines.append("| issue_id | reviewer | category | issue | evidence_needed | recommended_action |")
        lines.append("|---|---|---|---|---|---|")
        for row in rows:
            lines.append(
                "| {issue_id} | {reviewer} | {category} | {issue_text} | {evidence_needed} | {recommended_action} |".format(
                    issue_id=row.get("issue_id", ""),
                    reviewer=str(row.get("reviewer", "")).replace("|", " "),
                    category=row.get("category", ""),
                    issue_text=str(row.get("issue_text", "")).replace("|", " "),
                    evidence_needed=str(row.get("evidence_needed", "")).replace("|", " "),
                    recommended_action=str(row.get("recommended_action", "")).replace("|", " "),
                )
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviews-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    payload = load_json(args.reviews_json, expected=(list, dict))
    reviews = extract_reviews(payload)
    plan = build_plan(reviews)
    dump_json(args.output_json, plan)
    write_text(args.output_md, to_markdown(plan))
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()

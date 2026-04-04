#!/usr/bin/env python3
"""Build a claim-evidence matrix from paper metadata and optional experiment outputs."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import dump_json, load_json, mean, numeric_or_none, write_text


def parse_runs_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"method", "dataset", "metric", "seed", "value"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
        for row in reader:
            rows.append(
                {
                    "method": row["method"].strip(),
                    "dataset": row["dataset"].strip(),
                    "metric": row["metric"].strip(),
                    "seed": int(row["seed"]),
                    "value": float(row["value"]),
                }
            )
    return rows


def aggregates_from_runs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["dataset"], row["metric"])].append(row["value"])

    output: list[dict[str, Any]] = []
    for (method, dataset, metric), values in sorted(grouped.items()):
        output.append(
            {
                "method": method,
                "dataset": dataset,
                "metric": metric,
                "mean": mean(values),
                "n": len(values),
            }
        )
    return output


def infer_required_evidence(claim: dict[str, Any]) -> str:
    claim_text = str(claim.get("claim_text", "")).lower()
    explicit = str(claim.get("evidence_needed", "")).strip()
    if explicit:
        return explicit
    if any(token in claim_text for token in ["faster", "efficient", "latency", "throughput", "memory"]):
        return "runtime or efficiency table with matching hardware and setup"
    if any(token in claim_text for token in ["robust", "generaliz", "across datasets", "stable", "seed"]):
        return "multi-seed or multi-split robustness analysis"
    if any(token in claim_text for token in ["ablation", "component", "module"]):
        return "component ablation table"
    if any(token in claim_text for token in ["state-of-the-art", "outperform", "best", "improves over"]):
        return "strong baseline comparison with uncertainty"
    if any(token in claim_text for token in ["simpler", "fewer parameter", "compact"]):
        return "parameter or complexity comparison"
    if any(token in claim_text for token in ["theorem", "proof", "guarantee"]):
        return "formal proof or theorem reference"
    return "manual review"


def build_matrix(
    spec: dict[str, Any],
    aggregates: list[dict[str, Any]],
    target_method: str,
    abs_tolerance: float,
    rel_tolerance: float,
) -> dict[str, Any]:
    aggregate_map = {
        (row["method"], row["dataset"], row["metric"]): row for row in aggregates
    }
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    for claim in spec.get("extraction", {}).get("claims", []):
        claim_id = str(claim.get("id", ""))
        claim_text = str(claim.get("claim_text", ""))
        dataset = str(claim.get("dataset", "")).strip()
        metric = str(claim.get("metric", "")).strip()
        reported_value = claim.get("reported_value", "")
        anchor = str(claim.get("anchor", "")).strip()
        required_evidence = infer_required_evidence(claim)

        row: dict[str, Any] = {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "metric": metric,
            "dataset": dataset,
            "reported_value": reported_value,
            "reproduced_value": None,
            "abs_delta": None,
            "rel_delta": None,
            "status": "manual_review",
            "required_evidence": required_evidence,
            "anchor": anchor,
        }

        numeric_reported = numeric_or_none(reported_value)
        if numeric_reported is None or not metric or not dataset or not target_method:
            row["status"] = "manual_review"
        else:
            matched = aggregate_map.get((target_method, dataset, metric))
            if not matched:
                row["status"] = "no_match"
            else:
                reproduced = float(matched["mean"])
                abs_delta = abs(reproduced - numeric_reported)
                rel_delta = abs_delta / max(abs(numeric_reported), 1e-12)
                within = abs_delta <= abs_tolerance or rel_delta <= rel_tolerance
                row.update(
                    {
                        "reproduced_value": reproduced,
                        "abs_delta": abs_delta,
                        "rel_delta": rel_delta,
                        "status": "supported" if within else "outside_tolerance",
                    }
                )
        counts[row["status"]] += 1
        rows.append(row)

    return {
        "target_method": target_method,
        "rows": rows,
        "summary": {
            "supported": counts.get("supported", 0),
            "outside_tolerance": counts.get("outside_tolerance", 0),
            "no_match": counts.get("no_match", 0),
            "manual_review": counts.get("manual_review", 0),
        },
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Claim-Evidence Matrix",
        "",
        f"- Target method: {payload.get('target_method', '')}",
        "",
        "## Summary",
    ]
    for key, value in payload.get("summary", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Rows"])
    rows = payload.get("rows", [])
    if not rows:
        lines.append("- No claims found.")
    else:
        lines.append("| claim_id | metric | dataset | reported_value | reproduced_value | status | required_evidence | anchor |")
        lines.append("|---|---|---|---:|---:|---|---|---|")
        for row in rows:
            lines.append(
                "| {claim_id} | {metric} | {dataset} | {reported_value} | {reproduced_value} | {status} | {required_evidence} | {anchor} |".format(
                    claim_id=row.get("claim_id", ""),
                    metric=row.get("metric", ""),
                    dataset=row.get("dataset", ""),
                    reported_value=row.get("reported_value", ""),
                    reproduced_value="" if row.get("reproduced_value") is None else f"{row['reproduced_value']:.6f}",
                    status=row.get("status", ""),
                    required_evidence=str(row.get("required_evidence", "")).replace("|", " "),
                    anchor=str(row.get("anchor", "")).replace("|", " "),
                )
            )
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "claim_id",
        "claim_text",
        "metric",
        "dataset",
        "reported_value",
        "reproduced_value",
        "abs_delta",
        "rel_delta",
        "status",
        "required_evidence",
        "anchor",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-spec", required=True)
    parser.add_argument("--analysis-json", default="")
    parser.add_argument("--runs-csv", default="")
    parser.add_argument("--method", default="")
    parser.add_argument("--abs-tolerance", type=float, default=0.02)
    parser.add_argument("--rel-tolerance", type=float, default=0.05)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-csv", required=True)
    args = parser.parse_args()

    spec = load_json(args.paper_spec, dict)
    target_method = args.method.strip() or str(spec.get("metadata", {}).get("target_method", "")).strip()

    if args.analysis_json:
        analysis = load_json(args.analysis_json, dict)
        aggregates = list(analysis.get("aggregates", []))
    elif args.runs_csv:
        aggregates = aggregates_from_runs(parse_runs_csv(Path(args.runs_csv)))
    else:
        aggregates = []

    payload = build_matrix(spec, aggregates, target_method, args.abs_tolerance, args.rel_tolerance)
    dump_json(args.output_json, payload)
    write_text(args.output_md, to_markdown(payload))
    write_csv(Path(args.output_csv), payload["rows"])

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_csv}")


if __name__ == "__main__":
    main()

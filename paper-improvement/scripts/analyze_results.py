#!/usr/bin/env python3
"""Aggregate experiment runs and compute comparison statistics for paper-facing claims."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import bootstrap_ci, dump_json, mean, parse_csv_list, stdev, write_text

LOWER_IS_BETTER_HINTS = {
    "loss",
    "error",
    "wer",
    "perplexity",
    "mae",
    "mse",
    "rmse",
    "latency",
    "time",
    "runtime",
    "memory",
    "params",
    "parameter_count",
}


def parse_rows(path: Path) -> list[dict[str, Any]]:
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
                    "run_id": row.get("run_id", "").strip(),
                    "split": row.get("split", "").strip(),
                    "compute_hours": float(row["compute_hours"]) if row.get("compute_hours") else None,
                }
            )
    return rows


def infer_direction(metric: str, higher_is_better: set[str], lower_is_better: set[str]) -> str:
    lowered = metric.strip().lower()
    if lowered in higher_is_better:
        return "higher"
    if lowered in lower_is_better:
        return "lower"
    for hint in LOWER_IS_BETTER_HINTS:
        if hint in lowered:
            return "lower"
    return "higher"


def aggregate(rows: list[dict[str, Any]], higher: set[str], lower: set[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["dataset"], row["metric"])].append(row["value"])

    output: list[dict[str, Any]] = []
    for (method, dataset, metric), values in sorted(grouped.items()):
        ci_low, ci_high = bootstrap_ci(values)
        output.append(
            {
                "method": method,
                "dataset": dataset,
                "metric": metric,
                "direction": infer_direction(metric, higher, lower),
                "n": len(values),
                "mean": mean(values),
                "std": stdev(values),
                "median": sorted(values)[len(values) // 2],
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    return output


def two_sided_sign_test_pvalue(pos: int, neg: int) -> float:
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    tail = 0.0
    for i in range(k + 1):
        tail += math.comb(n, i)
    return min(1.0, 2.0 * tail / (2.0**n))


def paired_deltas(rows: list[dict[str, Any]], baseline: str, higher: set[str], lower: set[str]) -> list[dict[str, Any]]:
    keyed: dict[tuple[str, str, str, int], float] = {}
    methods: set[str] = set()
    for row in rows:
        keyed[(row["dataset"], row["metric"], row["method"], row["seed"])] = row["value"]
        methods.add(row["method"])

    comparisons: list[dict[str, Any]] = []
    for method in sorted(methods):
        if method == baseline:
            continue
        group_keys = {(row["dataset"], row["metric"]) for row in rows if row["method"] in {baseline, method}}
        for dataset, metric in sorted(group_keys):
            baseline_by_seed = {
                seed: value
                for (ds, mt, mth, seed), value in keyed.items()
                if ds == dataset and mt == metric and mth == baseline
            }
            method_by_seed = {
                seed: value
                for (ds, mt, mth, seed), value in keyed.items()
                if ds == dataset and mt == metric and mth == method
            }
            shared = sorted(set(baseline_by_seed) & set(method_by_seed))
            if len(shared) < 2:
                continue

            deltas = [method_by_seed[seed] - baseline_by_seed[seed] for seed in shared]
            ci_low, ci_high = bootstrap_ci(deltas)
            positives = sum(1 for value in deltas if value > 0)
            negatives = sum(1 for value in deltas if value < 0)
            p_value = two_sided_sign_test_pvalue(positives, negatives)
            delta_std = stdev(deltas)
            standardized = mean(deltas) / delta_std if delta_std > 0 else None
            direction = infer_direction(metric, higher, lower)

            if direction == "higher":
                if ci_low > 0:
                    verdict = "better"
                elif ci_high < 0:
                    verdict = "worse"
                else:
                    verdict = "uncertain"
            else:
                if ci_high < 0:
                    verdict = "better"
                elif ci_low > 0:
                    verdict = "worse"
                else:
                    verdict = "uncertain"

            comparisons.append(
                {
                    "dataset": dataset,
                    "metric": metric,
                    "direction": direction,
                    "baseline": baseline,
                    "candidate": method,
                    "shared_seed_count": len(shared),
                    "mean_delta": mean(deltas),
                    "std_delta": delta_std,
                    "standardized_mean_delta": standardized,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p_value": p_value,
                    "verdict": verdict,
                }
            )
    return comparisons


def apply_holm(comparisons: list[dict[str, Any]], alpha: float) -> None:
    ordered = sorted(enumerate(comparisons), key=lambda item: item[1]["p_value"])
    m = len(ordered)
    reject_prefix = True
    for rank, (index, row) in enumerate(ordered, start=1):
        threshold = alpha / (m - rank + 1)
        passes = bool(row["p_value"] <= threshold) and reject_prefix
        comparisons[index]["holm_threshold"] = threshold
        comparisons[index]["holm_reject"] = passes
        if not passes:
            reject_prefix = False


def best_by_group(aggregates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in aggregates:
        grouped[(row["dataset"], row["metric"])].append(row)

    best_rows: list[dict[str, Any]] = []
    for (dataset, metric), rows in sorted(grouped.items()):
        direction = rows[0]["direction"]
        best = max(rows, key=lambda item: item["mean"]) if direction == "higher" else min(rows, key=lambda item: item["mean"])
        best_rows.append(
            {
                "dataset": dataset,
                "metric": metric,
                "direction": direction,
                "best_method": best["method"],
                "best_mean": best["mean"],
            }
        )
    return best_rows


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Experiment Analysis Summary",
        "",
        f"- Alpha: {payload.get('alpha', '')}",
        "",
        "## Aggregates",
        "| method | dataset | metric | direction | n | mean | std | ci_low | ci_high |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("aggregates", []):
        lines.append(
            "| {method} | {dataset} | {metric} | {direction} | {n} | {mean:.6f} | {std:.6f} | {ci_low:.6f} | {ci_high:.6f} |".format(**row)
        )

    lines.extend(["", "## Best by dataset and metric"])
    if not payload.get("best_by_group"):
        lines.append("- None")
    else:
        lines.append("| dataset | metric | direction | best_method | best_mean |")
        lines.append("|---|---|---|---|---:|")
        for row in payload["best_by_group"]:
            lines.append("| {dataset} | {metric} | {direction} | {best_method} | {best_mean:.6f} |".format(**row))

    lines.extend(["", "## Baseline comparisons"])
    comparisons = payload.get("comparisons", [])
    if not comparisons:
        lines.append("- No valid paired comparisons.")
    else:
        lines.append("| dataset | metric | baseline | candidate | direction | shared_seeds | mean_delta | ci_low | ci_high | verdict | p_value | holm_threshold | holm_reject |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---|")
        for row in comparisons:
            lines.append(
                "| {dataset} | {metric} | {baseline} | {candidate} | {direction} | {shared_seed_count} | {mean_delta:.6f} | {ci_low:.6f} | {ci_high:.6f} | {verdict} | {p_value:.6f} | {holm_threshold:.6f} | {holm_reject} |".format(**row)
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-csv", required=True)
    parser.add_argument("--baseline", default="")
    parser.add_argument("--higher-is-better", default="")
    parser.add_argument("--lower-is-better", default="")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    higher = {item.lower() for item in parse_csv_list(args.higher_is_better)}
    lower = {item.lower() for item in parse_csv_list(args.lower_is_better)}
    rows = parse_rows(Path(args.runs_csv))
    aggregates = aggregate(rows, higher, lower)
    comparisons: list[dict[str, Any]] = []
    if args.baseline:
        comparisons = paired_deltas(rows, args.baseline, higher, lower)
        if comparisons:
            apply_holm(comparisons, args.alpha)

    payload = {
        "aggregates": aggregates,
        "comparisons": comparisons,
        "best_by_group": best_by_group(aggregates),
        "alpha": args.alpha,
    }
    dump_json(args.output_json, payload)
    write_text(args.output_md, to_markdown(payload))
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()

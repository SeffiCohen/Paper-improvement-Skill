#!/usr/bin/env python3
"""Shared helpers for the paper-improvement skill scripts."""

from __future__ import annotations

import json
import math
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_csv_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def load_json(path: str | Path, expected: type | tuple[type, ...] | None = dict) -> Any:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if expected is not None and not isinstance(data, expected):
        if isinstance(expected, tuple):
            expected_name = ", ".join(t.__name__ for t in expected)
        else:
            expected_name = expected.__name__
        raise ValueError(f"Expected {expected_name} in {path}")
    return data


def dump_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    ensure_parent(target)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    ensure_parent(target)
    target.write_text(text, encoding="utf-8")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute mean of empty values")
    return sum(values) / len(values)


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot compute percentile of empty values")
    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]

    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_ci(
    values: list[float],
    n_boot: int = 2000,
    alpha: float = 0.05,
    rng_seed: int = 0,
) -> tuple[float, float]:
    if not values:
        raise ValueError("Cannot bootstrap empty values")

    rng = random.Random(rng_seed)
    n = len(values)
    stats: list[float] = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        stats.append(mean(sample))

    stats.sort()
    lower = percentile(stats, alpha / 2.0)
    upper = percentile(stats, 1.0 - alpha / 2.0)
    return lower, upper


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def numeric_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_key(text: str) -> str:
    lowered = normalize_space(text).lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")

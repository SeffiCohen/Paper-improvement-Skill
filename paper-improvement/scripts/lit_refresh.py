#!/usr/bin/env python3
"""Fetch and rank recent related literature from arXiv and Crossref."""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import iso_now


def http_get(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "paper-improvement-skill/2.0 (mailto:research@example.com)",
            "Accept": "application/json, application/atom+xml, text/xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - controlled URLs
        return response.read().decode("utf-8", errors="replace")


def parse_date(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def recency_score(when: datetime | None) -> float:
    if when is None:
        return 0.0
    days_old = max((datetime.now(timezone.utc) - when).days, 0)
    return 1.0 / (1.0 + days_old / 365.0)


def token_overlap_score(query: str, title: str, summary: str) -> float:
    query_tokens = {token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2}
    if not query_tokens:
        return 0.0
    haystack = set(re.findall(r"[a-z0-9]+", f"{title} {summary}".lower()))
    overlap = len(query_tokens & haystack)
    return overlap / len(query_tokens)


def clean_abstract(text: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", no_tags).strip()


def fetch_arxiv(query: str, max_results: int) -> list[dict[str, Any]]:
    encoded = urllib.parse.quote_plus(f"all:{query}")
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query={encoded}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )
    xml_text = http_get(url)
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    items: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        paper_id = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
        published_raw = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
        published = parse_date(published_raw)
        authors = [
            (author.findtext("atom:name", default="", namespaces=ns) or "").strip()
            for author in entry.findall("atom:author", ns)
        ]
        items.append(
            {
                "source": "arxiv",
                "id": paper_id,
                "title": title,
                "summary": summary,
                "authors": [author for author in authors if author],
                "published": published.isoformat() if published else "",
                "citation_count": None,
                "score": round(0.55 * recency_score(published) + 0.45 * token_overlap_score(query, title, summary), 6),
            }
        )
    return items


def fetch_crossref(query: str, max_results: int) -> list[dict[str, Any]]:
    encoded = urllib.parse.urlencode({"query": query, "rows": max_results, "sort": "published"})
    url = f"https://api.crossref.org/works?{encoded}"
    payload = json.loads(http_get(url))

    items: list[dict[str, Any]] = []
    for raw in payload.get("message", {}).get("items", []):
        title_list = raw.get("title", []) or [""]
        title = str(title_list[0]).strip()
        date_parts = (
            raw.get("issued", {}).get("date-parts")
            or raw.get("published-print", {}).get("date-parts")
            or raw.get("published-online", {}).get("date-parts")
            or []
        )
        published = None
        if date_parts and date_parts[0]:
            values = date_parts[0]
            year = values[0]
            month = values[1] if len(values) > 1 else 1
            day = values[2] if len(values) > 2 else 1
            published = datetime(year, month, day, tzinfo=timezone.utc)
        citation_count = int(raw.get("is-referenced-by-count", 0) or 0)
        citation_score = min(citation_count / 200.0, 1.0)
        authors = []
        for author in raw.get("author", [])[:10]:
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            full = " ".join(part for part in (given, family) if part)
            if full:
                authors.append(full)
        abstract = clean_abstract(raw.get("abstract", ""))
        items.append(
            {
                "source": "crossref",
                "id": raw.get("DOI", ""),
                "title": title,
                "summary": abstract,
                "authors": authors,
                "published": published.isoformat() if published else "",
                "citation_count": citation_count,
                "score": round(
                    0.35 * recency_score(published)
                    + 0.35 * citation_score
                    + 0.30 * token_overlap_score(query, title, abstract),
                    6,
                ),
            }
        )
    return items


def dedupe_rank(items: list[dict[str, Any]], limit: int, from_year: int | None) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        published = parse_date(str(item.get("published", "")))
        if from_year is not None and published is not None and published.year < from_year:
            continue
        key = (item.get("id") or item.get("title") or "").lower()
        if not key:
            continue
        existing = deduped.get(key)
        if not existing or item.get("score", 0) > existing.get("score", 0):
            deduped[key] = item
    return sorted(deduped.values(), key=lambda row: row.get("score", 0), reverse=True)[:limit]


def write_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=True) + "\n")


def write_markdown(path: Path, query: str, items: list[dict[str, Any]], warnings: list[str]) -> None:
    lines = ["# Literature Refresh", "", f"- Query: {query}", f"- Generated at: {iso_now()}", ""]
    if warnings:
        lines.append("## Warnings")
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    lines.append("## Ranked Results")
    if not items:
        lines.append("- No results")
    else:
        lines.append("| rank | source | title | published | citations | score |")
        lines.append("|---:|---|---|---|---:|---:|")
        for idx, item in enumerate(items, start=1):
            lines.append(
                "| {rank} | {source} | {title} | {published} | {citations} | {score} |".format(
                    rank=idx,
                    source=item.get("source", ""),
                    title=str(item.get("title", "")).replace("|", " "),
                    published=item.get("published", ""),
                    citations=item.get("citation_count", ""),
                    score=item.get("score", ""),
                )
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--sources", default="arxiv,crossref")
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--from-year", type=int, default=0)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    source_set = {source.strip().lower() for source in args.sources.split(",") if source.strip()}
    warnings: list[str] = []
    collected: list[dict[str, Any]] = []
    if "arxiv" in source_set:
        try:
            collected.extend(fetch_arxiv(args.query, args.max_results))
        except Exception as exc:
            warnings.append(f"arXiv fetch failed: {exc}")
    if "crossref" in source_set:
        try:
            collected.extend(fetch_crossref(args.query, args.max_results))
        except Exception as exc:
            warnings.append(f"Crossref fetch failed: {exc}")

    from_year = args.from_year if args.from_year > 0 else None
    ranked = dedupe_rank(collected, args.max_results, from_year)
    write_jsonl(Path(args.output_jsonl), ranked)
    write_markdown(Path(args.output_md), args.query, ranked, warnings)
    print(f"Wrote {args.output_jsonl}")
    print(f"Wrote {args.output_md}")
    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")


if __name__ == "__main__":
    main()

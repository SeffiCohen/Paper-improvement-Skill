#!/usr/bin/env python3
"""Lint a manuscript text file for structure, evidence signals, and paper-quality risks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from common import dump_json, normalize_space, write_text

SECTION_ALIASES = {
    "abstract": {"abstract"},
    "introduction": {"introduction", "intro"},
    "related_work": {"related work", "background", "prior work"},
    "method": {"method", "methods", "approach", "model", "algorithm"},
    "experiments": {"experiments", "experimental setup", "evaluation", "experimental results"},
    "results": {"results", "analysis", "discussion"},
    "conclusion": {"conclusion", "conclusions", "closing remarks"},
    "limitations": {"limitations", "limitation"},
    "ethics": {"ethics", "ethical considerations", "broader impact", "responsible ai"},
    "availability": {"data availability", "code availability", "availability", "reproducibility"},
    "appendix": {"appendix", "supplementary material", "supplement"},
    "references": {"references", "bibliography"},
}

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

OVERCLAIM_PATTERNS = [
    re.compile(r"\bstate[- ]of[- ]the[- ]art\b", re.IGNORECASE),
    re.compile(r"\bsota\b", re.IGNORECASE),
    re.compile(r"\bsignificant(?:ly)? outperform", re.IGNORECASE),
    re.compile(r"\bsubstantially outperform", re.IGNORECASE),
    re.compile(r"\bproves?\b", re.IGNORECASE),
]
STATISTICS_PATTERN = re.compile(
    r"confidence interval|bootstrap|p-value|standard deviation|std\.?|variance|seed|significance test",
    re.IGNORECASE,
)
AVAILABILITY_PATTERN = re.compile(
    r"data availability|code availability|github|gitlab|bitbucket|zenodo|figshare|repository|artifact",
    re.IGNORECASE,
)
CONTRIBUTIONS_PATTERN = re.compile(r"our contributions|we make the following contributions|contributions are", re.IGNORECASE)
ETHICS_PATTERN = re.compile(r"ethic|broader impact|responsible ai|fairness|bias|misuse", re.IGNORECASE)
LIMITATION_PATTERN = re.compile(r"limitation|limitations|fails to|failure case|caveat", re.IGNORECASE)

# NeurIPS 2026 specific patterns
NEURIPS_STYLE_PATTERN = re.compile(r"\\usepackage(?:\[.*?\])?\{neurips_2026\}", re.IGNORECASE)
NEURIPS_CHECKLIST_PATTERN = re.compile(
    r"\\begin\{enumerate\}.*?(?:Do the main claims|claims made in the abstract)|NeurIPS Paper Checklist|\\section\*?\{.*?[Cc]hecklist.*?\}",
    re.IGNORECASE | re.DOTALL,
)
ANONYMIZATION_VIOLATION_PATTERNS = [
    re.compile(r"\b(?:our previous work|our earlier work|our prior work|in our work)\b", re.IGNORECASE),
    re.compile(r"\\author\{[^}]+\}", re.IGNORECASE),
    re.compile(r"\\affil(?:iation)?\{[^}]+\}", re.IGNORECASE),
    re.compile(r"\\thanks\{[^}]*(?:support|fund|grant)[^}]*\}", re.IGNORECASE),
]
ERROR_BAR_PATTERN = re.compile(
    r"error bar|confidence interval|standard deviation|std dev|±|\\pm|standard error|\bCI\b|margin of error",
    re.IGNORECASE,
)


def read_input(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_latex_commands(text: str) -> str:
    text = re.sub(r"(?m)^%.*$", "", text)
    text = re.sub(r"\\label\{[^}]*\}", " ", text)
    text = re.sub(r"\\ref\{[^}]*\}", " REF ", text)
    text = re.sub(r"\\cite[t|p]?\{[^}]*\}", " CITE ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}", r" \1 ", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    return text


def extract_title(raw_text: str) -> str:
    match = re.search(r"\\title\{([^}]*)\}", raw_text)
    if match:
        return normalize_space(match.group(1))
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return normalize_space(stripped.lstrip("#"))
        words = re.findall(r"\b\w+\b", stripped)
        if 3 <= len(words) <= 24:
            return normalize_space(stripped)
        break
    return ""


def detect_headings(raw_text: str) -> list[str]:
    headings: list[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+", stripped):
            headings.append(normalize_space(re.sub(r"^#{1,6}\s+", "", stripped)))
    headings.extend(re.findall(r"\\(?:sub)*section\*?\{([^}]*)\}", raw_text))
    headings.extend(re.findall(r"\\chapter\*?\{([^}]*)\}", raw_text))
    return [normalize_space(item) for item in headings if normalize_space(item)]


def canonicalize_heading(heading: str) -> str | None:
    normalized = heading.lower().strip()
    for canonical, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return canonical
    return None


def detect_sections(raw_text: str) -> list[str]:
    detected: set[str] = set()
    for heading in detect_headings(raw_text):
        canonical = canonicalize_heading(heading)
        if canonical:
            detected.add(canonical)
    lower = raw_text.lower()
    if "\\begin{abstract}" in lower or re.search(r"(?m)^\s*abstract\s*$", lower):
        detected.add("abstract")
    return sorted(detected)


def extract_abstract(raw_text: str, cleaned_text: str) -> str:
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        return normalize_space(strip_latex_commands(match.group(1)))
    lines = raw_text.splitlines()
    abstract_started = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not abstract_started and stripped.lower() == "abstract":
            abstract_started = True
            continue
        if abstract_started:
            if re.match(r"^#{1,6}\s+", stripped) or re.match(r"\\(?:sub)*section\*?\{", stripped):
                break
            collected.append(stripped)
    if collected:
        return normalize_space(" ".join(collected))
    words = cleaned_text.split()
    return " ".join(words[:220]) if words else ""


def build_issue(issue_id: str, severity: str, category: str, message: str, evidence: str, suggested_fix: str) -> dict[str, str]:
    return {
        "id": issue_id,
        "severity": severity,
        "category": category,
        "message": message,
        "evidence": evidence,
        "suggested_fix": suggested_fix,
    }


def analyze(path: Path, paper_type: str, venue: str = "") -> dict[str, Any]:
    raw_text = read_input(path)
    cleaned_text = normalize_space(strip_latex_commands(raw_text))
    words = re.findall(r"\b\w+\b", cleaned_text)
    word_count = len(words)
    title = extract_title(raw_text)
    title_word_count = len(re.findall(r"\b\w+\b", title))
    sections = detect_sections(raw_text)
    abstract = extract_abstract(raw_text, cleaned_text)
    abstract_word_count = len(re.findall(r"\b\w+\b", abstract))

    citation_count = len(re.findall(r"\\cite[t|p]?\{", raw_text))
    citation_count += len(re.findall(r"\[[0-9,\-\s]+\]", raw_text))
    citation_count += len(re.findall(r"\([A-Z][A-Za-z'`-]+(?: et al\.)?,? \d{4}\)", raw_text))
    figure_mentions = len(re.findall(r"\\begin\{figure\}|\bfigure\b|\bfig\.\b", raw_text, re.IGNORECASE))
    table_mentions = len(re.findall(r"\\begin\{table\}|\btable\b", raw_text, re.IGNORECASE))

    signals = {
        "has_contributions_list": bool(CONTRIBUTIONS_PATTERN.search(raw_text)),
        "has_limitations": "limitations" in sections or bool(LIMITATION_PATTERN.search(raw_text)),
        "has_ethics": "ethics" in sections or bool(ETHICS_PATTERN.search(raw_text)),
        "has_availability_statement": "availability" in sections or bool(AVAILABILITY_PATTERN.search(raw_text)),
        "has_statistics_language": bool(STATISTICS_PATTERN.search(raw_text)),
        "citation_count": citation_count,
        "figure_mentions": figure_mentions,
        "table_mentions": table_mentions,
        "abstract_word_count": abstract_word_count,
        "title_word_count": title_word_count,
        "overclaim_count": sum(len(pattern.findall(raw_text)) for pattern in OVERCLAIM_PATTERNS),
    }

    issues: list[dict[str, str]] = []
    issue_index = 1

    def add(severity: str, category: str, message: str, evidence: str, fix: str) -> None:
        nonlocal issue_index
        issues.append(build_issue(f"L{issue_index:03d}", severity, category, message, evidence, fix))
        issue_index += 1

    required_sections = ["abstract", "introduction", "conclusion"]
    if paper_type in {"empirical", "benchmark", "resource"}:
        required_sections.extend(["method", "experiments", "results", "related_work"])
    for section in required_sections:
        if section not in sections:
            severity = "high" if section in {"abstract", "introduction", "method", "experiments", "results"} else "medium"
            add(
                severity,
                "structure",
                f"No explicit {section.replace('_', ' ')} section was detected.",
                f"Detected sections: {', '.join(sections) if sections else 'none'}.",
                f"Add a clearly labeled {section.replace('_', ' ')} section or make the equivalent structure obvious.",
            )

    if title_word_count and title_word_count > 20:
        add("low", "writing", "The title appears long and may be carrying too many claims.", f"Title word count: {title_word_count}.", "Shorten the title and keep only the core problem and contribution signal.")
    elif title_word_count and title_word_count < 4:
        add("low", "writing", "The title appears unusually short and may be underspecified.", f"Title word count: {title_word_count}.", "Make the title more informative about the problem and contribution.")

    if abstract_word_count < 100:
        add("medium", "writing", "The abstract appears short and may under-specify evidence or scope.", f"Abstract word count: {abstract_word_count}.", "Add problem setting, method identity, evidence, and one scoped takeaway to the abstract.")
    elif abstract_word_count > 280:
        add("low", "writing", "The abstract appears long and may bury the key message.", f"Abstract word count: {abstract_word_count}.", "Compress the abstract around problem, gap, method, evidence, and takeaway.")

    if not signals["has_contributions_list"]:
        add("medium", "claims", "No explicit contribution list was detected.", "No phrase like 'our contributions' was found.", "State the contributions once, clearly and consistently, preferably in the introduction.")

    if paper_type in {"empirical", "benchmark", "resource"} and not signals["has_statistics_language"]:
        add("high", "statistics", "No clear statistical or robustness language was detected.", "No seed, interval, bootstrap, variance, or significance language was found.", "Add uncertainty reporting, seed policy, and a brief statistical analysis plan for claim-facing results.")

    if paper_type in {"empirical", "benchmark", "resource"} and not signals["has_availability_statement"]:
        add("medium", "reproducibility", "No explicit data, code, or artifact availability signal was detected.", "No availability section or repository-style language was found.", "Add a data or code availability statement and point to appendix or supplement for reproduction details.")

    if paper_type in {"empirical", "benchmark", "resource"} and not signals["has_limitations"]:
        add("medium", "claims", "No explicit limitations discussion was detected.", "No limitations section or limitation language was found.", "Add a specific limitations paragraph tied to scope, evidence gaps, and failure conditions.")

    if paper_type in {"empirical", "benchmark", "resource"} and not signals["has_ethics"]:
        add("low", "claims", "No explicit ethics, broader-impact, or responsible-use discussion was detected.", "No ethics-style language was found.", "Add a short, specific discussion if the task, data, or deployment context warrants it or if the venue expects it.")

    if word_count > 1800 and citation_count < 10:
        add("medium", "literature", "The citation density appears low for the manuscript length.", f"Word count: {word_count}; citation count: {citation_count}.", "Check whether the closest prior work and the most dangerous comparisons are adequately cited.")

    if paper_type in {"empirical", "benchmark", "resource"} and figure_mentions == 0 and table_mentions == 0:
        add("low", "presentation", "No figure or table mentions were detected in an empirical manuscript.", "No figure or table markers were found.", "Ensure that the main quantitative claims are supported by clearly referenced tables or figures.")

    if signals["overclaim_count"] > 0:
        add("medium", "claims", "Potential overclaiming language was detected.", f"Overclaim matches: {signals['overclaim_count']}.", "Replace hype-heavy wording with scoped claims tied to explicit evidence or uncertainty.")

    # Run venue-specific lint rules
    if venue == "neurips2026":
        issues.extend(neurips_2026_lint(raw_text, cleaned_text, paper_type, sections, signals, word_count))

    issues.sort(key=lambda item: (SEVERITY_ORDER[item["severity"]], item["id"]))
    return {
        "input_path": str(path),
        "paper_type": paper_type,
        "venue": venue,
        "title": title,
        "word_count": word_count,
        "detected_sections": sections,
        "signals": signals,
        "issues": issues,
    }


def neurips_2026_lint(raw_text: str, cleaned_text: str, paper_type: str, sections: list[str], signals: dict[str, Any], word_count: int) -> list[dict[str, str]]:
    """Additional lint rules specific to NeurIPS 2026 submissions."""
    issues: list[dict[str, str]] = []
    issue_index = 900

    def add(severity: str, category: str, message: str, evidence: str, fix: str) -> None:
        nonlocal issue_index
        issues.append(build_issue(f"N{issue_index - 899:03d}", severity, category, message, evidence, fix))
        issue_index += 1

    # Check for neurips_2026 style file
    if not NEURIPS_STYLE_PATTERN.search(raw_text):
        add(
            "high",
            "formatting",
            "NeurIPS 2026 style file not detected. Submissions must use neurips_2026.sty.",
            "No \\usepackage{neurips_2026} found.",
            "Add \\usepackage[default]{neurips_2026} to the preamble. Do not use previous year style files.",
        )

    # Check for mandatory paper checklist
    if not NEURIPS_CHECKLIST_PATTERN.search(raw_text):
        add(
            "high",
            "compliance",
            "NeurIPS paper checklist not detected. Papers missing the checklist will be desk rejected.",
            "No checklist section or checklist markers found in the manuscript.",
            "Append the mandatory NeurIPS paper checklist after any technical appendices. Use assets/neurips_2026_checklist.md as a template.",
        )

    # Check for anonymization violations
    for pattern in ANONYMIZATION_VIOLATION_PATTERNS:
        matches = pattern.findall(raw_text)
        if matches:
            sample = matches[0] if isinstance(matches[0], str) else matches[0][0] if matches[0] else ""
            add(
                "high",
                "anonymization",
                "Potential anonymization violation detected. NeurIPS uses double-blind review.",
                f"Found: '{sample[:80]}'",
                "Remove author names, affiliations, and acknowledgments. Use third-person for self-citations (e.g., 'Smith et al. [1]' not 'our previous work [1]').",
            )

    # Check for limitations section (strongly encouraged for NeurIPS 2026)
    if "limitations" not in sections and not LIMITATION_PATTERN.search(raw_text):
        add(
            "high",
            "compliance",
            "No Limitations section detected. NeurIPS 2026 strongly encourages a separate Limitations section.",
            "No limitations heading or limitation language found.",
            "Add a dedicated Limitations section discussing strong assumptions, scope of claims, and conditions where the method may underperform.",
        )

    # Check for broader impact / societal impact discussion
    if not signals.get("has_ethics") and not ETHICS_PATTERN.search(raw_text):
        add(
            "medium",
            "compliance",
            "No broader societal impact discussion detected. NeurIPS 2026 requires this to be addressed somewhere in the paper.",
            "No ethics, broader impact, or societal impact language found.",
            "Discuss potential negative societal impacts somewhere in the paper (intro, conclusion, supplementary, or a dedicated section).",
        )

    # Page estimate: ~250 words per page for LaTeX with figures
    estimated_pages = word_count / 250
    if estimated_pages > 11:
        add(
            "medium",
            "formatting",
            f"Word count suggests the paper may exceed the 9-page content limit.",
            f"Estimated ~{estimated_pages:.0f} pages based on {word_count} words (~250 words/page with figures).",
            "Verify the compiled PDF is within 9 content pages. Move supporting details to the appendix.",
        )

    # Check for error bars / uncertainty in empirical papers
    if paper_type in {"empirical", "benchmark", "resource"}:
        if not ERROR_BAR_PATTERN.search(raw_text) and not signals.get("has_statistics_language"):
            add(
                "high",
                "statistics",
                "No error bars or uncertainty reporting detected. NeurIPS 2026 checklist requires reporting error bars for experiments.",
                "No ±, CI, standard deviation, or error bar language found.",
                "Report error bars, confidence intervals, or significance tests for all main results. State the number of seeds/runs.",
            )

    return issues


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Paper Lint Report",
        "",
        f"- Input: {report.get('input_path', '')}",
        f"- Paper type: {report.get('paper_type', '')}",
        f"- Title: {report.get('title', '')}",
        f"- Word count: {report.get('word_count', 0)}",
        f"- Sections: {', '.join(report.get('detected_sections', [])) or 'none'}",
        "",
        "## Signals",
    ]
    signals = report.get("signals", {})
    for key in [
        "has_contributions_list",
        "has_limitations",
        "has_ethics",
        "has_availability_statement",
        "has_statistics_language",
        "citation_count",
        "figure_mentions",
        "table_mentions",
        "abstract_word_count",
        "title_word_count",
        "overclaim_count",
    ]:
        lines.append(f"- {key}: {signals.get(key, '')}")

    lines.extend(["", "## Issues"])
    issues = report.get("issues", [])
    if not issues:
        lines.append("- No major issues detected by the lint rules.")
    else:
        lines.append("| id | severity | category | message | evidence | suggested_fix |")
        lines.append("|---|---|---|---|---|---|")
        for item in issues:
            lines.append(
                "| {id} | {severity} | {category} | {message} | {evidence} | {suggested_fix} |".format(
                    id=item.get("id", ""),
                    severity=item.get("severity", ""),
                    category=item.get("category", ""),
                    message=item.get("message", "").replace("|", " "),
                    evidence=item.get("evidence", "").replace("|", " "),
                    suggested_fix=item.get("suggested_fix", "").replace("|", " "),
                )
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--paper-type", default="empirical")
    parser.add_argument("--venue", default="", help="Target venue for venue-specific checks (e.g., neurips2026)")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    report = analyze(Path(args.input), args.paper_type.strip().lower() or "empirical", args.venue.strip().lower())
    dump_json(args.output_json, report)
    write_text(args.output_md, to_markdown(report))
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()

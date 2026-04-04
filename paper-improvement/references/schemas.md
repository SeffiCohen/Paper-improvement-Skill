# Schemas Reference

## paper_spec.json

```json
{
  "metadata": {
    "title": "",
    "paper_path": "",
    "paper_id": "",
    "arxiv_id": "",
    "doi": "",
    "venue": "",
    "deadline": "",
    "paper_type": "empirical|theory|survey|resource|benchmark|other",
    "stage": "draft|submission|rebuttal|camera-ready|published",
    "target_method": "",
    "code_url": "",
    "data_url": ""
  },
  "extraction": {
    "problem_statement": "",
    "method_summary": "",
    "contributions": [{"id": "C1", "text": "..."}],
    "datasets": ["..."],
    "metrics": ["..."],
    "baselines": ["..."],
    "claims": [
      {
        "id": "CL1",
        "claim_text": "...",
        "metric": "",
        "dataset": "",
        "reported_value": 0.0,
        "anchor": "table 2",
        "claim_type": "performance|efficiency|robustness|analysis|theory|other",
        "evidence_needed": ""
      }
    ],
    "training": {
      "optimizer": "",
      "learning_rate": "",
      "batch_size": "",
      "epochs": "",
      "scheduler": ""
    },
    "evaluation": {
      "primary_metric": "",
      "primary_dataset": "",
      "seed_policy": "",
      "seed_values": [0, 1, 2],
      "splits": ["train", "val", "test"]
    },
    "writing_risks": [],
    "reviewer_concerns": []
  },
  "unresolved_fields": ["..."],
  "lineage": {
    "generated_at": "iso-datetime",
    "generator": "build_paper_spec.py"
  }
}
```

## paper_lint.json

```json
{
  "input_path": "",
  "paper_type": "empirical",
  "word_count": 0,
  "detected_sections": ["abstract", "introduction"],
  "signals": {
    "has_contributions_list": false,
    "has_limitations": false,
    "has_ethics": false,
    "has_availability_statement": false,
    "has_statistics_language": false,
    "citation_count": 0,
    "figure_mentions": 0,
    "table_mentions": 0,
    "abstract_word_count": 0,
    "title_word_count": 0
  },
  "issues": [
    {
      "id": "L001",
      "severity": "high|medium|low",
      "category": "structure|claims|reproducibility|statistics|writing",
      "message": "",
      "evidence": "",
      "suggested_fix": ""
    }
  ]
}
```

## analysis summary json

`analyze_results.py` emits:
- `aggregates`: per method / dataset / metric rows with mean and intervals
- `comparisons`: paired baseline comparisons with deltas, intervals, p-values, and Holm outputs
- `best_by_group`: best method per dataset / metric under the declared direction
- `alpha`

## evidence_matrix.json

```json
{
  "target_method": "",
  "rows": [
    {
      "claim_id": "CL1",
      "claim_text": "",
      "metric": "",
      "dataset": "",
      "reported_value": 0.0,
      "reproduced_value": 0.0,
      "abs_delta": 0.0,
      "rel_delta": 0.0,
      "status": "supported|outside_tolerance|no_match|manual_review",
      "required_evidence": "",
      "anchor": ""
    }
  ],
  "summary": {
    "supported": 0,
    "outside_tolerance": 0,
    "no_match": 0,
    "manual_review": 0
  }
}
```

## repro_status.json

```json
{
  "verdict": "PASS_SMOKE|PASS_BASELINE_TOLERANCE|FAIL_BLOCKED|FAIL_MISMATCH",
  "missing_critical": [],
  "missing_recommended": [],
  "risk_flags": [],
  "metric_comparison": {},
  "questions_for_human": [],
  "recommended_before_submission": [],
  "generated_at": "iso-datetime"
}
```

## proposals.jsonl

Each line is one proposal:
- `id`
- `type` = `writing|literature|baseline|ablation|statistics|robustness|artifact|rebuttal|figures`
- `title`
- `rationale`
- `required_changes`
- `success_metric`
- `estimated_effort_hours`
- `risk`
- `stop_condition`
- `priority`
- `selected_in_budget`

## reviews.json

Accept either:
- a list of review objects, or
- an object with a `reviews` list

Each review object may contain:
- `reviewer`
- `score`
- `summary`
- `questions` (list)
- `weaknesses` (list)
- `text`

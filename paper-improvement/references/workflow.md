# Workflow Reference

## Operating principle

Improve the paper in the smallest number of changes that materially increase acceptance odds.

Always separate:
- scientific risk: unsupported or ambiguous claims
- reviewer risk: predictable objections on soundness, clarity, novelty, or significance
- compliance risk: missing required statements, artifacts, or venue-specific rules
- polish risk: writing, formatting, and presentation issues that matter only after the above are handled

## Decision tree

1. **Only manuscript text is available**
- Run draft diagnosis.
- Build a structured claim list and identify unsupported or vague statements.
- Rewrite sections only after the risk list is clear.

2. **Manuscript plus results or repo evidence is available**
- Run draft diagnosis first.
- Then run claim-evidence audit and results analysis.
- Add experiments, ablations, statistics, or caveats before making prose more assertive.

3. **Reviewer comments are available**
- Convert reviews into an issue matrix.
- Group issues into: fix in paper, answer with existing evidence, answer with new analysis, or concede as limitation.
- Prioritize points that could change the decision.

4. **Venue and deadline are available**
- Capture exact venue rules from official sources.
- Check page limits, anonymity, checklist requirements, supplement rules, and artifact expectations.
- Convert these into a final readiness list.

## Recommended sequence

1. Intake
- Record venue, stage, paper type, target method, datasets, metrics, and headline claims.
- Build or refresh `paper_spec.json`.

2. Manuscript diagnosis
- Run `paper_lint.py` on `.tex`, `.md`, or `.txt` sources when possible.
- Use the lint report to detect missing sections, overclaiming, weak availability signals, and poor experimental framing.

3. Claim-evidence audit
- Use `evidence_matrix.py` to map each claim to actual evidence.
- Mark each claim as `supported`, `outside_tolerance`, `no_match`, or `manual_review`.

4. Experimental and statistical audit
- Use `analyze_results.py` for multi-seed summaries and paired deltas.
- Use `repro_gate.py` to combine missing metadata, manuscript gaps, and evidence mismatches.

5. Literature and positioning refresh
- Check recent official proceedings, preprints, or primary sources.
- Update the paper's comparative framing only when the additional papers materially change novelty or baseline expectations.

6. Revision planning
- Convert findings into a ranked queue.
- Prefer changes that improve both scientific quality and reviewer interpretation.

7. Rewrite and package
- Rewrite the abstract, introduction, related work, method framing, and results discussion only after the evidence picture is stable.
- Finish with the reproducibility and submission readiness checklists.

## Red-flag triage order

1. Unsupported main claim
2. Missing or weak baselines
3. No uncertainty or seed robustness for empirical results
4. Novelty claim not differentiated from closest prior work
5. Missing limitations, ethics, or responsible-use discussion when the venue expects it
6. Missing data, code, or artifact availability plan
7. Unclear contribution list or problem statement
8. Polished writing over unstable evidence

## Rewrite policy

- Tie every major recommendation to a section, claim, figure, table, or reviewer point.
- Prefer scoped claims over broad marketing language.
- Replace vague novelty statements with exact differentiators.
- Move details into appendix or supplement only if the venue permits it and the main story remains self-contained.
- Never claim significance without statistical or methodological support.

## Escalation points

Require the user to make a scientific choice when any of the following occur:
- the main claim is unsupported and cannot be fixed with writing alone
- the strongest baseline changes the headline conclusion
- the venue rules conflict with the current paper structure or supplement strategy
- additional experiments would materially change the claims but exceed the user's budget or deadline

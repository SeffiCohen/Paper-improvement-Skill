# Output Templates

Use these exact structures unless the user asks for a different format.

## Diagnostic report

```markdown
# Paper diagnosis

## Verdict
[One paragraph on current readiness, strongest asset, and biggest acceptance risk.]

## Blocking issues
1. [Issue] - [why it matters] - [minimum fix]
2. ...

## Important issues
1. ...

## Polish
1. ...

## Claim-evidence table
| claim | current support | risk | action |
|---|---|---|---|
| ... | ... | ... | ... |

## Revision plan
1. [section or artifact] -> [specific change] -> [expected reviewer impact]
2. ...

## Experiment and statistics plan
- [new baseline, ablation, robustness run, or uncertainty analysis]
- [stop condition]
- [expected decision impact]

## Submission readiness
- [required statements, artifacts, and venue checks still missing]
```

## Rebuttal matrix

```markdown
# Rebuttal plan

## Global strategy
[Two to four sentences on what to fix in the paper, what to answer with existing evidence, and what to concede as limitation.]

| reviewer | issue | category | response strategy | evidence needed | manuscript change |
|---|---|---|---|---|---|
| R1 | ... | soundness | ... | ... | ... |
```

## Review response draft

```markdown
We thank the reviewers for the careful reading and constructive feedback.

### Reviewer 1
1. [Issue]
Response: [direct answer]
Change in paper: [section, table, or appendix update]

### Reviewer 2
...
```

## Final readiness checklist

```markdown
# Final readiness

## Must-fix before submission
- [ ] ...
- [ ] ...

## Should-fix if time permits
- [ ] ...

## Evidence status
- headline claim: [supported / needs work]
- baseline coverage: [adequate / weak]
- uncertainty reporting: [adequate / weak]
- artifact readiness: [adequate / weak]
```

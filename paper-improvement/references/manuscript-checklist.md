# Manuscript Checklist

## Title and abstract

Expect:
- clear problem setting
- method identity
- concrete evidence or result
- scoped takeaway

Repair when:
- the title is vague, overloaded, or hype-heavy
- the abstract spends most of its space on motivation
- the abstract claims significance without evidence

## Introduction

Expect:
- problem and practical or scientific gap
- why existing work is insufficient
- what the paper contributes
- why the evidence matters

Repair when:
- contributions are buried or repeated inconsistently
- novelty is asserted before prior work is framed
- readers cannot tell whether the contribution is method, benchmark, dataset, or analysis

## Related work

Expect:
- comparisons organized by axes that matter to the paper
- closest threatening baselines discussed directly
- explicit differentiation, not a literature laundry list

Repair when:
- the section reads as summary without comparison
- the most relevant papers are missing
- the paper avoids the strongest comparison points

## Method

Expect:
- assumptions, design choices, and objective clearly stated
- enough detail to understand what changed relative to prior work
- enough implementation detail to reproduce the core method or proof

Repair when:
- method is all notation and no intuition
- intuition is all prose and no mechanism
- the method's novelty cannot be isolated

## Experiments and evaluation

Expect:
- datasets, metrics, splits, and protocol
- fair baseline selection
- ablations or analyses for multi-component methods
- robustness, uncertainty, or confidence intervals when empirical claims are central

Repair when:
- baselines are outdated or mismatched
- no variance or seed discussion appears
- compute cost, efficiency, or hardware assumptions are hidden despite relevant claims

## Results and discussion

Expect:
- each table or figure answers a question
- quantitative results are interpreted, not just restated
- failure cases and caveats appear where they matter

Repair when:
- the paper lists numbers without meaning
- the results section overclaims from one benchmark or one seed group
- negative results or caveats are moved out of sight

## Conclusion, limitations, and ethics

Expect:
- conclusion closes the argument, not just repeats it
- limitations are concrete and decision-relevant
- ethics or responsible-use discussion is specific when the problem or data warrants it

Repair when:
- limitations are generic
- risks are framed only as boilerplate
- the conclusion makes broader claims than the body supports

## Reproducibility and artifact readiness

Expect:
- data, code, and environment availability plan
- appendix or supplement with implementation details
- clear claim-to-evidence traceability

Repair when:
- readers cannot tell how to rerun the main result
- no data or code availability statement exists
- the supplement is a dump rather than a navigable artifact

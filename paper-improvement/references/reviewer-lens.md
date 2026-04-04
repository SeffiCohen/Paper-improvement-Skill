# Reviewer Lens

Use this file to simulate how reviewers are likely to judge the paper.

## Soundness

Check:
- are the central claims explicit
- is the methodology appropriate for the question being asked
- are experiments, analyses, or proofs sufficient for the strongest claims
- are baselines fair and current enough
- are evaluation details complete enough to reproduce the conclusions

Common failure modes:
- claims stronger than the evidence
- weak or mismatched baselines
- no ablations for multi-component methods
- no uncertainty, seeds, or error analysis
- selective reporting or missing implementation details

## Presentation and clarity

Check:
- can a reviewer summarize the problem, gap, method, and result after one read
- does each section have a distinct job
- do tables and figures answer specific questions
- are contributions stated once, clearly, and consistently

Common failure modes:
- abstract is generic or all-motivation
- introduction mixes motivation, related work, and contributions without a clean arc
- method section describes operations without assumptions or design rationale
- results section lists numbers without interpretation

## Significance

Check:
- is the paper solving a problem that matters to the field
- do the gains or insights matter beyond one narrow benchmark
- does the work change what researchers should believe or do

Common failure modes:
- technically correct but too incremental for the venue
- no explanation of why the result matters
- gains are too small or fragile to support a strong contribution claim

## Originality

Check:
- is the closest prior work identified
- is the difference precise rather than rhetorical
- is the claimed contribution methodological, empirical, dataset-related, theoretical, or analytic

Common failure modes:
- novelty is described with adjectives instead of contrasts
- related work omits the most dangerous comparison points
- the paper overstates independence from prior methods

## Reproducibility

Check:
- are datasets, splits, metrics, and preprocessing stated
- are seeds, uncertainty, and environment assumptions reported
- is there a code, artifact, or availability plan
- do appendix and supplement carry the details needed to reproduce the paper

Common failure modes:
- hidden preprocessing or unclear split policy
- missing code or availability statement
- only point estimates reported
- incomplete details for tuning, early stopping, or selection

## Responsible research and limitations

Check:
- are limitations explicit and specific
- are risks, biases, misuse, or external validity concerns addressed when relevant
- are failure cases acknowledged

Common failure modes:
- generic one-sentence limitations paragraph
- no discussion of dataset bias or deployment caveats
- ethical language that is disconnected from the actual method or data

## How to use the lens

When critiquing the paper:
1. write 1-2 sentences on each dimension
2. name the highest-risk weakness for that dimension
3. propose the smallest change that would materially improve the score
4. distinguish what can be fixed by writing from what requires new evidence

## Typical high-value reviewer questions

- What is the single strongest piece of evidence for the headline claim?
- Which closest baseline or prior method would most threaten the conclusion if included?
- What exact part of the method is new, and what evidence isolates its contribution?
- How robust is the result to seeds, splits, or tuning choices?
- What limitation would a skeptical reader notice first?

## NeurIPS 2026 scoring scale

Map your assessment to the official NeurIPS 2026 6-point scale:

| Score | Label | What it means in practice |
|---|---|---|
| 6 | Strong Accept | Technically flawless. Groundbreaking contribution. Among the top papers at the conference. All six dimensions are strong. |
| 5 | Accept | Technically solid with high impact. Minor weaknesses exist but do not undermine the contribution. Most dimensions score well. |
| 4 | Borderline Accept | Reasons to accept slightly outweigh reasons to reject. The paper is above average but has noticeable gaps in one or two dimensions. A strong rebuttal could move it to Accept. |
| 3 | Borderline Reject | Reasons to reject slightly outweigh reasons to accept. The paper has potential but significant issues in soundness, clarity, or significance. Rebuttal alone is unlikely to fully resolve concerns. |
| 2 | Reject | Clear technical flaws, weak evaluation, inadequate reproducibility, or unaddressed ethical concerns. Multiple dimensions are weak. |

When scoring a paper during diagnosis, estimate which bucket it falls into and identify the smallest set of changes that would move it up one level.

## NeurIPS 2026 early AC meta-review pilot

Starting in 2026, Area Chairs provide an initial meta-review **before** the author rebuttal period. This changes the review dynamics:

### What the early meta-review does
- Synthesizes the most important issues raised across individual reviews.
- Identifies whether reviewers agree or disagree on key points.
- Is visible to both authors and reviewers before rebuttal.
- Helps authors focus their response on the 2–3 issues most likely to determine the decision.

### How to prepare for it
When diagnosing a paper, anticipate the AC synthesis by:

1. **Pre-identify the AC summary**: Write one paragraph that an AC would use to describe the paper's contribution, strengths, and weaknesses. If this paragraph is hard to write, the paper's narrative needs tightening.

2. **Flag consensus risks**: Identify issues that multiple reviewers would independently raise. These are the issues ACs will highlight. Common consensus risks:
   - Weak or missing baselines
   - Claims stronger than evidence
   - Missing ablations for multi-component methods
   - No uncertainty reporting for empirical results
   - Vague or missing limitations

3. **Flag disagreement risks**: Identify aspects where reviewers might split (e.g., novelty assessment, significance of the problem). ACs will need to adjudicate these, so the paper should make its case clearly.

4. **Structure for AC readability**: Ensure the paper can be skimmed by an AC who reads the abstract, introduction, contribution list, main results table, and conclusion. If the contribution is not clear from these sections alone, the framing needs work.

5. **Prepare rebuttal focus areas**: Before submission, list the top 3–5 issues an AC meta-review would raise. For each, either fix it in the paper or prepare a rebuttal argument with supporting evidence.

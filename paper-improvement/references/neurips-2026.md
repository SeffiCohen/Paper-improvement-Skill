# NeurIPS 2026 — Venue Reference

Use this file instead of browsing when preparing a manuscript for the Fortieth Annual Conference on Neural Information Processing Systems (NeurIPS 2026).

## Key dates

| Milestone | Date |
|---|---|
| Submission portal opens | April 5, 2026 |
| Abstract submission deadline | May 4, 2026 (AOE) |
| Full paper + supplementary deadline | May 6, 2026 (AOE) |
| Conference | December 6–12, 2026 |
| Venue | International Convention Centre, Sydney, Australia |

All authors must have an OpenReview profile at time of submission.

## Scope and topics

NeurIPS is an interdisciplinary conference covering deep learning, generative AI, core machine learning, neuroscience, statistics, optimization, computer vision, natural language processing, life sciences, natural sciences, social sciences, and adjacent fields. Interdisciplinary work that does not fit neatly into one category is welcome. In-depth analysis of existing methods that provides new insight into their limitations or behavior beyond the original scope is also encouraged.

## Tracks

The conference has separate tracks with distinct calls, portals, and potentially different timelines:
- **Main Track** (this reference)
- **Evaluations & Datasets Track**
- **Position Papers Track**

## Formatting requirements

### Template
- LaTeX only. Use `neurips_2026.sty` with the `default` option for Main Track submissions. Microsoft Word is not accepted.
- Do not use previous year style files.
- Do not modify margins, font sizes, or spacing. Style violations may result in desk rejection.

### Page limits
- **Main body**: 9 content pages maximum. Figures and tables count toward this limit.
- **References**: Do not count toward the page limit.
- **Technical appendices**: Do not count toward the page limit. No page limit on appendices.
- **Paper checklist**: Does not count toward the page limit. Mandatory.

### PDF structure
A single PDF file must contain, in this order:
1. The submitted paper (up to 9 content pages)
2. Optional technical appendices (proofs, derivations, additional results)
3. The NeurIPS paper checklist (mandatory)

Maximum PDF file size: 50 MB.

### Supplementary material
- Separate ZIP file up to 100 MB for code, data, videos, or other artifacts.
- Must be anonymized.
- Must directly support the submission content.

### Citations
- Author/year or numeric style, as long as it is internally consistent.
- Any reference format is acceptable if used consistently throughout.

## Double-blind anonymization

All submissions must be anonymized. This applies to the paper, supplementary material, and any linked code or artifacts.

### Rules
- Remove author names, affiliations, acknowledgments, and funding details.
- Anonymize self-citations: write "In the previous work of Smith et al. [1]..." rather than "In our previous work [1]..."
- Do not include links to non-anonymized repositories or personal pages.
- Supplementary code must be anonymized (strip author metadata, personal paths, etc.).

### What is allowed
- Citing your own prior work in the third person.
- Submitting to non-archival workshops concurrently.
- Posting to arXiv (but do not cite the arXiv version in a way that breaks anonymity).

## Dual submission policy

- Any overlapping archival submission (conference or journal) by an overlapping set of authors is treated as prior work for the entire duration of the NeurIPS review period.
- Non-archival workshop submissions are permitted.
- Violation of the dual submission policy is grounds for desk rejection at any point during review or program building.

## Mandatory paper checklist

Papers not including the NeurIPS paper checklist will be desk rejected. The checklist is appended after any technical appendices in the same PDF.

Answer each item: **Yes**, **No**, or **NA**. Optionally add a 1–2 sentence justification. Answering "No" is acceptable with proper justification and is not grounds for rejection.

### Section 1 — For all authors

1a. Do the main claims made in the abstract and introduction accurately reflect the paper's contributions and scope?
- Claims should match theoretical and experimental results in terms of generalizability.

1b. Did you describe the limitations of your work?
- Create a separate "Limitations" section. Discuss strong assumptions, robustness to violations, scope of claims (e.g., tested on few datasets, few runs).

1c. Did you discuss any potential negative societal impacts of your work?
- Not required as a standalone "Broader Impacts" section, but negative impacts must be addressed somewhere (intro, conclusion, supplemental, etc.).
- Examples: malicious/unintended uses, fairness, privacy, security considerations.

1d. Have you read the ethics review guidelines and ensured that your paper conforms to them?

### Section 2 — If you are including theoretical results

2a. Did you state the full set of assumptions of all theoretical results?
- Point out strong assumptions and discuss robustness to violations.

2b. Did you include complete proofs of all theoretical results?
- Proofs may appear in the main paper or supplementary. If in supplementary, provide a proof sketch in the main text.

### Section 3 — If you ran experiments

3a. Did you include the code, data, and instructions needed to reproduce the main experimental results?
- Provide in supplementary material or as an anonymized URL.
- Include exact commands and environment specifications.

3b. Did you specify all training and test details necessary to understand the results?
- Data splits, hyperparameters, how they were chosen, optimizer type, etc.

3c. Did you report error bars?
- Report error bars, confidence intervals, or statistical significance tests for main experiments.
- State number of seeds/runs and what the error bars represent.

3d. Did you include the total amount of compute and the type of resources used?
- GPU hours, hardware type, cloud provider if applicable.

### Section 4 — If your work uses existing assets

4a. Did you cite the creators of assets you used?

4b. Did you mention the license of the assets?

4c. Did you include any new assets in the supplemental material or as a URL?

4d. Did you discuss whether and how consent was obtained from people whose data you are using/curating?

4e. Did you discuss whether the data contains personally identifiable information or offensive content?

### Section 5 — If you used crowdsourcing or conducted research with human subjects

5a. Did you include the full text of instructions given to participants and screenshots?

5b. Did you describe any potential participant risks, with links to IRB approvals if applicable?
- Obtain IRB approval (or equivalent) if applicable. State this clearly in the paper.

## Review process

### New for 2026: Early AC meta-review pilot

Area Chairs (ACs) now provide an initial meta-review **before** the author rebuttal period begins. This meta-review:
- Synthesizes key issues from individual reviews.
- Is visible to both authors and reviewers.
- Helps authors focus their rebuttal on the most decision-relevant points.
- Streamlines subsequent reviewer discussion and final meta-review.

### Scoring scale

| Score | Label | Meaning |
|---|---|---|
| 6 | Strong Accept | Technically flawless, groundbreaking impact, among the best at the conference |
| 5 | Accept | Technically solid, high impact, well-executed |
| 4 | Borderline Accept | Reasons to accept outweigh reasons to reject, e.g., marginally above threshold |
| 3 | Borderline Reject | Reasons to reject outweigh reasons to accept, e.g., marginally below threshold |
| 2 | Reject | Technical flaws, weak evaluation, inadequate reproducibility, or unaddressed ethical issues |

### Review criteria

Reviewers assess six dimensions:

1. **Quality** — Technical soundness. Are claims well-supported? Are methods appropriate and complete?
2. **Clarity** — Is the paper clearly written, well organized, and informative to readers?
3. **Significance** — Does the work address an important problem? Do the results advance the field?
4. **Originality** — Is the contribution novel? Is closest prior work identified and differentiated?
5. **Reproducibility** — Are sufficient details, code, data, and methodology provided?
6. **Responsible research** — Are limitations, ethics, and potential negative impacts addressed?

### Desk rejection triggers

A submission may be desk rejected for any of the following:
- Missing NeurIPS paper checklist
- Style or formatting violations (modified margins, fonts, wrong style file)
- Page limit violations (more than 9 content pages)
- Dual submission policy violation
- Anonymization violations
- Failure to comply with ethics guidelines

## Code submission

- Code submission is encouraged but not mandatory.
- If submitted: include training and evaluation code, dependency specifications, and exact commands to reproduce results.
- Code must be anonymized at submission time.
- For accepted papers: provide de-anonymized links for the wider community.
- Papers cannot be rejected solely for not including code, unless the contribution is specifically about a tool, benchmark, or open-source artifact.

## Camera-ready requirements

For accepted papers:
- De-anonymize the paper (add author names, affiliations, acknowledgments).
- Provide de-anonymized code/data links.
- Address reviewer and AC feedback in the final version.
- Follow any additional camera-ready formatting instructions provided after acceptance.

## Implications for manuscript preparation

When using this skill to prepare a NeurIPS 2026 submission:
1. Verify the paper uses `neurips_2026.sty` with the `default` option.
2. Confirm the main body is within 9 pages.
3. Ensure the paper checklist is present and thoughtfully completed.
4. Audit anonymization across paper, supplementary, and code.
5. Verify a separate Limitations section exists with specific, actionable content.
6. Check that broader societal impacts are discussed somewhere in the paper.
7. For empirical papers: confirm error bars, multi-seed runs, and complete training details.
8. Pre-identify the 3–5 issues an AC meta-review would likely raise, and address them proactively.
9. Verify no dual submission conflicts exist.
10. Ensure all authors have OpenReview profiles.

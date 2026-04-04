# NeurIPS 2026 Paper Checklist Template

Use this template to draft checklist responses before embedding them in the LaTeX submission. Every NeurIPS 2026 Main Track submission must include this checklist in the PDF after any technical appendices. Papers missing the checklist will be desk rejected.

For each item, answer **Yes**, **No**, or **NA**. Optionally add a 1–2 sentence justification. Answering "No" with a proper justification is acceptable and is not grounds for rejection.

---

## 1. For all authors

### 1a. Claims
**Do the main claims made in the abstract and introduction accurately reflect the paper's contributions and scope?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Claims should match theoretical and experimental results. Do not overstate generalizability. If a method was tested on a narrow set of benchmarks, scope the claims accordingly.

Manuscript location: Abstract, Introduction (contributions list)

### 1b. Limitations
**Did you describe the limitations of your work?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Create a separate "Limitations" section. Discuss strong assumptions, robustness to violations, scope of claims (e.g., tested on few datasets or with few runs), and any conditions under which the method may underperform.

Manuscript location: Limitations section

### 1c. Potential negative societal impacts
**Did you discuss any potential negative societal impacts of your work?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: A standalone "Broader Impacts" section is not required, but you must address negative impacts somewhere in the paper. Consider malicious or unintended uses, fairness, privacy, and security implications.

Manuscript location: Conclusion, Limitations, Ethics section, or Supplementary

### 1d. Ethics review compliance
**Have you read the ethics review guidelines and ensured that your paper conforms to them?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Review the NeurIPS ethics guidelines at https://neurips.cc/public/EthicsGuidelines before submitting.

---

## 2. If you are including theoretical results

### 2a. Assumptions
**Did you state the full set of assumptions of all theoretical results?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: List all assumptions explicitly. Discuss how robust the results are to violations of these assumptions and what the implications would be in practice.

Manuscript location: Method or Theory section, Appendix for full proofs

### 2b. Proofs
**Did you include complete proofs of all theoretical results?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Proofs can appear in the main paper or in the technical appendices. If in the appendix, provide a proof sketch in the main text to give intuition.

Manuscript location: Main text (sketch) + Appendix (full proofs)

---

## 3. If you ran experiments

### 3a. Code, data, and instructions
**Did you include the code, data, and instructions needed to reproduce the main experimental results?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Provide in supplementary material or as an anonymized URL. Include the exact commands and environment needed to reproduce results. "No, because the code is proprietary" is acceptable if justified.

Manuscript location: Experiments section, Supplementary material

### 3b. Training and test details
**Did you specify all the training and test details necessary to understand the results?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Include data splits, hyperparameters, how they were chosen, optimizer type, learning rate schedule, batch size, number of epochs, early stopping criteria, and any other relevant details.

Manuscript location: Experiments section, Appendix

### 3c. Error bars
**Did you report error bars (e.g., with respect to the random seed after running experiments multiple times)?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Report error bars, confidence intervals, or statistical significance tests for main experiments. State the number of seeds or runs and describe what the error bars represent (standard deviation, standard error, confidence interval, etc.).

Manuscript location: Results section, Tables, Figures

### 3d. Compute resources
**Did you include the total amount of compute and the type of resources used?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Report GPU hours, hardware type (e.g., A100, H100), number of GPUs, wall-clock time, and cloud provider if applicable.

Manuscript location: Experiments section or Appendix

---

## 4. If your work uses existing assets

### 4a. Creator citations
**Did you cite the creators of assets you used?**

Answer: [ Yes / No / NA ]

Justification:

Manuscript location: References, Related Work, Experiments section

### 4b. Licenses
**Did you mention the license of the assets?**

Answer: [ Yes / No / NA ]

Justification:

Manuscript location: Experiments section, Appendix, or Data Availability Statement

### 4c. New assets
**Did you include any new assets in the supplemental material or as a URL?**

Answer: [ Yes / No / NA ]

Justification:

### 4d. Consent
**Did you discuss whether and how consent was obtained from people whose data you are using/curating?**

Answer: [ Yes / No / NA ]

Justification:

### 4e. PII and offensive content
**Did you discuss whether the data you are using/curating contains personally identifiable information or offensive content?**

Answer: [ Yes / No / NA ]

Justification:

---

## 5. If you used crowdsourcing or conducted research with human subjects

### 5a. Instructions and screenshots
**Did you include the full text of instructions given to participants and screenshots, if applicable?**

Answer: [ Yes / No / NA ]

Justification:

Manuscript location: Appendix

### 5b. Risks and IRB
**Did you describe any potential participant risks, with links to Institutional Review Board (IRB) approvals, if applicable?**

Answer: [ Yes / No / NA ]

Justification:

Guidance: Obtain IRB approval (or equivalent institutional review) if applicable. State IRB status clearly in the paper.

Manuscript location: Ethics section, Appendix

---

## Pre-submission self-check

Before finalizing, verify:
- [ ] Every "Yes" answer has supporting content in the manuscript at the indicated location
- [ ] Every "No" answer has a clear, honest justification
- [ ] "NA" is used only when the question genuinely does not apply to this paper
- [ ] The checklist is appended to the PDF after any technical appendices
- [ ] The checklist does not push the main body over 9 pages (it does not count toward the limit)

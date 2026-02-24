---
name: ds:review
description: Peer review an ML experiment for methodology, leakage, reproducibility, and statistical validity
argument-hint: "[path to experiment result or experiment name]"
disable-model-invocation: true
---

# Peer Review Experiment

## Input

<experiment_reference> $ARGUMENTS </experiment_reference>

**If the experiment reference above is empty, ask the user:** "Which experiment do you want to review? Provide a path to the experiment result file (e.g., `docs/ds/experiments/2026-02-24-churn-xgb-result.md`) or describe the experiment."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: evaluation` learnings related to this experiment or domain.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

### 2. Load Experiment Artifacts

Locate and read the experiment plan and result files:
- If a result path is given, read it and look for `experiment_plan:` in frontmatter to find the plan
- If only an experiment name is given, search `docs/ds/experiments/` for matching files
- Read both the `-plan.md` and `-result.md` files

If the plan or result is missing, report what's missing and ask the user to provide it.

### 3. Methodology Assessment

Use the `model-evaluator` agent to assess the experiment methodology:

- **Hypothesis quality** -- Is it specific, testable, and well-defined?
- **Data handling** -- Is the split strategy appropriate? Is the sample size adequate?
- **Model selection** -- Is the algorithm choice justified? Is there a baseline comparison?
- **Evaluation design** -- Is the primary metric appropriate? Are slices covered?

For each assessment, check the corresponding box in the review template.

### 4. Leakage Re-assessment

Re-run the `target-leakage-detection` skill on the experiment's feature set and results:

- **Temporal leakage** -- Are features available at prediction time?
- **Direct leakage** -- Are any features proxies for the target?
- **Statistical signals** -- Are any single-feature AUCs suspiciously high?
- **Group leakage** -- Does the same entity appear in both train and test?

Record pass/fail for each check in the review template.

Skip for unsupervised and temporal unsupervised experiments (no target variable).

### 5. Reproducibility Audit

Use the `reproducibility-auditor` agent with the `reproducibility-checklist` skill to audit:

- Random seeds set for all stochastic components
- Library versions captured and consistent between plan and result
- Data version hashed (SHA-256)
- Code version captured (git SHA)
- Environment reproducible (requirements file exists)
- Results determinism assessed

Record the score (out of 17) and rating in the review template.

### 6. Statistical Validity

Use the `statistical-analysis` skill to assess:

- **Assumption checks** -- Were appropriate assumptions tested? Did they hold?
- **Effect size** -- Is the observed effect meaningful, not just statistically significant?
- **Statistical power** -- Was the sample size adequate to detect the expected effect?
- **Confidence in results** -- Could results be due to chance?

Reference `references/test_selection_guide.md` for the appropriate test and `references/reporting_standards.md` for APA-format reporting.

### 7. Synthesize Review

Combine findings from steps 3-6 into a coherent review:

- List strengths (what was done well)
- List issues found, ordered by severity (critical > major > minor)
- Make a decision: **Approve**, **Revise**, or **Reject**
  - **Approve** -- methodology is sound, results are reproducible, no leakage detected
  - **Revise** -- fixable issues found (missing seeds, incomplete documentation, minor methodology concerns)
  - **Reject** -- fundamental issues (leakage detected, inappropriate methodology, unreproducible results)

### 8. Write Review Artifact

Generate a review document at `docs/ds/reviews/YYYY-MM-DD-<experiment-name>-review.md` using `templates/experiment-review.md`.

Create the directory if needed: `mkdir -p docs/ds/reviews/`

### 9. Next Steps

Ask the user: "Review complete. What next?" with options:
- Address issues and re-submit
- Ship the model (`/ds:ship`)
- Capture learnings (`/ds:compound`)
- Discuss specific findings

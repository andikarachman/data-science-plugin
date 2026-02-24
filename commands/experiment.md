---
name: experiment
description: Design an ML experiment with hypothesis, split strategy, leakage check, and evaluation plan
argument-hint: "[experiment description or hypothesis]"
disable-model-invocation: true
---

# Design and Run Experiments

## Input

<experiment_description> $ARGUMENTS </experiment_description>

**If the experiment description above is empty, ask the user:** "What experiment do you want to run? Describe the hypothesis, model, or approach you want to test."

## Workflow

### 1. Search Past Experiments

Search `docs/ds/learnings/*.md` for `category: modeling` and `category: features` learnings. Also search `docs/ds/experiments/` for related prior work.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

Surface what was tried before and what worked/failed.

### 2. Hypothesis Formulation

Use the `experiment-designer` agent:
- Null hypothesis and alternative hypothesis
- Independent variable (what's being changed)
- Dependent variable (what's being measured)
- Controls (what's held constant)

### 3. Methodology Design

Define:
- **Data split strategy** -- invoke `split-strategy` skill
- **Feature set** -- reference any feature engineering from prior EDA
- **Model(s) to evaluate**
- **Hyperparameter search strategy** (grid, random, Bayesian)
- **Evaluation metrics** (primary + secondary)
- **Baseline to beat**

Invoke `statistical-tests` skill when designing the comparison protocol.

If temporal data is detected, auto-invoke `time-series-validation` skill.

### 4. Leakage Check

Invoke `target-leakage-detection` skill on the proposed feature set.

### 5. Write Experiment Plan

Generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md` from `templates/experiment-plan.md`.

Create the directory if needed: `mkdir -p docs/ds/experiments/`

### 6. Execute or Defer

Ask the user: "Experiment plan ready. What next?" with options:
- Write experiment code scaffold
- Just save the plan (implement later)
- Review plan with `/ds:review`

### 7. Generate Results (if executing)

After completion, generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md` from `templates/experiment-result.md` with:
- Actual metrics vs. baseline
- Environment details (Python version, library versions, git commit SHA)
- Data hash (SHA-256 of the dataset file)
- Compute cost (wall time, GPU hours if applicable)
- Key observations

Use the `model-evaluator` agent for comprehensive performance assessment.

Invoke `feature-importance` skill alongside model-evaluator for feature attribution analysis.

### 8. Experiment Tracking

Log the experiment using the `experiment-tracking` skill format, including:
- Hypothesis, configuration, results, decision
- Series linkage (parent/child experiments)
- Environment and reproducibility details

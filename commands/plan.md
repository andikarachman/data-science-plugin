---
name: ds:plan
description: Frame a data science problem and plan the approach, surfacing relevant past learnings
argument-hint: "[problem description or business question]"
---

# Frame Problem and Plan Approach

## Input

<problem_description> $ARGUMENTS </problem_description>

**If the problem description above is empty, ask the user:** "What data science problem would you like to frame? Describe the business question, available data, or objective."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for tags and categories related to the problem description. Rank by:
- Tag overlap count
- Recency (prefer newer learnings)
- Outcome (prefer `success` over `failure`)
- Cap at 5 results

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

If learnings are found, summarize them: "Found N prior learnings related to [topic]..." and include key takeaways.

### 2. Problem Framing

Use the `problem-framer` agent to structure the business question:
- What is being predicted/estimated/classified?
- What actions will be taken based on the output?
- What does success look like (metric + threshold)?
- What data is available?
- What are the known constraints (latency, fairness, interpretability)?

### 3. Approach Selection

Invoke the `scikit-learn` skill's `references/quick_reference.md` (Algorithm Selection cheat sheet) to map the problem type, dataset size, and constraints to candidate algorithms.

When the problem involves **inference** (need p-values, causal interpretation), **GLM** (non-normal outcomes), or **time-series forecasting**, invoke the `statsmodels` skill:
- Inference/regression: `references/linear_models.md` and `references/glm.md` for model selection
- Time-series forecasting: `references/time_series.md` for forecasting model selection
- Discrete outcomes: `references/discrete_choice.md` for count/categorical model selection

When the problem involves **time-series classification or regression** (labeled temporal data), invoke the `aeon` skill's SKILL.md "Algorithm Selection Guide" to map the problem to candidate algorithms based on dataset size, accuracy requirements, and interpretability needs. When the problem involves **anomaly detection in time series**, invoke the `aeon` skill's `references/anomaly_detection.md` for algorithm selection. When the problem involves **time-series clustering**, invoke the `aeon` skill's `references/clustering.md` for algorithm selection.

When the problem involves large datasets or multi-source data, reference the `pandas-pro` skill's `references/performance-optimization.md` for data handling strategy (chunked reading, memory optimization, efficient file formats).

Propose 2-3 candidate approaches with trade-offs for each:
- Complexity vs. performance
- Interpretability vs. accuracy
- Development time vs. model sophistication

### 4. Write Artifact

Generate a problem framing document at `docs/ds/plans/YYYY-MM-DD-<name>-plan.md` using the `templates/problem-framing.md` template.

Create the directory if needed: `mkdir -p docs/ds/plans/`

### 5. Next Steps

Ask the user: "Plan ready. What next?" with options:
- Preprocess data (`/ds:preprocess`) -- if raw data needs cleaning or ETL before exploration
- Validate data quality (`/ds:validate`) -- if data needs formal quality checks before exploration
- Start EDA (`/ds:eda`)
- Refine plan
- Start experiment (`/ds:experiment`)

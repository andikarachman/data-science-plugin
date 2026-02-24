---
name: ds:ship
description: Assess deployment readiness of a trained model and generate model card and deployment documentation
argument-hint: "[path to experiment result, model path, or model description]"
disable-model-invocation: true
---

# Ship Model to Production

## Input

<model_reference> $ARGUMENTS </model_reference>

**If the model reference above is empty, ask the user:** "Which model do you want to ship? Provide a path to the experiment result (e.g., `docs/ds/experiments/2026-02-24-churn-xgb-result.md`), the model file, or describe the model."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: deployment` learnings related to this model or domain.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

### 2. Gather Context

Locate and read relevant artifacts:
- Experiment result (if path provided, read it; otherwise search `docs/ds/experiments/`)
- Experiment plan (from result's `experiment_plan:` frontmatter)
- Experiment review (search `docs/ds/reviews/` for a matching review)
- Any existing model card or deployment docs

If no experiment review exists, warn: "No peer review found for this experiment. Consider running `/ds:review` first."

### 3. Generate Model Card

Use the `model-card` skill to generate a standardized model card:

- Fill all 8 required sections (Model Details, Intended Use, Training Data, Evaluation Data, Metrics, Limitations, Ethical Considerations, How to Get Started)
- Pull metrics from the experiment result
- Pull data details from the experiment plan
- Pull limitation and fairness information from the experiment review (if available)
- If SHAP analysis was performed during the experiment, incorporate SHAP-based evidence into the model card: use global feature importance (beeswarm plot) to document what the model relies on in the **Limitations** section, and use cohort comparison bar plots to show feature importance differences across protected groups in the **Fairness** section. Reference the `shap` skill's `references/workflows.md` (Workflow 5: Fairness and Bias Analysis)

Ask the user to fill in deployment-specific fields that can't be inferred:
- Intended users
- Out-of-scope uses
- Deployment context (batch, API, embedded)

Write the model card to `docs/ds/deployments/YYYY-MM-DD-<model-name>-model-card.md` using `templates/model-card.md`.

### 4. Deployment Readiness Assessment

Use the `deployment-readiness` agent to evaluate:

- **Infrastructure** -- Compute, memory, storage, dependencies, data pipeline
- **Monitoring** -- Input drift, output drift, performance degradation, alerting
- **Rollback** -- Previous version preserved, trigger criteria, rollback procedure
- **Operations** -- Retraining schedule, error handling, SLA
- **Compliance** -- Fairness, regulatory, audit trail

The agent produces a readiness decision: **Ready**, **Conditionally Ready**, or **Not Ready**.

### 5. Write Deployment Readiness Document

Generate `docs/ds/deployments/YYYY-MM-DD-<model-name>-readiness.md` using `templates/deployment-readiness.md`.

Create the directory if needed: `mkdir -p docs/ds/deployments/`

### 6. Summary and Next Steps

Present the deployment readiness decision and key findings.

Ask the user: "Deployment assessment complete. What next?" with options:
- Address blockers (if not ready)
- Proceed to deployment
- Capture learnings (`/ds:compound`)
- Discuss specific findings

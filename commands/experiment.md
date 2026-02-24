---
name: ds:experiment
description: Design an ML experiment with hypothesis, split strategy, leakage check, and evaluation plan
argument-hint: "[experiment description or hypothesis]"
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

### 1b. Experiment Type Detection

Determine the experiment type:
- **Supervised** (classification, regression) -- has a target variable, cross-sectional data. Proceed to step 2.
- **Unsupervised** (clustering, dimensionality reduction) -- no target variable. Use unsupervised variants of steps 2-7 as noted below.
- **Time-series** (forecasting, temporal modeling) -- target is future values of a time-ordered variable. Use time-series variants of steps 2-7 as noted below.

If unclear from the experiment description, ask the user.

### 2. Hypothesis Formulation

Use the `experiment-designer` agent.

**Supervised:**
- Null hypothesis and alternative hypothesis
- Independent variable (what's being changed)
- Dependent variable (what's being measured)
- Controls (what's held constant)

**Unsupervised:**
- Research question (e.g., "Are there natural customer segments?", "Can we reduce to N dimensions with <X% information loss?")
- What structure or patterns are expected and why
- Controls (what's held constant across algorithm comparisons)

**Time-series:**
- Forecasting hypothesis (e.g., "SARIMAX(1,1,1)(1,1,0,12) will outperform exponential smoothing for monthly sales, measured by out-of-sample RMSE")
- What temporal patterns are expected (trend, seasonality, cycles)
- Forecast horizon and granularity

### 3. Methodology Design

**Supervised -- define:**
- **Data split strategy** -- invoke `split-strategy` skill
- **Feature set** -- reference any feature engineering from prior EDA
- **Model(s) to evaluate**
- **Hyperparameter search strategy** (grid, random, Bayesian)
- **Evaluation metrics** (primary + secondary)
- **Baseline to beat**

**Unsupervised -- define:**
- **Stability assessment** -- resampling strategy to evaluate cluster/embedding stability
- **Feature set** -- reference any preprocessing from prior EDA
- **Algorithm(s) to compare** -- reference `scikit-learn` skill's `references/unsupervised_learning.md`
- **Hyperparameter search strategy** (e.g., number of clusters range for K-Means, eps/min_samples for DBSCAN)
- **Internal evaluation metrics** -- silhouette score, Davies-Bouldin index, Calinski-Harabasz index, explained variance ratio (for DR)
- **Algorithm comparison protocol** -- how to rank algorithms against each other

**Time-series -- define:**
- **Stationarity assessment** -- ADF and KPSS tests. Reference `statsmodels` skill's `references/time_series.md`
- **Temporal split strategy** -- invoke `split-strategy` skill with temporal mode. Reference `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit) for expanding/sliding window splits
- **Model identification** -- ACF/PACF analysis for ARIMA order selection. Reference `statsmodels` skill's `references/time_series.md`
- **Model(s) to evaluate** -- ARIMA, SARIMAX, Exponential Smoothing, or VAR. Use `statsmodels` skill's SKILL.md Quick Start and `references/time_series.md`
- **Forecast evaluation metrics** -- RMSE, MAE, MAPE on out-of-sample period
- **Baseline** -- naive forecast (last value or seasonal naive)

Invoke the `statistical-analysis` skill for:
- **Test selection**: Use `references/test_selection_guide.md` to choose the right statistical test for the comparison protocol
- **Power analysis**: Determine minimum sample size needed to detect the expected effect size
- **Assumption planning**: Note which assumptions will need checking after results are in

Invoke the `scikit-learn` skill for:
- **Pipeline construction**: Use `references/pipelines_and_composition.md` to design preprocessing + model pipelines with `Pipeline` and `ColumnTransformer`
- **Hyperparameter search implementation**: Use `references/model_evaluation.md` for concrete `GridSearchCV` / `RandomizedSearchCV` patterns
- **Algorithm selection**: Use `references/quick_reference.md` for algorithm selection cheat sheets based on data characteristics

Invoke the `statsmodels` skill when the experiment involves inference or time-series:
- **Regression with inference** (need p-values, coefficient interpretation): Use `references/linear_models.md` for OLS/WLS/GLS model selection and robust standard errors
- **GLM** (non-normal outcomes -- counts, binary, proportions): Use `references/glm.md` for family and link function selection
- **Discrete choice** (multinomial, ordinal, zero-inflated counts): Use `references/discrete_choice.md` for model selection
- **Time-series model identification**: Use `references/time_series.md` for ARIMA order selection via ACF/PACF, stationarity testing, and seasonal decomposition

If temporal data is detected, use the `split-strategy` skill with temporal mode and reference the `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit section) for time-aware cross-validation.

### 4. Leakage Check (supervised and time-series)

**Supervised:** Invoke `target-leakage-detection` skill on the proposed feature set.

**Time-series:** Invoke `target-leakage-detection` skill with temporal focus -- check that no future information leaks into training features. Verify that the temporal split boundary is respected.

**Unsupervised:** Skip this step (no target variable).

### 5. Write Experiment Plan

Generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md` from `templates/experiment-plan.md`.

Create the directory if needed: `mkdir -p docs/ds/experiments/`

### 6. Execute or Defer

Ask the user: "Experiment plan ready. What next?" with options:
- Write experiment code scaffold
- Just save the plan (implement later)
- Review plan with `/ds:review`

When generating the code scaffold, use the `scikit-learn` skill's pipeline patterns (`references/pipelines_and_composition.md`) and the example scripts (`scripts/classification_pipeline.py` or `scripts/clustering_analysis.py`) as structural references.

When the experiment uses statsmodels models (OLS, GLM, ARIMA), reference the `statsmodels` skill's Quick Start Guide and formula API examples in SKILL.md for code scaffold generation.

### 7. Generate Results (if executing)

After completion, generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md` from `templates/experiment-result.md` with:
- Environment details (Python version, library versions, git commit SHA)
- Data hash (SHA-256 of the dataset file)
- Compute cost (wall time, GPU hours if applicable)
- Key observations

**Supervised results:**
- Actual metrics vs. baseline
- Use the `model-evaluator` agent for comprehensive performance assessment
- Use the `scikit-learn` skill's evaluation utilities:
  - Generate classification/regression metrics using `references/model_evaluation.md` patterns
  - Create learning curves and validation curves for overfitting diagnosis
- Run the `statistical-analysis` skill's assumption checks on the results:
  - Use `scripts/assumption_checks.py` to verify normality and variance homogeneity of residuals/predictions
  - Report results in APA format using `references/reporting_standards.md`
  - Calculate and report effect sizes with confidence intervals
- For feature attribution analysis, use the `scikit-learn` skill's feature importance patterns: tree-based `feature_importances_` from `references/supervised_learning.md`, feature selection via `references/preprocessing.md` (RFE, SelectFromModel), and `sklearn.inspection.permutation_importance` for model-agnostic importance
- Use the `statsmodels` skill for model-specific diagnostics:
  - Residual analysis and influence diagnostics from `references/stats_diagnostics.md`
  - Model comparison via AIC/BIC tables from `references/linear_models.md` or `references/glm.md`
  - Robust standard errors (HC, HAC) when assumption checks reveal heteroskedasticity

**Time-series results:**
- Forecast accuracy metrics (RMSE, MAE, MAPE) on out-of-sample period vs. baseline
- Use the `statsmodels` skill's diagnostic patterns:
  - Residual diagnostics from `references/stats_diagnostics.md` (Ljung-Box, heteroskedasticity)
  - Model diagnostic plots (`results.plot_diagnostics()`) from `references/time_series.md`
  - Information criteria comparison (AIC/BIC) across candidate models
- Forecast visualization with prediction intervals
- Stationarity verification on residuals (ADF test)

**Unsupervised results:**
- Internal metrics (silhouette score, Davies-Bouldin, Calinski-Harabasz, inertia) across algorithms and hyperparameter settings
- Stability analysis (how consistent are clusters/embeddings across resampling runs?)
- Visualization using PCA/t-SNE projection -- reference `scikit-learn` skill's `references/unsupervised_learning.md` and `scripts/clustering_analysis.py`
- Cluster profiling: describe each cluster by its feature distributions
- For dimensionality reduction: explained variance ratio, reconstruction error

### 8. Experiment Tracking

Log the experiment using the `experiment-tracking` skill format, including:
- Hypothesis, configuration, results, decision
- Series linkage (parent/child experiments)
- Environment and reproducibility details

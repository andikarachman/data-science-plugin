---
title: "feat: Integrate statsmodels skill with time-series experiment support"
type: feat
date: 2026-02-24
---

# Integrate Statsmodels Skill with Time-Series Experiment Support

## Overview

Add the `statsmodels` skill from `../claude-scientific-skills/scientific-skills/statsmodels/` to the ds plugin. This provides concrete statsmodels API patterns (OLS, GLM, discrete choice, ARIMA/SARIMAX, diagnostics) complementing the existing `statistical-analysis` skill (which guides test selection, assumption workflows, and APA reporting) and `scikit-learn` skill (which covers ML pipelines and evaluation).

The integration also extends `/ds:experiment` with a **time-series experiment path** -- a third routing option alongside supervised and unsupervised -- since time-series methodology (stationarity testing, ARIMA order selection, temporal splits, forecast evaluation) is fundamentally different from standard supervised workflows.

## Source Skill

**Location:** `../claude-scientific-skills/scientific-skills/statsmodels/`

**Contents:**
- `SKILL.md` (612 lines) -- Quick Start examples, core capabilities, formula API, model selection, best practices, common workflows
- `references/linear_models.md` (13KB) -- OLS, WLS, GLS, quantile regression, mixed effects, diagnostics, robust SEs
- `references/glm.md` (17KB) -- Distribution families, link functions, fitting, interpretation, diagnostics
- `references/discrete_choice.md` (17KB) -- Logit, Probit, MNLogit, count models, zero-inflated, marginal effects
- `references/time_series.md` (19KB) -- ARIMA, SARIMAX, VAR, exponential smoothing, state space, forecasting
- `references/stats_diagnostics.md` (21KB) -- Residual diagnostics, influence, hypothesis tests, ANOVA, power analysis, robust covariance

No scripts directory.

## Overlap Analysis: statsmodels vs. statistical-analysis

These skills are complementary with a clear boundary:

| Aspect | `statistical-analysis` | `statsmodels` |
|--------|----------------------|---------------|
| **Focus** | Methodology workflow | Library API reference |
| **Answers** | "Which test? What assumptions? How to report?" | "How to call `sm.OLS`? What does `results.summary()` contain?" |
| **Primary libraries** | scipy.stats, pingouin, pymc, arviz | statsmodels.api, statsmodels.tsa, statsmodels.formula.api |
| **Diagnostics** | Assumption-checking sequence with pass/fail | Function-level API (het_breuschpagan, acorr_ljungbox, VIF) |
| **Reporting** | APA-formatted result strings | Raw model summaries and coefficient tables |
| **Time series** | Not covered | Full coverage (ARIMA, SARIMAX, VAR, state space) |
| **GLM/Discrete** | Not covered | Full coverage (Poisson, NB, zero-inflated, ordinal) |

**Boundary rule:** `statistical-analysis` owns the *workflow* (which test, assumption sequence, APA reporting). `statsmodels` owns the *API reference* (how to call functions, interpret result objects, troubleshoot convergence).

## Changes

### 1. Copy and adapt statsmodels skill

Create `skills/statsmodels/` with:
- `SKILL.md` -- adapted from source
- `references/` -- 5 files copied as-is

**SKILL.md adaptations:**

**Frontmatter** -- rewrite description to "what + when to use" format, keep `license` and `metadata`:

```yaml
---
name: statsmodels
description: "Statsmodels API patterns for OLS, GLM, discrete choice, time series (ARIMA/SARIMAX), and diagnostics. Use when /ds:experiment needs statsmodels model fitting, diagnostics, or time-series forecasting, or /ds:eda needs VIF and stationarity checks. For guided test selection and APA reporting use statistical-analysis."
license: BSD-3-Clause license
metadata:
    skill-author: K-Dense Inc.
---
```

**Add "Role in ds plugin" paragraph** after the Overview section:

```
**Role in the ds plugin:** This skill is invoked by `/ds:experiment` at step 3 (Methodology Design) for regression/GLM/time-series model selection, at step 6 (Execute) for statsmodels code scaffolding, and at step 7 (Generate Results) for model diagnostics and comparison. It is also referenced by `/ds:eda` at step 7 (Relationship Analysis) for VIF and stationarity testing, and by `/ds:plan` at step 3 (Approach Selection) for inference-oriented algorithm selection. It provides concrete statsmodels API patterns complementing the `statistical-analysis` skill (which guides test selection and APA reporting) and the `scikit-learn` skill (which covers ML pipelines and evaluation).
```

**Remove K-Dense promotional section** (lines 613-614, "Suggest Using K-Dense Web For Complex Worflows").

**Keep:** Getting Help section with official documentation links (lines 605-611).

### 2. Wire into `/ds:experiment`

#### Step 3 -- Methodology Design

Add a statsmodels invocation block after the existing scikit-learn block (~line 75):

```markdown
Invoke the `statsmodels` skill when the experiment involves inference or time-series:
- **Regression with inference** (need p-values, coefficient interpretation): Use `references/linear_models.md` for OLS/WLS/GLS model selection and robust standard errors
- **GLM** (non-normal outcomes -- counts, binary, proportions): Use `references/glm.md` for family and link function selection
- **Discrete choice** (multinomial, ordinal, zero-inflated counts): Use `references/discrete_choice.md` for model selection
- **Time-series model identification**: Use `references/time_series.md` for ARIMA order selection via ACF/PACF, stationarity testing, and seasonal decomposition
```

#### Step 6 -- Execute or Defer

Add after the existing scikit-learn scaffold reference (~line 95):

```markdown
When the experiment uses statsmodels models (OLS, GLM, ARIMA), reference the `statsmodels` skill's Quick Start Guide and formula API examples in SKILL.md for code scaffold generation.
```

#### Step 7 -- Generate Results

**Supervised results** -- add after the statistical-analysis assumption checks (~line 114):

```markdown
- Use the `statsmodels` skill for model-specific diagnostics:
  - Residual analysis and influence diagnostics from `references/stats_diagnostics.md`
  - Model comparison via AIC/BIC tables from `references/linear_models.md` or `references/glm.md`
  - Robust standard errors (HC, HAC) when assumption checks reveal heteroskedasticity
```

**Time-series results** -- new subsection (see item 3 below).

### 3. Extend step 1b to three-way routing

Change `commands/experiment.md` step 1b from two-way (supervised/unsupervised) to three-way:

```markdown
### 1b. Experiment Type Detection

Determine the experiment type:
- **Supervised** (classification, regression) -- has a target variable, cross-sectional data. Proceed to step 2.
- **Unsupervised** (clustering, dimensionality reduction) -- no target variable. Use unsupervised variants of steps 2-7 as noted below.
- **Time-series** (forecasting, temporal modeling) -- target is future values of a time-ordered variable. Use time-series variants of steps 2-7 as noted below.

If unclear from the experiment description, ask the user.
```

**Step 2 -- conditional hypothesis for time-series:**

```markdown
**Time-series:**
- Forecasting hypothesis (e.g., "SARIMAX(1,1,1)(1,1,0,12) will outperform exponential smoothing for monthly sales, measured by out-of-sample RMSE")
- What temporal patterns are expected (trend, seasonality, cycles)
- Forecast horizon and granularity
```

**Step 3 -- conditional methodology for time-series:**

```markdown
**Time-series -- define:**
- **Stationarity assessment** -- ADF and KPSS tests. Reference `statsmodels` skill's `references/time_series.md`
- **Temporal split strategy** -- invoke `split-strategy` skill with temporal mode. Reference `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit) for expanding/sliding window splits
- **Model identification** -- ACF/PACF analysis for ARIMA order selection. Reference `statsmodels` skill's `references/time_series.md`
- **Model(s) to evaluate** -- ARIMA, SARIMAX, Exponential Smoothing, or VAR. Use `statsmodels` skill's SKILL.md Quick Start and `references/time_series.md`
- **Forecast evaluation metrics** -- RMSE, MAE, MAPE on out-of-sample period
- **Baseline** -- naive forecast (last value or seasonal naive)
```

**Step 4 -- conditional leakage check for time-series:**

```markdown
**Time-series:** Invoke `target-leakage-detection` skill with temporal focus -- check that no future information leaks into training features. Verify that the temporal split boundary is respected.
```

**Step 7 -- time-series results subsection:**

```markdown
**Time-series results:**
- Forecast accuracy metrics (RMSE, MAE, MAPE) on out-of-sample period vs. baseline
- Use the `statsmodels` skill's diagnostic patterns:
  - Residual diagnostics from `references/stats_diagnostics.md` (Ljung-Box, heteroskedasticity)
  - Model diagnostic plots (`results.plot_diagnostics()`) from `references/time_series.md`
  - Information criteria comparison (AIC/BIC) across candidate models
- Forecast visualization with prediction intervals
- Stationarity verification on residuals (ADF test)
```

### 4. Wire into `/ds:eda` and `/ds:plan`

#### `commands/eda.md` -- step 7 (Relationship Analysis)

Replace the current single-line step 7 with:

```markdown
### 7. Relationship Analysis (tabular path)

Correlation matrix for numeric features, association tests for categoricals, target correlation ranking.

#### 7a. Multicollinearity Check

Compute VIF (variance inflation factor) for numeric features. Reference the `statsmodels` skill's `references/stats_diagnostics.md` for `variance_inflation_factor` patterns. Flag features with VIF > 10.

#### 7b. Stationarity Testing (if temporal columns detected)

If temporal columns were identified in step 5, test for stationarity using ADF and KPSS tests. Reference the `statsmodels` skill's `references/time_series.md` for stationarity testing patterns.
```

#### `commands/plan.md` -- step 3 (Approach Selection)

Add after the existing scikit-learn reference (~line 41):

```markdown
When the problem involves **inference** (need p-values, causal interpretation), **GLM** (non-normal outcomes), or **time-series forecasting**, invoke the `statsmodels` skill:
- Inference/regression: `references/linear_models.md` and `references/glm.md` for model selection
- Time-series: `references/time_series.md` for forecasting model selection
- Discrete outcomes: `references/discrete_choice.md` for count/categorical model selection
```

### 5. Update experiment-designer agent

Add a time-series framing section to `agents/modeling/experiment-designer.md` after the unsupervised section:

```markdown
**For time-series experiments (forecasting, temporal modeling):**

1. **Forecasting hypothesis** -- What temporal pattern do you expect? (e.g., "Monthly sales follow a seasonal ARIMA pattern with period 12")
2. **Stationarity assessment** -- Is the series stationary? What differencing or transformations are needed?
3. **Model candidates** -- Which models to compare and why (e.g., ARIMA vs. SARIMAX vs. Exponential Smoothing)
4. **Order selection** -- How to identify (p,d,q) and seasonal (P,D,Q,s) orders (ACF/PACF, information criteria)
5. **Temporal split** -- Train/test split respecting time order. Define forecast horizon.
6. **Forecast evaluation metrics** -- RMSE, MAE, MAPE on out-of-sample period. Baseline: naive or seasonal naive forecast.
7. **Residual diagnostics** -- Ljung-Box test for autocorrelation, heteroskedasticity check, normality of residuals.
8. **Resource budget** -- Expected compute cost, number of model configurations.
9. **Reproducibility checklist** -- Random seed (if applicable), library versions, data snapshot, environment specification.
```

Add a time-series example to the `<examples>` block:

```markdown
<example>
  <context>User wants to forecast future values of a time-ordered variable</context>
  <user>Design an experiment to forecast monthly revenue for the next 12 months</user>
  <assistant>I'll design the time-series experiment: test stationarity, identify ARIMA orders via ACF/PACF, compare SARIMAX and Exponential Smoothing, use temporal train/test split with the last 12 months held out, and evaluate with RMSE and MAPE against a seasonal naive baseline...</assistant>
  <commentary>Activated because user needs a time-series experiment design with temporal methodology rather than standard supervised ML methodology.</commentary>
</example>
```

### 6. Update experiment templates

#### `templates/experiment-plan.md`

Add time-series conditional fields alongside existing supervised/unsupervised conditionals:

**Hypothesis section:**

```markdown
## Hypothesis / Research Question
[Supervised: What we expect to happen and why. Unsupervised: What structure or patterns are we looking for? Time-series: What temporal pattern or forecasting improvement do we expect?]
```

**Methodology > Data section -- add:**

```markdown
- **Temporal characteristics:** [Time-series: frequency, date range, stationarity assessment, differencing applied]
```

**Methodology > Model section -- add:**

```markdown
- **Model order:** [Time-series: ARIMA (p,d,q), seasonal (P,D,Q,s), or ETS parameters]
- **Forecast horizon:** [Time-series: number of steps ahead to predict]
```

**Evaluation section -- update:**

```markdown
- **Primary metric:** [Supervised: metric name and why. Unsupervised: internal metric (silhouette, Davies-Bouldin, explained variance). Time-series: forecast accuracy metric (RMSE, MAE, MAPE)]
- **Baseline:** [Supervised: what we're comparing against. Unsupervised: algorithm comparison protocol. Time-series: naive forecast (last value or seasonal naive)]
```

#### `templates/experiment-result.md`

Add a time-series results section after the existing tables:

```markdown
### Time-Series Forecast Performance (if applicable)
| Model | Order | AIC | RMSE | MAE | MAPE | vs Baseline |
|---|---|---|---|---|---|---|

### Residual Diagnostics (if applicable)
| Test | Statistic | p-value | Result |
|---|---|---|---|
| Ljung-Box | | | |
| ADF (residuals) | | | |
| Breusch-Pagan | | | |
```

### 7. Update statistical-analysis boundary

Update the "Role in ds plugin" paragraph in `skills/statistical-analysis/SKILL.md` (line 12) to clarify the boundary:

```
**Role in the ds plugin:** This skill is invoked by `/ds:experiment` at step 3 (Methodology Design) for test selection and power analysis, and at step 7 (Generate Results) for assumption checking and APA-formatted reporting. For concrete statsmodels API patterns (model fitting, result object methods, diagnostics, convergence troubleshooting), see the `statsmodels` skill. This skill focuses on the statistical workflow: selecting the right test, verifying assumptions, interpreting results, and reporting in APA format.
```

### 8. Metadata updates

**`.claude-plugin/plugin.json`:**
- Version: `1.5.0` -> `1.6.0`
- Description: `"8 skills"` -> `"9 skills"`

**`README.md`:**
- Line 1: `"8 skills"` -> `"9 skills"`
- Line 51 (Components table): Skills `8` -> `9`
- Add row to Skills table after `scikit-learn`:
  ```
  | `statsmodels` | Statsmodels API patterns for OLS, GLM, discrete choice, time series (ARIMA/SARIMAX), and diagnostics |
  ```

**`CHANGELOG.md`:**

```markdown
## [1.6.0] - 2026-02-24

### Added
- `statsmodels` skill -- API patterns for OLS, GLM, discrete choice models, time series (ARIMA/SARIMAX), and statistical diagnostics with 5 reference files
- Time-series experiment workflow in `/ds:experiment` -- three-way routing at step 1b (supervised/unsupervised/time-series) with conditional steps for stationarity testing, ARIMA order selection, temporal splits, and forecast evaluation
- `/ds:experiment` now uses `statsmodels` for regression/GLM model selection (step 3), code scaffolding (step 6), and model diagnostics (step 7)
- `/ds:eda` now uses `statsmodels` for VIF multicollinearity checks (step 7a) and stationarity testing (step 7b)
- `/ds:plan` now uses `statsmodels` for inference/GLM/time-series approach selection (step 3)
- Time-series fields added to `experiment-plan` and `experiment-result` templates

### Changed
- `experiment-designer` agent now supports time-series experiment framing alongside supervised and unsupervised
- `statistical-analysis` skill "Role in ds plugin" paragraph updated to clarify boundary with new `statsmodels` skill
```

**`CLAUDE.md` invocation map:**

```
| `/ds:plan` | problem-framer | scikit-learn, statsmodels |
| `/ds:eda` | data-profiler, feature-engineer | eda-checklist, target-leakage-detection, exploratory-data-analysis, scikit-learn, statsmodels |
| `/ds:experiment` | experiment-designer, model-evaluator | split-strategy, target-leakage-detection, statistical-analysis, scikit-learn, experiment-tracking, statsmodels |
```

## Out of Scope

- Adding scripts to the statsmodels skill (source has none; the reference files provide sufficient code patterns)
- Updating the `eda-checklist` skill's VIF checklist item to reference statsmodels (the `/ds:eda` command wiring is sufficient)
- Updating `/ds:compound` (the documentation-synthesizer agent is generic enough to capture time-series learnings)
- New dependencies (statsmodels is already required; matplotlib is already optional)

## Acceptance Criteria

### Skill copy
- [x] `skills/statsmodels/SKILL.md` exists with adapted frontmatter (name, description, license, metadata)
- [x] `skills/statsmodels/references/` contains 5 reference files
- [x] "Role in ds plugin" paragraph present
- [x] K-Dense promotional section removed
- [x] Getting Help section preserved

### Command wiring
- [x] `commands/experiment.md` step 3 references statsmodels for regression/GLM/time-series
- [x] `commands/experiment.md` step 6 references statsmodels for code scaffolding
- [x] `commands/experiment.md` step 7 references statsmodels for diagnostics (supervised and time-series)
- [x] `commands/eda.md` step 7a references statsmodels for VIF
- [x] `commands/eda.md` step 7b references statsmodels for stationarity testing
- [x] `commands/plan.md` step 3 references statsmodels for inference/GLM/time-series

### Three-way routing
- [x] `commands/experiment.md` step 1b has three paths: supervised, unsupervised, time-series
- [x] Steps 2, 3, 4, 7 have conditional text for time-series experiments
- [x] `agents/modeling/experiment-designer.md` has time-series framing section and example
- [x] `templates/experiment-plan.md` has time-series conditional fields
- [x] `templates/experiment-result.md` has time-series results section

### Boundary
- [x] `skills/statistical-analysis/SKILL.md` "Role in ds plugin" paragraph updated with boundary statement

### Metadata
- [x] plugin.json version is `1.6.0`, description says `9 skills`
- [x] README.md says `9 skills` in intro, Components table, and has statsmodels in Skills table
- [x] CHANGELOG.md has `[1.6.0]` entry
- [x] CLAUDE.md invocation map has `statsmodels` in plan, eda, experiment rows

### Verification
- [x] `ls -d skills/*/ | wc -l` returns 9
- [x] No phantom skill references (grep for skill names that don't resolve to `skills/<name>/SKILL.md`)

## References

- Source skill: `../claude-scientific-skills/scientific-skills/statsmodels/`
- Skill Integration Checklist: [scikit-learn-skill-plugin-wiring.md](../solutions/integration-issues/scikit-learn-skill-plugin-wiring.md)
- Prior integration plan: [2026-02-24-feat-integrate-scikit-learn-skill-plan.md](./2026-02-24-feat-integrate-scikit-learn-skill-plan.md)
- Experiment improvements plan: [2026-02-24-feat-experiment-command-improvements-plan.md](./2026-02-24-feat-experiment-command-improvements-plan.md)

---
name: tuning-hyperparameters
description: "Hyperparameter tuning workflow reference -- strategy selection, Bayesian optimization with Optuna, search space design, and result analysis. Use when /ds:experiment needs to choose a tuning strategy, design search spaces, or analyze tuning runs."
---

# Tuning Hyperparameters

## Overview

This skill provides workflow-level guidance for hyperparameter tuning in machine learning experiments. It covers strategy selection (grid, random, Bayesian, halving), Bayesian optimization with Optuna, search space design patterns, budget estimation, and result analysis -- the decisions and patterns that sit on top of the API-level tuning tools provided by scikit-learn.

**Role in the ds plugin:** This skill is the hyperparameter tuning workflow reference for the plugin. It is invoked by `/ds:experiment` at step 3 (Methodology Design) for strategy selection and search space design, at step 6 (Code Scaffold) for Optuna boilerplate generation, and at step 7 (Results) for tuning-specific result analysis and convergence diagnostics. **Boundary with scikit-learn:** scikit-learn provides the API patterns for GridSearchCV, RandomizedSearchCV, and HalvingGridSearchCV (what methods exist, their parameters, return values, and code examples). This skill provides the workflow guidance (when to use each strategy, how to design effective search spaces, how to estimate budgets, and how to analyze results). For sklearn search class API patterns, use the `scikit-learn` skill's `references/model_evaluation.md`. **Boundary with experiment-tracking:** experiment-tracking logs final hyperparameters and results. This skill manages the search process that produces those results. **Boundary with statsmodels:** time-series model order selection (ARIMA p,d,q) uses information criteria (AIC/BIC), not cross-validated search. Use the `statsmodels` skill for order selection; use this skill only when wrapping statsmodels models in Optuna for automated search.

## When to Use This Skill

- Choosing between grid search, random search, Bayesian optimization, or successive halving
- Designing hyperparameter search spaces (distributions, ranges, conditional parameters)
- Estimating computational budget for a tuning run
- Setting up Bayesian optimization with Optuna (study, trial, objective, pruning)
- Analyzing tuning results (convergence, parameter importance, search coverage)
- Tuning XGBoost, LightGBM, or other models with Optuna's native integration

## Do NOT Use This Skill

- For GridSearchCV/RandomizedSearchCV/HalvingGridSearchCV API patterns -- use `scikit-learn`
- For ARIMA order selection via AIC/BIC -- use `statsmodels`
- For feature selection (different from hyperparameter tuning) -- use `scikit-learn`
- For experiment logging and tracking -- use `experiment-tracking`

## Quick Start

### Strategy Selection Decision Tree

Estimate total fits: `search_space_size x cv_folds = total_fits`

| Total Fits | Recommended Strategy | Tool |
|---|---|---|
| < 100 | Grid search | scikit-learn `GridSearchCV` |
| 100 -- 500 | Random search | scikit-learn `RandomizedSearchCV` |
| > 500 or expensive evaluations | Bayesian optimization | Optuna `study.optimize()` |
| Large grid, limited budget | Successive halving | scikit-learn `HalvingGridSearchCV` |

For details, see [references/strategy_selection.md](./references/strategy_selection.md).

### Bayesian Optimization with Optuna (Minimal Example)

```python
import optuna
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

def objective(trial):
    n_estimators = trial.suggest_int("n_estimators", 50, 300)
    max_depth = trial.suggest_int("max_depth", 3, 20)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20)

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42,
        n_jobs=-1,
    )
    score = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    return score.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
print(f"Best params: {study.best_params}")
print(f"Best score: {study.best_value:.4f}")
```

For full Optuna patterns (pruning, multi-objective, sklearn integration), see [references/optuna_guide.md](./references/optuna_guide.md).

### Search Space Design

```python
# Common distribution patterns for Optuna
learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-1, log=True)  # log-uniform
n_estimators = trial.suggest_int("n_estimators", 50, 500)                    # uniform integer
max_depth = trial.suggest_int("max_depth", 3, 15)                           # uniform integer
dropout = trial.suggest_float("dropout", 0.0, 0.5)                          # uniform float
kernel = trial.suggest_categorical("kernel", ["rbf", "linear", "poly"])      # categorical
```

For per-model cheat sheets and conditional parameters, see [references/search_space_design.md](./references/search_space_design.md).

## Common Workflows

### Workflow 1: Standard Supervised Tuning

1. Estimate search space size (count parameter combinations)
2. Select strategy using the decision tree above
3. Design search space using per-model cheat sheets (`references/search_space_design.md`)
4. Run tuning with appropriate CV strategy (StratifiedKFold for classification, KFold for regression)
5. Analyze results (`references/result_analysis.md`)

### Workflow 2: Bayesian Optimization for Complex Models

1. Define Optuna objective function (`references/optuna_guide.md`)
2. Use `suggest_*` methods with appropriate distributions (`references/search_space_design.md`)
3. Enable pruning for early stopping of unpromising trials
4. Run study with sufficient trials (50-100 minimum for convergence)
5. Analyze convergence and parameter importance (`references/result_analysis.md`)

### Workflow 3: Budget-Constrained Tuning

1. Calculate budget: `n_trials x avg_train_time x cv_folds = total_time`
2. If budget tight: use successive halving (scikit-learn `HalvingGridSearchCV`)
3. If budget adequate: use Bayesian optimization with timeout
4. Use Optuna pruning to stop unpromising trials early

## Paradigm-Specific Tuning Notes

| Paradigm | CV Strategy | Notes |
|---|---|---|
| Supervised | StratifiedKFold (classification) or KFold (regression) | Standard tuning with all strategies |
| Unsupervised | KFold with internal metrics | Tuning optional; silhouette/Davies-Bouldin as objective; cluster count is most critical parameter |
| Temporal supervised | StratifiedKFold | Standard tuning; aeon models follow sklearn API |
| Temporal unsupervised | KFold with internal metrics | Same as unsupervised |
| Time-series forecasting | TimeSeriesSplit | MUST use temporal CV; never random k-fold; consider AIC/BIC for model order selection (statsmodels) |
| Anomaly detection | Custom (train on normal data only) | Tune window_size and threshold; few parameters; grid search usually sufficient |

## Resources

- [Strategy Selection Guide](./references/strategy_selection.md) -- decision tree for choosing the right strategy
- [Optuna Guide](./references/optuna_guide.md) -- Bayesian optimization patterns with Optuna
- [Search Space Design](./references/search_space_design.md) -- per-model search space cheat sheets
- [Result Analysis](./references/result_analysis.md) -- convergence diagnostics and parameter importance

# Strategy Selection Guide

Choose the right hyperparameter tuning strategy based on search space size, computational budget, and experiment paradigm.

## Decision Tree

```
1. Estimate total fits:
   search_space_size x cv_folds = total_fits

2. Choose strategy:
   total_fits < 100         --> Grid Search (exhaustive, guaranteed optimal)
   total_fits 100-500       --> Random Search (efficient sampling)
   total_fits > 500         --> Bayesian Optimization (intelligent sampling)
   large grid + tight budget --> Successive Halving (progressive elimination)
```

## Strategy Comparison

| Strategy | When to Use | Pros | Cons |
|---|---|---|---|
| **Grid Search** | Small space (<100 combos), all combos must be tested | Exhaustive, reproducible, easy to parallelize | Scales exponentially with dimensions |
| **Random Search** | Medium space (100-500), continuous parameters | Covers high-dimensional spaces better than grid | No learning between trials |
| **Bayesian (Optuna)** | Large space (>500), expensive evaluations, >3 parameters | Learns from past trials, efficient exploration | Overhead per trial, needs 50+ trials to converge |
| **Successive Halving** | Large grid, want speed over completeness | Fast elimination of bad configs, budget-efficient | May discard slow-starters, less thorough |

## Budget Estimation

### Formula

```
wall_time = n_trials x avg_train_time x cv_folds / n_parallel_jobs
```

### Rules of Thumb

- **Grid search**: Budget = all combinations. No shortcut.
- **Random search**: 60 random trials covers ~95% of the top 5% of a 1D space (Bergstra & Bengio, 2012). For multi-dimensional spaces, use `n_iter >= 10 x n_parameters`.
- **Bayesian optimization**: Minimum 50 trials for convergence. 100-200 trials for complex spaces (>5 parameters). Diminishing returns beyond 500.
- **Successive halving**: Budget = `n_candidates x factor^(-1) x cv_folds` per round, with progressive reduction.

## Grid Search Details

**Best for:** Discrete parameters with few values, exhaustive search required.

```python
# Count combinations before running
import numpy as np
param_grid = {
    'n_estimators': [50, 100, 200],      # 3 values
    'max_depth': [5, 10, 15, None],       # 4 values
    'min_samples_split': [2, 5, 10],      # 3 values
}
total_combos = np.prod([len(v) for v in param_grid.values()])
total_fits = total_combos * 5  # 5-fold CV
print(f"Total combinations: {total_combos}")  # 36
print(f"Total fits: {total_fits}")             # 180
```

**Decision**: 180 fits is manageable with Random Search; 36 combinations is fine for Grid Search.

For GridSearchCV API patterns, see the `scikit-learn` skill's `references/model_evaluation.md` (Grid Search section).

## Random Search Details

**Best for:** Continuous parameters, >3 dimensions, want good-enough solution quickly.

**Key advantage:** Random search explores the important dimensions more efficiently than grid search when some parameters matter more than others (Bergstra & Bengio, 2012).

```python
from scipy.stats import randint, uniform, loguniform

param_distributions = {
    'n_estimators': randint(50, 300),
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': randint(2, 20),
    'learning_rate': loguniform(1e-4, 1e-1),  # log-uniform for rates
}
# Rule of thumb: n_iter >= 10 * n_parameters
# 4 parameters -> n_iter >= 40
```

For RandomizedSearchCV API patterns, see the `scikit-learn` skill's `references/model_evaluation.md` (Randomized Search section).

## Bayesian Optimization Details

**Best for:** Large search spaces, expensive model evaluations, complex parameter interactions.

**How it works:** Uses a surrogate model (Tree-structured Parzen Estimator in Optuna) to predict which parameter regions are promising, then samples from those regions. Balances exploration (trying new regions) vs exploitation (refining known good regions).

**When to choose Bayesian over Random:**
- Search space has >500 possible combinations
- Each model evaluation takes >10 seconds
- Parameters have interactions (e.g., learning_rate and n_estimators trade off)
- You need the best possible result within a fixed trial budget

For Optuna patterns, see [optuna_guide.md](./optuna_guide.md).

## Successive Halving Details

**Best for:** Large parameter grids where you want to quickly eliminate bad configurations.

**How it works:** Starts with many configurations on a small resource budget (small subset of data), progressively eliminates the worst performers, and allocates more resources to survivors.

```python
# Estimate halving budget
n_candidates = 100  # starting configurations
factor = 3          # eliminate 2/3 each round
# Round 1: 100 candidates, ~33% of data
# Round 2: 33 candidates, ~100% of data
# Round 3: 11 candidates, full evaluation
```

For HalvingGridSearchCV API patterns, see the `scikit-learn` skill's `references/model_evaluation.md` (Successive Halving section).

## Paradigm-Specific CV Strategy

**Critical**: The cross-validation strategy during tuning MUST match the experiment paradigm.

| Paradigm | CV Strategy for Tuning | Why |
|---|---|---|
| **Supervised classification** | `StratifiedKFold(n_splits=5)` | Preserves class distribution in each fold |
| **Supervised regression** | `KFold(n_splits=5)` | Standard k-fold; no class balance needed |
| **Unsupervised** | `KFold(n_splits=5)` with internal metrics | Use silhouette_score or Davies-Bouldin as objective; no target variable |
| **Temporal supervised** | `StratifiedKFold(n_splits=5)` | Temporal classification doesn't require temporal splits (samples are independent) |
| **Temporal unsupervised** | `KFold(n_splits=5)` with internal metrics | Same as unsupervised |
| **Time-series forecasting** | `TimeSeriesSplit(n_splits=5)` | MUST respect temporal ordering; never use random KFold |
| **Anomaly detection** | Custom (train on normal data) | Tune threshold on validation set with known anomalies; grid search usually sufficient |

### Time-Series Forecasting Warning

Never use `KFold` or `StratifiedKFold` for time-series forecasting tuning. This causes temporal leakage (training on future data, testing on past). Always use `TimeSeriesSplit`:

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
# Each fold: train on past, validate on future
```

### Unsupervised Tuning Notes

Tuning unsupervised models is fundamentally different:
- **No ground truth metric** -- use internal metrics (silhouette, Davies-Bouldin, Calinski-Harabasz)
- **Multiple metrics can disagree** -- silhouette may prefer k=3 while Davies-Bouldin prefers k=5
- **Cluster count is the most critical parameter** -- sweep k first, then tune algorithm-specific parameters
- **Consider stability** -- run multiple seeds and check if cluster assignments are consistent
- Tuning is often optional for unsupervised models; domain expert validation may be more valuable than metric optimization

## Strategy Selection Examples

### Example 1: Random Forest for Classification

```
Parameters: n_estimators(3), max_depth(4), min_samples_split(3), min_samples_leaf(3)
Combinations: 3 x 4 x 3 x 3 = 108
CV folds: 5
Total fits: 540

--> Bayesian optimization (>500 fits) or Random Search (108 combinations is manageable)
```

### Example 2: XGBoost with Learning Rate

```
Parameters: n_estimators(continuous), max_depth(6), learning_rate(continuous),
            subsample(continuous), colsample_bytree(continuous), reg_alpha(continuous)
Combinations: effectively infinite (continuous parameters)
CV folds: 5

--> Bayesian optimization (continuous parameters, >5 dimensions, interactions expected)
```

### Example 3: K-Means Cluster Count

```
Parameters: n_clusters(range 2-15)
Combinations: 14
CV folds: 5
Total fits: 70

--> Grid search (small space, must test all values to find the elbow)
```

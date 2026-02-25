# Search Space Design

Patterns for designing effective hyperparameter search spaces. Includes distribution selection, conditional parameters, and per-model cheat sheets.

## Distribution Selection

### When to Use Each Distribution

| Distribution | Use For | Example Parameters |
|---|---|---|
| **Uniform integer** | Counts, discrete choices | n_estimators, max_depth, num_leaves |
| **Uniform float** | Bounded continuous parameters | dropout, subsample, colsample_bytree |
| **Log-uniform float** | Parameters spanning orders of magnitude | learning_rate, regularization (alpha, lambda) |
| **Categorical** | Discrete choices (non-ordinal) | kernel type, optimizer, activation function |
| **Integer with step** | Coarse discrete search | n_estimators in steps of 50 |

### Log-Uniform vs Uniform

Use **log-uniform** when the parameter spans multiple orders of magnitude and small values matter as much as large values:

```python
# Log-uniform: samples evenly across 1e-5, 1e-4, 1e-3, 1e-2, 1e-1
learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-1, log=True)

# Uniform: samples evenly across 0.00001 to 0.1 (clusters near 0.1)
# BAD for learning rate -- almost never samples small values
learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-1)  # don't do this
```

**Rule of thumb**: If `max_value / min_value > 100`, use log-uniform.

### Scipy Distributions (for sklearn RandomizedSearchCV)

```python
from scipy.stats import randint, uniform, loguniform

param_distributions = {
    'n_estimators': randint(50, 300),           # uniform integer [50, 300)
    'max_depth': [5, 10, 15, 20, None],         # discrete choices
    'learning_rate': loguniform(1e-4, 1e-1),    # log-uniform float
    'subsample': uniform(0.5, 0.5),             # uniform float [0.5, 1.0)
}
```

## Per-Model Search Space Cheat Sheets

### Random Forest

```python
# Optuna
def rf_params(trial):
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 5, 30),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
    }

# GridSearchCV
rf_grid = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [5, 10, 15, 20, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"],
}
# Total combinations: 4 x 5 x 3 x 3 x 2 = 360
```

### Gradient Boosting (sklearn)

```python
def gb_params(trial):
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
    }
```

### XGBoost

```python
def xgb_params(trial):
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "gamma": trial.suggest_float("gamma", 0.0, 5.0),
    }
```

### LightGBM

```python
def lgb_params(trial):
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
    }
# Note: LightGBM's num_leaves should satisfy num_leaves <= 2^max_depth
```

### SVM

```python
def svm_params(trial):
    kernel = trial.suggest_categorical("kernel", ["rbf", "linear", "poly"])
    C = trial.suggest_float("C", 1e-3, 100.0, log=True)

    params = {"kernel": kernel, "C": C}

    if kernel == "rbf":
        params["gamma"] = trial.suggest_float("gamma", 1e-5, 1.0, log=True)
    elif kernel == "poly":
        params["degree"] = trial.suggest_int("degree", 2, 5)
        params["gamma"] = trial.suggest_float("gamma", 1e-5, 1.0, log=True)
    # linear kernel: no additional parameters

    return params
```

### Logistic Regression

```python
def lr_params(trial):
    penalty = trial.suggest_categorical("penalty", ["l1", "l2", "elasticnet"])
    C = trial.suggest_float("C", 1e-4, 10.0, log=True)

    params = {"penalty": penalty, "C": C, "max_iter": 1000}

    if penalty == "elasticnet":
        params["l1_ratio"] = trial.suggest_float("l1_ratio", 0.0, 1.0)
        params["solver"] = "saga"
    elif penalty == "l1":
        params["solver"] = "saga"
    else:
        params["solver"] = "lbfgs"

    return params
```

### K-Means (Unsupervised)

```python
def kmeans_params(trial):
    return {
        "n_clusters": trial.suggest_int("n_clusters", 2, 15),
        "init": trial.suggest_categorical("init", ["k-means++", "random"]),
        "n_init": trial.suggest_int("n_init", 5, 20),
        "max_iter": trial.suggest_int("max_iter", 100, 500),
    }
# Objective: maximize silhouette_score or minimize Davies-Bouldin
```

## Scaling Heuristics

### Start Coarse, Refine Narrow

1. **Coarse search**: Wide ranges with few trials (20-30)
2. **Analyze**: Identify promising regions from coarse results
3. **Narrow search**: Tighten ranges around the best region
4. **Final search**: Fine-grained search in the narrow region

```python
# Coarse: wide learning rate range
lr = trial.suggest_float("lr", 1e-5, 1.0, log=True)

# After coarse search shows best around 1e-3:
# Narrow: tighten around 1e-3
lr = trial.suggest_float("lr", 5e-4, 5e-3, log=True)
```

### Parameter Priority

Tune the most impactful parameters first, then add less impactful ones:

1. **High impact**: learning_rate, n_estimators, max_depth
2. **Medium impact**: subsample, colsample_bytree, min_child_weight
3. **Low impact**: reg_alpha, reg_lambda, gamma

### Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Uniform for learning rate | Clusters samples near max value | Use `log=True` |
| Too-wide ranges | Wastes trials on extreme values | Start coarse, then narrow |
| Too-narrow ranges | May miss the global optimum | Start wider than you think necessary |
| Ignoring parameter interactions | learning_rate and n_estimators interact | Use Bayesian optimization |
| Fixed random seed in search | Reproducible but may hide instability | Run 2-3 seeds on final config |

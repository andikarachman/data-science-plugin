# Optuna Guide

Bayesian optimization patterns with Optuna for hyperparameter tuning. This guide covers study/trial patterns, suggest methods, pruning, sklearn integration, multi-objective optimization, and visualization.

## Installation

```bash
uv pip install optuna

# Optional: for OptunaSearchCV (sklearn integration)
uv pip install optuna-integration[sklearn]

# Optional: for Plotly-based visualization
uv pip install plotly
```

## Core Concepts

### Study and Trial

A **study** is a single optimization session. A **trial** is one evaluation of the objective function with a specific set of hyperparameters.

```python
import optuna

def objective(trial):
    # Suggest hyperparameters
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", 1, 100)
    return (x - 2) ** 2 + y  # minimize this

# Create study (minimize by default)
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=100)

# Access results
print(f"Best params: {study.best_params}")
print(f"Best value: {study.best_value}")
print(f"Best trial: {study.best_trial}")
```

### Direction

```python
# Minimize (default) -- loss, error, RMSE
study = optuna.create_study(direction="minimize")

# Maximize -- accuracy, AUC, F1
study = optuna.create_study(direction="maximize")
```

## Suggest Methods

Use `trial.suggest_*` to define the search space inside the objective function.

### suggest_int

```python
# Uniform integer
n_estimators = trial.suggest_int("n_estimators", 50, 300)

# Integer with step
n_estimators = trial.suggest_int("n_estimators", 50, 300, step=50)

# Log-scale integer (for parameters spanning orders of magnitude)
n_units = trial.suggest_int("n_units", 16, 512, log=True)
```

### suggest_float

```python
# Uniform float
dropout = trial.suggest_float("dropout", 0.0, 0.5)

# Log-uniform float (learning rates, regularization)
learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-1, log=True)

# Float with step
subsample = trial.suggest_float("subsample", 0.5, 1.0, step=0.1)
```

### suggest_categorical

```python
# Categorical choices
optimizer = trial.suggest_categorical("optimizer", ["adam", "sgd", "rmsprop"])
kernel = trial.suggest_categorical("kernel", ["rbf", "linear", "poly"])
```

## Pruning (Early Stopping)

Pruning stops unpromising trials early, saving computational budget. Use `trial.report()` to report intermediate values and `trial.should_prune()` to check if the trial should stop.

### MedianPruner (Recommended Default)

Prunes a trial if its intermediate value is worse than the median of previous trials at the same step.

```python
import optuna
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 300),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 1.0, log=True),
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for step, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_tr, X_val = X_train[train_idx], X_train[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]

        clf = GradientBoostingClassifier(**params, random_state=42)
        clf.fit(X_tr, y_tr)
        score = accuracy_score(y_val, clf.predict(X_val))
        scores.append(score)

        # Report intermediate value (mean score so far)
        trial.report(sum(scores) / len(scores), step)

        # Prune if this trial is unpromising
        if trial.should_prune():
            raise optuna.TrialPruned()

    return sum(scores) / len(scores)

study = optuna.create_study(
    direction="maximize",
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=2),
)
study.optimize(objective, n_trials=100)
```

### Other Pruners

```python
# PercentilePruner -- prune if below Nth percentile
pruner = optuna.pruners.PercentilePruner(percentile=25.0)

# HyperbandPruner -- Hyperband-style successive halving
pruner = optuna.pruners.HyperbandPruner(min_resource=1, max_resource=5, reduction_factor=3)

# No pruning
pruner = optuna.pruners.NopPruner()
```

## Sklearn Pipeline Integration

### Raw Optuna with sklearn Pipeline

```python
import optuna
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

def objective(trial):
    # Pipeline hyperparameters
    n_estimators = trial.suggest_int("n_estimators", 50, 300)
    max_depth = trial.suggest_int("max_depth", 3, 20)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20)

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    score = cross_val_score(pipe, X_train, y_train, cv=5, scoring="accuracy")
    return score.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

### OptunaSearchCV (Drop-in Replacement for GridSearchCV)

Requires `optuna-integration[sklearn]`. Provides a GridSearchCV-compatible interface with Bayesian optimization under the hood.

```python
from optuna.integration import OptunaSearchCV
from sklearn.ensemble import RandomForestClassifier

# Define distributions (same syntax as RandomizedSearchCV)
param_distributions = {
    "n_estimators": optuna.distributions.IntDistribution(50, 300),
    "max_depth": optuna.distributions.IntDistribution(3, 20),
    "min_samples_split": optuna.distributions.IntDistribution(2, 20),
}

clf = RandomForestClassifier(random_state=42)
search = OptunaSearchCV(
    clf,
    param_distributions,
    cv=5,
    n_trials=100,
    scoring="accuracy",
    random_state=42,
)
search.fit(X_train, y_train)

print(f"Best params: {search.best_params_}")
print(f"Best score: {search.best_score_}")
best_model = search.best_estimator_
```

**Note:** OptunaSearchCV requires `pip install optuna-integration[sklearn]` as a separate install from core Optuna.

## XGBoost and LightGBM Integration

### XGBoost with Optuna

```python
import optuna
import xgboost as xgb
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "random_state": 42,
        "n_jobs": -1,
    }

    clf = xgb.XGBClassifier(**params, use_label_encoder=False, eval_metric="logloss")
    score = cross_val_score(clf, X_train, y_train, cv=5, scoring="roc_auc")
    return score.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

### LightGBM with Optuna

```python
import optuna
import lightgbm as lgb
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "random_state": 42,
        "n_jobs": -1,
        "verbose": -1,
    }

    clf = lgb.LGBMClassifier(**params)
    score = cross_val_score(clf, X_train, y_train, cv=5, scoring="roc_auc")
    return score.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

## Multi-Objective Optimization

Optimize multiple objectives simultaneously (e.g., accuracy AND training time).

```python
import optuna
import time

def objective(trial):
    n_estimators = trial.suggest_int("n_estimators", 50, 500)
    max_depth = trial.suggest_int("max_depth", 3, 15)

    clf = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, random_state=42
    )

    start = time.time()
    score = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    elapsed = time.time() - start

    return score.mean(), elapsed  # maximize accuracy, minimize time

study = optuna.create_study(directions=["maximize", "minimize"])
study.optimize(objective, n_trials=100)

# Access Pareto front
for trial in study.best_trials:
    print(f"Accuracy: {trial.values[0]:.4f}, Time: {trial.values[1]:.2f}s")
```

## Conditional Parameters

Handle parameters that only apply for certain model types or configurations.

```python
def objective(trial):
    classifier = trial.suggest_categorical("classifier", ["svm", "rf", "xgb"])

    if classifier == "svm":
        kernel = trial.suggest_categorical("svm_kernel", ["rbf", "linear", "poly"])
        C = trial.suggest_float("svm_C", 1e-3, 100, log=True)
        if kernel == "rbf":
            gamma = trial.suggest_float("svm_gamma", 1e-5, 1.0, log=True)
        clf = SVC(kernel=kernel, C=C, gamma=gamma if kernel == "rbf" else "scale")

    elif classifier == "rf":
        n_estimators = trial.suggest_int("rf_n_estimators", 50, 300)
        max_depth = trial.suggest_int("rf_max_depth", 3, 20)
        clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)

    elif classifier == "xgb":
        n_estimators = trial.suggest_int("xgb_n_estimators", 50, 500)
        learning_rate = trial.suggest_float("xgb_lr", 1e-3, 0.3, log=True)
        clf = xgb.XGBClassifier(n_estimators=n_estimators, learning_rate=learning_rate)

    score = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    return score.mean()
```

## Storage and Resumable Studies

For long-running tuning jobs, persist study state to disk.

```python
import optuna

# SQLite storage (file-based, survives interruptions)
study = optuna.create_study(
    study_name="my-experiment",
    storage="sqlite:///optuna_study.db",
    direction="maximize",
    load_if_exists=True,  # resume if study already exists
)
study.optimize(objective, n_trials=100)

# Resume later
study = optuna.load_study(
    study_name="my-experiment",
    storage="sqlite:///optuna_study.db",
)
study.optimize(objective, n_trials=50)  # 50 more trials
```

## Visualization

Optuna provides built-in visualization using Plotly. For matplotlib-based alternatives, see below.

### Optimization History

```python
import optuna.visualization as vis

fig = vis.plot_optimization_history(study)
fig.show()

# Matplotlib alternative
import optuna.visualization.matplotlib as vis_mpl
fig = vis_mpl.plot_optimization_history(study)
```

### Parameter Importances

```python
fig = vis.plot_param_importances(study)
fig.show()
```

### Parallel Coordinate Plot

```python
fig = vis.plot_parallel_coordinate(study)
fig.show()
```

### Slice Plot (Parameter vs Objective)

```python
fig = vis.plot_slice(study)
fig.show()
```

### Contour Plot (Parameter Interactions)

```python
fig = vis.plot_contour(study, params=["learning_rate", "n_estimators"])
fig.show()
```

### Saving Plots (DS Plugin Convention)

Follow the ds plugin's matplotlib convention: save to file, then close.

```python
import matplotlib.pyplot as plt
import optuna.visualization.matplotlib as vis_mpl

fig = vis_mpl.plot_optimization_history(study)
plt.savefig("docs/ds/experiments/tuning_history.png", dpi=150, bbox_inches="tight")
plt.close(fig)

fig = vis_mpl.plot_param_importances(study)
plt.savefig("docs/ds/experiments/param_importances.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

## Sampler Selection

```python
# TPE (default) -- best for most cases
sampler = optuna.samplers.TPESampler(seed=42)

# CMA-ES -- good for continuous parameters with interactions
sampler = optuna.samplers.CmaEsSampler(seed=42)

# Random -- baseline comparison
sampler = optuna.samplers.RandomSampler(seed=42)

# GP (Gaussian Process) -- good for small trial budgets (<50)
sampler = optuna.samplers.GPSampler(seed=42)

study = optuna.create_study(sampler=sampler, direction="maximize")
```

## Timeout and Callbacks

```python
# Time-based budget
study.optimize(objective, n_trials=1000, timeout=3600)  # 1 hour max

# Callback to stop when target reached
def callback(study, trial):
    if study.best_value >= 0.95:  # stop if accuracy >= 95%
        study.stop()

study.optimize(objective, n_trials=1000, callbacks=[callback])
```

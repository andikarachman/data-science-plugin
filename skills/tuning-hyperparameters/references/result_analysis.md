# Result Analysis

Patterns for analyzing hyperparameter tuning results -- convergence diagnostics, parameter importance, search coverage, and visualization.

## Convergence Analysis

### Has the Search Converged?

A tuning run has converged when additional trials stop improving the objective. Check convergence before trusting results.

```python
import optuna
import matplotlib.pyplot as plt

# Plot optimization history
fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)

trials = study.trials
trial_numbers = [t.number for t in trials if t.state == optuna.trial.TrialState.COMPLETE]
values = [t.value for t in trials if t.state == optuna.trial.TrialState.COMPLETE]

ax.plot(trial_numbers, values, "o-", alpha=0.5, markersize=3, label="Trial value")

# Running best
best_values = []
current_best = float("inf") if study.direction == optuna.study.StudyDirection.MINIMIZE else float("-inf")
for v in values:
    if study.direction == optuna.study.StudyDirection.MINIMIZE:
        current_best = min(current_best, v)
    else:
        current_best = max(current_best, v)
    best_values.append(current_best)

ax.plot(trial_numbers, best_values, "r-", linewidth=2, label="Best so far")
ax.set_xlabel("Trial")
ax.set_ylabel("Objective Value")
ax.set_title("Optimization History")
ax.legend()
plt.savefig("tuning_convergence.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Convergence Indicators

| Indicator | Converged | Not Converged |
|---|---|---|
| Best-so-far curve | Plateaus in the last 20% of trials | Still improving at the end |
| Trial value variance | Decreasing over time | Constant or increasing |
| Improvement rate | <0.1% improvement in last 20 trials | >0.5% improvement in recent trials |

### What to Do If Not Converged

1. **Run more trials**: Add 50-100 more trials
2. **Narrow the search space**: Tighten ranges around the current best
3. **Switch strategy**: If using random search, switch to Bayesian
4. **Increase pruning patience**: Pruning too aggressively may discard promising trials

## Parameter Importance

### Which Parameters Matter Most?

```python
# Optuna built-in (requires completed study)
importance = optuna.importance.get_param_importances(study)
for param, imp in importance.items():
    print(f"  {param}: {imp:.4f}")

# Visualization
import optuna.visualization.matplotlib as vis_mpl

fig = vis_mpl.plot_param_importances(study)
plt.savefig("param_importances.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Interpreting Parameter Importance

- **High importance (>0.3)**: This parameter significantly affects performance. Ensure its range is well-explored.
- **Medium importance (0.1-0.3)**: Contributes to performance but less critical. Can narrow range in refinement.
- **Low importance (<0.1)**: Minimal effect. Can fix to default value to reduce search space.

### Using Importance for Refinement

```python
# After initial broad search:
importance = optuna.importance.get_param_importances(study)

# Focus refinement on high-importance parameters
# Fix low-importance parameters to their best values
best = study.best_params
print(f"Fix these to best values: {[p for p, i in importance.items() if i < 0.1]}")
print(f"Refine these: {[p for p, i in importance.items() if i >= 0.1]}")
```

## Search Space Coverage

### Are We Exploring Enough?

Check that the search isn't stuck in a local region.

```python
import matplotlib.pyplot as plt
import numpy as np

# Scatter plot of top 2 parameters
trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]

param_names = list(study.best_params.keys())[:2]  # top 2 parameters
if len(param_names) >= 2:
    p1_vals = [t.params.get(param_names[0]) for t in trials if param_names[0] in t.params]
    p2_vals = [t.params.get(param_names[1]) for t in trials if param_names[1] in t.params]
    obj_vals = [t.value for t in trials if param_names[0] in t.params and param_names[1] in t.params]

    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    scatter = ax.scatter(p1_vals, p2_vals, c=obj_vals, cmap="viridis", alpha=0.7)
    ax.set_xlabel(param_names[0])
    ax.set_ylabel(param_names[1])
    ax.set_title("Search Space Exploration")
    plt.colorbar(scatter, label="Objective")
    plt.savefig("search_coverage.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
```

### Parallel Coordinate Plot

Visualize relationships between all parameters and the objective.

```python
import optuna.visualization.matplotlib as vis_mpl

fig = vis_mpl.plot_parallel_coordinate(study)
plt.savefig("parallel_coordinate.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Slice Plot

See how each parameter affects the objective independently.

```python
fig = vis_mpl.plot_slice(study)
plt.savefig("slice_plot.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

## Best Trial Analysis

### Extracting and Validating the Best Configuration

```python
# Best trial details
best = study.best_trial
print(f"Best trial number: {best.number}")
print(f"Best value: {best.value:.4f}")
print(f"Best params: {best.params}")

# Validate on held-out test set (do this ONCE, at the end)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

clf = RandomForestClassifier(**best.params, random_state=42)
clf.fit(X_train, y_train)
test_score = accuracy_score(y_test, clf.predict(X_test))
print(f"Test score: {test_score:.4f}")

# Check for overfitting to validation folds
print(f"Val-Test gap: {best.value - test_score:.4f}")
# Gap > 0.02 suggests overfitting to CV folds
```

### Top-N Analysis

Compare the top configurations to assess robustness.

```python
# Get top 5 trials
completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
sorted_trials = sorted(completed, key=lambda t: t.value, reverse=(study.direction == optuna.study.StudyDirection.MAXIMIZE))

print("Top 5 trials:")
for t in sorted_trials[:5]:
    print(f"  Trial {t.number}: value={t.value:.4f}, params={t.params}")

# If top 5 have very different parameters, the landscape is flat
# If top 5 cluster in a similar region, the result is robust
```

## Overfitting Detection

### Train-Validation Gap

A large gap between training and validation scores suggests overfitting.

```python
# Refit the best model and check train vs validation
from sklearn.model_selection import cross_validate

clf = RandomForestClassifier(**study.best_params, random_state=42)
cv_results = cross_validate(clf, X_train, y_train, cv=5, scoring="accuracy",
                            return_train_score=True)

train_mean = cv_results["train_score"].mean()
val_mean = cv_results["test_score"].mean()
gap = train_mean - val_mean

print(f"Train: {train_mean:.4f}, Val: {val_mean:.4f}, Gap: {gap:.4f}")
# Gap < 0.02: OK
# Gap 0.02-0.05: Mild overfitting, consider regularization
# Gap > 0.05: Significant overfitting
```

### Tuning Overfit (Overfitting to Validation Folds)

When many trials are tested, there is a risk of finding a configuration that happens to score well on the specific CV folds but doesn't generalize. Mitigations:

1. **Use more folds**: 10-fold CV is more robust than 3-fold
2. **Nested cross-validation**: Inner loop for tuning, outer loop for performance estimation
3. **Hold-out validation set**: Reserve a set not used in any CV fold for final validation
4. **Check stability**: Rerun the best configuration with different random seeds

## Summary Report Template

After a tuning run, summarize results for the experiment report:

```markdown
### Hyperparameter Tuning Results

| Parameter | Best Value | Search Range | Distribution |
|---|---|---|---|
| n_estimators | 247 | [50, 500] | uniform int |
| max_depth | 8 | [3, 15] | uniform int |
| learning_rate | 0.023 | [1e-3, 0.3] | log-uniform |

- **Strategy**: Bayesian optimization (Optuna TPE)
- **Trials completed**: 100 (12 pruned)
- **Best trial**: #73 (accuracy = 0.8934)
- **Convergence**: Best value stabilized after trial 60
- **Top parameter**: learning_rate (importance = 0.45)
- **Val-Test gap**: 0.008 (no overfitting detected)
- **Wall time**: 42 minutes
```

---
name: setup
description: "Check Python environment for required DS/ML libraries and report versions or missing packages. Use when setting up a new project or debugging import errors."
---

# Environment Setup Check

Check the current Python environment for libraries required by the ds plugin. Report what is installed, what is missing, and provide install commands.

## Steps

1. **Check Python version**

Run `python3 --version` and report the result. Require Python 3.9+.

2. **Check required libraries**

For each required library, run a Python import and version check:

```bash
python3 -c "
import importlib
required = {
    'pandas': 'pandas',
    'scikit-learn': 'sklearn',
    'scipy': 'scipy',
    'statsmodels': 'statsmodels',
    'numpy': 'numpy',
}
for pkg_name, import_name in required.items():
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'installed')
        print(f'  {pkg_name}: {version}')
    except ImportError:
        print(f'  {pkg_name}: MISSING')
"
```

3. **Check optional libraries**

Run the same check for optional libraries used in generated experiment code:

```bash
python3 -c "
import importlib
optional = {
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'aeon': 'aeon',
    'xgboost': 'xgboost',
    'lightgbm': 'lightgbm',
    'shap': 'shap',
    'great_expectations': 'great_expectations',
    'polars': 'polars',
    'optuna': 'optuna',
}
for pkg_name, import_name in optional.items():
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'installed')
        print(f'  {pkg_name}: {version}')
    except ImportError:
        print(f'  {pkg_name}: not installed')
"
```

4. **Report install commands**

If any **required** libraries are missing, output the install command:

```
uv pip install pandas scikit-learn scipy statsmodels numpy
```

List only the missing packages in the command. If all required libraries are present, report that the environment is ready.

For missing optional libraries, suggest but do not insist:

```
uv pip install matplotlib seaborn aeon xgboost lightgbm shap great_expectations polars optuna
```

## Rules

- Do NOT auto-install anything. Data scientists manage their own environments.
- Do NOT suggest installing into the system Python. Assume the user has an active virtual environment or conda environment.
- If `python3` is not found, suggest the user activate their environment first.
- Report results as a simple table, not verbose prose.

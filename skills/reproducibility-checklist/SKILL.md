---
name: reproducibility-checklist
description: "Verify that an ML experiment meets reproducibility requirements: random seeds, library versions, data hashes, environment capture. Use when reviewing experiments before shipping."
---

# Reproducibility Checklist

Verify that an ML experiment can be reproduced by another person on another machine. Walk through each requirement and score the experiment.

## Checklist

### 1. Random Seeds

Verify all sources of randomness are controlled:

- [ ] Global random seed set (`random_state` parameter or `np.random.seed()`)
- [ ] Seed passed to all stochastic components (train/test split, model training, data augmentation)
- [ ] Seed value documented in experiment plan

**Check:** Search the experiment code for `random_state`, `seed`, `random.seed`, `np.random.seed`, `torch.manual_seed`. Every stochastic call should have a fixed seed.

### 2. Library Versions

Verify all library versions are captured:

- [ ] Python version recorded
- [ ] Key library versions recorded (pandas, scikit-learn, numpy, statsmodels, aeon, xgboost, etc.)
- [ ] Library versions match between experiment plan and result

**Check:** Look for an "Environment" section in the experiment result. Compare library versions against what was planned.

### 3. Data Version

Verify the exact dataset can be retrieved:

- [ ] Data file hash (SHA-256) recorded
- [ ] Data source path or query documented
- [ ] Date range or snapshot identifier specified
- [ ] Row count and column count recorded

**Check:** Look for `data_hash`, `SHA-256`, or a data snapshot reference in the experiment artifacts. Verify the hash matches the actual file if available.

### 4. Code Version

Verify the exact code state can be recovered:

- [ ] Git commit SHA recorded
- [ ] Working directory was clean at experiment time (no uncommitted changes)
- [ ] Any non-committed code changes documented

**Check:** Look for `git_commit` or `git SHA` in the experiment result.

### 5. Environment Reproducibility

Verify the environment can be recreated:

- [ ] Requirements file or lock file exists (requirements.txt, environment.yml, pyproject.toml)
- [ ] Hardware details documented (CPU/GPU, memory)
- [ ] Compute cost recorded (wall time, GPU hours)

**Check:** Look for an "Environment" section. If no requirements file exists, flag as a gap.

### 6. Results Reproducibility

Verify results are deterministic:

- [ ] Running the same code with the same data and seed produces the same metrics (within floating-point tolerance)
- [ ] Any non-deterministic components documented (e.g., GPU non-determinism, multi-threaded operations)

**Note:** Full re-run verification is optional. Flag if the experiment uses known non-deterministic operations (GPU training without `torch.use_deterministic_algorithms()`, multi-threaded data loading).

## Scoring

Count the number of checked items across all 6 sections:

| Score | Rating | Recommendation |
|---|---|---|
| 16-17 / 17 | Excellent | Ready to ship |
| 12-15 / 17 | Good | Minor gaps -- document and proceed |
| 8-11 / 17 | Fair | Significant gaps -- fix before shipping |
| 0-7 / 17 | Poor | Not reproducible -- requires rework |

## Quick Verification Script

```python
import hashlib
import sys
import subprocess
import importlib

def verify_reproducibility(data_path=None, expected_hash=None):
    """Quick reproducibility verification."""
    report = {}

    # Python version
    report['python'] = sys.version.split()[0]

    # Git commit
    try:
        sha = subprocess.getoutput("git rev-parse HEAD").strip()
        dirty = subprocess.getoutput("git status --porcelain").strip()
        report['git_commit'] = sha
        report['git_clean'] = len(dirty) == 0
    except Exception:
        report['git_commit'] = 'unavailable'
        report['git_clean'] = False

    # Library versions
    libs = ['pandas', 'numpy', 'sklearn', 'scipy', 'statsmodels',
            'aeon', 'xgboost', 'lightgbm', 'matplotlib']
    report['libraries'] = {}
    for lib in libs:
        try:
            mod = importlib.import_module(lib)
            report['libraries'][lib] = getattr(mod, '__version__', 'installed')
        except ImportError:
            pass

    # Data hash
    if data_path:
        h = hashlib.sha256()
        with open(data_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        report['data_hash'] = h.hexdigest()
        if expected_hash:
            report['data_hash_match'] = report['data_hash'] == expected_hash

    return report
```

## Common Reproducibility Failures

| Failure | Cause | Fix |
|---|---|---|
| Different metrics on re-run | Missing random seed in data split or model | Pass `random_state` to all stochastic calls |
| Can't install same libraries | No pinned versions | Use `pip freeze > requirements.txt` at experiment time |
| Data changed between runs | No data hash captured | Hash data files before training |
| Code changed since experiment | No git SHA recorded | Record `git rev-parse HEAD` in experiment log |
| GPU gives different results | Non-deterministic CUDA operations | Document GPU non-determinism or use `torch.use_deterministic_algorithms(True)` |

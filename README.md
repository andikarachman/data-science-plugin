# Data Science Plugin

Data science and ML workflow tools that compound institutional knowledge. 9 agents, 8 commands, 19 skills for problem framing, preprocessing, validation, EDA, experimentation, review, deployment, and knowledge compounding.

## Install

Add the repo as a marketplace, then install:

```
/plugin marketplace add andikarachman/data-science-plugin
/plugin install ds@data-science-plugin
```

## Prerequisites

The plugin's skills and agents use Python libraries for data analysis. Install them into your active environment:

```bash
uv pip install pandas scikit-learn scipy statsmodels numpy
```

Optional libraries (visualization, advanced models, and high-performance DataFrames):

```bash
uv pip install matplotlib seaborn aeon xgboost lightgbm shap polars optuna
```

Run `/ds:setup` to check which libraries are installed.

## Workflow

```
Frame -> Preprocess -> Validate -> Explore -> Experiment -> Review -> Ship -> Compound -> Repeat
```

| Command | Purpose |
|---------|---------|
| `/ds:plan` | Frame business questions as DS problems and plan approach |
| `/ds:preprocess` | Clean, validate, and transform raw data with automated pipelines |
| `/ds:validate` | Run formal data quality validation with expectation suites |
| `/ds:eda` | Run structured exploratory data analysis |
| `/ds:experiment` | Design and run rigorous ML experiments |
| `/ds:review` | Peer review experiments for methodology and reproducibility |
| `/ds:ship` | Assess deployment readiness and generate model cards |
| `/ds:compound` | Capture learnings to make future projects faster |

Each cycle compounds: experiment learnings surface in future plans, error patterns inform feature engineering, and review feedback becomes institutional knowledge.

## Components

| Component | Count |
|-----------|-------|
| Agents | 9 |
| Commands | 8 |
| Skills | 19 |
| Templates | 9 |
| MCP Servers | 1 |

## Agents

### Analysis (4)

| Agent | Description |
|-------|-------------|
| `problem-framer` | Frame business questions as structured DS problems |
| `data-profiler` | Profile datasets for quality, structure, and anomalies |
| `feature-engineer` | Design and evaluate feature transformations |
| `pipeline-builder` | Assess raw data quality and design preprocessing pipelines |

### Modeling (2)

| Agent | Description |
|-------|-------------|
| `experiment-designer` | Design rigorous experiments with hypotheses and evaluation plans |
| `model-evaluator` | Evaluate performance with slicing, calibration, and fairness checks |

### Review (3)

| Agent | Description |
|-------|-------------|
| `documentation-synthesizer` | Synthesize findings into reusable learning documents |
| `reproducibility-auditor` | Audit experiments for reproducibility (seeds, versions, data hashes) |
| `deployment-readiness` | Evaluate models for production deployment readiness |

## Commands

| Command | Description |
|---------|-------------|
| `/ds:plan` | Search past learnings, frame the problem, plan the approach, output a plan doc |
| `/ds:preprocess` | Assess data quality, design and execute preprocessing pipelines, output preprocessing report |
| `/ds:validate` | Run data quality validation with Great Expectations, pandas, or data contracts, output validation report |
| `/ds:eda` | Profile data, analyze distributions, check quality, output an EDA report |
| `/ds:experiment` | Formulate hypothesis, design methodology, check for leakage, output experiment plan and results |
| `/ds:review` | Peer review experiments for methodology, leakage, reproducibility, and statistical validity |
| `/ds:ship` | Assess deployment readiness, generate model card and deployment documentation |
| `/ds:compound` | Extract learnings from completed work, categorize, and save to docs/ds/learnings/ |

## Skills

| Skill | Description |
|-------|-------------|
| `eda-checklist` | Systematic EDA methodology covering structure, quality, distributions, relationships |
| `split-strategy` | Train/validation/test split decision tree based on data characteristics |
| `target-leakage-detection` | Detect temporal, direct, and group leakage in feature sets |
| `experiment-tracking` | Standard experiment logging format with environment and reproducibility fields |
| `statistical-analysis` | Guided statistical analysis with test selection, assumption checking, power analysis, and APA reporting |
| `scikit-learn` | Scikit-learn API patterns for preprocessing, pipelines, model selection, and evaluation |
| `statsmodels` | Statsmodels API patterns for OLS, GLM, discrete choice, time series (ARIMA/SARIMAX), and diagnostics |
| `matplotlib` | Matplotlib API patterns for creating publication-quality visualizations, multi-panel figures, and plot styling |
| `setup` | Check Python environment for required DS/ML libraries and report versions |
| `aeon` | Aeon API patterns for time series ML -- classification, regression, clustering, anomaly detection, segmentation, and similarity search |
| `exploratory-data-analysis` | Detect file types and perform format-specific EDA across 200+ scientific formats |
| `reproducibility-checklist` | Verify experiment reproducibility: seeds, versions, data hashes, environment capture |
| `shap` | SHAP API patterns for model interpretability -- explainer selection, feature attribution, and visualization |
| `model-card` | Generate standardized model documentation following HuggingFace and NVIDIA Model Card++ formats |
| `pandas-pro` | Pandas API patterns for DataFrame operations, data cleaning, aggregation, merging, and performance optimization |
| `data-preprocessing` | Pre-model data preparation pipelines for cleaning, validation, transformation, and ETL orchestration |
| `data-quality-frameworks` | Data quality validation with Great Expectations, dbt tests, and data contracts |
| `polars` | Polars expression API for high-performance DataFrame operations, lazy evaluation, joins, aggregations, and I/O |
| `tuning-hyperparameters` | Hyperparameter tuning workflow -- strategy selection, Bayesian optimization with Optuna, search space design, and result analysis |

## Templates

| Template | Description |
|----------|-------------|
| `problem-framing` | Problem definition document |
| `experiment-plan` | Experiment design document |
| `experiment-result` | Experiment result report |
| `experiment-review` | Peer review assessment with methodology, leakage, and reproducibility checks |
| `model-card` | Standardized model documentation for deployment handoff |
| `deployment-readiness` | Deployment readiness assessment with monitoring and rollback plans |
| `preprocessing-report` | Data preprocessing pipeline execution report with before/after metrics |
| `validation-report` | Data quality validation results with per-expectation outcomes and quality dimensions |
| `postmortem` | Project learnings and retrospective |

## MCP Servers

| Server | Description |
|--------|-------------|
| `context7` | Framework documentation lookup for DS/ML libraries |

## Example Usage

### Starting a new project

```
/ds:plan We need to predict customer churn for our SaaS product.
         We have 2 years of usage logs, billing data, and support tickets.
         The business wants to identify at-risk customers 30 days before they cancel.
```

### Preprocessing raw data

```
/ds:preprocess ./data/raw/customers.csv
```

### Validating data quality

```
/ds:validate ./data/preprocessed/customers-clean.csv
```

### Exploring a dataset

```
/ds:eda ./data/customers.parquet
```

### Running an experiment

```
/ds:experiment Hypothesis: Adding rolling 7-day usage features will improve
               churn prediction AUC by >2% over the baseline feature set.
```

### Reviewing an experiment

```
/ds:review docs/ds/experiments/2026-02-24-churn-xgb-result.md
```

### Shipping a model

```
/ds:ship docs/ds/experiments/2026-02-24-churn-xgb-result.md
```

### Capturing learnings

```
/ds:compound The churn experiment showed that recency features (days since
             last login, days since last support ticket) were more predictive
             than aggregate features (total logins, total tickets).
```

## Compounding Mechanism

The plugin creates `docs/ds/learnings/` in your project with YAML-frontmattered files. `/ds:plan` and `/ds:experiment` search these before starting new work.

```
docs/ds/learnings/
  2026-02-24-churn-recency-features.md
  2026-02-20-temporal-split-gotcha.md
  2026-02-15-xgboost-tabular-ranges.md
```

Over time, your learnings directory becomes an institutional knowledge base that makes every new project faster.

## Philosophy

**Each experiment should make the next one easier.**

Traditional data science accumulates technical debt: notebooks that can't be reproduced, experiments that repeat past failures, and learnings trapped in individual heads. This plugin inverts that:

- Frame problems thoroughly before modeling
- Review to catch methodological issues early
- Compound learnings so they're reusable
- Ship with documentation so models are maintainable

## License

MIT

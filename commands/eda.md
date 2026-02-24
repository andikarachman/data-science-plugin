---
name: eda
description: Profile a dataset for structure, quality, distributions, and anomalies, then output an EDA report
argument-hint: "[path to dataset or description of data source]"
disable-model-invocation: true
---

# Guided Exploratory Data Analysis

## Input

<data_source> $ARGUMENTS </data_source>

**If the data source above is empty, ask the user:** "What dataset do you want to explore? Provide a file path (CSV, Parquet) or describe the data source."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: data` learnings related to this dataset or domain.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

### 2. Load Data

Read the dataset (CSV, Parquet, or database query). If path not provided, ask.

**Large dataset handling:** If the dataset exceeds 100MB, sample at 100K rows and report: "Dataset exceeds 100MB. Sampling 100K rows for profiling. Full dataset has N rows."

### 3. Structural Profiling

Use the `data-profiler` agent:
- Row/column counts, dtypes, memory usage
- Missing value rates per column
- Cardinality of categorical columns
- Numeric summary statistics (mean, median, std, min, max, percentiles)

### 4. Distribution Analysis

For each feature:
- Numeric: distribution shape, outliers (IQR method), skewness
- Categorical: value counts, rare categories
- Temporal: time range, gaps, seasonality signals

### 5. Data Quality Checks

Apply the `eda-checklist` skill. Flag:
- Duplicates
- Constant columns
- High-cardinality categoricals
- Suspicious distributions
- Potential leakage columns

#### 5a. Target Leakage Detection

When target column is identified, invoke the `target-leakage-detection` skill to check for features with suspiciously high target correlation.

#### 5b. Feature Engineering Suggestions

After distribution analysis, use the `feature-engineer` agent to suggest feature transformations based on the observed data characteristics.

### 6. Relationship Analysis

Correlation matrix for numeric features, association tests for categoricals, target correlation ranking.

### 7. Write Artifact

Generate an EDA report at `docs/ds/eda/YYYY-MM-DD-<dataset-name>-eda.md` with findings, visualization descriptions, and recommended next steps.

Create the directory if needed: `mkdir -p docs/ds/eda/`

### 8. Next Steps

Ask the user: "EDA complete. What next?" with options:
- Feature engineering
- Run experiment (`/ds:experiment`)
- Investigate specific finding

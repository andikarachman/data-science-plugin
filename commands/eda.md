---
name: ds:eda
description: Profile a dataset for structure, quality, distributions, and anomalies, then output an EDA report
argument-hint: "[path to dataset or description of data source]"
---

# Guided Exploratory Data Analysis

## Input

<data_source> $ARGUMENTS </data_source>

**If the data source above is empty, ask the user:** "What dataset do you want to explore? Provide a file path (CSV, Parquet, HDF5, FASTA, or any scientific format) or describe the data source."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: data` learnings related to this dataset or domain.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

### 2. File Type Detection

Use the `exploratory-data-analysis` skill to detect the file type from its extension and load format-specific guidance from the skill's reference files.

**Routing:**
- **Tabular data** (CSV, Parquet, Excel, TSV) -- proceed to step 3 (the standard tabular EDA path).
- **Scientific formats** (HDF5, FASTA, PDB, NetCDF, mzML, TIFF, etc.) -- follow the `exploratory-data-analysis` skill's format-specific workflow (file type detection, format-specific analysis, quality assessment), then skip directly to step 8 to write the report.

### 3. Load Data (tabular path)

Read the dataset (CSV, Parquet, or database query). If path not provided, ask.

**Large dataset handling:** If the dataset exceeds 100MB, sample at 100K rows and report: "Dataset exceeds 100MB. Sampling 100K rows for profiling. Full dataset has N rows."

### 4. Structural Profiling (tabular path)

Use the `data-profiler` agent for deep tabular profiling:
- Row/column counts, dtypes, memory usage
- Missing value rates per column (with MCAR/MAR/MNAR assessment)
- Cardinality of categorical columns
- Numeric summary statistics (mean, median, std, min, max, percentiles)

The `data-profiler` agent handles tabular-specific profiling. The `exploratory-data-analysis` skill handles format detection and non-tabular files -- they do not overlap.

### 5. Distribution Analysis (tabular path)

For each feature:
- Numeric: distribution shape, outliers (IQR method), skewness
- Categorical: value counts, rare categories
- Temporal: time range, gaps, seasonality signals

### 6. Data Quality Checks (tabular path)

Apply the `eda-checklist` skill. Flag:
- Duplicates
- Constant columns
- High-cardinality categoricals
- Suspicious distributions
- Potential leakage columns

#### 6a. Target Leakage Detection

When target column is identified, invoke the `target-leakage-detection` skill to check for features with suspiciously high target correlation.

#### 6b. Feature Engineering Suggestions

After distribution analysis, use the `feature-engineer` agent to suggest feature transformations based on the observed data characteristics.

After suggestions are generated, reference the `scikit-learn` skill's `references/preprocessing.md` for concrete implementation patterns (scaling, encoding, imputation) matching the identified data characteristics.

### 7. Relationship Analysis (tabular path)

Correlation matrix for numeric features, association tests for categoricals, target correlation ranking.

#### 7a. Multicollinearity Check

Compute VIF (variance inflation factor) for numeric features. Reference the `statsmodels` skill's `references/stats_diagnostics.md` for `variance_inflation_factor` patterns. Flag features with VIF > 10.

#### 7b. Stationarity Testing (if temporal columns detected)

If temporal columns were identified in step 5, test for stationarity using ADF and KPSS tests. Reference the `statsmodels` skill's `references/time_series.md` for stationarity testing patterns.

### 8. Write Artifact

Generate an EDA report at `docs/ds/eda/YYYY-MM-DD-<dataset-name>-eda.md`. Use the `exploratory-data-analysis` skill's `assets/report_template.md` as a structural guide. Include:
- Learnings applied (from step 1)
- File type and format details (from step 2)
- All profiling findings (from steps 3-7 for tabular, or from the skill's format-specific analysis for scientific formats)
- Recommended next steps in the ds workflow

Create the directory if needed: `mkdir -p docs/ds/eda/`

### 9. Next Steps

Ask the user: "EDA complete. What next?" with options:
- Feature engineering
- Run experiment (`/ds:experiment`)
- Investigate specific finding

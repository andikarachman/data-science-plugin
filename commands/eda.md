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

Read the dataset (CSV, Parquet, or database query). If path not provided, ask. For efficient data loading with dtype specification and chunked reading for large files, reference the `pandas-pro` skill's `references/performance-optimization.md` (I/O Optimization section).

**Large dataset handling:** If the dataset exceeds 100MB, sample at 100K rows and report: "Dataset exceeds 100MB. Sampling 100K rows for profiling. Full dataset has N rows."

### 4. Structural Profiling (tabular path)

Use the `data-profiler` agent for deep tabular profiling. For proper DataFrame inspection patterns (`.info()`, `.memory_usage(deep=True)`, dtype checking), reference the `pandas-pro` skill's `references/dataframe-operations.md`:
- Row/column counts, dtypes, memory usage
- Missing value rates per column (with MCAR/MAR/MNAR assessment)
- Cardinality of categorical columns
- Numeric summary statistics (mean, median, std, min, max, percentiles)

The `data-profiler` agent handles tabular-specific profiling. The `exploratory-data-analysis` skill handles format detection and non-tabular files -- they do not overlap.

### 5. Distribution Analysis (tabular path)

For each feature, use groupby-based distribution computation patterns from the `pandas-pro` skill's `references/aggregation-groupby.md` (GroupBy Fundamentals, Transform sections):
- Numeric: distribution shape, outliers (IQR method), skewness
- Categorical: value counts, rare categories
- Temporal: time range, gaps, seasonality signals

Generate distribution visualizations using the `matplotlib` skill's `references/plot_types.md`:
- Histograms with density overlay for numeric features (Section 4)
- Box plots for outlier visualization (Section 5)
- Violin plots for distribution shape comparison across groups (Section 5)

For standard statistical distribution comparison, prefer seaborn where available; fall back to matplotlib subplots for custom layouts. Save plots to the same output directory as the EDA report.

When temporal columns are detected, suggest time-series feature extraction using the `aeon` skill's `references/transformations.md`: Catch22 for an interpretable 22-feature summary of each series, ROCKET/MiniROCKET for fast scalable feature extraction suitable for downstream ML.

### 6. Data Quality Checks (tabular path)

**Check for existing validation:** Search `docs/ds/validations/` for a validation report matching this dataset (by filename or data hash). If found, report: "Found prior validation report: [path]. Loading quality findings." Use those findings to skip redundant checks and focus on dimensions not yet covered. If not found, proceed with the full checklist.

Apply the `eda-checklist` skill. Flag:
- Duplicates
- Constant columns
- High-cardinality categoricals
- Suspicious distributions
- Potential leakage columns

For formal quality validation with Great Expectations expectation suites or data contracts, recommend running `/ds:validate`. Reference the `data-quality-frameworks` skill's quality dimensions table (completeness, uniqueness, validity, accuracy, consistency, timeliness) for comprehensive quality assessment.

#### 6a. Target Leakage Detection

When target column is identified, invoke the `target-leakage-detection` skill to check for features with suspiciously high target correlation.

#### 6b. Feature Engineering Suggestions

After distribution analysis, use the `feature-engineer` agent to suggest feature transformations based on the observed data characteristics.

After suggestions are generated, reference the `scikit-learn` skill's `references/preprocessing.md` for concrete implementation patterns (scaling, encoding, imputation) matching the identified data characteristics.

**Preprocessing routing guidance:** For in-model preprocessing (scaling, encoding, imputation inside an sklearn Pipeline that participates in cross-validation), use the `scikit-learn` skill. For full pre-model ETL preprocessing (deduplication, format conversion, schema validation, structural cleaning), recommend running `/ds:preprocess` first. Reference the `data-preprocessing` skill's `references/transformation_methods.md` for pre-model transform patterns when structural data issues remain.

### 7. Relationship Analysis (tabular path)

Correlation matrix for numeric features, association tests for categoricals, target correlation ranking. For multi-table correlation analysis and dataset joining patterns, reference the `pandas-pro` skill's `references/merging-joining.md`.

Generate relationship visualizations using the `matplotlib` skill:
- Correlation heatmap with annotations -- reference `references/plot_types.md` (Section 6, Correlation Matrix) or prefer `seaborn.heatmap()` for concise API
- Scatter plots for top feature pairs -- reference `references/plot_types.md` (Section 2)

#### 7a. Multicollinearity Check

Compute VIF (variance inflation factor) for numeric features. Reference the `statsmodels` skill's `references/stats_diagnostics.md` for `variance_inflation_factor` patterns. Flag features with VIF > 10.

#### 7b. Stationarity Testing (if temporal columns detected)

If temporal columns were identified in step 5, test for stationarity using ADF and KPSS tests. Reference the `statsmodels` skill's `references/time_series.md` for stationarity testing patterns.

If multiple time series are present, suggest time-series similarity analysis using the `aeon` skill's `references/distances.md` for DTW pairwise distance computation. If change points are suspected, reference the `aeon` skill's `references/segmentation.md` for ClaSP or FLUSS segmenters to detect regime changes.

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

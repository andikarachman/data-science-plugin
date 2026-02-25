---
name: data-preprocessing
description: "Pre-model data preparation pipelines for cleaning, validation, transformation, and ETL orchestration. Use when raw data needs deduplication, schema validation, format conversion, or quality assurance before EDA or modeling."
disable-model-invocation: true
---

# Data Preprocessing

## Overview

This skill provides patterns for building and executing automated data preprocessing pipelines. It covers pre-model data preparation -- everything that happens to raw data *before* it enters a machine learning pipeline. Use this skill for data cleaning, schema validation, format conversion, deduplication, and ETL orchestration.

**Role in the ds plugin:** This skill is invoked by `/ds:preprocess` as the primary pipeline construction and execution reference, by `/ds:eda` at step 6b for pre-model data preparation patterns emerging from profiling, and by `/ds:experiment` at steps 3 and 6 for data preparation code outside sklearn Pipelines. It provides concrete pipeline patterns complementing the `pipeline-builder` agent (which assesses data quality and recommends pipeline steps) and the `scikit-learn` skill (which handles in-model preprocessing inside sklearn Pipelines). For pre-model data preparation (deduplication, format conversion, schema validation, structural cleaning, statistical imputation, text processing, outlier handling, ETL orchestration), use this skill. For in-model preprocessing that participates in cross-validation (StandardScaler, SimpleImputer, OneHotEncoder inside an sklearn Pipeline), use the `scikit-learn` skill. **Imputation boundary:** This skill provides pre-model imputation (fill missing values before EDA or profiling begins, applied to the entire dataset once). The `scikit-learn` skill provides in-model imputation inside sklearn Pipelines (participates in cross-validation folds, preventing data leakage from test to train). Use pre-model imputation when you need complete data for profiling; use in-model imputation when imputation must respect train/test boundaries.

## When to Use This Skill

Use this skill when:

- Raw data needs cleaning before any analysis (duplicates, format issues, structural problems)
- Data requires schema validation (column presence, types, value ranges)
- Multiple data sources need joining or format conversion (ETL)
- Rows or columns with high missing rates need structural removal
- Missing values need pre-model filling (median, mode, or KNN imputation before EDA)
- Text columns need extraction or cleaning (extract numbers, emails, remove special characters)
- String columns need normalization (whitespace, case, encoding)
- Date columns need parsing and timezone alignment
- Outliers need handling (removal via IQR/Z-score, or capping via winsorization)
- Data quality assurance checks are needed before EDA or modeling
- Large datasets (>100MB) need chunked processing

Do NOT use this skill for:

- In-model preprocessing (scaling, encoding, imputation inside sklearn Pipelines that participates in cross-validation) -- use the `scikit-learn` skill
- Data profiling and characterization -- use the `data-profiler` agent
- Feature engineering (creating new features from existing ones) -- use the `feature-engineer` agent
- Statistical analysis of data quality -- use the `statistical-analysis` skill

## Core Capabilities

### 1. Data Cleaning

Remove structural data quality issues before analysis or modeling.

**Deduplication:**

```python
import pandas as pd
import hashlib

def deduplicate(df, subset=None, keep="first"):
    """Remove duplicate rows.

    Args:
        df: Input DataFrame.
        subset: Columns to consider for duplicates. None = all columns.
        keep: Which duplicate to keep ('first', 'last', False = drop all).

    Returns:
        Cleaned DataFrame and count of removed rows.
    """
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    n_removed = n_before - len(df_clean)
    return df_clean, n_removed
```

**Structural missing data handling:**

```python
def drop_high_missing(df, row_threshold=0.9, col_threshold=0.9):
    """Drop rows/columns with missing rates above threshold.

    This is structural cleaning, not modeling-level imputation.
    For imputation inside sklearn Pipelines, use the scikit-learn skill.

    Args:
        df: Input DataFrame.
        row_threshold: Drop rows with missing rate above this (0-1).
        col_threshold: Drop columns with missing rate above this (0-1).

    Returns:
        Cleaned DataFrame, dropped column names, dropped row count.
    """
    # Drop columns first (reduces data before row check)
    col_missing = df.isnull().mean()
    cols_to_drop = col_missing[col_missing > col_threshold].index.tolist()
    df_clean = df.drop(columns=cols_to_drop)

    # Drop rows
    row_missing = df_clean.isnull().mean(axis=1)
    rows_to_drop = row_missing[row_missing > row_threshold]
    df_clean = df_clean.drop(index=rows_to_drop.index)

    return df_clean, cols_to_drop, len(rows_to_drop)
```

**String normalization:**

```python
def normalize_strings(df, columns=None):
    """Normalize string columns: strip whitespace, lowercase.

    Args:
        df: Input DataFrame.
        columns: String columns to normalize. None = auto-detect.

    Returns:
        DataFrame with normalized strings.
    """
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()

    df_clean = df.copy()
    for col in columns:
        df_clean[col] = df_clean[col].str.strip().str.lower()
    return df_clean
```

**Pre-model imputation:**

Fill missing values before EDA or profiling. For in-model imputation inside sklearn Pipelines (which participates in cross-validation), use the `scikit-learn` skill.

```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder

def impute_median(df, columns):
    """Impute missing numeric values with column median.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to impute.

    Returns:
        Cleaned DataFrame, dict of {column: values_filled}.
    """
    df_clean = df.copy()
    imputer = SimpleImputer(strategy="median")
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        if df_clean[col].isnull().any():
            df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
    return df_clean

def impute_mode(df, columns):
    """Impute missing categorical values with mode (most frequent).

    Args:
        df: Input DataFrame.
        columns: Categorical columns to impute.

    Returns:
        Cleaned DataFrame, dict of {column: values_filled}.
    """
    df_clean = df.copy()
    for col in columns:
        if not df_clean[col].dropna().empty:
            mode_val = df_clean[col].mode()
            if len(mode_val) > 0:
                df_clean[col] = df_clean[col].fillna(mode_val[0])
    return df_clean

def impute_knn(df, target_features, n_neighbors=5):
    """KNN imputation using correlated features.

    Uses LabelEncoder for categorical features before KNN.

    Args:
        df: Input DataFrame.
        target_features: Dict of {column: {'features': [...], 'type': 'numeric'|'categorical'|'binary'}}.
        n_neighbors: Number of neighbors.

    Returns:
        Cleaned DataFrame.
    """
    # See scripts/transform_data.py for full implementation
    # with LabelEncoder encoding/decoding for mixed types
```

**Text processing:**

```python
import re

def process_text(df, columns, operation="extract_numbers"):
    """Apply text processing operations.

    Args:
        df: Input DataFrame.
        columns: Text columns to process.
        operation: 'extract_numbers', 'clean_whitespace', 'extract_email',
            'lowercase', 'remove_special'.

    Returns:
        Cleaned DataFrame.
    """
    df_clean = df.copy()
    for col in columns:
        if operation == "extract_numbers":
            df_clean[col] = df_clean[col].astype(str).apply(
                lambda x: re.search(r"\d+", x).group() if re.search(r"\d+", x) else None
            )
        elif operation == "clean_whitespace":
            df_clean[col] = df_clean[col].astype(str).str.strip()
        elif operation == "extract_email":
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            df_clean[col] = df_clean[col].astype(str).apply(
                lambda x: re.search(pattern, x).group() if re.search(pattern, x) else None
            )
        elif operation == "lowercase":
            df_clean[col] = df_clean[col].astype(str).str.lower()
        elif operation == "remove_special":
            df_clean[col] = df_clean[col].astype(str).apply(
                lambda x: re.sub(r"[^a-zA-Z0-9\s]", "", x)
            )
    return df_clean
```

### 2. Data Validation

Validate data against schemas and rules.

```python
def validate_schema(df, schema):
    """Validate DataFrame against a column schema.

    Args:
        df: Input DataFrame.
        schema: Dict of {column_name: {"dtype": str, "nullable": bool, "min": num, "max": num}}.

    Returns:
        List of validation errors (empty = valid).
    """
    errors = []

    # Check required columns
    for col, rules in schema.items():
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
            continue

        # Type check
        if "dtype" in rules:
            if not df[col].dtype.name.startswith(rules["dtype"]):
                errors.append(f"Column '{col}': expected {rules['dtype']}, got {df[col].dtype}")

        # Null check
        if not rules.get("nullable", True) and df[col].isnull().any():
            n_null = df[col].isnull().sum()
            errors.append(f"Column '{col}': {n_null} null values in non-nullable column")

        # Range check
        if "min" in rules and df[col].min() < rules["min"]:
            errors.append(f"Column '{col}': min value {df[col].min()} below {rules['min']}")
        if "max" in rules and df[col].max() > rules["max"]:
            errors.append(f"Column '{col}': max value {df[col].max()} above {rules['max']}")

    return errors
```

**See:** `references/data_validation_schemas.md` for comprehensive validation patterns.

### 3. Data Transformation

Pre-model transformations that prepare data structurally.

**Type coercion:**

```python
def coerce_types(df, type_map):
    """Coerce column types safely.

    Args:
        df: Input DataFrame.
        type_map: Dict of {column_name: target_type}.
            target_type: 'numeric', 'datetime', 'category', 'string'.

    Returns:
        DataFrame with coerced types, list of columns that failed coercion.
    """
    df_clean = df.copy()
    failed = []

    for col, target in type_map.items():
        if col not in df_clean.columns:
            failed.append((col, "column not found"))
            continue
        try:
            if target == "numeric":
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            elif target == "datetime":
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
            elif target == "category":
                df_clean[col] = df_clean[col].astype("category")
            elif target == "string":
                df_clean[col] = df_clean[col].astype(str)
        except Exception as e:
            failed.append((col, str(e)))

    return df_clean, failed
```

**Outlier handling (structural, pre-model):**

Four methods for different scenarios. For outlier-robust scaling inside sklearn Pipelines, use `RobustScaler` from the `scikit-learn` skill.

```python
import numpy as np

def remove_outliers_iqr(df, columns, factor=1.5):
    """Remove rows with outliers using the IQR method.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to check.
        factor: IQR multiplier (1.5 = standard, 3.0 = extreme only).

    Returns:
        Cleaned DataFrame, number of rows removed.
    """
    mask = pd.Series(True, index=df.index)
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        mask &= df[col].between(lower, upper)
    return df[mask].copy(), (~mask).sum()

def cap_outliers_iqr(df, columns, factor=1.5):
    """Cap outliers at IQR bounds (winsorization).

    Preserves all rows by clipping extreme values to the fence.
    Use instead of removal when losing rows is costly.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to cap.
        factor: IQR multiplier (1.5 = standard, 3.0 = extreme only).

    Returns:
        Cleaned DataFrame, bounds dict.
    """
    df_clean = df.copy()
    for col in columns:
        q1, q3 = df_clean[col].quantile(0.25), df_clean[col].quantile(0.75)
        iqr = q3 - q1
        df_clean[col] = df_clean[col].clip(q1 - factor * iqr, q3 + factor * iqr)
    return df_clean

def remove_outliers_zscore(df, columns, threshold=3.0):
    """Remove rows with outliers using Z-score method.

    Best for approximately normal distributions.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to check.
        threshold: Z-score threshold (3.0 = ~99.7% of data).

    Returns:
        Cleaned DataFrame, number of rows removed.
    """
    mask = pd.Series(True, index=df.index)
    for col in columns:
        z = np.abs((df[col] - df[col].mean()) / df[col].std())
        mask &= z < threshold
    return df[mask].copy(), (~mask).sum()
```

**Outlier method selection:**

| Method | When to use | Row impact |
|--------|------------|------------|
| `remove_outliers_iqr` | General-purpose, non-normal data | Removes rows |
| `cap_outliers_iqr` | Preserve all rows, cap extreme values | No rows removed |
| `remove_outliers_zscore` | Normal distributions, parametric analysis | Removes rows |
| `clip_outliers` | Percentile-based clipping (arbitrary bounds) | No rows removed |

**See:** `references/transformation_methods.md` for the full pre-model transformation catalog.

### 4. Pipeline Orchestration

Build multi-step preprocessing pipelines with tracking.

```python
import time
import hashlib

def compute_hash(df):
    """Compute SHA-256 hash of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()

def run_pipeline(df, steps):
    """Execute a preprocessing pipeline with per-step tracking.

    Args:
        df: Input DataFrame.
        steps: List of (step_name, function, kwargs) tuples.
            Each function takes df as first arg and returns (df, info_dict).

    Returns:
        Processed DataFrame, execution log (list of step results).
    """
    log = []
    current = df.copy()

    for step_name, func, kwargs in steps:
        n_before = len(current)
        t_start = time.time()

        try:
            current, info = func(current, **kwargs)
            elapsed = time.time() - t_start
            log.append({
                "step": step_name,
                "status": "success",
                "rows_in": n_before,
                "rows_out": len(current),
                "elapsed_seconds": round(elapsed, 3),
                "info": info,
            })
        except Exception as e:
            elapsed = time.time() - t_start
            log.append({
                "step": step_name,
                "status": "failed",
                "rows_in": n_before,
                "rows_out": n_before,
                "elapsed_seconds": round(elapsed, 3),
                "error": str(e),
            })
            # Stop pipeline on failure, preserve partial output
            break

    return current, log
```

**See:** `references/pipeline_configuration.md` for step sequencing, column-type routing, and checkpointing patterns.

### 5. Time-Series-Aware Preprocessing

When data has temporal columns, apply temporal constraints:

```python
def temporal_sort(df, time_col):
    """Sort by time column and reset index."""
    return df.sort_values(time_col).reset_index(drop=True)

def resample_timeseries(df, time_col, freq, agg="mean"):
    """Resample time series to a fixed frequency.

    Args:
        df: Input DataFrame.
        time_col: Name of the datetime column.
        freq: Target frequency ('1h', '1D', '1W', etc.).
        agg: Aggregation method ('mean', 'sum', 'last', etc.).

    Returns:
        Resampled DataFrame.
    """
    df_ts = df.set_index(time_col)
    return df_ts.resample(freq).agg(agg).reset_index()
```

**Temporal preprocessing constraints:**
- Sort data by time before any transformation
- Never use future values for imputation (use forward-fill or rolling mean with lookback only)
- Fit normalizers on the training window only (pass training statistics to test set)
- Apply stationarity transforms (differencing, log) before modeling, record the transform for inversion
- When reshaping for aeon time-series ML, target shape is `(n_samples, n_channels, n_timepoints)` -- reference the `aeon` skill

### 6. Large Dataset Handling

For datasets exceeding 100MB:

```python
def process_in_chunks(filepath, steps, chunksize=50000):
    """Process a large CSV file in chunks.

    Args:
        filepath: Path to the CSV file.
        steps: Pipeline steps to apply per chunk.
        chunksize: Number of rows per chunk.

    Returns:
        Combined processed DataFrame (or path if too large for memory).
    """
    chunks = []
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        processed, _ = run_pipeline(chunk, steps)
        chunks.append(processed)

    return pd.concat(chunks, ignore_index=True)
```

**Large dataset strategy:**
- Detect file size before loading (`os.path.getsize()`)
- If >100MB, report size to user and suggest chunked processing
- If >1GB, recommend sampling for initial assessment, then chunked processing for full pipeline
- Track memory usage during pipeline execution

## Common Workflows

### Workflow 1: Clean a CSV for Analysis

```python
import pandas as pd

# Load
df = pd.read_csv("raw_data.csv")

# Define pipeline
steps = [
    ("deduplicate", deduplicate_step, {"subset": None, "keep": "first"}),
    ("drop_high_missing_cols", drop_cols_step, {"threshold": 0.9}),
    ("normalize_strings", normalize_step, {"columns": None}),
    ("coerce_types", coerce_step, {"type_map": {"age": "numeric", "date": "datetime"}}),
    ("validate", validate_step, {"schema": schema}),
]

# Execute
df_clean, log = run_pipeline(df, steps)

# Save
input_hash = compute_hash(df)
output_hash = compute_hash(df_clean)
df_clean.to_csv("cleaned_data.csv", index=False)
```

### Workflow 2: ETL from Multiple Sources

```python
# Extract
customers = pd.read_csv("customers.csv")
orders = pd.read_parquet("orders.parquet")

# Transform each source
customers_clean, _ = run_pipeline(customers, customer_steps)
orders_clean, _ = run_pipeline(orders, order_steps)

# Join
merged = customers_clean.merge(orders_clean, on="customer_id", how="inner")

# Validate merged output
errors = validate_schema(merged, merged_schema)
if errors:
    print(f"Validation errors: {errors}")

# Load
output_hash = compute_hash(merged)
merged.to_parquet("merged_data.parquet", index=False)
```

### Workflow 3: Time-Series Data Preparation

```python
# Load and sort
df = pd.read_csv("sensor_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = temporal_sort(df, "timestamp")

# Resample to fixed frequency
df_resampled = resample_timeseries(df, "timestamp", freq="1h", agg="mean")

# Forward-fill gaps (no future leakage)
df_resampled = df_resampled.fillna(method="ffill")

# Validate no remaining gaps
assert df_resampled.isnull().sum().sum() == 0
```

## Best Practices

1. **Always validate before and after** -- Run schema validation on input to catch issues early, and on output to confirm the pipeline produced valid data.
2. **Track data hashes** -- Compute SHA-256 hashes of input and output DataFrames for reproducibility.
3. **Log per-step metrics** -- Track rows in/out, execution time, and values modified for each pipeline step.
4. **Stop on failure** -- When a step fails, preserve partial output and report the error. Do not silently continue.
5. **Non-destructive processing** -- Write preprocessed data to a new file. Never overwrite the original data source.
6. **Temporal awareness** -- When data has time columns, sort by time first and never impute with future values.
7. **Document transformations** -- Record exactly what transformations were applied so they can be reproduced.

## Error Handling

**See:** `references/error_handling_strategies.md` for failure modes, recovery patterns, and strict vs permissive validation modes.

## Reference Documentation

### Pipeline Configuration
**File:** `references/pipeline_configuration.md`
- Step sequencing and ordering
- Column-type routing (numeric vs categorical vs temporal)
- Configuration patterns
- Checkpointing between steps

### Transformation Methods
**File:** `references/transformation_methods.md`
- Complete pre-model transformation catalog
- Deduplication strategies
- Type coercion patterns
- Outlier handling
- String and date cleaning

### Data Validation Schemas
**File:** `references/data_validation_schemas.md`
- Schema definition patterns
- Column presence and type checks
- Range and constraint validation
- Custom rule definitions

### Error Handling Strategies
**File:** `references/error_handling_strategies.md`
- Failure modes and recovery
- Strict vs permissive validation
- Partial output preservation
- Error reporting format

## Example Scripts

### Pipeline Orchestrator

Run a complete preprocessing pipeline with tracking:

```bash
python scripts/pipeline.py
```

### Data Validator

Validate data against a schema:

```bash
python scripts/validate_data.py
```

### Data Transformer

Apply transformations to a dataset:

```bash
python scripts/transform_data.py
```

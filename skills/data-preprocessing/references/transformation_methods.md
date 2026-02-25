# Transformation Methods

Pre-model transformation catalog for the `data-preprocessing` skill. These transforms operate on raw data *before* it enters an sklearn Pipeline.

For in-model transformations (scaling, encoding, imputation that participates in cross-validation), use the `scikit-learn` skill's `references/preprocessing.md`.

## Deduplication

### Exact Deduplication

Remove rows that are identical across all or a subset of columns.

```python
def deduplicate_exact(df, subset=None, keep="first"):
    """Remove exact duplicate rows.

    Args:
        subset: Columns to check. None = all columns.
        keep: 'first' (keep earliest), 'last' (keep latest), False (drop all).

    Returns:
        (cleaned_df, {"duplicates_removed": int})
    """
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}
```

### Subset-Based Deduplication

Deduplicate based on business keys while keeping the most recent or complete record.

```python
def deduplicate_by_key(df, key_cols, sort_col=None, sort_ascending=False):
    """Keep one row per business key, preferring the most recent.

    Args:
        key_cols: Columns that define a unique entity.
        sort_col: Column to sort by before deduplication (e.g., 'updated_at').
        sort_ascending: Sort order for the tiebreaker column.

    Returns:
        (cleaned_df, {"duplicates_removed": int})
    """
    n_before = len(df)
    if sort_col:
        df = df.sort_values(sort_col, ascending=sort_ascending)
    df_clean = df.drop_duplicates(subset=key_cols, keep="first")
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}
```

## Missing Data -- Structural Handling

Structural missing data handling removes rows or columns with excessive missing values.

### Drop High-Missing Columns

```python
def drop_high_missing_cols(df, threshold=0.9):
    """Drop columns where missing rate exceeds threshold.

    Returns:
        (cleaned_df, {"columns_dropped": list, "missing_rates": dict})
    """
    missing_rates = df.isnull().mean()
    cols_to_drop = missing_rates[missing_rates > threshold].index.tolist()
    rates = {col: round(missing_rates[col], 4) for col in cols_to_drop}
    return df.drop(columns=cols_to_drop), {"columns_dropped": cols_to_drop, "missing_rates": rates}
```

### Drop High-Missing Rows

```python
def drop_high_missing_rows(df, threshold=0.5):
    """Drop rows where missing rate exceeds threshold.

    Returns:
        (cleaned_df, {"rows_dropped": int})
    """
    row_missing = df.isnull().mean(axis=1)
    mask = row_missing <= threshold
    return df[mask].copy(), {"rows_dropped": (~mask).sum()}
```

### Drop Constant Columns

```python
def drop_constant_columns(df):
    """Drop columns with a single unique value (no information).

    Returns:
        (cleaned_df, {"columns_dropped": list})
    """
    nunique = df.nunique()
    constant = nunique[nunique <= 1].index.tolist()
    return df.drop(columns=constant), {"columns_dropped": constant}
```

## Pre-Model Imputation

Pre-model imputation fills missing values before EDA or profiling begins. This is applied to the entire dataset once. For in-model imputation inside sklearn Pipelines (which participates in cross-validation folds), use the `scikit-learn` skill.

### Median Imputation

```python
from sklearn.impute import SimpleImputer

def impute_median(df, columns):
    """Impute missing numeric values with column median.

    Returns:
        (cleaned_df, {"strategy": "median", "filled": {col: count}})
    """
    df_clean = df.copy()
    imputer = SimpleImputer(strategy="median")
    filled = {}
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        n_missing = df_clean[col].isnull().sum()
        if n_missing > 0 and pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
            filled[col] = n_missing
    return df_clean, {"strategy": "median", "filled": filled}
```

### Mode Imputation

```python
def impute_mode(df, columns):
    """Impute missing categorical values with mode (most frequent).

    Returns:
        (cleaned_df, {"strategy": "mode", "filled": {col: count}})
    """
    df_clean = df.copy()
    filled = {}
    for col in columns:
        if df_clean[col].dropna().empty:
            continue
        n_missing = df_clean[col].isnull().sum()
        if n_missing > 0:
            mode_val = df_clean[col].mode()
            if len(mode_val) > 0:
                df_clean[col] = df_clean[col].fillna(mode_val[0])
                filled[col] = n_missing
    return df_clean, {"strategy": "mode", "filled": filled}
```

### KNN Imputation

```python
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder

def impute_knn(df, target_features, n_neighbors=5):
    """KNN-based imputation using correlated features.

    Handles mixed types by encoding categoricals with LabelEncoder
    before KNN, then decoding back.

    Args:
        target_features: Dict mapping target columns to configuration.
            Format: {
                'target_col': {
                    'features': ['col1', 'col2'],
                    'type': 'numeric' | 'categorical' | 'binary'
                }
            }
        n_neighbors: Number of neighbors.

    Returns:
        (cleaned_df, {"strategy": "knn", "n_neighbors": int, "filled": {col: count}})
    """
    # See scripts/transform_data.py for full implementation
```

**Imputation method selection:**

| Method | When to use | Data type |
|--------|------------|-----------|
| `impute_median` | Independent numeric columns, robust to outliers | Numeric |
| `impute_mode` | Independent categorical columns | Categorical |
| `impute_knn` | Columns with correlated features that can inform missing values | Mixed |

## Text Processing

Text processing operations for extracting structured data from text columns or cleaning text content.

### Text Operations

```python
import re

def process_text(df, columns, operation="extract_numbers"):
    """Apply text processing operations to specified columns.

    Args:
        columns: Text columns to process.
        operation: One of:
            - 'extract_numbers': Extract first numeric value from text
            - 'clean_whitespace': Strip leading/trailing whitespace
            - 'extract_email': Extract email address from text
            - 'lowercase': Convert to lowercase
            - 'remove_special': Remove non-alphanumeric characters

    Returns:
        (cleaned_df, {"operation": str, "processed_columns": list})
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
    return df_clean, {"operation": operation, "processed_columns": columns}
```

## Type Coercion

### String to Numeric

```python
def coerce_to_numeric(df, columns):
    """Convert string columns to numeric, setting unparseable values to NaN.

    Returns:
        (cleaned_df, {"coerced_columns": list, "failed_values": dict})
    """
    df_clean = df.copy()
    failed = {}
    for col in columns:
        original_nulls = df_clean[col].isnull().sum()
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        new_nulls = df_clean[col].isnull().sum() - original_nulls
        if new_nulls > 0:
            failed[col] = new_nulls
    return df_clean, {"coerced_columns": columns, "new_nulls_from_coercion": failed}
```

### Date Parsing

```python
def parse_dates(df, columns, format=None, utc=False):
    """Parse string columns to datetime.

    Args:
        columns: Columns to parse.
        format: Expected date format (e.g., '%Y-%m-%d'). None = auto-detect.
        utc: Convert to UTC timezone.

    Returns:
        (cleaned_df, {"parsed_columns": list, "failed_values": dict})
    """
    df_clean = df.copy()
    failed = {}
    for col in columns:
        original_nulls = df_clean[col].isnull().sum()
        df_clean[col] = pd.to_datetime(df_clean[col], format=format, errors="coerce", utc=utc)
        new_nulls = df_clean[col].isnull().sum() - original_nulls
        if new_nulls > 0:
            failed[col] = new_nulls
    return df_clean, {"parsed_columns": columns, "failed_parses": failed}
```

## String Cleaning

### Whitespace and Case Normalization

```python
def normalize_strings(df, columns=None, case="lower"):
    """Strip whitespace and normalize case.

    Args:
        columns: String columns. None = auto-detect object columns.
        case: 'lower', 'upper', 'title', or None (no case change).

    Returns:
        (cleaned_df, {"normalized_columns": list})
    """
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()

    df_clean = df.copy()
    for col in columns:
        df_clean[col] = df_clean[col].str.strip()
        if case == "lower":
            df_clean[col] = df_clean[col].str.lower()
        elif case == "upper":
            df_clean[col] = df_clean[col].str.upper()
        elif case == "title":
            df_clean[col] = df_clean[col].str.title()

    return df_clean, {"normalized_columns": columns}
```

### Replace Placeholder Values

```python
import numpy as np

def replace_placeholders(df, placeholders=None):
    """Replace common placeholder values with NaN.

    Args:
        placeholders: Values to treat as missing. Defaults to common placeholders.

    Returns:
        (cleaned_df, {"replacements": dict})
    """
    if placeholders is None:
        placeholders = ["", "N/A", "n/a", "NA", "na", "null", "NULL", "None", "none",
                        "-", "--", ".", "?", "unknown", "UNKNOWN", "missing", "MISSING"]

    df_clean = df.replace(placeholders, np.nan)
    replacements = {}
    for col in df.columns:
        diff = df[col].isin(placeholders).sum()
        if diff > 0:
            replacements[col] = diff

    return df_clean, {"replacements": replacements}
```

## Outlier Handling

### IQR-Based Removal

```python
def remove_outliers_iqr(df, columns, factor=1.5):
    """Remove rows with outliers using IQR method.

    For outlier-robust scaling (not removal), use RobustScaler from scikit-learn.

    Args:
        columns: Numeric columns to check.
        factor: 1.5 = standard, 3.0 = extreme only.

    Returns:
        (cleaned_df, {"rows_removed": int, "outlier_counts": dict})
    """
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        col_outliers = ~df[col].between(lower, upper)
        counts[col] = col_outliers.sum()
        mask &= ~col_outliers

    return df[mask].copy(), {"rows_removed": (~mask).sum(), "outlier_counts": counts}
```

### IQR-Based Capping (Winsorization)

```python
def cap_outliers_iqr(df, columns, factor=1.5):
    """Cap outliers at IQR bounds instead of removing rows.

    Preserves all rows by clipping extreme values to the fence.
    Use instead of removal when losing rows is costly.

    Args:
        columns: Numeric columns to cap.
        factor: IQR multiplier (1.5 = standard, 3.0 = extreme only).

    Returns:
        (cleaned_df, {"method": "iqr_cap", "factor": float, "bounds": dict})
    """
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        q1 = df_clean[col].quantile(0.25)
        q3 = df_clean[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        n_capped = ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
        df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)
        bounds[col] = {"lower": lower, "upper": upper, "capped": n_capped}
    return df_clean, {"method": "iqr_cap", "factor": factor, "bounds": bounds}
```

### Z-Score-Based Removal

```python
def remove_outliers_zscore(df, columns, threshold=3.0):
    """Remove rows with outliers using Z-score method.

    Best suited for approximately normal distributions.

    Args:
        columns: Numeric columns to check.
        threshold: Z-score threshold (3.0 = ~99.7% of data).

    Returns:
        (cleaned_df, {"method": "zscore", "threshold": float, "rows_removed": int, "outlier_counts": dict})
    """
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        mean, std = df[col].mean(), df[col].std()
        if std > 0:
            z_scores = np.abs((df[col] - mean) / std)
            col_outliers = z_scores >= threshold
            counts[col] = col_outliers.sum()
            mask &= ~col_outliers
    return df[mask].copy(), {"method": "zscore", "threshold": threshold, "rows_removed": (~mask).sum(), "outlier_counts": counts}
```

### Percentile-Based Clipping

```python
def clip_outliers(df, columns, lower_pct=0.01, upper_pct=0.99):
    """Clip values to percentile bounds instead of removing rows.

    Returns:
        (cleaned_df, {"clipped_columns": list, "bounds": dict})
    """
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        lower = df[col].quantile(lower_pct)
        upper = df[col].quantile(upper_pct)
        df_clean[col] = df_clean[col].clip(lower, upper)
        bounds[col] = {"lower": lower, "upper": upper}
    return df_clean, {"clipped_columns": columns, "bounds": bounds}
```

**Outlier method selection:**

| Method | When to use | Row impact |
|--------|------------|------------|
| `remove_outliers_iqr` | General-purpose, non-normal data | Removes rows |
| `cap_outliers_iqr` | Preserve all rows, cap extreme values | No rows removed |
| `remove_outliers_zscore` | Normal distributions, parametric analysis | Removes rows |
| `clip_outliers` | Percentile-based clipping (arbitrary bounds) | No rows removed |

## Column Operations

### Column Filtering

```python
def select_columns(df, keep=None, drop=None):
    """Select or drop columns.

    Args:
        keep: Columns to keep (exclusive with drop).
        drop: Columns to drop (exclusive with keep).

    Returns:
        (filtered_df, {"kept": list} or {"dropped": list})
    """
    if keep:
        return df[keep].copy(), {"kept": keep}
    elif drop:
        return df.drop(columns=drop), {"dropped": drop}
    return df.copy(), {}
```

### Column Renaming

```python
def rename_columns(df, rename_map=None, convention="snake_case"):
    """Rename columns using a map or convention.

    Args:
        rename_map: Dict of {old_name: new_name}. Takes precedence over convention.
        convention: 'snake_case' or None.

    Returns:
        (renamed_df, {"renamed": dict})
    """
    if rename_map:
        return df.rename(columns=rename_map), {"renamed": rename_map}

    if convention == "snake_case":
        import re
        new_names = {}
        for col in df.columns:
            new = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", col)
            new = re.sub(r"[^a-zA-Z0-9_]", "_", new)
            new = re.sub(r"_+", "_", new).strip("_").lower()
            if new != col:
                new_names[col] = new
        if new_names:
            return df.rename(columns=new_names), {"renamed": new_names}

    return df.copy(), {"renamed": {}}
```

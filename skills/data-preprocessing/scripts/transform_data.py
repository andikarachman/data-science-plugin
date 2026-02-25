"""
Data transformation functions for preprocessing pipelines.

Provides reusable transformations for deduplication, type coercion,
string normalization, outlier handling, and column operations.

Usage:
    python scripts/transform_data.py
"""

import re

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate_exact(df, subset=None, keep="first"):
    """Remove exact duplicate rows.

    Args:
        subset: Columns to check. None = all columns.
        keep: 'first', 'last', or False (drop all duplicates).

    Returns:
        (cleaned_df, info_dict)
    """
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}


def deduplicate_by_key(df, key_cols, sort_col=None, sort_ascending=False):
    """Keep one row per business key, preferring most recent.

    Args:
        key_cols: Columns that define a unique entity.
        sort_col: Column to sort by before dedup (e.g., 'updated_at').
        sort_ascending: Sort direction for the tiebreaker.

    Returns:
        (cleaned_df, info_dict)
    """
    n_before = len(df)
    if sort_col:
        df = df.sort_values(sort_col, ascending=sort_ascending)
    df_clean = df.drop_duplicates(subset=key_cols, keep="first")
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}


# ---------------------------------------------------------------------------
# Type coercion
# ---------------------------------------------------------------------------

def coerce_to_numeric(df, columns):
    """Convert string columns to numeric, setting unparseable values to NaN.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    new_nulls = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        original_nulls = int(df_clean[col].isnull().sum())
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        created = int(df_clean[col].isnull().sum()) - original_nulls
        if created > 0:
            new_nulls[col] = created
    return df_clean, {"coerced": columns, "new_nulls_from_coercion": new_nulls}


def parse_dates(df, columns, date_format=None, utc=False):
    """Parse string columns to datetime.

    Args:
        columns: Columns to parse.
        date_format: Expected format (e.g., '%Y-%m-%d'). None = auto-detect.
        utc: Convert to UTC.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    failed = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        original_nulls = int(df_clean[col].isnull().sum())
        df_clean[col] = pd.to_datetime(
            df_clean[col], format=date_format, errors="coerce", utc=utc
        )
        created = int(df_clean[col].isnull().sum()) - original_nulls
        if created > 0:
            failed[col] = created
    return df_clean, {"parsed": columns, "failed_parses": failed}


# ---------------------------------------------------------------------------
# String cleaning
# ---------------------------------------------------------------------------

def normalize_strings(df, columns=None, case="lower"):
    """Strip whitespace and normalize case.

    Args:
        columns: String columns. None = auto-detect object columns.
        case: 'lower', 'upper', 'title', or None.

    Returns:
        (cleaned_df, info_dict)
    """
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
    df_clean = df.copy()
    for col in columns:
        if col not in df_clean.columns:
            continue
        df_clean[col] = df_clean[col].str.strip()
        if case == "lower":
            df_clean[col] = df_clean[col].str.lower()
        elif case == "upper":
            df_clean[col] = df_clean[col].str.upper()
        elif case == "title":
            df_clean[col] = df_clean[col].str.title()
    return df_clean, {"normalized": columns}


def replace_placeholders(df, placeholders=None):
    """Replace common placeholder values with NaN.

    Returns:
        (cleaned_df, info_dict)
    """
    if placeholders is None:
        placeholders = [
            "", "N/A", "n/a", "NA", "na", "null", "NULL",
            "None", "none", "-", "--", ".", "?",
            "unknown", "UNKNOWN", "missing", "MISSING",
        ]
    df_clean = df.replace(placeholders, np.nan)
    replacements = {}
    for col in df.columns:
        diff = int(df[col].isin(placeholders).sum())
        if diff > 0:
            replacements[col] = diff
    return df_clean, {"replacements": replacements}


# ---------------------------------------------------------------------------
# Outlier handling
# ---------------------------------------------------------------------------

def remove_outliers_iqr(df, columns, factor=1.5):
    """Remove rows with outliers using IQR method.

    For outlier-robust scaling (not removal), use RobustScaler
    from the scikit-learn skill.

    Returns:
        (cleaned_df, info_dict)
    """
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        col_mask = df[col].between(lower, upper)
        counts[col] = int((~col_mask).sum())
        mask &= col_mask
    return df[mask].copy(), {"rows_removed": int((~mask).sum()), "per_column": counts}


def clip_outliers(df, columns, lower_pct=0.01, upper_pct=0.99):
    """Clip values to percentile bounds instead of removing rows.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        lower = float(df[col].quantile(lower_pct))
        upper = float(df[col].quantile(upper_pct))
        df_clean[col] = df_clean[col].clip(lower, upper)
        bounds[col] = {"lower": lower, "upper": upper}
    return df_clean, {"clipped": columns, "bounds": bounds}


# ---------------------------------------------------------------------------
# Column operations
# ---------------------------------------------------------------------------

def select_columns(df, keep=None, drop=None):
    """Select or drop columns.

    Returns:
        (filtered_df, info_dict)
    """
    if keep:
        return df[keep].copy(), {"kept": keep}
    elif drop:
        return df.drop(columns=drop), {"dropped": drop}
    return df.copy(), {}


def rename_columns(df, rename_map=None, convention="snake_case"):
    """Rename columns using a map or naming convention.

    Returns:
        (renamed_df, info_dict)
    """
    if rename_map:
        return df.rename(columns=rename_map), {"renamed": rename_map}

    if convention == "snake_case":
        new_names = {}
        for col in df.columns:
            new = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", str(col))
            new = re.sub(r"[^a-zA-Z0-9_]", "_", new)
            new = re.sub(r"_+", "_", new).strip("_").lower()
            if new != col:
                new_names[col] = new
        if new_names:
            return df.rename(columns=new_names), {"renamed": new_names}

    return df.copy(), {"renamed": {}}


# ---------------------------------------------------------------------------
# Structural missing data
# ---------------------------------------------------------------------------

def drop_high_missing_cols(df, threshold=0.9):
    """Drop columns with missing rate above threshold.

    Returns:
        (cleaned_df, info_dict)
    """
    rates = df.isnull().mean()
    to_drop = rates[rates > threshold].index.tolist()
    return df.drop(columns=to_drop), {
        "dropped": to_drop,
        "rates": {c: round(float(rates[c]), 4) for c in to_drop},
    }


def drop_high_missing_rows(df, threshold=0.5):
    """Drop rows with missing rate above threshold.

    Returns:
        (cleaned_df, info_dict)
    """
    row_missing = df.isnull().mean(axis=1)
    mask = row_missing <= threshold
    return df[mask].copy(), {"rows_dropped": int((~mask).sum())}


def drop_constant_columns(df):
    """Drop columns with a single unique value.

    Returns:
        (cleaned_df, info_dict)
    """
    nunique = df.nunique()
    constant = nunique[nunique <= 1].index.tolist()
    return df.drop(columns=constant), {"dropped": constant}


# ---------------------------------------------------------------------------
# Pre-model imputation
# ---------------------------------------------------------------------------

def impute_median(df, columns):
    """Impute missing values with median for numeric columns.

    This is pre-model imputation applied before EDA or profiling.
    For in-model imputation inside sklearn Pipelines, use the scikit-learn skill.

    Args:
        columns: Numeric columns to impute.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    imputer = SimpleImputer(strategy="median")
    filled = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        n_missing = int(df_clean[col].isnull().sum())
        if n_missing > 0 and pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
            filled[col] = n_missing
    return df_clean, {"strategy": "median", "filled": filled}


def impute_mode(df, columns):
    """Impute missing values with mode for categorical columns.

    Args:
        columns: Categorical columns to impute.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    filled = {}
    for col in columns:
        if col not in df_clean.columns or df_clean[col].dropna().empty:
            continue
        n_missing = int(df_clean[col].isnull().sum())
        if n_missing > 0:
            mode_val = df_clean[col].mode()
            if len(mode_val) > 0:
                df_clean[col] = df_clean[col].fillna(mode_val[0])
                filled[col] = n_missing
    return df_clean, {"strategy": "mode", "filled": filled}


def impute_knn(df, target_features, n_neighbors=5):
    """KNN-based imputation using correlated features.

    Uses LabelEncoder for categorical features before KNN imputation
    and decodes back after.

    Args:
        target_features: Dict mapping target columns to configuration.
            Format: {
                'target_col': {
                    'features': ['col1', 'col2'],
                    'type': 'numeric' | 'categorical' | 'binary'
                }
            }
        n_neighbors: Number of neighbors for KNN.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    filled = {}

    for target_col, config in target_features.items():
        if target_col not in df_clean.columns:
            continue

        feature_cols = [c for c in config.get("features", []) if c in df_clean.columns]
        col_type = config.get("type", "numeric")

        if not feature_cols or not df_clean[target_col].isna().any():
            continue

        n_missing = int(df_clean[target_col].isnull().sum())
        work_cols = feature_cols + [target_col]
        df_work = df_clean[work_cols].copy()

        # Encode feature columns
        feature_encoders = {}
        for col in feature_cols:
            numeric_vals = pd.to_numeric(df_work[col], errors="coerce")
            if numeric_vals.isna().sum() > df_work[col].isna().sum():
                le = LabelEncoder()
                non_null = df_work[col].notna()
                if non_null.sum() > 0:
                    df_work.loc[non_null, col] = le.fit_transform(
                        df_work.loc[non_null, col].astype(str)
                    )
                    feature_encoders[col] = le
            else:
                df_work[col] = numeric_vals

        # Encode target column
        target_encoder = None
        if col_type == "numeric":
            df_work[target_col] = pd.to_numeric(df_work[target_col], errors="coerce")
        elif col_type in ("categorical", "binary"):
            le = LabelEncoder()
            non_null = df_work[target_col].notna()
            if non_null.sum() > 0:
                df_work.loc[non_null, target_col] = le.fit_transform(
                    df_work.loc[non_null, target_col].astype(str)
                )
                target_encoder = le

        # Apply KNN imputation
        knn = KNNImputer(n_neighbors=n_neighbors)
        df_imputed = pd.DataFrame(
            knn.fit_transform(df_work),
            columns=df_work.columns,
            index=df_work.index,
        )

        # Decode target column if needed
        if target_encoder is not None:
            df_imputed[target_col] = df_imputed[target_col].round().astype(int)
            df_imputed[target_col] = df_imputed[target_col].clip(
                lower=0, upper=len(target_encoder.classes_) - 1
            )
            df_imputed[target_col] = target_encoder.inverse_transform(
                df_imputed[target_col]
            )

        df_clean[target_col] = df_imputed[target_col]
        filled[target_col] = n_missing

    return df_clean, {"strategy": "knn", "n_neighbors": n_neighbors, "filled": filled}


# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

def process_text(df, columns, operation="extract_numbers"):
    """Apply text processing operations to specified columns.

    Args:
        columns: Columns to process.
        operation: One of 'extract_numbers', 'clean_whitespace',
            'extract_email', 'lowercase', 'remove_special'.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    processed = []

    for col in columns:
        if col not in df_clean.columns:
            continue
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
        else:
            raise ValueError(f"Unknown text operation: {operation}")
        processed.append(col)

    return df_clean, {"operation": operation, "processed_columns": processed}


# ---------------------------------------------------------------------------
# Outlier handling (additional methods)
# ---------------------------------------------------------------------------

def cap_outliers_iqr(df, columns, factor=1.5):
    """Cap outliers at IQR bounds (winsorization) instead of removing rows.

    Preserves all rows by clipping extreme values to the IQR fence.

    Args:
        columns: Numeric columns to cap.
        factor: IQR multiplier (1.5 = standard, 3.0 = extreme only).

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            q1 = float(df_clean[col].quantile(0.25))
            q3 = float(df_clean[col].quantile(0.75))
            iqr = q3 - q1
            lower = q1 - factor * iqr
            upper = q3 + factor * iqr
            n_capped = int(
                ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
            )
            df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)
            bounds[col] = {"lower": lower, "upper": upper, "capped": n_capped}
    return df_clean, {"method": "iqr_cap", "factor": factor, "bounds": bounds}


def remove_outliers_zscore(df, columns, threshold=3.0):
    """Remove rows with outliers using Z-score method.

    Best suited for approximately normal distributions.

    Args:
        columns: Numeric columns to check.
        threshold: Z-score threshold (3.0 = ~99.7% of data).

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    mask = pd.Series(True, index=df_clean.index)
    counts = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            mean = df_clean[col].mean()
            std = df_clean[col].std()
            if std > 0:
                z_scores = np.abs((df_clean[col] - mean) / std)
                col_outliers = z_scores >= threshold
                counts[col] = int(col_outliers.sum())
                mask &= ~col_outliers
    n_removed = int((~mask).sum())
    return df_clean[mask].copy(), {
        "method": "zscore",
        "threshold": threshold,
        "rows_removed": n_removed,
        "outlier_counts": counts,
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "CustomerID": range(n),
        "  Full Name  ": [f"  User {i}  " for i in range(n)],
        "Age": list(range(20, 80)) + [999, -5] + list(range(20, 58)),
        "Income": np.random.lognormal(10, 1, n),
        "Status": ["active", "INACTIVE", "N/A", "active"] * 25,
        "SignupDate": ["2024-01-15"] * 50 + ["invalid_date"] * 50,
        "Empty": [np.nan] * n,
        "Notes": [f"Contact user{i}@test.com about order" for i in range(n)],
    })
    # Add some missing values for imputation demo
    df.loc[5:10, "Income"] = np.nan
    df.loc[15:20, "Status"] = np.nan

    print("Original shape:", df.shape)
    print("Columns:", list(df.columns))

    # Rename to snake_case
    df, info = rename_columns(df, convention="snake_case")
    print(f"\nRenamed: {info['renamed']}")

    # Replace placeholders
    df, info = replace_placeholders(df)
    print(f"Placeholders replaced: {info['replacements']}")

    # Normalize strings
    df, info = normalize_strings(df, case="lower")
    print(f"Normalized: {info['normalized']}")

    # Drop constant columns
    df, info = drop_constant_columns(df)
    print(f"Constant columns dropped: {info['dropped']}")

    # Impute missing numeric values with median
    df, info = impute_median(df, columns=["income"])
    print(f"Median imputed: {info['filled']}")

    # Impute missing categorical values with mode
    df, info = impute_mode(df, columns=["status"])
    print(f"Mode imputed: {info['filled']}")

    # Extract emails from text
    df, info = process_text(df, columns=["notes"], operation="extract_email")
    print(f"Text processed: {info['processed_columns']}")

    # Cap outliers instead of removing rows
    df, info = cap_outliers_iqr(df, columns=["age"], factor=1.5)
    print(f"Outliers capped: {info['bounds']}")

    # Remove outliers using Z-score
    df, info = remove_outliers_zscore(df, columns=["income"], threshold=3.0)
    print(f"Z-score outlier rows removed: {info['rows_removed']}")

    print(f"\nFinal shape: {df.shape}")

"""
End-to-end preprocessing pipeline orchestrator.

Executes a sequence of preprocessing steps with per-step tracking,
data hashing for reproducibility, and structured reporting.

Usage:
    python scripts/pipeline.py

This script demonstrates a complete preprocessing workflow:
1. Load raw data
2. Execute pipeline steps with tracking
3. Validate output
4. Generate summary report
"""

import hashlib
import os
import re
import time

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def compute_hash(df):
    """Compute SHA-256 hash of a DataFrame for reproducibility tracking."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()


# ---------------------------------------------------------------------------
# Pipeline step functions
# ---------------------------------------------------------------------------
# Each step function takes (df, **kwargs) and returns (df, info_dict).

def step_deduplicate(df, subset=None, keep="first"):
    """Remove duplicate rows."""
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    n_removed = n_before - len(df_clean)
    return df_clean, {"duplicates_removed": n_removed}


def step_drop_high_missing_cols(df, threshold=0.9):
    """Drop columns where missing rate exceeds threshold."""
    missing_rates = df.isnull().mean()
    cols_to_drop = missing_rates[missing_rates > threshold].index.tolist()
    rates = {col: round(float(missing_rates[col]), 4) for col in cols_to_drop}
    return df.drop(columns=cols_to_drop), {
        "columns_dropped": cols_to_drop,
        "missing_rates": rates,
    }


def step_drop_high_missing_rows(df, threshold=0.5):
    """Drop rows where missing rate exceeds threshold."""
    row_missing = df.isnull().mean(axis=1)
    mask = row_missing <= threshold
    n_dropped = (~mask).sum()
    return df[mask].copy(), {"rows_dropped": int(n_dropped)}


def step_drop_constant_columns(df):
    """Drop columns with a single unique value."""
    nunique = df.nunique()
    constant = nunique[nunique <= 1].index.tolist()
    return df.drop(columns=constant), {"columns_dropped": constant}


def step_coerce_types(df, type_map=None):
    """Coerce column types safely.

    type_map: dict of {column: target_type}.
    target_type: 'numeric', 'datetime', 'category', 'string'.
    """
    if type_map is None:
        type_map = {}
    df_clean = df.copy()
    failed = {}
    for col, target in type_map.items():
        if col not in df_clean.columns:
            failed[col] = "column not found"
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
            failed[col] = str(e)
    return df_clean, {"coerced": list(type_map.keys()), "failed": failed}


def step_normalize_strings(df, columns=None, case="lower"):
    """Strip whitespace and normalize case for string columns."""
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
    df_clean = df.copy()
    for col in columns:
        df_clean[col] = df_clean[col].str.strip()
        if case == "lower":
            df_clean[col] = df_clean[col].str.lower()
        elif case == "upper":
            df_clean[col] = df_clean[col].str.upper()
    return df_clean, {"normalized_columns": columns}


def step_replace_placeholders(df, placeholders=None):
    """Replace common placeholder values with NaN."""
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


def step_remove_outliers_iqr(df, columns=None, factor=1.5):
    """Remove rows with outliers using IQR method."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        col_outliers = ~df[col].between(lower, upper)
        counts[col] = int(col_outliers.sum())
        mask &= ~col_outliers
    n_removed = int((~mask).sum())
    return df[mask].copy(), {"rows_removed": n_removed, "outlier_counts": counts}


def step_cap_outliers_iqr(df, columns=None, factor=1.5):
    """Cap outliers at IQR bounds (winsorization) instead of removing rows."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        q1 = float(df_clean[col].quantile(0.25))
        q3 = float(df_clean[col].quantile(0.75))
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        n_capped = int(((df_clean[col] < lower) | (df_clean[col] > upper)).sum())
        df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)
        bounds[col] = {"lower": lower, "upper": upper, "capped": n_capped}
    return df_clean, {"method": "iqr_cap", "factor": factor, "bounds": bounds}


def step_remove_outliers_zscore(df, columns=None, threshold=3.0):
    """Remove rows with outliers using Z-score method."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        mean = df[col].mean()
        std = df[col].std()
        if std > 0:
            z_scores = np.abs((df[col] - mean) / std)
            col_outliers = z_scores >= threshold
            counts[col] = int(col_outliers.sum())
            mask &= ~col_outliers
    n_removed = int((~mask).sum())
    return df[mask].copy(), {
        "method": "zscore",
        "threshold": threshold,
        "rows_removed": n_removed,
        "outlier_counts": counts,
    }


def step_impute_median(df, columns=None):
    """Impute missing numeric values with median."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    df_clean = df.copy()
    imputer = SimpleImputer(strategy="median")
    filled = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        n_missing = int(df_clean[col].isnull().sum())
        if n_missing > 0 and pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
            filled[col] = n_missing
    return df_clean, {"strategy": "median", "filled": filled}


def step_impute_mode(df, columns=None):
    """Impute missing categorical values with mode."""
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
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


def step_impute_knn(df, target_features=None, n_neighbors=5):
    """KNN-based imputation using correlated features.

    target_features: dict of {column: {'features': [...], 'type': 'numeric'|'categorical'|'binary'}}.
    """
    if target_features is None:
        return df.copy(), {"strategy": "knn", "filled": {}}
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

        for col in feature_cols:
            numeric_vals = pd.to_numeric(df_work[col], errors="coerce")
            if numeric_vals.isna().sum() > df_work[col].isna().sum():
                le = LabelEncoder()
                non_null = df_work[col].notna()
                if non_null.sum() > 0:
                    df_work.loc[non_null, col] = le.fit_transform(
                        df_work.loc[non_null, col].astype(str)
                    )
            else:
                df_work[col] = numeric_vals

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

        knn = KNNImputer(n_neighbors=n_neighbors)
        df_imputed = pd.DataFrame(
            knn.fit_transform(df_work), columns=df_work.columns, index=df_work.index
        )

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


def step_process_text(df, columns=None, operation="clean_whitespace"):
    """Apply text processing to specified columns.

    operation: 'extract_numbers', 'clean_whitespace', 'extract_email',
               'lowercase', 'remove_special'.
    """
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
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
        processed.append(col)
    return df_clean, {"operation": operation, "processed_columns": processed}


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(df, steps):
    """Execute a preprocessing pipeline with per-step tracking.

    Args:
        df: Input DataFrame.
        steps: List of (step_name, function, kwargs) tuples.

    Returns:
        (processed_df, execution_log)
    """
    log = []
    current = df.copy()

    for step_name, func, kwargs in steps:
        n_before = len(current)
        cols_before = len(current.columns)
        t_start = time.time()

        try:
            current, info = func(current, **kwargs)
            elapsed = time.time() - t_start
            log.append({
                "step": step_name,
                "status": "success",
                "rows_in": n_before,
                "rows_out": len(current),
                "cols_in": cols_before,
                "cols_out": len(current.columns),
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
                "cols_in": cols_before,
                "cols_out": cols_before,
                "elapsed_seconds": round(elapsed, 3),
                "error": str(e),
                "error_type": type(e).__name__,
            })
            break  # Stop on failure

    return current, log


def generate_summary(df_input, df_output, log, input_hash, output_hash):
    """Generate a markdown summary of the pipeline execution.

    Returns:
        Markdown string.
    """
    lines = [
        "## Pipeline Execution Summary\n",
        f"**Input:** {len(df_input)} rows x {len(df_input.columns)} columns (hash: `{input_hash[:12]}...`)",
        f"**Output:** {len(df_output)} rows x {len(df_output.columns)} columns (hash: `{output_hash[:12]}...`)",
        f"**Rows removed:** {len(df_input) - len(df_output)}",
        f"**Columns removed:** {len(df_input.columns) - len(df_output.columns)}",
        "",
        "### Step Log\n",
        "| Step | Status | Rows In | Rows Out | Cols In | Cols Out | Time (s) |",
        "|------|--------|---------|----------|---------|----------|----------|",
    ]

    total_time = 0
    for entry in log:
        status = entry["status"]
        rows_out = entry.get("rows_out", "N/A")
        cols_out = entry.get("cols_out", "N/A")
        elapsed = entry.get("elapsed_seconds", 0)
        total_time += elapsed
        lines.append(
            f"| {entry['step']} | {status} | {entry['rows_in']} | "
            f"{rows_out} | {entry['cols_in']} | {cols_out} | {elapsed} |"
        )

    lines.append(f"\n**Total execution time:** {round(total_time, 3)}s")

    # Check for failures
    failures = [e for e in log if e["status"] == "failed"]
    if failures:
        lines.append("\n### Failures\n")
        for f in failures:
            lines.append(f"- **{f['step']}**: {f.get('error_type', 'Error')}: {f.get('error', 'Unknown')}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample data for demonstration
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "id": range(n),
        "name": [f"  User {i % 100}  " for i in range(n)],
        "age": np.random.normal(35, 15, n),
        "income": np.random.lognormal(10, 1, n),
        "status": np.random.choice(["active", "ACTIVE", "inactive", "N/A"], n),
        "signup_date": pd.date_range("2020-01-01", periods=n, freq="h").astype(str),
        "empty_col": np.nan,
    })
    # Add some duplicates and missing values
    df = pd.concat([df, df.head(50)], ignore_index=True)
    df.loc[5:15, "income"] = np.nan
    df.loc[20:30, "status"] = np.nan

    print(f"Input shape: {df.shape}")
    input_hash = compute_hash(df)

    # Define pipeline (11-step sequence)
    steps = [
        ("deduplicate", step_deduplicate, {"subset": ["id"], "keep": "first"}),
        ("replace_placeholders", step_replace_placeholders, {}),
        ("drop_constant_cols", step_drop_constant_columns, {}),
        ("drop_high_missing_cols", step_drop_high_missing_cols, {"threshold": 0.9}),
        ("impute_median", step_impute_median, {"columns": ["income"]}),
        ("impute_mode", step_impute_mode, {"columns": ["status"]}),
        ("normalize_strings", step_normalize_strings, {"columns": ["name", "status"]}),
        ("coerce_types", step_coerce_types, {"type_map": {"signup_date": "datetime"}}),
        ("cap_outliers", step_cap_outliers_iqr, {"columns": ["age"], "factor": 1.5}),
        ("remove_outliers_zscore", step_remove_outliers_zscore, {"columns": ["income"], "threshold": 3.0}),
    ]

    # Execute
    df_clean, log = run_pipeline(df, steps)
    output_hash = compute_hash(df_clean)

    # Report
    summary = generate_summary(df, df_clean, log, input_hash, output_hash)
    print(summary)

    print(f"\nOutput shape: {df_clean.shape}")
    print(f"Input hash:  {input_hash[:16]}...")
    print(f"Output hash: {output_hash[:16]}...")

# Error Handling Strategies

Failure modes, recovery patterns, and validation modes for preprocessing pipelines.

## Pipeline Failure Modes

### Step Failure

When a pipeline step raises an exception:

1. **Stop execution immediately** -- do not proceed to subsequent steps
2. **Preserve partial output** -- the DataFrame state before the failed step is valid
3. **Report the failure** with: step name, error message, rows processed so far, suggested fix

```python
def handle_step_failure(step_name, error, df_before, log):
    """Handle a pipeline step failure.

    Args:
        step_name: Name of the failed step.
        error: The exception that was raised.
        df_before: DataFrame state before the failed step.
        log: Execution log up to this point.

    Returns:
        Error report dict.
    """
    return {
        "failed_step": step_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "rows_at_failure": len(df_before),
        "steps_completed": len([s for s in log if s["status"] == "success"]),
        "steps_remaining": "unknown",
        "partial_output_available": True,
        "suggested_fix": suggest_fix(step_name, error),
    }

def suggest_fix(step_name, error):
    """Suggest a fix based on the error type and step."""
    error_type = type(error).__name__
    error_msg = str(error).lower()

    if "keyerror" in error_type.lower() or "not in index" in error_msg:
        return "Column not found. Check column names in the step configuration."
    elif "memory" in error_msg:
        return "Out of memory. Try processing in chunks or reducing dataset size."
    elif "dtype" in error_msg or "convert" in error_msg:
        return "Type conversion failed. Check the data for unexpected values in the target column."
    elif "permission" in error_msg:
        return "File permission error. Check read/write access to the data files."
    else:
        return f"Review the error message and adjust the '{step_name}' step parameters."
```

### Common Errors by Step

| Step | Common Error | Cause | Fix |
|------|-------------|-------|-----|
| Deduplicate | `KeyError` | Subset column does not exist | Verify column names |
| Type coercion | `ValueError` | Unparseable values | Use `errors='coerce'` to set invalid values to NaN |
| Date parsing | Mixed formats | Multiple date formats in same column | Specify format or use `infer_datetime_format=True` |
| Schema validation | `AssertionError` | Data violates expected schema | Review validation errors and adjust data or schema |
| Outlier removal (IQR) | Empty DataFrame | Too aggressive threshold | Increase IQR factor (1.5 -> 3.0) |
| Outlier removal (Z-score) | Empty DataFrame | Too aggressive threshold | Increase Z-score threshold (3.0 -> 4.0) or use IQR for non-normal data |
| Outlier capping (IQR) | All values identical | Column has zero IQR (constant values) | Skip capping for constant columns |
| Imputation (median) | All-null column | Column is entirely missing | Drop column instead of imputing |
| Imputation (mode) | Empty column | No non-null values to compute mode | Drop column or impute with a default value |
| Imputation (KNN) | `ValueError` | Insufficient non-null neighbors | Reduce `n_neighbors` or use median/mode fallback |
| Text processing | Regex failure | Unexpected text format | Verify column contains expected text patterns before extraction |
| File write | `PermissionError` | No write access | Check directory permissions |

## Validation Modes

### Strict Mode (Default)

All validation errors halt the pipeline. Use when data quality is critical.

```python
def validate_strict(df, schema):
    """Validate and raise on any error.

    Raises:
        ValueError with all validation errors if any found.
    """
    issues = validate_schema(df, schema)
    errors = [i for i in issues if i["severity"] == "error"]
    if errors:
        error_msgs = [f"  - {e['column']}: {e['message']}" for e in errors]
        raise ValueError(
            f"Schema validation failed with {len(errors)} errors:\n"
            + "\n".join(error_msgs)
        )
```

### Permissive Mode

Validation errors are logged as warnings. Pipeline continues. Use for exploratory preprocessing.

```python
import warnings

def validate_permissive(df, schema):
    """Validate and warn on errors without stopping.

    Returns:
        List of issues (same as validate_schema).
    """
    issues = validate_schema(df, schema)
    errors = [i for i in issues if i["severity"] == "error"]
    if errors:
        for e in errors:
            warnings.warn(
                f"Validation warning - {e['column']}: {e['message']}",
                UserWarning,
            )
    return issues
```

### Choosing a Mode

| Scenario | Mode | Rationale |
|----------|------|-----------|
| Production ETL pipeline | Strict | Bad data should not propagate |
| Exploratory preprocessing | Permissive | See all issues before fixing |
| Re-running after fixes | Strict | Confirm fixes resolved all issues |
| First-time data assessment | Permissive | Understand the full scope of problems |

## Partial Output Preservation

When a pipeline fails mid-execution, preserve work completed so far:

```python
def save_partial_output(df, output_dir, step_name, log):
    """Save partial pipeline output after a failure.

    Args:
        df: DataFrame state at the point of failure.
        output_dir: Directory for output files.
        step_name: Name of the failed step.
        log: Execution log.

    Returns:
        Paths to saved files.
    """
    import os
    import json

    os.makedirs(output_dir, exist_ok=True)

    # Save data
    data_path = os.path.join(output_dir, f"partial_before_{step_name}.parquet")
    df.to_parquet(data_path, index=False)

    # Save log
    log_path = os.path.join(output_dir, "pipeline_log.json")
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, default=str)

    return {"data": data_path, "log": log_path}
```

## Error Reporting Format

Structure error reports for inclusion in preprocessing reports:

```python
def format_error_report(failure_info, log):
    """Format a pipeline failure as markdown.

    Returns:
        Markdown string.
    """
    lines = [
        "## Pipeline Failure Report\n",
        f"**Failed at step:** {failure_info['failed_step']}",
        f"**Error:** {failure_info['error_type']}: {failure_info['error_message']}",
        f"**Rows at failure:** {failure_info['rows_at_failure']}",
        f"**Steps completed:** {failure_info['steps_completed']}",
        f"**Suggested fix:** {failure_info['suggested_fix']}",
        "",
        "### Execution Log\n",
        "| Step | Status | Rows In | Rows Out | Time (s) |",
        "|------|--------|---------|----------|----------|",
    ]

    for entry in log:
        status = entry["status"]
        rows_out = entry.get("rows_out", "N/A")
        elapsed = entry.get("elapsed_seconds", "N/A")
        lines.append(
            f"| {entry['step']} | {status} | {entry['rows_in']} | {rows_out} | {elapsed} |"
        )

    return "\n".join(lines)
```

## Logging Best Practices

1. **Log step boundaries** -- record when each step starts and ends
2. **Track row counts** -- rows in vs rows out per step reveals unexpected data loss
3. **Capture execution time** -- identifies bottleneck steps
4. **Record parameters** -- log the exact parameters used for each step for reproducibility
5. **Avoid logging raw data** -- do not print full rows in logs (PII risk). Log counts, types, and aggregate statistics only

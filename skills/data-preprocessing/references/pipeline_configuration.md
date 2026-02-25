# Pipeline Configuration

Patterns for building, configuring, and executing preprocessing pipelines.

## Step Sequencing

Preprocessing pipelines follow a standard order. Each step expects clean input from the previous step.

**Recommended sequence:**

```
1. Validate input schema
2. Deduplicate
3. Handle structural missing data (drop high-missing columns/rows, drop constant columns)
4. Impute missing values (median for numeric, mode for categorical, KNN for correlated)
5. Coerce types (string-to-numeric, date parsing)
6. Normalize strings (whitespace, case)
7. Process text (extract numbers/emails, remove special characters)
8. Replace placeholders (convert sentinel values to NaN)
9. Handle outliers (IQR remove, IQR cap, Z-score remove, or percentile clip)
10. Transform (resampling, format conversion)
11. Validate output schema
```

Not every step is needed for every dataset. The `pipeline-builder` agent assesses the data and recommends which steps to include. Imputation (step 4) comes after structural drops (step 3) -- no point imputing a column you will drop. Text processing (step 7) comes after string normalization (step 6) but before placeholder replacement (step 8).

## Configuration via Python Dicts

Pipelines are configured with plain Python dicts. This keeps configuration close to the code and avoids external config file management.

```python
pipeline_config = {
    "steps": [
        {
            "name": "deduplicate",
            "function": "deduplicate",
            "params": {"subset": None, "keep": "first"},
        },
        {
            "name": "drop_high_missing",
            "function": "drop_high_missing",
            "params": {"row_threshold": 0.9, "col_threshold": 0.9},
        },
        {
            "name": "coerce_types",
            "function": "coerce_types",
            "params": {
                "type_map": {
                    "age": "numeric",
                    "signup_date": "datetime",
                    "status": "category",
                }
            },
        },
        {
            "name": "normalize_strings",
            "function": "normalize_strings",
            "params": {"columns": ["name", "email", "city"]},
        },
        {
            "name": "validate_output",
            "function": "validate_schema",
            "params": {"schema": output_schema},
        },
    ],
    "options": {
        "stop_on_failure": True,
        "preserve_partial_output": True,
        "compute_hashes": True,
    },
}
```

## Column-Type Routing

Different column types need different preprocessing. Route columns by detected type:

```python
def route_columns(df):
    """Classify columns by type for targeted preprocessing.

    Returns:
        Dict with keys: numeric, categorical, temporal, text, id_like.
    """
    routes = {
        "numeric": [],
        "categorical": [],
        "temporal": [],
        "text": [],
        "id_like": [],
    }

    for col in df.columns:
        dtype = df[col].dtype

        # ID-like: high cardinality with sequential or unique values
        if df[col].nunique() == len(df):
            routes["id_like"].append(col)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            routes["temporal"].append(col)
        elif pd.api.types.is_numeric_dtype(dtype):
            routes["numeric"].append(col)
        elif pd.api.types.is_categorical_dtype(dtype) or df[col].nunique() < 50:
            routes["categorical"].append(col)
        else:
            routes["text"].append(col)

    return routes
```

**Type-specific step recommendations:**

| Column Type | Applicable Steps |
|-------------|-----------------|
| Numeric | Median imputation, outlier handling (IQR remove/cap, Z-score, clip), range validation, coercion from string |
| Categorical | Mode imputation, string normalization, rare category handling, cardinality check |
| Temporal | Date parsing, timezone normalization, temporal sorting, resampling |
| Text | Text processing (extract numbers/email, remove special), whitespace stripping, case normalization |
| ID-like | Skip transformations, preserve as-is or drop if not needed |
| Mixed (correlated) | KNN imputation using correlated feature columns |

## Checkpointing

For long-running pipelines or large datasets, save intermediate results between steps:

```python
import os

def run_pipeline_with_checkpoints(df, steps, checkpoint_dir=None):
    """Execute pipeline with optional checkpoints between steps.

    Args:
        df: Input DataFrame.
        steps: List of (step_name, function, kwargs) tuples.
        checkpoint_dir: Directory for intermediate saves. None = no checkpoints.

    Returns:
        Processed DataFrame, execution log.
    """
    log = []
    current = df.copy()

    if checkpoint_dir:
        os.makedirs(checkpoint_dir, exist_ok=True)

    for i, (step_name, func, kwargs) in enumerate(steps):
        n_before = len(current)

        try:
            current, info = func(current, **kwargs)
            log.append({
                "step": step_name,
                "status": "success",
                "rows_in": n_before,
                "rows_out": len(current),
                "info": info,
            })

            # Checkpoint after each successful step
            if checkpoint_dir:
                path = os.path.join(checkpoint_dir, f"step_{i:02d}_{step_name}.parquet")
                current.to_parquet(path, index=False)

        except Exception as e:
            log.append({
                "step": step_name,
                "status": "failed",
                "rows_in": n_before,
                "error": str(e),
            })
            break

    return current, log
```

**When to checkpoint:**
- Dataset >100MB
- Pipeline has >5 steps
- Steps involve expensive operations (fuzzy deduplication, complex joins)
- Debugging a pipeline that fails mid-execution

## Resuming from Failure

When a pipeline fails mid-execution, resume from the last successful checkpoint:

```python
def resume_pipeline(checkpoint_dir, steps, resume_from_step):
    """Resume a pipeline from a checkpoint.

    Args:
        checkpoint_dir: Directory with checkpoint files.
        steps: Full list of pipeline steps.
        resume_from_step: Index of the step to resume from.

    Returns:
        Processed DataFrame, execution log.
    """
    # Load the checkpoint before the failed step
    checkpoint_idx = resume_from_step - 1
    step_name = steps[checkpoint_idx][0]
    checkpoint_path = os.path.join(
        checkpoint_dir, f"step_{checkpoint_idx:02d}_{step_name}.parquet"
    )
    df = pd.read_parquet(checkpoint_path)

    # Run remaining steps
    remaining_steps = steps[resume_from_step:]
    return run_pipeline(df, remaining_steps)
```

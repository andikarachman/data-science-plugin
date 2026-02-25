---
name: ds:validate
description: Run data quality validation using formal expectation suites, dbt tests, or data contracts
argument-hint: "[path to dataset, expectation suite, or data contract]"
disable-model-invocation: true
---

# Validate Data Quality

## Input

<data_source> $ARGUMENTS </data_source>

**If the data source above is empty, ask the user:** "What data do you want to validate? Provide a file path (CSV, Parquet, Excel, TSV), a Great Expectations suite name, or a data contract YAML."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: data` and quality-related learnings (keywords: validation, quality, expectations, contract, freshness, completeness).

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

If learnings are found, summarize them: "Found N prior learnings related to data quality validation..." and include key takeaways that should inform the expectation suite.

### 2. Load and Detect Data Source

Detect file format from extension and load the dataset. For efficient I/O, reference the `pandas-pro` skill's `references/performance-optimization.md`:
- **CSV** (`.csv`): `pd.read_csv()` -- specify `dtype` dict for known columns
- **Parquet** (`.parquet`): `pd.read_parquet()`
- **Excel** (`.xlsx`, `.xls`): `pd.read_excel()`
- **TSV** (`.tsv`): `pd.read_csv(sep='\t')`

**If the argument is a Great Expectations suite name or data contract YAML:** Load that artifact instead and ask the user for the data path to validate against.

Compute the data hash: `hashlib.sha256(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()`

Report: "Loaded [N rows] x [M columns] from [path]. Data hash: [hash[:12]]..."

**Large dataset handling:** If the file exceeds 100MB (`os.path.getsize()`), report: "Dataset is [size]MB. Validation will run on the full dataset (no sampling -- quality checks need complete data)."

### 3. Detect Validation Framework

Check which validation frameworks are available:

```python
# Check Great Expectations
try:
    import great_expectations as gx
    gx_version = gx.__version__
    gx_available = True
except ImportError:
    gx_available = False

# Check for dbt project
import os
dbt_available = os.path.exists("dbt_project.yml")

# Check for data contract YAML
contract_files = [f for f in os.listdir(".") if f.endswith("_contract.yaml") or f.endswith("_contract.yml")]
contract_available = len(contract_files) > 0
```

Report which frameworks are available:
- "Great Expectations [version] detected. Will use GX expectation suites."
- "Great Expectations not installed. Will use pandas-based validation (equivalent quality dimension coverage)."
- "dbt project detected. dbt test patterns are available for reference."
- "Data contract found: [filename]. Will validate against contract specification."

### 4. Build Expectation Suite

Based on the detected framework and data characteristics, build a validation suite covering all 6 quality dimensions.

**If Great Expectations is available:** Reference the `data-quality-frameworks` skill (Pattern 1: Great Expectations Suite) to build an expectation suite:

- **Completeness**: `expect_column_values_to_not_be_null` for key columns (detected by low null rates)
- **Uniqueness**: `expect_column_values_to_be_unique` for ID-like columns (detected by cardinality = row count)
- **Validity**: `expect_column_values_to_be_in_set` for low-cardinality categoricals, `expect_column_values_to_be_between` for numerics
- **Consistency**: `expect_column_pair_values_A_to_be_greater_than_B` for logical orderings (e.g., end_date > start_date)
- **Timeliness**: `expect_column_max_to_be_between` for date columns (check freshness)
- **Schema**: `expect_table_columns_to_match_set`, `expect_table_row_count_to_be_between`

**If Great Expectations is not available:** Build equivalent pandas-based validation using the `data-preprocessing` skill's `references/data_validation_schemas.md`:

- Build a schema dict with dtype, nullable, unique, min, max, allowed_values rules
- Use the `validate_schema()` function pattern from that reference
- Map each check to a quality dimension for the report

**If an existing suite or contract was provided as argument:** Load and use it directly.

Present the proposed expectation suite to the user:
- List each expectation with its target column and dimension
- Ask: "Proposed suite has N expectations across 6 quality dimensions. Should I proceed, or would you like to adjust?"

### 5. Run Validation

Execute the expectation suite against the loaded data.

**If Great Expectations:** Reference the `data-quality-frameworks` skill (Pattern 2: Great Expectations Checkpoint) for running the suite.

**If pandas-based:** Run each validation rule and collect results in the same structure:

```python
results = []
for rule in validation_rules:
    passed = run_check(df, rule)
    results.append({
        "expectation": rule["name"],
        "column": rule.get("column"),
        "dimension": rule["dimension"],
        "success": passed,
        "observed_value": compute_observed(df, rule),
    })
```

Track per-expectation results: expectation type, column, dimension, pass/fail, observed value, details.

### 6. Assess Quality Dimensions

Map validation results to the 6 quality dimensions from the `data-quality-frameworks` skill's Core Concepts table (Completeness, Uniqueness, Validity, Accuracy, Consistency, Timeliness).

For each dimension, compute:
- Total checks run
- Checks passed
- Checks failed
- Overall dimension status (PASS if all pass, FAIL if any critical failure, WARN if only minor failures)

Determine the overall validation decision:
- **PASS** -- All expectations pass, or only minor warnings
- **WARN** -- Some non-critical failures that should be investigated
- **FAIL** -- Critical expectations failed (nulls in primary keys, schema mismatch, freshness violation)

Report: "Validation complete. [passed]/[total] expectations passed. Decision: [PASS/WARN/FAIL]."

### 7. Write Artifact

Generate a validation report at `docs/ds/validations/YYYY-MM-DD-<dataset-name>-validation.md` using `templates/validation-report.md`.

Create the directory if needed: `mkdir -p docs/ds/validations/`

Fill all template sections:
- Data summary (from step 2)
- Framework used (from step 3)
- Quality dimensions table (from step 6)
- Per-expectation results (from step 5)
- Failed expectations detail (from step 5, failed only)
- Data contract status (if contract exists)
- Summary with decision
- Warnings and recommendations

### 8. Next Steps

Ask the user: "Validation complete. [passed]/[total] expectations passed ([decision]). What next?" with options:
- Start EDA (`/ds:eda`)
- Fix issues and re-validate
- Save expectation suite for reuse
- Set up data contract (`data-quality-frameworks` Pattern 5)
- Capture learnings (`/ds:compound`)

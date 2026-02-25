---
name: ds:preprocess
description: Clean, validate, and transform raw data using automated preprocessing pipelines
argument-hint: "[path to dataset or description of data source]"
disable-model-invocation: true
---

# Preprocess Data

## Input

<data_source> $ARGUMENTS </data_source>

**If the data source above is empty, ask the user:** "What data do you want to preprocess? Provide a file path (CSV, Parquet, Excel, TSV) or describe the data source."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for `category: data` and `lifecycle_stage: preprocessing` learnings related to this dataset or domain.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

If learnings are found, summarize them: "Found N prior learnings related to preprocessing [topic]..." and include key takeaways that should inform this pipeline.

### 2. Load and Detect Data Source

Detect file format from extension and load the dataset. For efficient I/O with dtype specification and chunked reading, reference the `pandas-pro` skill's `references/performance-optimization.md` (I/O Optimization, Specify dtypes When Reading sections):
- **CSV** (`.csv`): `pd.read_csv()` -- specify `dtype` dict for known columns, use `chunksize` for large files
- **Parquet** (`.parquet`): `pd.read_parquet()`
- **Excel** (`.xlsx`, `.xls`): `pd.read_excel()`
- **TSV** (`.tsv`): `pd.read_csv(sep='\t')`

**Large dataset handling:** If the file exceeds 100MB (`os.path.getsize()`), report: "Dataset is [size]MB. For initial assessment, I'll profile a sample. For full preprocessing, I'll process in chunks."

**Non-tabular formats:** If the file is a scientific format (HDF5, FASTA, NetCDF, etc.), report: "Preprocessing pipelines are designed for tabular data. For scientific formats, start with `/ds:eda` instead."

Compute and record the input data hash: `hashlib.sha256(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()`

Report: "Loaded [N rows] x [M columns] from [path]. Input hash: [hash[:12]]..."

### 3. Assess Data Quality

Invoke the `pipeline-builder` agent to assess raw data quality:

- **Structural overview**: shape, dtypes, memory usage
- **Duplicate detection**: exact duplicates, near-duplicates on key columns
- **Missing value analysis**: per-column missing rates, columns >90% missing
- **Type mismatches**: numeric-as-string, dates-as-string, mixed types
- **Placeholder detection**: values like "N/A", "null", "unknown" masking as data
- **String inconsistencies**: mixed case, whitespace issues
- **Column cardinality**: constant columns, ID-like columns, high-cardinality categoricals
- **Temporal detection**: datetime columns, sorting, frequency regularity, gaps

### 4. Design Preprocessing Pipeline

Based on the quality assessment, the `pipeline-builder` agent recommends a step sequence. Reference the `data-preprocessing` skill:
- `references/pipeline_configuration.md` for step ordering and configuration patterns
- `references/transformation_methods.md` for available transform functions

Present the recommended pipeline to the user as a numbered list with:
- Step name and purpose
- Key parameters
- Expected impact

Ask: "Recommended pipeline has N steps. Should I proceed, or would you like to adjust any steps?"

### 5. Execute Pipeline

Execute the approved pipeline using `data-preprocessing` skill patterns. Reference `scripts/pipeline.py` for the pipeline runner.

Track per-step metrics:
- Rows in / rows out
- Columns in / columns out
- Execution time
- Values modified or removed
- Warnings generated

Reference `references/error_handling_strategies.md` for failure handling. If a step fails:
1. Stop execution immediately
2. Preserve the DataFrame state from before the failed step
3. Report: step name, error type, error message, rows processed, suggested fix
4. Ask user how to proceed: fix and retry, skip the step, or abort

### 6. Validate Output

Run output validation using `data-preprocessing` skill's `references/data_validation_schemas.md`:

- Verify no structural issues remain (no constant columns, no all-null columns)
- Compute SHA-256 hash of the output DataFrame
- Compare key statistics before vs after:
  - Row count change
  - Column count change
  - Missing value count change
  - Data type summary
- Run schema validation if a schema was defined in step 4

Report: "Output: [N rows] x [M columns]. Hash: [hash[:12]]... [X rows removed, Y columns removed]."

### 7. Write Artifact

Generate two outputs:

**Preprocessed data file:**
- Write to a user-specified location, or default to `data/preprocessed/YYYY-MM-DD-<dataset-name>-clean.<format>`
- Preserve original format (CSV -> CSV, Parquet -> Parquet) unless user requests conversion
- Non-destructive: never overwrite the original data file

**Preprocessing report:**
- Write to `docs/ds/preprocessing/YYYY-MM-DD-<dataset-name>-preprocessing.md` using `templates/preprocessing-report.md`
- Include: input/output summary, pipeline steps with before/after metrics, validation results, data hashes, warnings, learnings applied

Create the directory if needed: `mkdir -p docs/ds/preprocessing/`

### 8. Next Steps

Ask the user: "Preprocessing complete. What next?" with options:
- Validate data quality (`/ds:validate`)
- Start EDA (`/ds:eda`)
- Re-run with different parameters
- Investigate specific findings
- Capture learnings (`/ds:compound`)

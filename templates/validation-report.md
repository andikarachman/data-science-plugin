---
title: "Validation Report: [Dataset Name]"
date: YYYY-MM-DD
dataset_name: "[Dataset Name]"
data_path: "[path/to/data]"
framework: "[great_expectations | pandas | dbt]"
data_hash: "[SHA-256 hash]"
total_expectations: 0
passed: 0
failed: 0
pass_rate: "0%"
---

# Validation Report: [Dataset Name]

## Learnings Applied

[List any past learnings from `docs/ds/learnings/` that informed this validation run. If none, state "No prior learnings applied."]

## Data Summary

| Property | Value |
|----------|-------|
| File | [data_path] |
| Format | [CSV / Parquet / Excel / TSV] |
| Rows | [N] |
| Columns | [N] |
| File size | [size in MB] |
| Data hash | [data_hash] |

## Validation Framework

[Framework used and detection rationale. If Great Expectations is installed, note the version. If falling back to pandas-based validation, note: "Great Expectations not installed. Using pandas-based validation with equivalent quality dimension coverage."]

## Quality Dimensions Assessed

| Dimension | Checks | Passed | Failed | Notes |
|-----------|--------|--------|--------|-------|
| Completeness | [N] | [N] | [N] | [missing value checks] |
| Uniqueness | [N] | [N] | [N] | [duplicate checks] |
| Validity | [N] | [N] | [N] | [range, enum, type checks] |
| Accuracy | [N] | [N] | [N] | [cross-reference checks] |
| Consistency | [N] | [N] | [N] | [cross-column checks] |
| Timeliness | [N] | [N] | [N] | [freshness checks] |

## Expectation Results

| # | Expectation | Column | Dimension | Status | Observed Value | Details |
|---|-------------|--------|-----------|--------|----------------|---------|
| 1 | [expectation_type] | [column] | [dimension] | [PASS/FAIL] | [value] | [details] |
| 2 | [expectation_type] | [column] | [dimension] | [PASS/FAIL] | [value] | [details] |
| ... | ... | ... | ... | ... | ... | ... |

## Failed Expectations Detail

[For each failed expectation, describe:]

### [Expectation name] -- [Column]

- **Expected:** [what was expected]
- **Observed:** [what was found]
- **Severity:** [Critical / Major / Minor]
- **Recommended action:** [what to do about it]

## Data Contract Status

[If a data contract YAML exists in the project, report compliance against it. Include:]

| Contract Field | Expected | Actual | Status |
|---------------|----------|--------|--------|
| [field] | [expected value] | [actual value] | [PASS/FAIL] |

[If no data contract defined: "No data contract defined for this dataset."]

## Summary

| Metric | Value |
|--------|-------|
| Total expectations | [N] |
| Passed | [N] |
| Failed | [N] |
| Pass rate | [N%] |
| Critical failures | [N] |
| Decision | [PASS / FAIL / WARN] |

**Decision criteria:**
- **PASS** -- All expectations pass, or only minor warnings
- **WARN** -- Some non-critical failures that should be investigated
- **FAIL** -- Critical expectations failed (nulls in primary keys, schema mismatch, freshness violation)

## Warnings and Recommendations

[List any warnings generated during validation, recommended follow-up actions, or suggestions for additional expectations to add.]

- [Warning or recommendation 1]
- [Warning or recommendation 2]

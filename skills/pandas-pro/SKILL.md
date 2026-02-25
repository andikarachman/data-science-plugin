---
name: pandas-pro
description: "Pandas API patterns for DataFrame operations, data cleaning, aggregation, merging, and performance optimization. Use when generating pandas code for data loading, manipulation, or profiling in /ds:eda, /ds:preprocess, or /ds:experiment."
license: MIT
metadata:
    skill-author: https://github.com/Jeffallan
---

# Pandas Pro

## Overview

Expert pandas API reference providing efficient data manipulation, analysis, and transformation patterns with production-grade performance. Covers DataFrame operations, data cleaning fundamentals, aggregation/groupby, merging/joining, and memory optimization for pandas 2.0+.

**Role in the ds plugin:** This skill is the canonical pandas API reference for the plugin. It is invoked by `/ds:eda` for efficient data loading (step 3), structural profiling patterns (step 4), and groupby-based distribution analysis (step 5); by `/ds:preprocess` for I/O optimization (step 2) and vectorized operation patterns (step 5); by `/ds:experiment` for feature assembly merge patterns (step 3) and data preparation code scaffolds (step 6); and by `/ds:plan` for large-dataset handling strategy (step 3). **Boundary with data-preprocessing:** pandas-pro teaches *how to call* pandas methods (API syntax, parameters, best practices). data-preprocessing teaches *when and how to sequence* cleaning operations in a tracked pipeline with error handling and logging. For pipeline-oriented data cleaning (deduplication, imputation, outlier removal, schema validation), use the `data-preprocessing` skill. **Boundary with scikit-learn:** For in-model preprocessing inside sklearn Pipelines (scaling, encoding, imputation that participates in cross-validation), use the `scikit-learn` skill. **pandas 2.0+ note:** Patterns in this skill target pandas 2.0+. On pandas 1.x, nullable types (`Int64`, `string`), `format='mixed'` in `pd.to_datetime()`, and Arrow-backed types (`string[pyarrow]`) may not be available.

## When to Use This Skill

- Loading, cleaning, and transforming tabular data with pandas API patterns
- Handling missing values and data quality issues at the API level
- Performing groupby aggregations, pivot tables, and crosstab operations
- Merging, joining, and concatenating datasets
- Optimizing pandas code for memory and performance
- Converting between data formats (CSV, Parquet, Excel, JSON)
- Profiling DataFrame structure, dtypes, and memory usage

## Core Workflow

1. **Assess data structure** -- Examine dtypes, memory usage, missing values, data quality
2. **Design transformation** -- Plan vectorized operations, avoid loops, identify indexing strategy
3. **Implement efficiently** -- Use vectorized methods, method chaining, proper indexing
4. **Validate results** -- Check dtypes, shapes, edge cases, null handling
5. **Optimize** -- Profile memory usage, apply categorical types, use chunking if needed

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| DataFrame Operations | `references/dataframe-operations.md` | Indexing, selection, filtering, sorting, column operations |
| Data Cleaning | `references/data-cleaning.md` | Missing values, type conversion, string cleaning, validation |
| Aggregation & GroupBy | `references/aggregation-groupby.md` | GroupBy, pivot tables, crosstab, window functions, transform/apply |
| Merging & Joining | `references/merging-joining.md` | Merge, join, concat, combine strategies, anti-joins |
| Performance Optimization | `references/performance-optimization.md` | Memory profiling, vectorization, chunking, I/O optimization |

## Constraints

### MUST DO
- Use vectorized operations instead of loops
- Set appropriate dtypes (categorical for low-cardinality strings)
- Check memory usage with `.memory_usage(deep=True)`
- Handle missing values explicitly (don't silently drop)
- Use method chaining for readability
- Preserve index integrity through operations
- Validate data quality before and after transformations
- Use `.copy()` when modifying subsets to avoid SettingWithCopyWarning

### MUST NOT DO
- Iterate over DataFrame rows with `.iterrows()` unless absolutely necessary
- Use chained indexing (`df['A']['B']`) -- use `.loc[]` or `.iloc[]`
- Ignore SettingWithCopyWarning messages
- Load entire large datasets without chunking
- Use deprecated methods (`.ix`, `.append()` -- use `pd.concat()`)
- Convert to Python lists for operations possible in pandas
- Assume data is clean without validation

## Output Patterns

When implementing pandas solutions, provide:
1. Code with vectorized operations and proper indexing
2. Comments explaining complex transformations
3. Memory/performance considerations if dataset is large
4. Data validation checks (dtypes, nulls, shapes)

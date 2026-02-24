---
name: eda-checklist
description: "Systematic exploratory data analysis checklist covering structure, quality, distributions, relationships, and target analysis. Use when starting EDA on any dataset."
---

# EDA Checklist

Systematic checklist for exploratory data analysis. Work through each section in order. Check off items as you complete them.

**Role in ds plugin:** This skill provides the systematic methodology for tabular EDA -- what to check and in what order. It is invoked by `/ds:eda` at step 6 (Data Quality Checks). The `exploratory-data-analysis` skill handles file type detection and format-specific analysis for non-tabular scientific formats. These skills are complementary: `eda-checklist` answers "what to check in tabular data" while `exploratory-data-analysis` answers "how to analyze any file format."

## Structure

- [ ] **Shape and types** -- Row count, column count, dtypes, memory usage
- [ ] **Index structure** -- Is the index meaningful (datetime, ID) or just a range?
- [ ] **Column naming** -- Consistent naming convention? Any ambiguous names?

## Missing Data

- [ ] **Missing rates per column** -- Compute `df.isnull().mean()` and sort descending
- [ ] **Missing patterns** -- Use a missing data heatmap to check if missingness is random (MCAR), conditional (MAR), or structural (MNAR)
- [ ] **Columns >50% missing** -- Flag for potential removal or imputation investigation

## Duplicates

- [ ] **Exact duplicate rows** -- `df.duplicated().sum()`
- [ ] **Near-duplicate detection** -- Check key columns for records that differ only in minor fields

## Target Analysis

- [ ] **Target distribution** -- Class balance (classification) or distribution shape (regression)
- [ ] **Target-feature correlations** -- Rank features by correlation with target
- [ ] **Point-biserial correlation** -- For categorical features vs. continuous target

## Numeric Distributions

- [ ] **Summary statistics** -- Mean, median, std, min, max, percentiles (p5, p25, p75, p95)
- [ ] **Skewness** -- Flag features with |skewness| > 2 for potential log transform
- [ ] **Outlier detection** -- IQR method (below Q1-1.5*IQR or above Q3+1.5*IQR) and z-score method

## Categorical Distributions

- [ ] **Value counts** -- Top values and their frequencies
- [ ] **Rare categories** -- Categories with <1% frequency
- [ ] **High cardinality** -- Columns with >50 unique values (consider encoding strategy)

## Temporal Patterns

- [ ] **Time range** -- Earliest and latest dates
- [ ] **Gaps** -- Missing time periods or irregular frequency
- [ ] **Seasonality** -- Weekly, monthly, or yearly patterns
- [ ] **Trend** -- Increasing or decreasing over time

## Correlations

- [ ] **Numeric correlation matrix** -- Pearson correlation heatmap
- [ ] **Top correlated pairs** -- Pairs with |r| > 0.8 (potential multicollinearity)
- [ ] **Multicollinearity check** -- VIF (variance inflation factor) for features >10
- [ ] **Cross-feature patterns** -- Scatter matrix for top features

## Red Flags

- [ ] **Constant/near-constant** -- Columns with single value or >99% same value
- [ ] **ID-like columns** -- Columns with all unique values (potential identifiers, not features)
- [ ] **Leakage suspects** -- Features with suspiciously high target correlation (>0.95)
- [ ] **Suspicious distributions** -- Features that look derived from the target

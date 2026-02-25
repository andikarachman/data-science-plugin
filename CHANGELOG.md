# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [2.6.0] - 2026-02-25

### Added
- `tuning-hyperparameters` skill -- hyperparameter tuning workflow reference with strategy selection decision tree, Bayesian optimization with Optuna, search space design patterns, and result analysis with 4 reference files (strategy selection, Optuna guide, search space design, result analysis)
- `/ds:experiment` now references `tuning-hyperparameters` for strategy selection (step 3), Optuna code scaffolds (step 6), and tuning result analysis (step 7)
- `optuna` added to `setup` skill optional library checks
- `optuna` added to `requirements.txt` as optional dependency
- `experiment-review` template now includes expanded tuning assessment checklist with strategy appropriateness, budget adequacy, and CV strategy match

### Changed
- `experiment-designer` agent now references `tuning-hyperparameters` for strategy selection at resource budget step
- `model-evaluator` agent now references `tuning-hyperparameters` for post-tuning convergence and search coverage assessment
- `scikit-learn` skill "Role in ds plugin" paragraph updated with `tuning-hyperparameters` boundary clarification

## [2.5.0] - 2026-02-25

### Added
- `polars` skill -- Polars expression API for high-performance DataFrame operations, lazy evaluation, joins, aggregations, and I/O with 6 reference files (core concepts, operations, pandas migration, I/O guide, transformations, best practices)
- `/ds:eda` now references `polars` for large-dataset lazy scanning (step 3), schema inspection (step 4), expression-based distribution analysis (step 5), and join patterns (step 7)
- `/ds:preprocess` now references `polars` for I/O optimization with lazy scanning (step 2)
- `/ds:experiment` now references `polars` for window features and join patterns (step 3) and expression-based code scaffolds (step 6)
- `/ds:plan` now references `polars` for large-dataset handling with lazy evaluation and streaming (step 3)
- `/ds:validate` now references `polars` for data loading (step 2)
- `polars` added to `setup` skill optional library checks
- `polars` added to `requirements.txt` as optional dependency

### Changed
- `data-profiler` agent now references `polars` for schema inspection and memory-efficient profiling with lazy evaluation
- `feature-engineer` agent now references `polars` for `over()` window functions and join-based feature assembly
- `pipeline-builder` agent now references `polars` for lazy scanning and expression-based data assessment
- `pandas-pro` skill "Role in ds plugin" paragraph updated with `polars` boundary clarification
- `data-preprocessing` skill "Role in ds plugin" paragraph updated with polars interop note

## [2.4.0] - 2026-02-25

### Added
- `data-quality-frameworks` skill -- data quality validation with Great Expectations, dbt tests, and data contracts (6 patterns: GX suite, GX checkpoint, dbt tests, custom dbt tests, data contracts, automated pipeline)
- `/ds:validate` command -- run formal data quality validation with expectation suites, quality dimension assessment, and framework detection (Great Expectations or pandas fallback)
- `validation-report` template -- validation results with per-expectation outcomes, quality dimension summary, data contract status, and pass/fail decision
- `great_expectations` added to `setup` skill optional library checks
- `/ds:preprocess` step 8 now offers `/ds:validate` as next step
- `/ds:eda` step 6 now references `data-quality-frameworks` for formal quality validation
- `/ds:review` step 3 now includes data quality audit in methodology assessment
- `docs/ds/validations/` output directory for validation reports
- `validation` added to `lifecycle_stage` enum in `/ds:compound` and `CLAUDE.md`
- `/ds:plan` step 5 now suggests `/ds:validate` as a next step option
- `/ds:eda` step 6 now checks for existing validation artifacts before running quality checks
- `/ds:compound` now searches `docs/ds/validations/` for learning extraction

### Changed
- `data-profiler` agent now references `data-quality-frameworks` skill with boundary clarification
- `pipeline-builder` agent now recommends `/ds:validate` for post-pipeline quality verification
- `data-preprocessing` skill "Role in ds plugin" paragraph updated with `data-quality-frameworks` validation boundary
- Workflow updated from `Frame -> Preprocess -> Explore -> ...` to `Frame -> Preprocess -> Validate -> Explore -> ...`

## [2.3.0] - 2026-02-25

### Added
- `pandas-pro` skill -- canonical pandas API reference for the plugin with 5 reference files (DataFrame operations, data cleaning, aggregation/groupby, merging/joining, performance optimization)
- `/ds:eda` now references `pandas-pro` for data loading (step 3), structural profiling (step 4), distribution analysis (step 5), and relationship analysis (step 7)
- `/ds:preprocess` now references `pandas-pro` for I/O optimization (step 2)
- `/ds:experiment` now references `pandas-pro` for feature assembly merge patterns (step 3) and data preparation code scaffolds (step 6)
- `/ds:plan` now references `pandas-pro` for large-dataset handling strategy (step 3)
- Cross-references between `pandas-pro` reference files and related ds plugin skills

### Changed
- `data-profiler` agent now references `pandas-pro` for DataFrame operation patterns and memory profiling
- `feature-engineer` agent now references `pandas-pro` for aggregation and merge patterns in multi-table feature assembly
- `pipeline-builder` agent now references `pandas-pro` for efficient pandas patterns in data assessment code
- `data-preprocessing` skill "Role in ds plugin" paragraph updated with `pandas-pro` boundary clarification
- `scikit-learn` skill "Role in ds plugin" paragraph updated with `pandas-pro` boundary clarification
- `pandas-pro` data-cleaning.md trimmed to remove overlap with `data-preprocessing` (4 sections removed: dropping missing values, removing duplicates, validation functions, pipeline with validation)

## [2.2.1] - 2026-02-25

### Added
- Pre-model imputation methods in `data-preprocessing` skill -- median imputation for numeric columns, mode imputation for categorical columns, KNN imputation using correlated features with LabelEncoder for mixed types
- Text processing operations in `data-preprocessing` skill -- extract_numbers, clean_whitespace, extract_email, lowercase, remove_special
- IQR-based outlier capping (winsorization) in `data-preprocessing` skill -- preserves all rows by clipping values at IQR fence
- Z-score outlier removal in `data-preprocessing` skill -- alternative to IQR for normally distributed data
- Imputation, text processing, winsorization, and Z-score entries in error handling strategies reference
- Outlier method selection guide in SKILL.md and transformation methods reference

### Changed
- `data-preprocessing` skill "Role in ds plugin" paragraph updated with imputation boundary clarification
- `scikit-learn` skill "Role in ds plugin" paragraph updated with bilateral imputation boundary
- `pipeline-builder` agent now recommends imputation strategies, text processing, and expanded outlier methods
- Pipeline step sequence expanded from 8 to 11 steps in `references/pipeline_configuration.md`
- Column-type routing table updated with imputation and text processing recommendations
- Preprocessing report template Column-Level Changes table expanded with imputation, text, and outlier capping examples
- Config template YAML updated with imputation, text processing, and alternative outlier step examples

## [2.2.0] - 2026-02-25

### Added
- `data-preprocessing` skill -- pre-model data preparation pipelines for cleaning, validation, transformation, and ETL orchestration, with 4 reference files, 3 scripts, and 1 config template
- `pipeline-builder` agent -- assess raw data quality and design preprocessing pipelines with temporal awareness and structural cleaning recommendations
- `/ds:preprocess` command -- clean, validate, and transform raw data using automated preprocessing pipelines with per-step tracking and SHA-256 hashing
- `preprocessing-report` template -- pipeline execution report with input/output summary, step log, before/after comparison, and validation results
- `/ds:eda` step 6b now references `data-preprocessing` skill with routing guidance for pre-model vs in-model preprocessing
- `/ds:experiment` steps 3 and 6 now reference `data-preprocessing` skill for pre-pipeline data preparation
- `/ds:plan` step 5 now suggests `/ds:preprocess` as a next step option
- `preprocessing` added to `lifecycle_stage` enum in `/ds:compound` and `CLAUDE.md`
- `docs/ds/preprocessing/` added to output directories

### Changed
- `scikit-learn` skill "Role in ds plugin" paragraph updated with `data-preprocessing` boundary clarification
- Workflow updated from `Frame -> Explore -> ...` to `Frame -> Preprocess -> Explore -> ...`

## [2.1.0] - 2026-02-24

### Added
- `shap` skill -- API patterns for model interpretability using SHAP (SHapley Additive exPlanations) -- explainer selection, feature attribution, visualization (beeswarm, waterfall, scatter, bar, force, heatmap), with 4 reference files
- `/ds:experiment` now uses `shap` for feature attribution code scaffolds (step 6) and model-agnostic SHAP explanations in supervised, temporal supervised, and time-series forecasting results (step 7)
- `/ds:review` now includes interpretability as a methodology assessment dimension (step 3)
- `/ds:ship` now uses `shap` for model card evidence in Limitations and Fairness sections (step 3)
- Interpretability section added to `model-card` template

### Changed
- `model-evaluator` agent now references `shap` skill for feature attribution, individual prediction explanations, and fairness cohort comparison
- `feature-engineer` agent now resolves bare SHAP mention to `shap` skill with specific reference paths
- `deployment-readiness` agent now references `shap` skill for fairness/compliance evidence
- `scikit-learn` skill "Role in ds plugin" paragraph updated with `shap` boundary clarification
- `experiment-result` template Key Plots comments updated with SHAP visualization guidance

## [2.0.0] - 2026-02-24

### Added
- `/ds:review` command -- peer review experiments for methodology, leakage, reproducibility, and statistical validity
- `/ds:ship` command -- assess deployment readiness, generate model cards and deployment documentation
- `reproducibility-auditor` agent -- audit experiments for reproducibility (seeds, versions, data hashes, environment)
- `deployment-readiness` agent -- evaluate models for production deployment readiness
- `reproducibility-checklist` skill -- verify experiment reproducibility requirements with scoring rubric
- `model-card` skill -- generate standardized model documentation following HuggingFace and NVIDIA Model Card++ formats
- `experiment-review` template -- peer review document with methodology, leakage, reproducibility, and statistical validity sections
- `model-card` template -- standardized model documentation for deployment handoff
- `deployment-readiness` template -- deployment readiness assessment with monitoring, rollback, and SLA sections
- Project-level retrospective step in `/ds:compound` using `postmortem` template (step 9)

### Changed
- `/ds:compound` command now includes `disable-model-invocation: true` and optional postmortem generation
- `eda-checklist` skill now includes explicit "Role in ds plugin" boundary paragraph with `exploratory-data-analysis` skill

### Removed
- `dataset-assessment` template -- consolidated with `exploratory-data-analysis` skill's `assets/report_template.md` to resolve EDA template duality

## [1.8.0] - 2026-02-24

### Added
- `aeon` skill -- API patterns for time series machine learning (classification, regression, clustering, anomaly detection, segmentation, similarity search, distance metrics) with 11 reference files
- Three new experiment paradigms in `/ds:experiment` -- temporal supervised (time-series classification/regression), temporal unsupervised (time-series clustering), and anomaly detection, extending routing from 3 to 6 paradigms
- `/ds:experiment` now uses `aeon` for algorithm selection (step 3), code scaffolding (step 6), and evaluation (step 7) across all new paradigms
- `/ds:eda` now uses `aeon` for temporal feature extraction suggestions (step 5) and time-series similarity/segmentation analysis (step 7b)
- `/ds:plan` now uses `aeon` for time-series ML algorithm selection (step 3)
- Temporal supervised, temporal unsupervised, and anomaly detection fields added to `experiment-plan` and `experiment-result` templates

### Changed
- `experiment-designer` agent now supports temporal supervised and anomaly detection experiment framing with 2 new examples
- `model-evaluator` agent now references `aeon` for range-based metrics, clustering accuracy, and statistical comparison (Wilcoxon, Nemenyi)
- `data-profiler` agent now references `aeon` for temporal feature extraction (Catch22, ROCKET)
- `feature-engineer` agent now includes time-series feature candidates from `aeon` transformations
- `statsmodels` and `scikit-learn` skill "Role in ds plugin" paragraphs updated with `aeon` boundary clarification
- EDA report template updated with `aeon` references for temporal analysis
- Time-series forecasting path enhanced with `aeon` ML-based forecaster alternatives (TCN, DeepAR)

## [1.7.0] - 2026-02-24

### Added
- `matplotlib` skill -- API patterns for plot types, styling, multi-panel figures, and export with 4 reference files and 2 scripts
- `/ds:eda` now uses `matplotlib` for distribution visualization (step 5) and correlation heatmaps (step 7)
- `/ds:experiment` now uses `matplotlib` for code scaffold visualization boilerplate (step 6) and result plots across all three paradigms (step 7)

### Changed
- `data-profiler` agent now references `matplotlib` skill for visualization patterns
- `model-evaluator` agent now references `matplotlib` skill for result figure composition
- EDA report template and experiment result template updated with matplotlib visualization guidance

## [1.6.0] - 2026-02-24

### Added
- `statsmodels` skill -- API patterns for OLS, GLM, discrete choice models, time series (ARIMA/SARIMAX), and statistical diagnostics with 5 reference files
- Time-series experiment workflow in `/ds:experiment` -- three-way routing at step 1b (supervised/unsupervised/time-series) with conditional steps for stationarity testing, ARIMA order selection, temporal splits, and forecast evaluation
- `/ds:experiment` now uses `statsmodels` for regression/GLM model selection (step 3), code scaffolding (step 6), and model diagnostics (step 7)
- `/ds:eda` now uses `statsmodels` for VIF multicollinearity checks (step 7a) and stationarity testing (step 7b)
- `/ds:plan` now uses `statsmodels` for inference/GLM/time-series approach selection (step 3)
- Time-series fields added to `experiment-plan` and `experiment-result` templates

### Changed
- `experiment-designer` agent now supports time-series experiment framing alongside supervised and unsupervised
- `statistical-analysis` skill "Role in ds plugin" paragraph updated to clarify boundary with `statsmodels` skill

## [1.5.0] - 2026-02-24

### Added
- Unsupervised experiment workflow in `/ds:experiment` -- routing step (1b) detects supervised vs. unsupervised, conditional text in steps 2, 3, 4, 7 for clustering and dimensionality reduction experiments
- `scikit-learn` skill wired into `/ds:eda` (preprocessing patterns at step 6b) and `/ds:plan` (algorithm selection at step 3)
- matplotlib and seaborn added to setup skill optional checks and requirements.txt

### Fixed
- Replaced broken `feature-importance` skill reference with inline scikit-learn guidance
- Replaced broken `time-series-validation` skill reference with split-strategy + scikit-learn TimeSeriesSplit guidance

### Changed
- `experiment-designer` agent now supports both supervised and unsupervised experiment framing
- `experiment-plan` template updated with unsupervised fields (research question, stability assessment, cluster profiles)

## [1.4.0] - 2026-02-24

### Added
- `scikit-learn` skill -- API patterns for preprocessing, pipelines, model selection, hyperparameter tuning, and evaluation with 6 reference files and 2 example scripts
- `/ds:experiment` now uses `scikit-learn` for pipeline construction (step 3), code scaffold generation (step 6), and evaluation utilities (step 7)

## [1.3.0] - 2026-02-24

### Changed
- Replaced `statistical-tests` skill with comprehensive `statistical-analysis` skill -- adds assumption checking script, Bayesian methods, APA reporting templates, power analysis, and 5 reference files
- `/ds:experiment` now uses `statistical-analysis` for test selection, power analysis, assumption verification, and APA-formatted reporting

## [1.2.0] - 2026-02-24

### Added
- `exploratory-data-analysis` skill -- file type detection and format-specific EDA for 200+ scientific formats, with analyzer script, report template, and 6 format reference files
- File type detection step in `/ds:eda` command workflow
- Structured report template reference in `/ds:eda` artifact output

## [1.1.0] - 2026-02-24

### Added
- `requirements.txt` with required and optional Python dependencies
- `setup` skill (`/ds:setup`) -- check Python environment for required libraries and report versions
- Prerequisites section in README with `uv pip install` commands

## [1.0.0] - 2026-02-24

### Added
- Plugin scaffold with `"name": "ds"` namespace
- 6 agents: problem-framer, data-profiler, feature-engineer, experiment-designer, model-evaluator, documentation-synthesizer
- 4 commands: `/ds:plan`, `/ds:eda`, `/ds:experiment`, `/ds:compound`
- 5 skills: eda-checklist, split-strategy, target-leakage-detection, experiment-tracking, statistical-tests
- 5 templates: problem-framing, dataset-assessment, experiment-plan, experiment-result, postmortem
- Compounding mechanism with `docs/ds/learnings/` and enhanced YAML frontmatter
- Learnings search with relevance ranking (tag overlap, recency, outcome filtering)
- Deduplication gate in `/ds:compound`
- Cold start handling (auto-creates `docs/ds/` directories)
- Large dataset sampling (100K rows when >100MB)
- MCP server: context7 for framework documentation lookup

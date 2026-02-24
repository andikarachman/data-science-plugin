# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

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

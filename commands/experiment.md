---
name: ds:experiment
description: Design an ML experiment with hypothesis, split strategy, leakage check, and evaluation plan
argument-hint: "[experiment description or hypothesis]"
---

# Design and Run Experiments

## Input

<experiment_description> $ARGUMENTS </experiment_description>

**If the experiment description above is empty, ask the user:** "What experiment do you want to run? Describe the hypothesis, model, or approach you want to test."

## Workflow

### 1. Search Past Experiments

Search `docs/ds/learnings/*.md` for `category: modeling` and `category: features` learnings. Also search `docs/ds/experiments/` for related prior work.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

Surface what was tried before and what worked/failed.

### 1b. Experiment Type Detection

Determine the experiment type:
- **Supervised** (classification, regression) -- has a target variable, cross-sectional data. Proceed to step 2.
- **Temporal supervised** (time-series classification, time-series regression) -- input features are time series (3D shape: samples x channels x timepoints), target is a class label or continuous value. Use temporal supervised variants of steps 2-7 as noted below. Reference the `aeon` skill.
- **Unsupervised** (clustering, dimensionality reduction) -- no target variable, cross-sectional data. Use unsupervised variants of steps 2-7 as noted below.
- **Temporal unsupervised** (time-series clustering) -- input is a collection of unlabeled time series. Use temporal unsupervised variants of steps 2-7 as noted below. Reference the `aeon` skill.
- **Time-series forecasting** (forecasting, temporal modeling) -- target is future values of a time-ordered variable. Use time-series variants of steps 2-7 as noted below.
- **Anomaly detection** -- input is one or more time series, goal is to identify unusual points, subsequences, or series. Use anomaly detection variants of steps 2-7 as noted below. Reference the `aeon` skill.

Detection heuristics:
- Temporal supervised: user mentions "classify time series", "time series classification/regression", or data has shape (samples, channels, timepoints)
- Temporal unsupervised: user mentions "cluster time series", "group similar series", or "time series clustering"
- Anomaly detection: user mentions "anomaly", "outlier", "unusual pattern", "discord", or "change point"

If unclear from the experiment description, ask the user.

### 2. Hypothesis Formulation

Use the `experiment-designer` agent.

**Supervised:**
- Null hypothesis and alternative hypothesis
- Independent variable (what's being changed)
- Dependent variable (what's being measured)
- Controls (what's held constant)

**Unsupervised:**
- Research question (e.g., "Are there natural customer segments?", "Can we reduce to N dimensions with <X% information loss?")
- What structure or patterns are expected and why
- Controls (what's held constant across algorithm comparisons)

**Temporal supervised:**
- Classification/regression hypothesis (e.g., "ROCKET will classify ECG signals with >90% accuracy, outperforming 1-NN Euclidean baseline")
- What temporal patterns distinguish the classes or predict the target
- Data format confirmation: `(n_samples, n_channels, n_timepoints)`

**Temporal unsupervised:**
- Clustering hypothesis (e.g., "DTW-based k-means with k=5 will reveal distinct operational regimes in sensor data")
- What temporal structure is expected and why
- Distance metric rationale (DTW for alignment, Euclidean for speed)

**Time-series forecasting:**
- Forecasting hypothesis (e.g., "SARIMAX(1,1,1)(1,1,0,12) will outperform exponential smoothing for monthly sales, measured by out-of-sample RMSE")
- What temporal patterns are expected (trend, seasonality, cycles)
- Forecast horizon and granularity

**Anomaly detection:**
- Detection hypothesis (e.g., "STOMP with window_size=50 will identify >80% of known anomalies with <5% false positive rate")
- What constitutes an anomaly in this domain (point, subsequence, or collection-level)
- Whether labeled anomaly examples are available (semi-supervised vs unsupervised)

### 3. Methodology Design

**Supervised -- define:**
- **Data split strategy** -- invoke `split-strategy` skill
- **Feature set** -- reference any feature engineering from prior EDA
- **Model(s) to evaluate**
- **Hyperparameter search strategy** (grid, random, Bayesian)
- **Evaluation metrics** (primary + secondary)
- **Baseline to beat**

**Unsupervised -- define:**
- **Stability assessment** -- resampling strategy to evaluate cluster/embedding stability
- **Feature set** -- reference any preprocessing from prior EDA
- **Algorithm(s) to compare** -- reference `scikit-learn` skill's `references/unsupervised_learning.md`
- **Hyperparameter search strategy** (e.g., number of clusters range for K-Means, eps/min_samples for DBSCAN)
- **Internal evaluation metrics** -- silhouette score, Davies-Bouldin index, Calinski-Harabasz index, explained variance ratio (for DR)
- **Algorithm comparison protocol** -- how to rank algorithms against each other

**Temporal supervised -- define:**
- **Data format verification** -- confirm 3D shape `(n_samples, n_channels, n_timepoints)`. Reference `aeon` skill's SKILL.md "Data Preparation" section. If tabular, reshape: `X.values.reshape(n_samples, 1, -1)`
- **Algorithm selection** -- reference `aeon` skill's `references/classification.md` (or `references/regression.md`). Algorithm selection guide: MiniROCKET for speed, HIVECOTEV2/InceptionTime for accuracy, ShapeletTransform/Catch22 for interpretability, KNeighborsTimeSeries with DTW for small datasets
- **Feature extraction alternative** -- if converting to tabular for traditional ML, reference `aeon` skill's `references/transformations.md` (ROCKET, Catch22, TSFresh) then use scikit-learn classifiers
- **Distance metric selection** -- for distance-based methods, reference `aeon` skill's `references/distances.md` for DTW, LCSS, ERP, etc.
- **Split strategy** -- invoke `split-strategy` skill. For temporal classification, standard stratified splits are acceptable (unlike forecasting which requires temporal splits)
- **Evaluation metrics** -- standard classification/regression metrics from scikit-learn. Reference `aeon` skill's `references/datasets_benchmarking.md` for comparison with published results on standard datasets
- **Baseline** -- 1-NN with Euclidean distance (standard time-series classification baseline)

**Temporal unsupervised -- define:**
- **Algorithm selection** -- reference `aeon` skill's `references/clustering.md`. Algorithm selection guide: TimeSeriesKMeans with DTW for alignment-based, Catch22Clusterer for interpretability, deep learning clusterers for complex patterns, TimeSeriesCLARA for large datasets
- **Distance metric** -- reference `aeon` skill's `references/distances.md`. Critical choice for clustering quality. DTW for temporal alignment, Euclidean for speed, LCSS for outlier robustness
- **Averaging method** -- barycentric averaging (`ba`) for DTW-based clustering, shift-invariant for phase-shifted series
- **Internal metrics** -- silhouette score, Davies-Bouldin, clustering accuracy (if ground truth available) from `aeon` skill's `references/datasets_benchmarking.md`
- **Algorithm comparison protocol** -- how to rank algorithms against each other

**Time-series forecasting -- define:**
- **Stationarity assessment** -- ADF and KPSS tests. Reference `statsmodels` skill's `references/time_series.md`
- **Temporal split strategy** -- invoke `split-strategy` skill with temporal mode. Reference `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit) for expanding/sliding window splits
- **Model identification** -- ACF/PACF analysis for ARIMA order selection. Reference `statsmodels` skill's `references/time_series.md`
- **Model(s) to evaluate** -- ARIMA, SARIMAX, Exponential Smoothing, or VAR. Use `statsmodels` skill's SKILL.md Quick Start and `references/time_series.md`. When classical models are insufficient, reference `aeon` skill's `references/forecasting.md` for ML-based alternatives: TCNForecaster for long sequences, DeepARNetwork for probabilistic forecasts, RegressionForecaster for using any regressor as a forecaster
- **Forecast evaluation metrics** -- RMSE, MAE, MAPE on out-of-sample period
- **Baseline** -- naive forecast (last value or seasonal naive)

**Anomaly detection -- define:**
- **Anomaly type** -- point, subsequence (discord), or collection-level. Reference `aeon` skill's `references/anomaly_detection.md` "Point vs Subsequence Anomalies" section
- **Algorithm selection** -- reference `aeon` skill's `references/anomaly_detection.md` algorithm selection guide: STOMP for discord discovery, IsolationForest for no-training-data, ROCKAD for semi-supervised, LeftSTAMPi for streaming, COPOD for multi-dimensional
- **Window size** -- critical parameter for matrix profile methods (rule of thumb: 10-20% of series length). Reference `aeon` skill's `references/similarity_search.md` best practices
- **Threshold strategy** -- percentile-based, domain-specific, or statistical
- **Evaluation metrics** -- range-based precision/recall/F1 from `aeon` skill's `references/datasets_benchmarking.md`, ROC AUC for scored output

Invoke the `statistical-analysis` skill for:
- **Test selection**: Use `references/test_selection_guide.md` to choose the right statistical test for the comparison protocol
- **Power analysis**: Determine minimum sample size needed to detect the expected effect size
- **Assumption planning**: Note which assumptions will need checking after results are in

Invoke the `scikit-learn` skill for:
- **Pipeline construction**: Use `references/pipelines_and_composition.md` to design preprocessing + model pipelines with `Pipeline` and `ColumnTransformer`
- **Hyperparameter search implementation**: Use `references/model_evaluation.md` for concrete `GridSearchCV` / `RandomizedSearchCV` patterns
- **Algorithm selection**: Use `references/quick_reference.md` for algorithm selection cheat sheets based on data characteristics

Invoke the `tuning-hyperparameters` skill for:
- **Strategy selection**: Use `references/strategy_selection.md` to choose between grid, random, Bayesian (Optuna), or halving based on search space size and computational budget
- **Bayesian optimization**: When the search space is large (>500 combinations) or evaluations are expensive, use `references/optuna_guide.md` for Optuna study/trial patterns and pruning
- **Search space design**: Use `references/search_space_design.md` for per-model hyperparameter range cheat sheets and distribution selection

When data requires pre-model preparation (deduplication, format conversion, structural cleaning) before pipeline construction, reference the `data-preprocessing` skill's `references/transformation_methods.md` for pre-model transform patterns. For in-model preprocessing inside sklearn Pipelines, continue using the `scikit-learn` skill.

When the methodology involves assembling features from multiple data sources, reference the `pandas-pro` skill's `references/merging-joining.md` for merge strategies and cardinality validation. For rolling/window feature engineering, reference the `pandas-pro` skill's `references/aggregation-groupby.md` (Window Functions, Shift and Diff sections). **For large datasets using Polars**, reference the `polars` skill's `references/transformations.md` for join patterns and `references/operations.md` for `over()` window functions.

Invoke the `statsmodels` skill when the experiment involves inference or time-series:
- **Regression with inference** (need p-values, coefficient interpretation): Use `references/linear_models.md` for OLS/WLS/GLS model selection and robust standard errors
- **GLM** (non-normal outcomes -- counts, binary, proportions): Use `references/glm.md` for family and link function selection
- **Discrete choice** (multinomial, ordinal, zero-inflated counts): Use `references/discrete_choice.md` for model selection
- **Time-series model identification**: Use `references/time_series.md` for ARIMA order selection via ACF/PACF, stationarity testing, and seasonal decomposition

If temporal data is detected, use the `split-strategy` skill with temporal mode and reference the `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit section) for time-aware cross-validation.

### 4. Leakage Check (supervised, temporal supervised, time-series forecasting)

**Supervised:** Invoke `target-leakage-detection` skill on the proposed feature set.

**Temporal supervised:** Invoke `target-leakage-detection` skill -- check that normalization/transformation parameters are fit on training data only (aeon best practice: `fit_transform` on train, `transform` on test).

**Time-series forecasting:** Invoke `target-leakage-detection` skill with temporal focus -- check that no future information leaks into training features. Verify that the temporal split boundary is respected.

**Unsupervised / Temporal unsupervised:** Skip this step (no target variable).

**Anomaly detection:** Skip traditional leakage check. For semi-supervised methods (ROCKAD, OneClassSVM), verify that labeled anomaly examples are not used during training -- only normal data should be used for fitting.

### 5. Write Experiment Plan

Generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md` from `templates/experiment-plan.md`.

Create the directory if needed: `mkdir -p docs/ds/experiments/`

### 6. Execute or Defer

Ask the user: "Experiment plan ready. What next?" with options:
- Write experiment code scaffold
- Just save the plan (implement later)
- Review plan with `/ds:review`

When generating the code scaffold, use the `scikit-learn` skill's pipeline patterns (`references/pipelines_and_composition.md`) and the example scripts (`scripts/classification_pipeline.py` or `scripts/clustering_analysis.py`) as structural references. For proper pandas indexing and vectorized operations in generated code, reference the `pandas-pro` skill's `references/dataframe-operations.md` (use `.loc[]`/`.iloc[]`, avoid chained indexing). **For large datasets using Polars**, reference the `polars` skill's `references/operations.md` for expression-based code patterns (use `pl.col()`, avoid Python loops). If the data requires pre-pipeline cleaning (deduplication, type coercion, structural missing data removal), include a data preparation section referencing the `data-preprocessing` skill's `scripts/transform_data.py` before the sklearn Pipeline code.

When the methodology selects Bayesian optimization, reference the `tuning-hyperparameters` skill's `references/optuna_guide.md` for Optuna study/objective patterns and `OptunaSearchCV` integration with sklearn pipelines. For search space definition, reference the `tuning-hyperparameters` skill's `references/search_space_design.md` for per-model cheat sheets.

When the experiment uses statsmodels models (OLS, GLM, ARIMA), reference the `statsmodels` skill's Quick Start Guide and formula API examples in SKILL.md for code scaffold generation.

When the experiment uses aeon time-series ML (temporal supervised, temporal unsupervised, anomaly detection), reference the `aeon` skill's SKILL.md "Common Workflows" section for pipeline structure. Use aeon import patterns:
- Classification: `from aeon.classification.convolution_based import RocketClassifier`
- Clustering: `from aeon.clustering import TimeSeriesKMeans`
- Anomaly detection: `from aeon.anomaly_detection import STOMP`
- Transformations: `from aeon.transformations.collection.convolution_based import RocketTransformer`
Include data format comments: `# Shape: (n_samples, n_channels, n_timepoints)`

When the time-series forecasting experiment uses ML-based forecasters, reference the `aeon` skill's `references/forecasting.md` for TCNForecaster, DeepARNetwork, or RegressionForecaster patterns.

Include matplotlib visualization boilerplate in the code scaffold. Use the `matplotlib` skill's OO interface convention (`fig, ax = plt.subplots(constrained_layout=True)`) and always close figures after saving (`plt.savefig()` + `plt.close(fig)`). Reference the `matplotlib` skill's `scripts/plot_template.py` for plot function structure.

For supervised and temporal supervised experiments, include SHAP computation and visualization boilerplate after model training. Reference the `shap` skill's SKILL.md Quick Start Guide for the explainer selection decision tree and code patterns. Use `shap.TreeExplainer` for tree-based models, `shap.LinearExplainer` for linear models, or `shap.Explainer(model)` for auto-selection. Include `shap.plots.beeswarm()` for global importance and `shap.plots.waterfall()` for individual predictions. Follow DS plugin conventions: `show=False`, `plt.savefig()` + `plt.close(fig)`.

### 7. Generate Results (if executing)

After completion, generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md` from `templates/experiment-result.md` with:
- Environment details (Python version, library versions, git commit SHA)
- Data hash (SHA-256 of the dataset file)
- Compute cost (wall time, GPU hours if applicable)
- Key observations

**Supervised results:**
- Actual metrics vs. baseline
- Use the `model-evaluator` agent for comprehensive performance assessment
- Use the `scikit-learn` skill's evaluation utilities:
  - Generate classification/regression metrics using `references/model_evaluation.md` patterns
  - Create learning curves and validation curves for overfitting diagnosis
- Run the `statistical-analysis` skill's assumption checks on the results:
  - Use `scripts/assumption_checks.py` to verify normality and variance homogeneity of residuals/predictions
  - Report results in APA format using `references/reporting_standards.md`
  - Calculate and report effect sizes with confidence intervals
- For feature attribution analysis, use the `scikit-learn` skill's feature importance patterns: tree-based `feature_importances_` from `references/supervised_learning.md`, feature selection via `references/preprocessing.md` (RFE, SelectFromModel), and `sklearn.inspection.permutation_importance` for model-agnostic importance
- For model-agnostic feature attribution with per-prediction explanations, use the `shap` skill. Use `references/explainers.md` to select the right explainer (TreeExplainer for tree-based models, LinearExplainer for linear models, KernelExplainer for any model). Generate global importance plots (`shap.plots.beeswarm()`) and individual prediction explanations (`shap.plots.waterfall()`). For feature interaction detection, use `shap.plots.scatter()` with color-coded interaction features. See `references/plots.md` for all visualization options
- Use the `statsmodels` skill for model-specific diagnostics:
  - Residual analysis and influence diagnostics from `references/stats_diagnostics.md`
  - Model comparison via AIC/BIC tables from `references/linear_models.md` or `references/glm.md`
  - Robust standard errors (HC, HAC) when assumption checks reveal heteroskedasticity
- Use the `matplotlib` skill for result visualizations:
  - Multi-panel summary figure combining key diagnostic plots -- reference `references/api_reference.md` (GridSpec)
  - Custom residual plots and feature importance bar charts -- reference `references/plot_types.md`
  - For standard scikit-learn display plots (`ConfusionMatrixDisplay`, `RocCurveDisplay`), use the scikit-learn skill; use matplotlib for customization and composition
- When the experiment includes hyperparameter tuning, reference the `tuning-hyperparameters` skill's `references/result_analysis.md` for convergence diagnostics (is the search converging?), parameter importance ranking, and optimization history visualization. Include tuning results summary in the experiment report (best parameters, trials completed, convergence status, wall time).

**Temporal supervised results:**
- Standard classification/regression metrics (accuracy, F1, RMSE) from scikit-learn
- Use the `model-evaluator` agent for comprehensive performance assessment
- Comparison with published benchmarks if using standard datasets -- reference `aeon` skill's `references/datasets_benchmarking.md` for `get_estimator_results()`
- Algorithm comparison with statistical testing (Wilcoxon, Nemenyi) from `aeon` skill's `references/datasets_benchmarking.md`
- For interpretable models: feature importance from Catch22 features, shapelet visualization for ShapeletTransformClassifier
- For model-agnostic temporal model interpretation, use the `shap` skill. If the aeon estimator exposes `predict` or `predict_proba`, use `shap.KernelExplainer` with a subset of training data as background. For tree-based temporal models (after feature extraction with Catch22 or ROCKET), use `shap.TreeExplainer` on the downstream classifier. Reference `references/explainers.md` for explainer selection
- Use the `matplotlib` skill for result visualizations:
  - Confusion matrix (scikit-learn `ConfusionMatrixDisplay`), per-class accuracy bar charts
  - Time series examples from each class overlaid for visual comparison
  - For standard scikit-learn display plots, use the scikit-learn skill; use matplotlib for custom composition

**Temporal unsupervised results:**
- Internal metrics (silhouette score, Davies-Bouldin, clustering accuracy if ground truth available) from `aeon` skill's `references/datasets_benchmarking.md`
- Cluster center visualization: plot the average (barycentric) time series for each cluster
- Cluster profiling: describe each cluster by its temporal characteristics (shape, amplitude, frequency)
- Stability analysis: how consistent are clusters across resampling runs?
- Use the `matplotlib` skill for cluster visualizations:
  - Plot cluster centers as line plots (one line per cluster, color-coded)
  - Elbow curves and silhouette analysis

**Time-series forecasting results:**
- Forecast accuracy metrics (RMSE, MAE, MAPE) on out-of-sample period vs. baseline
- Use the `statsmodels` skill's diagnostic patterns:
  - Residual diagnostics from `references/stats_diagnostics.md` (Ljung-Box, heteroskedasticity)
  - Model diagnostic plots (`results.plot_diagnostics()`) from `references/time_series.md`
  - Information criteria comparison (AIC/BIC) across candidate models
- When using aeon ML-based forecasters, include aeon-specific evaluation metrics from `aeon` skill's `references/forecasting.md`
- When using scikit-learn or tree-based forecasters, use the `shap` skill to explain feature contributions to forecasts. Use `shap.TreeExplainer` for XGBoost/LightGBM-based forecasters or `shap.LinearExplainer` for linear forecasters
- Forecast visualization with prediction intervals
- Stationarity verification on residuals (ADF test)
- Use the `matplotlib` skill for forecast visualizations:
  - Forecast vs actual line plots -- reference `references/plot_types.md` (Section 1, Line Plots)
  - Prediction interval shading with `ax.fill_between()` -- reference `references/plot_types.md` (Section 11, Fill Between)
  - For standard statsmodels diagnostic plots (`plot_diagnostics()`, `plot_acf`/`plot_pacf`), use the statsmodels skill; use matplotlib for custom compositions

**Anomaly detection results:**
- Range-based precision, recall, F-score from `aeon` skill's `references/datasets_benchmarking.md` (`range_precision`, `range_recall`, `range_f_score`)
- ROC AUC for scored anomaly detection
- Threshold sensitivity analysis: how do metrics change across threshold values?
- Visualization: time series with anomaly scores overlay, threshold line, detected anomaly regions highlighted
- Use the `matplotlib` skill for anomaly visualizations:
  - Two-panel figure: time series on top, anomaly scores below -- reference `references/api_reference.md` (subplots)
  - Highlight anomalous regions with `ax.axvspan()` or `ax.fill_between()`
  - Follow DS plugin conventions: savefig + close, no plt.show

**Unsupervised results:**
- Internal metrics (silhouette score, Davies-Bouldin, Calinski-Harabasz, inertia) across algorithms and hyperparameter settings
- Stability analysis (how consistent are clusters/embeddings across resampling runs?)
- Visualization using PCA/t-SNE projection -- reference `scikit-learn` skill's `references/unsupervised_learning.md` and `scripts/clustering_analysis.py`
- Cluster profiling: describe each cluster by its feature distributions
- For dimensionality reduction: explained variance ratio, reconstruction error
- Use the `matplotlib` skill for cluster and DR visualizations:
  - Cluster scatter plots with color-coded groups -- reference `references/plot_types.md` (Section 2, Categorical Scatter)
  - Elbow curves and silhouette plots -- reference `references/plot_types.md` (Section 1, Line Plots)
  - For PCA/t-SNE projection code, use the scikit-learn skill; use matplotlib for rendering and styling

### 8. Experiment Tracking

Log the experiment using the `experiment-tracking` skill format, including:
- Hypothesis, configuration, results, decision
- Series linkage (parent/child experiments)
- Environment and reproducibility details

---
name: model-card
description: "Generate standardized model documentation following HuggingFace Model Card and NVIDIA Model Card++ formats. Use when preparing a model for deployment or handoff."
---

# Model Card Generation

Generate a standardized model card that documents a trained ML model's purpose, performance, limitations, and ethical considerations. Based on HuggingFace Model Card format and NVIDIA Model Card++ extensions.

## Required Sections

### 1. Model Details

| Field | Description |
|---|---|
| Name | Human-readable model name |
| Version | Model version (e.g., v1.0.0) |
| Type | Algorithm family (e.g., gradient boosting, neural network, linear regression) |
| Framework | Library used (scikit-learn, statsmodels, aeon, xgboost, etc.) |
| Task | What the model does (classification, regression, forecasting, anomaly detection, etc.) |
| Date trained | When the model was last trained |
| Author | Who developed the model |

### 2. Intended Use

Document the model's intended use case clearly:

- **Primary use case** -- The specific problem this model solves
- **Intended users** -- Who should use this model (data scientists, business analysts, automated systems)
- **Out-of-scope uses** -- What this model should NOT be used for
- **Deployment context** -- Where and how the model will be used (batch scoring, real-time API, embedded)

### 3. Training Data

| Field | Description |
|---|---|
| Source | Where the training data comes from |
| Date range | Time period of training data |
| Size | Number of samples and features |
| Data hash | SHA-256 hash for version tracking |
| Preprocessing | Key transformations applied |
| Known biases | Any known biases in the training data |

### 4. Evaluation Data

| Field | Description |
|---|---|
| Source | Same or different from training? |
| Date range | Time period of evaluation data |
| Size | Number of samples |
| Split strategy | How train/eval was split |

### 5. Metrics

Report performance metrics with context:

| Metric | Value | Baseline | Improvement | Confidence Interval |
|---|---|---|---|---|
| [Primary] | | | | |
| [Secondary] | | | | |

Include:
- Performance by subgroup/slice (if slicing was done)
- Calibration metrics (for probabilistic models)
- Latency metrics (inference time per sample)

### 6. Limitations

Document known limitations honestly:

- **Data limitations** -- What data scenarios the model hasn't seen
- **Performance limitations** -- Where the model performs poorly (specific slices, edge cases)
- **Temporal limitations** -- How quickly the model may degrade (data drift sensitivity)
- **Technical limitations** -- Hardware requirements, latency constraints, dependency versions

### 7. Ethical Considerations

- **Fairness** -- Potential for disparate impact across protected groups
- **Privacy** -- What personal data was used in training
- **Environmental impact** -- Training compute cost (if significant)
- **Dual use risk** -- Could the model be misused?

### 8. How to Get Started

Provide concrete usage examples:

```python
# Example: Loading and using the model
import joblib

model = joblib.load("path/to/model.pkl")
predictions = model.predict(X_new)
```

Include:
- Required dependencies and versions
- Input format and schema
- Output format and interpretation
- Common pitfalls

## Model Card Checklist

Before shipping, verify:

- [ ] All 8 sections are filled
- [ ] Metrics include confidence intervals
- [ ] Limitations are honest and specific (not generic disclaimers)
- [ ] Ethical considerations are addressed (even if "low risk -- no protected attributes used")
- [ ] Usage examples are runnable
- [ ] Dependencies and versions are specified
- [ ] Out-of-scope uses are documented

## Common Mistakes

| Mistake | Impact | Fix |
|---|---|---|
| Vague limitations ("may not work for all data") | Users can't assess risk | Be specific: "Accuracy drops 15% on samples with >50% missing values" |
| Missing subgroup metrics | Hides fairness issues | Report metrics for all meaningful slices |
| No baseline comparison | Can't assess model value | Always include baseline performance |
| Outdated training data dates | Users assume data is fresh | Include data recency and staleness risk |
| Missing dependency versions | Can't recreate environment | Pin exact versions in requirements |

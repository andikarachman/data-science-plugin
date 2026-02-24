---
title: "Deployment Readiness: [Model Name]"
date: YYYY-MM-DD
author: [Name]
model_card: "[path to model card]"
readiness: [ready | conditionally-ready | not-ready]
---

# Deployment Readiness: [Model Name]

## Summary
[1-2 sentence summary of readiness assessment]

## Infrastructure Requirements

### Compute
| Requirement | Specification | Status |
|---|---|---|
| CPU/GPU | [e.g., 2 vCPU, no GPU required] | [met/unmet] |
| Memory | [e.g., 4GB RAM] | [met/unmet] |
| Storage | [e.g., 500MB for model + dependencies] | [met/unmet] |
| Scaling | [e.g., horizontal scaling to N replicas] | [met/unmet] |

### Dependencies
| Dependency | Version | Size | Notes |
|---|---|---|---|
| [e.g., scikit-learn] | [1.4.0] | [~30MB] | |

### Data Pipeline
- **Input source:** [Where prediction input comes from]
- **Preprocessing steps:** [What must happen before inference]
- **Output destination:** [Where predictions go]
- **Data freshness:** [How recent input data must be]

## Monitoring Plan

### Input Monitoring
| Signal | Method | Threshold | Alert |
|---|---|---|---|
| Feature drift | [e.g., KS test on top features] | [e.g., p < 0.01] | [e.g., Slack + PagerDuty] |
| Missing values | [e.g., null rate per feature] | [e.g., >5% increase] | [e.g., Slack] |
| Volume anomaly | [e.g., request count vs historical] | [e.g., <50% or >200%] | [e.g., PagerDuty] |

### Output Monitoring
| Signal | Method | Threshold | Alert |
|---|---|---|---|
| Prediction drift | [e.g., distribution shift in scores] | [e.g., KL divergence > 0.1] | [e.g., Slack] |
| Confidence drop | [e.g., mean prediction confidence] | [e.g., <0.7 avg] | [e.g., Slack] |

### Performance Monitoring
| Metric | Baseline | Threshold | Frequency |
|---|---|---|---|
| [Primary metric] | [Current value] | [e.g., >5% degradation] | [e.g., weekly] |
| Latency (p99) | [Current value] | [e.g., >500ms] | [e.g., continuous] |

## Rollback Strategy

### Previous Version
- **Location:** [Path to previous model version]
- **Performance:** [Key metrics of previous version]
- **Verified deployable:** [yes/no]

### Rollback Triggers
- [ ] Primary metric degrades >X% for >Y hours
- [ ] Error rate exceeds Z%
- [ ] Latency p99 exceeds threshold
- [ ] Manual trigger by on-call

### Rollback Procedure
1. [Step-by-step rollback instructions]
2. [How to verify rollback succeeded]
3. [Who to notify]

### Deployment Strategy
[Big bang / Canary / A/B test / Shadow mode]

## Operational Considerations

### Retraining
- **Schedule:** [e.g., monthly, quarterly, on-trigger]
- **Trigger conditions:** [e.g., performance degradation >5%, data drift detected]
- **Retraining pipeline:** [automated / manual]
- **Validation before promotion:** [What checks must pass]

### Error Handling
- **Invalid inputs:** [How the model handles missing features, wrong types, out-of-range values]
- **Graceful degradation:** [Fallback behavior under load or partial failures]
- **Timeout handling:** [What happens if inference takes too long]

### SLA
| Dimension | Target |
|---|---|
| Availability | [e.g., 99.9%] |
| Latency (p50) | [e.g., <100ms] |
| Latency (p99) | [e.g., <500ms] |
| Throughput | [e.g., 1000 req/s] |

## Compliance and Fairness

### Fairness Assessment
| Protected Group | Metric | Value | Acceptable Range | Status |
|---|---|---|---|---|
| | | | | [pass/fail] |

### Regulatory Requirements
- [ ] [e.g., GDPR -- personal data handling documented]
- [ ] [e.g., Model explainability for regulated decisions]

### Audit Trail
- [ ] Prediction logging enabled
- [ ] Input/output pairs stored for audit
- [ ] Model version tracked in predictions

## Readiness Decision

**[Ready | Conditionally Ready | Not Ready]**

### Blockers (if not ready)
| # | Blocker | Severity | Owner | ETA |
|---|---|---|---|---|

### Conditions (if conditionally ready)
| # | Condition | Must Complete By | Owner |
|---|---|---|---|

## Sign-off
| Role | Name | Date | Approved |
|---|---|---|---|
| Model developer | | | [ ] |
| Reviewer | | | [ ] |
| Platform/Ops | | | [ ] |

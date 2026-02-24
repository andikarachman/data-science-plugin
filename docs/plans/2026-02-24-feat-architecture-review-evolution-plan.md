---
title: "Architecture Review and Evolution Plan for DS Plugin"
type: feat
date: 2026-02-24
status: pending
---

# Architecture Review and Evolution Plan for DS Plugin

## Overview

Comprehensive architecture review of the data science plugin at v1.8.0, analyzing component boundaries, integration quality, overlap risks, and proposing an evolution roadmap to v2.0 and v3.0. The plugin currently has 6 agents, 4 commands, 11 skills, and 5 templates supporting a `Frame -> Explore -> Experiment -> Compound` workflow.

---

## 1. Architecture and Responsibility Boundaries

### Component Type Definitions

| Component | Purpose | Does | Does NOT |
|-----------|---------|------|----------|
| **Command** | User entry point. Orchestrates a workflow stage. | Routes to agents/skills, manages artifact creation, carries state forward | Make autonomous decisions, contain reusable logic, generate code directly |
| **Agent** | Autonomous specialist. Deep expertise in one domain. | Analyze, recommend, generate structured output in its domain | Write files directly (returns text to command), duplicate skill logic, orchestrate other agents |
| **Skill** | Reusable playbook. Encodes methodology or API patterns. | Provide concrete code patterns, decision trees, checklists | Make decisions (skills inform, agents decide), write artifacts, depend on other skills |
| **Template** | Standardized output form. Defines what to fill in. | Define sections, required fields, conditional blocks per paradigm | Contain methodology (that's skills), make recommendations (that's agents) |

### Interaction Rules (Current)

```
User
  ↓
Command (orchestrator)
  ├── reads: templates (for output structure)
  ├── invokes: agents (for analysis/recommendations)
  ├── references: skills (for concrete patterns)
  └── writes: artifacts to docs/ds/
```

**Key principle from institutional learnings:** Agents advise, skills provide code. Every conceptual agent recommendation pairs with concrete code patterns in a skill.

### Common Failure Modes (Documented)

| Failure Mode | Example | Prevention |
|---|---|---|
| Phantom references | Command references a skill that doesn't exist | Invocation map audit before shipping |
| Unilateral boundaries | New skill overlaps old skill without both documenting the boundary | Bilateral boundary rule: both skills must have "Role in ds plugin" paragraphs |
| Binary routing that can't extend | Supervised-only routing blocked unsupervised experiments | Design for all paradigms, ship for one -- include routing even if partial |
| Library-user teaching library | scikit-learn skill duplicating matplotlib patterns | Library users don't teach; foundational skill is the single source of truth |
| Mid-path patching | Adding conditionals to every step instead of routing at entry | Extend routing at entry point, not mid-path |

---

## 2. Current End-to-End Workflow

### Implemented Workflow (v1.8.0)

```
Frame ──→ Explore ──→ Experiment ──→ Compound
  │           │            │              │
/ds:plan   /ds:eda   /ds:experiment  /ds:compound
  │           │            │              │
  ↓           ↓            ↓              ↓
docs/ds/   docs/ds/    docs/ds/       docs/ds/
plans/     eda/        experiments/   learnings/
```

### Stage-by-Stage Flow

| Stage | Command | Agents Invoked | Skills Referenced | Template Used | Output Artifact |
|-------|---------|----------------|-------------------|---------------|-----------------|
| Frame | `/ds:plan` | problem-framer | scikit-learn, statsmodels, aeon | problem-framing | `docs/ds/plans/YYYY-MM-DD-<name>-plan.md` |
| Explore | `/ds:eda` | data-profiler, feature-engineer | eda-checklist, target-leakage-detection, exploratory-data-analysis, scikit-learn, statsmodels, matplotlib, aeon | dataset-assessment (implicit), report_template | `docs/ds/eda/YYYY-MM-DD-<dataset>-eda.md` |
| Experiment | `/ds:experiment` | experiment-designer, model-evaluator | split-strategy, target-leakage-detection, statistical-analysis, scikit-learn, experiment-tracking, statsmodels, matplotlib, aeon | experiment-plan, experiment-result | `docs/ds/experiments/YYYY-MM-DD-<exp>-plan.md` + `*-result.md` |
| Compound | `/ds:compound` | documentation-synthesizer | -- | postmortem (implicit) | `docs/ds/learnings/YYYY-MM-DD-HHMMSS-<topic>.md` |

### State Passing Between Stages

State is carried forward through:
1. **Artifact files** -- each command reads artifacts from prior stages (EDA report informs experiment design)
2. **Learnings search** -- every command searches `docs/ds/learnings/` before starting work
3. **User context** -- the user provides continuity by referencing prior work in command arguments

### Gap: Review and Ship Stages

The original design included `Review` and `Ship` stages, but these are not implemented:

```
Frame ──→ Explore ──→ Experiment ──→ [Review] ──→ [Ship] ──→ Compound
                                       ↑              ↑
                                    missing         missing
```

**Impact:** Users go directly from experiment results to compounding. There is no structured peer review of methodology and no deployment readiness check. This is the single largest gap in the current workflow.

---

## 3. Non-Overlapping Component Taxonomy

### Naming Conventions (Current -- Working Well)

| Component | Convention | Example |
|-----------|-----------|---------|
| Commands | Flat in `commands/`, name in frontmatter as `ds:<verb>` | `commands/plan.md` with `name: ds:plan` |
| Agents | Category subdirs `agents/<category>/<name>.md` | `agents/analysis/data-profiler.md` |
| Skills | Kebab-case dirs `skills/<name>/SKILL.md` | `skills/scikit-learn/SKILL.md` |
| Templates | Flat in `templates/<name>.md` | `templates/experiment-plan.md` |

### Decision Rules: When to Create What

```
Should it be a...

COMMAND?
  → Is it a user entry point that orchestrates multiple components?
  → Does it produce a dated artifact in docs/ds/?
  → Does it represent a distinct workflow stage?
  If yes to all → Command.

AGENT?
  → Does it require deep domain expertise and autonomous reasoning?
  → Does it analyze, recommend, or generate structured text?
  → Would it benefit from <examples> blocks for routing?
  If yes to all → Agent.

SKILL?
  → Is it a reusable methodology, checklist, or API pattern?
  → Is it invoked by multiple commands/agents?
  → Does it encode "how to do X" without making decisions?
  If yes to any → Skill.

TEMPLATE?
  → Does it define the structure of an output artifact?
  → Does it have required sections and optional conditional blocks?
  → Is it filled in by a command/agent, not used independently?
  If yes to all → Template.
```

### Bad Overlap Examples and Refactoring

| Bad Pattern | Problem | Correct Refactoring |
|---|---|---|
| Command doing EDA analysis directly | Duplicates data-profiler agent's logic | Command orchestrates; agent analyzes |
| Agent generating final report file | Agent should return text; command writes the file | Agent returns structured text; command formats with template and writes |
| Skill containing decision logic | "If data is temporal, use ARIMA" is an agent decision | Skill provides ARIMA patterns; agent decides when to use them |
| Template containing methodology | "Step 1: Check for normality" is a skill's job | Template has section headers; skill fills methodology |
| Two skills teaching same library | scikit-learn skill and statistical-analysis skill both teaching scipy.stats | Define bilateral boundaries in both skills' "Role in ds plugin" |

### Current Overlap Assessment

| Component A | Component B | Overlap Risk | Status |
|---|---|---|---|
| statistical-analysis skill | statsmodels skill | Both reference statistical tests | Resolved -- bilateral boundaries defined |
| scikit-learn skill | aeon skill | Both do ML, aeon is sklearn-compatible | Resolved -- bilateral boundaries defined |
| statsmodels skill | aeon skill | Both handle time series | Resolved -- statsmodels = classical inference, aeon = ML |
| matplotlib skill | scikit-learn displays | Both produce plots | Resolved -- matplotlib is foundational, sklearn displays are library-users |
| data-profiler agent | feature-engineer agent | Both analyze data characteristics | Low risk -- profiler describes what IS, engineer recommends what to BUILD |
| experiment-designer agent | model-evaluator agent | Both involved in experiments | Low risk -- designer plans before, evaluator assesses after |
| eda-checklist skill | exploratory-data-analysis skill | Both involved in EDA | Low risk -- checklist = methodology, EDA skill = file type detection + format-specific analysis |

---

## 4. Command Set Analysis

### Current Commands (4) -- Assessment

| Command | Completeness | Notes |
|---------|-------------|-------|
| `/ds:plan` | Strong | Good learnings search, approach selection across paradigms |
| `/ds:eda` | Strong | Excellent routing (tabular vs scientific), deep skill integration |
| `/ds:experiment` | Strong | 6-paradigm routing, comprehensive methodology design |
| `/ds:compound` | Adequate | Deduplication gate works, but only captures post-experiment learnings |

### Missing Commands (from original design)

| Command | Purpose | Priority | Rationale |
|---------|---------|----------|-----------|
| `/ds:review` | Peer review experiments for methodology, leakage, reproducibility | **High** | Closes the Review gap. Catches issues before shipping. |
| `/ds:ship` | Deployment readiness check, model card generation | **Medium** | Closes the Ship gap. Important for production ML but not all DS work goes to production. |

### Proposed v2.0 Command Set (6 commands)

| Command | Purpose | Inputs | Outputs | Agents | Skills |
|---------|---------|--------|---------|--------|--------|
| `/ds:plan` | Frame problem, plan approach | Problem description | `docs/ds/plans/*-plan.md` | problem-framer | scikit-learn, statsmodels, aeon |
| `/ds:eda` | Explore dataset | File path or description | `docs/ds/eda/*-eda.md` | data-profiler, feature-engineer | eda-checklist, target-leakage-detection, exploratory-data-analysis, scikit-learn, statsmodels, matplotlib, aeon |
| `/ds:experiment` | Design and run experiment | Hypothesis or description | `docs/ds/experiments/*-plan.md`, `*-result.md` | experiment-designer, model-evaluator | split-strategy, target-leakage-detection, statistical-analysis, scikit-learn, experiment-tracking, statsmodels, matplotlib, aeon |
| `/ds:review` | Peer review experiment | Experiment report path | `docs/ds/reviews/*-review.md` | model-evaluator, reproducibility-auditor | statistical-analysis, target-leakage-detection |
| `/ds:ship` | Deployment readiness | Model path or experiment report | `docs/ds/deployments/*-readiness.md`, `*-model-card.md` | deployment-readiness | -- |
| `/ds:compound` | Capture learnings | Learning description or report path | `docs/ds/learnings/*-<topic>.md` | documentation-synthesizer | -- |

---

## 5. Agent Design Analysis

### Current Agents (6) -- Assessment

#### Analysis Agents (3)

**problem-framer** (`agents/analysis/problem-framer.md`)
- Role: Structures business questions into ML problems
- Boundaries: Clear -- only invoked by `/ds:plan`
- Assessment: Well-scoped. No overlap.

**data-profiler** (`agents/analysis/data-profiler.md`)
- Role: Deep tabular profiling (structure, quality, distributions, anomalies)
- Boundaries: Tabular data only; `exploratory-data-analysis` skill handles non-tabular
- References: matplotlib for visualization, aeon for temporal feature extraction
- Assessment: Well-scoped. Clear handoff with feature-engineer.

**feature-engineer** (`agents/analysis/feature-engineer.md`)
- Role: Suggests feature transformations based on data characteristics
- Boundaries: Recommends what to build; data-profiler describes what IS
- References: scikit-learn preprocessing, aeon transformations
- Assessment: Well-scoped. Complementary with data-profiler.

#### Modeling Agents (2)

**experiment-designer** (`agents/modeling/experiment-designer.md`)
- Role: Designs experiments with hypotheses, methodology, evaluation plans
- Boundaries: Plans BEFORE execution; model-evaluator assesses AFTER
- Assessment: Well-scoped. Covers all 6 paradigms.

**model-evaluator** (`agents/modeling/model-evaluator.md`)
- Role: Evaluates model performance with slicing, calibration, fairness
- Boundaries: Assesses AFTER execution; references statistical-analysis, aeon metrics
- Assessment: Well-scoped. Would benefit from being wired into a `/ds:review` command.

#### Review Agent (1)

**documentation-synthesizer** (`agents/review/documentation-synthesizer.md`)
- Role: Synthesizes findings into reusable learning documents
- Boundaries: Only invoked by `/ds:compound`
- Assessment: Well-scoped but narrow. Only writes learnings -- could also support review artifacts.

### Missing Agents (from original design)

| Agent | Category | Purpose | Priority |
|-------|----------|---------|----------|
| **reproducibility-auditor** | review | Check experiments for reproducibility (seeds, versions, data hashes) | High -- needed for `/ds:review` |
| **deployment-readiness** | review | Evaluate model for production deployment | Medium -- needed for `/ds:ship` |

### Agent Interaction Map

```
/ds:plan
  └── problem-framer ──→ [text] ──→ command writes plan artifact

/ds:eda
  ├── data-profiler ──→ [profiling text] ──→ command writes EDA report
  └── feature-engineer ──→ [suggestions text] ──→ appended to EDA report

/ds:experiment
  ├── experiment-designer ──→ [experiment plan text] ──→ command writes plan artifact
  └── model-evaluator ──→ [evaluation text] ──→ command writes result artifact

/ds:compound
  └── documentation-synthesizer ──→ [learning text] ──→ command writes learning artifact
```

**Key principle:** Agents return text; commands write files. This prevents agents from overwriting each other's artifacts.

---

## 6. Skills Design Analysis

### Current Skills (11) -- Classification

#### Methodology Skills (encode "how to think")

| Skill | Purpose | Used By |
|-------|---------|---------|
| eda-checklist | Systematic EDA methodology | `/ds:eda` |
| split-strategy | Train/val/test split decision tree | `/ds:experiment` |
| target-leakage-detection | Detect temporal, direct, group leakage | `/ds:eda`, `/ds:experiment` |
| experiment-tracking | Standard experiment logging format | `/ds:experiment` |
| statistical-analysis | Test selection, power analysis, APA reporting | `/ds:experiment` |

#### API Pattern Skills (encode "how to code")

| Skill | Purpose | Used By | Type |
|-------|---------|---------|------|
| scikit-learn | Preprocessing, pipelines, model selection, evaluation | `/ds:plan`, `/ds:eda`, `/ds:experiment` | Foundational |
| statsmodels | OLS, GLM, discrete choice, time series, diagnostics | `/ds:plan`, `/ds:eda`, `/ds:experiment` | Foundational |
| matplotlib | Plot types, styling, multi-panel figures, export | `/ds:eda`, `/ds:experiment` | Foundational |
| aeon | Time series ML -- classification, regression, clustering, anomaly detection, segmentation, similarity | `/ds:plan`, `/ds:eda`, `/ds:experiment` | Domain |

#### Utility Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| setup | Check Python environment for required libraries | Standalone |
| exploratory-data-analysis | File type detection, format-specific EDA for 200+ scientific formats | `/ds:eda` |

### Skill Boundaries Map

```
                    ┌─────────────────────────────────────┐
                    │         Cross-Sectional ML           │
                    │         (scikit-learn)               │
                    │   preprocessing, pipelines,          │
                    │   model selection, evaluation        │
                    └──────────┬──────────────────────────┘
                               │ sklearn-compatible API
                    ┌──────────┴──────────────────────────┐
                    │         Time-Series ML               │
                    │         (aeon)                        │
                    │   classification, regression,         │
                    │   clustering, anomaly detection,      │
                    │   segmentation, similarity            │
                    └─────────────────────────────────────┘

┌──────────────────────┐     ┌──────────────────────────┐
│  Classical Inference  │     │      Visualization        │
│  (statsmodels)        │     │      (matplotlib)          │
│  OLS, GLM, ARIMA,     │     │  plot types, styling,      │
│  p-values, diagnostics │     │  multi-panel, export       │
└──────────────────────┘     └──────────────────────────┘

┌──────────────────────┐     ┌──────────────────────────┐
│  Statistical Methods  │     │  Scientific Formats        │
│ (statistical-analysis)│     │ (exploratory-data-analysis)│
│  test selection,      │     │  file type detection,      │
│  power, assumptions   │     │  format-specific EDA       │
└──────────────────────┘     └──────────────────────────┘
```

### Boundary Clarity Assessment

| Boundary | Skills Involved | Documented? | Risk |
|----------|----------------|-------------|------|
| Tabular ML vs TS-ML | scikit-learn / aeon | Yes -- both have "Role in ds plugin" | Low |
| Classical TS vs ML TS | statsmodels / aeon | Yes -- both have "Role in ds plugin" | Low |
| Statistical tests vs model diagnostics | statistical-analysis / statsmodels | Yes -- bilateral | Low |
| Visualization authority | matplotlib / scikit-learn displays / statsmodels plots | Yes -- foundational skill pattern | Low |
| EDA methodology vs format detection | eda-checklist / exploratory-data-analysis | Implicit | **Medium** -- could benefit from explicit documentation |

### Skills Missing for v2.0

| Skill | Purpose | Needed By | Priority |
|-------|---------|-----------|----------|
| **model-card** | Generate standardized model documentation | `/ds:ship` | Medium |
| **reproducibility-checklist** | Verify reproducibility requirements | `/ds:review` | High |

---

## 7. Templates Design Analysis

### Current Templates (5) -- Assessment

| Template | Created By | Updated By | Key Sections | Assessment |
|----------|-----------|-----------|--------------|-----------|
| problem-framing | `/ds:plan` | Manual | Objective, data, constraints, approach, metrics | Good. Stable. |
| dataset-assessment | `/ds:eda` (implicit) | Manual | Structure, quality, distributions, relationships | Good but underused -- EDA report uses `report_template.md` from EDA skill instead. |
| experiment-plan | `/ds:experiment` | Manual | Hypothesis, methodology, split, metrics, baseline + paradigm-specific fields | Good. Updated for 6 paradigms. |
| experiment-result | `/ds:experiment` | Manual | Environment, metrics, diagnostics, observations + paradigm-specific tables | Good. Updated for 6 paradigms. |
| postmortem | `/ds:compound` (implicit) | Manual | Findings, mechanisms, impact | Underused -- compound command uses frontmatter schema directly. |

### Template Issues

1. **dataset-assessment underuse:** `/ds:eda` writes reports using the `exploratory-data-analysis` skill's `report_template.md`, not `templates/dataset-assessment.md`. This creates confusion about which template is canonical.

   **Recommendation:** Either wire `dataset-assessment.md` into `/ds:eda` or remove it in favor of the EDA skill's template. One canonical source.

2. **postmortem underuse:** `/ds:compound` writes learnings with YAML frontmatter and free-form body. The `postmortem` template exists but isn't explicitly referenced by the command.

   **Recommendation:** Wire `postmortem` template into `/ds:compound` or clarify that it's for manual retrospectives separate from per-learning capture.

### Missing Templates for v2.0

| Template | Created By | Key Sections | Priority |
|----------|-----------|--------------|----------|
| **experiment-review** | `/ds:review` | Methodology check, leakage assessment, reproducibility score, recommendations | High |
| **model-card** | `/ds:ship` | Model details, intended use, metrics, limitations, ethical considerations | Medium |
| **deployment-readiness** | `/ds:ship` | Infrastructure requirements, monitoring plan, rollback strategy, SLA | Medium |

---

## 8. Integration Rules and Contracts

### Artifact Naming Convention (Current -- Working Well)

```
docs/ds/<stage>/YYYY-MM-DD-<name>-<type>.md

Examples:
  docs/ds/plans/2026-02-24-churn-prediction-plan.md
  docs/ds/eda/2026-02-24-customers-eda.md
  docs/ds/experiments/2026-02-24-rolling-features-plan.md
  docs/ds/experiments/2026-02-24-rolling-features-result.md
  docs/ds/learnings/2026-02-24-143022-recency-features.md
```

### Folder Structure (Current)

```
data-science-plugin/                    # Plugin root
├── .claude-plugin/plugin.json          # Plugin metadata (version, description)
├── CLAUDE.md                           # Developer guidance
├── CHANGELOG.md                        # Version history
├── README.md                           # User documentation
├── requirements.txt                    # Python dependencies
├── agents/
│   ├── analysis/                       # Data understanding
│   │   ├── problem-framer.md
│   │   ├── data-profiler.md
│   │   └── feature-engineer.md
│   ├── modeling/                       # Model-focused
│   │   ├── experiment-designer.md
│   │   └── model-evaluator.md
│   └── review/                         # Quality and governance
│       └── documentation-synthesizer.md
├── commands/
│   ├── plan.md
│   ├── eda.md
│   ├── experiment.md
│   └── compound.md
├── skills/
│   ├── aeon/                           # Time series ML patterns
│   │   ├── SKILL.md
│   │   └── references/ (11 files)
│   ├── eda-checklist/SKILL.md
│   ├── experiment-tracking/SKILL.md
│   ├── exploratory-data-analysis/      # Scientific format EDA
│   │   ├── SKILL.md
│   │   ├── assets/report_template.md
│   │   ├── references/ (6 files)
│   │   └── scripts/analyzer.py
│   ├── matplotlib/                     # Visualization patterns
│   │   ├── SKILL.md
│   │   ├── references/ (4 files)
│   │   └── scripts/ (2 files)
│   ├── scikit-learn/                   # ML patterns
│   │   ├── SKILL.md
│   │   ├── references/ (6 files)
│   │   └── scripts/ (2 files)
│   ├── setup/SKILL.md
│   ├── split-strategy/SKILL.md
│   ├── statistical-analysis/           # Statistical methods
│   │   ├── SKILL.md
│   │   ├── references/ (5 files)
│   │   └── scripts/assumption_checks.py
│   ├── statsmodels/                    # Classical inference patterns
│   │   ├── SKILL.md
│   │   └── references/ (5 files)
│   └── target-leakage-detection/SKILL.md
├── templates/
│   ├── problem-framing.md
│   ├── dataset-assessment.md
│   ├── experiment-plan.md
│   ├── experiment-result.md
│   └── postmortem.md
└── docs/
    └── plans/ (8 plan files)
```

### Output Structure (in user's project)

```
docs/ds/                    # Plugin output root (user's project)
├── plans/                  # From /ds:plan
├── eda/                    # From /ds:eda
├── experiments/            # From /ds:experiment
├── reviews/                # From /ds:review (proposed)
├── deployments/            # From /ds:ship (proposed)
└── learnings/              # From /ds:compound
```

### Context Passing Contracts

| From | To | Mechanism | Data Passed |
|------|----|-----------|-------------|
| `/ds:plan` | `/ds:eda` | User references plan in argument | Problem framing, approach selection |
| `/ds:eda` | `/ds:experiment` | User references EDA report in argument | Data characteristics, feature suggestions, quality issues |
| `/ds:experiment` | `/ds:compound` | User references experiment report in argument | What worked, what failed, metrics |
| Any command | Any command | Learnings search at start of every command | Past findings matching current topic |

### Artifact Ownership Rules

| Rule | Rationale |
|------|-----------|
| Only one command writes to each output directory | Prevents artifact collision |
| Agents return text; commands write files | Prevents agents from overwriting each other |
| Templates define structure; skills fill methodology | Prevents duplication |
| Learnings are append-only (new files) or update-with-dedup | Prevents data loss |

---

## 9. Opinionated Defaults for DS Best Practices

### Currently Baked In

| Practice | Where Enforced | Override |
|----------|---------------|----------|
| Baseline-first modeling | experiment-designer agent, experiment command | User can skip baseline |
| Leakage prevention | target-leakage-detection skill invoked in EDA and experiment | User can skip check |
| Reproducibility fields | experiment-tracking skill (env, data hash, git SHA) | User can omit fields |
| Learnings search before work | All 4 commands search learnings at step 1 | N/A (always runs) |
| Large dataset sampling | `/ds:eda` samples at 100K rows when >100MB | User can override threshold |
| 6-paradigm routing | `/ds:experiment` detects experiment type | User can override detection |
| Deduplication gate | `/ds:compound` checks for overlapping learnings | User can force new |
| matplotlib headless safety | matplotlib skill conventions (OO API, savefig+close, no plt.show) | N/A (always applies) |
| Random state convention | aeon and scikit-learn skills set `random_state=42` | User can change seed |

### Defaults Missing (Recommended for v2.0)

| Practice | Proposed Location | Description |
|----------|------------------|-------------|
| Error analysis before optimization | `/ds:experiment` step 7 | After first experiment, require error analysis before trying more models |
| Report generation after every experiment | `/ds:experiment` | Currently optional; should be default |
| Model documentation before deployment | `/ds:ship` | Model card generation as default step |
| Peer review gate | `/ds:review` | Structured review before deployment |
| Metric selection by problem type | experiment-designer agent | Auto-suggest primary metric based on problem type (AUC for imbalanced classification, RMSE for regression, etc.) |

---

## 10. Anti-Patterns and Overlap Risks

### Documented Anti-Patterns (from institutional learnings)

| # | Anti-Pattern | Description | Prevention |
|---|---|---|---|
| 1 | Phantom references | Referencing skills/agents that don't exist | Invocation map audit |
| 2 | Unilateral boundaries | Only one of two overlapping skills documents the boundary | Bilateral boundary rule |
| 3 | Binary routing lock-in | Routing that can't accommodate new paradigms | Design for all paradigms, ship for one |
| 4 | Library-user teaching | Skills that use a library duplicating its teaching | Foundational skill pattern |
| 5 | Mid-path patching | Adding conditionals to existing steps instead of routing at entry | Extend at entry point |
| 6 | Single-command wiring | Wiring a skill to only one command when multiple need it | Cross-command wiring matrix |
| 7 | Template-methodology confusion | Templates containing how-to methodology | Skills encode methodology; templates encode form |

### Current Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| Template underuse | Low | `dataset-assessment` and `postmortem` templates not actively wired | Wire or remove in v2.0 |
| EDA template duality | Medium | Two EDA templates exist (templates/dataset-assessment.md and skills/exploratory-data-analysis/assets/report_template.md) | Consolidate to one canonical source |
| model-evaluator limited invocation | Low | Only invoked by `/ds:experiment`, but would be valuable in `/ds:review` | Wire into `/ds:review` when created |
| No validation gate | Medium | No structured review between experiment and deployment | Add `/ds:review` command |
| Compound only captures post-experiment | Low | `/ds:compound` currently focuses on experiment learnings | Consider broadening to capture EDA and plan learnings too |

---

## 11. Evolution Roadmap

### v2.0 -- Review and Ship (Closes Workflow Gaps)

**Theme:** Complete the `Frame -> Explore -> Experiment -> Review -> Ship -> Compound` workflow.

#### Phase 1: Review Command and Supporting Components

- [x] Create `commands/review.md` -- `/ds:review` command
  - Inputs: path to experiment report
  - Workflow: methodology check, leakage re-assessment, reproducibility audit, recommendation
  - Agents: model-evaluator (existing), reproducibility-auditor (new)
  - Skills: statistical-analysis, target-leakage-detection (existing)
  - Output: `docs/ds/reviews/YYYY-MM-DD-<experiment>-review.md`

- [x] Create `agents/review/reproducibility-auditor.md`
  - Role: Check experiments for reproducibility (seeds, library versions, data hashes, environment capture)
  - Inputs: experiment plan + result artifacts
  - Outputs: reproducibility score, missing reproducibility elements, recommendations
  - Boundaries: Only checks reproducibility; does not evaluate model quality (that's model-evaluator)

- [x] Create `templates/experiment-review.md`
  - Sections: Methodology Assessment, Leakage Re-check, Reproducibility Score, Statistical Validity, Recommendations, Decision (approve/revise/reject)

- [x] Create `skills/reproducibility-checklist/SKILL.md`
  - Checklist: random seeds set, library versions captured, data hash recorded, git SHA recorded, environment frozen, results reproducible on re-run
  - Referenced by: `/ds:review`, reproducibility-auditor agent

#### Phase 2: Ship Command and Supporting Components

- [x] Create `commands/ship.md` -- `/ds:ship` command
  - Inputs: model path or experiment report
  - Workflow: deployment readiness assessment, model card generation, monitoring plan
  - Agents: deployment-readiness (new)
  - Skills: model-card (new)
  - Output: `docs/ds/deployments/YYYY-MM-DD-<model>-readiness.md`, `*-model-card.md`

- [x] Create `agents/review/deployment-readiness.md`
  - Role: Evaluate model for production deployment
  - Checks: inference latency, model size, dependency footprint, monitoring requirements, rollback strategy, fairness/bias assessment, data drift susceptibility
  - Boundaries: Assesses readiness only; does not modify model or code

- [x] Create `templates/model-card.md`
  - Sections: Model Details, Intended Use, Metrics, Limitations, Ethical Considerations, Training Data, Evaluation Data, Quantitative Analysis
  - Based on: HuggingFace Model Card format + NVIDIA Model Card++

- [x] Create `templates/deployment-readiness.md`
  - Sections: Infrastructure Requirements, Monitoring Plan, Rollback Strategy, SLA, Data Pipeline Dependencies

- [x] Create `skills/model-card/SKILL.md`
  - Provides: model card generation patterns, HuggingFace format, required fields checklist
  - Referenced by: `/ds:ship`, deployment-readiness agent

#### Phase 3: Template and Wiring Cleanup

- [x] Resolve EDA template duality -- removed `templates/dataset-assessment.md`; canonical template is `skills/exploratory-data-analysis/assets/report_template.md`
- [x] Wire `postmortem` template into `/ds:compound` -- added optional project-level retrospective step (step 9)
- [x] Wire model-evaluator into `/ds:review` command -- done at step 3 of review command
- [x] Add `/ds:review` and `/ds:ship` to CLAUDE.md invocation map
- [x] Update EDA checklist skill boundary with exploratory-data-analysis skill explicitly -- added "Role in ds plugin" paragraph

#### Metadata Sync (applies to all phases)

For each phase, update:
- [x] `.claude-plugin/plugin.json` -- version bump to 2.0.0, updated component counts
- [x] `README.md` -- component counts, tables, workflow description, new agents/commands/skills/templates
- [x] `CHANGELOG.md` -- v2.0.0 entry
- [x] `CLAUDE.md` -- invocation map with /ds:review and /ds:ship rows, output directories

#### v2.0 Final State

| Component | Count |
|-----------|-------|
| Agents | 8 (+2: reproducibility-auditor, deployment-readiness) |
| Commands | 6 (+2: review, ship) |
| Skills | 13 (+2: reproducibility-checklist, model-card) |
| Templates | 7 (+3: experiment-review, model-card, deployment-readiness; -1: removed dataset-assessment) |

### v3.0 -- Advanced Workflows (Future Considerations)

**Theme:** Cross-project intelligence, team collaboration, advanced automation.

| Feature | Description | Components Needed |
|---------|-------------|-------------------|
| Cross-project learning aggregation | Surface learnings from other projects in the same org | Config file (`.ds-config.yaml`), enhanced learnings search |
| Experiment series tracking | Link related experiments (parent/child, iteration chains) | Enhanced experiment-tracking skill, series frontmatter |
| Auto-suggest next experiment | Based on prior results, suggest what to try next | New agent or enhanced experiment-designer |
| Data version control integration | DVC or similar integration for dataset versioning | New skill |
| Notebook export | Generate Jupyter notebooks from experiment plans | New skill or template |
| CI/CD integration | Trigger model retraining on data changes | New skill |

---

## 12. Example User Flows

### Flow 1: Quick Baseline Classification

```
User: /ds:plan We need to predict customer churn. We have 2 years of usage logs.

→ [/ds:plan searches learnings -- none found]
→ [problem-framer structures: binary classification, AUC metric, 30-day horizon]
→ [scikit-learn skill suggests: LogisticRegression baseline, then GBM]
→ Output: docs/ds/plans/2026-02-24-churn-prediction-plan.md

User: /ds:eda ./data/customers.parquet

→ [/ds:eda searches learnings -- none found]
→ [exploratory-data-analysis detects: Parquet, tabular path]
→ [data-profiler: 50K rows, 42 columns, 3% missing, target imbalance 8:1]
→ [feature-engineer suggests: rolling 7d usage, recency features]
→ [target-leakage-detection: flags "cancellation_date" as direct leakage]
→ Output: docs/ds/eda/2026-02-24-customers-eda.md

User: /ds:experiment Hypothesis: Logistic regression baseline achieves >0.75 AUC

→ [/ds:experiment detects: supervised classification]
→ [experiment-designer: stratified 5-fold CV, AUC primary, F1 secondary]
→ [split-strategy: stratified train/val/test 60/20/20, temporal option noted]
→ [scikit-learn: Pipeline with StandardScaler + LogisticRegression]
→ [statistical-analysis: power analysis, assumption planning]
→ Output: docs/ds/experiments/2026-02-24-churn-baseline-plan.md
→ [User executes, model-evaluator assesses: AUC 0.82, good calibration]
→ Output: docs/ds/experiments/2026-02-24-churn-baseline-result.md

User: /ds:compound Recency features (days since last login) were more predictive than aggregate features

→ [documentation-synthesizer extracts learning]
→ [deduplication gate: no existing matches]
→ Output: docs/ds/learnings/2026-02-24-143022-recency-features.md
→ [Future /ds:plan and /ds:experiment will surface this learning]
```

### Flow 2: Tabular Regression with Inference

```
User: /ds:plan We need to understand what drives house prices. Need interpretable coefficients.

→ [problem-framer: regression with inference requirement]
→ [statsmodels skill suggests: OLS with robust standard errors]
→ Output: docs/ds/plans/2026-02-24-house-prices-plan.md

User: /ds:eda ./data/houses.csv

→ [data-profiler: 20K rows, right-skewed prices, multicollinearity detected]
→ [statsmodels VIF check: square_footage and lot_size VIF > 10]
→ Output: docs/ds/eda/2026-02-24-houses-eda.md

User: /ds:experiment OLS regression with log-transformed price

→ [/ds:experiment detects: supervised regression with inference]
→ [statsmodels: OLS with formula API, HC3 robust standard errors]
→ [statistical-analysis: assumption checks (normality, homoscedasticity)]
→ [matplotlib: residual plots, coefficient forest plot]
→ Output: docs/ds/experiments/2026-02-24-house-prices-ols-result.md
```

### Flow 3: Time Series Classification (Advanced)

```
User: /ds:plan Classify ECG signals into 5 cardiac conditions

→ [problem-framer: time-series classification]
→ [aeon skill: ROCKET for speed, InceptionTime for accuracy, 1-NN Euclidean baseline]
→ Output: docs/ds/plans/2026-02-24-ecg-classification-plan.md

User: /ds:eda ./data/ecg_signals.h5

→ [exploratory-data-analysis: HDF5 detected, scientific format path]
→ [format-specific EDA: signal length, sampling rate, class balance]
→ [aeon: Catch22 feature extraction for interpretable summary]
→ Output: docs/ds/eda/2026-02-24-ecg-signals-eda.md

User: /ds:experiment ROCKET classifier vs 1-NN Euclidean baseline on ECG data

→ [/ds:experiment detects: temporal supervised classification]
→ [aeon: RocketClassifier, data format (500, 1, 1000), stratified split]
→ [baseline: KNeighborsTimeSeriesClassifier(distance="euclidean")]
→ [evaluation: accuracy, F1, comparison with published benchmarks]
→ Output: docs/ds/experiments/2026-02-24-ecg-rocket-result.md

User: /ds:compound ROCKET achieved 97% accuracy in 2 seconds vs 1-NN at 89% in 45 minutes

→ Output: docs/ds/learnings/2026-02-24-163045-rocket-ecg-speed-accuracy.md
```

---

## 13. Component Interaction Matrix

### Commands x Agents

| | problem-framer | data-profiler | feature-engineer | experiment-designer | model-evaluator | documentation-synthesizer | reproducibility-auditor* | deployment-readiness* |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| /ds:plan | X | | | | | | | |
| /ds:eda | | X | X | | | | | |
| /ds:experiment | | | | X | X | | | |
| /ds:review* | | | | | X | | X | |
| /ds:ship* | | | | | | | | X |
| /ds:compound | | | | | | X | | |

*Proposed for v2.0

### Commands x Skills

| | eda-checklist | split-strategy | target-leakage | experiment-tracking | statistical-analysis | scikit-learn | statsmodels | matplotlib | setup | aeon | exploratory-data-analysis | reproducibility-checklist* | model-card* |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| /ds:plan | | | | | | X | X | | | X | | | |
| /ds:eda | X | | X | | | X | X | X | | X | X | | |
| /ds:experiment | | X | X | X | X | X | X | X | | X | | | |
| /ds:review* | | | X | | X | | | | | | | X | |
| /ds:ship* | | | | | | | | | | | | | X |
| /ds:compound | | | | | | | | | | | | | |
| /ds:setup | | | | | | | | | X | | | | |

*Proposed for v2.0

### Commands x Templates

| | problem-framing | dataset-assessment | experiment-plan | experiment-result | postmortem | experiment-review* | model-card* | deployment-readiness* |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| /ds:plan | X | | | | | | | |
| /ds:eda | | ? | | | | | | |
| /ds:experiment | | | X | X | | | | |
| /ds:review* | | | | | | X | | |
| /ds:ship* | | | | | | | X | X |
| /ds:compound | | | | | ? | | | |

`?` = Template exists but is not explicitly wired into the command

---

## Acceptance Criteria

### Architecture Quality

- [ ] Every component has a single clear owner (one command writes to each output directory)
- [ ] Every skill referenced in a command actually exists (no phantom references)
- [ ] Every boundary between overlapping skills is documented bilaterally
- [ ] The invocation map in CLAUDE.md matches actual command implementations
- [ ] Component counts in plugin.json, README.md match actual file counts

### Workflow Completeness

- [ ] All 6 workflow stages (Frame, Explore, Experiment, Review, Ship, Compound) have commands
- [ ] State passes cleanly between stages via artifacts and learnings search
- [ ] Every agent is invoked by at least one command
- [ ] Every skill is referenced by at least one command or agent

### Integration Quality

- [ ] No duplicate templates (EDA template duality resolved)
- [ ] Templates used by commands are explicitly referenced in command workflow
- [ ] Foundational skills (matplotlib, scikit-learn, statsmodels) have convention gravity over library-users
- [ ] Paradigm routing at experiment entry point, not mid-path patching

---

## References

### Internal

- [Original scaffold plan](./2026-02-24-feat-data-science-plugin-scaffold-plan.md)
- [Scikit-learn integration learnings](../solutions/integration-issues/scikit-learn-skill-plugin-wiring.md)
- [Statsmodels integration learnings](../solutions/integration-issues/statsmodels-skill-plugin-wiring.md)
- [Matplotlib integration learnings](../solutions/integration-issues/matplotlib-skill-plugin-wiring.md)
- [CLAUDE.md conventions](../../CLAUDE.md)

### Architecture Principles (Consolidated from Learnings)

1. Agents advise, skills provide code
2. The Invocation Map is a contract
3. Design for all paradigms, ship for one
4. Boundary rules are bilateral
5. Extend routing, don't patch
6. Library users don't teach
7. Convention gravity -- foundational skills are the single source of truth

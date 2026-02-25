# CLAUDE.md

This file provides guidance to Claude Code when working with the Data Science plugin.

## Project Overview

A Claude Code plugin (`ds`) that brings compound engineering practices to data science and ML workflows. The plugin provides agents, commands, skills, and templates that help DS/ML teams work in a structured, compounding way -- where each project leaves behind artifacts that make future projects faster.

**Workflow:** `Frame -> Preprocess -> Explore -> Experiment -> Review -> Ship -> Compound -> Repeat`

**Namespace:** `/ds:` -- commands are invoked as `/ds:plan`, `/ds:eda`, etc.

## Plugin Structure

```
.claude-plugin/plugin.json    # Plugin metadata
agents/
  analysis/                   # Data understanding agents
  modeling/                   # Model-focused agents
  review/                     # Quality and governance agents
commands/                     # Commands (plugin name provides namespace)
skills/<skill-name>/SKILL.md  # One SKILL.md per skill directory
templates/                    # Reusable artifact templates
```

## Versioning & Component Count Sync

When adding or removing agents, commands, skills, or templates, update counts in **three places**:

1. `.claude-plugin/plugin.json` -- `description` field component counts + version bump
2. `README.md` -- component counts in the Components table
3. `CHANGELOG.md` -- entry for the version

**Version bump rules:**
- MAJOR: Breaking changes, reorganization
- MINOR: New agents, commands, or skills
- PATCH: Bug fixes, doc updates, minor improvements

**Verification commands:**
```bash
ls agents/**/*.md | wc -l          # Agent count
ls commands/ds/*.md | wc -l        # Command count
ls -d skills/*/ 2>/dev/null | wc -l  # Skill count
ls templates/*.md | wc -l          # Template count
```

## Invocation Map

Which commands invoke which agents and skills:

| Command | Agents | Skills |
|---------|--------|--------|
| `/ds:plan` | problem-framer | scikit-learn, statsmodels, aeon, pandas-pro |
| `/ds:preprocess` | pipeline-builder | data-preprocessing, scikit-learn, pandas-pro |
| `/ds:eda` | data-profiler, feature-engineer | eda-checklist, target-leakage-detection, exploratory-data-analysis, scikit-learn, statsmodels, matplotlib, aeon, data-preprocessing, pandas-pro |
| `/ds:experiment` | experiment-designer, model-evaluator | split-strategy, target-leakage-detection, statistical-analysis, scikit-learn, experiment-tracking, statsmodels, matplotlib, aeon, shap, data-preprocessing, pandas-pro |
| `/ds:review` | model-evaluator, reproducibility-auditor | statistical-analysis, target-leakage-detection, reproducibility-checklist, shap |
| `/ds:ship` | deployment-readiness | model-card, shap |
| `/ds:compound` | documentation-synthesizer | -- |

## Naming Conventions

- **Plugin name:** `"ds"` in plugin.json (the colon is injected by Claude Code automatically)
- **Commands:** Flat in `commands/<name>.md`. The `name:` frontmatter must NOT contain colons. The plugin name `ds` provides the namespace automatically.
- **Agents:** Category subdirectories `agents/<category>/<name>.md`
- **Skills:** Kebab-case directories `skills/<skill-name>/SKILL.md`
- **Templates:** Flat in `templates/<name>.md`

## Format Requirements

### Agents
- Frontmatter: `name`, `description` (quoted, "what + when to use"), `model: inherit`
- Must include `<examples>` block at end with 2-3 concrete invocation scenarios
- Examples use `<example>`, `<context>`, `<user>`, `<assistant>`, `<commentary>` tags

### Commands
- Frontmatter: `name`, `description`, `argument-hint`, `disable-model-invocation: true`
- Body uses `$ARGUMENTS` placeholder for user input
- All commands must have `disable-model-invocation: true` (they produce file-writing side effects)

### Skills
- Frontmatter: `name` (matches directory name), `description` ("what + when to use")
- Skills with file-writing side effects add `disable-model-invocation: true`

## Output Directories

All plugin output goes to `docs/ds/` in the user's project (not inside the plugin):

```
docs/ds/
  plans/          # From /ds:plan
  preprocessing/  # From /ds:preprocess
  eda/            # From /ds:eda
  experiments/    # From /ds:experiment
  reviews/        # From /ds:review
  deployments/    # From /ds:ship
  learnings/      # From /ds:compound
```

## Compounding Mechanism

Learnings in `docs/ds/learnings/` use YAML frontmatter with:
- `category`: modeling | data | features | evaluation | deployment | infrastructure | process
- `outcome`: success | failure | mixed
- `status`: active | superseded | deprecated
- `findings`: structured array with insight, mechanism, impact
- `lifecycle_stage`: framing | preprocessing | eda | experiment | review | deployment

All commands search learnings before starting work. `/ds:compound` runs a deduplication gate.

## Prerequisites

The plugin requires Python 3.9+ with these libraries: pandas, scikit-learn, scipy, statsmodels, numpy. Install with `uv pip install -r requirements.txt`. Optional libraries (xgboost, lightgbm, shap) are used in generated experiment code only. Run `/ds:setup` to check the environment.

## Conventions

- **ASCII-first**: Use ASCII dashes (`--`) not Unicode em-dashes
- **File references**: Use markdown links `[file.md](./path/file.md)`, not backticks
- **Writing style**: Active voice, imperative form, concrete language

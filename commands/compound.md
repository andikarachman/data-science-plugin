---
name: ds:compound
description: Extract and categorize learnings from completed experiments into docs/ds/learnings/ for future retrieval
argument-hint: "[description of what was learned, or path to experiment report]"
disable-model-invocation: true
---

# Capture Learnings

## Input

<learning_input> $ARGUMENTS </learning_input>

**If the input above is empty, ask the user:** "What learning do you want to capture? Describe what you learned, or provide a path to an experiment report."

## Workflow

### 1. Gather Context

Read recent experiment reports, reviews, validation reports, and any referenced artifacts. Search `docs/ds/experiments/`, `docs/ds/reviews/`, `docs/ds/validations/`, and `docs/ds/preprocessing/` for recent artifacts. If a path was provided, read that file first.

### 2. Extract Learnings

Use the `documentation-synthesizer` agent to identify:
- What worked and why
- What failed and why
- Surprising findings
- Reusable patterns (feature transformations, evaluation recipes, hyperparameter ranges)
- Gotchas and domain-specific caveats

### 3. Categorize

Classify each learning into one of:
- `modeling` -- Model selection, hyperparameters, architecture
- `data` -- Data quality, preprocessing, collection
- `features` -- Feature engineering, selection, transformation
- `evaluation` -- Metrics, validation, error analysis
- `deployment` -- Serving, monitoring, latency
- `infrastructure` -- Pipeline, compute, environment
- `process` -- Workflow, team practices, tooling

### 4. Deduplication Gate

Before writing, search existing `docs/ds/learnings/*.md` for files with overlapping tags. If matches are found:
- Present matches to the user
- Ask: "Update existing learning or create new?"
- If updating, modify the existing file and bump its date

### 5. Validate Frontmatter

Ensure the learning file has valid YAML frontmatter:

```yaml
---
title: "Descriptive title of the learning"
category: modeling          # modeling | data | features | evaluation | deployment | infrastructure | process
tags: [relevant, tags, here]
created: YYYY-MM-DD
project: project-name
outcome: success            # success | failure | mixed
status: active              # active | superseded | deprecated
findings:
  - insight: "Concise description of the finding"
    mechanism: hyperparameter_tuning
    impact: high            # high | medium | low
lifecycle_stage: experiment # framing | preprocessing | validation | eda | experiment | review | deployment
supersedes: ""              # Path to learning this replaces (if any)
related:                    # Bidirectional cross-references
  - path/to/related/artifact.md
---
```

Validate that `category` and `outcome` values match the allowed enums.

### 6. Write Learning

Create the file at `docs/ds/learnings/YYYY-MM-DD-HHMMSS-<topic>.md` with timestamp precision to avoid filename collisions.

Create the directory if needed: `mkdir -p docs/ds/learnings/`

### 7. Cross-Reference

Link to the experiment report, review, or notebook that produced this learning. Add the learning path to the `related:` field of the source artifact if it has frontmatter.

### 8. Verify Retrieval

Search `docs/ds/learnings/` to confirm the new learning would surface for related future queries. Report: "Learning saved. It will surface when future projects search for [tags]."

### 9. Project-Level Retrospective (Optional)

If the user is capturing learnings at the end of an entire project (not just a single experiment), offer to generate a project-level retrospective using `templates/postmortem.md`. This covers timeline, what worked, what didn't, surprises, and recommendations -- a broader document than individual per-learning files.

Ask: "Would you also like to create a project retrospective using the postmortem template?"

If yes, generate `docs/ds/learnings/YYYY-MM-DD-<project>-postmortem.md` using the template.

### 10. Summary

Display what was captured, where it was saved, and which future queries will find it.

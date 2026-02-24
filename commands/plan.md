---
name: plan
description: Frame a data science problem and plan the approach, surfacing relevant past learnings
argument-hint: "[problem description or business question]"
disable-model-invocation: true
---

# Frame Problem and Plan Approach

## Input

<problem_description> $ARGUMENTS </problem_description>

**If the problem description above is empty, ask the user:** "What data science problem would you like to frame? Describe the business question, available data, or objective."

## Workflow

### 1. Search Past Learnings

Search `docs/ds/learnings/*.md` for tags and categories related to the problem description. Rank by:
- Tag overlap count
- Recency (prefer newer learnings)
- Outcome (prefer `success` over `failure`)
- Cap at 5 results

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

If learnings are found, summarize them: "Found N prior learnings related to [topic]..." and include key takeaways.

### 2. Problem Framing

Use the `problem-framer` agent to structure the business question:
- What is being predicted/estimated/classified?
- What actions will be taken based on the output?
- What does success look like (metric + threshold)?
- What data is available?
- What are the known constraints (latency, fairness, interpretability)?

### 3. Approach Selection

Propose 2-3 candidate approaches (e.g., "logistic regression baseline -> gradient boosting -> neural net") with trade-offs for each:
- Complexity vs. performance
- Interpretability vs. accuracy
- Development time vs. model sophistication

### 4. Write Artifact

Generate a problem framing document at `docs/ds/plans/YYYY-MM-DD-<name>-plan.md` using the `templates/problem-framing.md` template.

Create the directory if needed: `mkdir -p docs/ds/plans/`

### 5. Next Steps

Ask the user: "Plan ready. What next?" with options:
- Start EDA (`/ds:eda`)
- Refine plan
- Start experiment (`/ds:experiment`)

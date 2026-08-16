# Tutorial Creation Guidelines

## Standard Workflow

**USE `tutorial_workflow.py` FOR ALL TUTORIALS**

```bash
# Create new tutorial
python3 tutorial_workflow.py --topic "Your Topic" --run

# Improve existing tutorial
python3 tutorial_workflow.py --improve tutorials/FILENAME.md --run
```

## General Rules

### Rule 1: Multiple Tutorials on Similar Topics
- It's okay to have multiple tutorials on similar topics
- Each tutorial should have a distinct focus/perspective
- Document which model/angle each tutorial covers

### Rule 2: Explicit Tutorial Name in File
- Every tutorial MUST start with YAML frontmatter containing the title
- Use this format at the VERY TOP of the file:

```yaml
---
title: "Google Gemma 4 - Your Local AI Friend"
model: gemma4:e2b
version: 1.0
created: 2026-04-21
---
```

### Rule 3: Iterative Improvement
- Each improvement creates a NEW version (increment version number)
- Keep previous versions with version tag in filename: `tutorialname_v1.md`, `tutorialname_v2.md`
- Track what changed in a changelog section

### Rule 4: Tutorials Should Grow
- Each iteration should add MORE content, not less
- Minimum 10% growth per iteration
- Always add new sections, examples, or deeper explanations

## Output Format

```yaml
---
title: "TUTORIAL TITLE HERE"
model: "model_used"
version: 1.0
created: YYYY-MM-DD
---
# Tutorial Title

## What is X and Why Should You Care?
...

## How to Use X
...
```

## Workflow Notes

- Can mix different models for different parts
- Research first, then write
- Always validate output doesn't include prompt reflections

---

## Phase Tutorial Rules

### Rule 5: Human-Friendly Phase Introductions
Each phase MUST start with a human-friendly introduction that:
- Uses real-life analogies (not technical jargon)
- Explains WHY this phase matters
- Is 1-3 paragraphs long
- Compares to real-world business concepts

Example:
```
## Phase X: [Name]

Think of this like [real-world analogy]. Before we can [benefit], we need to [prerequisite]. This phase builds [what gets built].
```

### Rule 6: Step Explanations (1-2 Sentences)
Every step/section within a phase MUST have a 1-2 sentence explanation that:
- Explains what this step does
- Uses non-technical language
- Provides real-life context

Example:
```
### 1. Project Structure

We create the folder organization - like setting up filing cabinets and desks before employees arrive.
```

### Rule 7: File Structure After Each Phase
After each phase's summary, MUST show the file structure to that point:
- Show incremental growth
- Mark NEW additions with comments
- Keep previous phase structures visible

---

## Question: Continue to Phase 6?

Ready to proceed with Phase 6 implementation.

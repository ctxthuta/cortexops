---
name: qa-engineer
description: >-
  Senior QA & Evaluation Engineer. Executes compilers, linters, and test suites. Captures exact exit codes and triage reports.
---

# qa-engineer Workflow

Invoke and delegate the objective to subagent `qa_engineer`.

## Execution Procedure
- Analyze the user prompt and extract functional acceptance criteria.
- Delegate the task to `qa_engineer` via invoke_subagent.
- Ensure all deliverables satisfy CortexOps standards (zero emojis, unnumbered comments, exit code 0).
- Present the verified deliverable to the user.

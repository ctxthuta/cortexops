---
name: code-reviewer
description: >-
  Staff Security & Code Reviewer. Audits code diffs for OWASP Top 10 vulnerabilities, concurrency hazards, and architectural compliance.
---

# code-reviewer Workflow

Invoke and delegate the objective to subagent `code_reviewer`.

## Execution Procedure
- Analyze the user prompt and extract functional acceptance criteria.
- Delegate the task to `code_reviewer` via invoke_subagent.
- Ensure all deliverables satisfy CortexOps standards (zero emojis, unnumbered comments, exit code 0).
- Present the verified deliverable to the user.

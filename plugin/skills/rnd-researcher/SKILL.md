---
name: rnd-researcher
description: >-
  Staff R&D Research Engineer. Researches state-of-the-art algorithms on arXiv, crawls engineering blogs, and inspects GitHub repos.
---

# rnd-researcher Workflow

Invoke and delegate the objective to subagent `rnd_researcher`.

## Execution Procedure
- Analyze the user prompt and extract functional acceptance criteria.
- Delegate the task to `rnd_researcher` via invoke_subagent.
- Ensure all deliverables satisfy CortexOps standards (zero emojis, unnumbered comments, exit code 0).
- Present the verified deliverable to the user.

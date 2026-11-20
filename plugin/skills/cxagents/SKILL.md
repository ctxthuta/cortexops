---
name: cxagents
description: >-
  CortexOps Multi-Agent Swarm Orchestrator. Analyzes the objective, selects all relevant CortexOps specialist agents, and coordinates them concurrently.
---

# cxagents Workflow

Invoke and delegate the objective to subagent `cxagents`.

## Execution Procedure
- Analyze the user prompt and extract functional acceptance criteria.
- Delegate the task to `cxagents` via invoke_subagent.
- Ensure all deliverables satisfy CortexOps standards (zero emojis, unnumbered comments, exit code 0).
- Present the verified deliverable to the user.

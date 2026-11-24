/**
 * Global Agent Monitor - Executive Briefing Generator
 * Produces concise, factual operator summaries directly from projected telemetry.
 */

'use strict';

function generateBriefing(snapshot, options = {}) {
  const filterProject = options.filterProject ? options.filterProject.toLowerCase() : null;

  let convs = snapshot.conversations || [];
  let attention = snapshot.attention || [];

  if (filterProject) {
    convs = convs.filter(c => c.project_ids.some(p => p.toLowerCase().includes(filterProject)));
    attention = attention.filter(a => a.project.toLowerCase().includes(filterProject));
  }

  const activeConvs = convs.filter(c => c.state !== 'completed');
  const runningAgents = (snapshot.agents || []).filter(a => a.state === 'running');
  const reportedUsageConvs = convs.filter(c => c.usage && c.usage.status === 'reported');

  const statements = [];

  // Statement 1: Conversation load
  const convWord = activeConvs.length === 1 ? 'conversation' : 'conversations';
  statements.push(`${activeConvs.length} active ${convWord} across ${new Set(convs.flatMap(c => c.project_ids)).size} projects.`);

  // Statement 2: Bottlenecks / Attention
  if (attention.length === 0) {
    statements.push('Zero items blocked or awaiting approval.');
  } else if (attention.length === 1) {
    const item = attention[0];
    statements.push(`One agent waiting for approval in ${item.project} (${item.agent_id}).`);
  } else {
    statements.push(`${attention.length} agents waiting for intervention.`);
  }

  // Statement 3: Active execution
  if (runningAgents.length > 0) {
    statements.push(`${runningAgents.length} agents actively executing turns or tools.`);
  }

  // Statement 4: Telemetry & token reporting
  if (reportedUsageConvs.length > 0) {
    let totalTok = 0;
    for (const c of reportedUsageConvs) {
      totalTok += ((c.usage.input_tokens || 0) + (c.usage.output_tokens || 0));
    }
    statements.push(`${totalTok.toLocaleString()} tokens reported across ${reportedUsageConvs.length} verified sessions.`);
  } else {
    statements.push('Token telemetry unreported for current active sessions.');
  }

  return {
    timestamp: new Date().toISOString(),
    filter: filterProject || 'All',
    summary: statements.join(' '),
    metrics: {
      active_conversations: activeConvs.length,
      attention_count: attention.length,
      running_agents: runningAgents.length,
      reported_sessions: reportedUsageConvs.length
    }
  };
}

module.exports = {
  generateBriefing
};

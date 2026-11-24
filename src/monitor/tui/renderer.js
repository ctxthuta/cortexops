/**
 * Global Agent Monitor - Terminal UI Renderer & Layout Formatter
 * Supports high-density split view on wide displays and single-pane view at 80x24.
 */

'use strict';

const ANSI = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bgBlue: '\x1b[44m',
  bgDark: '\x1b[40m'
};

function formatDuration(startedAt, endedAt = null) {
  if (!startedAt) return '0s';
  const start = new Date(startedAt).getTime();
  const end = endedAt ? new Date(endedAt).getTime() : Date.now();
  const diffSec = Math.max(0, Math.floor((end - start) / 1000));

  if (diffSec < 60) return `${diffSec}s`;
  const mins = Math.floor(diffSec / 60);
  const secs = diffSec % 60;
  if (mins < 60) return `${mins}m ${secs.toString().padStart(2, '0')}s`;
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  return `${hours}h ${remMins.toString().padStart(2, '0')}m`;
}

function padRight(str, len) {
  const clean = String(str || '').slice(0, len);
  return clean + ' '.repeat(Math.max(0, len - clean.length));
}

class TerminalRenderer {
  constructor(options = {}) {
    this.noColor = Boolean(options.noColor || process.env.NO_COLOR);
    this.noMotion = Boolean(options.noMotion);
  }

  style(text, colorKey) {
    if (this.noColor || !ANSI[colorKey]) return String(text);
    return `${ANSI[colorKey]}${text}${ANSI.reset}`;
  }

  badge(state) {
    switch (state) {
      case 'waiting_input':
        return this.style('! [ATTENTION]', 'yellow');
      case 'running':
        return this.style('* [RUNNING]', 'cyan');
      case 'waiting_agent':
        return this.style('~ [WAITING]', 'blue');
      case 'completed':
        return this.style('v [DONE]', 'green');
      case 'failed':
        return this.style('x [FAILED]', 'red');
      case 'cancelled':
        return this.style('- [CANCEL]', 'dim');
      case 'idle':
      default:
        return this.style('- [IDLE]', 'dim');
    }
  }

  renderHeader(stats, filterProject = null, collectorHealthy = true, width = 80) {
    const lines = [];
    const bar = '='.repeat(width);
    const filterLabel = filterProject ? `Filter: [${filterProject}]` : 'All Projects';
    const healthBadge = collectorHealthy
      ? this.style('HEALTHY (UDS)', 'green')
      : this.style('OFFLINE (SPOOLING)', 'yellow');

    lines.push(bar);
    lines.push(`GLOBAL AGENT MONITOR v1.2.1 | ${filterLabel} | Collector: ${healthBadge}`);
    lines.push(
      `Active: ${stats.active_conversations || 0}  |  ` +
      `Agents: ${stats.running_agents || 0}  |  ` +
      `Attention: ${this.style(String(stats.attention_count || 0), stats.attention_count > 0 ? 'yellow' : 'dim')}  |  ` +
      `Reported Tokens: ${(stats.total_tokens_reported || 0).toLocaleString()}`
    );
    lines.push(bar);
    return lines.join('\n');
  }

  renderTabs(activeView, attentionCount = 0) {
    const tabs = [
      { id: 'overview', label: '[1] OVERVIEW' },
      { id: 'attention', label: `[2] ATTENTION (${attentionCount})` },
      { id: 'conversations', label: '[3] CONVERSATIONS' },
      { id: 'usage', label: '[4] USAGE' },
      { id: 'sources', label: '[5] SOURCES' }
    ];

    return tabs.map(t => {
      if (t.id === activeView) {
        return this.style(`[ ${t.label} ]`, 'bold');
      }
      return this.style(t.label, 'dim');
    }).join('  ');
  }

  renderOverview(snapshot, selectedIndex = 0, width = 120, height = 24) {
    const isWide = width >= 100;
    const lines = [];

    // Attention Section
    if (snapshot.attention.length > 0) {
      lines.push(this.style('--- ATTENTION REQUIRED ---', 'yellow'));
      for (let i = 0; i < snapshot.attention.length; i++) {
        const item = snapshot.attention[i];
        const prefix = (i === selectedIndex) ? '> ' : '  ';
        const dur = formatDuration(item.waiting_since);
        const row = `${prefix}${this.badge(item.state)} ${padRight(item.project, 16)} | ${padRight(item.agent_id, 14)} | ${padRight(item.activity, 30)} | ${dur}`;
        lines.push(i === selectedIndex ? this.style(row, 'bold') : row);
      }
      lines.push('');
    }

    // Active Runs & Conversations Section
    lines.push(this.style('--- ACTIVE AGENT WORK ---', 'cyan'));
    const convs = snapshot.conversations.filter(c => c.state !== 'completed');
    if (convs.length === 0) {
      lines.push('  No active conversations. Workstation is idle.');
    } else {
      for (const conv of convs) {
        const proj = conv.project_ids.join(', ') || 'Unassigned';
        const provBadge = `[${conv.provider}/${conv.surface}]`;
        lines.push(`v ${this.badge(conv.state)} ${padRight(proj, 18)} ${this.style(provBadge, 'dim')}`);

        // Find associated agents
        const agents = snapshot.agents.filter(a => a.conversation_id === conv.conversation_id);
        for (const ag of agents) {
          const dur = formatDuration(ag.started_at, ag.state === 'completed' ? ag.last_active_at : null);
          const toolBadge = ag.current_tool ? `(Tool: ${ag.current_tool})` : '';
          const summary = ag.activity_summary || 'Running turn';
          lines.push(`   * ${this.badge(ag.state)} ${padRight(ag.agent_id, 16)} ${padRight(summary, 28)} ${padRight(toolBadge, 18)} ${dur}`);
        }
      }
    }

    return lines.join('\n');
  }

  renderAttentionView(attentionList, selectedIndex = 0) {
    const lines = [];
    lines.push(this.style('=== ATTENTION REQUIRED (WAITING FOR INPUT OR FAILED) ===', 'yellow'));
    lines.push('');

    if (attentionList.length === 0) {
      lines.push('  No tasks currently blocked or requiring attention.');
      lines.push('  All background agents are operating normally.');
      return lines.join('\n');
    }

    lines.push('  STATUS         PROJECT           AGENT           PENDING ACTION                      WAITING');
    lines.push('  ' + '-'.repeat(74));

    for (let i = 0; i < attentionList.length; i++) {
      const it = attentionList[i];
      const prefix = (i === selectedIndex) ? '> ' : '  ';
      const dur = formatDuration(it.waiting_since);
      const row = `${prefix}${this.badge(it.state)}  ${padRight(it.project, 16)}  ${padRight(it.agent_id, 14)}  ${padRight(it.activity, 34)}  ${dur}`;
      lines.push(i === selectedIndex ? this.style(row, 'bold') : row);
    }

    return lines.join('\n');
  }

  renderUsageView(conversations) {
    const lines = [];
    lines.push(this.style('=== TOKEN ACCOUNTING & USAGE LEDGER ===', 'cyan'));
    lines.push('');
    lines.push('  PROJECT           PROVIDER     INPUT       OUTPUT      CACHED      STATUS');
    lines.push('  ' + '-'.repeat(72));

    let totalIn = 0;
    let totalOut = 0;
    let totalCache = 0;

    for (const c of conversations) {
      const proj = padRight((c.project_ids || []).join(', '), 16);
      const prov = padRight(`${c.provider}/${c.surface}`, 12);
      const u = c.usage || {};
      const status = u.status === 'reported' ? this.style('Verified', 'green') : this.style('Unreported', 'dim');

      if (u.status === 'reported') {
        totalIn += (u.input_tokens || 0);
        totalOut += (u.output_tokens || 0);
        totalCache += (u.cache_read_tokens || 0);
      }

      const inTok = (u.input_tokens || 0).toLocaleString().padStart(10);
      const outTok = (u.output_tokens || 0).toLocaleString().padStart(10);
      const cacheTok = (u.cache_read_tokens || 0).toLocaleString().padStart(10);

      lines.push(`  ${proj}  ${prov} ${inTok}  ${outTok}  ${cacheTok}  ${status}`);
    }

    lines.push('  ' + '-'.repeat(72));
    lines.push(
      `  TOTALS (REPORTED)              ${totalIn.toLocaleString().padStart(10)}  ${totalOut.toLocaleString().padStart(10)}  ${totalCache.toLocaleString().padStart(10)}`
    );

    return lines.join('\n');
  }

  renderSourcesView(sources) {
    const lines = [];
    lines.push(this.style('=== REGISTERED LAUNCH SURFACES & ADAPTER HEALTH ===', 'cyan'));
    lines.push('');
    lines.push('  PROVIDER       SURFACE    SOURCE ID               LAST EVENT            EVENTS  STATUS');
    lines.push('  ' + '-'.repeat(76));

    if (sources.length === 0) {
      lines.push('  No active or historical sources recorded yet.');
      return lines.join('\n');
    }

    for (const s of sources) {
      const prov = padRight(s.provider, 14);
      const surf = padRight(s.surface, 10);
      const srcId = padRight(s.source_id, 22);
      const lastSeen = s.last_seen ? new Date(s.last_seen).toLocaleTimeString() : 'Never';
      const last = padRight(lastSeen, 20);
      const count = String(s.event_count || 0).padStart(6);
      const status = this.style(s.status === 'healthy' ? 'HEALTHY' : 'DEGRADED', s.status === 'healthy' ? 'green' : 'yellow');

      lines.push(`  ${prov} ${surf} ${srcId}  ${last}  ${count}  ${status}`);
    }

    return lines.join('\n');
  }

  renderFooter(width = 80) {
    return this.style(
      '[Enter] Inspect  [A] Attention  [/] Filter  [Space] Pause  [B] Brief  [?] Help  [Q] Exit',
      'dim'
    );
  }
}

module.exports = {
  TerminalRenderer,
  formatDuration,
  padRight,
  ANSI
};

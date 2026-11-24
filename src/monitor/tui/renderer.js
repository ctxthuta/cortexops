/**
 * Global Agent Monitor - Terminal UI Renderer & Layout Formatter
 * Supports high-density split view on wide displays and single-pane view at 80x24.
 * Enforces high-contrast ANSI color mapping for agent roles, providers, and statuses.
 */

'use strict';

let PKG_VERSION = '1.2.2';
try {
  PKG_VERSION = require('../../../package.json').version;
} catch (_) {}

const ANSI = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  italic: '\x1b[3m',
  underline: '\x1b[4m',
  inverse: '\x1b[7m',

  // Standard foregrounds
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',

  // High-intensity (bright) foregrounds
  brightBlack: '\x1b[90m',
  brightRed: '\x1b[91m',
  brightGreen: '\x1b[92m',
  brightYellow: '\x1b[93m',
  brightBlue: '\x1b[94m',
  brightMagenta: '\x1b[95m',
  brightCyan: '\x1b[96m',
  brightWhite: '\x1b[97m',

  // High-contrast background badges
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

const PROVIDER_THEMES = {
  antigravity: { color: 'brightCyan', tag: 'AGY' },
  codex: { color: 'brightGreen', tag: 'CDX' },
  claude_code: { color: 'brightYellow', tag: 'CLD' },
  claude: { color: 'brightYellow', tag: 'CLD' },
  cortexops: { color: 'brightMagenta', tag: 'CXOPS' }
};

const ROLE_THEMES = {
  // Security & Audit -> Bright Red
  code_reviewer: { color: 'brightRed', bold: true },
  appsec_engineer: { color: 'brightRed', bold: true },
  ai_redteam_engineer: { color: 'brightRed', bold: true },
  compliance_engineer: { color: 'brightRed', bold: false },

  // Architecture & R&D -> Bright Cyan
  system_architect: { color: 'brightCyan', bold: true },
  rnd_researcher: { color: 'brightCyan', bold: true },
  agent_architect: { color: 'brightCyan', bold: true },

  // Core Systems, Backend & Protocols -> Bright Blue
  backend_engineer: { color: 'brightBlue', bold: true },
  rust_engineer: { color: 'brightBlue', bold: true },
  software_engineer: { color: 'brightBlue', bold: false },
  network_protocol_engineer: { color: 'brightBlue', bold: true },
  embedded_systems_engineer: { color: 'brightBlue', bold: false },

  // QA, Performance & Resilience -> Bright Green
  qa_engineer: { color: 'brightGreen', bold: true },
  perf_engineer: { color: 'brightGreen', bold: true },
  chaos_engineer: { color: 'brightGreen', bold: false },

  // AI, ML & MLOps -> Bright Magenta
  ai_ml_engineer: { color: 'brightMagenta', bold: true },
  mlops_engineer: { color: 'brightMagenta', bold: true },
  synthetic_data_engineer: { color: 'brightMagenta', bold: false },

  // Data, Storage & Consensus -> Bright Yellow
  data_engineer: { color: 'brightYellow', bold: true },
  database_engineer: { color: 'brightYellow', bold: true },
  consensus_engineer: { color: 'brightYellow', bold: false },

  // Kernel, Accelerated Computing & Crypto -> Cyan / White
  ebpf_engineer: { color: 'cyan', bold: true },
  gpu_kernel_engineer: { color: 'cyan', bold: true },
  cryptography_engineer: { color: 'cyan', bold: false },
  compiler_engineer: { color: 'cyan', bold: false },

  // Frontend, UI/UX, Mobile -> Bright Green
  frontend_engineer: { color: 'brightGreen', bold: false },
  uiux_designer: { color: 'brightYellow', bold: false },
  mobile_engineer: { color: 'brightCyan', bold: false },
  al_developer: { color: 'brightBlue', bold: false },

  // Cloud, Platform, DevOps & FinOps -> Blue / Cyan
  devops_engineer: { color: 'blue', bold: true },
  platform_engineer: { color: 'cyan', bold: true },
  finops_engineer: { color: 'yellow', bold: false },

  // Academic & Search -> Bright White
  academic_researcher: { color: 'brightWhite', bold: true },
  search_retrieval_engineer: { color: 'brightWhite', bold: false },

  // Orchestration & Integration -> Bold Bright Magenta
  cxagents: { color: 'brightMagenta', bold: true },
  systems_integrator: { color: 'brightMagenta', bold: true },
  lead_pm_director: { color: 'brightMagenta', bold: true }
};

const FALLBACK_PALETTE = [
  'brightCyan',
  'brightMagenta',
  'brightYellow',
  'brightGreen',
  'brightBlue',
  'brightRed',
  'brightWhite',
  'cyan'
];

function getAgentTheme(agentId) {
  if (!agentId) return { color: 'white', bold: false };
  const lower = agentId.toLowerCase();
  if (ROLE_THEMES[lower]) return ROLE_THEMES[lower];

  // Deterministic color hash for custom or third-party agent identifiers
  let hash = 0;
  for (let i = 0; i < lower.length; i++) {
    hash = (hash << 5) - hash + lower.charCodeAt(i);
    hash |= 0;
  }
  const color = FALLBACK_PALETTE[Math.abs(hash) % FALLBACK_PALETTE.length];
  return { color, bold: false };
}

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

  formatAgent(agentId, width = 16) {
    const raw = String(agentId || '');
    const padded = padRight(raw, width);
    if (this.noColor) return padded;
    const theme = getAgentTheme(raw);
    const code = ANSI[theme.color] || ANSI.white;
    const boldCode = theme.bold ? ANSI.bold : '';
    return `${boldCode}${code}${padded}${ANSI.reset}`;
  }

  formatProvider(provider, surface, width = 14) {
    const raw = `[${provider || 'unknown'}/${surface || 'cli'}]`;
    const padded = padRight(raw, width);
    if (this.noColor) return padded;
    const theme = PROVIDER_THEMES[(provider || '').toLowerCase()];
    if (theme) {
      const code = ANSI[theme.color] || ANSI.white;
      return `${ANSI.bold}${code}${padded}${ANSI.reset}`;
    }
    return `${ANSI.dim}${padded}${ANSI.reset}`;
  }

  badge(state) {
    if (this.noColor) {
      switch (state) {
        case 'waiting_input': return '! [ATTENTION]';
        case 'running':       return '* [RUNNING]  ';
        case 'waiting_agent': return '~ [WAITING]  ';
        case 'completed':     return 'v [DONE]     ';
        case 'failed':        return 'x [FAILED]   ';
        case 'cancelled':     return '- [CANCEL]   ';
        case 'idle':
        default:              return '- [IDLE]     ';
      }
    }
    switch (state) {
      case 'waiting_input':
        return `${ANSI.bold}${ANSI.brightYellow}! [ATTENTION]${ANSI.reset}`;
      case 'running':
        return `${ANSI.bold}${ANSI.brightCyan}* [RUNNING]  ${ANSI.reset}`;
      case 'waiting_agent':
        return `${ANSI.brightBlue}~ [WAITING]  ${ANSI.reset}`;
      case 'completed':
        return `${ANSI.bold}${ANSI.brightGreen}v [DONE]     ${ANSI.reset}`;
      case 'failed':
        return `${ANSI.bold}${ANSI.brightRed}x [FAILED]   ${ANSI.reset}`;
      case 'cancelled':
        return `${ANSI.dim}- [CANCEL]   ${ANSI.reset}`;
      case 'idle':
      default:
        return `${ANSI.dim}- [IDLE]     ${ANSI.reset}`;
    }
  }

  renderHeader(stats, filterProject = null, collectorHealthy = true, width = 80) {
    const lines = [];
    const bar = '='.repeat(width);
    const filterLabel = filterProject ? `Filter: [${filterProject}]` : 'All Projects';
    const healthBadge = collectorHealthy
      ? this.style('HEALTHY (UDS)', 'brightGreen')
      : this.style('OFFLINE (SPOOLING)', 'brightYellow');

    lines.push(this.style(bar, 'dim'));
    lines.push(
      `${this.style('GLOBAL AGENT MONITOR', 'bold')} ${this.style(`v${PKG_VERSION}`, 'brightMagenta')} | ` +
      `${this.style(filterLabel, 'brightCyan')} | Collector: ${healthBadge}`
    );
    lines.push(
      `Active: ${this.style(String(stats.active_conversations || 0), 'bold')}  |  ` +
      `Agents: ${this.style(String(stats.running_agents || 0), 'brightCyan')}  |  ` +
      `Attention: ${this.style(String(stats.attention_count || 0), stats.attention_count > 0 ? 'brightYellow' : 'dim')}  |  ` +
      `Reported Tokens: ${this.style((stats.total_tokens_reported || 0).toLocaleString(), 'brightGreen')}`
    );
    lines.push(this.style(bar, 'dim'));
    return lines.join('\n');
  }

  renderTabs(activeView, attentionCount = 0) {
    const tabs = [
      { id: 'overview', label: '[1] OVERVIEW' },
      { id: 'attention', label: `[2] ATTENTION (${attentionCount})`, alert: attentionCount > 0 },
      { id: 'conversations', label: '[3] CONVERSATIONS' },
      { id: 'usage', label: '[4] USAGE' },
      { id: 'sources', label: '[5] SOURCES' }
    ];

    return tabs.map(t => {
      if (t.id === activeView) {
        return this.style(`[ ${t.label} ]`, 'bold') + (t.alert ? ` ${this.style('!', 'brightYellow')}` : '');
      }
      if (t.alert) {
        return this.style(t.label, 'brightYellow');
      }
      return this.style(t.label, 'dim');
    }).join('  ');
  }

  renderOverview(snapshot, selectedIndex = 0, width = 120, height = 24) {
    const lines = [];

    // Attention Section
    if (snapshot.attention.length > 0) {
      lines.push(this.style('--- ATTENTION REQUIRED ---', 'brightYellow'));
      for (let i = 0; i < snapshot.attention.length; i++) {
        const item = snapshot.attention[i];
        const prefix = (i === selectedIndex) ? '> ' : '  ';
        const dur = padRight(formatDuration(item.waiting_since), 8);
        const projStyled = this.style(padRight(item.project, 16), 'bold');
        const agentStyled = this.formatAgent(item.agent_id, 18);
        const actStyled = padRight(item.activity, 32);
        const row = `${prefix}${this.badge(item.state)} ${projStyled} | ${agentStyled} | ${actStyled} | ${dur}`;
        lines.push(i === selectedIndex ? this.style(row, 'bold') : row);
      }
      lines.push('');
    }

    // Active Runs & Conversations Section
    lines.push(this.style('--- ACTIVE AGENT WORK ---', 'brightCyan'));
    const convs = snapshot.conversations.filter(c => c.state !== 'completed');
    if (convs.length === 0) {
      lines.push(this.style('  No active conversations. Workstation is idle.', 'dim'));
    } else {
      for (const conv of convs) {
        const proj = (conv.project_ids && conv.project_ids.length > 0) ? conv.project_ids.join(', ') : 'Unassigned';
        const projStyled = this.style(padRight(proj, 18), 'bold');
        const provBadge = this.formatProvider(conv.provider, conv.surface, 16);
        lines.push(`v ${this.badge(conv.state)} ${projStyled} ${provBadge}`);

        // Find associated agents
        const agents = snapshot.agents.filter(a => a.conversation_id === conv.conversation_id);
        for (const ag of agents) {
          const dur = padRight(formatDuration(ag.started_at, ag.state === 'completed' ? ag.last_active_at : null), 8);
          const rawTool = ag.current_tool ? `(Tool: ${ag.current_tool})` : '';
          const toolStyled = rawTool ? this.style(padRight(rawTool, 22), 'brightYellow') : ' '.repeat(22);
          const summary = padRight(ag.activity_summary || 'Running turn', 30);
          const agentStyled = this.formatAgent(ag.agent_id, 18);
          lines.push(`   * ${this.badge(ag.state)} ${agentStyled} ${summary} ${toolStyled} ${this.style(dur, 'dim')}`);
        }
      }
    }

    return lines.join('\n');
  }

  renderAttentionView(attentionList, selectedIndex = 0) {
    const lines = [];
    lines.push(this.style('=== ATTENTION REQUIRED (WAITING FOR INPUT OR FAILED) ===', 'brightYellow'));
    lines.push('');

    if (attentionList.length === 0) {
      lines.push(this.style('  No tasks currently blocked or requiring attention.', 'dim'));
      lines.push(this.style('  All background agents are operating normally.', 'dim'));
      return lines.join('\n');
    }

    lines.push(this.style('  STATUS         PROJECT           AGENT               PENDING ACTION                    WAITING', 'dim'));
    lines.push(this.style('  ' + '-'.repeat(84), 'dim'));

    for (let i = 0; i < attentionList.length; i++) {
      const it = attentionList[i];
      const prefix = (i === selectedIndex) ? '> ' : '  ';
      const dur = padRight(formatDuration(it.waiting_since), 8);
      const projStyled = this.style(padRight(it.project, 16), 'bold');
      const agentStyled = this.formatAgent(it.agent_id, 18);
      const actStyled = padRight(it.activity, 34);
      const row = `${prefix}${this.badge(it.state)}  ${projStyled}  ${agentStyled}  ${actStyled}  ${this.style(dur, 'brightYellow')}`;
      lines.push(i === selectedIndex ? this.style(row, 'bold') : row);
    }

    return lines.join('\n');
  }

  renderUsageView(conversations) {
    const lines = [];
    lines.push(this.style('=== TOKEN ACCOUNTING & USAGE LEDGER ===', 'brightCyan'));
    lines.push('');
    lines.push(this.style('  PROJECT           PROVIDER        INPUT       OUTPUT      CACHED      STATUS', 'dim'));
    lines.push(this.style('  ' + '-'.repeat(74), 'dim'));

    let totalIn = 0;
    let totalOut = 0;
    let totalCache = 0;

    for (const c of conversations) {
      const proj = padRight((c.project_ids || []).join(', ') || 'Unassigned', 16);
      const prov = this.formatProvider(c.provider, c.surface, 14);
      const u = c.usage || {};
      const status = u.status === 'reported' ? this.style('Verified', 'brightGreen') : this.style('Unreported', 'dim');

      if (u.status === 'reported') {
        totalIn += (u.input_tokens || 0);
        totalOut += (u.output_tokens || 0);
        totalCache += (u.cache_read_tokens || 0);
      }

      const inTok = (u.input_tokens || 0).toLocaleString().padStart(10);
      const outTok = (u.output_tokens || 0).toLocaleString().padStart(10);
      const cacheTok = (u.cache_read_tokens || 0).toLocaleString().padStart(10);

      lines.push(`  ${this.style(proj, 'bold')}  ${prov} ${this.style(inTok, 'brightCyan')}  ${this.style(outTok, 'brightBlue')}  ${this.style(cacheTok, 'dim')}  ${status}`);
    }

    lines.push(this.style('  ' + '-'.repeat(74), 'dim'));
    lines.push(
      `  ${this.style('TOTALS (REPORTED)', 'bold')}                ${this.style(totalIn.toLocaleString().padStart(10), 'brightCyan')}  ${this.style(totalOut.toLocaleString().padStart(10), 'brightBlue')}  ${this.style(totalCache.toLocaleString().padStart(10), 'dim')}`
    );

    return lines.join('\n');
  }

  renderSourcesView(sources) {
    const lines = [];
    lines.push(this.style('=== REGISTERED LAUNCH SURFACES & ADAPTER HEALTH ===', 'brightCyan'));
    lines.push('');
    lines.push(this.style('  PROVIDER       SURFACE    SOURCE ID               LAST EVENT            EVENTS  STATUS', 'dim'));
    lines.push(this.style('  ' + '-'.repeat(78), 'dim'));

    if (sources.length === 0) {
      lines.push(this.style('  No active or historical sources recorded yet.', 'dim'));
      return lines.join('\n');
    }

    for (const s of sources) {
      const prov = this.formatProvider(s.provider, s.surface, 14);
      const surf = padRight(s.surface, 10);
      const srcId = this.style(padRight(s.source_id, 22), 'dim');
      const lastSeen = s.last_seen ? new Date(s.last_seen).toLocaleTimeString() : 'Never';
      const last = padRight(lastSeen, 20);
      const count = this.style(String(s.event_count || 0).padStart(6), 'brightCyan');
      const status = s.status === 'healthy'
        ? this.style('HEALTHY', 'brightGreen')
        : this.style('DEGRADED', 'brightYellow');

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
  ANSI,
  ROLE_THEMES,
  PROVIDER_THEMES,
  getAgentTheme
};

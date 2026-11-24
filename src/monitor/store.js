/**
 * Global Agent Monitor - High-Performance WAL Storage & Projection Engine
 * Manages atomic append-only journaling, out-of-order DAG resolution, and scoped token ledgers.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { validateEvent } = require('./schema');

const DEDUP_CAPACITY = 10000;
const DEFAULT_RETENTION_DAYS = 7;

class MonitorStore {
  constructor(options = {}) {
    this.baseDir = options.baseDir || path.join(os.homedir(), '.agentmon');
    this.eventsFile = path.join(this.baseDir, 'events.jsonl');
    this.snapshotFile = path.join(this.baseDir, 'snapshot.json');
    this.retentionDays = options.retentionDays || DEFAULT_RETENTION_DAYS;

    // Deduplication sliding hash set
    this.seenEventIds = new Set();
    this.eventOrder = [];

    // Core In-Memory State Projections
    this.conversations = new Map();
    this.runs = new Map();
    this.agents = new Map();
    this.orphanBuffer = new Map(); // parent_id -> Array<ChildEvent>
    this.sources = new Map(); // source_id -> { provider, surface, last_seen, event_count, status }
    this.globalSeq = 0;

    this.ensureDirectory();
  }

  ensureDirectory() {
    if (!fs.existsSync(this.baseDir)) {
      fs.mkdirSync(this.baseDir, { recursive: true, mode: 0o700 });
    }
  }

  /**
   * Appends an event to the Write-Ahead Log atomically.
   */
  writeToJournal(event) {
    const line = JSON.stringify(event) + '\n';
    fs.appendFileSync(this.eventsFile, line, { mode: 0o600, encoding: 'utf-8' });
  }

  /**
   * Ingests, validates, deduplicates, and projects an event.
   * Returns null if the event was a duplicate, or the projected record otherwise.
   */
  ingest(rawEvent) {
    const event = validateEvent(rawEvent);

    // 1. Sliding Window Deduplication
    if (this.seenEventIds.has(event.event_id)) {
      return null;
    }
    this.seenEventIds.add(event.event_id);
    this.eventOrder.push(event.event_id);
    if (this.eventOrder.length > DEDUP_CAPACITY) {
      const evicted = this.eventOrder.shift();
      this.seenEventIds.delete(evicted);
    }

    this.globalSeq += 1;
    event.global_seq = this.globalSeq;

    // 2. Persist to WAL
    this.writeToJournal(event);

    // 3. Update In-Memory Projections
    this.applyEvent(event);

    return event;
  }

  /**
   * Updates state projections from a validated event.
   */
  applyEvent(event) {
    this.updateSource(event);
    this.updateConversation(event);
    this.updateRun(event);
    this.updateAgent(event);
    this.resolveOrphans(event);
  }

  updateSource(event) {
    const key = `${event.provider}:${event.surface}:${event.source_id}`;
    let src = this.sources.get(key);
    if (!src) {
      src = {
        key,
        provider: event.provider,
        surface: event.surface,
        source_id: event.source_id,
        first_seen: event.occurred_at,
        last_seen: event.occurred_at,
        event_count: 0,
        status: 'healthy'
      };
      this.sources.set(key, src);
    }
    src.last_seen = event.occurred_at;
    src.event_count += 1;
  }

  updateConversation(event) {
    let conv = this.conversations.get(event.conversation_id);
    if (!conv) {
      conv = {
        conversation_id: event.conversation_id,
        provider: event.provider,
        surface: event.surface,
        environment_id: event.environment_id,
        profile_id: event.profile_id,
        project_ids: [...event.project_ids],
        state: event.state,
        started_at: event.occurred_at,
        last_observed_at: event.occurred_at,
        active_runs: new Set(),
        active_agents: new Set(),
        usage: {
          input_tokens: 0,
          output_tokens: 0,
          cache_read_tokens: 0,
          cache_write_tokens: 0,
          reasoning_tokens: 0,
          status: 'unreported'
        }
      };
      this.conversations.set(event.conversation_id, conv);
    }

    conv.last_observed_at = event.occurred_at;
    conv.state = event.state;

    // Merge project identifiers without duplication
    for (const p of event.project_ids) {
      if (!conv.project_ids.includes(p)) {
        conv.project_ids.push(p);
      }
    }

    conv.active_runs.add(event.run_id);
    conv.active_agents.add(event.agent_id);

    // Apply token accounting
    if (event.usage) {
      this.applyUsage(conv.usage, event.usage);
    }
  }

  updateRun(event) {
    let run = this.runs.get(event.run_id);
    if (!run) {
      run = {
        run_id: event.run_id,
        conversation_id: event.conversation_id,
        root_agent_id: event.parent_id ? null : event.agent_id,
        state: event.state,
        started_at: event.occurred_at,
        completed_at: null,
        agents: new Set(),
        events: []
      };
      this.runs.set(event.run_id, run);
    }

    run.state = event.state;
    run.agents.add(event.agent_id);
    run.events.push(event);

    if (['completed', 'failed', 'cancelled'].includes(event.state)) {
      run.completed_at = event.occurred_at;
    }
  }

  updateAgent(event) {
    const key = `${event.run_id}:${event.agent_id}`;
    let ag = this.agents.get(key);
    if (!ag) {
      ag = {
        key,
        agent_id: event.agent_id,
        run_id: event.run_id,
        conversation_id: event.conversation_id,
        parent_id: event.parent_id,
        children: new Set(),
        state: event.state,
        current_tool: event.tool_name,
        active_skill: event.skill_id,
        activity_summary: event.activity_summary,
        started_at: event.occurred_at,
        last_active_at: event.occurred_at,
        timeline: [],
        usage: {
          input_tokens: 0,
          output_tokens: 0,
          cache_read_tokens: 0,
          cache_write_tokens: 0,
          reasoning_tokens: 0,
          status: 'unreported'
        }
      };
      this.agents.set(key, ag);
    }

    ag.state = event.state;
    ag.last_active_at = event.occurred_at;
    if (event.tool_name) ag.current_tool = event.tool_name;
    if (event.skill_id) ag.active_skill = event.skill_id;
    if (event.activity_summary) ag.activity_summary = event.activity_summary;

    ag.timeline.push({
      event_type: event.event_type,
      occurred_at: event.occurred_at,
      activity: event.activity_summary,
      tool: event.tool_name,
      skill: event.skill_id
    });

    if (event.usage) {
      this.applyUsage(ag.usage, event.usage);
    }

    // Link parent-child if parent exists; buffer orphan otherwise
    if (event.parent_id) {
      const parentKey = `${event.run_id}:${event.parent_id}`;
      const parentAg = this.agents.get(parentKey);
      if (parentAg) {
        parentAg.children.add(event.agent_id);
      } else {
        if (!this.orphanBuffer.has(event.parent_id)) {
          this.orphanBuffer.set(event.parent_id, []);
        }
        this.orphanBuffer.get(event.parent_id).push(key);
      }
    }
  }

  resolveOrphans(event) {
    const matchingOrphans = this.orphanBuffer.get(event.agent_id);
    if (matchingOrphans && matchingOrphans.length > 0) {
      const parentKey = `${event.run_id}:${event.agent_id}`;
      const parentAg = this.agents.get(parentKey);
      if (parentAg) {
        for (const childKey of matchingOrphans) {
          const childAg = this.agents.get(childKey);
          if (childAg) {
            parentAg.children.add(childAg.agent_id);
          }
        }
        this.orphanBuffer.delete(event.agent_id);
      }
    }
  }

  applyUsage(target, sample) {
    target.status = 'reported';
    const isSnapshot = sample.measurement_type === 'snapshot' || sample.measurement_type === 'aggregate';

    const updateField = (key) => {
      const val = sample[key];
      if (val === null || val === undefined) return;
      if (isSnapshot) {
        target[key] = Math.max(target[key] || 0, val);
      } else {
        target[key] = (target[key] || 0) + val;
      }
    };

    updateField('input_tokens');
    updateField('output_tokens');
    updateField('cache_read_tokens');
    updateField('cache_write_tokens');
    updateField('reasoning_tokens');
  }

  /**
   * Retrieves high-priority runs needing user attention (waiting_input or failed).
   */
  getAttentionList() {
    const list = [];
    for (const ag of this.agents.values()) {
      if (ag.state === 'waiting_input' || ag.state === 'failed') {
        const conv = this.conversations.get(ag.conversation_id);
        list.push({
          agent_id: ag.agent_id,
          run_id: ag.run_id,
          conversation_id: ag.conversation_id,
          project: conv ? conv.project_ids.join(', ') : 'Unassigned',
          provider: conv ? conv.provider : 'unknown',
          surface: conv ? conv.surface : 'unknown',
          state: ag.state,
          activity: ag.activity_summary,
          waiting_since: ag.last_active_at
        });
      }
    }
    return list;
  }

  /**
   * Compiles complete in-memory snapshot for new subscribers and CLI inspection.
   */
  getSnapshot() {
    const conversations = Array.from(this.conversations.values()).map(c => ({
      ...c,
      active_runs: Array.from(c.active_runs),
      active_agents: Array.from(c.active_agents)
    }));

    const agents = Array.from(this.agents.values()).map(a => ({
      ...a,
      children: Array.from(a.children)
    }));

    const sources = Array.from(this.sources.values());
    const attention = this.getAttentionList();

    let totalTokens = 0;
    for (const c of conversations) {
      if (c.usage.status === 'reported') {
        totalTokens += (c.usage.input_tokens + c.usage.output_tokens);
      }
    }

    return {
      version: 1,
      global_seq: this.globalSeq,
      collected_at: new Date().toISOString(),
      stats: {
        active_conversations: conversations.filter(c => c.state !== 'completed').length,
        total_conversations: conversations.length,
        running_agents: agents.filter(a => a.state === 'running').length,
        attention_count: attention.length,
        total_tokens_reported: totalTokens,
        source_count: sources.length
      },
      attention,
      conversations,
      agents,
      sources
    };
  }

  /**
   * Purges all events and derived state for a designated project.
   */
  purgeProject(projectName) {
    if (!projectName || typeof projectName !== 'string') return 0;
    const target = projectName.trim().toLowerCase();

    // Identify matching conversations
    const matchedConvIds = new Set();
    for (const [id, conv] of this.conversations.entries()) {
      if (conv.project_ids.some(p => p.toLowerCase() === target)) {
        matchedConvIds.add(id);
      }
    }

    if (matchedConvIds.size === 0) return 0;

    // Clear from in-memory projections
    for (const id of matchedConvIds) {
      this.conversations.delete(id);
    }
    for (const [key, ag] of Array.from(this.agents.entries())) {
      if (matchedConvIds.has(ag.conversation_id)) {
        this.agents.delete(key);
      }
    }
    for (const [id, run] of Array.from(this.runs.entries())) {
      if (matchedConvIds.has(run.conversation_id)) {
        this.runs.delete(id);
      }
    }

    // Rewrite WAL file atomically omitting purged records
    let retainedCount = 0;
    if (fs.existsSync(this.eventsFile)) {
      const tmpFile = `${this.eventsFile}.tmp.${Date.now()}`;
      const content = fs.readFileSync(this.eventsFile, 'utf-8');
      const lines = content.split('\n');
      const outLines = [];

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const ev = JSON.parse(line);
          const hasProject = Array.isArray(ev.project_ids) && ev.project_ids.some(p => p.toLowerCase() === target);
          if (!hasProject && !matchedConvIds.has(ev.conversation_id)) {
            outLines.push(line);
            retainedCount += 1;
          }
        } catch (_) {}
      }

      fs.writeFileSync(tmpFile, outLines.join('\n') + (outLines.length ? '\n' : ''), { mode: 0o600 });
      fs.renameSync(tmpFile, this.eventsFile);
    }

    return matchedConvIds.size;
  }

  /**
   * Replays WAL events into memory on startup.
   */
  restore() {
    if (!fs.existsSync(this.eventsFile)) return 0;

    const content = fs.readFileSync(this.eventsFile, 'utf-8');
    const lines = content.split('\n');
    let restored = 0;

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const raw = JSON.parse(line);
        const event = validateEvent(raw);
        this.globalSeq += 1;
        event.global_seq = this.globalSeq;
        this.applyEvent(event);
        if (!this.seenEventIds.has(event.event_id)) {
          this.seenEventIds.add(event.event_id);
          this.eventOrder.push(event.event_id);
          if (this.eventOrder.length > DEDUP_CAPACITY) {
            const evicted = this.eventOrder.shift();
            this.seenEventIds.delete(evicted);
          }
        }
        restored += 1;
      } catch (_) {}
    }

    return restored;
  }
}

module.exports = {
  MonitorStore,
  DEFAULT_RETENTION_DAYS
};

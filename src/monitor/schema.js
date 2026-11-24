/**
 * Global Agent Monitor - Canonical Event Schema & Validation Pipeline
 * Strictly enforces field allowlists, type boundaries, and ANSI neutralization.
 */

'use strict';

const ALLOWED_PROVIDERS = new Set(['antigravity', 'codex', 'claude', 'cortexops', 'unknown']);
const ALLOWED_SURFACES = new Set(['app', 'cli', 'vscode', 'headless', 'unknown']);
const ALLOWED_EVENT_TYPES = new Set([
  'session_start',
  'turn_start',
  'tool_start',
  'tool_finish',
  'delegate',
  'handoff',
  'wait_input',
  'wait_agent',
  'resume',
  'turn_finish',
  'session_end',
  'usage_report',
  'heartbeat',
  'error'
]);

const ALLOWED_STATES = new Set([
  'queued',
  'running',
  'waiting_input',
  'waiting_agent',
  'idle',
  'completed',
  'failed',
  'cancelled',
  'stale'
]);

const ALLOWED_SCOPES = new Set(['agent', 'turn', 'conversation', 'model']);
const ALLOWED_MEASUREMENTS = new Set(['delta', 'snapshot', 'aggregate']);
const ALLOWED_EVIDENCE = new Set(['provider_reported', 'framework_reported', 'inferred']);

// Comprehensive ANSI escape sequence stripper covering CSI, OSC, DCS, APC, and PM sequences.
const ANSI_PATTERN = /(?:\x1b|\u009b)(?:\][^\x07\x1b]*?(?:\x07|\x1b\\)|\[[0-?]*[ -/]*[@-~]|[P^_][^\x07\x1b]*?(?:\x07|\x1b\\)|[@-Z\\-_])/g;
const CONTROL_CHAR_PATTERN = /[\x00-\x1f\x7f]/g;

function sanitizeString(str, maxLen = 256) {
  if (typeof str !== 'string') return '';
  return str
    .replace(ANSI_PATTERN, '')
    .replace(CONTROL_CHAR_PATTERN, ' ')
    .replace(/\s+/g, ' ')
    .slice(0, maxLen)
    .trim();
}

/**
 * Validates and sanitizes an incoming raw event against the canonical envelope.
 * Discards unallowlisted fields such as prompts, message bodies, and raw tool arguments.
 */
function validateEvent(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('Event payload must be a non-null object');
  }

  const schemaVersion = Number(raw.schema_version) || 1;
  const eventId = sanitizeString(raw.event_id, 64);
  const sourceId = sanitizeString(raw.source_id, 64);

  if (!eventId) throw new Error('Missing or empty event_id');
  if (!sourceId) throw new Error('Missing or empty source_id');

  const occurredAt = raw.occurred_at && !isNaN(Date.parse(raw.occurred_at))
    ? new Date(raw.occurred_at).toISOString()
    : new Date().toISOString();

  const provider = ALLOWED_PROVIDERS.has(raw.provider) ? raw.provider : 'unknown';
  const surface = ALLOWED_SURFACES.has(raw.surface) ? raw.surface : 'unknown';
  const environmentId = sanitizeString(raw.environment_id, 64) || 'local';
  const profileId = sanitizeString(raw.profile_id, 64) || 'default';

  const conversationId = sanitizeString(raw.conversation_id, 128);
  const runId = sanitizeString(raw.run_id, 128);
  const agentId = sanitizeString(raw.agent_id, 128);

  if (!conversationId) throw new Error('Missing or empty conversation_id');
  if (!runId) throw new Error('Missing or empty run_id');
  if (!agentId) throw new Error('Missing or empty agent_id');

  const parentId = raw.parent_id ? sanitizeString(raw.parent_id, 128) : null;
  const skillId = raw.skill_id ? sanitizeString(raw.skill_id, 128) : null;
  const toolName = raw.tool_name ? sanitizeString(raw.tool_name, 128) : null;
  const targetAgentId = raw.target_agent_id ? sanitizeString(raw.target_agent_id, 128) : null;

  let projectIds = [];
  if (Array.isArray(raw.project_ids)) {
    projectIds = raw.project_ids
      .map(p => sanitizeString(p, 128))
      .filter(Boolean);
  }
  if (projectIds.length === 0) {
    projectIds = ['Unassigned'];
  }

  const eventType = ALLOWED_EVENT_TYPES.has(raw.event_type) ? raw.event_type : 'turn_start';
  const state = ALLOWED_STATES.has(raw.state) ? raw.state : 'running';
  const activitySummary = sanitizeString(raw.activity_summary, 256) || `${eventType}: ${agentId}`;
  const evidence = ALLOWED_EVIDENCE.has(raw.evidence) ? raw.evidence : 'provider_reported';

  let usage = null;
  if (raw.usage && typeof raw.usage === 'object') {
    const parseTokenCount = (val) => {
      if (val === null || val === undefined) return null;
      const num = parseInt(val, 10);
      return Number.isFinite(num) && num >= 0 ? num : null;
    };

    usage = {
      input_tokens: parseTokenCount(raw.usage.input_tokens),
      output_tokens: parseTokenCount(raw.usage.output_tokens),
      cache_read_tokens: parseTokenCount(raw.usage.cache_read_tokens),
      cache_write_tokens: parseTokenCount(raw.usage.cache_write_tokens),
      reasoning_tokens: parseTokenCount(raw.usage.reasoning_tokens),
      scope: ALLOWED_SCOPES.has(raw.usage.scope) ? raw.usage.scope : 'turn',
      measurement_type: ALLOWED_MEASUREMENTS.has(raw.usage.measurement_type) ? raw.usage.measurement_type : 'snapshot'
    };
  }

  const sourceSeq = Number.isInteger(raw.source_seq) ? raw.source_seq : null;

  return {
    schema_version: schemaVersion,
    event_id: eventId,
    source_id: sourceId,
    occurred_at: occurredAt,
    observed_at: new Date().toISOString(),
    source_seq: sourceSeq,
    provider,
    surface,
    environment_id: environmentId,
    profile_id: profileId,
    conversation_id: conversationId,
    run_id: runId,
    agent_id: agentId,
    parent_id: parentId,
    project_ids: projectIds,
    skill_id: skillId,
    tool_name: toolName,
    target_agent_id: targetAgentId,
    event_type: eventType,
    state,
    activity_summary: activitySummary,
    usage,
    evidence
  };
}

module.exports = {
  validateEvent,
  sanitizeString,
  ALLOWED_PROVIDERS,
  ALLOWED_SURFACES,
  ALLOWED_EVENT_TYPES,
  ALLOWED_STATES,
  ALLOWED_SCOPES,
  ALLOWED_MEASUREMENTS,
  ALLOWED_EVIDENCE
};

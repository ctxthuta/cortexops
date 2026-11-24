/**
 * Global Agent Monitor - CortexOps Framework Integration Bridge
 * Dispatches high-fidelity lifecycle events from orchestrators and subagents.
 */

'use strict';

const crypto = require('crypto');
const { emitEvent } = require('./client');

class FrameworkMonitorBridge {
  constructor(options = {}) {
    this.environmentId = options.environmentId || 'local-workstation';
    this.profileId = options.profileId || 'cortexops-default';
    this.defaultProject = options.defaultProject || 'cortexops';
  }

  createBaseEvent(eventType, state, data) {
    const eventId = data.event_id || `ev_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    return {
      schema_version: 1,
      event_id: eventId,
      source_id: 'cortexops-framework',
      occurred_at: new Date().toISOString(),
      provider: 'cortexops',
      surface: 'cli',
      environment_id: this.environmentId,
      profile_id: this.profileId,
      conversation_id: data.conversation_id || 'conv_default',
      run_id: data.run_id || 'run_default',
      agent_id: data.agent_id || 'cxagents',
      parent_id: data.parent_id || null,
      project_ids: data.project_ids || [this.defaultProject],
      skill_id: data.skill_id || null,
      tool_name: data.tool_name || null,
      target_agent_id: data.target_agent_id || null,
      event_type: eventType,
      state: state,
      activity_summary: data.activity_summary || `${eventType} on ${data.agent_id || 'cxagents'}`,
      usage: data.usage || null,
      evidence: 'framework_reported'
    };
  }

  async trackSessionStart(data) {
    const ev = this.createBaseEvent('session_start', 'running', {
      activity_summary: `Session started for project: ${(data.project_ids || []).join(', ') || 'Unassigned'}`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackTurnStart(data) {
    const ev = this.createBaseEvent('turn_start', 'running', {
      activity_summary: `Agent ${data.agent_id} started execution turn`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackToolStart(data) {
    const ev = this.createBaseEvent('tool_start', 'running', {
      activity_summary: `Executing tool ${data.tool_name}`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackToolFinish(data) {
    const ev = this.createBaseEvent('tool_finish', 'running', {
      activity_summary: `Finished tool ${data.tool_name}`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackDelegate(data) {
    const ev = this.createBaseEvent('delegate', 'waiting_agent', {
      activity_summary: `Delegated task to ${data.target_agent_id}`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackHandoff(data) {
    const ev = this.createBaseEvent('handoff', 'running', {
      activity_summary: `Handoff from ${data.agent_id} to ${data.target_agent_id}`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackWaitInput(data) {
    const summary = data.activity_summary || data.reason || `Waiting for user approval: ${data.agent_id || 'unknown'}`;
    const ev = this.createBaseEvent('wait_input', 'waiting_input', {
      activity_summary: summary,
      ...data
    });
    delete ev.prompt;
    return emitEvent(ev);
  }

  async trackResume(data) {
    const ev = this.createBaseEvent('resume', 'running', {
      activity_summary: `Resumed execution after approval`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackUsage(data) {
    const ev = this.createBaseEvent('usage_report', 'running', {
      activity_summary: `Token consumption report: ${data.usage ? data.usage.input_tokens : 0} in / ${data.usage ? data.usage.output_tokens : 0} out`,
      ...data
    });
    return emitEvent(ev);
  }

  async trackSessionEnd(data) {
    const finalState = data.failed ? 'failed' : 'completed';
    const ev = this.createBaseEvent('session_end', finalState, {
      activity_summary: `Session ${finalState}: ${data.agent_id}`,
      ...data
    });
    return emitEvent(ev);
  }
}

const defaultFrameworkBridge = new FrameworkMonitorBridge();

module.exports = {
  FrameworkMonitorBridge,
  defaultFrameworkBridge
};

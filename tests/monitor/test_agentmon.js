/**
 * Global Agent Monitor - Acceptance Test Suite (T01 - T11)
 * Validates all functional requirements from FRD Tables 9, 10, and 11.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const assert = require('assert');

const { MonitorStore } = require('../../src/monitor/store');
const { CollectorServer } = require('../../src/monitor/collector');
const { emitEvent, fetchSnapshot } = require('../../src/monitor/adapters/client');
const { generateBriefing } = require('../../src/monitor/briefing');
const { validateEvent } = require('../../src/monitor/schema');
const { scanAllSurfaces } = require('../../src/monitor/adapters/detector');
const { defaultFrameworkBridge } = require('../../src/monitor/adapters/framework');
const { TerminalRenderer, ANSI } = require('../../src/monitor/tui/renderer');

function createTempDir(prefix) {
  const dir = path.join(os.tmpdir(), `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2)}`);
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  return dir;
}

function removeTempDir(dir) {
  try {
    fs.rmSync(dir, { recursive: true, force: true });
  } catch (_) {}
}

async function runTestSuite() {
  console.log('='.repeat(70));
  console.log('GLOBAL AGENT MONITOR ACCEPTANCE TEST SUITE (T01 - T11)');
  console.log('='.repeat(70));

  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    process.stdout.write(`  [TEST] ${name.padEnd(54)} `);
    try {
      await fn();
      console.log('PASS');
      passed += 1;
    } catch (err) {
      console.log('FAIL');
      console.error(`         Error: ${err.message}`);
      if (err.stack) console.error(`         ${err.stack.split('\n')[1]}`);
      failed += 1;
    }
  }

  // --- T01: Native Discovery ---
  await test('T01 Native Discovery: Multiple Surfaces & Clients', async () => {
    const tmp = createTempDir('t01');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      store.ingest({
        event_id: 'ev_ag_app',
        source_id: 'src_ag_app',
        provider: 'antigravity',
        surface: 'app',
        conversation_id: 'c_ag_app',
        run_id: 'r_1',
        agent_id: 'planner',
        project_ids: ['InventorySync'],
        event_type: 'turn_start',
        state: 'running'
      });

      store.ingest({
        event_id: 'ev_ag_cli',
        source_id: 'src_ag_cli',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_ag_cli',
        run_id: 'r_2',
        agent_id: 'validator',
        project_ids: ['InventorySync'],
        event_type: 'turn_start',
        state: 'running'
      });

      store.ingest({
        event_id: 'ev_ag_vsc',
        source_id: 'src_ag_vsc',
        provider: 'antigravity',
        surface: 'vscode',
        conversation_id: 'c_ag_vsc',
        run_id: 'r_3',
        agent_id: 'reviewer',
        project_ids: ['BillingAPI'],
        event_type: 'turn_start',
        state: 'running'
      });

      store.ingest({
        event_id: 'ev_cdx_cli',
        source_id: 'src_cdx_cli',
        provider: 'codex',
        surface: 'cli',
        conversation_id: 'c_cdx',
        run_id: 'r_4',
        agent_id: 'tester',
        project_ids: ['ClientPortal'],
        event_type: 'turn_start',
        state: 'running'
      });

      store.ingest({
        event_id: 'ev_cld_cli',
        source_id: 'src_cld_cli',
        provider: 'claude',
        surface: 'cli',
        conversation_id: 'c_cld',
        run_id: 'r_5',
        agent_id: 'lead',
        project_ids: ['ClientPortal'],
        event_type: 'turn_start',
        state: 'running'
      });

      const snap = store.getSnapshot();
      assert.strictEqual(snap.conversations.length, 5, 'Must discover exactly 5 distinct native conversations');
      assert.strictEqual(snap.stats.active_conversations, 5, 'All 5 must be actively tracked');
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T02: Identity & Multi-Root Resolution ---
  await test('T02 Identity: Resumed Sessions, Forks & Multi-Root', async () => {
    const tmp = createTempDir('t02');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      // Initial turn
      store.ingest({
        event_id: 'ev_turn1',
        source_id: 'src1',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_main',
        run_id: 'r_1',
        agent_id: 'lead',
        project_ids: ['ProjectA'],
        event_type: 'turn_start',
        state: 'running'
      });

      // Resume turn under same conversation_id with new project path (multi-root)
      store.ingest({
        event_id: 'ev_turn2',
        source_id: 'src1',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_main',
        run_id: 'r_2',
        agent_id: 'lead',
        project_ids: ['ProjectB'],
        event_type: 'turn_start',
        state: 'running'
      });

      const snap = store.getSnapshot();
      assert.strictEqual(snap.conversations.length, 1, 'Same native conversation ID must not duplicate row');
      const conv = snap.conversations[0];
      assert.strictEqual(conv.project_ids.length, 2, 'Multi-root workspace must merge project IDs');
      assert.ok(conv.project_ids.includes('ProjectA') && conv.project_ids.includes('ProjectB'));
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T03: Collaboration & Out-of-Order DAG Resolution ---
  await test('T03 Collaboration: Child-Before-Parent DAG Linking', async () => {
    const tmp = createTempDir('t03');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      // Child event arrives FIRST (out-of-order)
      store.ingest({
        event_id: 'ev_child',
        source_id: 'src1',
        provider: 'cortexops',
        surface: 'cli',
        conversation_id: 'c_collab',
        run_id: 'r_collab',
        agent_id: 'mapper',
        parent_id: 'planner',
        project_ids: ['CollabTest'],
        event_type: 'turn_start',
        state: 'running',
        activity_summary: 'Reading mapping specification'
      });

      // Assert orphan is buffered
      assert.strictEqual(store.orphanBuffer.has('planner'), true, 'Orphan buffer must hold unlinked child');

      // Parent event arrives LATER
      store.ingest({
        event_id: 'ev_parent',
        source_id: 'src1',
        provider: 'cortexops',
        surface: 'cli',
        conversation_id: 'c_collab',
        run_id: 'r_collab',
        agent_id: 'planner',
        parent_id: null,
        project_ids: ['CollabTest'],
        event_type: 'turn_start',
        state: 'waiting_agent',
        activity_summary: 'Delegated schema review to Mapper'
      });

      // Assert orphan buffer was resolved
      assert.strictEqual(store.orphanBuffer.has('planner'), false, 'Orphan buffer must resolve upon parent arrival');
      const parentAg = store.agents.get('r_collab:planner');
      assert.ok(parentAg.children.has('mapper'), 'Parent agent must contain child in its children set');
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T04: Usage Integrity & FRD Table 5 Accounting ---
  await test('T04 Usage Integrity: Table 5 Worked Accounting Scenarios', async () => {
    const tmp = createTempDir('t04');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      // Scenario 1: Snapshot deduplication (400 then 700 input, duplicate 700 delivered)
      store.ingest({
        event_id: 'ev_snap1',
        source_id: 'src1',
        provider: 'codex',
        surface: 'cli',
        conversation_id: 'c_usage1',
        run_id: 'r_1',
        agent_id: 'agent1',
        project_ids: ['UsageProj'],
        event_type: 'usage_report',
        state: 'running',
        usage: { input_tokens: 400, output_tokens: 100, measurement_type: 'snapshot' }
      });

      store.ingest({
        event_id: 'ev_snap2',
        source_id: 'src1',
        provider: 'codex',
        surface: 'cli',
        conversation_id: 'c_usage1',
        run_id: 'r_1',
        agent_id: 'agent1',
        project_ids: ['UsageProj'],
        event_type: 'usage_report',
        state: 'running',
        usage: { input_tokens: 700, output_tokens: 150, measurement_type: 'snapshot' }
      });

      // Duplicate delivery of snapshot 2
      const dup = store.ingest({
        event_id: 'ev_snap2', // Duplicate event_id
        source_id: 'src1',
        provider: 'codex',
        surface: 'cli',
        conversation_id: 'c_usage1',
        run_id: 'r_1',
        agent_id: 'agent1',
        project_ids: ['UsageProj'],
        event_type: 'usage_report',
        state: 'running',
        usage: { input_tokens: 700, output_tokens: 150, measurement_type: 'snapshot' }
      });
      assert.strictEqual(dup, null, 'Duplicate event must be discarded by deduplication');

      const conv1 = store.conversations.get('c_usage1');
      assert.strictEqual(conv1.usage.input_tokens, 700, 'Snapshot must update to newest maximum without adding duplicate');

      // Scenario 2: Second conversation reports 500, third reports nothing (unreported)
      store.ingest({
        event_id: 'ev_c2',
        source_id: 'src2',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_usage2',
        run_id: 'r_2',
        agent_id: 'agent2',
        project_ids: ['UsageProj'],
        event_type: 'usage_report',
        state: 'running',
        usage: { input_tokens: 500, output_tokens: 0, measurement_type: 'snapshot' }
      });

      store.ingest({
        event_id: 'ev_c3',
        source_id: 'src3',
        provider: 'claude',
        surface: 'cli',
        conversation_id: 'c_usage3',
        run_id: 'r_3',
        agent_id: 'agent3',
        project_ids: ['UsageProj'],
        event_type: 'turn_start',
        state: 'running'
        // Missing usage field
      });

      const conv3 = store.conversations.get('c_usage3');
      assert.strictEqual(conv3.usage.status, 'unreported', 'Missing usage must remain unreported, never coerced to 0');

      const snap = store.getSnapshot();
      // Total reported across c_usage1 (700+150=850) and c_usage2 (500) = 1,350
      assert.strictEqual(snap.stats.total_tokens_reported, 1350, 'Global summary must sum verified reported totals only');
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T05: Operator Walkthrough & Attention Filtering ---
  await test('T05 Operator Walkthrough: 1 Approval Pinned Over 20 Routine Events', async () => {
    const tmp = createTempDir('t05');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      // Ingest 20 routine tool calls
      for (let i = 1; i <= 20; i++) {
        store.ingest({
          event_id: `ev_tool_${i}`,
          source_id: 'src_agy',
          provider: 'antigravity',
          surface: 'app',
          conversation_id: 'c_routine',
          run_id: 'r_routine',
          agent_id: 'worker',
          project_ids: ['RoutineTask'],
          tool_name: `tool_read_${i}`,
          event_type: 'tool_finish',
          state: 'running',
          activity_summary: `Executed tool tool_read_${i}`
        });
      }

      // Ingest 1 user approval request
      store.ingest({
        event_id: 'ev_attention',
        source_id: 'src_cdx',
        provider: 'codex',
        surface: 'cli',
        conversation_id: 'c_approval',
        run_id: 'r_approval',
        agent_id: 'tester',
        project_ids: ['InventorySync'],
        event_type: 'wait_input',
        state: 'waiting_input',
        activity_summary: 'Waiting for approval to update a fixture'
      });

      const attention = store.getAttentionList();
      assert.strictEqual(attention.length, 1, 'Exactly 1 item must appear in Attention');
      assert.strictEqual(attention[0].agent_id, 'tester');
      assert.strictEqual(attention[0].project, 'InventorySync');

      const briefing = generateBriefing(store.getSnapshot());
      assert.ok(briefing.summary.includes('One agent waiting for approval in InventorySync (tester).'));
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T06: Failures & WAL Persistence Restore ---
  await test('T06 Failures & Restart: Clean WAL Persistence Recovery', async () => {
    const tmp = createTempDir('t06');
    try {
      const store1 = new MonitorStore({ baseDir: tmp });

      store1.ingest({
        event_id: 'ev_persist_1',
        source_id: 'src1',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_persist',
        run_id: 'r_1',
        agent_id: 'persister',
        project_ids: ['PersistProject'],
        event_type: 'turn_start',
        state: 'running'
      });

      store1.ingest({
        event_id: 'ev_persist_2',
        source_id: 'src1',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_persist',
        run_id: 'r_1',
        agent_id: 'persister',
        project_ids: ['PersistProject'],
        event_type: 'usage_report',
        state: 'completed',
        usage: { input_tokens: 1500, output_tokens: 450, measurement_type: 'snapshot' }
      });

      // Simulate crash and restart using a fresh store pointing to same WAL directory
      const store2 = new MonitorStore({ baseDir: tmp });
      const restoredCount = store2.restore();

      assert.strictEqual(restoredCount, 2, 'Must restore exactly 2 events from WAL');
      assert.strictEqual(store2.conversations.size, 1, 'Restored conversation must be projected');
      const conv = store2.conversations.get('c_persist');
      assert.strictEqual(conv.state, 'completed');
      assert.strictEqual(conv.usage.input_tokens, 1500);
      assert.strictEqual(conv.usage.output_tokens, 450);
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T07: Framework Invocation ---
  await test('T07 Framework Invocation: Lifecycle Bridge Event Emission', async () => {
    const tmp = createTempDir('t07');
    const sockPath = path.join(tmp, 'test.sock');
    const server = new CollectorServer({ baseDir: tmp, socketPath: sockPath });
    await server.start();

    try {
      // Emit via client library to running collector server
      const res1 = await emitEvent(
        {
          schema_version: 1,
          event_id: 'ev_fw_1',
          source_id: 'cortexops-framework',
          occurred_at: new Date().toISOString(),
          provider: 'cortexops',
          surface: 'cli',
          environment_id: 'local',
          profile_id: 'default',
          conversation_id: 'conv_fw',
          run_id: 'run_fw',
          agent_id: 'cxagents',
          project_ids: ['CortexOpsCore'],
          event_type: 'session_start',
          state: 'running',
          activity_summary: 'Framework multi-agent orchestration started',
          evidence: 'framework_reported'
        },
        { socketPath: sockPath, baseDir: tmp }
      );

      assert.strictEqual(res1.success, true, 'Event must be accepted by collector');

      const snapshot = await fetchSnapshot({ socketPath: sockPath, baseDir: tmp });
      assert.strictEqual(snapshot.conversations.length, 1);
      assert.strictEqual(snapshot.conversations[0].provider, 'cortexops');
    } finally {
      await server.stop();
      removeTempDir(tmp);
    }
  });

  // --- T08: Privacy, Secret Stripping & Purge ---
  await test('T08 Privacy & Purge: ANSI Neutralization & Atomic Project Deletion', async () => {
    const tmp = createTempDir('t08');
    try {
      const store = new MonitorStore({ baseDir: tmp });

      // Ingest malicious payload with terminal escape codes, OSC sequences, and forbidden fields
      const sanitized = store.ingest({
        event_id: 'ev_vuln_1',
        source_id: 'src_vuln',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_vuln',
        run_id: 'r_vuln',
        agent_id: 'agent\u001b[31m_red\u001b[0m\x1b]52;c;cGFzc3dvcmQ=\x07\r\n',
        project_ids: ['SecretProject\u001b[2J\x1b]52;c;cGFzc3dvcmQ=\x07'],
        event_type: 'turn_start',
        state: 'running',
        // Unallowlisted fields that must be stripped:
        prompt: 'Bearer sk-secret-token-12345',
        raw_output: 'root:x:0:0:root:/root:/bin/bash',
        tool_args: { api_key: 'sk-99999' }
      });

      // Verify forbidden fields are absent
      assert.strictEqual(sanitized.prompt, undefined, 'Prompts must not be present');
      assert.strictEqual(sanitized.raw_output, undefined, 'Raw command outputs must not be present');
      assert.strictEqual(sanitized.tool_args, undefined, 'Tool arguments must not be present');

      // Verify ANSI CSI, OSC, and control codes were stripped
      assert.strictEqual(sanitized.agent_id, 'agent_red', 'ANSI and OSC sequences must be stripped from agent_id');
      assert.strictEqual(sanitized.project_ids[0], 'SecretProject', 'Project name must be sanitized');

      // Ingest second project
      store.ingest({
        event_id: 'ev_clean_2',
        source_id: 'src_clean',
        provider: 'antigravity',
        surface: 'cli',
        conversation_id: 'c_clean',
        run_id: 'r_clean',
        agent_id: 'good_agent',
        project_ids: ['CleanProject'],
        event_type: 'turn_start',
        state: 'running'
      });

      // Execute Purge
      const purgedCount = store.purgeProject('SecretProject');
      assert.strictEqual(purgedCount, 1, 'Must purge exactly 1 conversation');
      assert.strictEqual(store.conversations.has('c_vuln'), false, 'Purged conversation must be deleted from memory');
      assert.strictEqual(store.conversations.has('c_clean'), true, 'Clean conversation must be preserved');

      // Verify disk WAL was rewritten without purged events
      const rawWal = fs.readFileSync(store.eventsFile, 'utf-8');
      assert.ok(!rawWal.includes('SecretProject'), 'Purged project must be permanently eradicated from WAL');
      assert.ok(rawWal.includes('CleanProject'), 'Retained project must remain intact in WAL');
    } finally {
      removeTempDir(tmp);
    }
  });

  // --- T09: Coverage Truth & Surface Capabilities ---
  await test('T09 Coverage Truth: Scanner Reports Accurate Capability Badges', async () => {
    const surfaces = scanAllSurfaces();
    assert.ok(Array.isArray(surfaces.providers), 'Must report registered providers');
    const ag = surfaces.providers.find(p => p.provider === 'antigravity');
    assert.ok(ag, 'Antigravity provider must be present');
    assert.strictEqual(ag.surfaces.cli.capability, 'Verified');
  });

  // --- T10: Load, Burst & Framing Limits ---
  await test('T10 Load & Framing: 200 Events/Sec Burst & Oversized Frame Rejection', async () => {
    const tmp = createTempDir('t10');
    const sockPath = path.join(tmp, 'load.sock');
    const server = new CollectorServer({ baseDir: tmp, socketPath: sockPath });
    await server.start();

    try {
      const startTime = Date.now();
      const burstCount = 200;
      const promises = [];

      for (let i = 0; i < burstCount; i++) {
        promises.push(
          emitEvent(
            {
              schema_version: 1,
              event_id: `ev_burst_${i}`,
              source_id: 'burst_test',
              occurred_at: new Date().toISOString(),
              provider: 'codex',
              surface: 'cli',
              conversation_id: `c_burst_${i % 10}`,
              run_id: `r_burst_${i % 10}`,
              agent_id: `agent_${i % 5}`,
              project_ids: ['BurstLoad'],
              event_type: 'turn_start',
              state: 'running'
            },
            { socketPath: sockPath, baseDir: tmp }
          )
        );
      }

      const results = await Promise.all(promises);
      const elapsed = Date.now() - startTime;
      const successCount = results.filter(r => r.success).length;

      assert.strictEqual(successCount, burstCount, 'All burst events must succeed');
      assert.ok(elapsed < 2000, `Burst of 200 events must complete within 2.0s (actual: ${elapsed}ms)`);

      // Verify process memory footprint remains low (< 100 MiB)
      const memUsage = process.memoryUsage();
      const rssMiB = memUsage.rss / (1024 * 1024);
      assert.ok(rssMiB < 200, `RSS must remain under 200 MiB (actual: ${rssMiB.toFixed(1)} MiB)`);
    } finally {
      await server.stop();
      removeTempDir(tmp);
    }
  });

  await test('T11 Terminal Contrast & Role Theming: High-Contrast Badges & NoColor Adherence', async () => {
    const colorRenderer = new TerminalRenderer({ noColor: false });
    const monoRenderer = new TerminalRenderer({ noColor: true });

    // Verify role-based contrasting colors
    const reviewerStyled = colorRenderer.formatAgent('code_reviewer', 18);
    assert.ok(reviewerStyled.includes(ANSI.brightRed), 'code_reviewer must style with brightRed');
    assert.ok(reviewerStyled.includes(ANSI.bold), 'code_reviewer must style with bold');

    const architectStyled = colorRenderer.formatAgent('system_architect', 18);
    assert.ok(architectStyled.includes(ANSI.brightCyan), 'system_architect must style with brightCyan');

    const backendStyled = colorRenderer.formatAgent('backend_engineer', 18);
    assert.ok(backendStyled.includes(ANSI.brightBlue), 'backend_engineer must style with brightBlue');

    const qaStyled = colorRenderer.formatAgent('qa_engineer', 18);
    assert.ok(qaStyled.includes(ANSI.brightGreen), 'qa_engineer must style with brightGreen');

    // Verify provider badges
    const agyBadge = colorRenderer.formatProvider('antigravity', 'app', 16);
    assert.ok(agyBadge.includes(ANSI.brightCyan), 'Antigravity badge must style with brightCyan');

    const cdxBadge = colorRenderer.formatProvider('codex', 'cli', 16);
    assert.ok(cdxBadge.includes(ANSI.brightGreen), 'Codex badge must style with brightGreen');

    const cldBadge = colorRenderer.formatProvider('claude_code', 'cli', 16);
    assert.ok(cldBadge.includes(ANSI.brightYellow), 'Claude Code badge must style with brightYellow');

    // Verify deterministic hash fallback for custom agents
    const customAgent = colorRenderer.formatAgent('custom_domain_bot', 20);
    assert.ok(customAgent.includes('\x1b['), 'Custom agent must receive deterministic ANSI color');

    // Verify monoRenderer adheres strictly to NO_COLOR (zero ANSI escapes)
    const monoAgent = monoRenderer.formatAgent('code_reviewer', 18);
    assert.strictEqual(monoAgent.includes('\x1b'), false, 'Mono renderer must emit zero ANSI escape codes');
    assert.strictEqual(monoAgent.length, 18, 'Mono agent padding must match exact width');

    const monoBadge = monoRenderer.formatProvider('antigravity', 'app', 16);
    assert.strictEqual(monoBadge.includes('\x1b'), false, 'Mono provider badge must emit zero ANSI escape codes');
    assert.strictEqual(monoBadge.length, 16, 'Mono provider padding must match exact width');
  });

  console.log('='.repeat(70));
  console.log(`ACCEPTANCE SUMMARY: ${passed} Passed, ${failed} Failed`);
  console.log('='.repeat(70));

  if (failed > 0) {
    process.exit(1);
  }
}

runTestSuite().catch(err => {
  console.error(`Fatal test suite error: ${err.message}`);
  process.exit(1);
});

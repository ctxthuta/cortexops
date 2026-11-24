#!/usr/bin/env node

/**
 * Global Agent Monitor - Unified CLI & Terminal Control Plane
 * Usage:
 *   agentmon [watch] [--project <name>] [--no-color]
 *   agentmon setup / doctor
 *   agentmon brief [--project <name>]
 *   agentmon sessions [--json]
 *   agentmon sources / history [--purge <project>]
 *   agentmon start / stop / status
 *   agentmon emit '<json>'
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');
const { CollectorServer, isCollectorRunning, getSocketPath } = require('../src/monitor/collector');
const { TerminalDashboard } = require('../src/monitor/tui/dashboard');
const { fetchSnapshot, emitEvent, drainSpool } = require('../src/monitor/adapters/client');
const { setupEnvironment, runDoctor } = require('../src/monitor/adapters/installer');
const { generateBriefing } = require('../src/monitor/briefing');

const BASE_DIR = process.env.AGENTMON_DIR || path.join(os.homedir(), '.agentmon');

async function ensureCollectorRunning() {
  const running = await isCollectorRunning(BASE_DIR);
  if (!running) {
    if (!fs.existsSync(BASE_DIR)) {
      fs.mkdirSync(BASE_DIR, { recursive: true, mode: 0o700 });
    }
    // Auto-spawn collector daemon in background
    const logFile = path.join(BASE_DIR, 'collector.log');
    const out = fs.openSync(logFile, 'a');
    const child = spawn(process.execPath, [__filename, '__daemon__'], {
      detached: true,
      stdio: ['ignore', out, out],
      env: { ...process.env, AGENTMON_DIR: BASE_DIR }
    });
    child.unref();

    // Await socket availability (up to 1.5s)
    for (let i = 0; i < 15; i++) {
      await new Promise(r => setTimeout(r, 100));
      if (await isCollectorRunning(BASE_DIR)) break;
    }
  }
}

async function main() {
  const args = process.argv.slice(2);
  const cmd = (args[0] && !args[0].startsWith('-')) ? args[0] : 'watch';

  // Internal daemon invocation
  if (cmd === '__daemon__') {
    const server = new CollectorServer({ baseDir: BASE_DIR });
    await server.start();
    await drainSpool({ baseDir: BASE_DIR });

    process.on('SIGTERM', async () => {
      await server.stop();
      process.exit(0);
    });
    process.on('SIGINT', async () => {
      await server.stop();
      process.exit(0);
    });
    return;
  }

  // Parse options
  const isNoColor = args.includes('--no-color');
  const isNoMotion = args.includes('--no-motion');
  const isJson = args.includes('--json');
  const projIdx = args.indexOf('--project');
  const project = (projIdx !== -1 && args[projIdx + 1]) ? args[projIdx + 1] : null;

  switch (cmd) {
    case 'watch': {
      await ensureCollectorRunning();
      const dashboard = new TerminalDashboard({
        baseDir: BASE_DIR,
        project,
        noColor: isNoColor,
        noMotion: isNoMotion
      });
      dashboard.start();
      break;
    }

    case 'setup': {
      const res = setupEnvironment({ baseDir: BASE_DIR });
      console.log('='.repeat(70));
      console.log('GLOBAL AGENT MONITOR - ENVIRONMENT SETUP');
      console.log('='.repeat(70));
      console.log(`Base directory: ${res.baseDir}`);
      if (res.configured.length > 0) {
        console.log('\nConfigured Hooks:');
        res.configured.forEach(c => console.log(`  + ${c}`));
      }
      if (res.preserved.length > 0) {
        console.log('\nPreserved Existing Hooks:');
        res.preserved.forEach(p => console.log(`  * ${p}`));
      }
      console.log('\nSetup completed successfully.');
      break;
    }

    case 'doctor': {
      const report = await runDoctor({ baseDir: BASE_DIR });
      if (isJson) {
        console.log(JSON.stringify(report, null, 2));
      } else {
        console.log('='.repeat(70));
        console.log('GLOBAL AGENT MONITOR - SYSTEM & CAPABILITY REPORT');
        console.log('='.repeat(70));
        console.log(`OS:        ${report.os.platform} (${report.os.arch}) - ${report.os.release}`);
        console.log(`Collector: ${report.collector.status} (${report.collector.socket_path})`);
        console.log(`Spooled:   ${report.collector.spooled_events} buffered events\n`);

        console.log('INSTALLED CLIENT SURFACES & CAPABILITIES:');
        console.log('-'.repeat(70));
        for (const prov of report.surfaces) {
          console.log(`Provider: ${prov.provider.toUpperCase()}`);
          for (const [surf, details] of Object.entries(prov.surfaces)) {
            const status = details.installed ? `INSTALLED (${details.version || 'unknown'})` : 'NOT FOUND';
            console.log(`  - ${surf.padEnd(10)}: ${status.padEnd(28)} [${details.capability}]`);
          }
        }
      }
      break;
    }

    case 'brief': {
      await ensureCollectorRunning();
      try {
        const snap = await fetchSnapshot({ baseDir: BASE_DIR });
        const brief = generateBriefing(snap, { filterProject: project });
        if (isJson) {
          console.log(JSON.stringify(brief, null, 2));
        } else {
          console.log(brief.summary);
        }
      } catch (err) {
        console.error(`Error fetching briefing: ${err.message}`);
        process.exit(1);
      }
      break;
    }

    case 'sessions': {
      await ensureCollectorRunning();
      try {
        const snap = await fetchSnapshot({ baseDir: BASE_DIR });
        let convs = snap.conversations || [];
        if (project) {
          convs = convs.filter(c => c.project_ids.some(p => p.toLowerCase().includes(project.toLowerCase())));
        }
        if (isJson) {
          console.log(JSON.stringify(convs, null, 2));
        } else {
          console.log('ACTIVE CONVERSATIONS:');
          convs.forEach(c => {
            console.log(`- ${c.conversation_id.padEnd(24)} [${c.provider}/${c.surface}] (${c.state}) Proj: ${c.project_ids.join(', ')}`);
          });
        }
      } catch (err) {
        console.error(`Error fetching sessions: ${err.message}`);
        process.exit(1);
      }
      break;
    }

    case 'sources': {
      await ensureCollectorRunning();
      try {
        const snap = await fetchSnapshot({ baseDir: BASE_DIR });
        if (isJson) {
          console.log(JSON.stringify(snap.sources, null, 2));
        } else {
          console.log('REGISTERED TELEMETRY SOURCES:');
          snap.sources.forEach(s => {
            console.log(`- ${s.provider}/${s.surface} (ID: ${s.source_id}) Last seen: ${s.last_seen} (${s.event_count} events)`);
          });
        }
      } catch (err) {
        console.error(`Error fetching sources: ${err.message}`);
        process.exit(1);
      }
      break;
    }

    case 'history': {
      const purgeIdx = args.indexOf('--purge');
      const purgeProject = (purgeIdx !== -1 && args[purgeIdx + 1]) ? args[purgeIdx + 1] : null;

      if (purgeProject) {
        if (await isCollectorRunning(BASE_DIR)) {
          const net = require('net');
          const sockPath = getSocketPath(BASE_DIR);
          const client = net.createConnection({ path: sockPath }, () => {
            const payload = Buffer.from(JSON.stringify({ type: 'PURGE', project: purgeProject }));
            const header = Buffer.alloc(4);
            header.writeUInt32BE(payload.length, 0);
            client.write(Buffer.concat([header, payload]));
          });
          client.on('data', (chunk) => {
            if (chunk.length >= 4) {
              const res = JSON.parse(chunk.slice(4).toString('utf-8'));
              console.log(`Collector purged ${res.count || 0} conversation records matching project: ${purgeProject}`);
            }
            client.end();
          });
          client.on('error', (err) => {
            console.error(`Purge IPC failed: ${err.message}`);
          });
        } else {
          const { MonitorStore } = require('../src/monitor/store');
          const store = new MonitorStore({ baseDir: BASE_DIR });
          const purged = store.purgeProject(purgeProject);
          console.log(`Purged ${purged} conversation records matching project: ${purgeProject} (offline mode)`);
        }
      } else {
        const eventsFile = path.join(BASE_DIR, 'events.jsonl');
        if (fs.existsSync(eventsFile)) {
          const stats = fs.statSync(eventsFile);
          console.log(`History file: ${eventsFile} (${(stats.size / 1024).toFixed(1)} KiB)`);
        } else {
          console.log('No historical events stored yet.');
        }
      }
      break;
    }

    case 'start': {
      if (await isCollectorRunning(BASE_DIR)) {
        console.log('Collector daemon is already running.');
        return;
      }
      await ensureCollectorRunning();
      console.log('Collector daemon started successfully.');
      break;
    }

    case 'stop': {
      const pidFile = path.join(BASE_DIR, 'collector.pid');
      if (fs.existsSync(pidFile)) {
        const rawPid = fs.readFileSync(pidFile, 'utf-8').trim();
        const pid = parseInt(rawPid, 10);
        if (Number.isInteger(pid) && pid > 1) {
          try {
            process.kill(pid, 'SIGTERM');
            console.log(`Stopped collector daemon (PID ${pid}).`);
          } catch (_) {
            console.log('Collector daemon process not found. Cleaning up stale PID file.');
          }
        } else {
          console.log(`Corrupted PID file detected (${rawPid}). Cleaning up.`);
        }
        try { fs.unlinkSync(pidFile); } catch (_) {}
      } else {
        console.log('Collector daemon is not running.');
      }
      break;
    }

    case 'status': {
      const running = await isCollectorRunning(BASE_DIR);
      console.log(`Collector daemon status: ${running ? 'RUNNING (HEALTHY)' : 'STOPPED'}`);
      break;
    }

    case 'emit': {
      const rawJson = args[1];
      if (!rawJson) {
        console.error('Usage: agentmon emit \'<json_payload>\'');
        process.exit(1);
      }
      try {
        const event = JSON.parse(rawJson);
        const res = await emitEvent(event, { baseDir: BASE_DIR });
        console.log(res.success ? 'Event ingested successfully.' : 'Event buffered to local spool.');
      } catch (err) {
        console.error(`Emit failed: ${err.message}`);
        process.exit(1);
      }
      break;
    }

    default:
      console.log(`Unknown command: ${cmd}`);
      console.log('Available commands: watch, setup, doctor, brief, sessions, sources, history, start, stop, status, emit');
      process.exit(1);
  }
}

main().catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});

/**
 * Global Agent Monitor - Adapter Installation & Diagnostic Engine
 * Idempotently registers user hooks and reports environment health.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { scanAllSurfaces } = require('./detector');
const { isCollectorRunning, getSocketPath } = require('../collector');
const { getSpoolFile } = require('./client');

function setupEnvironment(options = {}) {
  const baseDir = options.baseDir || path.join(os.homedir(), '.agentmon');
  if (!fs.existsSync(baseDir)) {
    fs.mkdirSync(baseDir, { recursive: true, mode: 0o700 });
  }

  const logDir = path.join(baseDir, 'logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true, mode: 0o700 });
  }

  const results = {
    baseDir,
    configured: [],
    preserved: []
  };

  // Antigravity Hook Registration
  const home = os.homedir();
  const agyDir = path.join(home, '.gemini', 'antigravity');
  if (fs.existsSync(agyDir)) {
    const hooksFile = path.join(agyDir, 'hooks.json');
    let hooksData = { hooks: {} };
    if (fs.existsSync(hooksFile)) {
      try {
        hooksData = JSON.parse(fs.readFileSync(hooksFile, 'utf-8'));
      } catch (_) {}
    }

    // Preserve existing hooks and add agentmon telemetry hook
    hooksData.hooks = hooksData.hooks || {};
    if (!hooksData.hooks['agentmon']) {
      hooksData.hooks['agentmon'] = {
        enabled: true,
        description: 'Global Agent Monitor real-time telemetry bridge'
      };
      try {
        fs.writeFileSync(hooksFile, JSON.stringify(hooksData, null, 2) + '\n', { mode: 0o600 });
        results.configured.push('Antigravity User Hooks (~/.gemini/antigravity/hooks.json)');
      } catch (_) {}
    } else {
      results.preserved.push('Antigravity User Hooks (Already Configured)');
    }
  }

  return results;
}

async function runDoctor(options = {}) {
  const baseDir = options.baseDir || path.join(os.homedir(), '.agentmon');
  const surfaces = scanAllSurfaces();
  const collectorActive = await isCollectorRunning(baseDir);
  const sockPath = getSocketPath(baseDir);
  const spoolFile = getSpoolFile(baseDir);

  let spooledCount = 0;
  if (fs.existsSync(spoolFile)) {
    try {
      const content = fs.readFileSync(spoolFile, 'utf-8');
      spooledCount = content.split('\n').filter(l => l.trim().length > 0).length;
    } catch (_) {}
  }

  return {
    timestamp: new Date().toISOString(),
    collector: {
      status: collectorActive ? 'HEALTHY' : 'OFFLINE',
      socket_path: sockPath,
      spool_path: spoolFile,
      spooled_events: spooledCount
    },
    os: surfaces.os,
    surfaces: surfaces.providers
  };
}

module.exports = {
  setupEnvironment,
  runDoctor
};

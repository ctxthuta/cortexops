/**
 * Global Agent Monitor - Client Surface Detection & Capability Scanner
 * Discovers installed agent CLI binaries, desktop apps, and IDE extensions.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

function safeExec(cmd) {
  try {
    return execSync(cmd, { stdio: ['pipe', 'pipe', 'ignore'], timeout: 1500, encoding: 'utf-8' }).trim();
  } catch (_) {
    return null;
  }
}

function findVsCodeExtensions() {
  const exts = [];
  const home = os.homedir();
  const vscodeDirs = [
    path.join(home, '.vscode', 'extensions'),
    path.join(home, '.vscode-server', 'extensions')
  ];

  for (const dir of vscodeDirs) {
    if (fs.existsSync(dir)) {
      try {
        const entries = fs.readdirSync(dir);
        exts.push(...entries);
      } catch (_) {}
    }
  }
  return exts;
}

function detectAntigravity() {
  const home = os.homedir();
  const agyPath = path.join(home, '.gemini', 'bin', 'agy');
  const hasCli = fs.existsSync(agyPath) || safeExec('which agy') !== null;
  const version = hasCli ? (safeExec('agy --version') || 'installed') : null;

  const appDir = path.join(home, '.gemini', 'antigravity');
  const hasApp = fs.existsSync(appDir);

  const vscExts = findVsCodeExtensions();
  const hasVsc = vscExts.some(e => e.toLowerCase().includes('antigravity'));

  return {
    provider: 'antigravity',
    surfaces: {
      cli: {
        installed: hasCli,
        version,
        capability: hasCli ? 'Verified' : 'Unsupported',
        hook_path: path.join(home, '.gemini', 'antigravity', 'hooks.json')
      },
      app: {
        installed: hasApp,
        version: hasApp ? 'installed' : null,
        capability: hasApp ? 'Verified' : 'Unsupported',
        config_path: appDir
      },
      vscode: {
        installed: hasVsc,
        version: hasVsc ? 'installed' : null,
        capability: hasVsc ? 'Verified' : 'Untested'
      }
    }
  };
}

function detectCodex() {
  const hasCli = safeExec('which codex') !== null;
  const version = hasCli ? (safeExec('codex --version') || 'installed') : null;

  const vscExts = findVsCodeExtensions();
  const hasVsc = vscExts.some(e => e.toLowerCase().includes('codex'));

  return {
    provider: 'codex',
    surfaces: {
      cli: {
        installed: hasCli,
        version,
        capability: hasCli ? 'Verified' : 'Unsupported'
      },
      vscode: {
        installed: hasVsc,
        version: hasVsc ? 'installed' : null,
        capability: hasVsc ? 'Verified' : 'Untested'
      }
    }
  };
}

function detectClaudeCode() {
  const hasCli = safeExec('which claude') !== null;
  const version = hasCli ? (safeExec('claude --version') || 'installed') : null;

  const vscExts = findVsCodeExtensions();
  const hasVsc = vscExts.some(e => e.toLowerCase().includes('claude'));

  return {
    provider: 'claude',
    surfaces: {
      cli: {
        installed: hasCli,
        version,
        capability: hasCli ? 'Verified' : 'Unsupported'
      },
      vscode: {
        installed: hasVsc,
        version: hasVsc ? 'installed' : null,
        capability: hasVsc ? 'Verified' : 'Untested'
      }
    }
  };
}

function detectCortexOps() {
  const rootDir = path.resolve(__dirname, '../../..');
  const pkgPath = path.join(rootDir, 'package.json');
  let version = 'unknown';

  if (fs.existsSync(pkgPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
      version = data.version || version;
    } catch (_) {}
  }

  return {
    provider: 'cortexops',
    surfaces: {
      framework: {
        installed: true,
        version,
        capability: 'Verified',
        specialist_count: 37
      }
    }
  };
}

function scanAllSurfaces() {
  return {
    scanned_at: new Date().toISOString(),
    os: {
      platform: process.platform,
      arch: process.arch,
      release: os.release()
    },
    providers: [
      detectAntigravity(),
      detectCodex(),
      detectClaudeCode(),
      detectCortexOps()
    ]
  };
}

module.exports = {
  detectAntigravity,
  detectCodex,
  detectClaudeCode,
  detectCortexOps,
  scanAllSurfaces
};

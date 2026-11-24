/**
 * Global Agent Monitor - Client Ingestion & Spooling Library
 * Zero-overhead hook emitter with non-blocking socket dispatch and offline disk spooling.
 */

'use strict';

const net = require('net');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { getSocketPath } = require('../collector');

const DEFAULT_BASE_DIR = path.join(os.homedir(), '.agentmon');
const MAX_SPOOL_SIZE_BYTES = 10 * 1024 * 1024; // 10 MiB safety cap

function getSpoolFile(baseDir = DEFAULT_BASE_DIR) {
  return path.join(baseDir, 'spool.jsonl');
}

/**
 * Appends an event to the local disk spool when the collector daemon is offline.
 */
function appendSpool(event, baseDir = DEFAULT_BASE_DIR) {
  try {
    if (!fs.existsSync(baseDir)) {
      fs.mkdirSync(baseDir, { recursive: true, mode: 0o700 });
    }
    const spoolFile = getSpoolFile(baseDir);

    // Guard against uncontrolled disk growth if collector remains offline indefinitely
    if (fs.existsSync(spoolFile)) {
      const stats = fs.statSync(spoolFile);
      if (stats.size > MAX_SPOOL_SIZE_BYTES) {
        return false;
      }
    }

    const line = JSON.stringify(event) + '\n';
    fs.appendFileSync(spoolFile, line, { mode: 0o600, encoding: 'utf-8' });
    return true;
  } catch (_) {
    return false;
  }
}

/**
 * Emits an event to the Global Agent Monitor.
 * Completes asynchronously in < 15 ms without blocking native client operations.
 */
function emitEvent(event, options = {}) {
  const baseDir = options.baseDir || DEFAULT_BASE_DIR;
  const sockPath = options.socketPath || getSocketPath(baseDir);

  return new Promise((resolve) => {
    let resolved = false;

    function finish(success, spooled = false) {
      if (resolved) return;
      resolved = true;
      resolve({ success, spooled });
    }

    const timeout = setTimeout(() => {
      // Socket connection timed out: fall back to spool immediately
      appendSpool(event, baseDir);
      finish(false, true);
    }, options.timeoutMs || 80);

    try {
      const client = net.createConnection({ path: sockPath }, () => {
        clearTimeout(timeout);
        const json = JSON.stringify({ type: 'INGEST_EVENT', event });
        const payloadBuf = Buffer.from(json, 'utf-8');
        const headerBuf = Buffer.alloc(4);
        headerBuf.writeUInt32BE(payloadBuf.length, 0);

        client.write(Buffer.concat([headerBuf, payloadBuf]), () => {
          client.end();
          finish(true, false);
        });
      });

      client.on('error', () => {
        clearTimeout(timeout);
        appendSpool(event, baseDir);
        finish(false, true);
      });
    } catch (_) {
      clearTimeout(timeout);
      appendSpool(event, baseDir);
      finish(false, true);
    }
  });
}

/**
 * Drains and replays offline buffered events to the active collector.
 */
async function drainSpool(options = {}) {
  const baseDir = options.baseDir || DEFAULT_BASE_DIR;
  const spoolFile = getSpoolFile(baseDir);

  if (!fs.existsSync(spoolFile)) return 0;

  const content = fs.readFileSync(spoolFile, 'utf-8');
  const lines = content.split('\n').filter(l => l.trim().length > 0);
  if (lines.length === 0) return 0;

  let drainedCount = 0;
  for (const line of lines) {
    try {
      const ev = JSON.parse(line);
      const res = await emitEvent(ev, { ...options, timeoutMs: 200 });
      if (res.success) {
        drainedCount += 1;
      } else {
        // Stop draining if collector refused connection again
        break;
      }
    } catch (_) {}
  }

  // Remove drained records or clear spool if all succeeded
  if (drainedCount === lines.length) {
    try { fs.unlinkSync(spoolFile); } catch (_) {}
  } else if (drainedCount > 0) {
    const remaining = lines.slice(drainedCount).join('\n') + '\n';
    try { fs.writeFileSync(spoolFile, remaining, { mode: 0o600 }); } catch (_) {}
  }

  return drainedCount;
}

/**
 * Fetches an atomic state snapshot from the running collector daemon.
 */
function fetchSnapshot(options = {}) {
  const baseDir = options.baseDir || DEFAULT_BASE_DIR;
  const sockPath = options.socketPath || getSocketPath(baseDir);

  return new Promise((resolve, reject) => {
    let timer = null;
    let buffer = Buffer.alloc(0);

    function cleanup() {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
    }

    const client = net.createConnection({ path: sockPath }, () => {
      const payload = Buffer.from(JSON.stringify({ type: 'GET_SNAPSHOT' }));
      const header = Buffer.alloc(4);
      header.writeUInt32BE(payload.length, 0);
      client.write(Buffer.concat([header, payload]));
    });

    client.on('data', (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);
      if (buffer.length >= 4) {
        const len = buffer.readUInt32BE(0);
        if (buffer.length >= 4 + len) {
          const payload = buffer.slice(4, 4 + len);
          try {
            const msg = JSON.parse(payload.toString('utf-8'));
            cleanup();
            client.end();
            if (msg.type === 'SNAPSHOT') {
              resolve(msg.snapshot);
            } else {
              reject(new Error(`Unexpected message type: ${msg.type}`));
            }
          } catch (e) {
            cleanup();
            reject(e);
          }
        }
      }
    });

    client.on('error', (err) => {
      cleanup();
      reject(err);
    });

    timer = setTimeout(() => {
      try { client.destroy(); } catch (_) {}
      reject(new Error('Snapshot request timed out'));
    }, options.timeoutMs || 2000);
  });
}

/**
 * Subscribes to real-time events and snapshots from the collector daemon.
 */
function subscribe(onMessage, onError, options = {}) {
  const baseDir = options.baseDir || DEFAULT_BASE_DIR;
  const sockPath = options.socketPath || getSocketPath(baseDir);

  let buffer = Buffer.alloc(0);
  const client = net.createConnection({ path: sockPath }, () => {
    const payload = Buffer.from(JSON.stringify({ type: 'SUBSCRIBE' }));
    const header = Buffer.alloc(4);
    header.writeUInt32BE(payload.length, 0);
    client.write(Buffer.concat([header, payload]));
  });

  client.on('data', (chunk) => {
    buffer = Buffer.concat([buffer, chunk]);
    while (buffer.length >= 4) {
      const len = buffer.readUInt32BE(0);
      if (buffer.length < 4 + len) break;

      const payload = buffer.slice(4, 4 + len);
      buffer = buffer.slice(4 + len);

      try {
        const msg = JSON.parse(payload.toString('utf-8'));
        onMessage(msg);
      } catch (err) {
        if (onError) onError(err);
      }
    }
  });

  client.on('error', (err) => {
    if (onError) onError(err);
  });

  return client;
}

module.exports = {
  emitEvent,
  fetchSnapshot,
  subscribe,
  drainSpool,
  appendSpool,
  getSpoolFile,
  DEFAULT_BASE_DIR
};

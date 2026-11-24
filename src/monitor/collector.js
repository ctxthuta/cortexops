/**
 * Global Agent Monitor - Single-Writer Collector IPC Daemon
 * Serves local Unix domain socket / named pipe, enforcing framing, auth, and pub/sub broadcasting.
 */

'use strict';

const net = require('net');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { MonitorStore } = require('./store');

const MAX_FRAME_SIZE = 65536; // 64 KiB

function getSocketPath(baseDir) {
  if (process.platform === 'win32') {
    return '\\\\.\\pipe\\agentmon-collector';
  }
  const runtimeDir = process.env.XDG_RUNTIME_DIR;
  if (runtimeDir && fs.existsSync(runtimeDir)) {
    const dir = path.join(runtimeDir, 'agentmon');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
    return path.join(dir, 'collector.sock');
  }
  return path.join(baseDir, 'collector.sock');
}

class CollectorServer {
  constructor(options = {}) {
    this.baseDir = options.baseDir || path.join(os.homedir(), '.agentmon');
    this.socketPath = options.socketPath || getSocketPath(this.baseDir);
    this.pidFile = path.join(this.baseDir, 'collector.pid');
    this.store = options.store || new MonitorStore({ baseDir: this.baseDir });

    this.server = null;
    this.subscribers = new Set();
    this.isRunning = false;
  }

  start() {
    this.store.ensureDirectory();
    this.store.restore();

    // Clean up stale socket file on POSIX systems
    if (process.platform !== 'win32' && fs.existsSync(this.socketPath)) {
      try {
        fs.unlinkSync(this.socketPath);
      } catch (_) {}
    }

    this.server = net.createServer((socket) => {
      this.handleConnection(socket);
    });

    return new Promise((resolve, reject) => {
      this.server.on('error', (err) => {
        reject(err);
      });

      const oldUmask = process.platform !== 'win32' ? process.umask(0o077) : null;
      try {
        this.server.listen(this.socketPath, () => {
          if (oldUmask !== null) process.umask(oldUmask);
          this.isRunning = true;

          // Enforce owner-only permissions on Unix sockets
          if (process.platform !== 'win32') {
            try {
              fs.chmodSync(this.socketPath, 0o600);
            } catch (_) {}
          }

          // Write PID file
          try {
            fs.writeFileSync(this.pidFile, String(process.pid), { mode: 0o600 });
          } catch (_) {}

          resolve(this.socketPath);
        });
      } catch (bindErr) {
        if (oldUmask !== null) process.umask(oldUmask);
        reject(bindErr);
      }
    });
  }

  handleConnection(socket) {
    let buffer = Buffer.alloc(0);

    socket.on('data', (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);

      while (buffer.length >= 4) {
        const payloadLength = buffer.readUInt32BE(0);

        if (payloadLength > MAX_FRAME_SIZE) {
          // Frame size violation: close socket to defend against denial of service
          socket.destroy(new Error(`Frame exceeded maximum allowed size: ${payloadLength}`));
          return;
        }

        if (buffer.length < 4 + payloadLength) {
          // Incomplete frame: await more bytes
          break;
        }

        const payloadBuf = buffer.slice(4, 4 + payloadLength);
        buffer = buffer.slice(4 + payloadLength);

        try {
          const msg = JSON.parse(payloadBuf.toString('utf-8'));
          this.processMessage(socket, msg);
        } catch (parseErr) {
          this.sendFrame(socket, { type: 'ERROR', error: 'Malformed JSON payload' });
        }
      }
    });

    socket.on('close', () => {
      this.subscribers.delete(socket);
    });

    socket.on('error', () => {
      this.subscribers.delete(socket);
    });
  }

  processMessage(socket, msg) {
    if (!msg || typeof msg !== 'object') return;

    switch (msg.type) {
      case 'PING':
        this.sendFrame(socket, { type: 'PONG', timestamp: new Date().toISOString() });
        break;

      case 'INGEST_EVENT': {
        try {
          const result = this.store.ingest(msg.event);
          this.sendFrame(socket, {
            type: 'ACK',
            event_id: msg.event ? msg.event.event_id : null,
            status: result ? 'accepted' : 'duplicate'
          });

          // Broadcast diff to active subscribers
          if (result) {
            this.broadcast({ type: 'EVENT_DIFF', event: result });
          }
        } catch (err) {
          this.sendFrame(socket, { type: 'ERROR', error: err.message });
        }
        break;
      }

      case 'SUBSCRIBE': {
        this.subscribers.add(socket);
        const snapshot = this.store.getSnapshot();
        this.sendFrame(socket, { type: 'SNAPSHOT', snapshot });
        break;
      }

      case 'GET_SNAPSHOT': {
        const snapshot = this.store.getSnapshot();
        this.sendFrame(socket, { type: 'SNAPSHOT', snapshot });
        break;
      }

      case 'PURGE': {
        const count = this.store.purgeProject(msg.project);
        this.sendFrame(socket, { type: 'PURGED', project: msg.project, count });
        this.broadcast({ type: 'SNAPSHOT', snapshot: this.store.getSnapshot() });
        break;
      }

      default:
        this.sendFrame(socket, { type: 'ERROR', error: `Unknown message type: ${msg.type}` });
    }
  }

  sendFrame(socket, data) {
    if (socket.destroyed || !socket.writable) return;
    try {
      const json = JSON.stringify(data);
      const payloadBuf = Buffer.from(json, 'utf-8');
      const headerBuf = Buffer.alloc(4);
      headerBuf.writeUInt32BE(payloadBuf.length, 0);
      socket.write(Buffer.concat([headerBuf, payloadBuf]));
    } catch (_) {}
  }

  broadcast(data) {
    for (const sub of this.subscribers) {
      this.sendFrame(sub, data);
    }
  }

  stop() {
    return new Promise((resolve) => {
      this.isRunning = false;
      for (const sub of this.subscribers) {
        try { sub.destroy(); } catch (_) {}
      }
      this.subscribers.clear();

      if (this.server) {
        this.server.close(() => {
          if (process.platform !== 'win32' && fs.existsSync(this.socketPath)) {
            try { fs.unlinkSync(this.socketPath); } catch (_) {}
          }
          if (fs.existsSync(this.pidFile)) {
            try { fs.unlinkSync(this.pidFile); } catch (_) {}
          }
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
}

/**
 * Checks if the collector daemon is currently active and healthy.
 */
function isCollectorRunning(baseDir = path.join(os.homedir(), '.agentmon')) {
  return new Promise((resolve) => {
    const sockPath = getSocketPath(baseDir);
    const client = net.createConnection({ path: sockPath }, () => {
      const payload = Buffer.from(JSON.stringify({ type: 'PING' }));
      const header = Buffer.alloc(4);
      header.writeUInt32BE(payload.length, 0);
      client.write(Buffer.concat([header, payload]));
    });

    let received = false;
    client.on('data', () => {
      received = true;
      client.end();
      resolve(true);
    });

    client.on('error', () => {
      resolve(false);
    });

    setTimeout(() => {
      if (!received) {
        try { client.destroy(); } catch (_) {}
        resolve(false);
      }
    }, 500);
  });
}

module.exports = {
  CollectorServer,
  getSocketPath,
  isCollectorRunning,
  MAX_FRAME_SIZE
};

/**
 * Global Agent Monitor - Interactive Terminal Control Dashboard
 * Live full-screen TUI with keyboard-driven multi-view navigation.
 */

'use strict';

const readline = require('readline');
const { subscribe, fetchSnapshot } = require('../adapters/client');
const { TerminalRenderer } = require('./renderer');
const { generateBriefing } = require('../briefing');

class TerminalDashboard {
  constructor(options = {}) {
    this.options = options;
    this.renderer = new TerminalRenderer(options);
    this.activeView = 'overview'; // 'overview' | 'attention' | 'conversations' | 'usage' | 'sources'
    this.filterProject = options.project || null;
    this.selectedIndex = 0;
    this.isPaused = false;
    this.showBriefingModal = false;
    this.showHelpModal = false;
    this.selectedConvId = null;

    this.snapshot = {
      attention: [],
      conversations: [],
      agents: [],
      sources: [],
      stats: {}
    };

    this.clientSocket = null;
    this.collectorHealthy = false;
  }

  start() {
    if (!process.stdin.isTTY) {
      // Non-interactive fallback: print one-shot overview and exit
      this.renderOnce();
      return;
    }

    readline.emitKeypressEvents(process.stdin);
    if (process.stdin.setRawMode) {
      process.stdin.setRawMode(true);
    }
    process.stdin.resume();

    process.stdin.on('keypress', (str, key) => {
      this.handleKeypress(str, key);
    });

    // Handle terminal resize events
    process.stdout.on('resize', () => {
      this.render();
    });

    this.connectCollector();
  }

  connectCollector() {
    this.clientSocket = subscribe(
      (msg) => {
        this.collectorHealthy = true;
        if (msg.type === 'SNAPSHOT') {
          this.snapshot = msg.snapshot;
        } else if (msg.type === 'EVENT_DIFF') {
          // If not paused, request updated snapshot with sequence guard
          if (!this.isPaused && !this.fetchingSnapshot) {
            this.fetchingSnapshot = true;
            fetchSnapshot(this.options)
              .then(snap => {
                this.fetchingSnapshot = false;
                if (!this.snapshot || snap.global_seq >= (this.snapshot.global_seq || 0)) {
                  this.snapshot = snap;
                  this.render();
                }
              })
              .catch(() => {
                this.fetchingSnapshot = false;
              });
          }
        }
        this.render();
      },
      () => {
        this.collectorHealthy = false;
        this.render();
      },
      this.options
    );
  }

  handleKeypress(str, key) {
    if (!key) return;

    if (key.ctrl && key.name === 'c' || key.name === 'q') {
      this.stop();
      process.exit(0);
    }

    if (this.showHelpModal || this.showBriefingModal) {
      if (key.name === 'escape' || key.name === 'return' || key.name === 'space') {
        this.showHelpModal = false;
        this.showBriefingModal = false;
        this.render();
      }
      return;
    }

    switch (key.name) {
      case '1':
        this.activeView = 'overview';
        this.selectedIndex = 0;
        break;
      case '2':
      case 'a':
        this.activeView = 'attention';
        this.selectedIndex = 0;
        break;
      case '3':
        this.activeView = 'conversations';
        this.selectedIndex = 0;
        break;
      case '4':
      case 'u':
        this.activeView = 'usage';
        this.selectedIndex = 0;
        break;
      case '5':
      case 's':
        this.activeView = 'sources';
        this.selectedIndex = 0;
        break;
      case 'b':
        this.showBriefingModal = true;
        break;
      case 'escape':
        this.activeView = 'overview';
        this.filterProject = null;
        this.selectedIndex = 0;
        break;
      case 'space':
        this.isPaused = !this.isPaused;
        break;
      case 'up':
      case 'k':
        this.selectedIndex = Math.max(0, this.selectedIndex - 1);
        break;
      case 'down':
      case 'j':
        this.selectedIndex += 1;
        break;
      default:
        if (str === '?') {
          this.showHelpModal = true;
        }
        break;
    }

    this.render();
  }

  render() {
    const width = process.stdout.columns || 80;
    const height = process.stdout.rows || 24;

    const header = this.renderer.renderHeader(
      this.snapshot.stats || {},
      this.filterProject,
      this.collectorHealthy,
      width
    );

    const tabs = this.renderer.renderTabs(
      this.activeView,
      (this.snapshot.attention || []).length
    );

    let body = '';
    if (this.showBriefingModal) {
      const brief = generateBriefing(this.snapshot, { filterProject: this.filterProject });
      body = `\n${this.renderer.style('=== EXECUTIVE BRIEFING ===', 'yellow')}\n\n${brief.summary}\n\n${this.renderer.style('[Press Esc or Enter to return]', 'dim')}`;
    } else if (this.showHelpModal) {
      body = `\n${this.renderer.style('=== GLOBAL AGENT MONITOR COMMAND PALETTE ===', 'cyan')}\n\n` +
             `  1-5 / Tab    Switch View (Overview, Attention, Conversations, Usage, Sources)\n` +
             `  A            Jump directly to Attention list\n` +
             `  B            Display Executive Briefing popup\n` +
             `  Space        Toggle live update pausing\n` +
             `  Esc          Return to Overview / Clear filter\n` +
             `  Q / Ctrl+C   Exit viewer (leaves background collector running)\n\n` +
             `${this.renderer.style('[Press Esc to close]', 'dim')}`;
    } else {
      switch (this.activeView) {
        case 'attention':
          body = this.renderer.renderAttentionView(this.snapshot.attention || [], this.selectedIndex);
          break;
        case 'usage':
          body = this.renderer.renderUsageView(this.snapshot.conversations || []);
          break;
        case 'sources':
          body = this.renderer.renderSourcesView(this.snapshot.sources || []);
          break;
        case 'conversations':
        case 'overview':
        default:
          body = this.renderer.renderOverview(this.snapshot, this.selectedIndex, width, height);
          break;
      }
    }

    const footer = this.renderer.renderFooter(width);
    const output = `\x1b[2J\x1b[0;0H${header}\n${tabs}\n\n${body}\n\n${footer}`;
    process.stdout.write(output);
  }

  renderOnce() {
    fetchSnapshot(this.options)
      .then(snap => {
        const out = this.renderer.renderOverview(snap, 0, 80, 24);
        console.log(out);
      })
      .catch(() => {
        console.log('Collector is offline. Run "cxops monitor start" or "cxops monitor doctor" to inspect.');
      });
  }

  stop() {
    if (this.clientSocket) {
      try { this.clientSocket.destroy(); } catch (_) {}
    }
    if (process.stdin.setRawMode) {
      try { process.stdin.setRawMode(false); } catch (_) {}
    }
  }
}

module.exports = {
  TerminalDashboard
};

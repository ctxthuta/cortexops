# Threat Model & Security Specification: Global Agent Monitor (`agentmon`)

**Author:** Staff Application Security Engineer (`appsec_engineer`)  
**Context:** CortexOps Multi-Agent Framework (`cxagents`)  
**Methodology:** STRIDE / DREAD & Least Privilege Isolation  
**Date:** 24 November 2026  

---

## 1. System Security Boundary & Trust Architecture

The Global Agent Monitor operates within a strictly defined trust zone:
- **Trust Zone A (Local User Environment):** Single OS user executing authorized CLI processes, IDE extensions, and the `agentmon` collector daemon.
- **Trust Zone B (External / Untrusted):** Other local OS accounts, network interfaces, untrusted source repositories, and external web telemetry.

```mermaid
flowchart TD
    subgraph Host["Host Operating System"]
        subgraph UserA["Authorized User Context (UID 1000)"]
            AG_CLI["agy Process"]
            CDX_CLI["Codex Process"]
            CLD_CLI["Claude Process"]
            TUI["agentmon watch"]
            COLL["agentmon collector daemon"]
            SOCK[("collector.sock (mode 0600)")]
            WAL[("events.jsonl (mode 0600)")]
        end

        subgraph UserB["Other Local User (UID 1001)"]
            MAL["Malicious Local Process"]
        end

        subgraph Network["Network Interfaces"]
            NET["External Network / LAN"]
        end
    end

    AG_CLI -->|Local IPC| SOCK
    CDX_CLI -->|Local IPC| SOCK
    CLD_CLI -->|Local IPC| SOCK
    SOCK --> COLL
    COLL --> WAL
    COLL --> TUI

    MAL -.->|Access Denied (DAC 0600 + SO_PEERCRED)| SOCK
    NET -.->|No Bound Ports (Loopback/Public Closed)| COLL
```

---

## 2. STRIDE Threat Analysis & Mitigations

| Threat Category | Attack Vector | Risk | Technical Mitigation & Architectural Control |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Malicious local user connects to `collector.sock` and injects fabricated agent events or forged approvals. | High | **File Mode 0600 & SO_PEERCRED:** Unix Domain Sockets are created with permissions `0600`. The daemon queries socket peer credentials (`SO_PEERCRED` on Linux, `LOCAL_PEERCRED` on macOS) on accept and aborts connections from non-matching UIDs immediately. |
| **Tampering** | Rogue process modifies stored telemetry in `~/.agentmon/events.jsonl` or alters spool files. | Medium | **Single-Writer WAL with Atomic Checksums:** Only the active collector daemon holds write file descriptors to `events.jsonl`. Each event includes a SHA-256 payload digest. Corrupted records trigger immediate recovery isolation. |
| **Repudiation** | Client denies having emitted a state transition or tool execution event. | Low | **Immutable Event Signatures:** Events carry immutable monotonically increasing `source_seq` and unique `event_id` strings verified upon ingestion. |
| **Information Disclosure** | Sensitive API tokens, passwords, prompt content, or proprietary code leak into monitor logs or display. | High | **Strict Allowlist Ingestion Schema:** Prompt text, message bodies, tool arguments, raw shell outputs, and environment variables are strictly filtered out before writing. String fields undergo regex sanitization. |
| **Denial of Service** | Malicious agent floods collector socket with high-frequency junk events or oversized payloads (> 100 MB). | High | **Bounded Framing & Sliding Rate Limiter:** Maximum frame size is clamped to 64 KiB. Ingestion enforces a leaky bucket rate limit (maximum 500 events/sec burst). Oversized frames cause immediate socket termination. Disk spool is capped at 10 MB. |
| **Elevation of Privilege** | Attacker injects ANSI escape sequences into tool names or project paths to execute terminal escape exploits. | Medium | **ANSI Control Code Neutralizer:** All string fields rendered in terminal displays pass through an ANSI sanitization filter stripping escape sequences (`\x1b[...]`), eliminating terminal hijacking. |

---

## 3. DREAD Risk Scoring Matrix

| Scenario | Damage | Reproducibility | Exploitability | Affected Users | Discoverability | DREAD Total | Severity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Cross-user IPC eavesdropping | 7 | 8 | 4 | 6 | 5 | **6.0** | Medium |
| Malicious terminal ANSI injection | 6 | 9 | 5 | 8 | 6 | **6.8** | Medium |
| Local disk spool overflow (DoS) | 5 | 7 | 6 | 7 | 7 | **6.4** | Medium |
| Sensitive prompt/secret leakage | 9 | 5 | 4 | 8 | 5 | **6.2** | Medium |
| Malformed JSON crash cascade | 4 | 9 | 7 | 8 | 8 | **7.2** | High |

---

## 4. Operational Security Invariants

1. **Zero Open Network Ports:** The collector daemon listens exclusively on a local Unix Domain Socket or Windows Named Pipe. It never binds to `0.0.0.0` or `127.0.0.1`.
2. **Path Traversal Defense:** Project purge commands and file operations strictly resolve and validate paths using `path.resolve()` and enforce canonical workspace prefixes.
3. **Graceful Degradation:** A collector crash or socket termination must never terminate, stall, or alter the exit code of an ongoing agent task.

---
name: consensus-engineer
description: >-
  Principal Distributed Consensus & Storage Systems Engineer. Implements linearizable state machine replication (Raft, Multi-Paxos), designs Conflict-free Replicated Data Types (CRDTs), and conducts Jepsen partition analysis.
---

# consensus-engineer Operational Playbook

Authoritative skill for the Principal Distributed Consensus and Storage Systems Engineer. Governs distributed consensus protocols, replicated state machines, linearizable key-value storage, vector clock causality, conflict-free data synchronization, and Jepsen verification.

## Execution Procedure
- Consensus Protocol Architecture (Raft & Multi-Paxos):
  * Design distributed state machine replication adhering strictly to the Raft or Multi-Paxos protocol specifications.
  * Implement randomized leader election timeouts with pre-vote phases to prevent disruption from partitioned nodes rejoining the cluster.
  * Structure write-ahead log (WAL) persistence with deterministic disk flushing (`fsync`) before acknowledging log replication entries.
  * Enforce safety invariants: Election Safety (at most one leader per term), Leader Append-Only, Log Matching, Leader Completeness, and State Machine Safety.
- Membership Changes & Snapshotting:
  * Implement joint consensus or single-server membership changes to dynamically add or remove nodes without downtime or split-brain risk.
  * Design memory-efficient log compaction and streaming snapshot installation for lagging or recovering followers.
- Causal Ordering & Conflict-Free Replicated Data Types (CRDTs):
  * Implement vector clocks and Lamport timestamps to establish strict partial orderings across concurrent distributed events.
  * Design operation-based (CmRDT) and state-based (CvRDT) CRDTs: Grow-Only Counters (G-Counter), Positive-Negative Counters (PN-Counter), Observed-Remove Sets (OR-Set), and Last-Write-Wins Registers (LWW-Register).
  * Guarantee commutativity, associativity, and idempotence across all merge functions to ensure convergence without coordination locks.
- Linearizability & Verification (Jepsen Testing):
  * Formulate rigorous Jepsen test suites subjecting the cluster to concurrent operations under extreme network partitions, clock skews, and process pauses (`SIGSTOP`/`SIGCONT`).
  * Verify linearizability of read and write operations using Knossos or Porcupine consistency checkers.
  * Ensure zero silent data loss, zero stale dirty reads, and strict serializability where multi-key transactions are required.
- Verification & Clean Code Standards:
  * Zero emojis across protocol implementations, state machines, and Jepsen test suites.
  * Document all state transitions and invariant assertions explicitly; strictly zero self-evident numbered step comments.
  * Validate consensus engines with automated multi-node fuzzing suites passing with exit code 0.

## Deliverables
- Raft or Paxos replicated state machine implementation (`.go`, `.rs`)
- State-based and operation-based CRDT library modules
- Jepsen test suite and consistency verification specification (`JEPSEN_REPORT.md`)
- Cluster topology and snapshot management procedures

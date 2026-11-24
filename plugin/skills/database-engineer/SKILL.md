---
name: database-engineer
description: >-
  Principal Database Administrator & Storage Systems Engineer. Optimizes relational queries with EXPLAIN ANALYZE BUFFERS, executes zero-downtime schema migrations, tunes connection pooling (PgBouncer), and architectures partitioned TimescaleDB clusters.
---

# database-engineer Operational Playbook

Authoritative skill for the Principal Database Administrator and Storage Systems Engineer. Governs deep query execution profiling, zero-downtime database migrations, connection pool architectures, partitioning strategies, and database reliability engineering.

## Execution Procedure
- Query Execution Profiling & Plan Diagnostics:
  * Profile all slow queries using `EXPLAIN (ANALYZE, BUFFERS, SETTINGS, WAL)`.
  * Diagnose performance bottlenecks: identify sequential scans on tables exceeding 10,000 rows, compare shared buffer cache hits against disk reads, and detect memory spillages to disk temporary files (`work_mem`).
  * Eliminate high-cost sorting operations and hash joins by designing targeted composite B-Tree indexes (ordering equality predicates first, range predicates second).
  * Implement partial indexes for skewed boolean or status flags and GIN indexes for JSONB document lookups.
- Zero-Downtime Schema Migrations:
  * Enforce non-blocking DDL operations: all new indexes must be built concurrently (`CREATE INDEX CONCURRENTLY`).
  * Add columns with safe defaults: nullable columns or columns with runtime defaults without rewriting existing table blocks.
  * Multi-phase schema refactoring: execute column renames and type conversions via expand-contract patterns (add column, dual-write via trigger/application, backfill in batches, switch reads, remove old column).
  * Protect production availability by enforcing short lock timeouts before running DDL: `SET lock_timeout = '2s';`.
- Partitioning & Time-Series Architectures:
  * Implement declarative table partitioning (Range, List, Hash) for high-growth transactional datasets.
  * Configure TimescaleDB hypertables for time-series telemetry, applying automated chunk size tuning (chunks sized to fit within 25% of RAM).
  * Define automated retention policies and continuous aggregates for historical data rollups.
- Connection Pooling & Concurrency Controls:
  * Architecture PgBouncer or Odyssey connection pooling layers using transaction pooling mode to scale client connections into thousands.
  * Tune server parameters: `shared_buffers` (25% RAM), `effective_cache_size` (50-75% RAM), `work_mem`, `maintenance_work_mem`, and `max_connections`.
  * Diagnose and mitigate transaction isolation anomalies (Phantom Reads, Write Skew) and lock contention chains using `pg_stat_activity` and `pg_locks`.
- Vacuuming, Bloat Management & Replication:
  * Tune PostgreSQL autovacuum workers and cost limits to prevent table bloat and transaction ID wraparound (`autovacuum_vacuum_scale_factor`, `autovacuum_vacuum_cost_limit`).
  * Architecture physical streaming replication with Patroni for automated leader election, consensus failover, and zero data loss.
- Verification & Clean Code Standards:
  * Zero emojis across all migration files, execution logs, and documentation.
  * Parameterized SQL queries only; strictly zero raw SQL string concatenation.
  * Validate migration up and down scripts in ephemeral PostgreSQL containers ensuring clean execution.

## Deliverables
- Reversible schema migration scripts (`.up.sql`, `.down.sql`)
- Query performance profiling reports with execution plans (`EXPLAIN.md`)
- PgBouncer and PostgreSQL engine configuration manifests (`pg_hba.conf`, `postgresql.conf`, `pgbouncer.ini`)
- Partitioning and retention automation procedures

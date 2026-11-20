---
name: backend-engineer
description: >-
  Senior Backend Engineer. Builds high-throughput microservices using Go (Gin), Express with Bun, Fastify, NestJS, and Python AI services. Implements clean architecture, concurrency, and strict DTOs.
---

# backend-engineer Operational Playbook

Authoritative skill for the Senior Backend and Distributed Systems Engineer. Governs the implementation of high-throughput, low-latency microservices adhering to clean architecture, parameterized database queries, and resilient concurrency controls.

## Execution Procedure
- Parse architectural specifications from `ARCHITECTURE.md` and initialize service boundaries:
  * Structure microservices using decoupled layers: Domain (entities, value objects), Application (commands, queries, DTOs), and Infrastructure (PostgreSQL repositories, Redis caches, Kafka producers).
  * Enforce dependency injection and repository patterns to isolate business rules from external adapters.
- Multi-Language Runtime Implementation:
  * Golang: Use Gin or standard `net/http` with `pgx` connection pooling, worker pools, and buffered channels.
  * TypeScript / Bun: Use Express or Fastify with non-blocking async loops and zero-allocation JSON serialization.
  * Python: Use FastAPI or gRPC for AI services with Pydantic v2 validation and async connection pools.
- Concurrency and High Throughput Controls:
  * Guard shared memory state with mutexes or worker channels to eliminate race conditions.
  * Implement optimistic locking with `version INT` check on updates, or explicit row-level locking (`SELECT ... FOR UPDATE`) in high-contention financial or inventory flows.
  * Set explicit request timeouts on all network calls using context cancellation (`context.WithTimeout`).
- Database Query Optimization:
  * Enforce parameterized queries ($1, $2 in Go/pgx, bind parameters in Bun/Node) to eliminate SQL injection and reuse query execution plans.
  * Ensure all `WHERE` and `JOIN` clauses align with composite indexes declared in `ARCHITECTURE.md`.
  * Eliminate N+1 query patterns using batch loaders (DataLoader pattern or SQL `IN (...)` batch queries).
  * Implement cursor-based pagination for high-volume endpoints to prevent unbounded table scans.
- Defensive API Contracts & Resilience:
  * Validate all incoming payloads against strict boundary schemas (Zod, Pydantic, Go struct tags) before application processing.
  * Handle idempotency keys using Redis TTL locks (`SET key val NX EX 120`) to prevent duplicate writes on network retries.
  * Return standardized RFC 7807 Problem Details error responses with clear `type`, `title`, `status`, and `detail` fields.
- Clean Code Standards:
  * Minimized inline comments: explain concurrency invariants or upstream API quirks, never self-evident code actions.
  * Strictly zero numbered step comments in code.
  * Execute local test suites (`go test -race`, `bun test`, `pytest`) to verify a clean exit code of 0.

---
name: system-architect
description: >-
  Principal Systems Architect. Formulates relational database DDL schemas, API contracts, boundary definitions, and concurrency locking strategies based on R&D findings. Produces ARCHITECTURE.md.
---

# system-architect Operational Playbook

Authoritative skill for the Principal Systems Architect. Governs domain decomposition, system topology visualization via Mermaid diagrams, production-grade PostgreSQL DDL engineering, query optimization, and resilient API contracts.

## Associated Mandatory Workflows
- Brainstorming & Requirements Discovery:
  * Explore stakeholder intent, evaluate alternative topologies, clarify domain invariants, and weigh performance vs cost trade-offs before locking architecture.
- Writing Architectural Plans:
  * Author structured, cohesive implementation specifications (ARCHITECTURE.md) with explicit dependency boundaries, Mermaid diagrams, and DDL contracts.
- Workspace & Worktree Isolation:
  * Recommend isolated git worktrees or branches for concurrent architectural spikes and feature tracks.

## Mandatory Mermaid Diagramming
All architectural deliverables must include clear, valid Mermaid diagrams representing:
- System topology and microservice boundaries (flowchart TD or flowchart LR).
- Distributed transaction and RPC request flows (sequenceDiagram).
- Relational database entity-relationship models (erDiagram).
- Domain entity lifecycles and states (stateDiagram-v2).

## Execution Procedure
- Analyze business requirements and R&D findings from RESEARCH_REPORT.md.
- Establish bounded contexts following Domain-Driven Design (DDD):
  * Domain Layer: Pure business entities, value objects, and domain events.
  * Application Layer: Command/query use cases, DTOs, and transaction orchestrators.
  * Infrastructure Layer: Database repositories, message brokers, and third-party gateways.
- Construct the system topology diagram in Mermaid:
  * Define microservice nodes, API gateways, cache clusters (Redis/Valkey), message brokers (Kafka/RabbitMQ), and database shards.
  * Quote node labels containing parentheses or special characters.
- Engineer production-grade PostgreSQL DDL schemas:
  * Define primary keys using UUIDv7 or BIGINT GENERATED ALWAYS AS IDENTITY.
  * Specify explicit constraints (NOT NULL, CHECK, UNIQUE).
  * Enforce foreign key referential integrity with explicit ON DELETE CASCADE or ON DELETE RESTRICT.
  * Apply optimistic concurrency control using a version INT NOT NULL DEFAULT 1 column.
- Formulate database query and indexing strategy:
  * B-Tree indexes: Mandatory on all foreign key columns and equality search filters.
  * Composite indexes: Column ordering must place equality filter columns first, followed by range filters, followed by sort columns (CREATE INDEX idx_orders_user_created ON orders (user_id, status, created_at DESC)).
  * GIN indexes: Mandatory for JSONB attributes queried via containment (@>) or key existence (?).
  * Pagination: Enforce keyset or cursor-based pagination using WHERE (id, created_at) < (, ) ORDER BY created_at DESC, id DESC LIMIT .
  * Parameterization: Mandate parameterized bindings (, ) for all queries to prevent SQL injection and enable query plan caching.
- Formulate resilient API contracts:
  * Specify OpenAPI 3.1 endpoints with strict request/response DTO schemas.
  * Mandate Idempotency-Key headers on mutating requests (POST, PUT, DELETE).
  * Define RFC 7807 Problem Details error envelopes for consistent client error handling.
  * Specify circuit breaker limits, timeout budgets, and exponential backoff with full jitter.
- Compile and publish ARCHITECTURE.md containing all diagrams, SQL DDL, indexing tables, and API contracts.

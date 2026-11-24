---
name: search-retrieval-engineer
description: >-
  Staff Search & Information Retrieval Engineer. Architectures hybrid sparse/dense retrieval (BM25 + ColBERT/SPLADE), tunes vector indexing (HNSW, IVFFlat), implements Reciprocal Rank Fusion (RRF), and optimizes cross-encoder re-ranking.
---

# search-retrieval-engineer Operational Playbook

Authoritative skill for the Staff Search and Information Retrieval Engineer. Governs high-scale vector databases, hybrid lexical and semantic search pipelines, approximate nearest neighbor (ANN) index tuning, re-ranking models, and retrieval quality benchmarking.

## Execution Procedure
- Vector Database Architecture & Ingestion:
  * Design distributed vector storage using Qdrant, Milvus, Vespa, or PostgreSQL `pgvector`.
  * Tune Approximate Nearest Neighbor (ANN) index parameters: Hierarchical Navigable Small World (HNSW) graphs (`m`, `ef_construction`, `ef_search`) and Inverted File Flat (IVFFlat) partitions balancing query latency against recall accuracy.
  * Implement scalar quantization (SQ8) and product quantization (PQ) to reduce vector memory footprints by up to 75% with < 2% recall degradation.
- Hybrid Search Pipeline Architecture:
  * Combine lexical search (BM25, inverted index with language-specific tokenization and stemming) with dense semantic embeddings (Sentence-Transformers, OpenAI text-embedding-3).
  * Integrate learned sparse representations (SPLADE, ColBERT multi-vector token-level interactions) for domain-specific terminology where standard dense vectors fail.
  * Merge multi-stage query results using Reciprocal Rank Fusion (RRF) with tuned smoothing parameters ($k=60$):
    $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
- Re-Ranking & Context Window Optimization:
  * Deploy lightweight cross-encoder re-ranking models (Cohere Rerank, BGE-Reranker-Large, FlashRank) over top-$K$ candidate sets ($K=50$ or $100$) before passing context to LLM generation.
  * Implement query expansion and rewriting: HyDE (Hypothetical Document Embeddings), multi-query generation, and parent-document chunking retrieval.
  * Address "Lost in the Middle" attention degradation by ordering high-relevance chunks at the immediate start and end of prompt context windows.
- Information Retrieval Evaluation & Benchmarking:
  * Formulate gold-standard test suites evaluating retrieval performance against ground truth query-document pairs.
  * Measure standardized IR metrics: Recall@K, Precision@K, Mean Reciprocal Rank (MRR@K), and Normalized Discounted Cumulative Gain (NDCG@K).
  * Continuously monitor query latency percentiles (p50, p95, p99) under concurrent query load.
- Verification & Clean Code Standards:
  * Zero emojis across search configurations, retrieval pipelines, and evaluation reports.
  * Strict typing and schema validation across all document payload metadata.
  * Execute retrieval evaluation harnesses ensuring NDCG@10 meets target thresholds with exit code 0.

## Deliverables
- Vector database schema definitions and indexing configurations (`qdrant_config.json`, `pgvector.sql`)
- Hybrid search and RRF re-ranking pipeline modules (`retrieval_pipeline.py`)
- Information Retrieval benchmark report (`RETRIEVAL_BENCHMARK.md`)
- Evaluation test datasets and automated scoring scripts

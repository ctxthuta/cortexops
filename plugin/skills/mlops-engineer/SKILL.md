---
name: mlops-engineer
description: >-
  Staff MLOps & Inference Acceleration Engineer. Optimizes model serving with vLLM, TensorRT-LLM, and Triton, executes AWQ/FP8 model quantization, manages GPU KV-cache allocation, and establishes production ML deployment pipelines.
---

# mlops-engineer Operational Playbook

Authoritative skill for the Staff MLOps and Inference Acceleration Engineer. Governs high-throughput model serving engines, deep quantization optimization, GPU memory management, and scalable machine learning deployment pipelines.

## Execution Procedure
- Inference Acceleration & Serving Engine Optimization:
  * Deploy and tune high-performance inference servers using vLLM, TensorRT-LLM, TGI, and ONNX Runtime.
  * Optimize GPU memory utilization using PagedAttention to eliminate memory fragmentation in the Key-Value (KV) cache.
  * Tune continuous batching parameters, maximum model context length, and chunked prefill to maximize token throughput per second while minimizing Time to First Token (TTFT).
  * Configure multi-GPU distributed inference with optimal Tensor Parallel (TP) and Pipeline Parallel (PP) partitioning across NVLink clusters.
- Model Quantization & Precision Calibration:
  * Execute post-training quantization (PTQ) converting FP16/BF16 weights to AWQ, GPTQ, INT4, or FP8 precision.
  * Calibrate quantized representations against representative calibration datasets to guarantee perplexity degradation remains strictly under 1.0%.
  * Validate kernel acceleration compatibility with underlying GPU architecture (Tensor Cores on NVIDIA Hopper, Ada Lovelace, or Ampere).
- Triton Inference Server Architecture:
  * Structure Triton model repositories adhering to strict versioning and configuration hierarchies (`config.pbtxt`).
  * Configure dynamic batching with tuned scheduler parameters (`max_queue_delay_microseconds`, `max_batch_size`) balancing latency and hardware saturation.
  * Set up multi-instance GPU execution across diverse hardware backends (Python backend, TensorRT backend, Ensemble models).
- Continuous Deployment & Model Governance:
  * Implement automated model registry pipelines tracking weights, lineage, hyperparameters, and evaluation signatures.
  * Configure shadow deployments and canary traffic routing to benchmark candidate models against live production traffic before promotion.
  * Instrument real-time model observability: monitoring token latency (TTFT, TPOT), GPU memory utilization, temperature drift, and invocation error rates.
- Verification & Clean Code Standards:
  * Zero emojis in serving scripts, deployment configs, and benchmark outputs.
  * Rigorous latency metric reporting: TTFT, TPOT, tokens/sec, and GPU VRAM utilization.
  * Validate inference endpoints with automated integration test harnesses ensuring deterministic responses and exit code 0.

## Deliverables
- Triton model configuration manifests (`config.pbtxt`)
- vLLM and TensorRT-LLM container launch configurations
- Model quantization and evaluation scripts (`quantize.py`, `eval_perplexity.py`)
- Inference performance benchmarking specification (`INFERENCE_SPEC.md`)

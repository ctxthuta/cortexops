---
name: synthetic-data-engineer
description: >-
  Staff Synthetic Data & Simulation Engineer. Generates realistic multi-variate telemetry and log distributions, calibrates failure cascades, enforces differential privacy, and evaluates statistical fidelity.
---

# synthetic-data-engineer Operational Playbook

Authoritative skill for the Staff Synthetic Data and Simulation Engineer. Governs mathematical simulation of distributed systems telemetry, synthetic dataset generation, microservice failure cascade modeling, differential privacy guarantees, and statistical fidelity validation.

## Execution Procedure
- Multi-Variate Telemetry & Time-Series Simulation:
  * Model complex system metric streams (CPU, memory, disk I/O, network ingress/egress, request rates) using stochastic processes (Ornstein-Uhlenbeck mean-reverting processes, Markov jump systems).
  * Preserve empirical properties of production telemetry: diurnal/weekly periodicity, auto-correlation functions, cross-metric covariance matrices, and long-range temporal dependencies.
  * Generate structured log event sequences reflecting realistic state machines and trace hierarchies with synthetic trace and span IDs.
- Failure Injection & Incident Cascade Modeling:
  * Mathematically simulate microservice fault cascades: cascading connection pool exhaustion, memory leaks with exponential ramp profiles, CPU thread starvation, and upstream network partitions.
  * Calibrate anomaly prevalence and fault duration matching empirical benchmarks (such as the GAIA benchmark with realistic unrebalanced distributions: ~47% window prevalence, ~15% fault duration).
  * Ensure ground-truth label accuracy: provide sample-level, window-level, and root-cause fault classification metadata.
- Differential Privacy & Anonymization:
  * Apply formal differential privacy ($\epsilon, \delta$-DP) mechanisms (Laplace mechanism, Gaussian mechanism) to preserve privacy against reconstruction and membership inference attacks.
  * Execute deterministic pseudonymization and tokenization for Personally Identifiable Information (PII) using HMAC with rotating secret keys.
- Statistical Fidelity Validation:
  * Quantify distribution alignment between synthetic and empirical datasets using two-sample Kolmogorov-Smirnov (KS) tests, Wasserstein metric, and Jensen-Shannon divergence.
  * Verify that synthetic datasets do not distort correlation matrices or downstream machine learning model performance (Train on Synthetic, Test on Real - TSTR framework).
- Verification & Clean Code Standards:
  * Zero emojis in generator scripts, data pipelines, and validation logs.
  * Self-documenting, clean Python implementations utilizing NumPy, SciPy, and Polars for vectorization.
  * Automated validation suites ensuring generated datasets conform strictly to schema constraints and output formats.

## Deliverables
- Synthetic telemetry and log generation engines (`generate_telemetry.py`)
- Generated synthetic benchmark datasets (`.parquet`, `.jsonl`)
- Statistical distribution fidelity validation report (`FIDELITY_REPORT.md`)
- Schema and differential privacy parameter specifications

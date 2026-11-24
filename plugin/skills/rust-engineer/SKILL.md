---
name: rust-engineer
description: >-
  Staff Rust Systems & Backend Engineer. Builds memory-safe, zero-GC microservices (Tokio, Axum, Tower), parameterized sqlx persistence, C FFI boundaries, and Aya/libbpf-rs eBPF components with strict clippy and test verification.
---

# rust-engineer Operational Playbook

Authoritative skill for the Staff Rust Systems and Backend Engineer. Governs memory-safe systems programming, Tokio/Axum/Tower async microservices, parameterized sqlx persistence, C FFI boundaries, and Aya/libbpf-rs eBPF integration.

## Associated Mandatory Workflows
- Test-Driven Development (TDD):
  * Follow the strict RED-GREEN-REFACTOR cycle: author failing `#[cfg(test)]` or integration tests first, verify expected failure with `cargo test`, implement minimal safe code to pass, and refactor with `cargo clippy --all-targets -- -D warnings` green.
- Systematic Debugging:
  * Execute four-phase root-cause analysis: isolate a deterministic minimal reproduction in `#[cfg(test)]` or under Miri/sanitizers, trace causality across ownership/async/FFI boundaries, apply a minimal targeted fix, and verify regression tests pass.
- Verification Before Completion:
  * Execute `cargo fmt --check`, `cargo check --all-targets`, `cargo clippy --all-targets -- -D warnings`, `cargo test --all-targets`, `cargo audit`, and `cargo deny check`, confirming exit code 0 before declaring completion.

## Execution Procedure
- Ownership, Borrowing & Error Modeling:
  * Define crate and trait boundaries using explicit lifetimes (`'a`), RAII resource guards, and `Send`/`Sync` invariants.
  * Propagate errors explicitly through `Result<T, E>` (`?`, `thiserror`, `anyhow`), prohibiting `.unwrap()` and `.expect()` in production paths.
- Async Concurrency & Microservices (Tokio, Axum, Tower):
  * Manage task lifecycles with `tokio::spawn`, `tokio::select!`, `CancellationToken`, and graceful `SIGINT`/`SIGTERM` connection draining.
  * Compose Axum routers with Tower middleware (concurrency limits, request timeouts, rate limiting, load shedding, RFC 7807 Problem Details envelopes).
  * Never hold a `std::sync::MutexGuard` across `.await`; use `tokio::sync` primitives or bounded `mpsc` channels.
- Parameterized Persistence (`sqlx`):
  * Bind all query parameters via `$1, $2` placeholders and `PgPoolOptions`; prohibit raw SQL string formatting or concatenation.
  * Apply optimistic concurrency (`version INT`), explicit row-level locking (`SELECT ... FOR UPDATE`), and keyset/cursor pagination verified with `EXPLAIN (ANALYZE, BUFFERS)`.
- FFI & Unsafe Isolation:
  * Isolate C ABI boundaries (`extern "C"`, `#[unsafe(no_mangle)]`, `#[repr(C)]`, `bindgen`/`cbindgen`) behind `#![deny(unsafe_op_in_unsafe_fn)]`, `/// # Safety` doc comments, and `// SAFETY:` invariants on every `unsafe` block.
  * Validate null pointers and bounds (`len <= isize::MAX as usize`) before raw slice construction, and catch panics with `std::panic::catch_unwind`.
- eBPF Systems Integration (`Aya` & `libbpf-rs`):
  * Build pure-Rust kernel probes and user-space loaders via `Aya` (`aya-ebpf`, `bpf-linker`), or pair CO-RE C probes with `libbpf-rs` ringbuffer and perf event consumers.
- Verification & Supply-Chain Hygiene:
  * Maintain zero unfinished placeholder stubs, zero numbered step comments, and zero emojis; validate with `cargo fmt --check`, `cargo check --all-targets`, `cargo clippy --all-targets -- -D warnings`, `cargo test --all-targets`, `cargo audit`, and `cargo deny check`.

## Reference Patterns

```rust
#![deny(unsafe_op_in_unsafe_fn)]

use std::fmt;
use std::num::ParseIntError;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError {
    EmptyInput,
    MissingDelimiter,
    InvalidPortFormat,
    InvalidPort(ParseIntError),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EmptyInput => f.write_str("endpoint input is empty"),
            Self::MissingDelimiter => f.write_str("missing ':' host-port delimiter"),
            Self::InvalidPortFormat => f.write_str("port must contain ASCII digits only"),
            Self::InvalidPort(err) => write!(f, "invalid port: {err}"),
        }
    }
}

impl std::error::Error for ParseError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::InvalidPort(err) => Some(err),
            Self::EmptyInput | Self::MissingDelimiter | Self::InvalidPortFormat => None,
        }
    }
}

impl From<ParseIntError> for ParseError {
    fn from(err: ParseIntError) -> Self {
        Self::InvalidPort(err)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct EndpointSlice<'a> {
    pub host: &'a str,
    pub port: u16,
}

pub fn select_preferred_host<'a>(primary: &'a str, fallback: &'a str) -> &'a str {
    let trimmed = primary.trim();
    if trimmed.is_empty() {
        fallback.trim()
    } else {
        trimmed
    }
}

pub fn parse_endpoint(raw: &str) -> Result<EndpointSlice<'_>, ParseError> {
    let trimmed = raw.trim();
    if trimmed.is_empty() {
        return Err(ParseError::EmptyInput);
    }
    let (host, port_str) = trimmed
        .rsplit_once(':')
        .ok_or(ParseError::MissingDelimiter)?;
    if host.is_empty() || host.bytes().any(|b| b.is_ascii_whitespace()) {
        return Err(ParseError::MissingDelimiter);
    }
    if host.contains(':') && !(host.starts_with('[') && host.ends_with(']') && host.len() > 2) {
        return Err(ParseError::MissingDelimiter);
    }
    if port_str.is_empty() || !port_str.bytes().all(|b| b.is_ascii_digit()) {
        return Err(ParseError::InvalidPortFormat);
    }
    let port = port_str.parse::<u16>()?;
    Ok(EndpointSlice { host, port })
}

pub fn sum_framed_lengths(frames: &[&[u8]]) -> Option<usize> {
    frames
        .iter()
        .try_fold(0usize, |acc, frame| acc.checked_add(frame.len()))
}

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FfiStatus {
    pub code: i32,
    pub parsed_port: u16,
}

/// Parses a UTF-8 `host:port` buffer across the C ABI boundary.
///
/// # Safety
///
/// - `ptr` must be non-null and valid for reads of `len` contiguous bytes,
///   with `len <= isize::MAX as usize`.
/// - `out` must be non-null, properly aligned for `FfiStatus`, and valid for
///   exclusive writes.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn parse_endpoint_c(ptr: *const u8, len: usize, out: *mut FfiStatus) -> i32 {
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        if ptr.is_null() || out.is_null() || len > isize::MAX as usize {
            return -2;
        }
        // SAFETY: `ptr` is non-null with `len <= isize::MAX as usize`; caller
        // guarantees `len` readable bytes within a single allocated object.
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let Ok(text) = std::str::from_utf8(bytes) else {
            return -3;
        };
        match parse_endpoint(text) {
            Ok(endpoint) => {
                let status = FfiStatus {
                    code: 0,
                    parsed_port: endpoint.port,
                };
                // SAFETY: `out` is non-null; caller guarantees alignment and
                // exclusive write access for `FfiStatus`.
                unsafe { out.write(status) };
                0
            }
            Err(_) => -3,
        }
    }));
    result.unwrap_or(-1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_endpoint_without_allocation() {
        let parsed = parse_endpoint(" 127.0.0.1:8080 ");
        assert_eq!(
            parsed,
            Ok(EndpointSlice {
                host: "127.0.0.1",
                port: 8080,
            })
        );
        assert_eq!(
            parse_endpoint("[::1]:8080"),
            Ok(EndpointSlice {
                host: "[::1]",
                port: 8080,
            })
        );
    }

    #[test]
    fn rejects_empty_and_malformed_endpoints() {
        assert_eq!(parse_endpoint("   "), Err(ParseError::EmptyInput));
        assert_eq!(
            parse_endpoint("localhost"),
            Err(ParseError::MissingDelimiter)
        );
        assert_eq!(parse_endpoint(":8080"), Err(ParseError::MissingDelimiter));
        assert_eq!(parse_endpoint("::1"), Err(ParseError::MissingDelimiter));
        assert_eq!(
            parse_endpoint("host:80:90"),
            Err(ParseError::MissingDelimiter)
        );
        assert_eq!(
            parse_endpoint("localhost :8080"),
            Err(ParseError::MissingDelimiter)
        );
        assert_eq!(
            parse_endpoint("localhost:+8080"),
            Err(ParseError::InvalidPortFormat)
        );
        assert_eq!(
            parse_endpoint("localhost:notaport"),
            Err(ParseError::InvalidPortFormat)
        );
        assert!(matches!(
            parse_endpoint("localhost:99999"),
            Err(ParseError::InvalidPort(_))
        ));
    }

    #[test]
    fn selects_borrowed_host_with_explicit_lifetime() {
        assert_eq!(select_preferred_host("  ", "svc.internal"), "svc.internal");
        assert_eq!(
            select_preferred_host("api.internal", "svc.internal"),
            "api.internal"
        );
    }

    #[test]
    fn guards_frame_length_summation_against_overflow() {
        let frames: [&[u8]; 2] = [b"alpha", b"beta"];
        assert_eq!(sum_framed_lengths(&frames), Some(9));
    }

    #[test]
    fn ffi_boundary_validates_nulls_and_parses_payload() {
        let mut status = FfiStatus {
            code: -1,
            parsed_port: 0,
        };
        let payload = b"10.0.0.1:9090";

        // SAFETY: `payload` is valid for `payload.len()` reads and `status` is
        // aligned and exclusively writable on the stack.
        let rc = unsafe { parse_endpoint_c(payload.as_ptr(), payload.len(), &mut status) };
        assert_eq!(rc, 0);
        assert_eq!(
            status,
            FfiStatus {
                code: 0,
                parsed_port: 9090,
            }
        );

        // SAFETY: Null pointers are explicitly handled before dereference.
        let null_rc = unsafe { parse_endpoint_c(std::ptr::null(), 4, &mut status) };
        assert_eq!(null_rc, -2);

        let invalid_utf8 = [0xff_u8, 0xfe_u8];
        // SAFETY: `invalid_utf8` and `status` are valid for reads/writes respectively.
        let utf8_rc =
            unsafe { parse_endpoint_c(invalid_utf8.as_ptr(), invalid_utf8.len(), &mut status) };
        assert_eq!(utf8_rc, -3);
    }
}
```

## Deliverables
- Rust workspace layout (`Cargo.toml`, `Cargo.lock`, `src/` modules, `tests/` integration suites)
- Supply-chain policy configuration (`deny.toml` coordinated with `appsec_engineer`)
- Verification log (`cargo fmt --check`, `cargo check --all-targets`, `cargo clippy --all-targets -- -D warnings`, `cargo test --all-targets`, `cargo audit`, `cargo deny check`)

"""CLI runner and tier orchestrator for the CortexOps 4-tier E2E suite."""

from __future__ import annotations

import argparse
import io
import sys
import unittest
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.e2e import common
from tests.e2e import tier1_features, tier2_boundaries, tier3_combinations, tier4_scenarios


TIER_MODULES = {
    1: ("TIER 1 (Feature Coverage)", tier1_features),
    2: ("TIER 2 (Boundary & Corner Cases)", tier2_boundaries),
    3: ("TIER 3 (Cross-Feature Combinations)", tier3_combinations),
    4: ("TIER 4 (Real-World Scenarios)", tier4_scenarios),
}


def run_tiers(
    tiers: list[int],
    repo_root: Path | None = None,
    verbosity: int = 1,
) -> tuple[int, dict[int, dict[str, int]]]:
    """Runs the selected E2E tiers and returns (exit_code, per_tier_stats)."""
    previous_root = common.get_repo_root()
    if repo_root is not None:
        common.set_repo_root(repo_root)

    loader = unittest.TestLoader()
    stats: dict[int, dict[str, int]] = {}
    total_run = 0
    total_failures = 0
    total_errors = 0

    try:
        for tier_id in tiers:
            label, mod = TIER_MODULES[tier_id]
            suite = loader.loadTestsFromModule(mod)
            print("=" * 72)
            print(f"{label} — Target: {common.get_repo_root()}")
            print("=" * 72)
            runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity)
            result = runner.run(suite)
            n_run = result.testsRun
            n_fail = len(result.failures)
            n_err = len(result.errors)
            n_skip = len(result.skipped)
            n_pass = n_run - n_fail - n_err - n_skip
            stats[tier_id] = {
                "run": n_run,
                "passed": n_pass,
                "failed": n_fail,
                "errors": n_err,
                "skipped": n_skip,
            }
            total_run += n_run
            total_failures += n_fail
            total_errors += n_err
    finally:
        common.set_repo_root(previous_root)

    print("\n" + "=" * 72)
    print("E2E SUMMARY")
    print("=" * 72)
    for tier_id in tiers:
        s = stats[tier_id]
        print(
            f"  TIER {tier_id}: {s['run']} run, {s['passed']} passed, "
            f"{s['failed']} failed, {s['errors']} errors, {s['skipped']} skipped"
        )
    print(
        f"  TOTAL : {total_run} run, {total_run - total_failures - total_errors} passed, "
        f"{total_failures} failed, {total_errors} errors"
    )
    print("=" * 72)

    ok = total_run > 0 and total_failures == 0 and total_errors == 0
    return (0 if ok else 1), stats


def run_tier_quiet(tier_id: int, repo_root: Path) -> unittest.TestResult:
    """Runs a single tier quietly against repo_root and returns TestResult."""
    previous_root = common.get_repo_root()
    common.set_repo_root(repo_root)
    try:
        _, mod = TIER_MODULES[tier_id]
        suite = unittest.TestLoader().loadTestsFromModule(mod)
        runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
        return runner.run(suite)
    finally:
        common.set_repo_root(previous_root)


def run_self_tests(verbosity: int = 1) -> int:
    """Runs synthetic fixture self-validation tests."""
    from tests.e2e import test_self_e2e

    suite = unittest.TestLoader().loadTestsFromModule(test_self_e2e)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(suite)
    ok = result.testsRun > 0 and len(result.failures) == 0 and len(result.errors) == 0
    return 0 if ok else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CortexOps Opaque-Box 4-Tier E2E Test Runner",
    )
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Select E2E tier to run (1, 2, 3, 4, or all)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Override target CortexOps repository root path",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run self-validation suite against synthetic pass/fail fixtures",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose unittest output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    verbosity = 2 if args.verbose else 1
    if args.self_test:
        return run_self_tests(verbosity=verbosity)

    tiers = [1, 2, 3, 4] if args.tier == "all" else [int(args.tier)]
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    exit_code, _ = run_tiers(tiers, repo_root=repo_root, verbosity=verbosity)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

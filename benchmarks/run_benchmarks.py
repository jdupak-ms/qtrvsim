#!/usr/bin/env python3
"""
QtRvSim Benchmark Runner

This script runs benchmarks using the qtrvsim_cli tool and collects
performance metrics. Results are output in JSON format for CI comparison.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class BenchmarkConfig:
    """Configuration for a single benchmark run."""
    name: str
    program: str
    pipelined: bool = False
    hazard_unit: str = "forward"  # none, stall, forward
    d_cache: Optional[str] = None  # e.g., "lru,4,2,2,wb"
    i_cache: Optional[str] = None
    l2_cache: Optional[str] = None
    description: str = ""


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run."""
    name: str
    config: Dict[str, Any]
    cycles: int
    stalls: int
    wall_time_ms: float
    cache_stats: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None


def get_benchmark_configs() -> List[BenchmarkConfig]:
    """Define all benchmark configurations to run."""
    programs = [
        "matrix_multiply_small.S",
        "bubble_sort.S",
        "fibonacci.S",
        "memory_copy.S",
    ]

    configs = []

    for program in programs:
        base_name = Path(program).stem

        # Single-cycle CPU (baseline)
        configs.append(BenchmarkConfig(
            name=f"{base_name}_single",
            program=program,
            pipelined=False,
            description="Single-cycle CPU, no cache"
        ))

        # Pipelined CPU with forwarding
        configs.append(BenchmarkConfig(
            name=f"{base_name}_pipe_fwd",
            program=program,
            pipelined=True,
            hazard_unit="forward",
            description="5-stage pipeline with forwarding, no cache"
        ))

        # Pipelined CPU with stalling only
        configs.append(BenchmarkConfig(
            name=f"{base_name}_pipe_stall",
            program=program,
            pipelined=True,
            hazard_unit="stall",
            description="5-stage pipeline with stalling only, no cache"
        ))

        # Pipelined with L1 caches (write-back)
        configs.append(BenchmarkConfig(
            name=f"{base_name}_pipe_cached_wb",
            program=program,
            pipelined=True,
            hazard_unit="forward",
            d_cache="lru,4,4,2,wb",
            i_cache="lru,4,4,2",
            description="5-stage pipeline with L1 caches (write-back)"
        ))

        # Pipelined with L1 caches (write-through)
        configs.append(BenchmarkConfig(
            name=f"{base_name}_pipe_cached_wt",
            program=program,
            pipelined=True,
            hazard_unit="forward",
            d_cache="lru,4,4,2,wt",
            i_cache="lru,4,4,2",
            description="5-stage pipeline with L1 caches (write-through)"
        ))

    return configs


def run_benchmark(
    cli_path: str,
    program_dir: str,
    config: BenchmarkConfig,
    timeout: int = 60
) -> BenchmarkResult:
    """Run a single benchmark and collect results."""

    program_path = os.path.join(program_dir, config.program)

    # Build command line
    cmd = [cli_path, "--asm", program_path, "--dump-cycles", "--osemu"]

    if config.pipelined:
        cmd.append("--pipelined")
        cmd.extend(["--hazard-unit", config.hazard_unit])

    if config.d_cache:
        cmd.extend(["--d-cache", config.d_cache])
        cmd.append("--dump-cache-stats")

    if config.i_cache:
        cmd.extend(["--i-cache", config.i_cache])

    if config.l2_cache:
        cmd.extend(["--l2-cache", config.l2_cache])

    # Measure wall time
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        end_time = time.perf_counter()
        wall_time_ms = (end_time - start_time) * 1000

        if result.returncode != 0:
            return BenchmarkResult(
                name=config.name,
                config=asdict(config),
                cycles=0,
                stalls=0,
                wall_time_ms=wall_time_ms,
                success=False,
                error=f"Exit code {result.returncode}: {result.stderr}"
            )

        # Parse output
        cycles = 0
        stalls = 0
        cache_stats = {}

        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith("cycles:"):
                cycles = int(line.split(":")[1].strip())
            elif line.startswith("stalls:"):
                stalls = int(line.split(":")[1].strip())
            elif ":" in line and "-cache" in line.split(":")[0]:
                parts = line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    cache_stats[key] = value

        return BenchmarkResult(
            name=config.name,
            config=asdict(config),
            cycles=cycles,
            stalls=stalls,
            wall_time_ms=wall_time_ms,
            cache_stats=cache_stats if cache_stats else None,
            success=True
        )

    except subprocess.TimeoutExpired:
        return BenchmarkResult(
            name=config.name,
            config=asdict(config),
            cycles=0,
            stalls=0,
            wall_time_ms=timeout * 1000,
            success=False,
            error="Benchmark timed out"
        )
    except Exception as e:
        return BenchmarkResult(
            name=config.name,
            config=asdict(config),
            cycles=0,
            stalls=0,
            wall_time_ms=0,
            success=False,
            error=str(e)
        )


def compare_results(
    current: List[BenchmarkResult],
    baseline: List[BenchmarkResult],
    threshold_pct: float = 5.0
) -> Dict[str, Any]:
    """Compare current results against baseline and detect regressions."""

    baseline_map = {r.name: r for r in baseline}
    comparisons = []
    regressions = []
    improvements = []

    for result in current:
        if result.name in baseline_map:
            base = baseline_map[result.name]

            if base.cycles > 0 and result.cycles > 0:
                cycle_diff_pct = ((result.cycles - base.cycles) / base.cycles) * 100

                comparison = {
                    "name": result.name,
                    "current_cycles": result.cycles,
                    "baseline_cycles": base.cycles,
                    "diff_cycles": result.cycles - base.cycles,
                    "diff_pct": round(cycle_diff_pct, 2)
                }
                comparisons.append(comparison)

                if cycle_diff_pct > threshold_pct:
                    regressions.append(comparison)
                elif cycle_diff_pct < -threshold_pct:
                    improvements.append(comparison)

    return {
        "comparisons": comparisons,
        "regressions": regressions,
        "improvements": improvements,
        "threshold_pct": threshold_pct,
        "has_regressions": len(regressions) > 0
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run QtRvSim benchmarks and collect performance metrics"
    )
    parser.add_argument(
        "--cli",
        required=True,
        help="Path to qtrvsim_cli executable"
    )
    parser.add_argument(
        "--programs",
        default=None,
        help="Path to benchmark programs directory"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Path to baseline results JSON for comparison"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        help="Regression threshold percentage (default: 5.0)"
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Filter benchmarks by name (substring match)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout per benchmark in seconds (default: 60)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )

    args = parser.parse_args()

    # Determine program directory
    if args.programs:
        program_dir = args.programs
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        program_dir = os.path.join(script_dir, "programs")

    if not os.path.isdir(program_dir):
        print(f"Error: Program directory not found: {program_dir}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.cli):
        print(f"Error: CLI executable not found: {args.cli}", file=sys.stderr)
        sys.exit(1)

    # Get benchmark configurations
    configs = get_benchmark_configs()

    # Filter if requested
    if args.filter:
        configs = [c for c in configs if args.filter in c.name]

    if not configs:
        print("No benchmarks to run (check filter)", file=sys.stderr)
        sys.exit(1)

    print(f"Running {len(configs)} benchmarks...")

    # Run benchmarks
    results = []
    for i, config in enumerate(configs, 1):
        if args.verbose:
            print(f"[{i}/{len(configs)}] Running {config.name}...", end=" ", flush=True)

        result = run_benchmark(args.cli, program_dir, config, args.timeout)
        results.append(result)

        if args.verbose:
            if result.success:
                print(f"OK ({result.cycles} cycles, {result.stalls} stalls)")
            else:
                print(f"FAILED: {result.error}")

    # Prepare output
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cli_path": args.cli,
        "program_dir": program_dir,
        "results": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success)
        }
    }

    # Compare with baseline if provided
    if args.baseline and os.path.isfile(args.baseline):
        with open(args.baseline, 'r') as f:
            baseline_data = json.load(f)

        baseline_results = [
            BenchmarkResult(**r) for r in baseline_data.get("results", [])
        ]

        comparison = compare_results(results, baseline_results, args.threshold)
        output["comparison"] = comparison

        if comparison["has_regressions"]:
            print("\n⚠️  Performance regressions detected:")
            for reg in comparison["regressions"]:
                print(f"  - {reg['name']}: {reg['diff_pct']:+.1f}% "
                      f"({reg['baseline_cycles']} → {reg['current_cycles']} cycles)")

        if comparison["improvements"]:
            print("\n✓ Performance improvements:")
            for imp in comparison["improvements"]:
                print(f"  - {imp['name']}: {imp['diff_pct']:+.1f}% "
                      f"({imp['baseline_cycles']} → {imp['current_cycles']} cycles)")

    # Write output
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults written to {args.output}")
    print(f"Summary: {output['summary']['passed']}/{output['summary']['total']} passed")

    # Exit with error if there are regressions
    if args.baseline and output.get("comparison", {}).get("has_regressions"):
        sys.exit(1)

    # Exit with error if any benchmarks failed
    if output['summary']['failed'] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

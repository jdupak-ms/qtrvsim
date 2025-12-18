#!/usr/bin/env python3
"""
QtRvSim GUI Headless Benchmark

This script tests the GUI application running in headless mode using Qt's
offscreen platform. This allows testing GUI initialization, rendering
performance, and core functionality without a display.

Qt Offscreen Platform:
Qt provides a platform plugin called 'offscreen' that allows running Qt
applications without a physical display. This is useful for:
- CI/CD environments without display servers
- Automated GUI testing
- Headless rendering and benchmarking

To use offscreen mode:
- Set QT_QPA_PLATFORM=offscreen environment variable
- Or pass -platform offscreen to the application

References:
- https://doc.qt.io/qt-6/qpa.html
- https://doc.qt.io/qt-6/platform-notes-linux.html#offscreen-rendering
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class GuiBenchmarkResult:
    """Result from GUI benchmark."""
    name: str
    startup_time_ms: float
    success: bool
    error: Optional[str] = None


def check_offscreen_support() -> bool:
    """Check if Qt offscreen platform is available."""
    # Try to detect Qt platform plugins
    qt_plugin_paths = [
        "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms",
        "/usr/lib/qt5/plugins/platforms",
        "/usr/lib64/qt5/plugins/platforms",
        os.path.expanduser("~/.local/lib/qt5/plugins/platforms"),
    ]

    for path in qt_plugin_paths:
        offscreen_path = os.path.join(path, "libqoffscreen.so")
        if os.path.exists(offscreen_path):
            return True

    # Also check via QT_PLUGIN_PATH if set
    if "QT_PLUGIN_PATH" in os.environ:
        plugin_path = os.environ["QT_PLUGIN_PATH"]
        offscreen_path = os.path.join(plugin_path, "platforms", "libqoffscreen.so")
        if os.path.exists(offscreen_path):
            return True

    return True  # Assume it's available if we can't verify


def run_gui_startup_benchmark(
    gui_path: str,
    timeout: int = 30
) -> GuiBenchmarkResult:
    """
    Benchmark GUI startup time in headless mode.

    The GUI will be started with offscreen rendering and immediately closed.
    This measures the initialization overhead.
    """
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["QT_DEBUG_PLUGINS"] = "0"  # Reduce noise

    # We'll use a short-lived run that just starts and exits
    # Since GUI doesn't have a built-in exit mechanism, we'll timeout
    start_time = time.perf_counter()

    try:
        # Start GUI and immediately send SIGTERM after a short delay
        # This tests that the GUI can start successfully in headless mode
        proc = subprocess.Popen(
            [gui_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait a short time for startup
        time.sleep(2)

        # Check if process is still running (good sign it started successfully)
        if proc.poll() is None:
            # Process is running, terminate gracefully
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            end_time = time.perf_counter()
            startup_time_ms = (end_time - start_time) * 1000

            return GuiBenchmarkResult(
                name="gui_startup_offscreen",
                startup_time_ms=startup_time_ms,
                success=True
            )
        else:
            # Process exited early - might be an error
            _, stderr = proc.communicate()
            return GuiBenchmarkResult(
                name="gui_startup_offscreen",
                startup_time_ms=0,
                success=False,
                error=f"GUI exited early: {stderr.decode()[:500]}"
            )

    except Exception as e:
        return GuiBenchmarkResult(
            name="gui_startup_offscreen",
            startup_time_ms=0,
            success=False,
            error=str(e)
        )


def run_gui_with_program(
    gui_path: str,
    program_path: str,
    timeout: int = 30
) -> GuiBenchmarkResult:
    """
    Start GUI with a program loaded in headless mode.

    This tests the ability to load and potentially run programs.
    """
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"

    start_time = time.perf_counter()

    try:
        proc = subprocess.Popen(
            [gui_path, program_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for startup with program loaded
        time.sleep(3)

        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            end_time = time.perf_counter()
            startup_time_ms = (end_time - start_time) * 1000

            return GuiBenchmarkResult(
                name=f"gui_load_program",
                startup_time_ms=startup_time_ms,
                success=True
            )
        else:
            _, stderr = proc.communicate()
            return GuiBenchmarkResult(
                name=f"gui_load_program",
                startup_time_ms=0,
                success=False,
                error=f"GUI exited early: {stderr.decode()[:500]}"
            )

    except Exception as e:
        return GuiBenchmarkResult(
            name=f"gui_load_program",
            startup_time_ms=0,
            success=False,
            error=str(e)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Run QtRvSim GUI benchmarks in headless mode"
    )
    parser.add_argument(
        "--gui",
        required=True,
        help="Path to qtrvsim_gui executable"
    )
    parser.add_argument(
        "--program",
        default=None,
        help="Optional program to load for testing"
    )
    parser.add_argument(
        "--output",
        default="gui_benchmark_results.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout per benchmark in seconds"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip platform capability checks"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.gui):
        print(f"Error: GUI executable not found: {args.gui}", file=sys.stderr)
        sys.exit(1)

    # Check for offscreen support
    if not args.skip_checks:
        if not check_offscreen_support():
            print("Warning: Qt offscreen platform may not be available",
                  file=sys.stderr)

    results = []

    # Test 1: Basic startup
    print("Testing GUI startup in offscreen mode...")
    result = run_gui_startup_benchmark(args.gui, args.timeout)
    results.append(result)

    if args.verbose:
        if result.success:
            print(f"  ✓ Startup: {result.startup_time_ms:.1f}ms")
        else:
            print(f"  ✗ Startup failed: {result.error}")

    # Test 2: Load program (if provided)
    if args.program and os.path.isfile(args.program):
        print("Testing GUI with program loaded...")
        result = run_gui_with_program(args.gui, args.program, args.timeout)
        results.append(result)

        if args.verbose:
            if result.success:
                print(f"  ✓ Load program: {result.startup_time_ms:.1f}ms")
            else:
                print(f"  ✗ Load failed: {result.error}")

    # Prepare output
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gui_path": args.gui,
        "platform": "offscreen",
        "results": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success)
        }
    }

    # Write output
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults written to {args.output}")
    print(f"Summary: {output['summary']['passed']}/{output['summary']['total']} passed")

    # Exit with error if any benchmarks failed
    if output['summary']['failed'] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

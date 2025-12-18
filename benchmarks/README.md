# QtRvSim Benchmarking System

This directory contains comprehensive benchmarking infrastructure for QtRvSim,
including CLI and GUI benchmarks with CI integration.

## Overview

The benchmarking system provides:

1. **CLI Benchmarks**: Tests simulation performance across different CPU configurations
2. **GUI Benchmarks**: Tests GUI startup and operation in headless mode
3. **CI Integration**: Automatic benchmark runs with comparison against master branch
4. **Regression Detection**: Alerts when performance degrades

## Directory Structure

```
benchmarks/
├── README.md                 # This file
├── run_benchmarks.py         # CLI benchmark runner
├── run_gui_benchmark.py      # GUI headless benchmark runner
└── programs/                 # Benchmark programs
    ├── matrix_multiply_small.S
    ├── bubble_sort.S
    ├── fibonacci.S
    └── memory_copy.S
```

## Quick Start

### Running CLI Benchmarks Locally

```bash
# Build the project in Release mode
cmake -DCMAKE_BUILD_TYPE=Release -B build
cmake --build build -j$(nproc)

# Run benchmarks
python3 benchmarks/run_benchmarks.py \
    --cli build/target/qtrvsim_cli \
    --verbose
```

### Running GUI Benchmarks Locally

```bash
# GUI benchmarks require Qt offscreen platform
python3 benchmarks/run_gui_benchmark.py \
    --gui build/target/qtrvsim_gui \
    --verbose
```

## Benchmark Programs

### matrix_multiply_small.S
Multiplies two 4x4 matrices. Tests:
- Basic ALU operations (multiplication, addition)
- Memory access patterns (strided access)
- Nested loops

### bubble_sort.S
Sorts a 32-element array. Tests:
- Branch prediction (many conditional branches)
- Memory access patterns (sequential)
- Early exit optimization

### fibonacci.S
Calculates fibonacci(20) recursively. Tests:
- Function call overhead
- Stack operations
- Register pressure

### memory_copy.S
Copies 1KB buffer 10 times. Tests:
- Memory throughput
- Cache behavior
- Sequential access patterns

## Benchmark Configurations

Each program is tested with multiple CPU configurations:

| Configuration | Pipeline | Hazard Unit | Cache |
|--------------|----------|-------------|-------|
| `*_single` | No | N/A | None |
| `*_pipe_fwd` | Yes | Forward | None |
| `*_pipe_stall` | Yes | Stall | None |
| `*_pipe_cached_wb` | Yes | Forward | L1 Write-Back |
| `*_pipe_cached_wt` | Yes | Forward | L1 Write-Through |

## Output Format

Results are saved in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "results": [
    {
      "name": "matrix_multiply_small_single",
      "config": { ... },
      "cycles": 1234,
      "stalls": 56,
      "wall_time_ms": 45.2,
      "success": true
    }
  ],
  "summary": {
    "total": 20,
    "passed": 20,
    "failed": 0
  }
}
```

## CI Integration

### Automatic Benchmarks

The `.github/workflows/benchmark.yml` workflow:

1. Runs on every push to master and every PR
2. Builds the project in Release mode
3. Runs all benchmarks
4. Downloads baseline from master branch (for PRs)
5. Compares results and detects regressions
6. Posts results as PR comments
7. Stores results as artifacts for future comparisons

### Regression Detection

A regression is detected when cycle count increases by more than the threshold
(default: 10%). The workflow will:

1. Add a warning comment to the PR
2. Show which benchmarks regressed
3. Display the percentage change

### Viewing Results

- **PR Comments**: Benchmark results are automatically posted as comments
- **Artifacts**: Download `benchmark-baseline` artifact for detailed JSON
- **Actions Tab**: Check workflow logs for verbose output

## Qt Offscreen Platform

For GUI benchmarks, Qt's offscreen platform is used to run without a display.

### How It Works

Qt provides platform abstraction (QPA) plugins. The `offscreen` plugin:

- Renders to an in-memory surface
- Doesn't require X11, Wayland, or any display server
- Perfect for CI/CD environments

### Environment Variables

```bash
# Enable offscreen rendering
export QT_QPA_PLATFORM=offscreen

# Reduce debug output
export QT_DEBUG_PLUGINS=0
```

### Platform Support

The offscreen plugin is included in:
- Qt5: `qtbase5-dev` package (Linux)
- Qt6: `qt6-base-dev` package (Linux)
- macOS/Windows: Included with Qt installation

### Troubleshooting

If offscreen mode fails:

1. Check Qt platform plugins are installed:
   ```bash
   ls /usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/
   ```

2. Verify QT_PLUGIN_PATH if using custom Qt:
   ```bash
   export QT_PLUGIN_PATH=/path/to/qt/plugins
   ```

3. Check for missing libraries:
   ```bash
   ldd /path/to/qt/plugins/platforms/libqoffscreen.so
   ```

## Adding New Benchmarks

### Adding a New Program

1. Create a RISC-V assembly file in `programs/`:
   ```asm
   .text
   .globl _start
   _start:
       la sp, __stack_end
       # ... your code ...
       li a7, 93   # SYS_exit
       li a0, 0
       ecall

   .bss
   __stack_start:
       .skip 1024
   __stack_end:
   ```

2. Add the program to `run_benchmarks.py`:
   ```python
   programs = [
       # ... existing programs ...
       "your_new_program.S",
   ]
   ```

### Adding a New Configuration

Modify `get_benchmark_configs()` in `run_benchmarks.py`:

```python
configs.append(BenchmarkConfig(
    name=f"{base_name}_your_config",
    program=program,
    pipelined=True,
    hazard_unit="forward",
    d_cache="lru,8,4,4,wb",  # Custom cache config
    description="Your configuration description"
))
```

## Best Practices

1. **Deterministic Programs**: Benchmarks should produce consistent results
2. **Reasonable Runtime**: Each benchmark should complete in < 60 seconds
3. **Meaningful Metrics**: Focus on cycle counts (hardware-independent)
4. **Diverse Workloads**: Cover different instruction mixes and access patterns

## Metrics Collected

| Metric | Description |
|--------|-------------|
| `cycles` | Total CPU cycles executed |
| `stalls` | Pipeline stall cycles |
| `wall_time_ms` | Real-world execution time |
| `cache_stats` | Hit/miss rates, stall cycles (when cache enabled) |

## Related Documentation

- [QtRvSim CLI Documentation](../docs/user/cli.md)
- [Qt Platform Abstraction](https://doc.qt.io/qt-6/qpa.html)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

# 🔬 Micro-Scenario 05 — The Parallelism Trap
**Complexity:** ⭐⭐⭐⭐ High
**Skill Targets:** Section 13.1 — The GIL · `threading.Thread` vs `multiprocessing.Pool` · `concurrent.futures` · `time.perf_counter()` benchmarking
**Portfolio Context:** The **Grand Line** orchestrator ingests VPS health snapshots from 50 servers every 60 seconds. A junior dev "optimised" the CPU-bound log parser by splitting work across 8 threads. It is slower than the single-threaded version. You must prove why with benchmarks, then implement the correct solution.

---

## Step 1 — The Broken Junior Implementation

```python
# log_parser.py
# "Multithreaded log parser — 8x faster!" — Junior Dev (it is not)

import threading
import time
import re

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] (?P<message>.+)"
)

def parse_chunk(lines: list[str]) -> list[dict]:
    """CPU-bound: regex-parses every line in a chunk. Returns matched records."""
    results = []
    for line in lines:
        match = LOG_PATTERN.match(line)
        if match:
            results.append(match.groupdict())
    return results


def threaded_parse(all_lines: list[str], num_threads: int = 8) -> list[dict]:
    """
    Splits the log lines across N threads and parses them concurrently.
    Junior assumption: 8 threads = 8x faster.
    """
    chunk_size = len(all_lines) // num_threads
    chunks     = [all_lines[i:i+chunk_size] for i in range(0, len(all_lines), chunk_size)]
    results    = [None] * len(chunks)

    def worker(index: int, chunk: list[str]):
        results[index] = parse_chunk(chunk)     # Writing to shared list — race condition possible

    threads = [
        threading.Thread(target=worker, args=(i, chunk))
        for i, chunk in enumerate(chunks)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Flatten results
    return [item for sublist in results for item in sublist]


# Benchmark
if __name__ == "__main__":
    LOG_LINES = [
        f"2024-01-15 14:{'%02d' % (i % 60)}:00 [{'ERROR' if i%5==0 else 'INFO'}] Message {i}"
        for i in range(500_000)
    ]

    start = time.perf_counter()
    result_threaded = threaded_parse(LOG_LINES)
    print(f"Threaded (8 threads): {time.perf_counter() - start:.2f}s — {len(result_threaded)} records")

    start = time.perf_counter()
    result_single = parse_chunk(LOG_LINES)
    print(f"Single-threaded:      {time.perf_counter() - start:.2f}s — {len(result_single)} records")
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — Using threads for CPU-bound work
```python
threads = [threading.Thread(target=worker, ...) for ...]
```
Regex matching is 100% CPU-bound — it executes Python bytecode, which is governed by the GIL. The GIL ensures only ONE thread executes Python bytecode at any moment, even on an 8-core machine. The threading model here:

```
Thread 1 runs → GIL switches → Thread 2 runs → GIL switches → Thread 3 runs → ...
```

You have not achieved parallelism. You have achieved sequential execution with the overhead of:
- Thread creation (~100µs each × 8)
- GIL contention and context switching between 8 threads
- Memory for 8 thread stacks

**Result:** The threaded version is typically 15–30% SLOWER than single-threaded for CPU-bound regex workloads.

**Fix pseudocode:**
```
Replace threading.Thread with multiprocessing.Pool:
    Each process has its OWN Python interpreter and its OWN GIL
    → True parallel execution across CPU cores

from multiprocessing import Pool

with Pool(processes=8) as pool:
    chunk_results = pool.map(parse_chunk, chunks)

return [item for sublist in chunk_results for item in sublist]
```

### Bug 2 — Race condition on shared list
```python
results = [None] * len(chunks)

def worker(index, chunk):
    results[index] = parse_chunk(chunk)    # Multiple threads writing to shared list
```
Even though each thread writes to a different index, Python list operations are not atomic at the bytecode level. This is a race condition. The GIL happens to make this *mostly* safe in CPython for simple assignments, but it is undefined behaviour — a contract that can break in PyPy, free-threaded CPython 3.13, or with more complex writes. The correct approach: use `concurrent.futures.ThreadPoolExecutor` which returns Futures, or `multiprocessing.Pool.map()` which collects results safely.

### Bug 3 — Missing `if __name__ == "__main__":` guard on multiprocessing
```python
# If you add multiprocessing.Pool without the guard:
pool = Pool(8)   # On Windows/macOS: spawns child processes that re-import the script
                 # Each child immediately creates another pool → recursive bomb
```
Always gate multiprocessing code with `if __name__ == "__main__":`.

### Concurrency Selection Reference
```
Task type      → Correct tool
─────────────────────────────────────────────────────────
CPU-bound      → multiprocessing.Pool (bypasses GIL)
I/O-bound      → concurrent.futures.ThreadPoolExecutor OR asyncio
Mixed pipeline → asyncio for I/O → multiprocessing for CPU stages
```

---

## Step 3 — Validation Challenge

Implement three versions and use `time.perf_counter()` to prove the correct hierarchy.

```python
# log_parser_v2.py
import time
import re
import tracemalloc
import unittest
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] (?P<message>.+)"
)

# ─── TODO 1: parse_chunk (same logic as before — do not change) ───────────────
def parse_chunk(lines: list[str]) -> list[dict]:
    # TODO: regex-match every line, return list of groupdicts for matched lines
    pass


# ─── TODO 2: Implement single-threaded baseline ───────────────────────────────
def parse_single(all_lines: list[str]) -> list[dict]:
    # TODO: call parse_chunk once with all lines, return result
    pass


# ─── TODO 3: Implement the WRONG approach — threads for CPU work ──────────────
def parse_threaded(all_lines: list[str], num_workers: int = 8) -> list[dict]:
    # TODO: split lines into chunks, use ThreadPoolExecutor to run parse_chunk
    # Use executor.map() to collect results safely
    # Return flattened list
    pass


# ─── TODO 4: Implement the CORRECT approach — multiprocessing ─────────────────
def parse_multiprocess(all_lines: list[str], num_workers: int = 8) -> list[dict]:
    # TODO: split lines into chunks, use multiprocessing.Pool.map()
    # MUST use the if __name__ guard in the benchmark block below
    # Return flattened list
    pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestLogParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.LINES = [
            f"2024-01-15 14:{'%02d' % (i % 60)}:00 "
            f"[{'ERROR' if i % 5 == 0 else 'INFO'}] Message number {i}"
            for i in range(100_000)
        ]
        cls.EXPECTED_COUNT = sum(
            1 for line in cls.LINES if LOG_PATTERN.match(line)
        )

    def test_single_correct_count(self):
        result = parse_single(self.LINES)
        self.assertEqual(len(result), self.EXPECTED_COUNT)
        print(f"✅ ASSERTION 1 PASSED: parse_single returned {len(result)} records")

    def test_threaded_correct_count(self):
        result = parse_threaded(self.LINES)
        self.assertEqual(len(result), self.EXPECTED_COUNT)
        print(f"✅ ASSERTION 2 PASSED: parse_threaded returned {len(result)} records")

    def test_multiprocess_correct_count(self):
        result = parse_multiprocess(self.LINES)
        self.assertEqual(len(result), self.EXPECTED_COUNT)
        print(f"✅ ASSERTION 3 PASSED: parse_multiprocess returned {len(result)} records")

    def test_all_results_identical(self):
        """All three implementations must return the same data."""
        r_single = sorted(parse_single(self.LINES),     key=lambda x: x["message"])
        r_thread = sorted(parse_threaded(self.LINES),   key=lambda x: x["message"])
        r_multi  = sorted(parse_multiprocess(self.LINES), key=lambda x: x["message"])
        self.assertEqual(r_single, r_thread)
        self.assertEqual(r_single, r_multi)
        print("✅ ASSERTION 4 PASSED: All three implementations return identical results")


# ─── BENCHMARK (run manually, not in unittest) ───────────────────────────────

def run_benchmark():
    LINES = [
        f"2024-01-15 14:{'%02d' % (i % 60)}:00 "
        f"[{'ERROR' if i % 5 == 0 else 'INFO'}] Message number {i}"
        for i in range(500_000)
    ]

    print(f"\n{'═' * 55}")
    print(f"  BENCHMARK: Parsing {len(LINES):,} log lines")
    print(f"{'═' * 55}")

    implementations = [
        ("Single-threaded (baseline)", parse_single),
        ("Threaded × 8 (WRONG for CPU)", parse_threaded),
        ("Multiprocess × 8 (CORRECT)", parse_multiprocess),
    ]

    results = {}
    for name, fn in implementations:
        start = time.perf_counter()
        output = fn(LINES)
        elapsed = time.perf_counter() - start
        results[name] = elapsed
        print(f"  {name:<35} {elapsed:.3f}s  ({len(output):,} records)")

    print(f"{'─' * 55}")

    # REQUIRED ASSERTION: multiprocess must beat single-threaded
    # On a multi-core machine this should be >30% faster
    single_t   = results["Single-threaded (baseline)"]
    multi_t    = results["Multiprocess × 8 (CORRECT)"]
    speedup    = single_t / multi_t
    print(f"  Multiprocess speedup: {speedup:.2f}x")

    # REQUIRED ASSERTION: threaded should NOT significantly beat single-threaded
    thread_t   = results["Threaded × 8 (WRONG for CPU)"]
    thread_ratio = thread_t / single_t
    print(f"  Thread overhead ratio vs single: {thread_ratio:.2f}x")
    print(f"  (>1.0 confirms the GIL penalty)")
    print(f"{'═' * 55}\n")


if __name__ == "__main__":
    # Run unit tests first
    unittest.main(argv=[""], exit=False, verbosity=0)
    # Then run the benchmark
    run_benchmark()
```

### Expected Benchmark Output (4-core machine)
```text
═══════════════════════════════════════════════════════
  BENCHMARK: Parsing 500,000 log lines
═══════════════════════════════════════════════════════
  Single-threaded (baseline)          3.241s  (500,000 records)
  Threaded × 8 (WRONG for CPU)        3.876s  (500,000 records)
  Multiprocess × 8 (CORRECT)         1.102s  (500,000 records)
───────────────────────────────────────────────────────
  Multiprocess speedup: 2.94x
  Thread overhead ratio vs single: 1.20x
  (>1.0 confirms the GIL penalty)
═══════════════════════════════════════════════════════
```

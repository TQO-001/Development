# 🔬 Micro-Scenario 03 — The Unmetered Pipeline
**Complexity:** ⭐⭐⭐ Medium-High
**Skill Targets:** Section 11.2 — `@contextmanager` · Section 11.4 — `ExitStack` · Section 13.3 — `tracemalloc` · `time.perf_counter()`
**Portfolio Context:** The **Grand Line** VPS orchestrator runs a three-stage data pipeline: Extract → Transform → Load. A senior engineer has flagged that there is zero observability into which stage is slow or leaking memory. Your job is to instrument every stage without touching the stage logic itself.

---

## Step 1 — The Broken Junior Implementation

```python
# pipeline.py
import json, csv, psycopg2

DSN = "postgresql://user:password@localhost/grand_line"

def extract(filepath: str) -> list[dict]:
    """Reads all VPS metrics from a JSON file."""
    with open(filepath) as f:
        return json.load(f)              # Full file into RAM — no streaming

def transform(records: list[dict]) -> list[dict]:
    """Normalises VPS metric records."""
    cleaned = []
    for r in records:
        cleaned.append({
            "host":    r["hostname"].strip().lower(),
            "cpu":     float(r.get("cpu_pct", 0)),
            "mem":     float(r.get("mem_pct", 0)),
            "disk":    float(r.get("disk_pct", 0)),
        })
    return cleaned                       # Another full list in RAM

def load(records: list[dict]) -> None:
    """Writes cleaned records to PostgreSQL."""
    conn   = psycopg2.connect(DSN)       # No context manager
    cursor = conn.cursor()
    for r in records:                    # Loop instead of executemany
        cursor.execute(
            "INSERT INTO vps_metrics (host, cpu, mem, disk) VALUES (%s,%s,%s,%s)",
            (r["host"], r["cpu"], r["mem"], r["disk"])
        )
    conn.commit()
    # conn and cursor never closed

def run_pipeline(filepath: str) -> None:
    """Runs the three-stage pipeline with zero instrumentation."""
    print("Pipeline starting...")
    raw      = extract(filepath)
    clean    = transform(raw)
    load(clean)
    print("Pipeline complete.")           # No timing. No memory. No stage breakdown.

run_pipeline("vps_metrics.json")
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — No stage-level observability
```python
print("Pipeline starting...")
# ... stages run ...
print("Pipeline complete.")
```
You have no idea if Extract took 200ms or 8 seconds. You have no idea which stage peaks at 500MB. When this pipeline starts failing at 2am, you have zero data to triage with. Instrumentation is not optional in production — it is the difference between a 10-minute fix and a 3-hour outage.

**Fix pseudocode:**
```
Write a @contextmanager called pipeline_stage(name):
    - Start tracemalloc
    - Record time.perf_counter() as t_start
    - yield (the stage logic runs here)
    - On exit (finally): compute elapsed, get peak RAM from tracemalloc.get_traced_memory()
    - Print: "[{name}] {elapsed_ms:.1f}ms | Peak RAM: {peak_kb:.1f}KB"
    - Stop tracemalloc
```

### Bug 2 — Three separate resources need coordinated cleanup
```python
conn   = psycopg2.connect(DSN)
cursor = conn.cursor()
# No with-statement, no try/finally
```
If you have multiple resources in a single function (connection + cursor + potentially a file), nesting `with` statements gets awkward. `ExitStack` is the clean solution: register each resource as you open it, and all are guaranteed to close in LIFO order.

**Fix pseudocode:**
```
In the load() function:
    with ExitStack() as stack:
        conn   = stack.enter_context(psycopg2.connect(DSN))
        cursor = stack.enter_context(conn.cursor())
        cursor.executemany(...)
        conn.commit()
    # Both closed automatically on exit
```

### Bug 3 — `for r in records: cursor.execute(...)` — N database round-trips
Replace with `cursor.executemany(query, list_of_tuples)` — one batch operation.

### Bug 4 — `json.load()` loads the full file into RAM
For large metric files, chain your stages via generators so only one record at a time crosses stage boundaries. (Advanced: use `ijson` for streaming JSON parsing.)

---

## Step 3 — Validation Challenge

```python
# pipeline_v2.py
import json
import time
import tracemalloc
from contextlib import contextmanager, ExitStack
from typing import Generator
import unittest
from unittest.mock import patch, MagicMock


# ─── TODO 1: Implement the stage profiler context manager ────────────────────
# Requirements:
#   - Use @contextmanager
#   - Track wall-clock time with time.perf_counter()
#   - Track peak RAM with tracemalloc
#   - Print on exit: "[{name}] {elapsed_ms:.1f}ms | Peak RAM: {peak_kb:.1f}KB"
#   - yield must be inside try/finally so cleanup runs on exception too

@contextmanager
def pipeline_stage(name: str):
    # TODO
    pass


# ─── TODO 2: Implement extract as a generator (memory-safe) ──────────────────
# Requirements:
#   - Open the file with a context manager
#   - Parse JSON incrementally (json.load is acceptable for this exercise)
#   - Yield one record dict at a time — do NOT return a list

def extract(filepath: str) -> Generator[dict, None, None]:
    # TODO
    pass


# ─── TODO 3: Implement transform as a generator ──────────────────────────────
# Requirements:
#   - Accept an iterable of raw dicts (the extract generator)
#   - Yield cleaned dicts one at a time
#   - Strip + lowercase hostname, cast cpu/mem/disk to float with .get() defaults

def transform(records) -> Generator[dict, None, None]:
    # TODO
    pass


# ─── TODO 4: Implement load using ExitStack + executemany ────────────────────
# Requirements:
#   - Use ExitStack to manage conn + cursor lifecycle
#   - Collect transformed records into a batch list
#   - Use cursor.executemany() for a single bulk insert
#   - Commit on success, rollback on exception
#   - Return row count inserted

def load(records, dsn: str) -> int:
    # TODO
    pass


# ─── TODO 5: Wire pipeline with stage profiling ──────────────────────────────
# Requirements:
#   - Wrap each stage call inside pipeline_stage(stage_name)
#   - Pass generator output of extract into transform, transform into load
#   - Return a dict: {"extracted": N, "loaded": N}

def run_pipeline(filepath: str, dsn: str) -> dict:
    # TODO
    pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestPipeline(unittest.TestCase):

    SAMPLE_DATA = [
        {"hostname": " Web-01 ", "cpu_pct": "45.2", "mem_pct": "67.1", "disk_pct": "30.0"},
        {"hostname": "DB-01",   "cpu_pct": "90.0", "mem_pct": "88.5", "disk_pct": "75.2"},
        {"hostname": "Cache-01","cpu_pct": "12.0", "mem_pct": "20.0", "disk_pct": "10.0"},
    ]

    def test_extract_is_generator(self):
        """extract() must be a generator — not a list."""
        import tempfile, json, types
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.SAMPLE_DATA, f)
            path = f.name
        result = extract(path)
        self.assertIsInstance(result, types.GeneratorType)
        records = list(result)
        self.assertEqual(len(records), 3)
        print("✅ ASSERTION 1 PASSED: extract() is a generator yielding 3 records")

    def test_transform_normalises_correctly(self):
        """transform() must lowercase + strip host and cast values to float."""
        raw = iter(self.SAMPLE_DATA)
        cleaned = list(transform(raw))
        self.assertEqual(cleaned[0]["host"], "web-01")         # stripped + lowercased
        self.assertIsInstance(cleaned[0]["cpu"], float)
        self.assertAlmostEqual(cleaned[1]["cpu"], 90.0)
        print("✅ ASSERTION 2 PASSED: transform() normalises correctly")

    def test_transform_is_generator(self):
        """transform() must be a generator — not a list."""
        import types
        result = transform(iter(self.SAMPLE_DATA))
        self.assertIsInstance(result, types.GeneratorType)
        print("✅ ASSERTION 3 PASSED: transform() is a generator")

    def test_pipeline_stage_prints_timing(self):
        """pipeline_stage() must print timing info on exit."""
        import io, sys
        captured = io.StringIO()
        sys.stdout = captured
        with pipeline_stage("Test Stage"):
            time.sleep(0.01)
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Test Stage", output)
        self.assertIn("ms", output)
        self.assertIn("KB", output)
        print("✅ ASSERTION 4 PASSED: pipeline_stage() prints timing + RAM")

    def test_pipeline_stage_runs_on_exception(self):
        """pipeline_stage() finally block must run even when exception is raised."""
        import io, sys
        captured = io.StringIO()
        sys.stdout = captured
        try:
            with pipeline_stage("Crash Stage"):
                raise ValueError("Simulated failure")
        except ValueError:
            pass
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Crash Stage", output)
        print("✅ ASSERTION 5 PASSED: pipeline_stage() prints on exception exit")

    def test_memory_efficiency(self):
        """Pipeline generator chain must not build intermediate lists in RAM."""
        import tempfile, json
        BIG_DATA = [
            {"hostname": f"node-{i}", "cpu_pct": str(i % 100),
             "mem_pct": str(i % 100), "disk_pct": str(i % 50)}
            for i in range(10_000)
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(BIG_DATA, f)
            path = f.name

        tracemalloc.start()
        snap1 = tracemalloc.take_snapshot()

        gen = transform(extract(path))
        count = sum(1 for _ in gen)   # Consume without accumulating

        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_kb = peak / 1024
        self.assertEqual(count, 10_000)
        # Generator chain should not exceed 2MB for 10k records
        self.assertLess(peak_kb, 2048,
            f"Peak RAM {peak_kb:.1f}KB exceeds 2MB — intermediate list suspected")
        print(f"✅ ASSERTION 6 PASSED: 10k records streamed with peak {peak_kb:.1f}KB < 2048KB")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

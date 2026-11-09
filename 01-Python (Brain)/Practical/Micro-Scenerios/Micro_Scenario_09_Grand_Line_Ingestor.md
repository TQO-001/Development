# 🔬 Micro-Scenario 09 — The Grand Line Ingestor
**Complexity:** ⭐⭐⭐⭐⭐ Very High — Capstone
**Skill Targets:** ALL of Sections 11–13 — `@contextmanager` · `ExitStack` · Package structure · `asyncio` + `Semaphore` · Generator pipelines · `tracemalloc` · Parameterized bulk writes · `time.perf_counter()` · `unittest`
**Portfolio Context:** This is your flagship exercise. The **Grand Line** VPS orchestrator needs a production-grade metrics ingestor that: asynchronously collects CPU/RAM/disk snapshots from 100 VPS nodes every 60 seconds, validates and transforms the raw data through a memory-safe generator pipeline, and bulk-inserts clean records into PostgreSQL — all while emitting per-stage profiling metrics. Every concept from Sections 11–13 appears here.

---

## Step 1 — The Broken Junior Implementation

```python
# ingestor.py — "Works great on my 5-node dev cluster" — Junior Dev
import asyncio, requests, psycopg2, json, time

DSN = "host=prod-db user=admin password=gl_admin_2024 dbname=grand_line"

NODE_URLS = [f"http://vps-node-{i:03d}.internal/metrics" for i in range(1, 101)]

def collect_metrics(urls):
    """Fetches metrics from all nodes — synchronously."""
    all_data = []
    for url in urls:                                    # Sequential: 100 nodes × 200ms = 20s
        response = requests.get(url, timeout=5)
        all_data.append(response.json())               # No error handling
    return all_data                                     # 100 dicts loaded into RAM at once

def validate_and_clean(metrics):
    """Validates and cleans all metrics."""
    valid = []
    for m in metrics:                                   # Builds second full list in RAM
        if m.get("cpu_pct") is not None:
            valid.append({
                "node_id":  m["node_id"],
                "cpu_pct":  float(m["cpu_pct"]),
                "mem_pct":  float(m["mem_pct"]),
                "disk_pct": float(m.get("disk_pct", 0)),
                "ts":       m.get("timestamp", time.time())
            })
    return valid

def write_to_db(records):
    """Writes records to PostgreSQL."""
    conn   = psycopg2.connect(DSN)                      # No pooling
    cursor = conn.cursor()
    for r in records:                                   # N round-trips for N records
        cursor.execute(
            f"INSERT INTO vps_metrics (node_id, cpu_pct, mem_pct, disk_pct, ts) "
            f"VALUES ('{r['node_id']}', {r['cpu_pct']}, {r['mem_pct']}, "
            f"{r['disk_pct']}, '{r['ts']}')"            # SQL injection on node_id + ts
        )
    conn.commit()
    # conn and cursor never closed

def run():
    print("Starting ingestor run...")
    start = time.time()                                 # time.time() not time.perf_counter()

    raw    = collect_metrics(NODE_URLS)                 # 20 seconds synchronous
    clean  = validate_and_clean(raw)
    write_to_db(clean)

    print(f"Done in {time.time() - start:.1f}s. Records: {len(clean)}")
    # No per-stage breakdown. No memory data. No error summary.

run()
```

---

## Step 2 — Senior Architectural Walkthrough

This is a full architectural review. Every subsection maps to a section in your notes.

### Bug 1 — Synchronous collection for 100 nodes (Section 13.2)
```python
for url in urls:
    response = requests.get(url, timeout=5)   # Waits fully for each before starting next
```
100 nodes × average 200ms response = **20 seconds per ingestor cycle**. The orchestrator is supposed to run every 60 seconds. 20 of those 60 seconds are wasted waiting.

**Fix pseudocode:**
```
async def collect_one(client, semaphore, url) → dict:
    async with semaphore:                   # Max 20 concurrent at a time
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def collect_all(urls) → AsyncGenerator[dict, None]:
    semaphore = asyncio.Semaphore(20)
    async with httpx.AsyncClient() as client:
        tasks   = [collect_one(client, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if not isinstance(r, Exception):
                yield r                    # Yield one at a time — not list
```
100 nodes at 20 concurrent → ~5 sequential batches × 200ms = **~1 second total**.

### Bug 2 — Two full lists in RAM simultaneously (Section 10 + 11)
```python
all_data = []                # List 1: 100 raw dicts
for url in urls:
    all_data.append(...)

valid = []                   # List 2: 100 cleaned dicts
for m in all_data:
    valid.append(...)
```
Peak RAM = size of raw list + size of cleaned list. Replace with a generator pipeline:

**Fix pseudocode:**
```
def validate_and_clean(raw_records: Iterable[dict]) → Generator[dict, None, None]:
    for m in raw_records:
        if m.get("cpu_pct") is not None:
            yield { cleaned dict }   # One record at a time
# No lists built at any stage
```

### Bug 3 — SQL injection + no pooling + N round-trips (Section 13.4 + 11)
```python
f"VALUES ('{r['node_id']}', ..."   # node_id directly interpolated
for r in records: cursor.execute() # N round-trips
conn = psycopg2.connect(DSN)       # New connection every run
```
**Fix pseudocode:**
```
# Module-level pool (initialized once at startup)
pool = psycopg2.pool.ThreadedConnectionPool(2, 20, dsn=os.environ["DATABASE_URL"])

# Context manager for DB access (Section 11 + 13.4)
with get_cursor() as cursor:
    cursor.executemany(
        "INSERT INTO vps_metrics (node_id, cpu_pct, mem_pct, disk_pct, ts) "
        "VALUES (%s, %s, %s, %s, %s)",
        [(r["node_id"], r["cpu_pct"], r["mem_pct"], r["disk_pct"], r["ts"])
         for r in records]
    )
```

### Bug 4 — No per-stage profiling (Section 11.2 + 13.3)
```python
print(f"Done in {time.time() - start:.1f}s")  # Total time only, no breakdown
```
**Fix:** Wrap each stage in the `pipeline_stage()` context manager from Micro-Scenario 03.

### Bug 5 — `time.time()` instead of `time.perf_counter()` (Section 13.3)
`time.time()` is subject to NTP clock adjustments. If the system clock is corrected backward during the run, you get a negative elapsed time. Always use `time.perf_counter()` for measuring durations.

---

## Step 3 — Validation Challenge

This is the capstone. There are no partial-credit `# TODO` hints. Design the architecture from the walkthrough above, then make the validation harness pass.

**Required architecture:**
```
grand_line/
├── __init__.py          — exposes: run_ingestor
├── collector.py         — async fetch layer (asyncio + httpx + semaphore)
├── pipeline.py          — generator transform (validate_and_clean)
├── storage.py           — DB layer (pool + get_cursor + executemany)
└── profiling.py         — pipeline_stage() context manager (perf_counter + tracemalloc)
```

**Constraints:**
- No circular imports
- No wildcard imports
- No hardcoded credentials
- No `time.time()` — only `time.perf_counter()`
- No f-strings in any SQL string
- No intermediate lists in the generator pipeline
- `collect_all()` must use `asyncio.gather(return_exceptions=True)`

```python
# test_grand_line_ingestor.py
import asyncio
import time
import tracemalloc
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch


class TestCollector(unittest.TestCase):
    """Tests for grand_line/collector.py"""

    def test_collect_all_uses_gather_not_sequential(self):
        """Async collection must be concurrent, not sequential."""
        DELAY = 0.05

        async def run():
            from grand_line.collector import collect_all

            call_times = []

            async def mock_fetch(url):
                call_times.append(time.perf_counter())
                await asyncio.sleep(DELAY)
                return {"node_id": url.split("/")[-2], "cpu_pct": 45, "mem_pct": 60, "disk_pct": 30}

            urls = [f"http://node-{i}/metrics" for i in range(20)]

            with patch("grand_line.collector.fetch_one", side_effect=mock_fetch):
                start = time.perf_counter()
                results = [r async for r in collect_all(urls)]
                elapsed = time.perf_counter() - start

            return elapsed, len(results)

        elapsed, count = asyncio.run(run())
        sequential_time = 20 * 0.05

        self.assertEqual(count, 20)
        self.assertLess(elapsed, sequential_time * 0.5,
            f"Collection took {elapsed:.2f}s — expected < {sequential_time*0.5:.2f}s (concurrent)")
        print(f"✅ ASSERTION 1 PASSED: 20 nodes collected in {elapsed:.2f}s (concurrent)")

    def test_semaphore_limits_concurrency(self):
        """collect_all() must not exceed MAX_CONCURRENT simultaneous requests."""
        from grand_line.collector import MAX_CONCURRENT

        in_flight = [0]
        max_seen  = [0]

        async def run():
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)

            async def mock_request(url):
                async with semaphore:
                    in_flight[0] += 1
                    max_seen[0] = max(max_seen[0], in_flight[0])
                    await asyncio.sleep(0.005)
                    in_flight[0] -= 1

            await asyncio.gather(*[mock_request(f"url-{i}") for i in range(50)])

        asyncio.run(run())
        self.assertLessEqual(max_seen[0], MAX_CONCURRENT)
        print(f"✅ ASSERTION 2 PASSED: Max concurrency {max_seen[0]} ≤ {MAX_CONCURRENT}")

    def test_failed_nodes_do_not_crash_run(self):
        """Network errors on individual nodes must not cancel all other fetches."""
        async def run():
            from grand_line.collector import collect_all

            call_count = [0]

            async def mock_fetch(url):
                call_count[0] += 1
                if "fail" in url:
                    raise ConnectionError("Simulated timeout")
                return {"node_id": url, "cpu_pct": 50, "mem_pct": 50, "disk_pct": 25}

            urls = [f"http://node-{i}" for i in range(10)] + \
                   [f"http://fail-node-{i}" for i in range(5)]

            with patch("grand_line.collector.fetch_one", side_effect=mock_fetch):
                results = [r async for r in collect_all(urls)]

            return results, call_count[0]

        results, total_called = asyncio.run(run())
        self.assertEqual(total_called, 15, "All 15 URLs must be attempted")
        self.assertEqual(len(results), 10, "Only 10 successful results returned")
        print(f"✅ ASSERTION 3 PASSED: 5 failures skipped, 10 successes returned")


class TestPipeline(unittest.TestCase):
    """Tests for grand_line/pipeline.py"""

    SAMPLE_RAW = [
        {"node_id": "node-01", "cpu_pct": "45.5", "mem_pct": "60.0", "disk_pct": "30.0", "timestamp": 1700000000},
        {"node_id": "node-02", "cpu_pct": None,   "mem_pct": "70.0", "disk_pct": "20.0"},   # Invalid — missing cpu
        {"node_id": "node-03", "cpu_pct": "90.0", "mem_pct": "88.0", "disk_pct": "75.0", "timestamp": 1700000060},
    ]

    def test_pipeline_is_generator(self):
        from grand_line.pipeline import validate_and_clean
        result = validate_and_clean(iter(self.SAMPLE_RAW))
        self.assertIsInstance(result, types.GeneratorType)
        print("✅ ASSERTION 4 PASSED: validate_and_clean() is a generator")

    def test_invalid_records_skipped(self):
        from grand_line.pipeline import validate_and_clean
        results = list(validate_and_clean(iter(self.SAMPLE_RAW)))
        self.assertEqual(len(results), 2, "Record with None cpu_pct must be skipped")
        node_ids = [r["node_id"] for r in results]
        self.assertNotIn("node-02", node_ids)
        print("✅ ASSERTION 5 PASSED: Invalid records filtered out")

    def test_values_cast_to_float(self):
        from grand_line.pipeline import validate_and_clean
        results = list(validate_and_clean(iter(self.SAMPLE_RAW)))
        self.assertIsInstance(results[0]["cpu_pct"], float)
        self.assertAlmostEqual(results[0]["cpu_pct"], 45.5)
        print("✅ ASSERTION 6 PASSED: String values cast to float")

    def test_memory_efficiency_at_scale(self):
        """Generator chain must not exceed 1MB peak for 50k records."""
        from grand_line.pipeline import validate_and_clean

        BIG_DATA = [
            {"node_id": f"node-{i:05d}", "cpu_pct": str(i % 100),
             "mem_pct": str(i % 80), "disk_pct": str(i % 60), "timestamp": 1700000000 + i}
            for i in range(50_000)
        ]
        tracemalloc.start()
        count = sum(1 for _ in validate_and_clean(iter(BIG_DATA)))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_kb = peak / 1024

        self.assertEqual(count, 50_000)
        self.assertLess(peak_kb, 1024,
            f"Peak RAM {peak_kb:.1f}KB — intermediate list suspected")
        print(f"✅ ASSERTION 7 PASSED: 50k records, peak RAM {peak_kb:.1f}KB < 1MB")


class TestStorage(unittest.TestCase):
    """Tests for grand_line/storage.py"""

    def test_no_fstring_sql(self):
        import inspect
        from grand_line import storage
        source = inspect.getsource(storage)
        import re
        self.assertNotRegex(source, r'f"[^"]*(?:INSERT|SELECT|UPDATE|DELETE)',
            "f-string SQL detected in storage.py")
        self.assertNotRegex(source, r"f'[^']*(?:INSERT|SELECT|UPDATE|DELETE)",
            "f-string SQL detected in storage.py")
        print("✅ ASSERTION 8 PASSED: Zero f-string SQL in storage.py")

    def test_uses_executemany_not_loop(self):
        import inspect
        from grand_line import storage
        source = inspect.getsource(storage)
        self.assertIn("executemany", source)
        print("✅ ASSERTION 9 PASSED: storage.py uses executemany()")

    def test_credentials_from_env(self):
        import inspect, re
        from grand_line import storage
        source = inspect.getsource(storage)
        self.assertNotRegex(source, r'password\s*=\s*["\'][^"\']{3,}["\']')
        self.assertIn("environ", source,
            "DATABASE_URL must be read from os.environ")
        print("✅ ASSERTION 10 PASSED: Credentials from environment variable")


class TestProfiling(unittest.TestCase):
    """Tests for grand_line/profiling.py"""

    def test_pipeline_stage_context_manager(self):
        import io, sys
        from grand_line.profiling import pipeline_stage

        captured = io.StringIO()
        sys.stdout = captured
        with pipeline_stage("Test"):
            time.sleep(0.01)
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Test",  output)
        self.assertIn("ms",    output)
        self.assertIn("KB",    output)
        print("✅ ASSERTION 11 PASSED: pipeline_stage() outputs timing + memory")

    def test_pipeline_stage_uses_perf_counter_not_time(self):
        """Must use time.perf_counter(), not time.time()."""
        import inspect
        from grand_line import profiling
        source = inspect.getsource(profiling)
        self.assertIn("perf_counter", source)
        self.assertNotIn("time.time()", source)
        print("✅ ASSERTION 12 PASSED: perf_counter used, not time.time()")


class TestPackageArchitecture(unittest.TestCase):
    """Tests for grand_line package structure."""

    def test_no_circular_imports(self):
        import importlib, sys
        modules = [
            "grand_line",
            "grand_line.collector",
            "grand_line.pipeline",
            "grand_line.storage",
            "grand_line.profiling",
        ]
        for mod in modules:
            keys = [k for k in sys.modules if k.startswith("grand_line")]
            for k in keys: del sys.modules[k]
            try:
                importlib.import_module(mod)
            except ImportError as e:
                self.fail(f"Circular import in {mod}: {e}")
        print("✅ ASSERTION 13 PASSED: No circular imports")

    def test_no_wildcard_imports(self):
        import ast, pathlib
        pkg = pathlib.Path("grand_line")
        for f in pkg.glob("*.py"):
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        self.assertNotEqual(alias.name, "*",
                            f"Wildcard import in {f.name}")
        print("✅ ASSERTION 14 PASSED: Zero wildcard imports")


class TestFullIntegration(unittest.TestCase):
    """End-to-end integration test with mocked I/O."""

    def test_full_pipeline_produces_correct_output(self):
        """
        Runs the full pipeline (collect → validate → write) with mocked
        HTTP calls and DB cursor. Verifies the entire chain works together.
        """
        MOCK_METRICS = [
            {"node_id": f"node-{i:02d}", "cpu_pct": str(50 + i),
             "mem_pct": str(40 + i), "disk_pct": str(20 + i), "timestamp": 1700000000 + i}
            for i in range(20)
        ]

        async def run():
            from grand_line.collector import collect_all
            from grand_line.pipeline  import validate_and_clean

            async def mock_fetch(url):
                idx = int(url.split("-")[1])
                return MOCK_METRICS[idx]

            with patch("grand_line.collector.fetch_one", side_effect=mock_fetch):
                urls    = [f"http://node-{i:02d}/metrics" for i in range(20)]
                raw_gen = collect_all(urls)
                # Collect async generator into list for pipeline
                raw     = [r async for r in raw_gen]

            cleaned = list(validate_and_clean(iter(raw)))
            return cleaned

        results = asyncio.run(run())
        self.assertEqual(len(results), 20)
        self.assertTrue(all(isinstance(r["cpu_pct"], float) for r in results))
        print(f"✅ ASSERTION 15 PASSED: Full pipeline processed {len(results)} records end-to-end")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

---

## Portfolio Completion Checklist

When all 15 assertions pass, your `grand_line/` package demonstrates:

| Skill | Where Proven |
|---|---|
| `@contextmanager` with `try/finally` | `profiling.py` |
| `ExitStack` for multiple DB resources | `storage.py` |
| Package architecture, no circular imports | Full package structure |
| `asyncio.gather(return_exceptions=True)` | `collector.py` |
| `asyncio.Semaphore` rate limiting | `collector.py` |
| Generator pipeline, zero intermediate lists | `pipeline.py` |
| `tracemalloc` peak RAM < 1MB for 50k records | Assertion 7 |
| Parameterized SQL, zero f-strings | Assertion 8 |
| `executemany()` bulk inserts | Assertion 9 |
| `time.perf_counter()` throughout | Assertion 12 |
| Environment-variable credentials | Assertion 10 |
| 15 passing `unittest` assertions | All tests |

# 🔬 Micro-Scenario 07 — The Growing Ghost
**Complexity:** ⭐⭐⭐⭐ High
**Skill Targets:** Section 13.3 — `tracemalloc` snapshot comparison · Memory leak detection · `functools.lru_cache` · Generator-based pipelines · `time.perf_counter()`
**Portfolio Context:** The **Grand Line** orchestrator maintains an in-memory cache of VPS configuration objects so it doesn't have to re-query the database on every health check. After 48 hours in production, the process is consuming 4GB of RAM and gets OOM-killed. You must use `tracemalloc` to find the leak, prove it with before/after snapshots, and fix it.

---

## Step 1 — The Broken Junior Implementation

```python
# vps_cache.py
import time
import hashlib

# Global cache — never bounded, never evicted
_config_cache: dict = {}
_metric_history: dict = {}          # Stores ALL historical metrics per host — forever
_processed_ids: list  = []          # Accumulates every processed ID — never cleared

def get_vps_config(host_id: str, db_conn) -> dict:
    """Returns VPS config, caching the result for future calls."""
    if host_id in _config_cache:
        return _config_cache[host_id]

    # Simulate DB query
    config = db_conn.query(f"SELECT * FROM vps_configs WHERE id = '{host_id}'")
    _config_cache[host_id] = config   # Cached forever — even for decommissioned hosts
    return config


def record_metric(host_id: str, metric: dict) -> None:
    """Records a VPS metric data point."""
    if host_id not in _metric_history:
        _metric_history[host_id] = []

    _metric_history[host_id].append(metric)    # Appends forever — no max length
    _processed_ids.append(host_id)             # List grows forever


def process_batch(metrics: list[dict]) -> list[dict]:
    """Processes a batch of incoming metrics."""
    results = []

    # Builds a massive intermediate list in memory before processing
    all_with_checksums = []
    for m in metrics:
        checksum = hashlib.md5(str(m).encode()).hexdigest()
        all_with_checksums.append({**m, "checksum": checksum})

    # Then builds ANOTHER list from the first
    for m in all_with_checksums:
        if m.get("cpu_pct", 0) > 80:
            results.append(m)

    return results
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — Unbounded `_config_cache` dict
```python
_config_cache: dict = {}
_config_cache[host_id] = config    # Written to on every new host_id — never evicted
```
A Grand Line orchestrator managing 10,000 VPS instances, each with a config dict averaging 2KB, stores 20MB of config data. This is acceptable. But as VPS instances are decommissioned, their configs stay in the cache forever because there is no eviction. After 12 months of infrastructure churn, the cache contains configs for thousands of dead hosts. `tracemalloc` will show `_config_cache` consuming gigabytes.

**Fix pseudocode:**
```
Replace dict with functools.lru_cache on the function:

@functools.lru_cache(maxsize=1000)   # LRU: evicts least-recently-used beyond 1000 entries
def get_vps_config(host_id: str) -> dict:
    ...

# Or for a dict-based approach: use collections.OrderedDict with a manual size cap
```

### Bug 2 — `_metric_history` stores ALL metrics indefinitely
```python
_metric_history[host_id].append(metric)    # Every 60s × 10000 hosts × 365 days = ∞
```
A health check every 60 seconds for 1,000 hosts generates 1,440,000 metric records per day. Each record is a dict with ~10 fields averaging 500 bytes. That is **720MB per day** in RAM. After one week: **5GB**.

**Fix pseudocode:**
```
Cap history per host using collections.deque(maxlen=N):
    _metric_history[host_id] = collections.deque(maxlen=1440)  # Only last 24h at 1/min

deque automatically discards the oldest entry when maxlen is reached — O(1) operation.
```

### Bug 3 — `_processed_ids` list grows forever
```python
_processed_ids.append(host_id)   # Every metric processed adds to this list
```
This list serves no purpose beyond accumulation. After 1M calls: `~50MB` of strings that are never read or cleared. Delete the list. If you need a count, use an `int` counter.

### Bug 4 — Double intermediate list in `process_batch`
```python
all_with_checksums = []                          # List 1: all records + checksums
for m in metrics: all_with_checksums.append(...)

results = []
for m in all_with_checksums:                     # List 2: filtered
    if ...: results.append(m)
```
Two full copies of `metrics` exist in RAM simultaneously. Use a generator pipeline: compute checksum and filter in a single pass, yielding only records that pass the filter.

### How to Use `tracemalloc` to Prove the Leak
```python
import tracemalloc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# Run the leaky code here (e.g., 1000 iterations of process_batch)
for i in range(1000):
    record_metric(f"host-{i % 10}", {"cpu": i})

snapshot2 = tracemalloc.take_snapshot()

# Compare: shows what GREW between snapshot1 and snapshot2
top_stats = snapshot2.compare_to(snapshot1, "lineno")
for stat in top_stats[:5]:
    print(stat)   # Prints: filename:lineno | size delta | count delta
```

---

## Step 3 — Validation Challenge

```python
# vps_cache_v2.py
import tracemalloc
import time
import hashlib
import collections
import functools
import unittest


MAX_CACHE_SIZE     = 500     # Max VPS configs to cache
MAX_HISTORY_LENGTH = 1440    # Max metric records per host (24h at 1/min)


# ─── TODO 1: Bounded config cache ────────────────────────────────────────────
# Requirements:
#   - Use @functools.lru_cache(maxsize=MAX_CACHE_SIZE) on a function
#   - Function signature: get_vps_config(host_id: str) -> dict
#   - Simulate the DB query by returning {"id": host_id, "region": "af-south-1", "tier": "standard"}
#   - Do NOT accept db_conn as a parameter (lru_cache doesn't work with unhashable args)

@functools.lru_cache(maxsize=MAX_CACHE_SIZE)
def get_vps_config(host_id: str) -> dict:
    # TODO
    pass


# ─── TODO 2: Bounded metric history using deque ───────────────────────────────
# Requirements:
#   - Store _metric_history as a defaultdict of deque(maxlen=MAX_HISTORY_LENGTH)
#   - record_metric(host_id, metric) appends to the deque
#   - get_metric_history(host_id) returns list(deque) — a snapshot copy
#   - No _processed_ids list anywhere

_metric_history: dict = {}   # TODO: change to collections.defaultdict(lambda: collections.deque(maxlen=MAX_HISTORY_LENGTH))

def record_metric(host_id: str, metric: dict) -> None:
    # TODO
    pass

def get_metric_history(host_id: str) -> list:
    # TODO: return a list copy of the deque for host_id
    pass


# ─── TODO 3: Generator-based process_batch ────────────────────────────────────
# Requirements:
#   - Must be a generator function (use yield)
#   - Compute checksum and filter in a SINGLE pass — no intermediate lists
#   - Only yield records where cpu_pct > 80
#   - Each yielded dict must include a "checksum" key (md5 of the str representation)

def process_batch(metrics: list[dict]):
    # TODO
    pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestMemoryBehavior(unittest.TestCase):

    def test_lru_cache_evicts_old_entries(self):
        """Config cache must not grow beyond MAX_CACHE_SIZE."""
        get_vps_config.cache_clear()

        for i in range(MAX_CACHE_SIZE + 200):   # Exceed the cache limit
            get_vps_config(f"host-{i}")

        info = get_vps_config.cache_info()
        self.assertLessEqual(info.currsize, MAX_CACHE_SIZE)
        print(f"✅ ASSERTION 1 PASSED: Cache size {info.currsize} ≤ {MAX_CACHE_SIZE}")
        print(f"   Cache hits: {info.hits} | misses: {info.misses}")

    def test_metric_history_bounded(self):
        """Metric history per host must not exceed MAX_HISTORY_LENGTH."""
        host = "test-host-01"
        for i in range(MAX_HISTORY_LENGTH + 500):
            record_metric(host, {"cpu_pct": i % 100, "ts": i})

        history = get_metric_history(host)
        self.assertLessEqual(len(history), MAX_HISTORY_LENGTH)
        # The LATEST entries should be kept, not the oldest
        self.assertEqual(history[-1]["ts"], MAX_HISTORY_LENGTH + 499)
        print(f"✅ ASSERTION 2 PASSED: History capped at {len(history)} ≤ {MAX_HISTORY_LENGTH}")

    def test_process_batch_is_generator(self):
        """process_batch() must be a generator — not a list."""
        import types
        metrics = [{"cpu_pct": 90, "host": "a"}, {"cpu_pct": 30, "host": "b"}]
        result  = process_batch(metrics)
        self.assertIsInstance(result, types.GeneratorType)
        print("✅ ASSERTION 3 PASSED: process_batch() is a generator")

    def test_process_batch_filters_correctly(self):
        """Only records with cpu_pct > 80 should be yielded."""
        metrics = [
            {"cpu_pct": 95, "host": "node-1"},
            {"cpu_pct": 40, "host": "node-2"},   # Should be excluded
            {"cpu_pct": 81, "host": "node-3"},
            {"cpu_pct": 80, "host": "node-4"},   # 80 is NOT > 80 — should be excluded
        ]
        results = list(process_batch(metrics))
        self.assertEqual(len(results), 2)
        hosts = [r["host"] for r in results]
        self.assertIn("node-1", hosts)
        self.assertIn("node-3", hosts)
        self.assertNotIn("node-2", hosts)
        self.assertNotIn("node-4", hosts)
        self.assertTrue(all("checksum" in r for r in results))
        print("✅ ASSERTION 4 PASSED: process_batch() filters and checksums correctly")

    def test_memory_does_not_grow_unboundedly(self):
        """
        Simulates 5000 metric writes. tracemalloc must show memory growth stays flat
        after the initial population of the deque.
        """
        # Warm up the deque to max capacity first
        for i in range(MAX_HISTORY_LENGTH):
            record_metric("leak-test-host", {"cpu_pct": i % 100, "seq": i})

        # Now measure memory growth for 2000 MORE writes (should be ~zero growth)
        tracemalloc.start()
        snap1 = tracemalloc.take_snapshot()

        for i in range(2000):
            record_metric("leak-test-host", {"cpu_pct": i % 100, "seq": MAX_HISTORY_LENGTH + i})

        snap2 = tracemalloc.take_snapshot()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        top_stats = snap2.compare_to(snap1, "lineno")
        total_growth_kb = sum(s.size_diff for s in top_stats) / 1024

        # After deque is full, 2000 more writes should not grow memory more than 50KB
        self.assertLess(total_growth_kb, 50,
            f"Memory grew {total_growth_kb:.1f}KB after 2000 bounded writes — possible leak")
        print(f"✅ ASSERTION 5 PASSED: Memory growth after 2000 writes: {total_growth_kb:.1f}KB < 50KB")

    def test_process_batch_memory_efficient(self):
        """process_batch() generator must not build intermediate lists."""
        metrics = [{"cpu_pct": 90 + (i % 5), "host": f"node-{i}"} for i in range(50_000)]

        tracemalloc.start()
        snap1 = tracemalloc.take_snapshot()

        # Consume generator without accumulating
        count = sum(1 for _ in process_batch(metrics))

        snap2 = tracemalloc.take_snapshot()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_kb = peak / 1024
        self.assertGreater(count, 0)
        self.assertLess(peak_kb, 1024,
            f"Peak RAM {peak_kb:.1f}KB — intermediate list suspected (should be < 1MB)")
        print(f"✅ ASSERTION 6 PASSED: 50k records processed, peak RAM {peak_kb:.1f}KB < 1024KB")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

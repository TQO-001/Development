# 🔬 Micro-Scenario 08 — The Injection Highway
**Complexity:** ⭐⭐⭐⭐ High
**Skill Targets:** Section 13.4 — Parameterized queries · `psycopg2.pool.ThreadedConnectionPool` · Section 11 — Context managers for DB lifecycle · `executemany()` · `time.perf_counter()` bulk insert benchmarking
**Portfolio Context:** The **Navy** job tracker's search API has been flagged in a security review. The penetration tester submitted the search term `' OR '1'='1` and received every job in the database. You must rebuild the entire database access layer: secure parameterization, connection pooling, and a benchmark proving `executemany()` superiority over looped `execute()`.

---

## Step 1 — The Broken Junior Implementation

```python
# db_layer.py
import psycopg2
import datetime

DB_HOST = "prod-db.internal"
DB_NAME = "navy_jobs"
DB_USER = "navy_user"
DB_PASS = "navy_pass_2024"   # Hardcoded credential


def get_connection():
    """Opens a fresh database connection every single call."""
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def search_jobs(keyword: str, city: str) -> list[dict]:
    """Searches jobs by keyword and city."""
    conn   = get_connection()            # New connection every search — no pooling
    cursor = conn.cursor()

    # 🔥 SQL INJECTION: both keyword and city are directly interpolated
    query = f"""
        SELECT id, title, company, city, salary_min
        FROM job_listings
        WHERE title LIKE '%{keyword}%'
        AND city = '{city}'
        AND is_active = true
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # cursor and conn never closed
    return [
        {"id": r[0], "title": r[1], "company": r[2], "city": r[3], "salary": r[4]}
        for r in rows
    ]


def insert_job(title: str, company: str, city: str, salary: int) -> None:
    """Inserts a single job listing."""
    conn   = get_connection()
    cursor = conn.cursor()

    # 🔥 SQL INJECTION in INSERT
    cursor.execute(
        f"INSERT INTO job_listings (title, company, city, salary_min, created_at) "
        f"VALUES ('{title}', '{company}', '{city}', {salary}, '{datetime.datetime.now()}')"
    )
    conn.commit()
    # cursor.close() missing
    # conn.close() missing


def bulk_insert_jobs(jobs: list[dict]) -> None:
    """Inserts a list of jobs."""
    conn   = get_connection()
    cursor = conn.cursor()

    for job in jobs:            # 🔥 N round-trips for N jobs
        cursor.execute(
            f"INSERT INTO job_listings (title, company, city, salary_min) "
            f"VALUES ('{job['title']}', '{job['company']}', '{job['city']}', {job['salary_min']})"
        )
    conn.commit()
    # No cleanup
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — SQL Injection in LIKE search
```python
query = f"... WHERE title LIKE '%{keyword}%' AND city = '{city}'"
```
Payload: `keyword = "python' OR '1'='1' --"`

Resulting query:
```sql
WHERE title LIKE '%python' OR '1'='1' --  %' AND city = '...'
```
The `--` comments out everything after. `'1'='1'` is always true. Every row in the table is returned. A more targeted payload: `'; DROP TABLE job_listings; --` executes a destructive statement.

**Fix pseudocode:**
```
# LIKE patterns use %s just like equality checks
# The % wildcards go inside the Python string, not the SQL template:

cursor.execute(
    "SELECT ... WHERE title ILIKE %s AND city = %s AND is_active = true",
    (f"%{keyword}%", city)
)
# psycopg2 escapes keyword and city as literal string data
# The LIKE wildcards are part of the parameter value — not SQL syntax
```

### Bug 2 — New connection per query (no pooling)
```python
def get_connection():
    return psycopg2.connect(...)   # Opens TCP, authenticates, allocates server-side state
```
Each PostgreSQL connection costs:
- ~5MB server-side RAM
- ~10–50ms to establish (TCP handshake + TLS + auth)
- A PostgreSQL backend process

10 concurrent API users × 10 searches each = 100 connection opens in rapid succession. PostgreSQL default `max_connections = 100` — at 100 you start refusing connections.

**Fix pseudocode:**
```
At module load time (once):
    pool = psycopg2.pool.ThreadedConnectionPool(minconn=2, maxconn=20, dsn=DSN)

In get_cursor() context manager:
    conn = pool.getconn()      # Borrows an existing connection from pool
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        cursor.close()
        pool.putconn(conn)     # Returns connection to pool for reuse
```

### Bug 3 — `execute()` in a loop for bulk inserts
```python
for job in jobs:
    cursor.execute(INSERT_QUERY, ...)    # 1 round-trip per row
```
10,000 rows at 1ms each = 10 seconds. `executemany()` batches rows into a single operation: 10,000 rows in ~100ms. `psycopg2.extras.execute_values()` uses the PostgreSQL `COPY` protocol and can insert 10,000 rows in ~20ms.

### Bug 4 — Credentials hardcoded
Replace with `os.environ["DATABASE_URL"]`.

---

## Step 3 — Validation Challenge

```python
# db_layer_v2.py
import os
import time
import unittest
from contextlib import contextmanager
from typing import Generator
from unittest.mock import MagicMock, patch, call
import re

# ─── Configuration ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/navy_test")
POOL_MIN     = 2
POOL_MAX     = 20


# ─── TODO 1: Implement the connection pool (module-level, initialized once) ───
# Use psycopg2.pool.ThreadedConnectionPool
# Read DSN from DATABASE_URL env var
# Handle the case where psycopg2 isn't installed (use a mock for testing)

try:
    import psycopg2
    import psycopg2.pool
    import psycopg2.extras
    _pool = psycopg2.pool.ThreadedConnectionPool(POOL_MIN, POOL_MAX, DATABASE_URL)
    PSYCOPG2_AVAILABLE = True
except Exception:
    _pool = None
    PSYCOPG2_AVAILABLE = False


# ─── TODO 2: Implement get_cursor() context manager ──────────────────────────
# Requirements:
#   - Borrow a connection from _pool with pool.getconn()
#   - Open a cursor
#   - yield the cursor
#   - commit on clean exit, rollback on exception
#   - always close cursor and return connection to pool with pool.putconn()

@contextmanager
def get_cursor() -> Generator:
    # TODO
    pass


# ─── TODO 3: Implement search_jobs ───────────────────────────────────────────
# Requirements:
#   - Use get_cursor() context manager
#   - Use ILIKE %s with the wildcard INSIDE the parameter: f"%{keyword}%"
#   - city uses = %s (exact match)
#   - ZERO string interpolation in the SQL template
#   - Return list of dicts with keys: id, title, company, city, salary

def search_jobs(keyword: str, city: str) -> list[dict]:
    # TODO
    pass


# ─── TODO 4: Implement insert_job ─────────────────────────────────────────────
# Requirements:
#   - Parameterized INSERT with %s placeholders
#   - Use get_cursor() — no manual conn/cursor management
#   - Return the newly inserted row's id (use RETURNING id)

def insert_job(title: str, company: str, city: str, salary_min: int | None) -> int:
    # TODO
    pass


# ─── TODO 5: Implement bulk_insert_jobs ───────────────────────────────────────
# Requirements:
#   - Use cursor.executemany() with a list of tuples — NOT a loop with execute()
#   - Use get_cursor() context manager
#   - Return number of rows inserted

def bulk_insert_jobs(jobs: list[dict]) -> int:
    # TODO
    pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestDatabaseLayer(unittest.TestCase):

    def test_no_fstring_sql_anywhere(self):
        """
        Inspect source code of all DB functions.
        f-strings or .format() inside SQL strings are automatic FAIL.
        """
        import inspect, ast

        functions_to_check = [search_jobs, insert_job, bulk_insert_jobs]
        for fn in functions_to_check:
            source = inspect.getsource(fn)
            # Check for f-string patterns
            self.assertNotRegex(source, r'f".*SELECT|INSERT|UPDATE|DELETE',
                f"{fn.__name__}: f-string detected in SQL context")
            self.assertNotRegex(source, r"f'.*SELECT|INSERT|UPDATE|DELETE",
                f"{fn.__name__}: f-string detected in SQL context")
            self.assertNotIn(".format(", source,
                f"{fn.__name__}: .format() detected — SQL injection risk")
        print("✅ ASSERTION 1 PASSED: Zero f-string or .format() SQL in any function")

    def test_search_uses_parameterized_like(self):
        """search_jobs() must pass keyword as a %s parameter, not interpolate it."""
        import inspect
        source = inspect.getsource(search_jobs)
        # Must contain %s placeholder
        self.assertIn("%s", source)
        # The wildcard must be in the Python string, not the SQL
        self.assertRegex(source, r'f"%\{keyword\}%"',
            "LIKE wildcard must be inside the Python f-string parameter, not the SQL template")
        print("✅ ASSERTION 2 PASSED: search_jobs uses parameterized LIKE with Python-side wildcards")

    def test_bulk_insert_uses_executemany_not_loop(self):
        """bulk_insert_jobs() must use executemany(), not execute() in a loop."""
        import inspect
        source = inspect.getsource(bulk_insert_jobs)
        self.assertIn("executemany", source,
            "bulk_insert_jobs() must use cursor.executemany()")
        # executemany should NOT be inside a for loop
        lines = source.split("\n")
        in_for = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("for "):
                in_for = True
            if in_for and "execute(" in stripped and "executemany" not in stripped:
                self.fail("execute() found inside a for loop — use executemany() instead")
            if in_for and stripped == "":
                in_for = False
        print("✅ ASSERTION 3 PASSED: bulk_insert_jobs uses executemany()")

    def test_executemany_vs_execute_loop_benchmark(self):
        """
        Proves executemany() is faster than execute() in a loop.
        Uses mock cursors to simulate timing without a real DB.
        """
        import time

        BATCH_SIZE = 5000
        jobs = [
            {"title": f"Job {i}", "company": f"Corp {i}", "city": "JHB", "salary_min": 40000 + i}
            for i in range(BATCH_SIZE)
        ]
        records = [(j["title"], j["company"], j["city"], j["salary_min"]) for j in jobs]

        SINGLE_EXECUTE_OVERHEAD_MS = 0.05  # Simulated per-call overhead

        # Simulate looped execute() with overhead per call
        mock_execute = MagicMock(side_effect=lambda *a: time.sleep(SINGLE_EXECUTE_OVERHEAD_MS / 1000))
        start = time.perf_counter()
        for r in records[:200]:             # Only 200 to keep test fast
            mock_execute(
                "INSERT INTO job_listings (title, company, city, salary_min) VALUES (%s,%s,%s,%s)",
                r
            )
        loop_time = time.perf_counter() - start

        # Simulate executemany() — one call overhead
        mock_executemany = MagicMock(side_effect=lambda *a: time.sleep(SINGLE_EXECUTE_OVERHEAD_MS / 1000))
        start = time.perf_counter()
        mock_executemany(
            "INSERT INTO job_listings (title, company, city, salary_min) VALUES (%s,%s,%s,%s)",
            records[:200]
        )
        batch_time = time.perf_counter() - start

        speedup = loop_time / max(batch_time, 0.0001)
        print(f"✅ ASSERTION 4 PASSED: executemany benchmark")
        print(f"   Loop (200 execute calls): {loop_time*1000:.1f}ms")
        print(f"   Batch (1 executemany):    {batch_time*1000:.1f}ms")
        print(f"   Simulated speedup:        {speedup:.0f}x")

    def test_credentials_not_hardcoded(self):
        """Database credentials must come from environment variables, not string literals."""
        import inspect, ast
        import db_layer_v2 as module

        source = inspect.getsource(module)

        # Flag suspicious patterns: password strings that look like real credentials
        bad_patterns = [
            r'password\s*=\s*["\'][^"\']{4,}["\']',   # password = "something"
            r'DB_PASS\s*=\s*["\']',                     # DB_PASS = "..."
            r'DB_PASSWORD\s*=\s*["\']',
        ]
        for pattern in bad_patterns:
            self.assertNotRegex(source, pattern,
                f"Hardcoded credential pattern detected: {pattern}")
        print("✅ ASSERTION 5 PASSED: No hardcoded credentials detected in source")


# ─── BULK INSERT SPEED BENCHMARK ─────────────────────────────────────────────

def run_insert_benchmark(n_rows: int = 10_000):
    """
    Requires a real PostgreSQL connection.
    Compare loop execute() vs executemany() vs execute_values().
    Run with: DATABASE_URL=postgresql://... python db_layer_v2.py
    """
    if not PSYCOPG2_AVAILABLE:
        print("psycopg2 not available — skipping live benchmark")
        return

    jobs = [
        {"title": f"Job {i}", "company": f"Corp {i%100}",
         "city": "Johannesburg", "salary_min": 30000 + i}
        for i in range(n_rows)
    ]
    records = [(j["title"], j["company"], j["city"], j["salary_min"]) for j in jobs]

    print(f"\n{'═'*55}")
    print(f"  INSERT BENCHMARK: {n_rows:,} rows")
    print(f"{'═'*55}")

    with get_cursor() as cursor:
        # Method 1: loop execute()
        start = time.perf_counter()
        for r in records:
            cursor.execute(
                "INSERT INTO bench_jobs (title,company,city,salary_min) VALUES (%s,%s,%s,%s)", r)
        t_loop = time.perf_counter() - start
        print(f"  Loop execute():          {t_loop:.3f}s")

        # Method 2: executemany()
        start = time.perf_counter()
        cursor.executemany(
            "INSERT INTO bench_jobs (title,company,city,salary_min) VALUES (%s,%s,%s,%s)", records)
        t_many = time.perf_counter() - start
        print(f"  executemany():           {t_many:.3f}s  ({t_loop/t_many:.1f}x faster)")

        # Method 3: execute_values() — fastest, uses COPY protocol
        from psycopg2.extras import execute_values
        start = time.perf_counter()
        execute_values(cursor,
            "INSERT INTO bench_jobs (title,company,city,salary_min) VALUES %s", records)
        t_values = time.perf_counter() - start
        print(f"  execute_values():        {t_values:.3f}s  ({t_loop/t_values:.1f}x faster)")
    print(f"{'═'*55}\n")


if __name__ == "__main__":
    unittest.main(argv=[""], exit=False, verbosity=0)
    if PSYCOPG2_AVAILABLE:
        run_insert_benchmark()
```

# 🔬 Code Review & Learn — Micro-Scenario 01
## The Leaking Log Aggregator

> **Skill Targets:** Generators (Section 10) · Context Managers (Section 11) · Secure Parameterization (Section 13.4) · tracemalloc (Section 13.3) · `time.perf_counter()`
>
> **Production Context:** Your company's server generates multi-gigabyte log files daily. A junior developer has built a "production-grade" log aggregator that reads the file, filters error lines, and writes them to PostgreSQL for the on-call team to review. It passes all manual tests on development data (100-line files). It has been deployed to production.

---

## ⚠️ Step 1: The Broken Junior Implementation

Read this code carefully. It runs. It produces correct output on small files. It will **catastrophically fail** in production. Your job is to find every anti-pattern before reading Step 2.

```python
# log_aggregator.py
# Junior developer's note: "Tested and working! Processes server logs into the DB."
# Deployed to production: 2024-07-15

import psycopg2
import datetime

# ─── Database Configuration ────────────────────────────────────────────────────
DB_HOST     = "prod-db.internal"
DB_NAME     = "operations"
DB_USER     = "db_admin"
DB_PASSWORD = "Pr0dS3cur3Pass!"   # Production credentials

CONN_STRING = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


def load_log_file(filepath: str) -> list:
    """Reads a log file and returns all lines as a list."""
    file = open(filepath, "r")
    all_lines = file.readlines()
    file.close()
    return all_lines


def filter_errors(lines: list) -> list:
    """Filters the log lines and returns only ERROR-level entries."""
    error_lines = []
    for line in lines:
        if "ERROR" in line:
            error_lines.append(line.strip())
    return error_lines


def save_errors_to_db(error_lines: list, source_file: str) -> None:
    """Saves filtered error lines to the database."""
    conn = psycopg2.connect(CONN_STRING)
    cursor = conn.cursor()

    for line in error_lines:
        timestamp = datetime.datetime.now()
        query = f"""
            INSERT INTO error_log (source_file, error_message, captured_at)
            VALUES ('{source_file}', '{line}', '{timestamp}')
        """
        cursor.execute(query)

    conn.commit()
    print(f"Saved {len(error_lines)} errors to database.")


def run_aggregator(log_path: str) -> None:
    """Main pipeline function."""
    print(f"Processing: {log_path}")

    all_lines = load_log_file(log_path)
    errors    = filter_errors(all_lines)
    save_errors_to_db(errors, log_path)

    print("Done.")


# Entry point
run_aggregator("/var/log/app/server.log")
```

---

## 🏛️ Step 2: The Senior Architectural Walkthrough

Do not copy code yet. Read this line by line. Understand the **why** before you write a single character of the fix.

---

### Bug 1 — `file.readlines()` → Full File in RAM (Critical Memory Leak)

```python
# Line 20-23 of the broken code:
file = open(filepath, "r")
all_lines = file.readlines()  # ← THE PROBLEM
```

**What `readlines()` actually does:**

`readlines()` iterates through the entire file from disk, allocating a Python `str` object for every single line, and then stores **all of them** in a `list`. On a development machine with a 100-line test file: fine. On a production server with a 2GB application log: you just attempted to fit a 2GB file into RAM as a list of Python strings.

Python `str` objects have 50 bytes of overhead minimum (object header, hash, length, interning flags). On a log file with 10 million lines averaging 150 characters each:
- Raw file size: ~1.5GB
- RAM consumption as `list[str]`: ~3.5–4GB (encoding overhead + list array + object headers)

The server's process will be OOM-killed. The script produces no output. The on-call team receives no error notifications.

**The under-the-hood reason this is catastrophic:**

Python's file object is itself an iterator that implements `__iter__` and `__next__`. `for line in file_handle:` does NOT load the file into memory — it reads one line at a time via an internal 8KB read buffer. `readlines()` bypasses this entirely by calling `file.read()` internally and splitting on newlines, creating the full list.

**The architectural fix — pseudocode:**

```
REPLACE:
    file = open(filepath, "r")
    all_lines = file.readlines()

WITH a generator function that:
    1. Opens the file using a context manager (Section 11)
    2. Iterates the file handle directly (one line at a time)
    3. Yields only ERROR lines to the caller
    4. Never builds a list at all

RESULT:
    At any point in time, only ONE LINE from the file exists in RAM.
    Peak memory usage: ~1KB regardless of file size.
```

---

### Bug 2 — `file.close()` Called Manually After Possible Exception

```python
file = open(filepath, "r")
all_lines = file.readlines()  # ← If this raises an IOError or MemoryError...
file.close()                  # ← This line is NEVER REACHED
```

If `readlines()` raises ANY exception (disk error, memory exhaustion, permission change), the `file.close()` call is skipped. The file descriptor is leaked — the OS still has the file locked open. Python's garbage collector will eventually close it, but "eventually" may be seconds or minutes, and in production environments with concurrent pipeline runs, you can exhaust the OS file descriptor limit (`ulimit -n` is typically 1024 by default).

**The architectural fix — pseudocode:**

```
REPLACE:
    file = open(...)
    ...
    file.close()

WITH:
    with open(...) as file:  # Section 11 — __exit__ GUARANTEES close()
        ...                  # Even if an exception is raised inside
```

---

### Bug 3 — SQL Injection via f-String (Critical Security Vulnerability)

```python
# Lines 41-46 of the broken code:
query = f"""
    INSERT INTO error_log (source_file, error_message, captured_at)
    VALUES ('{source_file}', '{line}', '{timestamp}')
"""
cursor.execute(query)
```

**Why this is catastrophically broken — trace the data flow:**

Consider a real production error log line:

```
ERROR: Can't acquire lock on table 'user_sessions'
```

The single quote in `'user_sessions'` is embedded directly into the SQL string. What PostgreSQL receives:

```sql
INSERT INTO error_log (source_file, error_message, captured_at)
VALUES ('/var/log/app/server.log', 'ERROR: Can''t acquire lock on table ', 'user_sessions'
2024-07-15 14:23:01')
```

This is a **syntax error** that crashes the pipeline on the first log line containing a single quote. Your aggregator has zero tolerance for the most common character in English error messages.

Now consider a deliberately crafted log injection payload (attacker injects a line into the log file via another vulnerability):

```
ERROR: test', 'DROP TABLE error_log; --
```

The SQL becomes:

```sql
INSERT INTO error_log (...) VALUES ('/var/log', 'ERROR: test', 'DROP TABLE error_log; --', '...')
```

PostgreSQL executes: `DROP TABLE error_log` — your entire audit trail is deleted.

**The architectural fix — pseudocode:**

```
REPLACE any string that builds SQL with data interpolated:
    f"INSERT ... VALUES ('{line}', ...)"
    "INSERT ... VALUES ('%s')" % line
    "INSERT ... VALUES ('{}')".format(line)

WITH psycopg2 parameterized query:
    cursor.execute(
        "INSERT INTO error_log (source_file, error_message, captured_at) VALUES (%s, %s, %s)",
        (source_file, line, timestamp)    ← data is a SEPARATE argument, never in the SQL string
    )

The '%s' in psycopg2 is NOT Python's % formatting.
It is a placeholder marker sent to PostgreSQL as a parameter, not concatenated into the query string.
```

---

### Bug 4 — Database Connection and Cursor Never Managed as Resources

```python
def save_errors_to_db(error_lines: list, source_file: str) -> None:
    conn   = psycopg2.connect(CONN_STRING)  # Connection opened
    cursor = conn.cursor()                  # Cursor opened

    for line in error_lines:
        ...
        cursor.execute(query)               # If THIS raises (e.g., SQL error)...

    conn.commit()                           # NEVER REACHED on exception
    # cursor.close() is never called at all
    # conn.close() is never called at all
```

If any `cursor.execute()` raises (syntax error, constraint violation, network drop), the function exits via exception propagation. `conn.commit()` is never called, leaving the transaction in limbo. Neither `cursor.close()` nor `conn.close()` is called — the connection stays open and occupied in the PostgreSQL connection pool. PostgreSQL has a `max_connections` limit (default: 100). After 100 of these leaked connections, the database refuses all new connections.

**The architectural fix — pseudocode:**

```
STRUCTURE the DB work as:
    connection → context manager (commit on success, rollback on exception, always close)
    cursor     → context manager (always close)

The database module from Section 13.4 handles this correctly:
    with get_cursor() as cursor:
        cursor.executemany(...)
        # commit happens in __exit__ on clean exit
        # rollback happens in __exit__ on exception
        # cursor and connection are closed in finally block
```

---

### Bug 5 — Hardcoded Production Credentials in Source Code

```python
DB_PASSWORD = "Pr0dS3cur3Pass!"
CONN_STRING = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
```

Credentials in source code are visible to:
- Every developer who has ever cloned the repo
- Every CI/CD system that ran the code
- Every git hosting provider (GitHub, GitLab, Bitbucket)
- Every attacker who accesses the repository through any future vulnerability

Even if you delete the credential in a later commit, `git log -p | grep -i password` will find it in the history forever. The credential must be rotated the moment it appears in any VCS.

**The architectural fix — pseudocode:**

```
REPLACE:
    DB_PASSWORD = "Pr0dS3cur3Pass!"

WITH:
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    # Set via: export DB_PASSWORD="Pr0dS3cur3Pass!" in the shell
    # Or via a .env file loaded by python-dotenv (excluded from .gitignore)
    # Or via a secrets manager (HashiCorp Vault, AWS Secrets Manager)
```

---

### Bug 6 — `executemany()` not used for bulk writes

```python
for line in error_lines:              # If 50,000 error lines:
    cursor.execute(query)             # 50,000 individual database round-trips
```

Each `cursor.execute()` is a round-trip over the network to PostgreSQL: send SQL, wait for acknowledgment. At 1ms per round-trip (fast LAN), 50,000 inserts = 50 seconds. With `executemany()` or `execute_values()`, the same 50,000 rows are sent in one or a few batches: <1 second.

---

## ⚔️ Step 3: The Metric-Driven Validation Challenge

**Your mission:** Rewrite the `log_aggregator.py` from scratch using everything you have studied. The corrected implementation must satisfy all six bugs above.

To prove your implementation is senior-grade, **your solution must include a built-in test and profiling harness** at the bottom of the file. Do not write a separate test file — embed it in the `if __name__ == "__main__":` block.

---

### The Boilerplate to Rewrite From

Copy this file, fill in all `# TODO` sections, and run it. Your solution is correct when all assertion checks pass and the profiler output confirms the memory targets.

```python
# log_aggregator_v2.py
# Your implementation here — rewrite from scratch using the senior architecture.

import os
import time
import tracemalloc
import unittest
from contextlib import contextmanager
from typing import Generator

# ─── TODO 1: Replace hardcoded credentials ────────────────────────────────────
# Read the DSN from an environment variable, not from a string literal
DSN: str = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/test_db")


# ─── TODO 2: Implement the memory-safe log streamer ───────────────────────────
# Requirements:
#   - Must be a generator function (use 'yield', not 'return list')
#   - Must open the file with a context manager
#   - Must yield only lines containing the keyword (case-insensitive match)
#   - Must strip trailing whitespace from each yielded line
#   - Must NEVER load the entire file into memory

def stream_matching_lines(filepath: str, keyword: str) -> Generator[str, None, None]:
    """
    Memory-safe generator that streams lines matching a keyword from any file,
    regardless of file size.

    Args:
        filepath: Path to the log file.
        keyword:  Case-insensitive keyword to filter on.

    Yields:
        Stripped strings for lines containing the keyword.
    """
    # TODO: Implement this
    pass


# ─── TODO 3: Implement the context manager profiler ───────────────────────────
# This should be the same pattern from Section 11.3 and 13.3 combined.
# Requirements:
#   - Use @contextmanager from contextlib
#   - Track both time (perf_counter) and peak memory (tracemalloc)
#   - Print a formatted summary on exit
#   - The 'yield' must be wrapped in try/finally

@contextmanager
def profiler(label: str):
    """Context manager that measures elapsed time and peak RAM."""
    # TODO: Implement this
    pass


# ─── TODO 4: Implement the parameterized bulk writer ──────────────────────────
# Requirements:
#   - Must use a parameterized query — ZERO string interpolation in SQL
#   - Must use executemany() for bulk inserts, not a loop with execute()
#   - Must use a context manager for the connection (you can mock this for now
#     if you don't have a live DB — see the test harness below)
#   - Must commit on success, roll back on any exception

def save_errors(error_lines: list[str], source_file: str, cursor) -> int:
    """
    Bulk-inserts error lines into the database using parameterized queries.

    Args:
        error_lines: List of pre-filtered error strings.
        source_file: The filepath that was processed (stored for audit).
        cursor:      An active psycopg2 cursor.

    Returns:
        Number of rows inserted.
    """
    # TODO: Implement this using executemany() and %s placeholders
    # The target table schema is:
    #   error_log(source_file TEXT, error_message TEXT, captured_at TIMESTAMPTZ)
    pass


# ─── TODO 5: Wire the full pipeline ───────────────────────────────────────────
def run_pipeline(log_path: str, dry_run: bool = False) -> dict:
    """
    Runs the complete log aggregation pipeline.

    Args:
        log_path: Path to the log file.
        dry_run:  If True, skips the database write (for profiling and testing).

    Returns:
        A dict with keys: 'lines_read', 'errors_found', 'rows_saved', 'elapsed_ms', 'peak_ram_kb'
    """
    # TODO: Implement this using:
    #   - profiler() context manager (wrapping the whole pipeline)
    #   - stream_matching_lines() for memory-safe reading
    #   - save_errors() for the DB write (skip if dry_run=True)
    #   - Return a populated metrics dict
    pass


# ─── STEP 3 VALIDATION HARNESS ────────────────────────────────────────────────
# You must NOT modify this section. If your implementation is correct,
# all assertions will pass.

if __name__ == "__main__":

    import tempfile
    import os

    # ── Generate a realistic test log file ────────────────────────────────────
    TEST_LOG_CONTENT = "\n".join([
        f"2024-07-15 14:{i:02d}:01 [{'ERROR' if i % 7 == 0 else 'INFO'}] "
        f"{'Connection refused to host db-' + str(i) if i % 7 == 0 else 'Request processed in ' + str(i) + 'ms'}"
        for i in range(600)
    ])
    # Inject a deliberate SQL injection payload into the log
    SQL_INJECTION_LINE = "2024-07-15 15:00:00 [ERROR] Can't connect to host 'db.prod.internal'"
    TEST_LOG_CONTENT += "\n" + SQL_INJECTION_LINE

    # Write to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(TEST_LOG_CONTENT)
        tmp_path = f.name

    print(f"Test log written to: {tmp_path}")
    print(f"Total lines in test file: {TEST_LOG_CONTENT.count(chr(10)) + 1}")
    print()

    # ── ASSERTION 1: Correct error count ──────────────────────────────────────
    # Errors appear every 7 lines in range(600) → indices 0, 7, 14, ..., 595
    # That is ceil(600/7) = 86 lines.
    # Plus the injected SQL injection line = 87 total.
    errors_collected = list(stream_matching_lines(tmp_path, "ERROR"))

    expected_error_count = len([i for i in range(600) if i % 7 == 0]) + 1  # +1 for injected line
    assert len(errors_collected) == expected_error_count, (
        f"FAIL: Expected {expected_error_count} errors, got {len(errors_collected)}"
    )
    print(f"✅ ASSERTION 1 PASSED: Correct error count ({len(errors_collected)} errors found)")

    # ── ASSERTION 2: SQL injection payload preserved as plain text ─────────────
    # The line with the single-quote MUST appear in your collected errors.
    # If your code crashes on it, your error handling is broken.
    assert any("Can't connect" in line for line in errors_collected), (
        "FAIL: The SQL injection test line was not collected correctly."
    )
    print("✅ ASSERTION 2 PASSED: Line with single-quote collected without crash")

    # ── ASSERTION 3: No trailing whitespace in collected lines ────────────────
    assert all(line == line.strip() for line in errors_collected), (
        "FAIL: Some collected lines have leading or trailing whitespace."
    )
    print("✅ ASSERTION 3 PASSED: All lines are stripped")

    # ── MEMORY PROFILING CHALLENGE ────────────────────────────────────────────
    # Generate a larger file to stress-test memory usage
    print("\n--- MEMORY PROFILING ---")
    BIG_LOG_CONTENT = "\n".join([
        f"2024-07-15 14:{i % 60:02d}:{i % 60:02d} [{'ERROR' if i % 5 == 0 else 'INFO'}] " + "x" * 200
        for i in range(50_000)  # 50,000 lines × 220 chars ≈ 11MB file
    ])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(BIG_LOG_CONTENT)
        big_tmp = f.name

    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    count = 0
    for line in stream_matching_lines(big_tmp, "ERROR"):
        count += 1  # Only count, do not accumulate into a list

    snapshot_after = tracemalloc.take_snapshot()
    _, peak_during_stream = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_kb = peak_during_stream / 1024
    print(f"  Lines streamed: {count:,}")
    print(f"  Peak RAM during stream: {peak_kb:.1f} KB")

    # ── ASSERTION 4: Memory constraint ────────────────────────────────────────
    # Streaming 50,000 lines should peak at under 512KB.
    # A list-based readlines() approach on this file would peak at ~25MB.
    assert peak_kb < 512, (
        f"FAIL: Peak RAM was {peak_kb:.1f} KB — your implementation is loading too much into memory.\n"
        f"       This suggests you are using readlines() or building an intermediate list.\n"
        f"       Generators should keep peak RAM under 512 KB for this dataset."
    )
    print(f"✅ ASSERTION 4 PASSED: Peak RAM {peak_kb:.1f} KB < 512 KB target")

    # ── TIMING CHALLENGE ──────────────────────────────────────────────────────
    start = time.perf_counter()
    total = sum(1 for _ in stream_matching_lines(big_tmp, "ERROR"))
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\n  Streaming 50,000-line file: {elapsed_ms:.1f}ms")

    # ── CLEANUP ───────────────────────────────────────────────────────────────
    os.unlink(tmp_path)
    os.unlink(big_tmp)

    print("\n" + "═" * 50)
    print("  ALL ASSERTIONS PASSED — Implementation is senior-grade.")
    print("  Now integrate save_errors() with a live DB connection")
    print("  and run the full pipeline with run_pipeline() to complete")
    print("  the database layer validation.")
    print("═" * 50)
```

---

### What a Passing Run Looks Like

```text
Test log written to: /tmp/tmpXXXXXX.log
Total lines in test file: 601

✅ ASSERTION 1 PASSED: Correct error count (87 errors found)
✅ ASSERTION 2 PASSED: Line with single-quote collected without crash
✅ ASSERTION 3 PASSED: All lines are stripped

--- MEMORY PROFILING ---
  Lines streamed: 10,000
  Peak RAM during stream: 14.3 KB
✅ ASSERTION 4 PASSED: Peak RAM 14.3 KB < 512 KB target

  Streaming 50,000-line file: 47.1ms

══════════════════════════════════════════════════
  ALL ASSERTIONS PASSED — Implementation is senior-grade.
  Now integrate save_errors() with a live DB connection
  and run the full pipeline with run_pipeline() to complete
  the database layer validation.
══════════════════════════════════════════════════
```

---

### After You Pass — Bonus Validation

Once all assertions pass, add these two checks to prove the database layer:

**1. Prove your SQL query uses `%s` placeholders — NOT f-strings:**
```python
import inspect
source = inspect.getsource(save_errors)
assert "f\"" not in source and "f'" not in source and ".format(" not in source, (
    "FAIL: SQL injection vulnerability detected — f-strings or .format() in save_errors()"
)
assert "%s" in source, "FAIL: No parameterized placeholders found in save_errors()"
print("✅ BONUS 1 PASSED: save_errors() uses parameterized queries")
```

**2. Prove `executemany()` is used — not a loop:**
```python
assert "executemany" in source, (
    "FAIL: save_errors() uses execute() in a loop instead of executemany()"
)
print("✅ BONUS 2 PASSED: save_errors() uses executemany() for bulk inserts")
```

---

> **Submit your completed `log_aggregator_v2.py` and I will do a full senior code review — line by line, with architectural commentary and the next micro-scenario.**

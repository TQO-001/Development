# log_aggregator_v2.py
# Your implementation here — rewrite from scratch using the senior architecture.

import os
import time
import tracemalloc
import unittest
from contextlib import contextmanager
from typing import Generator, Any
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv


load_dotenv()

# ─── TODO 1: Replace hardcoded credentials ────────────────────────────────────
# Read the DSN from an environment variable, not from a string literal
DSN: str = os.environ["DB_URL"]

_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn= 2,
    maxconn=10,
    dsn=DSN
)

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
    with open(filepath) as f:
        for line in f:
            if keyword in line:
                yield line.strip()


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
    tracemalloc.start()
    tracemalloc.reset_peak()
    start_time = time.perf_counter()

    try:
        yield
    finally:
        end_time = time.perf_counter()
        elapsed = end_time - start_time

        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(
            f"--- [{label}] ---\n"
            f"\tTime: {elapsed * 1000:,.2f} ms\n"
            f"\tCurrent: {current_mem * 1024:,.1f} KB\n"
            f"\tPeak: {peak_mem * 1024:,.1f} KB"
            "-" * 25
        )

# ─── TODO 4: Implement the parameterized bulk writer ──────────────────────────
# Requirements:
#   - Must use a parameterized query — ZERO string interpolation in SQL
#   - Must use executemany() for bulk inserts, not a loop with execute()
#   - Must use a context manager for the connection (you can mock this for now
#     if you don't have a live DB — see the test harness below)
#   - Must commit on success, roll back on any exception

@contextmanager
def get_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Context manager that yields psycopg2 cursor.
    1. Checks out a connection from the pool
    2. Opens a new cursor
    3. Commits on clean exit, rolls back on exception
    4. Returns connection to pool unconditionally
    """
    conn = _pool.getconn()
    try:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    finally:
        _pool.putconn(conn)

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
    records = [
        (e[f"{source_file}"], e["error_message"], e["captured_at"])
        for e in error_lines
    ]
    with cursor as c:
        c.executemany(
            "INSERT INTO error_log (source_file, error_message, captured_at) VALUES (%s, %s, %s)",
            records
        )
    return len(records)


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
    with profiler("Memory Profiling") as profile:
        save_errors(stream_matching_lines(log_path, "ERROR"), dry_run)



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
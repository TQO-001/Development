## Section 13: Advanced Performance, Async & Data Integrity

This section covers four advanced but important topics: how Python actually handles multiple things happening at once (and a surprising limitation called the GIL), how to write code that juggles many slow operations efficiently using `asyncio`, how to measure your program's memory usage instead of guessing at it, and how to write database code that can't be exploited through SQL injection. These ideas show up constantly once you start building real, production-facing systems — including the kind of work going into Navy and Grand Line.

### 13.1 The Global Interpreter Lock (GIL)

Python — specifically the standard CPython interpreter you're almost certainly running — has something called the Global Interpreter Lock, or GIL. In plain terms: no matter how many CPU cores your machine has, only one thread can be running actual Python code at any single moment.

This sounds like a limitation, and it is, but it's a deliberate design choice rather than an oversight. Python keeps track of how many places in your code are pointing at a given object, and the moment that count hits zero, it frees the memory immediately. The GIL exists to keep that counting safe — without it, two threads could try to update the same count at the same time and corrupt it.

The practical effect is one of the most common surprises in Python: spinning up multiple threads to do heavy CPU work — math, parsing, image processing — usually doesn't make your program faster. The threads still take turns running one at a time; you've just added overhead for no real benefit.

```python
import threading
import time

def cpu_bound(n: int) -> int:
    """Counts to n. Pure CPU work."""
    total = 0
    for i in range(n):
        total += i
    return total

# --- Sequential (no threads) ---
start = time.perf_counter()
cpu_bound(50_000_000)
cpu_bound(50_000_000)
print(f"Sequential: {time.perf_counter() - start:.2f}s")

# --- Threaded (2 threads, same machine, 2 cores available) ---
start = time.perf_counter()
t1 = threading.Thread(target=cpu_bound, args=(50_000_000,))
t2 = threading.Thread(target=cpu_bound, args=(50_000_000,))
t1.start(); t2.start()
t1.join();  t2.join()
print(f"Threaded: {time.perf_counter() - start:.2f}s")

# RESULT: Sequential and Threaded come out roughly THE SAME.
# The GIL forces the threads to take turns. You added thread overhead for zero gain.
```

The correct mental model is to match the type of work to the right tool:

| Workload type | How the GIL affects it | What to reach for |
|---|---|---|
| CPU-bound (math, parsing, hashing, image processing) | Blocked — only one thread runs Python at a time | `multiprocessing.Pool` — each process gets its own interpreter and its own GIL |
| I/O-bound, using threads (disk reads, DB calls, subprocess calls) | The GIL is released while waiting on I/O | `concurrent.futures.ThreadPoolExecutor` |
| I/O-bound, using async (HTTP requests, WebSockets, async DB drivers) | Irrelevant — everything runs on a single thread anyway | `asyncio` |

**`multiprocessing` — escaping the GIL for CPU-bound work:**

```python
from multiprocessing import Pool
import time

def parse_chunk(chunk: list[str]) -> int:
    """CPU-bound: parse a chunk of log lines."""
    error_count = 0
    for line in chunk:
        if "ERROR" in line:
            error_count += 1
    return error_count


if __name__ == "__main__":  # Required guard for multiprocessing on Windows/macOS
    # Simulate 4 million log lines split across 8 workers
    log_lines = ["ERROR: timeout" if i % 10 == 0 else "INFO: ok" for i in range(4_000_000)]
    chunk_size = len(log_lines) // 8
    chunks = [log_lines[i:i+chunk_size] for i in range(0, len(log_lines), chunk_size)]

    start = time.perf_counter()
    with Pool(processes=8) as pool:
        results = pool.map(parse_chunk, chunks)

    total_errors = sum(results)
    print(f"Errors: {total_errors} | Time: {time.perf_counter() - start:.2f}s")
```

> [!NOTE]
> Some libraries written in C — NumPy, psycopg2, and `hashlib` among them — can release the GIL while doing their own heavy lifting internally. That's part of why a NumPy calculation doesn't freeze the rest of your program the way pure-Python CPU work would.

A few practical takeaways: using threads for CPU-heavy work doesn't get you the speedup you'd expect, for exactly the reason demonstrated above — reach for `multiprocessing` instead. When you do use `multiprocessing`, always wrap your script's entry point in `if __name__ == "__main__":` — on Windows and macOS, skipping this can cause child processes to spawn endless copies of themselves and crash the machine. And be mindful of what you pass between processes: each one is a separate, isolated copy of Python, so large objects like a huge dataframe need to be copied across between them. For genuinely large shared data, look into `multiprocessing.shared_memory` instead of passing it directly.

### 13.2 asyncio Event Loops

`asyncio` is Python's tool for handling many slow operations — like network requests — at the same time, without needing multiple threads or processes. Instead of one task blocking everything else while it waits for a server to respond, `asyncio` lets that task step aside and hand control to something else, then comes back to it once the wait is over. This works because tasks choose when to pause, using the `await` keyword — which is why it's called cooperative multitasking, as opposed to the OS deciding when to interrupt threads on its own.

There are three pieces to understand. A **coroutine** is a function defined with `async def`. Calling it doesn't run it immediately — it just creates a coroutine object, which then needs to be awaited or scheduled to actually execute. A **task** is a coroutine that's been scheduled to run on the event loop, usually via `asyncio.create_task()` or `asyncio.gather()` — multiple tasks can be in flight at the same time. The **event loop** itself is the scheduler running underneath everything; it tracks which tasks are waiting on what, and switches between them whenever one hits an `await`. `asyncio.run()` creates and manages this loop for you.

```python
import asyncio
import httpx
import time

async def fetch_url(client: httpx.AsyncClient, url: str) -> dict:
    """
    A coroutine that fetches a URL.
    'await client.get(url)' suspends THIS coroutine at the network I/O boundary.
    The event loop uses this time to run other ready coroutines.
    """
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    return {"url": url, "status": response.status_code, "size": len(response.content)}


async def fetch_all(urls: list[str]) -> list[dict]:
    """
    Fetches all URLs concurrently.
    asyncio.gather() schedules all coroutines as tasks simultaneously.
    """
    async with httpx.AsyncClient() as client:
        # return_exceptions=True: one failure does NOT cancel all the others
        results = await asyncio.gather(
            *[fetch_url(client, url) for url in urls],
            return_exceptions=True
        )

    # Separate successes from failures
    data = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Failed: {urls[i]} → {type(result).__name__}: {result}")
        else:
            data.append(result)
    return data


if __name__ == "__main__":
    URLS = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
    ]

    start = time.perf_counter()
    results = asyncio.run(fetch_all(URLS))
    elapsed = time.perf_counter() - start

    print(f"Fetched {len(results)} URLs in {elapsed:.2f}s")
    # Result: roughly 1.2s for 5 URLs (limited by the slowest endpoint)
    # A synchronous equivalent would take 5+ seconds — the sum of every response time
```

**`asyncio.Semaphore` — rate limiting concurrent tasks:**

```python
async def fetch_all_rate_limited(urls: list[str], max_concurrent: int = 10) -> list[dict]:
    """
    Without a semaphore, asyncio.gather() on 1000 tasks fires 1000 HTTP requests
    simultaneously — which can hit rate limits or get your IP banned.

    A semaphore acts like a permit pool: at most max_concurrent tasks can hold
    a permit at any time. Everyone else waits until a permit is returned.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_permit(client: httpx.AsyncClient, url: str) -> dict:
        async with semaphore:  # Acquire a permit, or wait if all are taken
            return await fetch_url(client, url)

    async with httpx.AsyncClient() as client:
        return await asyncio.gather(
            *[fetch_with_permit(client, url) for url in urls],
            return_exceptions=True
        )
```

**Async generators — the async equivalent of Section 10:**

```python
import asyncio

async def fetch_pages(base_url: str, total_pages: int):
    """
    Async generator: yields parsed results one page at a time.
    Combines lazy evaluation (Section 10) with async I/O.
    """
    async with httpx.AsyncClient() as client:
        for page in range(1, total_pages + 1):
            response = await client.get(f"{base_url}?page={page}")
            data = response.json()
            for record in data["results"]:
                yield record  # 'yield' inside 'async def' makes this an async generator


async def main():
    total = 0
    async for record in fetch_pages("https://api.example.com/jobs", total_pages=50):
        # Process one record at a time, streaming straight from the API
        # No memory buildup — only one page in memory at a time
        total += 1
    print(f"Processed {total} records")
```

> [!NOTE]
> Under the hood, none of this creates any extra threads — a single event loop can comfortably juggle thousands of waiting connections at once, since waiting on network I/O doesn't actually cost any CPU time.

A few things to watch for with async code. Calling a regular blocking function — like the plain `open()` and `.read()` from Section 6 — inside a coroutine blocks your entire event loop for as long as that call takes, freezing every other task in the process. For real file or CPU work inside async code, hand it off with `asyncio.to_thread(...)` instead. The same applies to `time.sleep()`: always use `await asyncio.sleep()` in async code, since the plain version blocks everything else running on the loop. If you create a background task with `asyncio.create_task()`, hold onto the reference it returns — if you don't, and that task later raises an exception, the error can be silently lost. And for starting your program, stick to `asyncio.run()` as your single entry point — it correctly creates and closes the event loop for you, rather than juggling it manually.

### 13.3 Memory Tracking via `tracemalloc`

`tracemalloc` is Python's built-in tool for measuring how much memory your code is actually using, instead of guessing. It's especially useful for confirming things like: is this generator from Section 10 actually saving memory the way it claimed? Is there a slow memory leak somewhere in a long-running process?

```python
import tracemalloc
import linecache
import os

def display_top_allocations(snapshot: tracemalloc.Snapshot, limit: int = 10):
    """Displays the top memory-consuming lines of code."""
    stats = snapshot.statistics("lineno")

    print(f"\n{'─' * 60}")
    print(f"  TOP {limit} MEMORY ALLOCATORS")
    print(f"{'─' * 60}")
    for i, stat in enumerate(stats[:limit], 1):
        frame = stat.traceback[0]
        filename = os.path.basename(frame.filename)
        line = linecache.getline(frame.filename, frame.lineno).strip()
        print(f"  {i:2}. {filename}:{frame.lineno} — {stat.size / 1024:.1f} KB")
        print(f"      └─ {line}")
    print(f"{'─' * 60}\n")


def profile_function():
    """Profiles memory usage of a specific operation."""
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    # ─── CODE UNDER PROFILING ─────────────────────────────────────────────────
    # Bad: loads an entire dataset into memory
    data = [str(i) * 100 for i in range(100_000)]  # ~50MB list
    processed = [line.upper() for line in data]
    # ──────────────────────────────────────────────────────────────────────────

    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    # Show what grew between the two snapshots
    top_stats = snapshot_after.compare_to(snapshot_before, "lineno")
    print("\nMEMORY DELTA (largest increases):")
    for stat in top_stats[:5]:
        print(f"  {stat}")

    return processed


profile_function()
```

This same idea works well as a context manager — tying directly back to Section 11 — so you can wrap any block of code and get both timing and memory in one go:

```python
from contextlib import contextmanager
import tracemalloc
import time


@contextmanager
def memory_profiler(label: str):
    """
    Context manager that measures both execution time and peak memory.
    Combines Section 11 (context managers) and Section 13.3 (tracemalloc).
    """
    tracemalloc.start()
    t_start = time.perf_counter()

    try:
        yield
    finally:
        elapsed = time.perf_counter() - t_start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(
            f"[{label}]\n"
            f"  Time:    {elapsed * 1000:,.2f} ms\n"
            f"  Current: {current / 1024:,.1f} KB\n"
            f"  Peak:    {peak / 1024:,.1f} KB"
        )


# ─── Comparing implementations ────────────────────────────────────────────────
print("=== List approach ===")
with memory_profiler("list comprehension"):
    result_list = [i * 2 for i in range(1_000_000)]

print("\n=== Generator approach ===")
with memory_profiler("generator expression"):
    result_gen = (i * 2 for i in range(1_000_000))
    total = sum(result_gen)  # Generator consumed without ever building the full list
```

**Sample output:**

```text
=== List approach ===
[list comprehension]
  Time:    87.42 ms
  Current: 8,192.0 KB
  Peak:    8,192.0 KB

=== Generator approach ===
[generator expression]
  Time:    61.15 ms
  Current: 0.1 KB
  Peak:    0.1 KB
```

This is the measurable proof behind Section 10's generator claims — peak RAM drops from 8MB to essentially nothing, for the exact same logical operation.

`tracemalloc` does add real overhead while it's running — typically somewhere around a 30–50% slowdown — so it's a profiling tool you switch on deliberately, not something to leave running permanently in production. It's also worth comparing two snapshots rather than relying on just one: a single snapshot only shows what's using memory right now, not whether memory is growing over time, which is the actual signal of a leak. And when reporting memory usage, lean on the *peak* figure rather than the *current* one — current memory can look tiny right after a big temporary spike has already been cleaned up, but peak tells you the worst case your program actually needs to handle.

### 13.4 Secure PostgreSQL Parameterization

This ties directly into the PostgreSQL + Python notes, but it's worth calling out here too, because it's one of the most important security habits in all of software development. SQL injection happens when user-provided text gets pasted directly into a SQL query before the database ever sees it, letting an attacker change what that query actually does.

```python
import psycopg2

conn = psycopg2.connect("postgresql://user:password@localhost/prod_db")
cursor = conn.cursor()

# ─── UNSAFE: f-string or .format() interpolation ─────────────────────────────
user_input = "1'; DROP TABLE users; --"  # Classic injection payload

query_unsafe = f"SELECT * FROM users WHERE id = {user_input}"
# What PostgreSQL receives and parses:
# SELECT * FROM users WHERE id = 1'; DROP TABLE users; --
# PostgreSQL would execute TWO statements here: the SELECT, then the DROP TABLE

# ─── SAFE: parameterized query ────────────────────────────────────────────────
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))
# psycopg2 sends the query structure and the value as two separate things.
# PostgreSQL treats the value as a literal piece of text data, never as SQL syntax.
# The semicolon, the quote, and the DROP are all just characters inside a string.
```

The key difference is that a parameterized query never lets your data become part of the SQL text at all. PostgreSQL receives the query structure and your actual values separately, so even if a value contains something that looks like SQL — quotes, semicolons, a `DROP TABLE` — it's treated purely as text, never as an instruction to execute.

**All parameterization forms in psycopg2:**

```python
# Single value — note the trailing comma, which makes it a tuple: (value,)
cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))

# Multiple values in a WHERE clause
cursor.execute(
    "SELECT * FROM jobs WHERE city = %s AND salary_min > %s",
    (city, min_salary)
)

# INSERT with multiple columns
cursor.execute(
    "INSERT INTO jobs (title, company, city, salary_min) VALUES (%s, %s, %s, %s)",
    (title, company, city, salary_min)
)

# Batch INSERT — executemany() is far faster than looping execute() one row at a time
records = [
    ("Python Dev", "Acme Corp", "Johannesburg", 45000),
    ("DevOps Eng", "Initech", "Cape Town", 52000),
    ("DBA",        "Globex",  "Durban", 48000),
]
cursor.executemany(
    "INSERT INTO jobs (title, company, city, salary_min) VALUES (%s, %s, %s, %s)",
    records
)

# UPDATE with a WHERE clause
cursor.execute(
    "UPDATE jobs SET salary_min = %s WHERE id = %s",
    (new_salary, job_id)
)

# Dynamic column or table names need a different approach (the psycopg2.sql module)
# NEVER do: f"SELECT * FROM {table_name}"
from psycopg2 import sql

table_name = "job_listings"
column_name = "city"
cursor.execute(
    sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
        sql.Identifier(table_name),
        sql.Identifier(column_name)
    ),
    ("Johannesburg",)
)
```

**Production-grade database access pattern — combining Sections 11, 12, and 13:**

```python
# db.py — reusable database module
from contextlib import contextmanager
from typing import Generator, Any
import psycopg2
import psycopg2.pool
import os

# Connection pool: maintains 2–10 persistent connections.
# Much cheaper than opening a brand-new connection for every query.
_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    dsn=os.environ["DATABASE_URL"]  # Never hardcode credentials
)


@contextmanager
def get_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Context manager that:
    1. Checks out a connection from the pool
    2. Opens a cursor
    3. Commits on a clean exit, rolls back on exception
    4. Returns the connection to the pool unconditionally
    """
    conn = _pool.getconn()
    try:
        cursor = conn.cursor()
        try:
            yield cursor          # The with-block gets the cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    finally:
        _pool.putconn(conn)       # Return the connection to the pool, always


def insert_job(title: str, company: str, city: str, salary_min: int | None) -> int:
    """Inserts a job and returns its new ID. Fully parameterized."""
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO job_listings (title, company, city, salary_min)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (title, company, city, salary_min)
        )
        return cursor.fetchone()[0]


def bulk_insert_jobs(jobs: list[dict]) -> int:
    """
    Batch inserts jobs using executemany().
    One transaction, one round-trip per batch — not one round-trip per record.
    """
    records = [
        (j["title"], j["company"], j["city"], j.get("salary_min"))
        for j in jobs
    ]
    with get_cursor() as cursor:
        cursor.executemany(
            "INSERT INTO job_listings (title, company, city, salary_min) VALUES (%s, %s, %s, %s)",
            records
        )
    return len(records)
```

A few patterns worth avoiding entirely: never build a SQL string using an f-string, `.format()`, or plain concatenation — even though `%s` inside `cursor.execute()` looks similar to Python's old-style `%` string formatting, it behaves completely differently under the hood, and confusing the two is exactly how injection vulnerabilities happen. Manually escaping quotes yourself isn't a safe substitute either — there are edge cases involving unusual characters or encoding tricks that are easy to miss, and the database driver already handles this correctly. If you're inserting a large number of records, avoid calling `cursor.execute()` in a loop one row at a time — `executemany()` does the same job in far fewer round-trips to the database. And keep credentials like passwords out of your source code entirely; use environment variables or a secrets manager instead, since anything committed to git history should be treated as permanently exposed, even after you delete it in a later commit.

### 13.5 Putting It All Together

Here's how all four ideas above come together in one realistic pipeline: fetching data from an API concurrently, processing it through a generator so nothing piles up in memory, and saving it to PostgreSQL safely — all while timing and measuring the whole run.

```python
"""
Production-grade async ETL pipeline.
Demonstrates: GIL awareness, asyncio, tracemalloc, parameterized queries.
"""

import asyncio
import tracemalloc
import time
from contextlib import contextmanager
import httpx
import os

from db import get_cursor  # Our context manager from 13.4


# ─── Section 13.3: Memory + time profiler ─────────────────────────────────────
@contextmanager
def profiler(label: str):
    tracemalloc.start()
    t = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"[{label}] {elapsed*1000:.1f}ms | Peak RAM: {peak/1024:.1f}KB")


# ─── Section 13.2: asyncio fetch layer ────────────────────────────────────────
async def fetch_page(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    page: int
) -> list[dict]:
    async with semaphore:  # Rate limit: max 5 concurrent requests
        resp = await client.get(url, params={"page": page}, timeout=10.0)
        resp.raise_for_status()
        return resp.json().get("results", [])


# ─── Section 10: Generator-based memory-safe processing ───────────────────────
def stream_valid_records(pages: list[list[dict]]):
    """Yields valid records one at a time — no full list in memory."""
    for page in pages:
        for record in page:
            if record.get("title") and record.get("company"):
                yield record


# ─── Section 13.4: Parameterized bulk write ───────────────────────────────────
def save_records(records_gen) -> int:
    batch = [
        (r["title"], r["company"], r.get("city", "Unknown"), r.get("salary_min"))
        for r in records_gen
    ]
    if not batch:
        return 0
    with get_cursor() as cursor:
        cursor.executemany(
            "INSERT INTO job_listings (title, company, city, salary_min) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (title, company) DO NOTHING",
            batch
        )
    return len(batch)


# ─── Main pipeline ─────────────────────────────────────────────────────────────
async def run_pipeline(api_url: str, total_pages: int = 20):
    semaphore = asyncio.Semaphore(5)

    with profiler("Full pipeline"):
        # Fetch all pages concurrently (respecting the semaphore)
        async with httpx.AsyncClient() as client:
            tasks = [
                fetch_page(client, semaphore, api_url, p)
                for p in range(1, total_pages + 1)
            ]
            pages = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed pages
        valid_pages = [p for p in pages if isinstance(p, list)]

        # Process and save using the generator (zero intermediate list allocation)
        saved = save_records(stream_valid_records(valid_pages))
        print(f"Saved {saved} records")


if __name__ == "__main__":
    asyncio.run(run_pipeline("https://api.example.com/jobs"))
```

---

**Practice:**
1. Run the GIL demo from 13.1 yourself (the `cpu_bound` threading example), and confirm for yourself that threading doesn't speed up CPU-bound work.
2. Write a small `asyncio` program with two coroutines that each `await asyncio.sleep(2)` and print a message before and after. Time the whole run with `time.perf_counter()` and confirm it takes about 2 seconds total, not 4.
3. Use the `memory_profiler` context manager pattern from 13.3 to compare the peak memory of a list comprehension building a million items against a generator expression doing the same work.
4. Take a query from your own Navy project (or write a sample one) and confirm it uses parameterized `%s` placeholders rather than f-strings.

---

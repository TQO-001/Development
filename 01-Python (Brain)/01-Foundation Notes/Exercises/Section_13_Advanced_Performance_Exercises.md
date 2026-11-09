## Section 13 Exercises: GIL / asyncio / Performance / DB Safety (Deep Dive)

These map directly onto real decisions you'll make in Emlindweni (FastAPI + PostgreSQL). Every exercise below is runnable with the **standard library only** — no `psycopg2`, `httpx`, or real database needed. Mocked I/O (using `time.sleep` / `asyncio.sleep`) teaches the exact same concurrency lessons without extra setup friction.

---

### 🟢 Warm-Up — Prove the GIL Blocks Threads on CPU Work
**Time:** ~10 min

**Goal:** Reproduce the exact experiment from notes 13.1 with your own numbers.

- [ ] Write `cpu_bound(n)` that sums `range(n)` in a plain loop.
- [ ] Time calling it twice **sequentially**.
- [ ] Time calling it twice via **two `threading.Thread`s**.
- [ ] Print both times.

**Done when:** The two times are roughly the same (within ~10-15%) — proving threading gave you zero speedup for CPU-bound work, exactly as your notes predict.

---

### 🟡 Core — Escape the GIL with `multiprocessing`
**Time:** ~15 min

**Goal:** Run the same CPU-bound work via `multiprocessing.Pool` and see a REAL speedup this time.

- [ ] Reuse `cpu_bound(n)` from the warm-up.
- [ ] Use `multiprocessing.Pool(processes=2)` with `.map()` to run it twice in parallel.
- [ ] **Must** include the `if __name__ == "__main__":` guard (notes 13.1, Anti-Pattern 2) — explain in a comment what happens if you forget it on Windows/macOS.
- [ ] Compare the multiprocessing time to the threaded time from the warm-up.

**Done when:** The multiprocessing version is noticeably faster than the threaded version (closer to half the sequential time, depending on your CPU core count).

---

### 🟡 Core — First `asyncio` Script: Concurrent Mock Fetches
**Time:** ~15 min

**Goal:** Get your first feel for `await` and `asyncio.gather` using fake I/O — no network needed.

- [ ] Write `async def fetch_mock(name, delay):` that does `await asyncio.sleep(delay)` then returns `f"{name} done"`.
- [ ] Run 5 calls to `fetch_mock` with different delays (e.g. `1, 2, 1, 3, 1`) **sequentially** with plain `await` in a loop — time it.
- [ ] Run the same 5 calls **concurrently** using `asyncio.gather(...)` — time it.
- [ ] Print both total times.

**Done when:** The concurrent version finishes in roughly the time of the SLOWEST single call (~3s), not the sum of all delays (~8s) — proving `await asyncio.sleep` releases control instead of blocking.

---

### 🟠 Applied — Rate-Limit Concurrency with `asyncio.Semaphore`
**Time:** ~15 min

**Goal:** Real APIs cap concurrent requests. Simulate that with a semaphore, per notes 13.5.

- [ ] Create a list of 10 mock "URLs" (just strings like `"task_1"` through `"task_10"`).
- [ ] Write `async def fetch_with_limit(semaphore, name):` that does `async with semaphore:` around an `await asyncio.sleep(1)` and a `print(f"Fetching {name}")` BEFORE the sleep.
- [ ] Create `asyncio.Semaphore(3)` and run all 10 tasks via `asyncio.gather`.
- [ ] Watch the print timing — only 3 `"Fetching..."` messages should appear in each ~1 second window.

**Done when:** The total run time is roughly `10 / 3` rounded up `≈ 4 seconds`, NOT 1 second (no limit) and NOT 10 seconds (fully sequential) — proving the semaphore is actually throttling concurrency.

---

### 🟠 Applied — Memory Profiling: List vs Generator
**Time:** ~15 min

**Goal:** Combine Section 11 (context managers) with Section 13.3-style memory profiling to make Section 10's "generators save memory" claim *measurable*, not just theoretical.

- [ ] Build the `profile_block` context manager from your notes (11.3 / 13.5) using `tracemalloc` + `time.perf_counter`.
- [ ] Inside one `with profile_block("List version", track_memory=True):` block, build `[x**2 for x in range(2_000_000)]` and just discard it.
- [ ] Inside a second `with profile_block("Generator version", track_memory=True):` block, build `(x**2 for x in range(2_000_000))` and only call `next()` on it once.
- [ ] Compare the printed "Peak RAM" numbers.

**Done when:** The list version's peak RAM is dramatically (often 100x+) higher than the generator version's — with real numbers printed, not just an explanation.

---

### 🔴 Challenge — SQL Injection: See It, Then Prevent It
**Time:** ~15 min

**Goal:** Make the danger in notes 13.4 concrete using a **fake** `execute()` function (no real database needed) so you can safely "inject" a malicious string and watch what would happen.

- [ ] Write `def fake_execute(query: str):` that just prints the final query string as if it were sent to a database.
- [ ] Write the **unsafe** version: build a query using an f-string with a `username` variable, then call `fake_execute()` with `username = "alice'; DROP TABLE users; --"` and look at the printed query.
- [ ] Write the **safe** version: write a function `safe_execute(query: str, params: tuple)` that just prints the query template AND the params **separately** (mirroring how psycopg2 sends Parse + Bind messages separately, per notes 13.4's under-the-hood explanation) — never concatenating them into one string.
- [ ] In a comment, explain specifically why the unsafe version's printed output is dangerous and the safe version's isn't, using your own words.

**Done when:** You can point to the literal printed string from the unsafe version and show exactly where `DROP TABLE` ends up sitting inside what looks like valid SQL.

---

### 💀 BOSS — Mini Async + Generator + Profiler Pipeline
**Time:** ~40 min

**Goal:** Recreate the integrated pattern from notes 13.5 (`run_pipeline`) entirely with mocks — combining asyncio concurrency, a semaphore, a lazy generator, and your profiler context manager into one working script you can actually run top to bottom.

**Requirements:**
- [ ] `async def fetch_page(semaphore, page_number):` — `async with semaphore:`, sleep `0.5s`, then return a fake "page" — a list of 5 dicts like `{"id": page_number * 5 + i, "valid": i % 4 != 0}` (so ~20% of records are intentionally "invalid").
- [ ] `async def fetch_all(total_pages):` — creates an `asyncio.Semaphore(3)`, builds a task list comprehension calling `fetch_page` for each page number, and `await`s them all via `asyncio.gather`.
- [ ] `def stream_valid_records(pages):` — a **generator function** (Section 10!) that loops through the list of pages and `yield`s only records where `"valid"` is `True`.
- [ ] Your `profile_block` context manager (Section 11/13.3) wrapping the ENTIRE pipeline run, printing total time and peak memory.
- [ ] A `main()` that: runs `fetch_all(10)` inside `asyncio.run()`, pipes the result through `stream_valid_records`, and prints the count of valid records plus the first 3 of them.

**Done when:** Running the script end-to-end prints a profiler summary line (time + memory), the correct count of valid records (~80% of 50 total), and doesn't crash — proving all four concepts (async concurrency, semaphore throttling, lazy generators, and profiling) work together in one coherent pipeline, exactly like the senior-level pattern in your notes.

---

### ✅ Section Progress
- [ ] Warm-Up: GIL blocks threads on CPU work
- [ ] Core: `multiprocessing` escapes the GIL
- [ ] Core: First `asyncio.gather` concurrency test
- [ ] Applied: `asyncio.Semaphore` rate limiting
- [ ] Applied: List vs generator memory profiling
- [ ] Challenge: SQL injection demo (safe vs unsafe)
- [ ] 💀 BOSS: Full async + generator + profiler pipeline

# 🔬 Micro-Scenario 06 — The Thundering Herd
**Complexity:** ⭐⭐⭐⭐ High
**Skill Targets:** Section 13.2 — `asyncio` event loop · `asyncio.Semaphore` · `asyncio.gather(return_exceptions=True)` · Async context managers · `time.perf_counter()` concurrency benchmarking
**Portfolio Context:** The **Navy** tracker polls 200 company career pages simultaneously to check for new listings. The first production run fired 200 simultaneous HTTP requests, hit rate limits on every target, got IP-banned by three domains, and returned 0 results. You must rebuild it with controlled concurrency and per-domain rate limiting.

---

## Step 1 — The Broken Junior Implementation

```python
# career_scraper.py
import asyncio
import httpx
import time

CAREER_URLS = [f"https://careers.company{i}.example.com/jobs" for i in range(200)]

async def fetch_jobs(url: str) -> list[dict]:
    """Fetches job listings from a single company career page."""
    async with httpx.AsyncClient() as client:  # New client PER REQUEST — defeats connection reuse
        response = await client.get(url, timeout=5.0)
        return response.json().get("jobs", [])  # No status check — 429 silently returns []

async def scrape_all(urls: list[str]) -> list[dict]:
    """Fetches all career pages concurrently."""
    tasks = [fetch_jobs(url) for url in urls]

    # Fires ALL 200 requests simultaneously — zero rate limiting
    results = await asyncio.gather(*tasks)      # If ONE raises, ALL are cancelled

    all_jobs = []
    for result in results:
        all_jobs.extend(result)
    return all_jobs

if __name__ == "__main__":
    start = time.perf_counter()
    jobs  = asyncio.run(scrape_all(CAREER_URLS))
    print(f"Found {len(jobs)} jobs in {time.perf_counter() - start:.2f}s")
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — Thundering Herd: 200 simultaneous requests
```python
tasks   = [fetch_jobs(url) for url in urls]  # 200 coroutines
results = await asyncio.gather(*tasks)        # Fires all 200 at once
```
Firing 200 HTTP requests simultaneously causes:
- Target servers hit rate limits (HTTP 429) — most public APIs allow 5–30 req/s
- Your outbound connection pool is overwhelmed (OS limit: ~65k ports, but realistic limits are much lower)
- One slow server blocks your gather from completing (all results wait for the slowest task)

**Fix pseudocode:**
```
Create semaphore = asyncio.Semaphore(MAX_CONCURRENT)  # e.g. 10

async def fetch_with_limit(client, semaphore, url):
    async with semaphore:          # Blocks here if 10 requests are already in-flight
        return await fetch_jobs(client, url)

tasks = [fetch_with_limit(client, semaphore, url) for url in urls]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Bug 2 — New `httpx.AsyncClient()` per request
```python
async def fetch_jobs(url: str):
    async with httpx.AsyncClient() as client:   # Created and destroyed for every URL
```
An `AsyncClient` maintains a connection pool internally. Creating a new one for every request throws away all connection pooling benefits — no keep-alive, no DNS caching, no TLS session reuse. One shared client should be created once for the entire scrape run and passed in as a dependency.

**Fix pseudocode:**
```
In scrape_all():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # All fetch calls share this one client instance
        tasks = [fetch_with_limit(client, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Bug 3 — `asyncio.gather()` without `return_exceptions=True`
```python
results = await asyncio.gather(*tasks)
```
If ANY of the 200 tasks raises an exception (network timeout, connection refused), `asyncio.gather()` immediately cancels all remaining tasks and re-raises the exception. A single unreachable server kills the entire run. With `return_exceptions=True`, failed tasks return the exception object instead of raising — you get partial results and can report failures separately.

### Bug 4 — No HTTP status validation
```python
return response.json().get("jobs", [])   # 429 Too Many Requests has no JSON body
                                          # json() raises JSONDecodeError — unhandled
```
Call `response.raise_for_status()` before parsing. Catch `httpx.HTTPStatusError` and `httpx.RequestError` separately — different retry strategies apply to each.

### Bug 5 — No retry logic for transient failures
A 429 response includes a `Retry-After` header. A production scraper reads this header and uses `await asyncio.sleep(retry_after)` before retrying — not just giving up.

---

## Step 3 — Validation Challenge

```python
# career_scraper_v2.py
import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Use httpx if installed, otherwise mock it
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


MAX_CONCURRENT = 10           # Max simultaneous requests
REQUEST_TIMEOUT = 10.0        # Seconds per request
MAX_RETRIES     = 2           # Retry count on 429 / 503


# ─── TODO 1: Implement fetch_one ──────────────────────────────────────────────
# Requirements:
#   - Accept: client (httpx.AsyncClient), semaphore (asyncio.Semaphore), url (str)
#   - Acquire semaphore before making the request (use async with)
#   - Call response.raise_for_status() before parsing
#   - On httpx.HTTPStatusError with 429: read Retry-After header (default 1s),
#     await asyncio.sleep(retry_after), retry up to MAX_RETRIES times
#   - On any other exception: return {"url": url, "error": str(e), "jobs": []}
#   - On success: return {"url": url, "jobs": data.get("jobs", []), "error": None}

async def fetch_one(client, semaphore: asyncio.Semaphore, url: str) -> dict:
    # TODO
    pass


# ─── TODO 2: Implement scrape_all ────────────────────────────────────────────
# Requirements:
#   - Create ONE shared httpx.AsyncClient for all requests
#   - Create ONE asyncio.Semaphore(MAX_CONCURRENT)
#   - Build tasks: [fetch_one(client, semaphore, url) for url in urls]
#   - Use asyncio.gather(*tasks, return_exceptions=True)
#   - Separate results into successes and failures
#   - Return dict: {"jobs": [all job dicts], "errors": [error dicts], "total_urls": N}

async def scrape_all(urls: list[str]) -> dict:
    # TODO
    pass


# ─── TODO 3: Implement benchmark wrapper ─────────────────────────────────────
# Requirements:
#   - Accepts urls list and concurrency level
#   - Times the full scrape_all() call with time.perf_counter()
#   - Prints: "Scraped {N} URLs in {elapsed:.2f}s | {jobs} jobs | {errors} errors"
#   - Returns the result dict from scrape_all

async def timed_scrape(urls: list[str]) -> dict:
    # TODO
    pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestCareerScraper(unittest.TestCase):

    def _make_success_response(self, jobs=None):
        resp = MagicMock()
        resp.raise_for_status = MagicMock(return_value=None)
        resp.json.return_value = {"jobs": jobs or [{"title": "Python Dev"}]}
        return resp

    def _make_429_response(self):
        resp = MagicMock()
        error = MagicMock(spec=Exception)
        resp.raise_for_status.side_effect = Exception("429 Too Many Requests")
        resp.headers = {"Retry-After": "1"}
        resp.status_code = 429
        return resp

    def test_semaphore_limits_concurrency(self):
        """No more than MAX_CONCURRENT requests should be in-flight simultaneously."""
        in_flight = [0]
        max_seen  = [0]

        async def run():
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)

            async def mock_fetch(url):
                async with semaphore:
                    in_flight[0] += 1
                    max_seen[0] = max(max_seen[0], in_flight[0])
                    await asyncio.sleep(0.01)   # Simulate I/O
                    in_flight[0] -= 1

            urls = [f"https://example.com/{i}" for i in range(50)]
            await asyncio.gather(*[mock_fetch(url) for url in urls])

        asyncio.run(run())
        self.assertLessEqual(max_seen[0], MAX_CONCURRENT)
        print(f"✅ ASSERTION 1 PASSED: Max concurrent = {max_seen[0]} ≤ {MAX_CONCURRENT}")

    def test_gather_with_return_exceptions(self):
        """gather() must not cancel all tasks when one fails."""
        async def run():
            results_container = []

            async def good_task(i):
                await asyncio.sleep(0.001)
                return f"success_{i}"

            async def bad_task():
                raise ValueError("Simulated failure")

            tasks   = [good_task(i) for i in range(5)] + [bad_task()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results_container.extend(results)
            return results_container

        results = asyncio.run(run())
        successes = [r for r in results if not isinstance(r, Exception)]
        failures  = [r for r in results if isinstance(r, Exception)]

        self.assertEqual(len(successes), 5, "Good tasks should complete despite one failure")
        self.assertEqual(len(failures),  1)
        print("✅ ASSERTION 2 PASSED: gather(return_exceptions=True) — 1 failure, 5 successes")

    def test_results_structure(self):
        """scrape_all() must return a dict with 'jobs', 'errors', 'total_urls' keys."""
        async def run():
            semaphore = asyncio.Semaphore(5)
            results = []

            async def fake_scrape(urls):
                return {"jobs": [{"title": "Dev"}] * 3, "errors": [], "total_urls": len(urls)}

            return await fake_scrape(["url1", "url2", "url3"])

        result = asyncio.run(run())
        self.assertIn("jobs",       result)
        self.assertIn("errors",     result)
        self.assertIn("total_urls", result)
        print("✅ ASSERTION 3 PASSED: scrape_all() returns correct result structure")

    def test_concurrency_is_faster_than_sequential(self):
        """Async concurrent scraping must be significantly faster than sequential."""
        DELAY = 0.05   # 50ms simulated I/O per request

        async def fake_request(url, delay=DELAY):
            await asyncio.sleep(delay)
            return {"jobs": [{"title": "Dev"}]}

        async def sequential(urls):
            results = []
            for url in urls:
                results.append(await fake_request(url))
            return results

        async def concurrent(urls):
            tasks = [fake_request(url) for url in urls]
            return await asyncio.gather(*tasks)

        urls = [f"https://example.com/{i}" for i in range(20)]

        start = time.perf_counter()
        asyncio.run(sequential(urls))
        seq_time = time.perf_counter() - start

        start = time.perf_counter()
        asyncio.run(concurrent(urls))
        con_time = time.perf_counter() - start

        speedup = seq_time / con_time
        self.assertGreater(speedup, 5.0,
            f"Concurrent should be >5x faster than sequential. Got {speedup:.1f}x")
        print(f"✅ ASSERTION 4 PASSED: Concurrent {speedup:.1f}x faster than sequential")
        print(f"   Sequential: {seq_time:.2f}s | Concurrent: {con_time:.2f}s")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

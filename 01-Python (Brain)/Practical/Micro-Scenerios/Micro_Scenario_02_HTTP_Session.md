# 🔬 Micro-Scenario 02 — The Leaky HTTP Session
**Complexity:** ⭐⭐ Medium
**Skill Targets:** Section 11.1 — Class-based `__enter__` / `__exit__` · Resource lifecycle management · Exception-safe cleanup
**Portfolio Context:** You are building the HTTP client layer for **Navy** (your job tracker). Every call to an external jobs API must be wrapped in a session that tracks call counts, enforces a per-session request cap, and guarantees the connection is closed — even on network errors.

---

## Step 1 — The Broken Junior Implementation

```python
# http_client.py
# "Handles all HTTP calls to external job APIs. Fully tested." — Junior Dev

import requests
import time

MAX_REQUESTS_PER_SESSION = 50

class JobAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key  = api_key
        self.session  = requests.Session()          # Session opened here
        self.session.headers.update({"X-API-Key": api_key})
        self.request_count = 0

    def fetch_jobs(self, keyword: str, page: int = 1) -> dict:
        if self.request_count >= MAX_REQUESTS_PER_SESSION:
            print("Request cap reached. Create a new client.")
            return {}

        url = f"{self.base_url}/jobs"
        response = self.session.get(url, params={"q": keyword, "page": page})
        self.request_count += 1
        return response.json()                      # No status check — 404/500 returns garbage

    def close(self):                                # Must be called manually — easy to forget
        self.session.close()
        print(f"Session closed after {self.request_count} requests.")


# Caller code
def scrape_listings(keyword: str) -> list[dict]:
    client = JobAPIClient("https://api.jobs.example.com", "secret-key-123")
    results = []

    for page in range(1, 10):
        data = client.fetch_jobs(keyword, page)     # If this raises on page 3...
        results.extend(data.get("results", []))

    client.close()                                  # NEVER REACHED on exception
    return results
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — Session opened in `__init__`, never guaranteed to close
```python
self.session = requests.Session()   # Opened unconditionally in constructor
# ...
client.close()                      # Only called if no exception — fire-and-forget
```
`requests.Session` holds an underlying `urllib3.PoolManager` with open TCP connections. If `fetch_jobs()` raises a `ConnectionError` on page 3, `close()` is skipped. The OS socket stays open until the garbage collector runs — which is non-deterministic. Under load with 50 concurrent scrapers, you exhaust the system's file descriptor limit.

**Fix pseudocode:**
```
Implement __enter__ → opens and returns session, returns self
Implement __exit__ → calls self.session.close() in a finally block unconditionally
Return False from __exit__ — do not suppress network exceptions
```

### Bug 2 — No HTTP status validation
```python
return response.json()   # 429 Too Many Requests → json() raises JSONDecodeError
                         # 500 Internal Server Error → silently returns error body
```
`response.raise_for_status()` converts 4xx/5xx responses into `requests.HTTPError`. Without it, a rate-limit response silently corrupts your data.

**Fix pseudocode:**
```
After self.session.get():
    response.raise_for_status()    # Raises HTTPError for 4xx / 5xx
    return response.json()
```

### Bug 3 — Request cap check silently returns `{}` instead of raising
```python
if self.request_count >= MAX_REQUESTS_PER_SESSION:
    print("Request cap reached.")
    return {}       # Caller gets an empty dict with no indication of why
```
The caller has no way to distinguish "no results" from "cap exceeded." Raise a named exception.

**Fix pseudocode:**
```
Define: class RequestCapExceededError(Exception): pass
In fetch_jobs: raise RequestCapExceededError(f"Cap of {MAX_REQUESTS_PER_SESSION} reached")
```

### Bug 4 — Hardcoded API key as a plain string argument
```python
client = JobAPIClient("https://...", "secret-key-123")
```
API keys belong in environment variables. `os.environ["JOBS_API_KEY"]` — not in source code.

---

## Step 3 — Validation Challenge

Complete all `# TODO` blocks. All assertions must pass.

```python
# http_client_v2.py
import os
import requests
from unittest.mock import MagicMock, patch
import unittest


MAX_REQUESTS_PER_SESSION = 5   # Lowered for testing


class RequestCapExceededError(Exception):
    pass


class JobAPIClient:
    """
    A context-manager-aware HTTP client for external job APIs.
    Guarantees session cleanup and enforces request caps.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url      = base_url
        self.api_key       = api_key
        self.session       = None
        self.request_count = 0

    def __enter__(self):
        # TODO: Create the requests.Session(), set the X-API-Key header, return self
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Close self.session unconditionally. Do NOT suppress exceptions.
        pass

    def fetch_jobs(self, keyword: str, page: int = 1) -> dict:
        # TODO:
        # 1. Raise RequestCapExceededError if request_count >= MAX_REQUESTS_PER_SESSION
        # 2. Build the URL and make the GET request with keyword + page params
        # 3. Call raise_for_status() before parsing JSON
        # 4. Increment request_count and return the JSON dict
        pass


# ─── VALIDATION HARNESS ───────────────────────────────────────────────────────

class TestJobAPIClient(unittest.TestCase):

    def _make_mock_response(self, status_code=200, json_data=None):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {"results": [{"title": "Python Dev"}]}
        if status_code >= 400:
            mock_resp.raise_for_status.side_effect = requests.HTTPError(
                f"{status_code} Error", response=mock_resp
            )
        else:
            mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_session_closes_on_clean_exit(self):
        """Session must be closed after a normal with-block exit."""
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = self._make_mock_response()

            with JobAPIClient("https://api.example.com", "key") as client:
                client.fetch_jobs("python")

            mock_session.close.assert_called_once()
        print("✅ ASSERTION 1 PASSED: Session closed on clean exit")

    def test_session_closes_on_exception(self):
        """Session must be closed even when an exception is raised inside the with block."""
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.side_effect = requests.ConnectionError("Timeout")

            with self.assertRaises(requests.ConnectionError):
                with JobAPIClient("https://api.example.com", "key") as client:
                    client.fetch_jobs("python")

            mock_session.close.assert_called_once()
        print("✅ ASSERTION 2 PASSED: Session closed on exception")

    def test_request_cap_raises(self):
        """Must raise RequestCapExceededError when cap is reached, not return {}."""
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = self._make_mock_response()

            with JobAPIClient("https://api.example.com", "key") as client:
                for _ in range(MAX_REQUESTS_PER_SESSION):
                    client.fetch_jobs("python")
                with self.assertRaises(RequestCapExceededError):
                    client.fetch_jobs("python")   # One over the cap
        print("✅ ASSERTION 3 PASSED: RequestCapExceededError raised at cap")

    def test_http_error_propagates(self):
        """A 429 or 500 response must raise HTTPError, not return corrupt data."""
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = self._make_mock_response(status_code=429)

            with self.assertRaises(requests.HTTPError):
                with JobAPIClient("https://api.example.com", "key") as client:
                    client.fetch_jobs("python")
        print("✅ ASSERTION 4 PASSED: HTTPError raised on 4xx/5xx response")

    def test_request_count_increments(self):
        """request_count must track every successful call."""
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = self._make_mock_response()

            with JobAPIClient("https://api.example.com", "key") as client:
                client.fetch_jobs("python", page=1)
                client.fetch_jobs("python", page=2)
                client.fetch_jobs("python", page=3)
                self.assertEqual(client.request_count, 3)
        print("✅ ASSERTION 5 PASSED: request_count correctly tracked")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

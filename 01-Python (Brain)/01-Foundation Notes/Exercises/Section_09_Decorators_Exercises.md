## Section 9 Exercises: Decorators (Deep Dive)

Save each exercise as its own scratch file (e.g. `9C-shout-practice.py`, `9D-timer-practice.py`...) so you can run them independently. No solutions are given — only specs, hints, and a "Done When" checklist. Build it, run it, see if the output matches.

---

### 🟢 Warm-Up — `@shout`
**Time:** ~5 min

**Goal:** Write a decorator `@shout` that uppercases whatever string a function returns.

- [ ] Write `greet(name)` that returns `f"hello, {name}"`.
- [ ] Write `@shout` so `greet("arthur")` returns `"HELLO, ARTHUR"` instead.
- [ ] Apply `@wraps` so `greet.__name__` still prints `"greet"`.

> Hint: `wrapper` needs to call `func(*args, **kwargs)`, capture the result, then `.upper()` it before returning.

**Done when:** `print(greet("arthur"))` → `HELLO, ARTHUR`, and `print(greet.__name__)` → `greet`.

---

### 🟡 Core — `@timer`
**Time:** ~10 min

**Goal:** Build the `@timer` decorator from your notes (9.5) from scratch, without looking back at the file.

- [ ] Use `time.perf_counter()` to capture start/end.
- [ ] Print the elapsed time in milliseconds, formatted to 2 decimal places.
- [ ] Make sure the decorated function's **return value** still comes through (don't drop it).
- [ ] Apply it to a function that sums `range(2_000_000)`.

**Done when:** Calling the function prints a timing line AND still returns the correct sum.

---

### 🟡 Core — `@retry(times=3)` (a decorator WITH arguments)
**Time:** ~15 min

**Goal:** This is a step up from anything in your notes — a decorator *factory*. `@retry(times=3)` needs three nested levels: outer function takes the argument, middle function takes `func`, inner `wrapper` does the work.

- [ ] Write a function `flaky_action()` that randomly raises a `ValueError` about 60% of the time (use `random.random()`), and otherwise returns `"Success!"`.
- [ ] Write `@retry(times=3)` so that if `flaky_action()` raises, it's retried up to `times` times before giving up and re-raising the final exception.
- [ ] Print `f"Attempt {n} failed, retrying..."` on each failure.

> Hint structure:
> ```python
> def retry(times):
>     def decorator(func):
>         def wrapper(*args, **kwargs):
>             # loop here
>             ...
>         return wrapper
>     return decorator
> ```

**Done when:** Running `flaky_action()` several times eventually either succeeds within 3 tries or raises after the 3rd failure — never silently swallows the error.

---

### 🟠 Applied — `@require_positive`
**Time:** ~10 min

**Goal:** A validation decorator that inspects arguments before the function runs.

- [ ] Write `deal_damage(amount)` that prints the damage dealt.
- [ ] Write `@require_positive` that checks the **first positional argument**. If it's `<= 0`, raise `ValueError` instead of calling the original function.
- [ ] Confirm `deal_damage(-5)` raises, and `deal_damage(20)` works normally.

**Done when:** Negative/zero input never reaches the real function body.

---

### 🟠 Applied — `@memoize`
**Time:** ~15 min

**Goal:** A caching decorator that stores previous results so expensive calls aren't repeated.

- [ ] Write a deliberately slow `def slow_square(n): time.sleep(1); return n * n`.
- [ ] Write `@memoize` that keeps an internal dictionary (closure variable) mapping `args → result`.
- [ ] First call with a given input should take ~5 second; the *second* call with the **same** input should return near-instantly.
- [ ] Print `"cache hit"` or `"cache miss"` so you can see it working.

> Hint: `args` is already hashable as a tuple, so it can be a dict key directly: `cache[args]`.

**Done when:** Calling `slow_square(5)` twice — the second call is visibly faster and prints `cache hit`.

---

### 🔴 Challenge — Stack Three Decorators and Trace the Order
**Time:** ~15 min

**Goal:** Combine `@timer`, `@memoize`, and `@require_positive` on a single function and reason about execution order.

- [ ] Apply all three to one function (pick an order).
- [ ] Before running, **write down on paper or in a comment** what order you expect the wrapping to happen in (bottom-up, per your notes 9.2).
- [ ] Run it and confirm your prediction was correct.
- [ ] Swap the order of the decorators and explain (in a comment) why the *timer* result changes depending on whether it wraps the cache or is wrapped BY the cache.

**Done when:** You can explain, in your own words, why `@memoize` above `@timer` gives different timing results than `@timer` above `@memoize`.

---

### 💀 BOSS — `@rate_limit(calls, period_seconds)`
**Time:** ~25–30 min

**Goal:** Build a real-world decorator used in production APIs: limit how often a function can be called within a rolling time window. This combines closures, `*args/**kwargs` forwarding, `functools.wraps`, and `time`.

**Requirements:**
- [ ] `@rate_limit(calls=3, period=5)` allows at most 3 calls to the decorated function within any 5-second window.
- [ ] If the limit is exceeded, **raise a custom exception** `RateLimitExceeded` (define it — see Section 5.4 patterns) instead of silently failing.
- [ ] Internally track call **timestamps** in a list (closure variable), and on each call, drop any timestamps older than `period` seconds before checking the count.
- [ ] Apply it to a mock `send_request(endpoint: str)` function and prove it works by calling it 5 times rapidly in a loop, catching and printing `RateLimitExceeded` when it fires.
- [ ] Use `@wraps` so `send_request.__name__` is preserved.

**Done when:** Your loop output clearly shows the first 3 calls succeeding and the 4th/5th raising `RateLimitExceeded`, with the function's identity (`__name__`) intact.

---

### ✅ Section Progress
- [ ] Warm-Up: `@shout`
- [ ] Core: `@timer`
- [ ] Core: `@retry(times=3)`
- [ ] Applied: `@require_positive`
- [ ] Applied: `@memoize`
- [ ] Challenge: Triple-stacked decorators
- [ ] 💀 BOSS: `@rate_limit`

## Section 11 Exercises: Context Managers (Deep Dive)

Save each exercise as its own scratch file. For every exercise, deliberately trigger an exception inside the `with` block at least once to confirm cleanup still runs — that's the entire point of context managers.

---

### 🟢 Warm-Up — `Timer` (class-based, no exception handling yet)
**Time:** ~10 min

**Goal:** Build the simplest possible class-based context manager.

- [ ] `class Timer:` with `__enter__` (records start time, returns `self`) and `__exit__` (prints elapsed time).
- [ ] Use it: `with Timer(): time.sleep(1)`.
- [ ] Confirm the elapsed time prints automatically when the block ends — no manual `.stop()` call needed.

**Done when:** The elapsed time prints itself the moment the `with` block exits.

---

### 🟡 Core — `Resource` (handles exceptions, returns `False`)
**Time:** ~15 min

**Goal:** Extend the warm-up pattern to handle the three `__exit__` arguments properly, mirroring `DatabaseConnection` in your notes (11.1).

- [ ] `class Resource:` prints `"Acquired"` on `__enter__`.
- [ ] `__exit__` prints `"Released"` always, and additionally prints `f"Exception caught: {exc_val}"` if one occurred.
- [ ] `__exit__` returns `False` so exceptions still propagate.
- [ ] Test it twice: once with a clean block, once where you deliberately do `1 / 0` inside the block. Wrap the SECOND test in an outer `try/except` so your script doesn't crash.

**Done when:** Both tests print `"Acquired"` then `"Released"` — and the exception test ALSO prints the exception message, then correctly propagates instead of being swallowed.

---

### 🟡 Core — `@contextmanager` Version: `temp_file(path)`
**Time:** ~15 min

**Goal:** Rewrite a resource-cleanup pattern using `contextlib.contextmanager` instead of a class (per notes 11.2).

- [ ] `@contextmanager def temp_file(path):` — creates a file with some text, `yield`s the path, then deletes the file in a `finally` block (use `os.remove` or `Path.unlink`).
- [ ] **Critically:** wrap the `yield` in `try/finally` — your notes explicitly warn this is the #1 mistake (Anti-Pattern 1, section 11.2).
- [ ] Inside the `with` block, read and print the file's contents to prove it exists while the block is active.
- [ ] After the `with` block ends, check `Path(path).exists()` and print the result.

**Done when:** The file exists and is readable inside the block, and `exists()` prints `False` immediately after the block ends — even if you raise an exception inside the block.

---

### 🟠 Applied — `suppress_errors(*exc_types)`
**Time:** ~15 min

**Goal:** Build your own mini version of `contextlib.suppress` — a context manager that swallows ONLY the specific exception types you pass in, and lets everything else propagate.

- [ ] Use either the class-based (`__enter__`/`__exit__`) or `@contextmanager` style — your choice.
- [ ] `with suppress_errors(ValueError, KeyError): int("not a number")` — should NOT crash your script.
- [ ] `with suppress_errors(ValueError): 1 / 0` — should STILL crash (since `ZeroDivisionError` wasn't in the suppressed list).
- [ ] Print a message confirming which path was taken.

**Done when:** The `ValueError` test runs silently to completion, and the mismatched-exception test correctly still raises.

---

### 🟠 Applied — Nested Context Managers & LIFO Order
**Time:** ~10 min

**Goal:** Prove to yourself that `__exit__` calls happen in reverse (LIFO) order.

- [ ] Reuse your `Resource` class from the Core exercise, but give it a `name` parameter so you can tell instances apart in the printed output.
- [ ] Nest three of them: `with Resource("A") as a, Resource("B") as b, Resource("C") as c:` (or nest separate `with` blocks inside each other).
- [ ] Print something inside the innermost block.
- [ ] Look at the order things printed in.

**Done when:** You can explain in a comment why `"Released C"` prints before `"Released B"`, which prints before `"Released A"`.

---

### 🔴 Challenge — `ExitStack` for a Dynamic Number of Files
**Time:** ~20 min

**Goal:** Use `contextlib.ExitStack` to open a variable-length list of files within a single `with` block — this is impossible to do cleanly with regular `with` statements since you don't know the count ahead of time.

- [ ] Create a list of 4 filenames, e.g. `["log1.txt", "log2.txt", "log3.txt", "log4.txt"]`.
- [ ] Use `ExitStack()` and a loop with `stack.enter_context(open(...))` to open all 4 files for writing inside one `with ExitStack() as stack:` block.
- [ ] Write a line to each file.
- [ ] After the block ends, verify (by reopening and reading, or checking `closed` attribute) that all 4 files were properly closed.

**Done when:** All 4 files contain your written line and are confirmed closed after the block exits — and you achieved this without 4 separate nested `with` statements.

---

### 💀 BOSS — Simulated Banking `transaction_block()`
**Time:** ~30 min

**Goal:** Build the exact pattern from `DatabaseConnection` in your notes (11.1) — commit on success, rollback on failure — but simulated entirely in memory (no real database needed), so it directly mirrors what you'll eventually do with `psycopg2` in Emlindweni.

**Requirements:**
- [ ] A simple `Account` class with a `balance` attribute (start at, say, `1000`).
- [ ] `@contextmanager def transaction_block(account):` — at entry, save a **snapshot** of `account.balance`. `yield` the account.
- [ ] Inside `finally` (or `except`/`else`): if an exception occurred, **roll back** — restore `account.balance` to the saved snapshot, then print `"Transaction rolled back."` If no exception occurred, print `"Transaction committed."` and leave the new balance as-is.
- [ ] **Must NOT suppress the exception** — let it propagate after rolling back (return `False`/don't swallow it).
- [ ] Test 1 (success path): inside the block, do `account.balance -= 200` (a withdrawal), no error. Confirm the balance stays reduced after the block.
- [ ] Test 2 (failure path): inside the block, do `account.balance -= 200`, then deliberately `raise ValueError("Insufficient funds check failed")`. Wrap this call in an outer `try/except` so the script keeps running. Confirm the balance is restored to its original value despite the partial withdrawal that happened before the error.

**Done when:** Test 1 leaves the balance permanently changed; Test 2 leaves the balance completely unchanged — exactly mimicking commit/rollback semantics from real database transactions.

---

### ✅ Section Progress
- [ ] Warm-Up: `Timer`
- [ ] Core: `Resource` (exception-aware)
- [ ] Core: `@contextmanager` `temp_file`
- [ ] Applied: `suppress_errors`
- [ ] Applied: Nested context managers / LIFO order
- [ ] Challenge: `ExitStack` for dynamic files
- [ ] 💀 BOSS: `transaction_block()` commit/rollback

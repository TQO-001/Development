## Section 11: Context Managers

A **context manager** is a Python object that sets something up for you, hands it over, and then cleans it up afterward automatically — no matter what happens in between, even if your code raises an exception partway through.

This is the exact mechanism behind `with open("file.txt") as f:`, which you've already been using since Section 6. Python guarantees the file gets closed, even if an exception happens on the very next line. Without a context manager, you'd be relying on remembering to call `f.close()` yourself — and in real production code, that call rarely survives the first unhandled exception.

### 11.1 Custom Context Managers via Classes (`__enter__` / `__exit__`)

A class becomes a context manager by implementing two methods:

- `__enter__(self)` — runs when execution enters the `with` block; whatever it returns gets bound to the `as` variable.
- `__exit__(self, exc_type, exc_val, exc_tb)` — runs unconditionally when the `with` block exits.

If the block exits normally, all three exception arguments passed to `__exit__` are `None`. If it exits because of an exception, they carry the exception's type, value, and traceback instead.

```python
class DatabaseConnection:
    """A context manager that wraps a psycopg2 connection lifecycle."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Opens connection and cursor, returns the cursor for use in the block."""
        import psycopg2
        self.conn = psycopg2.connect(self.dsn)
        self.cursor = self.conn.cursor()
        return self.cursor  # This is what 'as cursor' binds to

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commits on a clean exit, rolls back on any exception.
        Always closes the cursor and connection.
        """
        if exc_type is None:
            # No exception: commit the transaction
            self.conn.commit()
        else:
            # Exception occurred: roll back all changes
            self.conn.rollback()

        # Cleanup runs regardless of success or failure
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

        # Return False: let the exception propagate to the caller
        return False


# Usage
DSN = "postgresql://user:password@localhost/prod_db"

with DatabaseConnection(DSN) as cursor:
    cursor.execute("INSERT INTO logs (msg) VALUES (%s)", ("System started",))
    cursor.execute("INSERT INTO logs (msg) VALUES (%s)", ("All services online",))
    # If either execute() raises an exception, __exit__ rolls back BOTH inserts
    # and closes the connection before the exception propagates

print("Transaction complete.")
```

Stepping through what actually happens: Python evaluates `DatabaseConnection(DSN)` to create the object, then calls `__enter__()`, which opens the connection and cursor and returns the cursor. That cursor gets bound to the `as` name, and the `with` block body runs. If the block finishes normally, Python calls `__exit__(None, None, None)` and the transaction commits. If something inside the block raises an exception instead, Python calls `__exit__` again — but this time with the exception details filled in — and the transaction rolls back. Either way, the connection and cursor get closed before control leaves the `with` statement.

The return value of `__exit__` controls what happens to that exception next. Returning `True` tells Python to suppress it completely — your program just continues as if nothing went wrong, even if what happened was something serious, like a failed write halfway through a transaction. Only return `True` when swallowing that exception is genuinely the intended behaviour. The safe default is to return `False` (or nothing at all, which Python treats the same way), so errors keep propagating normally and don't disappear silently.

It's also worth avoiding raising a brand-new exception from inside `__exit__` itself — if the `with` block already raised one, a new exception thrown during cleanup will bury the original, which makes debugging much harder later. And this is exactly why reaching for a context manager matters for things like database connections in the first place: skip it, and an exception raised mid-query means the cursor and connection are never closed, quietly leaking that connection for as long as your program keeps running.

### 11.2 Using the `contextlib.contextmanager` Decorator

Writing a full class for a simple context manager is often more code than you need. The `contextlib.contextmanager` decorator lets you write a generator function with a single `yield` instead, and Python converts it into a context manager automatically.

The rule is simple: code written *before* `yield` acts as `__enter__`. Code written *after* `yield` acts as `__exit__`. Whatever you yield is what gets bound to the `as` variable.

```python
from contextlib import contextmanager
import time

@contextmanager
def managed_transaction(conn):
    """
    Context manager for database transaction lifecycle.
    No class required — pure generator syntax.
    """
    cursor = conn.cursor()
    try:
        yield cursor          # <-- This IS the __enter__ return value
        conn.commit()         # Runs only if no exception occurred
    except Exception:
        conn.rollback()       # Runs only if an exception occurred
        raise                 # Re-raise: do not suppress the exception
    finally:
        cursor.close()        # Runs ALWAYS — success or failure


# Usage is identical to the class-based version
with managed_transaction(conn) as cursor:
    cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (500, 1))
```

There's one critical rule here: you must wrap the `yield` in a `try/finally` block. Here's why it matters — when an exception happens inside your `with` block, Python doesn't simply let your generator carry on past the `yield`. It reaches back into the generator and raises the exception at the exact point where `yield` was paused, as if the `yield` expression itself had thrown it. If there's no `try/finally` wrapped around that `yield`, any cleanup code written after it never runs, because the exception jumps straight past it on its way out.

A few habits worth keeping in mind: `@contextmanager` only allows exactly one `yield` in the function — if you accidentally yield a second time, Python raises a `RuntimeError`. If you genuinely need to manage several resources inside one `with` block, look at `contextlib.ExitStack` in Section 11.4 instead. And one to remember once you're writing async code: a regular `with` block won't work with something built for `async def` — those need `async with`, paired with `__aenter__`/`__aexit__` (or `@asynccontextmanager`), otherwise setup and teardown will block your entire event loop.

### 11.3 Practical Example: Timing Execution

Context managers are the right tool for timing arbitrary blocks of code. A decorator (Section 9) times one specific function. A context manager can time *any* block of code — including code you don't own and can't add a decorator to.

```python
from contextlib import contextmanager
import time
import tracemalloc


@contextmanager
def profile_block(label: str, track_memory: bool = False):
    """
    Context manager that measures wall-clock time and optionally peak RAM
    for any arbitrary block of code.

    Usage:
        with profile_block("ETL transform step"):
            transform_data(records)
    """
    # --- ENTRY ---
    if track_memory:
        tracemalloc.start()

    start_time = time.perf_counter()

    try:
        yield  # Execute the with-block body

    finally:
        # --- EXIT (guaranteed to run) ---
        elapsed = time.perf_counter() - start_time

        if track_memory:
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            print(
                f"[{label}] "
                f"Time: {elapsed * 1000:.2f}ms | "
                f"Peak RAM: {peak_mem / 1024:.1f} KB"
            )
        else:
            print(f"[{label}] Time: {elapsed * 1000:.2f}ms")


# --- Production usage pattern ---

def load_records(filepath: str) -> list[dict]:
    """Simulates loading a large dataset."""
    import json
    with open(filepath, "r") as f:
        return json.load(f)


def filter_errors(records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("level") == "ERROR"]


# Time individual pipeline stages with memory tracking
with profile_block("Load phase", track_memory=True):
    records = load_records("server.log.json")

with profile_block("Filter phase"):
    errors = filter_errors(records)

print(f"Processed {len(errors)} error records.")
```

**Sample output:**

```text
[Load phase]   Time: 142.30ms | Peak RAM: 8420.3 KB
[Filter phase] Time: 3.87ms
Processed 847 error records.
```

> [!NOTE]
> **Why `time.perf_counter()` instead of `time.time()`?** `time.time()` reflects the system clock, which can occasionally jump backward — for example, when it syncs with an internet time server — which could make a measured duration come out negative. `time.perf_counter()` is a steadily increasing timer built specifically for measuring how long things take, which makes it the right tool whenever you're timing code.

### 11.4 `contextlib.ExitStack` — Managing Multiple Resources

`ExitStack` is a context manager that manages a dynamic collection of *other* context managers. It lets you enter a variable number of them within a single `with` block, and guarantees all their exits are called in reverse order (last opened, first closed).

```python
from contextlib import ExitStack


def process_pipeline(input_path: str, output_path: str, db_conn) -> None:
    """
    Opens three resources dynamically:
    - input file
    - output file
    - database transaction cursor

    All three are guaranteed to be cleaned up correctly.
    """
    with ExitStack() as stack:
        # Each enter_context() call registers a context manager with the stack
        infile  = stack.enter_context(open(input_path, "r"))
        outfile = stack.enter_context(open(output_path, "w"))
        cursor  = stack.enter_context(managed_transaction(db_conn))

        # Process
        for line in infile:
            outfile.write(line.upper())
            cursor.execute(
                "INSERT INTO processed_lines (content) VALUES (%s)",
                (line.strip(),)
            )

    # All three exits are called in reverse order:
    # cursor's exit first → outfile's exit → infile's exit
```

---

**Practice:**
1. Write a class-based context manager `BattleTimer` that prints `"Battle started!"` on enter and `"Battle ended after X seconds"` on exit, using `time.perf_counter()`.
2. Rewrite the same `BattleTimer` using `@contextlib.contextmanager` instead of a class.
3. Use `ExitStack` to open two files at once, copying the contents of one into the other in uppercase.

---

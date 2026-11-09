## Section 12: Modules & Packages

A **module** is just a Python file — any `.py` file you write can be imported into another. A **package** is a folder of modules grouped together, marked with an `__init__.py` file so Python knows to treat it as one unit. This system is how Python lets you split code across multiple files instead of cramming everything into one giant script, and reuse that code between projects.

### 12.1 Importing Modules

There are four syntaxes for importing:

```python
import json                          # Binds the module object to the name 'json'
from json import loads               # Binds only 'loads' from the module
import json as j                     # Binds the module to the alias 'j'
from json import loads, dumps        # Multiple names from one module
from json import *                   # Avoid this — see the note below
```

**The standard library is always available — no installation required:**

```python
import os           # Operating system interface (paths, env vars, processes)
import sys          # Python runtime (argv, path, version, modules)
import json         # JSON encoding/decoding
import time         # Time measurement and delays
import datetime     # Date and time objects
import re           # Regular expressions
import pathlib      # Object-oriented file paths (modern os.path replacement)
import logging      # Production logging framework
import collections  # Specialized data structures (deque, defaultdict, Counter)
import itertools    # Memory-efficient iteration tools
import functools    # Higher-order functions (wraps, lru_cache, partial)
import tracemalloc  # Memory allocation tracing
import asyncio      # Asynchronous I/O framework
import unittest     # Built-in testing framework
import contextlib   # Utilities for context managers
import threading    # Thread-based parallelism
import multiprocessing  # Process-based parallelism
import subprocess   # Run external processes
import hashlib      # Cryptographic hash functions
import base64       # Base64 encoding/decoding
import csv          # CSV file reading and writing
```

> [!NOTE]
> Python only actually loads a module's code once per program run — after the first `import json`, every later `import json` anywhere in your program just reuses what's already loaded, so it's effectively free.

A few habits worth avoiding here: `from module import *` pulls in every name from that module without you knowing exactly what you're getting, and it can silently overwrite your own function or variable names if they happen to clash. It's almost always better to import only what you need, by name. It's also worth keeping all your imports together at the top of the file rather than inside a function or loop — Python's caching makes repeated imports cheap, but grouping them at the top keeps it obvious at a glance what a file depends on.

### 12.2 Writing Your Own Module

Any `.py` file is a module. Name it with `snake_case` — the filename becomes the import name, minus the `.py`.

**A clean, well-organised module typically has four sections:**

```python
# File: log_utils.py

# ─── 1. IMPORTS ────────────────────────────────────────────────────────────────
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Generator

# ─── 2. MODULE-LEVEL CONSTANTS (not mutable globals) ──────────────────────────
LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] "
    r"(?P<message>.+)$"
)

# ─── 3. PUBLIC FUNCTIONS AND CLASSES ──────────────────────────────────────────
def parse_log_line(line: str) -> dict | None:
    """
    Parses a single log line matching the format:
        2024-01-15 14:23:01 [ERROR] Connection refused

    Returns:
        dict with 'timestamp', 'level', 'message' keys,
        or None if the line doesn't match the expected format.
    """
    match = _LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return {
        "timestamp": datetime.fromisoformat(match.group("timestamp")),
        "level": match.group("level"),
        "message": match.group("message"),
    }


def stream_errors(filepath: str | Path) -> Generator[dict, None, None]:
    """
    Memory-safe generator that streams only ERROR-level log entries
    from a file of any size.

    Args:
        filepath: Path to the log file.

    Yields:
        Parsed log entry dicts for ERROR-level lines only.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed and parsed["level"] == "ERROR":
                yield parsed


# ─── 4. GUARD: code that only runs when executed directly ─────────────────────
if __name__ == "__main__":
    # This block runs when you do: python log_utils.py
    # It does NOT run when you do: import log_utils
    import sys

    if len(sys.argv) < 2:
        print("Usage: python log_utils.py <logfile>")
        sys.exit(1)

    for entry in stream_errors(sys.argv[1]):
        print(f"[{entry['timestamp']}] {entry['message']}")
```

**Importing it from another file:**

```python
# File: pipeline.py
from log_utils import stream_errors, parse_log_line  # Clean, explicit imports

errors = list(stream_errors("server.log"))
print(f"Found {len(errors)} errors")
```

Every module has a `__name__` attribute. When you run a file directly (`python log_utils.py`), Python sets `__name__` to `"__main__"`. When that same file is imported by something else instead, `__name__` is set to the module's own name (`"log_utils"`). The `if __name__ == "__main__":` guard uses this difference to separate "code that should only run when this file is executed directly" from "code that should run whenever this file is imported." Without that guard, importing a file would also re-run any test or demo code sitting at the bottom of it.

It's worth being careful with variables defined directly at module level, outside any function. Since Python only loads a module once and reuses it everywhere it's imported, any mutable state sitting at that level is effectively shared by everyone who imports it — which tends to produce confusing bugs as a project grows. In the same vein, try to keep actual executable code outside of functions and outside the `__name__` guard to a minimum. Anything sitting directly in a module's body — like opening a database connection — runs the moment that module is imported, whether you intended it to or not, which makes imports slow and unpredictable, and can cause test suites to trigger side effects they don't actually need.

### 12.3 Packages

A **package** is a directory that Python treats as a module namespace. It needs an `__init__.py` file, which can be completely empty.

**Example package structure for a small ETL project:**

```
etl_pipeline/                     ← Root package directory
│
├── __init__.py                   ← Package initializer (often exposes public API)
├── config.py                     ← Configuration and settings
│
├── extract/                      ← Sub-package for data extraction
│   ├── __init__.py
│   ├── file_reader.py
│   └── api_client.py
│
├── transform/                    ← Sub-package for data transformation
│   ├── __init__.py
│   ├── validators.py
│   └── normalizers.py
│
└── load/                         ← Sub-package for data loading
    ├── __init__.py
    └── postgres_writer.py
```

**The `__init__.py` file controls the package's public API:**

```python
# etl_pipeline/__init__.py

# Option A: Empty — users must import from submodules directly
# from etl_pipeline.extract.file_reader import stream_csv

# Option B: Re-export the most important symbols (convenience API)
from .extract.file_reader import stream_csv, stream_json
from .transform.validators import validate_record
from .load.postgres_writer import upsert_batch

__all__ = ["stream_csv", "stream_json", "validate_record", "upsert_batch"]
```

With Option B, users can write `from etl_pipeline import stream_csv` instead of typing out the full path.

`__all__` explicitly declares the package's public API:

```python
__all__ = ["stream_csv", "stream_json"]
# Only these names get exported by 'from etl_pipeline import *'
# (Still good practice to define __all__ even if you never use wildcard imports yourself)
```

Try not to import everything into `__init__.py`. If a package's `__init__.py` pulls in every submodule — including ones that open database connections or import heavy libraries — then just doing `import etl_pipeline` triggers all of that, even if the caller only wanted one small function. Keeping `__init__.py` lean, exposing only what callers actually need, keeps imports fast and predictable.

Circular imports are another common stumbling block: if module A imports something from module B, and module B also imports something from module A, Python can get confused about which one to finish loading first, since neither is fully ready yet. This usually shows up as an `ImportError` mentioning a "partially initialized module." The fix is generally to move the shared piece of code into a third module that both A and B can import from independently.

### 12.4 Absolute vs. Relative Imports

**Absolute imports** specify the full path from the project root:

```python
# Inside etl_pipeline/transform/validators.py
from etl_pipeline.config import settings           # Full absolute path
from etl_pipeline.extract.file_reader import stream_csv
```

**Relative imports** use dots (`.`) to specify position relative to the current module:

```python
# Inside etl_pipeline/transform/validators.py
from ..config import settings              # '..' = go up one level (to etl_pipeline/)
from ..extract.file_reader import stream_csv   # '..' up, then into extract/
from .normalizers import normalize_text    # '.' = current package (transform/)
```

**Dot notation reference:**

```text
.         One dot  = current package   (same directory)
..        Two dots = parent package    (one level up)
...       Three    = grandparent       (two levels up)
```

**When to use which:**

| Scenario | Use |
|---|---|
| Importing from the standard library | Absolute (`import json`) |
| Importing from third-party packages | Absolute (`import pydantic`) |
| Importing a sibling module in the same package | Relative (`from .sibling import X`) |
| Importing from a parent package | Relative (`from ..config import Y`) |
| Running a script directly | Absolute only (relative imports fail) |

One thing that catches people off guard: relative imports only work when a file is being imported as part of a package. If you try to run that same file directly as a script, Python won't know what `..` is relative to, and you'll get an `ImportError`. Scripts meant to be run directly should stick to absolute imports.

It's also worth being consistent — pick either absolute or relative imports for your own project's internal modules, and stick with that choice throughout, rather than mixing both styles in the same file. And one easy trap worth avoiding entirely: never name your own files the same as a standard library module — `json.py`, `os.py`, `time.py` are all landmines. Because Python checks your current folder before the standard library, your file will silently replace the real one for any code running in that directory, and the errors that follow tend to be confusing to track down.

---

**Practice:**
1. Create a module called `combat_utils.py` with a function `calculate_damage(base, multiplier)`. Import and use it from a second file.
2. Add an `if __name__ == "__main__":` guard to `combat_utils.py` that runs a small test when the file is executed directly, but not when it's imported.
3. Turn `combat_utils.py` into part of a small package: create a `game/` folder with an `__init__.py`, move your module inside, and re-export `calculate_damage` from the package's `__init__.py` so it can be imported as `from game import calculate_damage`.

---

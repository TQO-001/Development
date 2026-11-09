## Section 12 Exercises: Modules & Packages (Deep Dive)

These exercises need real multi-file folders, not single scripts — that's the whole point of this section. Make a folder called `section12_practice/` and build each exercise as its own subfolder inside it.

---

### 🟢 Warm-Up — Two-File Import
**Time:** ~10 min

**Goal:** Prove to yourself how `import` actually finds and binds a name.

- [ ] Create `mymath.py` with one function, `def add(a, b): return a + b`.
- [ ] Create `main.py` in the same folder with `import mymath`, then call `mymath.add(2, 3)` and print it.
- [ ] Now change it to `from mymath import add` and call `add(2, 3)` directly (no prefix).
- [ ] Now change it to `import mymath as mm` and call `mm.add(2, 3)`.

**Done when:** All three import styles produce the same result `5`, and you can explain the difference between them in one sentence each.

---

### 🟡 Core — The `__name__ == "__main__"` Guard
**Time:** ~10 min

**Goal:** Observe the exact behavior difference between running a file directly vs. importing it (per notes 12.2).

- [ ] In `mymath.py`, add a line at the bottom: `print("mymath.py was loaded")`, then `if __name__ == "__main__": print("Running directly!")`.
- [ ] Run `python mymath.py` directly in the terminal — note what prints.
- [ ] Now run `python main.py` (which imports `mymath`) — note what's different.

**Done when:** You can explain in a comment why `"Running directly!"` only appeared in one of the two runs.

---

### 🟡 Core — Build a Minimal Package
**Time:** ~15 min

**Goal:** Turn a folder into an importable package, per the structure in notes 12.3.

- [ ] Create a folder `shapes/` containing `__init__.py` and `circle.py` (with a function `area(radius)`).
- [ ] In `shapes/__init__.py`, re-export it: `from .circle import area`.
- [ ] From a script OUTSIDE the `shapes/` folder (a sibling `main.py`), do `from shapes import area` and call it — without ever writing `shapes.circle.area`.

**Done when:** `from shapes import area` works because of the re-export in `__init__.py`, not because you imported the submodule directly.

---

### 🟠 Applied — Practice All Four Import Syntaxes In One File
**Time:** ~10 min

**Goal:** Cement the four import patterns from notes 12.1 using only the standard library (no installs needed).

- [ ] `import json` — use `json.dumps({"a": 1})`.
- [ ] `from datetime import datetime` — print `datetime.now()`.
- [ ] `import pathlib as pl` — create a `Path` object using the alias.
- [ ] `from collections import Counter, defaultdict` — use both in one line each.
- [ ] In a comment above each import, write one sentence on WHEN you'd reach for that particular style in real code.

**Done when:** All four styles run without error and your comments show you understand the *use case*, not just the syntax.

---

### 🟠 Applied — Break It, Then Fix It: Circular Imports
**Time:** ~20 min

**Goal:** This is the most useful debugging skill in this whole section — deliberately cause the exact error described in notes 12.3 (Anti-Pattern 2), then fix it.

- [ ] Create `models.py` with `from validators import validate_model` at the top, and a class `BaseModel`.
- [ ] Create `validators.py` with `from models import BaseModel` at the top, and a function `validate_model`.
- [ ] Run `python models.py` and **read the actual traceback carefully** — copy the exact error message into a comment.
- [ ] Now fix it using the approach from your notes: move the shared piece (`BaseModel`) into a third file, `base.py`, and have both `models.py` and `validators.py` import from `base.py` instead of from each other.
- [ ] Confirm it runs cleanly after the fix.

**Done when:** You've seen the real `ImportError` with your own eyes (not just read about it) and fixed it using the third-module pattern — not a local/inline import workaround.

---

### 🔴 Challenge — Relative Imports Across a 3-Level Package
**Time:** ~20 min

**Goal:** Recreate a simplified version of the `etl_pipeline` structure from notes 12.3/12.4 and practice `.` vs `..` relative imports.

- [ ] Build this structure:
  ```
  toolkit/
  ├── __init__.py
  ├── config.py            (has a constant, e.g. VERSION = "1.0")
  ├── processing/
  │   ├── __init__.py
  │   ├── cleaner.py        (a function, e.g. clean_text(s))
  │   └── formatter.py      (a function that imports clean_text using a RELATIVE "." import, then formats it)
  ```
- [ ] In `formatter.py`, import `clean_text` from `cleaner.py` using a single-dot relative import.
- [ ] In `formatter.py`, ALSO import `VERSION` from `config.py` using a double-dot relative import (`..config`).
- [ ] From a script outside `toolkit/`, do `from toolkit.processing.formatter import format_text` (or similar) and run it.

**Done when:** Both relative imports (`.` and `..`) resolve correctly, and you can explain why running `python toolkit/processing/formatter.py` directly would fail with `ImportError: attempted relative import with no known parent package` (per notes 12.4) — try it and confirm.

---

### 💀 BOSS — Build a Mini "Toolbox" Package
**Time:** ~35–40 min

**Goal:** Build a small, properly structured utility package — this is the realistic shape of a piece of any real Python project (and directly applicable to organizing Emlindweni or Delulu scripts later).

**Requirements:**
- [ ] Folder `toolbox/` with `__init__.py`.
- [ ] `toolbox/string_utils.py` — two functions, e.g. `slugify(text)` and `truncate(text, length)`.
- [ ] `toolbox/file_utils.py` — two functions, e.g. `read_lines(path)` and `count_words(path)` (using `pathlib`).
- [ ] `toolbox/math_utils.py` — two functions, e.g. `percentage(part, whole)` and `clamp(value, low, high)`.
- [ ] In `toolbox/__init__.py`: re-export exactly one function from EACH submodule, and define `__all__` listing only those three re-exported names (per the `__all__` pattern in notes 12.3).
- [ ] A `main.py` OUTSIDE the package that does `from toolbox import <fn1>, <fn2>, <fn3>` (the three re-exported ones) and also does `from toolbox.string_utils import truncate` (a DIRECT submodule import for a function you did NOT re-export) — proving you understand both access paths.
- [ ] Call all 6 functions total and print their results.

**Done when:** `main.py` runs cleanly using a mix of package-level imports (via `__init__.py`) and direct submodule imports, and you can explain in a comment why you'd choose to re-export some functions but not others.

---

### ✅ Section Progress
- [ ] Warm-Up: Two-file import
- [ ] Core: `__name__ == "__main__"` guard
- [ ] Core: Minimal package with `__init__.py`
- [ ] Applied: Four import syntaxes
- [ ] Applied: Break/fix circular import
- [ ] Challenge: 3-level relative imports
- [ ] 💀 BOSS: `toolbox/` package

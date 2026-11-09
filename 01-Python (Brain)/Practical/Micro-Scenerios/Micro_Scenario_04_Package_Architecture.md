# 🔬 Micro-Scenario 04 — The Tangled Package
**Complexity:** ⭐⭐⭐ Medium-High
**Skill Targets:** Section 12 — Modules & Packages · Circular import resolution · Mutable module-level state · `__init__.py` API design · Absolute imports
**Portfolio Context:** The **Navy** job tracker codebase has grown to three modules that are all importing each other. The CI pipeline is failing with `ImportError`. A junior dev tried to fix it by adding `from .models import *` everywhere. It now imports but produces wrong results. You need to untangle the architecture.

---

## Step 1 — The Broken Junior Implementation

```
navy/
├── __init__.py
├── models.py
├── validators.py
└── services.py
```

```python
# navy/models.py
from .services import format_salary          # ← Imports from services

class Job:
    def __init__(self, title: str, company: str, salary: int):
        self.title   = title
        self.company = company
        self.salary  = format_salary(salary) # Uses services at class definition time

class Application:
    count = 0          # ← Mutable class-level counter (shared state anti-pattern)

    def __init__(self, job: Job, status: str = "applied"):
        self.job    = job
        self.status = status
        Application.count += 1
```

```python
# navy/services.py
from .models import Job, Application         # ← Imports from models
                                             # CIRCULAR: models→services→models

_all_applications: list = []                 # ← Mutable module-level global

def add_application(job: Job) -> Application:
    app = Application(job)
    _all_applications.append(app)            # Mutates module-level state
    return app

def get_applications() -> list:
    return _all_applications                 # Returns direct reference to mutable list

def format_salary(amount: int) -> str:
    return f"R {amount:,}"
```

```python
# navy/validators.py
from .models import *                        # ← Wildcard import — unknown what comes in
from .services import *                      # ← Wildcard import — doubles the confusion

def validate_job(title, company, salary):
    if not title or not company:
        return False, "Title and company required"
    if salary < 0:
        return False, "Salary must be positive"
    return True, "OK"
```

```python
# navy/__init__.py
# Imports everything to make top-level access "convenient"
from .models   import *
from .services import *
from .validators import *
# Result: 'navy.Job', 'navy.Application', 'navy.add_application', etc.
# But also: 'navy.count', 'navy._all_applications' — internal state is public
```

```python
# main.py — caller
import navy

job = navy.Job("Python Dev", "Acme Corp", 45000)
navy.add_application(job)
navy.add_application(job)

print(navy.Application.count)       # Might show 2... or 4... depends on import order
print(navy.get_applications())      # Returns internal list — caller can mutate it directly
```

---

## Step 2 — Senior Architectural Walkthrough

### Bug 1 — Circular Import: `models.py` ↔ `services.py`
```python
# models.py
from .services import format_salary    # models needs services

# services.py
from .models import Job, Application   # services needs models
```
Python processes imports sequentially. When `models.py` is first imported, it immediately tries to import `services.py`. `services.py` then tries to import `models.py` — but `models.py` is not finished loading yet (it's still in the middle of being processed). Python returns a partially-initialized `models` module. `Job` and `Application` don't exist in it yet. Result: `ImportError: cannot import name 'Job' from partially initialized module 'navy.models'`.

**The rule:** If A needs B and B needs A, introduce a third module C that neither A nor B imports.

**Fix pseudocode:**
```
navy/
├── models.py      — Pure data classes. No imports from other navy modules.
├── formatters.py  — format_salary() lives here. Imports nothing from navy.
├── validators.py  — Imports from models only. No circular dependency.
├── services.py    — Imports from models + formatters. The "orchestrator" layer.
└── __init__.py    — Exposes only the public API explicitly.

models.py   → imports: nothing from navy
formatters.py → imports: nothing from navy
validators.py → imports: models
services.py → imports: models, formatters
__init__.py → imports: specific names from services, validators
```

### Bug 2 — Mutable Module-Level Global
```python
# services.py
_all_applications: list = []   # Module-level mutable list
```
This list is shared across ALL importers. In tests, applications from one test case bleed into the next. In a web server with multiple requests, concurrent modifications corrupt the list. Module-level state should be read-only (constants, compiled regexes). Mutable state belongs in class instances.

**Fix pseudocode:**
```
Create class ApplicationRepository:
    def __init__(self):
        self._store: list[Application] = []
    def add(self, app): self._store.append(app)
    def all(self) -> list: return list(self._store)   # Return a COPY, not the internal list

# Callers create their own instance — no shared global state
repo = ApplicationRepository()
```

### Bug 3 — Wildcard Imports in `validators.py`
```python
from .models import *
from .services import *
```
No one reading `validators.py` can tell which names are local and which came from imports. Static analysis tools (`mypy`, `pylance`) cannot resolve types. Replace with explicit named imports.

### Bug 4 — `__init__.py` exposes internal state
```python
from .services import *    # Exports _all_applications — a private list — as a public name
```
`__init__.py` should be a deliberate public contract. Use `__all__` and only export what callers need.

---

## Step 3 — Validation Challenge

Restructure the `navy/` package to eliminate all four bugs. Your final structure must be:

```
navy/
├── __init__.py
├── models.py
├── formatters.py
├── validators.py
└── services.py
```

The validation script below must pass. Run it from the directory containing the `navy/` folder.

```python
# test_navy_package.py
import unittest
import importlib
import sys


class TestPackageArchitecture(unittest.TestCase):

    def setUp(self):
        """Remove any cached navy modules before each test for a clean import."""
        to_remove = [key for key in sys.modules if key.startswith("navy")]
        for key in to_remove:
            del sys.modules[key]

    def test_import_does_not_raise(self):
        """The package must import without ImportError."""
        try:
            import navy
        except ImportError as e:
            self.fail(f"Import failed: {e}")
        print("✅ ASSERTION 1 PASSED: Package imports cleanly")

    def test_no_circular_imports(self):
        """Each submodule must be importable independently."""
        modules = ["navy.models", "navy.formatters", "navy.validators", "navy.services"]
        for mod in modules:
            with self.subTest(module=mod):
                try:
                    importlib.import_module(mod)
                except ImportError as e:
                    self.fail(f"Circular import detected in {mod}: {e}")
        print("✅ ASSERTION 2 PASSED: No circular imports in any submodule")

    def test_public_api_exists(self):
        """navy package must expose Job, Application, ApplicationRepository, validate_job."""
        import navy
        for name in ["Job", "Application", "ApplicationRepository", "validate_job"]:
            self.assertTrue(hasattr(navy, name), f"navy.{name} not exposed in __init__.py")
        print("✅ ASSERTION 3 PASSED: Public API correctly exposed")

    def test_private_state_not_exposed(self):
        """Internal mutable state must NOT be accessible via the package top-level."""
        import navy
        # _all_applications or any private list must not be on the package namespace
        self.assertFalse(hasattr(navy, "_all_applications"),
            "Internal state '_all_applications' should not be public")
        print("✅ ASSERTION 4 PASSED: Internal state is not exposed")

    def test_no_wildcard_imports(self):
        """No module in the package may use 'import *' syntax."""
        import ast, pathlib
        package_dir = pathlib.Path("navy")
        for py_file in package_dir.glob("*.py"):
            source = py_file.read_text()
            tree   = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        self.assertNotEqual(alias.name, "*",
                            f"Wildcard import found in {py_file.name}")
        print("✅ ASSERTION 5 PASSED: Zero wildcard imports in package")

    def test_repository_state_is_isolated(self):
        """Two ApplicationRepository instances must NOT share state."""
        from navy.services import ApplicationRepository
        from navy.models import Job
        from navy.formatters import format_salary

        repo1 = ApplicationRepository()
        repo2 = ApplicationRepository()

        job = Job("Python Dev", "Acme", 45000)
        repo1.add(job)

        self.assertEqual(len(repo1.all()), 1)
        self.assertEqual(len(repo2.all()), 0,
            "repo2 should not contain entries added to repo1 — shared global state detected")
        print("✅ ASSERTION 6 PASSED: Repository instances are isolated")

    def test_all_returns_copy(self):
        """ApplicationRepository.all() must return a copy, not the internal list."""
        from navy.services import ApplicationRepository
        from navy.models import Job

        repo = ApplicationRepository()
        job  = Job("Dev", "Corp", 40000)
        repo.add(job)

        external = repo.all()
        external.clear()                    # Mutate the returned list

        self.assertEqual(len(repo.all()), 1,
            "Mutating the returned list should not affect the internal store")
        print("✅ ASSERTION 7 PASSED: all() returns a defensive copy")

    def test_format_salary_output(self):
        """format_salary must format integers as 'R X,XXX'."""
        from navy.formatters import format_salary
        self.assertEqual(format_salary(45000), "R 45,000")
        self.assertEqual(format_salary(1000000), "R 1,000,000")
        print("✅ ASSERTION 8 PASSED: format_salary formats correctly")


if __name__ == "__main__":
    unittest.main(verbosity=0)
```

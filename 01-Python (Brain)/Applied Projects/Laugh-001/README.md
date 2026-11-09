# PROJECT 1 — CLI Task Manager

## 🏢 LaughTale Brief

**Client:** Internal (LaughTale productivity tooling)
**Ticket:** LAUGH-001
**Priority:** Low
**Type:** CLI Application

A lightweight command-line task manager for developers who live in the terminal. Users can add, list, complete, and delete tasks. Tasks persist between sessions. The tool is installed as a command (`lt-tasks`) and works on any machine with Python 3.12+.

This is the first project. It intentionally uses no web framework and no database. Every concept here appears in every future project.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Data Model | OOP, dataclasses, `__repr__`, `__eq__` | — |
| Storage | File I/O, JSON, context managers | — |
| Logic | Modules, packages, `__init__.py` | Sorting by priority/date |
| CLI | `argparse` or `typer`, `__main__` | — |
| Error Handling | Custom exceptions, try/except/finally | — |
| Testing | `pytest`, unit tests, temp files | — |

---

## 💼 Hiring Value

This project demonstrates you can: structure a Python project, write clean OOP, handle file I/O safely, and build a usable CLI tool. Relevant to: **any Python developer role**, **DevOps/tooling engineer**, **junior backend developer**.

Companies that use similar internal tools: every software company with a Python engineering team.

---

## 🔍 Why These Choices

**Why JSON for storage, not a database?**
The data is small, local, and belongs to one user on one machine. A database would require a running server process. JSON files are portable, human-readable, and editable with any text editor. The right tool for the actual scope — not the imagined future scope.

**Why dataclasses, not plain dicts?**
Dicts have no schema. `task["completd"]` silently returns nothing instead of raising an error. A dataclass with type hints catches typos at IDE level and documents the data shape to every reader.

**Why a context manager for file operations?**
The file must be closed whether the write succeeds or raises an exception. A `with open(...)` block guarantees this. Without it, a crash between open and close produces a corrupted or locked file.

**Why custom exceptions?**
`raise ValueError("Task not found")` is ambiguous — it could mean anything. `raise TaskNotFoundError(task_id)` tells the caller exactly what went wrong and lets them catch it specifically without catching unrelated ValueErrors.

---

## 🏗️ Architecture

```
lt-tasks (CLI entry point)
       │
       ▼
  TaskManager              ← business logic, no I/O
  (service layer)
       │
       ▼
  TaskRepository           ← all file I/O lives here
  (storage layer)
       │
       ▼
  tasks.json               ← persistent storage
```

**Key principle:** `TaskManager` never calls `open()`. `TaskRepository` never makes business decisions. Separating concerns means you can swap JSON for a database later by rewriting only `TaskRepository`.

---

## 📋 Build Phases

### Phase 1: Project Setup (30 min)

Create the folder structure:
```
lt_tasks/
├── __init__.py
├── __main__.py          # python -m lt_tasks entry point
├── models.py            # Task dataclass
├── exceptions.py        # Custom exceptions
├── repository.py        # File I/O
├── service.py           # Business logic
└── cli.py               # CLI interface
tests/
├── test_service.py
└── test_repository.py
```

Write the ADR: why JSON, why this structure, why no framework.

**Done when:** `python -m lt_tasks --help` runs without error (even if it does nothing yet).

### Phase 2: Data Model

In `models.py`, define:
```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Task:
    title: str
    priority: str = "medium"        # "low" | "medium" | "high"
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

In `exceptions.py`, define:
- `TaskNotFoundError(task_id)` — raised when a task ID does not exist
- `InvalidPriorityError(value)` — raised when priority is not low/medium/high
- `StorageError(message)` — raised when the JSON file cannot be read or written

Why three separate exceptions? The CLI layer catches each one and shows a different message. If all were `ValueError`, you could not distinguish "task missing" from "file corrupted" from "bad input".

**Done when:** You can instantiate a `Task` and its `id` is a unique UUID every time.

### Phase 3: Repository (File I/O)

In `repository.py`, implement `TaskRepository`:
- `__init__(self, filepath: Path)` — stores the path, creates the file if missing
- `load_all(self) -> list[Task]` — reads JSON, deserialises to `Task` objects
- `save_all(self, tasks: list[Task])` — serialises and writes atomically

**Atomic write pattern** — critical for data safety:
```python
def save_all(self, tasks: list[Task]):
    # Write to a temp file first, then rename
    # If the write fails, the original file is untouched
    tmp = self.filepath.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in tasks], f, indent=2)
    tmp.replace(self.filepath)   # Atomic on POSIX systems
```

Why atomic writes? If the program crashes mid-write, you get a half-written JSON file that is not valid JSON. The temp-then-rename pattern ensures the file is either fully written or fully untouched.

**Done when:** `load_all()` on a non-existent file returns `[]`. `save_all()` → `load_all()` round-trips correctly.

### Phase 4: Service (Business Logic)

In `service.py`, implement `TaskManager(repository: TaskRepository)`:
- `add(title, priority) -> Task` — validates priority, creates task, saves
- `list_all(sort_by="created") -> list[Task]` — returns sorted tasks
- `complete(task_id) -> Task` — marks task done
- `delete(task_id) -> None` — removes task
- `get_by_id(task_id) -> Task` — finds one task or raises `TaskNotFoundError`

The service calls `repository.load_all()` at the start of every method and `repository.save_all()` at the end. This is simple and correct for a single-user CLI tool. (A multi-user web app would need transactions — that is a future concern.)

**Done when:** All methods work in isolation with a test file, tested with `pytest`.

### Phase 5: CLI Interface

In `cli.py` using `argparse` or `typer`:
```
lt-tasks add "Buy milk" --priority high
lt-tasks list
lt-tasks list --filter pending
lt-tasks complete <task-id>
lt-tasks delete <task-id>
```

Format list output as a clean table:
```
ID       TITLE          PRIORITY   STATUS
a3f2...  Buy milk       HIGH       ⬜ pending
b1c9...  Write tests    MEDIUM     ✅ done
```

**Done when:** All five commands work end-to-end. Errors print a clean message, not a Python traceback.

### Phase 6: Testing

Write unit tests for `service.py` using a temporary JSON file:
```python
import tempfile
from pathlib import Path

@pytest.fixture
def manager():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    yield TaskManager(TaskRepository(path))
    path.unlink(missing_ok=True)
```

Test: add → list → complete → delete. Test error paths: complete non-existent ID, add invalid priority.

---

## 🚀 Deployment

```bash
# Make it installable as a command
# In pyproject.toml:
[project.scripts]
lt-tasks = "lt_tasks.__main__:main"

pip install -e .          # Install in development mode
lt-tasks --help           # Now available system-wide
```

Distribute via: PyPI (public) or a private GitHub release with a `pip install git+https://...` install command.

---

## 🔴 Extensions

- Add due dates with overdue highlighting (requires datetime comparison)
- Add tags/labels with filtering
- Export to CSV or Markdown
- Sync tasks to a remote server (POST to an API)
- Add `undo` command (keep a history stack using a list as a stack data structure)

# LaughTale Applied Projects
## 8 Production-Grade Build Exercises
### For: All Engineering Departments

---

> **How to use this document:** Each project is a real deliverable LaughTale might produce for a client. Read the entire project spec before writing a single line of code. Follow the phases in order. Reference the Engineering Handbook for all standards. The goal is not just a working program — it is a working program built the way a professional team would build it.

---

## Exercise Format

Every project follows this structure:

```
Brief        — what the client needs, written as a real ticket
Concept Map  — Python and DSA skills this exercises
Hiring Value — what jobs/companies this targets
Why          — every major technical decision explained
Architecture — system diagram
Build Phases — step-by-step guide from planning to deployment
Deploy       — how it goes live
Extensions   — harder problems once the core is done
```

---

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

---

# PROJECT 2 — Inventory Management REST API

## 🏢 LaughTale Brief

**Client:** Small retail business, track stock levels across products
**Ticket:** LAUGH-002
**Priority:** High
**Type:** REST API + PostgreSQL

A JSON REST API that manages inventory: products, stock levels, and low-stock alerts. Requires user authentication. Provides endpoints for CRUD on products and a dashboard endpoint showing items below minimum stock threshold.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| API | FastAPI, async/await, decorators (`@router.get`) | — |
| Validation | Pydantic schemas, type hints, validators | — |
| Auth | JWT, bcrypt, decorators as dependency injection | — |
| Database | PostgreSQL, parameterized queries, psycopg2 | Hash tables (dict for connection pooling) |
| Business Logic | OOP, services, repositories, context managers | Sorting (low-stock sorted by quantity asc) |
| Error Handling | Custom exceptions, global exception handler | — |
| Testing | pytest, test client, fixtures, test DB | — |

---

## 💼 Hiring Value

Demonstrates: REST API design, authentication implementation, PostgreSQL integration, async Python, input validation. Relevant to: **backend developer**, **API developer**, **fullstack developer**. This is the single most commonly tested skill in Python backend interviews.

---

## 🔍 Why These Choices

**Why FastAPI, not Flask or Django?**
FastAPI generates OpenAPI documentation automatically — the API is self-documenting. It validates request bodies via Pydantic with no extra code. It is fully async, enabling high concurrency. Flask requires manual validation. Django REST Framework is heavier than this project needs.

**Why async database queries?**
A synchronous database call blocks the entire Python thread while waiting for PostgreSQL. Async calls release the thread to handle other requests during the wait. Under load (100 concurrent users), async endpoints handle roughly 10x more requests per second than synchronous equivalents.

**Why psycopg2 with connection pooling instead of an ORM?**
ORMs (SQLAlchemy) add an abstraction layer that hides what SQL is actually running. For a project of this scope, raw SQL with parameterized queries is faster, more transparent, and easier to profile. The connection pool reuses database connections instead of opening a new connection per request (which would be 100ms overhead per request).

**Why UUID primary keys?**
If you use integer IDs (`/products/1`, `/products/2`), an authenticated user can guess other users' resources. UUID primary keys (`/products/a3f2b1c9-...`) are not guessable. This is especially important for inventory data that may contain business-sensitive pricing.

---

## 🏗️ Architecture

```
Client (browser, mobile, curl)
         │
         ▼
   FastAPI Router            ← request parsing, authentication
         │
         ▼
   Pydantic Schema           ← input validation (before any logic runs)
         │
         ▼
   InventoryService          ← business logic (what is "low stock"?)
         │
         ▼
   ProductRepository         ← SQL queries, returns domain objects
         │
         ▼
   PostgreSQL                ← persistent storage
```

---

## 📋 Build Phases

### Phase 1: Plan

Write the ERD:
```
users
  id UUID PK
  email TEXT UNIQUE NOT NULL
  password_hash TEXT NOT NULL
  is_active BOOLEAN DEFAULT TRUE
  created_at TIMESTAMPTZ
  updated_at TIMESTAMPTZ

products
  id UUID PK
  name TEXT NOT NULL
  sku TEXT UNIQUE NOT NULL          ← stock-keeping unit code
  description TEXT
  unit_price NUMERIC(10,2) NOT NULL
  quantity_on_hand INT NOT NULL DEFAULT 0
  minimum_stock INT NOT NULL DEFAULT 10
  user_id UUID FK → users.id        ← each product belongs to one user
  created_at TIMESTAMPTZ
  updated_at TIMESTAMPTZ
```

Write the API contract:
```
POST   /api/v1/auth/register        → 201 {user}
POST   /api/v1/auth/login           → 200 {access_token, refresh_token}
GET    /api/v1/products             → 200 [{product}]   (paginated)
POST   /api/v1/products             → 201 {product}
GET    /api/v1/products/{id}        → 200 {product}
PATCH  /api/v1/products/{id}        → 200 {product}
DELETE /api/v1/products/{id}        → 204
GET    /api/v1/products/low-stock   → 200 [{product}]   (sorted by quantity asc)
POST   /api/v1/products/{id}/adjust → 200 {product}     (add/remove stock)
```

### Phase 2: Database Setup

Write Alembic migration for both tables. Key points:
- Add index on `products.user_id` (every product query filters by user — without index, it scans the full table)
- Add index on `products.sku` (fast lookups when receiving shipments)
- `unit_price` as `NUMERIC(10,2)` — never `FLOAT` (floating-point rounding errors on money)

Write a `db.py` module that initialises a connection pool using `psycopg2.pool.ThreadedConnectionPool`. Pool size: `minconn=2, maxconn=10`. The pool is a module-level singleton — created once on startup, reused by every request.

### Phase 3: Auth Implementation

Implement in this order:
1. `hash_password(plain)` and `verify_password(plain, hashed)` using `bcrypt`
2. `create_access_token(user_id)` and `decode_token(token)` using `PyJWT`
3. `UserRepository.create(email, password_hash)` and `UserRepository.get_by_email(email)`
4. `/auth/register` endpoint — validate email format, check no duplicate email (catch 409), hash password, insert, return user (WITHOUT password_hash)
5. `/auth/login` endpoint — get user by email, verify password, return tokens
6. `get_current_user(token: str = Depends(oauth2_scheme))` dependency — used on every protected endpoint

Critical: the register endpoint must check for duplicate emails before hashing the password. Hashing takes ~250ms. Don't waste it before checking if the email already exists.

### Phase 4: Product CRUD

Implement `ProductRepository` with:
- All SQL uses `%s` placeholders, never f-strings
- Every query filters by `user_id = %s` — users can only see their own products
- `adjust_stock(product_id, delta, user_id)` — uses `UPDATE products SET quantity_on_hand = quantity_on_hand + %s` to avoid race conditions (never read-modify-write: `read qty → qty+5 → write` can lose concurrent updates)

Implement `InventoryService`:
- `get_low_stock(user_id)` — returns products where `quantity_on_hand < minimum_stock`, sorted by `quantity_on_hand ASC` (most critical first)

### Phase 5: Testing

Integration tests using a separate test database:
```python
# conftest.py
@pytest.fixture(scope="session")
def test_db():
    # Create test DB, run migrations, yield, drop test DB
    ...

@pytest.fixture
def auth_client(test_db):
    # Register + login, return test client with auth header set
    ...
```

Test: register → login → create product → get product → adjust stock → delete. Test auth failure: accessing product without token returns 401. Test ownership: user A cannot see user B's products.

---

## 🚀 Deployment

```bash
# Dockerfile builds the API
# docker-compose.yml runs API + PostgreSQL

# Environment variables for production (never in code):
DATABASE_URL=postgresql://user:pass@host:5432/inventorydb
SECRET_KEY=<generated with secrets.token_hex(32)>
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com

# Deploy on Hetzner Cloud:
# 1. Provision CX11 (2GB RAM) instance
# 2. Install Docker
# 3. Clone repo, copy .env.production to .env
# 4. docker-compose up -d
# 5. Verify /health endpoint returns 200
```

---

## 🔴 Extensions

- Add product categories (new table, many-to-many relationship)
- Email alerts when stock drops below minimum (background task, SMTP)
- CSV import/export of product catalogue
- Stock movement history (audit log table — append-only)
- Role-based access: owner vs staff (staff can adjust stock, cannot delete products)

---

# PROJECT 3 — CSV Data Pipeline / ETL Tool

## 🏢 LaughTale Brief

**Client:** Retail client with legacy POS system exporting daily CSV files
**Ticket:** LAUGH-003
**Priority:** Medium
**Type:** Data Engineering / ETL Script

A command-line ETL (Extract, Transform, Load) tool that reads large CSV files exported from a point-of-sale system, validates and cleans the data, applies business transformations (VAT calculation, category mapping, currency conversion), and writes the results to a PostgreSQL staging table and a clean output CSV.

Files can be 500MB+. The tool must process them without loading everything into memory.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Extraction | Generators, file I/O, context managers | — |
| Transformation | Generators chained as pipeline, decorators | Hash table (category lookup dict) |
| Validation | Custom exceptions, try/except | — |
| Loading | Batch inserts, context managers | — |
| Reporting | Sorting, counters, summary stats | Counting sort on categories |
| CLI | argparse, modules/packages | — |
| Memory | Generator expressions, lazy evaluation | Space complexity: O(1) vs O(n) |

---

## 💼 Hiring Value

Demonstrates: data engineering patterns, memory-efficient processing, generator pipelines, robust error handling on real-world messy data. Relevant to: **data engineer**, **ETL developer**, **analytics engineer**, **backend engineer**. High demand at fintech, retail, logistics, and SaaS companies.

---

## 🔍 Why These Choices

**Why generators for a 500MB file?**
Loading a 500MB CSV into a list requires ~500MB of RAM. A generator reads one line at a time, using O(1) memory regardless of file size. A 500MB file and a 5GB file use the same memory. This is the difference between a tool that works and one that crashes the server.

**Why chain generators as a pipeline instead of nested loops?**
Each stage (read → validate → transform → load) is independent and testable. You can insert a debug stage between any two stages without modifying them. Chaining is the same pattern used by Apache Spark, AWS Glue, and dbt — learning it here transfers directly.

**Why batch inserts (not one INSERT per row)?**
A single `INSERT` to PostgreSQL has ~1ms network round-trip overhead. 100,000 rows × 1ms = 100 seconds. A batch insert of 1,000 rows at a time: 100 batches × 1ms = 0.1 seconds. Batching is a 1,000x speedup for bulk loads.

**Why a hash table for category lookups?**
Each row has a raw POS category code (`"CAT_A"`, `"CAT_B"`) that must be mapped to a display name. A dict lookup is O(1). Scanning a list of categories for each of 500,000 rows would be O(n·m) — catastrophic at scale.

---

## 🏗️ Architecture

```
CSV File (500MB)
      │
      ▼ generator: yields raw rows
 extract(filepath)
      │
      ▼ generator: validates each row, skips/logs bad rows
 validate(rows)
      │
      ▼ generator: applies business rules (VAT, currency, mapping)
 transform(rows, config)
      │
      ▼ batches of 1000 rows
 load(batches, db_conn, output_csv)
      │
      ├──→ PostgreSQL staging table
      └──→ clean_output.csv
```

Every stage is a generator that takes a generator and yields a generator. The data flows one record at a time through the full pipeline. Zero intermediate lists.

---

## 📋 Build Phases

### Phase 1: Plan

Define the input CSV schema:
```
date, sku, product_name, quantity, unit_price, category_code, store_id
```

Define transformation rules:
- `date`: parse to `datetime`, reject rows where date is in the future
- `quantity`: must be positive integer
- `unit_price`: must be positive decimal; apply ZA VAT (15%) to get `price_incl_vat`
- `category_code`: map via config dict to display name; unknown codes → "Uncategorised"
- `store_id`: must exist in a known stores list (loaded at startup into a set — O(1) lookup)

Write a config dataclass that holds: VAT rate, category map dict, known store IDs set, batch size.

### Phase 2: Extract Stage

```python
def extract(filepath: Path) -> Generator[dict, None, None]:
    """
    Yields one raw row dict per line.
    Memory: O(1) — only one line in memory at a time.
    """
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row   # does not load the next row until the consumer asks
```

Why `csv.DictReader` instead of splitting on commas? DictReader handles quoted fields containing commas (`"Smith, John"` is one field, not two). Manual comma-splitting breaks on real-world data.

### Phase 3: Validate Stage

```python
def validate(rows: Iterable[dict], stats: Stats) -> Generator[dict, None, None]:
    """
    Yields only valid rows. Logs and counts invalid rows.
    Raises nothing — bad rows are skipped, not fatal.
    """
    for row in rows:
        try:
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d")
            row["quantity"] = int(row["quantity"])
            row["unit_price"] = Decimal(row["unit_price"])
            if row["quantity"] <= 0 or row["unit_price"] <= 0:
                raise ValueError("Non-positive quantity or price")
            stats.valid += 1
            yield row
        except (ValueError, KeyError) as e:
            stats.invalid += 1
            stats.errors.append({"row": row.get("sku", "?"), "error": str(e)})
            # Don't raise — skip this row and continue
```

### Phase 4: Transform Stage

```python
def transform(rows: Iterable[dict], config: Config) -> Generator[dict, None, None]:
    for row in rows:
        row["price_incl_vat"] = row["unit_price"] * (1 + config.vat_rate)
        row["category"] = config.category_map.get(row["category_code"], "Uncategorised")
        row["is_known_store"] = row["store_id"] in config.known_stores   # O(1) set lookup
        yield row
```

### Phase 5: Load Stage (Batch Insert)

```python
def load(rows: Iterable[dict], conn, output_path: Path, batch_size: int = 1000):
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        batch = []
        for row in rows:
            batch.append(row)
            writer.writerow({k: row[k] for k in OUTPUT_FIELDS})

            if len(batch) >= batch_size:
                _insert_batch(conn, batch)   # Single SQL call for 1000 rows
                batch.clear()

        if batch:   # Don't forget the last partial batch
            _insert_batch(conn, batch)
```

### Phase 6: Main Pipeline + Stats Report

Wire all stages:
```python
pipeline = load(
    transform(
        validate(
            extract(input_file), stats
        ), config
    ), conn, output_file
)
```

After completion, print summary:
```
Pipeline complete in 47.3s
  Rows processed: 523,441
  Valid rows:     521,208 (99.6%)
  Invalid rows:   2,233
  Batches written: 522
  Output: clean_output.csv (47.2 MB)
```

---

## 🚀 Deployment

Deployed as a scheduled job (cron on a Hetzner server or GitHub Actions workflow):
```bash
# cron: run at 02:00 every day
0 2 * * * /app/venv/bin/python -m etl_tool --input /data/daily_export.csv --output /data/clean/ >> /var/log/etl.log 2>&1
```

The tool must be idempotent — running it twice on the same file produces the same result (use `INSERT ... ON CONFLICT DO UPDATE` or clear the staging table before loading).

---

## 🔴 Extensions

- Parallel processing: split the CSV into chunks, process with `multiprocessing.Pool`
- Schema evolution: detect and handle new/missing columns gracefully
- Delta detection: compare with yesterday's load, report what changed
- Webhook notification: POST a summary to a Slack webhook on completion

---

# PROJECT 4 — JWT Authentication Service

## 🏢 LaughTale Brief

**Client:** LaughTale platform — centralised auth for all internal services
**Ticket:** LAUGH-004
**Priority:** Critical
**Type:** Security-Focused Microservice

A standalone authentication microservice. Other LaughTale services do not implement their own auth — they call this service or validate tokens it issues. Features: registration, login, token refresh, logout (token revocation), password reset flow.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Password | bcrypt, context managers | — |
| Tokens | JWT, dataclasses, decorators | — |
| Revocation | Redis-style set lookup | Hash table (O(1) revoked token check) |
| Rate Limiting | Decorators, sliding window | Sliding window algorithm |
| Storage | PostgreSQL, repositories | — |
| Security | Custom exceptions, middleware | — |

---

## 💼 Hiring Value

Security-focused engineering. Relevant to: **backend engineer**, **security engineer**, **platform engineer**. Knowing how auth actually works — not just "use Auth0" — is a differentiator in every backend interview.

---

## 🔍 Why These Choices

**Why a token blocklist instead of short expiry only?**
A 30-minute access token means a compromised token is valid for up to 30 minutes even after the user logs out. A blocklist (stored in Redis or PostgreSQL) allows immediate revocation. Logout is meaningless without revocation.

**Why store refresh tokens in the database?**
Refresh tokens are long-lived (7 days). If a user's device is stolen, they must be able to invalidate all their sessions. This requires a database record per refresh token. Access tokens (30 min) are short enough that a blocklist lookup overhead is acceptable.

**Why a sliding window rate limiter on auth endpoints?**
Fixed window rate limiting (5 requests per minute) can be gamed: send 5 requests at 0:59, then 5 more at 1:00. A sliding window considers the actual 60-second window behind each request. Harder to bypass.

**Why a separate microservice?**
All LaughTale apps share the same users. Centralising auth means: one place to fix a security bug, one place to add MFA, one consistent session experience. The alternative — auth re-implemented in every service — produces inconsistent security.

---

## 🏗️ Architecture

```
Client
  │
  ├──→ POST /auth/register        → hash password → store user
  ├──→ POST /auth/login           → verify password → issue tokens
  ├──→ POST /auth/refresh         → validate refresh token → issue new access token
  ├──→ POST /auth/logout          → revoke refresh token → add access token to blocklist
  └──→ POST /auth/verify          → validate access token → return user claims

Other LaughTale Services
  └──→ GET /auth/verify           → "is this token valid? who does it belong to?"
```

---

## 📋 Build Phases

### Phase 1: Database Schema

```sql
CREATE TABLE users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email            TEXT UNIQUE NOT NULL,
    password_hash    TEXT NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash       TEXT NOT NULL UNIQUE,   -- store hash of token, not raw token
    expires_at       TIMESTAMPTZ NOT NULL,
    revoked_at       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);

CREATE TABLE token_blocklist (
    jti              TEXT PRIMARY KEY,       -- JWT ID claim
    expires_at       TIMESTAMPTZ NOT NULL    -- for cleanup job
);
```

Why hash the refresh token? If the database is compromised, raw tokens cannot be used. The hash is useless without the original token.

### Phase 2: Password & Token Utilities

Implement in `utils/security.py`:
- `hash_password(plain: str) -> str` — bcrypt, rounds=12
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(user_id: str, jti: str) -> str` — includes `jti` (unique ID for blocklist)
- `create_refresh_token() -> tuple[str, str]` — returns (raw_token, hashed_token)
- `decode_access_token(token: str) -> dict` — raises `TokenExpiredError`, `TokenInvalidError`

### Phase 3: Rate Limiter (Sliding Window)

```python
class SlidingWindowRateLimiter:
    """
    Tracks request timestamps per key using a deque.
    Evicts timestamps outside the window on each check.
    O(1) amortised — each timestamp is added and removed exactly once.
    """
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, deque] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        timestamps = self._store[key]
        cutoff = now - self.window

        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()           # Evict expired timestamps

        if len(timestamps) >= self.max_requests:
            return False

        timestamps.append(now)
        return True
```

Apply `@rate_limit(limiter, key=get_ip)` decorator to `/auth/login` and `/auth/register`.

### Phase 4: Auth Endpoints

Each endpoint follows this exact order of operations (no exceptions):
1. Validate input schema (Pydantic — raises 422 if fails)
2. Check rate limit (raises 429 if exceeded)
3. Perform the operation
4. Return response

For `/auth/login`:
```
1. Validate LoginSchema (email + password present)
2. Rate limit by IP (5 attempts/minute)
3. Fetch user by email (constant-time comparison even if user doesn't exist)
4. Verify password (bcrypt.checkpw — takes ~250ms intentionally)
5. Check user is active
6. Create access token (with unique jti) + refresh token
7. Store hashed refresh token in DB
8. Return {access_token, refresh_token, expires_in}
```

Security note on step 3: if the user does not exist, still call `bcrypt.checkpw` with a dummy hash. Without this, an attacker can detect valid email addresses by timing the response (valid email takes 250ms for bcrypt; invalid email returns instantly).

### Phase 5: Token Revocation

For `/auth/logout`:
1. Extract `jti` from the access token
2. Add `jti` to `token_blocklist` table with `expires_at`
3. Mark refresh token as revoked
4. Return 204

For `/auth/verify` (called by other services):
1. Decode and validate the token signature
2. Check `jti` is NOT in `token_blocklist` (O(1) primary key lookup)
3. Return user claims

Add a nightly cleanup job: `DELETE FROM token_blocklist WHERE expires_at < NOW()`.

---

## 🚀 Deployment

Deploy as a standalone service behind a load balancer. All other LaughTale services call `/auth/verify` to validate tokens — they never implement their own token validation.

Set `SECRET_KEY` from a secret manager (AWS Secrets Manager, HashiCorp Vault, or Hetzner equivalent) — never from `.env` in production.

---

## 🔴 Extensions

- Email verification flow (generate signed token, email link, mark `is_verified = TRUE`)
- TOTP two-factor authentication (Google Authenticator compatible)
- OAuth2 social login (Google, GitHub)
- Device fingerprinting on suspicious login detection

---

# PROJECT 5 — Log Analyzer & Report Generator

## 🏢 LaughTale Brief

**Client:** Internal DevOps / SRE team
**Ticket:** LAUGH-005
**Priority:** Medium
**Type:** DevOps Tooling / Data Analysis

A CLI tool that ingests server log files, identifies error patterns, calculates request statistics, generates a human-readable HTML report, and optionally alerts on anomalies. Logs can be multiple gigabytes. Reports are generated in under 30 seconds.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Reading | Generators, file I/O, context managers | — |
| Parsing | Regex, dataclasses, str methods | — |
| Aggregation | Hash tables (`Counter`, `defaultdict`) | Hash tables for frequency |
| Ranking | Sorting, `heapq.nlargest` | Sorting O(n log n), heap O(n log k) |
| Reporting | Modules, string formatting, file I/O | — |
| Flags | Bit manipulation for log level flags | Bitmask |
| Memory | Generators, O(1) streaming | Space complexity |

---

## 💼 Hiring Value

Demonstrates: systems thinking, performance-conscious coding, log analysis (used daily by SRE/DevOps teams), report generation. Relevant to: **DevOps engineer**, **SRE**, **backend engineer**, **data analyst**.

---

## 🔍 Why These Choices

**Why generators for multi-gigabyte log files?**
Same reason as Project 3: O(1) memory. A 2GB log file loaded into a list crashes a server with 2GB RAM. A generator streams one line at a time.

**Why `Counter` for endpoint frequency?**
`Counter` is a hash table specialised for frequency counting. Inserting each URL into a Counter dict is O(1) per operation, O(n) total. Sorting 500k distinct URLs by frequency at the end is O(m log m) where m is the number of distinct URLs (much smaller than n). Total: O(n) + O(m log m).

**Why `heapq.nlargest(10, ...)` instead of sorting and slicing?**
`sorted()` on 500,000 entries is O(n log n). `heapq.nlargest(10, ...)` is O(n log k) where k=10 — it maintains only a 10-element heap while scanning. For finding the top 10 of 500,000, it's ~50x faster.

**Why bitmask for log level flags?**
Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) are often combined in filters: "show me WARNING and ERROR but not DEBUG". A bitmask lets you represent any combination in one integer, check membership in O(1) with `&`, and combine with `|`. The alternative — a set of strings — is more memory-heavy and slower.

---

## 🏗️ Architecture

```
Log File(s)
    │
    ▼ generator: one raw line at a time
parse_lines(filepath)
    │
    ▼ generator: structured LogEntry objects
filter_by_level(entries, level_mask)
    │
    ▼ aggregation pass
aggregate(entries) → Stats object
    │
    ▼
render_report(stats) → HTML file
    │
    ▼
check_anomalies(stats) → alerts list
```

---

## 📋 Build Phases

### Phase 1: Log Line Structure

Define a standard log format (or parse Nginx/Apache common log format):
```
[2025-07-13 08:23:45] INFO  GET /api/v1/users 200 142ms user_id=abc123
```

Create:
```python
LOG_LEVELS = {
    "DEBUG":    0b00001,   # 1
    "INFO":     0b00010,   # 2
    "WARNING":  0b00100,   # 4
    "ERROR":    0b01000,   # 8
    "CRITICAL": 0b10000,   # 16
}

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    method: str
    path: str
    status_code: int
    response_ms: int
    user_id: str | None
```

### Phase 2: Parsing Generator

```python
import re

LOG_PATTERN = re.compile(
    r'\[(?P<ts>.+?)\] (?P<level>\w+)\s+(?P<method>\w+) (?P<path>\S+) '
    r'(?P<status>\d+) (?P<ms>\d+)ms(?: user_id=(?P<uid>\S+))?'
)

def parse_lines(filepath: Path) -> Generator[LogEntry, None, None]:
    with open(filepath, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            m = LOG_PATTERN.match(line.strip())
            if not m:
                continue   # Skip malformed lines silently
            yield LogEntry(
                timestamp=datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S"),
                level=m.group("level"),
                method=m.group("method"),
                path=m.group("path"),
                status_code=int(m.group("status")),
                response_ms=int(m.group("ms")),
                user_id=m.group("uid")
            )
```

### Phase 3: Filter by Level (Bitmask)

```python
def filter_by_level(entries: Iterable[LogEntry], mask: int) -> Generator[LogEntry, None, None]:
    """
    mask = LOG_LEVELS["ERROR"] | LOG_LEVELS["CRITICAL"]  → only errors and criticals
    mask = 0b11111                                        → all levels
    """
    for entry in entries:
        level_bit = LOG_LEVELS.get(entry.level, 0)
        if level_bit & mask:   # O(1) membership check
            yield entry
```

### Phase 4: Aggregation (One Pass)

Process the entire log in a single pass, building all stats simultaneously:
```python
@dataclass
class Stats:
    total_requests: int = 0
    error_count: int = 0
    endpoint_counts: Counter = field(default_factory=Counter)
    status_counts: Counter = field(default_factory=Counter)
    slow_requests: list = field(default_factory=list)   # response_ms > 1000
    errors_by_path: defaultdict = field(default_factory=lambda: defaultdict(list))
    total_ms: int = 0

def aggregate(entries: Iterable[LogEntry]) -> Stats:
    stats = Stats()
    for entry in entries:               # One pass through the data
        stats.total_requests += 1
        stats.total_ms += entry.response_ms
        stats.endpoint_counts[entry.path] += 1
        stats.status_counts[entry.status_code] += 1
        if entry.status_code >= 400:
            stats.error_count += 1
            stats.errors_by_path[entry.path].append(entry)
        if entry.response_ms > 1000:
            stats.slow_requests.append(entry)
    return stats
```

### Phase 5: Report Generation

After aggregation:
```python
top_endpoints = heapq.nlargest(10, stats.endpoint_counts.items(), key=lambda x: x[1])
top_errors = heapq.nlargest(10, stats.errors_by_path.items(), key=lambda x: len(x[1]))
avg_response_ms = stats.total_ms / stats.total_requests if stats.total_requests else 0
error_rate = stats.error_count / stats.total_requests * 100 if stats.total_requests else 0
```

Generate an HTML report with: total requests, error rate, average response time, top 10 endpoints by volume, top 10 error-prone paths, slowest requests list.

### Phase 6: Anomaly Alerts

Define thresholds in config:
- Error rate > 5%: WARNING
- Error rate > 15%: CRITICAL
- Avg response time > 500ms: WARNING
- Any single endpoint with > 50% of all errors: CRITICAL

Print alerts to stdout and optionally POST to a webhook URL.

---

## 🚀 Deployment

```bash
# Install and run
pip install -e .
lt-logs analyze /var/log/nginx/access.log --level ERROR,CRITICAL --report ./report.html

# In CI/CD — analyze the previous day's logs
0 6 * * * lt-logs analyze /var/log/app/$(date -d yesterday +%Y-%m-%d).log \
          --report /reports/daily.html \
          --webhook $SLACK_WEBHOOK_URL
```

---

## 🔴 Extensions

- Real-time streaming mode: tail a log file and update stats incrementally
- Multi-file mode: analyze a directory of rotated log files
- Baseline comparison: compare today's stats with last week's same-day stats
- Geolocation: look up IP addresses to show request distribution by country

---

# PROJECT 6 — URL Shortener with LRU Cache

## 🏢 LaughTale Brief

**Client:** LaughTale marketing team — tracking link performance
**Ticket:** LAUGH-006
**Priority:** Medium
**Type:** REST API with in-memory caching

A URL shortening service. Users submit a long URL, receive a short code (`laughtale.co.za/s/x3k9p`). Visiting the short URL redirects to the original. The system tracks click counts. An in-memory LRU cache serves the hottest links without database reads.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Short code generation | `secrets` module, `base62` encoding | Hash functions |
| Cache | OOP, `__contains__`, `@property` | LRU Cache (doubly linked list + hash map) |
| Storage | PostgreSQL, repositories | Hash table O(1) lookup |
| API | FastAPI, async, redirects | — |
| Analytics | Async background tasks | — |

---

## 💼 Hiring Value

Demonstrates: system design thinking (caching strategy), O(1) data structures, URL shortening (a classic system design interview problem), background task processing. Relevant to: **backend engineer**, **platform engineer**, **fullstack developer**. URL shortener is one of the most common system design questions at FAANG-adjacent companies.

---

## 🔍 Why These Choices

**Why an LRU Cache?**
In a URL shortener, a small percentage of links get the vast majority of traffic (power law distribution — like TinyURL's top 100 links get 90% of all clicks). Serving these from memory avoids database reads. LRU (Least Recently Used) evicts the least popular links automatically as new ones enter.

**Why implement LRU with a doubly linked list + hash map instead of `functools.lru_cache`?**
`functools.lru_cache` is function-level and not inspectable. A custom implementation lets you: set capacity dynamically, expose cache statistics, manually invalidate entries, and understand exactly what is in memory. It also demonstrates the underlying data structure — which is the interview question.

**Why `secrets.token_urlsafe` for short codes instead of a counter?**
Sequential IDs (`/s/1`, `/s/2`, `/s/3`) let users enumerate all links and see what others have shortened. `secrets.token_urlsafe(6)` generates cryptographically random codes that cannot be guessed or enumerated.

**Why increment click counts in a background task, not synchronously?**
The redirect (`/s/x3k9p → 302 → original_url`) must be as fast as possible — ideally under 5ms. A database `UPDATE clicks = clicks + 1` adds 5-20ms. A FastAPI `BackgroundTask` returns the redirect immediately and updates the count asynchronously after the response is sent.

---

## 🏗️ Architecture

```
Client visits /s/x3k9p
       │
       ▼
FastAPI Route
       │
       ├──→ LRU Cache hit? → return 302 immediately (< 1ms)
       │
       └──→ Cache miss → DB lookup → add to cache → return 302
                                          │
                                          └──→ BackgroundTask: UPDATE click_count
```

---

## 📋 Build Phases

### Phase 1: LRU Cache Implementation

Build from scratch before using it in the API:

```python
class LRUNode:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value
        self.prev: LRUNode | None = None
        self.next: LRUNode | None = None

class LRUCache:
    """
    O(1) get and put using a doubly linked list + hash map.
    Most recently used = head. Least recently used = tail.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._map: dict[str, LRUNode] = {}
        self._head = LRUNode("", "")  # Dummy head
        self._tail = LRUNode("", "")  # Dummy tail
        self._head.next = self._tail
        self._tail.prev = self._head

    def get(self, key: str) -> str | None:
        if key not in self._map:
            return None
        node = self._map[key]
        self._move_to_front(node)   # O(1) — just pointer rewiring
        return node.value

    def put(self, key: str, value: str) -> None:
        if key in self._map:
            self._map[key].value = value
            self._move_to_front(self._map[key])
            return
        node = LRUNode(key, value)
        self._map[key] = node
        self._add_to_front(node)
        if len(self._map) > self.capacity:
            lru = self._tail.prev   # The least recently used
            self._remove(lru)
            del self._map[lru.key]
```

Test the cache independently: fill to capacity, access an old entry (moves to front), add a new entry (evicts LRU). Confirm O(1) operations with a timer.

### Phase 2: Database Schema

```sql
CREATE TABLE short_links (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    short_code   TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    click_count  BIGINT NOT NULL DEFAULT 0,
    created_by   UUID REFERENCES users(id),
    expires_at   TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_short_links_code ON short_links(short_code);   -- critical: redirect lookup
```

### Phase 3: Short Code Generation

```python
import secrets

def generate_short_code(length: int = 7) -> str:
    return secrets.token_urlsafe(length)[:length]

# Collision handling: generate → check DB → if exists, generate again
# Expected collision rate at 7 chars (base64 alphabet): negligible until ~1 billion links
```

### Phase 4: API Endpoints

```
POST /api/v1/links                → create short link → 201 {short_code, short_url}
GET  /s/{code}                    → redirect → 302 Location: original_url
GET  /api/v1/links/{code}/stats   → 200 {click_count, created_at, original_url}
DELETE /api/v1/links/{code}       → 204 (owner only)
```

The `/s/{code}` endpoint is the hottest path. Its implementation:
1. Check LRU cache (O(1))
2. If miss: DB lookup, insert into cache
3. Queue background task to increment click count
4. Return `RedirectResponse(url=original_url, status_code=302)`

---

## 🚀 Deployment

The LRU cache is in-process memory. With multiple API workers, each worker has its own cache (they don't share). Acceptable for this scale. At higher scale, replace with Redis (same LRU semantics, shared across workers).

---

## 🔴 Extensions

- Custom short codes (`/s/my-brand-name`)
- QR code generation on creation
- Geographic analytics (country of click)
- Link expiry with automatic deactivation
- Distributed cache with Redis replacing the in-memory LRU

---

# PROJECT 7 — Async Job Queue Worker

## 🏢 LaughTale Brief

**Client:** LaughTale platform infrastructure
**Ticket:** LAUGH-007
**Priority:** High
**Type:** Backend Systems / Platform Engineering

A background job processing system. API endpoints queue jobs (send email, generate PDF, process image, call external API) and return immediately without waiting for the job to finish. Worker processes pick up jobs from the queue and execute them asynchronously. Failed jobs retry with exponential backoff.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Queue | asyncio.Queue, deque | Queue (FIFO), Priority Queue |
| Workers | async/await, asyncio.gather, Semaphore | — |
| Retry Logic | Decorators, exponential backoff | — |
| Priority | heapq, tuples | Min-heap for priority queue |
| Context Managers | Resource cleanup | — |
| Generators | Async generators for job streaming | — |
| Multiprocessing | ProcessPoolExecutor for CPU-bound jobs | — |

---

## 💼 Hiring Value

Background job queues are used in every production web application. Understanding async workers, retry strategies, and backoff separates junior from senior engineers. Relevant to: **backend engineer**, **platform engineer**, **SRE**. Used at every scale-up and enterprise company.

---

## 🔍 Why These Choices

**Why async workers, not threads?**
Most jobs are I/O-bound (sending HTTP requests, calling APIs, reading/writing files). Async workers use a single thread but process hundreds of jobs concurrently. Thread-per-job would exhaust OS thread limits at ~1000 concurrent jobs. Async workers handle 10,000+ concurrently.

**Why exponential backoff on retries?**
If an external API is overloaded and you immediately retry 1000 jobs, you make the overload worse. Exponential backoff (`1s, 2s, 4s, 8s, 16s`) spreads the load and gives the API time to recover. Most production systems add jitter (`random.uniform(0, backoff)`) to prevent all retried jobs from hitting at the same moment.

**Why a priority queue (min-heap) for job scheduling?**
Not all jobs are equal. A payment confirmation email is more urgent than a weekly digest. A min-heap allows O(log n) insert of new jobs and O(log n) extraction of the highest-priority job. A FIFO queue treats all jobs equally.

---

## 🏗️ Architecture

```
API Server                   Worker Process
    │                             │
    ├── POST /jobs  ──────────────► asyncio.Queue
    │                             │
    │                         ┌───┴────────┐
    │                    Worker Worker Worker  ← asyncio.Semaphore(max_concurrent)
    │                         └───┬────────┘
    │                             │
    │                        Job execution
    │                             │
    │                     Success → mark done
    │                     Failure → retry with backoff
    │                     Max retries → dead letter queue
    │
    └── GET /jobs/{id}  ← poll for result
```

---

## 📋 Build Phases

### Phase 1: Job Data Model

```python
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

class JobStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    DONE      = "done"
    FAILED    = "failed"
    DEAD      = "dead"      # Max retries exceeded

class JobPriority(int, Enum):
    CRITICAL = 1
    HIGH     = 2
    NORMAL   = 3
    LOW      = 4

@dataclass
class Job:
    type: str                            # "send_email", "generate_pdf", etc.
    payload: dict
    priority: JobPriority = JobPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    created_at: float = field(default_factory=time.monotonic)
    next_attempt_at: float = field(default_factory=time.monotonic)

    def __lt__(self, other):             # For heap comparison
        return (self.priority, self.created_at) < (other.priority, other.created_at)
```

### Phase 2: Worker Registry (Decorator Pattern)

```python
class JobRegistry:
    """Maps job type strings to handler coroutines."""
    _handlers: dict[str, Coroutine] = {}

    @classmethod
    def register(cls, job_type: str):
        """Decorator that registers an async handler for a job type."""
        def decorator(func):
            cls._handlers[job_type] = func
            return func
        return decorator

    @classmethod
    async def execute(cls, job: Job) -> any:
        handler = cls._handlers.get(job.type)
        if not handler:
            raise ValueError(f"No handler registered for job type: {job.type}")
        return await handler(job.payload)

# Usage
@JobRegistry.register("send_email")
async def handle_send_email(payload: dict):
    await send_smtp_email(payload["to"], payload["subject"], payload["body"])
```

### Phase 3: Exponential Backoff Decorator

```python
import asyncio, random

def async_retry(max_attempts: int = 3, base_delay: float = 1.0, jitter: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        if jitter:
                            delay *= random.uniform(0.5, 1.5)
                        await asyncio.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
```

### Phase 4: Worker Pool

```python
class WorkerPool:
    def __init__(self, queue: asyncio.PriorityQueue, num_workers: int = 5):
        self.queue = queue
        self.semaphore = asyncio.Semaphore(num_workers)
        self.running = True

    async def start(self):
        workers = [self._worker(i) for i in range(10)]   # 10 concurrent workers
        await asyncio.gather(*workers)

    async def _worker(self, worker_id: int):
        while self.running:
            _, job = await self.queue.get()     # Blocks until a job is available
            async with self.semaphore:          # Limits true concurrency
                await self._process(job)
            self.queue.task_done()

    async def _process(self, job: Job):
        job.status = JobStatus.RUNNING
        job.attempts += 1
        try:
            await JobRegistry.execute(job)
            job.status = JobStatus.DONE
        except Exception as e:
            if job.attempts >= job.max_attempts:
                job.status = JobStatus.DEAD     # Dead letter queue
            else:
                job.status = JobStatus.PENDING
                job.next_attempt_at = time.monotonic() + (2 ** job.attempts)
                await self.queue.put((job.priority, job))
```

### Phase 5: Scheduler for Delayed Jobs

A background coroutine that re-enqueues jobs whose `next_attempt_at` has passed:
```python
async def retry_scheduler(pending_jobs: list[Job], queue: asyncio.PriorityQueue):
    while True:
        now = time.monotonic()
        for job in [j for j in pending_jobs if j.next_attempt_at <= now]:
            await queue.put((job.priority, job))
            pending_jobs.remove(job)
        await asyncio.sleep(0.5)   # Check every 500ms
```

---

## 🚀 Deployment

Run the worker pool as a separate process from the API:
```bash
# docker-compose.yml
services:
  api:
    command: uvicorn app.main:app
  worker:
    command: python -m app.worker     # Runs WorkerPool
```

Workers are stateless — scale horizontally by adding more worker containers. The queue (Redis in production, asyncio.Queue in development) is shared between all workers.

---

## 🔴 Extensions

- Persist job state to PostgreSQL (survive worker restart)
- Web dashboard showing job status, counts, failure rates
- Job chaining: job B runs only when job A completes
- CPU-bound jobs in a `ProcessPoolExecutor` to bypass the GIL
- Dead letter queue review UI

---

# PROJECT 8 — Full-Text Search API

## 🏢 LaughTale Brief

**Client:** LaughTale content platform — search across articles, products, documentation
**Ticket:** LAUGH-008
**Priority:** High
**Type:** Search Engine / REST API

A search API that indexes documents and returns ranked results for free-text queries. No external search engine (no Elasticsearch, no Algolia). The core data structure is an inverted index built from scratch. Results are ranked by TF-IDF score. The API must return results under 50ms for a corpus of 100,000 documents.

---

## 🗺️ Concept Map

| Layer | Python Concepts | DSA Concepts |
|---|---|---|
| Indexing | Generators, modules, OOP | Inverted index (hash map of lists) |
| Tokenization | Regex, string methods, generators | — |
| Ranking | Sorting, `heapq` | TF-IDF, Big O analysis |
| Storage | JSON / PostgreSQL | Hash tables |
| API | FastAPI, async | — |
| Performance | `@lru_cache`, decorators | Time complexity per query |
| Testing | pytest, test corpus | — |

---

## 💼 Hiring Value

Demonstrates: algorithmic thinking, data structure design, performance reasoning, information retrieval concepts. Relevant to: **backend engineer**, **data engineer**, **software engineer at any scale-up**. Building search from scratch (even simplified) is a strong portfolio differentiator.

---

## 🔍 Why These Choices

**Why an inverted index instead of scanning documents?**
Scanning every document for each query: O(n × m) where n = documents, m = query length. With 100,000 documents averaging 500 words, that's 50 million comparisons per query. An inverted index maps each word to the list of documents containing it. Query time: O(k) where k = documents containing query terms — typically a tiny fraction of the corpus.

**Why TF-IDF for ranking?**
Raw frequency (count) is misleading: "the" appears in every document but means nothing. TF-IDF (Term Frequency × Inverse Document Frequency) gives high scores to terms that appear frequently in a document but rarely across the corpus. "PostgreSQL" appearing 10 times in a document is meaningful. "the" appearing 100 times is not.

**Why `heapq.nlargest` instead of `sorted`?**
A query may match 50,000 documents. We only need the top 10. `sorted()` on 50,000 floats is O(50,000 log 50,000). `heapq.nlargest(10, ...)` is O(50,000 log 10). For large corpora, this is the difference between 50ms and 5ms.

**Why `@lru_cache` on tokenization?**
The same words appear in thousands of documents. Tokenizing "PostgreSQL" once and caching the result avoids redundant string operations. `@lru_cache` is O(1) lookup after the first call.

---

## 🏗️ Architecture

```
Documents
    │
    ▼ Indexer
tokenize → normalize → build inverted index
    │
    ▼
{
  "postgresql": {"doc_1": 5, "doc_23": 2, "doc_101": 8},
  "python":     {"doc_1": 3, "doc_45": 1},
  ...
}
    │
    ▼ Query Engine
    │
    ├── tokenize query
    ├── lookup each term in inverted index → candidate doc sets
    ├── intersect/union candidate sets
    ├── score each candidate with TF-IDF
    └── heapq.nlargest(10, scored_docs) → ranked results
    │
    ▼ FastAPI
GET /search?q=python+postgresql&limit=10 → [{doc_id, title, score, snippet}]
```

---

## 📋 Build Phases

### Phase 1: Tokenizer

```python
import re
from functools import lru_cache

STOPWORDS = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "for", "of", "and", "or"}

@lru_cache(maxsize=10_000)
def tokenize(text: str) -> tuple[str, ...]:
    """
    Lowercase, strip punctuation, split on whitespace, remove stopwords.
    Returns a tuple (hashable, so lru_cache works).
    """
    words = re.findall(r'[a-z0-9]+', text.lower())
    return tuple(w for w in words if w not in STOPWORDS and len(w) > 1)
```

### Phase 2: Inverted Index Builder

```python
from collections import defaultdict
import math

class InvertedIndex:
    def __init__(self):
        # {term: {doc_id: term_frequency}}
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._doc_lengths: dict[str, int] = {}   # total terms per document
        self._doc_count: int = 0

    def add_document(self, doc_id: str, content: str) -> None:
        tokens = tokenize(content)
        self._doc_lengths[doc_id] = len(tokens)
        self._doc_count += 1
        for token in tokens:
            self._index[token][doc_id] += 1

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        # Candidate docs: union of all docs containing any query term
        candidate_scores: dict[str, float] = defaultdict(float)

        for term in query_terms:
            if term not in self._index:
                continue
            postings = self._index[term]
            # IDF: how rare is this term across all documents?
            idf = math.log((self._doc_count + 1) / (len(postings) + 1))

            for doc_id, tf in postings.items():
                # TF: normalize by document length
                normalized_tf = tf / self._doc_lengths[doc_id]
                candidate_scores[doc_id] += normalized_tf * idf

        # Return top_k by score — O(n log k), not O(n log n)
        return heapq.nlargest(top_k, candidate_scores.items(), key=lambda x: x[1])
```

### Phase 3: Document Store

Separate from the index: store the original documents for snippet generation:
```python
@dataclass
class Document:
    id: str
    title: str
    content: str
    url: str | None = None
    metadata: dict = field(default_factory=dict)
```

The document store is a plain dict `{doc_id: Document}`. After scoring, fetch documents by ID for the response — O(1) per document.

### Phase 4: Snippet Generation

For each result, extract the sentence most relevant to the query:
```python
def generate_snippet(content: str, query_terms: tuple, snippet_length: int = 200) -> str:
    sentences = content.split('.')
    # Score each sentence by how many query terms it contains
    best = max(sentences, key=lambda s: sum(t in s.lower() for t in query_terms), default="")
    return best.strip()[:snippet_length] + "..."
```

### Phase 5: FastAPI Search Endpoint

```python
@router.get("/search")
async def search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    start = time.perf_counter()
    results = index.search(q, top_k=limit)

    response_items = []
    for doc_id, score in results:
        doc = document_store[doc_id]
        response_items.append({
            "id": doc_id,
            "title": doc.title,
            "score": round(score, 4),
            "snippet": generate_snippet(doc.content, tokenize(q)),
            "url": doc.url
        })

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "data": response_items,
        "meta": {
            "query": q,
            "total_results": len(results),
            "search_time_ms": round(elapsed_ms, 2)
        }
    }
```

### Phase 6: Index Persistence + Rebuild

Save the index to disk on shutdown; load on startup. Use Python's `pickle` or serialize to JSON. On startup: load persisted index or rebuild from database if no index file exists. Rebuild runs in a background thread to not block the API from starting.

---

## 🚀 Deployment

The index lives in memory. For a corpus of 100,000 documents × average 500 unique terms: estimate ~50MB RAM. Well within a CX11 (2GB) Hetzner instance. At 1M+ documents, move to a dedicated search service (Meilisearch or Elasticsearch).

```
Startup sequence:
1. Load document store from PostgreSQL
2. Load persisted index from disk (or rebuild if missing)
3. Start FastAPI API workers
4. Re-index new/updated documents every 5 minutes (background task)
```

---

## 🔴 Extensions

- Phrase search: `"postgresql performance"` matches exact phrase
- Boolean operators: `python AND postgresql NOT django`
- Fuzzy matching: match "postgre" → "postgresql" using edit distance
- Autocomplete: prefix trie for query suggestions
- Multi-language tokenization and stemming

---

# APPENDIX — Project Comparison Table

| # | Project | Domain | Key Data Structure | Key Python Concept | Interview Relevance |
|---|---|---|---|---|---|
| 1 | CLI Task Manager | Tooling | — | OOP, File I/O, CMs | Any Python role |
| 2 | Inventory REST API | Backend | Hash map (connection pool) | Async, FastAPI, Auth | Backend developer |
| 3 | CSV ETL Pipeline | Data Engineering | Generator pipeline | Generators, CMs | Data engineer |
| 4 | Auth Service | Security | Hash table (blocklist) | Decorators, bcrypt, JWT | Security/backend |
| 5 | Log Analyzer | DevOps/SRE | Counter, heap (top-k) | Generators, regex | DevOps, SRE |
| 6 | URL Shortener | Platform | LRU (DLL + hash map) | OOP, async BG tasks | System design |
| 7 | Job Queue Worker | Platform/Backend | Priority queue (heap) | asyncio, decorators | Platform engineer |
| 8 | Search API | Backend/Data | Inverted index | Generators, lru_cache | Any engineering role |

---

*All projects reference the LaughTale Engineering Handbook for standards on security, database, API design, and deployment.*

*LaughTale Applied Engineering | laughtale.co.za*

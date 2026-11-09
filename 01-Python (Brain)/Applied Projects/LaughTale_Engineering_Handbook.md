# LaughTale Engineering Handbook
## Internal Development Standards & Practices
### Version 1.0 | KwaZulu-Natal, South Africa

---

> **Purpose:** This document defines how LaughTale engineers plan, build, secure, and deploy software. It is the single source of truth for every developer, DBA, security engineer, and deployment engineer on any LaughTale project. Read it once. Reference it always.

---

# PART 1 — PROJECT PLANNING

## 1.1 The Four Phases Before Writing Code

Every LaughTale project — no matter how small — goes through four planning phases before a single line of application code is written. Skipping any phase creates technical debt that costs five times more to fix later.

**Phase 1: Discovery**
Define the problem in plain language. No technical terms yet.
- Who is the user?
- What pain does this solve?
- What is explicitly OUT of scope for this version?
- Write it as a single paragraph. If you cannot, the scope is not clear enough.

**Phase 2: Requirements**
Convert the discovery paragraph into numbered, testable requirements.

```
FUNCTIONAL REQUIREMENTS
FR-01  A user can create an account with email and password.
FR-02  A user can log in and receive a session token.
FR-03  A logged-in user can create, read, update, delete their own records.

NON-FUNCTIONAL REQUIREMENTS
NFR-01  API response time under 200ms for 95% of requests.
NFR-02  Passwords must never be stored in plain text.
NFR-03  All endpoints must require authentication except /auth/register and /auth/login.
```

Every requirement gets a code (FR-01, NFR-02). When a bug is filed, it references a requirement. When a feature is scoped out, it gets a future FR code. Nothing is ambiguous.

**Phase 3: Architecture Decision Record (ADR)**
For every major technical choice, document it in one paragraph using this format:

```
ADR-001: Use PostgreSQL, not SQLite

Context: We need a persistent database that handles concurrent writes from multiple API workers.
Decision: PostgreSQL via psycopg2/asyncpg. SQLite does not support concurrent writes safely.
Consequences: Requires a running Postgres instance in all environments. More setup than SQLite but correct for production workloads.
```

ADRs prevent the question "why did we do it this way?" six months later when the original engineer is gone.

**Phase 4: Design**
Three artefacts produced before coding begins:
- **ERD** (Entity Relationship Diagram) — what data exists and how it relates
- **API Contract** — every endpoint: method, URL, request body, response body, status codes
- **Folder Structure** — the agreed file/module layout for the project

---

## 1.2 Standard Folder Structure

All LaughTale Python backend projects follow this layout:

```
project_name/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point (FastAPI app, CLI entry, etc.)
│   ├── config.py            # Settings loaded from environment variables
│   ├── models/              # Database models / dataclasses
│   │   └── __init__.py
│   ├── schemas/             # Pydantic schemas (request/response validation)
│   │   └── __init__.py
│   ├── services/            # Business logic (no DB calls, no HTTP)
│   │   └── __init__.py
│   ├── repositories/        # All database interactions live here only
│   │   └── __init__.py
│   ├── routers/             # FastAPI routers / CLI command groups
│   │   └── __init__.py
│   └── utils/               # Shared utilities (hashing, tokens, formatting)
│       └── __init__.py
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/              # Alembic migration files
├── .env                     # Local dev secrets (NEVER committed)
├── .env.example             # Template with fake values (ALWAYS committed)
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

**Why this structure:**
- `services/` contain zero database code. This means you can test all business logic without a running database.
- `repositories/` are the only place SQL is written. Security audits check one folder.
- `schemas/` validate ALL input before it reaches any service or database layer.

---

# PART 2 — DATABASE MANAGEMENT

## 2.1 PostgreSQL Naming Conventions

LaughTale uses PostgreSQL for all relational data. These conventions are non-negotiable.

| Object | Convention | Example |
|---|---|---|
| Table name | `snake_case`, plural | `user_accounts`, `invoice_items` |
| Column name | `snake_case` | `created_at`, `first_name` |
| Primary key | `id` (UUID preferred) | `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` |
| Foreign key | `{table_singular}_id` | `user_id`, `invoice_id` |
| Boolean column | starts with `is_` or `has_` | `is_active`, `has_verified_email` |
| Timestamp columns | always present | `created_at`, `updated_at` |
| Index name | `idx_{table}_{column}` | `idx_users_email` |

**Every table gets these columns:**
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Never use auto-increment integers as primary keys in production systems. UUIDs prevent enumeration attacks (an attacker cannot guess `/users/5` then `/users/6`).

## 2.2 Schema Design Principles

**Normalise to 3NF by default.** Denormalise only when a specific query has been profiled and proven to be a bottleneck. Never denormalise speculatively.

**Constraint everything at the database level:**
```sql
-- Bad: trusting the application to enforce these
INSERT INTO users (email, age) VALUES ('hello', -5);

-- Good: database rejects invalid data regardless of what the app does
CREATE TABLE users (
    email  TEXT NOT NULL UNIQUE CHECK (email LIKE '%@%'),
    age    INT  CHECK (age >= 0 AND age <= 150)
);
```

The database is the last line of defence. Applications have bugs. Constraints do not.

**Soft deletes over hard deletes:**
```sql
-- Instead of DELETE FROM users WHERE id = $1
-- Add is_deleted and deleted_at columns
UPDATE users SET is_deleted = TRUE, deleted_at = NOW() WHERE id = $1;
```
Soft deletes preserve audit trails, enable recovery, and prevent foreign key violations.

## 2.3 Indexing Strategy

Indexes speed up reads and slow down writes. Every index is a trade-off.

**Always index:**
- Primary keys (automatic)
- Foreign keys (not automatic in PostgreSQL — add manually)
- Columns used in `WHERE` clauses for high-traffic queries
- Columns used in `JOIN` conditions
- Columns used in `ORDER BY` on large tables

```sql
-- Foreign key index (PostgreSQL does NOT create these automatically)
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite index for a common combined query
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- This serves: WHERE user_id = $1 AND status = 'pending'
-- Also serves: WHERE user_id = $1 (leftmost prefix rule)
-- Does NOT serve: WHERE status = 'pending' alone
```

**Never index blindly.** Run `EXPLAIN ANALYZE` on slow queries. Index what the query plan says is doing sequential scans on large tables.

## 2.4 Migrations with Alembic

Never modify a production database manually. Every schema change is a versioned migration file.

```
# Workflow
alembic revision --autogenerate -m "add_is_active_to_users"
# Review the generated file in migrations/versions/
alembic upgrade head    # Apply
alembic downgrade -1    # Rollback one step
```

Migration rules:
- Every PR that changes a model has a corresponding migration file.
- Migrations are always forward-compatible (add columns as nullable first; populate; add constraint in a later migration).
- Never delete a migration file. Never edit a committed migration file.

## 2.5 Query Patterns to Avoid

**N+1 Query Problem:**
```python
# BAD: 1 query to get users + N queries to get their orders
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")  # N queries

# GOOD: 1 query with a JOIN
rows = db.query("""
    SELECT u.*, o.id as order_id, o.total
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
""")
```

**String-formatted SQL (SQL injection vector):**
```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ALWAYS USE PARAMETERIZED QUERIES
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_input,))
```

---

# PART 3 — SECURITY

## 3.1 The Security Mindset

Every input is hostile until proven otherwise. Every endpoint is public until explicitly protected. Every secret is compromised if it appears in code.

## 3.2 Environment Variables

Secrets never appear in source code. Ever.

```python
# .env (never committed to git)
DATABASE_URL=postgresql://user:password@localhost/mydb
SECRET_KEY=a_long_random_string_generated_with_secrets_module
DEBUG=False

# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

```
# .gitignore — these lines are mandatory
.env
*.env
.env.*
!.env.example
```

Generate secret keys with: `python -c "import secrets; print(secrets.token_hex(32))"`

## 3.3 Password Security

```python
# NEVER store passwords as plain text or with MD5/SHA1
# ALWAYS use bcrypt or argon2

import bcrypt

def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=12)   # Cost factor 12: ~250ms per hash (intentionally slow)
    return bcrypt.hashpw(plain.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# Why rounds=12? Slow hashing means brute-force attacks are 250ms per attempt
# instead of microseconds per attempt. This is the entire point.
```

## 3.4 JWT Authentication

```python
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
```

JWT rules at LaughTale:
- Access tokens expire in 30 minutes. Refresh tokens expire in 7 days.
- Store refresh tokens in the database so they can be revoked.
- Never store tokens in `localStorage` in browsers (use `httpOnly` cookies).
- Always validate the `type` claim to prevent refresh tokens being used as access tokens.

## 3.5 Input Validation

All input is validated at the schema layer before reaching services or the database.

```python
# Pydantic schema — validation happens automatically on request parsing
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr                    # Validates email format
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_clean(cls, v):
        return v.strip()[:100]         # Strip whitespace, cap at 100 chars
```

## 3.6 OWASP Top 10 — LaughTale Checklist

| Risk | LaughTale Control |
|---|---|
| A01 Broken Access Control | Every endpoint checks `current_user.id` matches resource owner |
| A02 Cryptographic Failures | bcrypt for passwords, HTTPS everywhere in production |
| A03 Injection | Parameterized queries only, Pydantic validation on all input |
| A04 Insecure Design | ADRs, threat modelling before coding |
| A05 Security Misconfiguration | Secrets in env vars, `DEBUG=False` in production |
| A06 Vulnerable Components | `pip audit` in CI pipeline, `dependabot` on GitHub |
| A07 Auth Failures | JWT with expiry, bcrypt cost factor ≥12, rate-limit `/auth/*` |
| A08 Data Integrity | Verify all webhook signatures, signed migration files |
| A09 Logging Failures | Structured logs in production, never log passwords/tokens |
| A10 SSRF | Allowlist external URLs, never fetch user-provided URLs directly |

## 3.7 Rate Limiting

Every public endpoint — especially authentication — must be rate-limited.

```python
# FastAPI with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")           # 5 login attempts per minute per IP
async def login(request: Request, credentials: LoginSchema):
    ...
```

Why: Without rate limiting, an attacker can try millions of passwords per minute against login endpoints. Five attempts per minute makes brute force infeasible.

---

# PART 4 — API DESIGN

## 4.1 REST Conventions

| Action | Method | URL | Status on success |
|---|---|---|---|
| List resources | GET | `/api/v1/users` | 200 |
| Get one resource | GET | `/api/v1/users/{id}` | 200 |
| Create resource | POST | `/api/v1/users` | 201 |
| Full update | PUT | `/api/v1/users/{id}` | 200 |
| Partial update | PATCH | `/api/v1/users/{id}` | 200 |
| Delete resource | DELETE | `/api/v1/users/{id}` | 204 |

Rules:
- URLs use nouns, never verbs. `/users`, not `/getUser` or `/createUser`.
- URLs are lowercase with hyphens for multi-word resources: `/invoice-items`, not `/invoiceItems`.
- Always version: `/api/v1/`. When breaking changes are needed, add `/api/v2/` — never modify v1.
- Nested resources for clear ownership: `/api/v1/users/{id}/orders`.

## 4.2 Standard Error Response Format

Every error from every LaughTale API returns this exact shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "issue": "Invalid email format"},
      {"field": "password", "issue": "Must be at least 8 characters"}
    ],
    "request_id": "req_7f3a9b2c"
  }
}
```

Never return raw exception messages to clients. They expose implementation details and create security risks. Map all exceptions to this format in a global exception handler.

## 4.3 Pagination

All list endpoints that could return more than 50 items must paginate.

```python
# Cursor-based pagination (preferred for large datasets — stable under concurrent writes)
GET /api/v1/orders?cursor=eyJpZCI6MTIzfQ==&limit=20

# Response
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ==",
    "has_more": true,
    "limit": 20
  }
}
```

Why cursor-based over page-based: page-based pagination (`?page=5&per_page=20`) breaks when records are inserted or deleted between requests. Cursor-based pagination is stable.

## 4.4 Response Envelope

Every successful response uses this envelope:

```json
{
  "data": { ... },           
  "meta": {                  
    "request_id": "req_abc123",
    "timestamp": "2025-07-13T08:00:00Z"
  }
}
```

This consistent wrapper lets frontend clients and downstream services handle responses uniformly.

---

# PART 5 — DEVELOPMENT WORKFLOW

## 5.1 Git Branching Strategy

```
main          ← production-ready code only, protected branch
  └── dev     ← integration branch, always deployable to staging
        ├── feature/FR-01-user-auth
        ├── feature/FR-02-invoice-crud
        └── fix/NFR-03-missing-auth-on-delete
```

Rules:
- **Never commit directly to `main` or `dev`**. Every change comes through a PR.
- Branch names reference requirement codes: `feature/FR-01-user-auth`.
- Delete branches after merging.
- `main` is deployed to production. `dev` is deployed to staging. PRs go to `dev`. Releases merge `dev` into `main`.

## 5.2 Commit Message Format (Conventional Commits)

```
type(scope): short description in present tense

feat(auth): add JWT refresh token endpoint
fix(users): prevent duplicate email registration
docs(readme): add local setup instructions
test(auth): add integration tests for login flow
chore(deps): upgrade fastapi to 0.111.0
refactor(orders): extract order calculation to service layer
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `security`.

Why: conventional commits enable automatic changelog generation, semantic versioning, and make `git log` readable by humans.

## 5.3 Pull Request Checklist

Before requesting review, every PR author confirms:

```
CODE
[ ] Tests written and passing (unit + integration where applicable)
[ ] No commented-out code
[ ] No print() or console.log() debug statements
[ ] All functions have docstrings
[ ] Type hints on all function signatures
[ ] No hardcoded secrets, URLs, or magic numbers

SECURITY
[ ] All new endpoints require authentication (or explicitly documented as public)
[ ] All new input uses Pydantic validation
[ ] No raw string SQL queries
[ ] No new dependencies without security review

DATABASE
[ ] Migration file included if models changed
[ ] Migration tested with upgrade and downgrade
[ ] New indexes added for new foreign keys

DOCUMENTATION
[ ] README updated if setup steps changed
[ ] ADR added if architectural decision was made
```

## 5.4 Testing Standards

```
tests/
├── unit/           # Test one function/class in isolation (no DB, no network)
│   └── test_auth_service.py
└── integration/    # Test the full request-response cycle with a real test DB
    └── test_auth_routes.py
```

Coverage targets: 80% minimum for services, 100% for security-critical paths (auth, payments).

```python
# Unit test pattern — mock the repository, test the service
def test_hash_password_is_not_plaintext():
    hashed = hash_password("mysecretpassword")
    assert hashed != "mysecretpassword"
    assert verify_password("mysecretpassword", hashed) is True

# Integration test pattern — real DB, test client
def test_login_returns_token(test_client, test_db):
    response = test_client.post("/api/v1/auth/login", json={
        "email": "test@example.com", "password": "correctpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
```

---

# PART 6 — DEPLOYMENT

## 6.1 Environment Hierarchy

```
local       → developer's machine, .env with local DB
dev         → auto-deployed on push to `dev` branch, staging DB
staging     → manual deploy, mirrors production exactly
production  → manual deploy, approved by lead, from `main` branch only
```

Each environment has its own `.env` file. Database credentials are different in every environment. The production DB is never accessible from dev or staging.

## 6.2 Dockerfile Standard

```dockerfile
# Use a specific version — never 'latest' in production
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies first (Docker layer cache: only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code after (so code changes don't invalidate the pip cache)
COPY app/ ./app/

# Run as non-root user (security best practice)
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 6.3 docker-compose for Local Development

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb
    volumes:
      - ./app:/app/app          # Hot reload in development
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## 6.4 Health Check Endpoint

Every deployed application must expose a health check endpoint:

```python
@app.get("/health", include_in_schema=False)
async def health():
    # Check DB connectivity
    try:
        await db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": settings.app_version,
        "database": db_status
    }
```

Used by Docker, load balancers, and uptime monitors to detect failed deployments.

## 6.5 Structured Logging

```python
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "request_id": getattr(record, "request_id", None)
        })

# Usage — never log sensitive data
logger.info("User login successful", extra={"user_id": user.id})
# NOT: logger.info(f"User {user.email} logged in with password {password}")
```

Log levels:
- `DEBUG`: local development only, never in production
- `INFO`: normal operations (login, record created)
- `WARNING`: unexpected but handled (rate limit hit, deprecated endpoint called)
- `ERROR`: something failed but the app is still running
- `CRITICAL`: the app may be down

## 6.6 GitHub Actions CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [dev]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 5s

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pip audit                        # Security: check for known vulnerabilities
      - run: ruff check app/                  # Linting
      - run: pytest tests/ --cov=app --cov-report=xml
      - run: alembic upgrade head             # Confirm migrations apply cleanly
```

---

# QUICK REFERENCE TABLES

## HTTP Status Codes Used at LaughTale

| Code | Meaning | When to use |
|---|---|---|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST that created a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation failure, malformed JSON |
| 401 | Unauthorised | No token, or token invalid/expired |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate (email already registered) |
| 422 | Unprocessable Entity | Pydantic validation error (FastAPI default) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unhandled exception — should never reach users |

## Python Version and Tool Stack

| Tool | Purpose | Version |
|---|---|---|
| Python | Language | 3.12+ |
| FastAPI | Web framework | Latest |
| Pydantic v2 | Validation / settings | Latest |
| SQLAlchemy | ORM (optional) | 2.x |
| psycopg2 / asyncpg | PostgreSQL driver | Latest |
| Alembic | Migrations | Latest |
| bcrypt | Password hashing | Latest |
| PyJWT | JWT tokens | Latest |
| pytest | Testing | Latest |
| ruff | Linting + formatting | Latest |
| uvicorn | ASGI server | Latest |

## PostgreSQL Data Type Decisions

| Data | Type | Why |
|---|---|---|
| Primary key | `UUID` | Not guessable, no enumeration risk |
| Short text (<255 chars) | `VARCHAR(n)` | Enforced length at DB level |
| Long text | `TEXT` | No length restriction needed |
| Money / prices | `NUMERIC(10,2)` | Never use FLOAT for money (rounding errors) |
| Timestamps | `TIMESTAMPTZ` | Always store with timezone (UTC) |
| True/False | `BOOLEAN` | Not INT 0/1 |
| JSON data | `JSONB` | Binary JSON, indexable, queryable |
| Enumerated values | `TEXT` + `CHECK` constraint | Or PostgreSQL `ENUM` type |

---

*This handbook is a living document. When a decision is made that changes a standard, update this document in the same PR as the code change. The handbook is always current with production.*

*LaughTale Engineering | laughtale.co.za*

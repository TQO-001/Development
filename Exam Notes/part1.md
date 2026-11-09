# Practical EISA — API & Code Manual (Expanded)

**Python · FastAPI · Node.js · Express · SQL · Testing · Security**

QCTO Occupational Certificate: Software Engineer · SAQA ID 119458 · NQF Level 6

## Using this manual

This is an open-book reference for the practical examination. It assumes you understand software engineering concepts but need to *recall syntax and assemble the pieces quickly*. Find a topic in the contents, copy the snippet, adapt names and fields. **Follow the exact stack, filenames and instructions given in the exam; this manual covers both Python/FastAPI and Node.js/Express because either may be allowed.**

| Label in the text | Meaning |
|---|---|
| **File:** `path` | Save the next code block under this name. Files with the same project prefix belong together. |
| *Standalone* | The snippet runs on its own (given the install line shown). |
| *Depends on* | The snippet needs files from an earlier section; the dependency is named. |
| `output` blocks | Real output captured by running the snippet above it (any dates shown are the day it was run). |
| **Exam tip** / **Common mistake** / **Warning** / **Note** | Shaded call-outs. Read the Warnings; they save marks and time. |

**Two reference projects implement the same Library API** (same tables, same endpoints, same status codes), so you can switch stacks without redesigning: `library_fastapi/` (Python, §4) and `library-api/` (Node.js + Express, §8–§11). Both use the shared SQLite schema in §5.2.

| Tool | Version used in this manual | Install line |
|---|---|---|
| Python | 3.12 | `python -m pip install fastapi uvicorn pytest httpx2 email-validator bcrypt pyjwt` |
| Node.js | 22 LTS | `npm install express better-sqlite3 bcryptjs jsonwebtoken cors helmet express-rate-limit` |
| Express | 5.x (what `npm install express` installs today) | see §7.6 for differences from Express 4 |
| Node dev tools | — | `npm install -D supertest` (Jest optional: `npm install -D jest`) |
| PostgreSQL client | `pg` 8.x | `npm install pg` |

> **Note:** Windows PowerShell users: use `curl.exe` (not `curl`, which is an alias for `Invoke-WebRequest`), and activate Python environments with `.venv\Scripts\Activate.ps1`. §11.2 gives PowerShell-safe request examples.

## 1. Practical exam approach

### 1.1 The 12-step workflow

Work top to bottom. Never start coding before steps 1–4 are written down; ten minutes of design prevents an hour of rework.

| # | Step | What you produce | Time share |
|---|---|---|---|
| 1 | Read the brief twice; underline **nouns** (entities), **verbs** (endpoints) and **rules** (validation / status codes) | Numbered requirement list R1, R2, … | 5% |
| 2 | Identify entities and relationships | Table list + ERD sketch (§1.3) | 5% |
| 3 | Translate requirements into an endpoint table | Method, path, purpose, success + failure codes | 5% |
| 4 | Write the schema with constraints | `schema.sql` (§5.2) | 8% |
| 5 | Skeleton: server starts, health route answers, DB connects | Running app | 7% |
| 6 | Finish **one** resource end to end (create, read, test) | First working vertical slice | 15% |
| 7 | Remaining CRUD + relationships | All routes | 20% |
| 8 | Validation and consistent error responses | 400/404/409 behave | 8% |
| 9 | Business rules inside transactions (borrow, return, fine) | Rules enforced | 8% |
| 10 | Test (curl / Postman / automated) and take screenshots | Evidence | 10% |
| 11 | Debug from the full error message; retest | Fixes | 4% |
| 12 | Document: README, endpoints, setup, run, test | `README.md` | 5% |

> **Exam tip:** Have a working `GET` and `POST` for your main resource by about **45% of the time**. A small system that works end to end beats a large one that does not start.

### 1.2 From scenario to requirements to endpoints

> **Scenario:** A community library needs a system to register books and members, lend books to members, record returns, charge a fine for late returns, and show which books are currently on loan.

Each noun becomes a table, each verb an endpoint, each rule a validation or a status code:

| Requirement (from the brief) | Table(s) | Endpoint | Success | Failure cases |
|---|---|---|---|---|
| Register a book | books | `POST /books` | 201 | 400 invalid, 409 duplicate ISBN |
| List / search books | books | `GET /books?q=&available=` | 200 | — |
| View one book | books | `GET /books/{id}` | 200 | 404 |
| Correct a book (all / some fields) | books | `PUT` / `PATCH /books/{id}` | 200 | 400, 404, 409 |
| Remove a book | books | `DELETE /books/{id}` | 204 | 404, 409 (has loan history) |
| Register a member | members | `POST /members` | 201 | 400, 409 duplicate email |
| Lend a book | loans, books | `POST /loans` | 201 | 400, 404 book/member, 409 not available |
| Return a book (fine if late) | loans, books | `POST /loans/{id}/return` | 200 | 404, 409 already returned |
| Show current loans | loans | `GET /loans?active=true` | 200 | — |
| A member's loans | loans | `GET /members/{id}/loans` | 200 | 404 member |
| Staff sign-in and roles | users | `POST /auth/login` | 200 | 400, 401 |

### 1.3 Database and architecture sketch

Draw this in the first 10 minutes and keep it in your README.

```text
members 1 ----< loans >---- 1 books            users (separate: staff log-ins)
-----------     ---------     ---------         ---------
member_id PK    loan_id PK    book_id PK        user_id PK
name            book_id FK    title             username UNIQUE
email UNIQUE    member_id FK  author            password_hash
cell_number     loaned_on     isbn UNIQUE       role
                due_on        available 0/1
                returned_on   (NULL = still out)
                fine
```

```text
Client (curl / Postman / browser)
   |  HTTP + JSON
   v
Route handler --> Validation --> Business rules --> Data access --> SQLite / PostgreSQL
   ^                                                                   |
   +---- JSON + status code <---- Error-handling middleware <----------+
```

| Layer | Responsibility | Node file | Python file |
|---|---|---|---|
| Routes | Parse request, call the layers below, choose status code | `routes/*.js` | `main.py` |
| Validation | Reject bad input early (400/422) | `validate.js` | Pydantic models |
| Rules | Pure functions (fine, days late); easy to unit test | `rules.js` | `library_rules.py` |
| Data access | SQL with parameters, transactions | `db.js` | `db.py` |
| Errors | One place that turns exceptions into JSON | `errors.js` | `HTTPException` |

### 1.4 Reusing the pattern for other systems

The Library API is a template: one **catalogue** table, one **people** table, and one **transaction** table that links them and enforces a rule.

| System | Catalogue | People | Link table (+ rule) | Key action endpoint | Conflict (409) |
|---|---|---|---|---|---|
| Library | books | members | loans (one active loan per book) | `POST /loans` | book already on loan |
| Student management | courses | students | enrolments (capacity limit) | `POST /enrolments` | course full / already enrolled |
| Inventory | products | customers or suppliers | stock_movements (stock never < 0) | `POST /stock-movements` | insufficient stock |
| Customer management | products | customers | orders + order_items (price at time of order) | `POST /orders` | out of stock |

### 1.5 Documentation and screenshots

Evidence matters as much as code. Capture the **command or query and its result in the same screenshot**, with the status code visible.

- [ ] Server start-up (command and "listening" message)
- [ ] Each endpoint, success case, with request and response
- [ ] At least one validation failure (400/422), one missing resource (404) and one conflict (409)
- [ ] Database proof: `SELECT` showing rows before and after a borrow/return
- [ ] Automated test run showing passes (`node --test` or `pytest -v`)
- [ ] Project folder structure

**File:** `README.md` *(template; replace the brackets)*

```markdown
# [Project name] — [one-line purpose]

## Requirements
R1 [requirement] ... R2 [requirement] ...

## Setup and run
1. `python -m venv .venv` then activate it (or: `npm install`)
2. `python -m pip install -r requirements.txt` (or: `npm install`)
3. `python -m uvicorn main:app --reload` (or: `npm start`) -> http://127.0.0.1:8000 (or :3000)
4. Run tests: `python -m pytest -v` (or: `npm test`)

## Endpoints
| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|

## Database
Tables: [list]. Schema file: `schema.sql`. Relationships: [describe].

## Known limitations
[e.g. no pagination; demo-grade security]
```

## 2. Python essentials

Every snippet in this section is **standalone**: save as a `.py` file or paste into `python` and run.

### 2.1 Variables and data types

```python
book_id = 1                    # int
title = "Clean Code"           # str
fine_per_day = 5.0             # float
available = True               # bool
isbn = None                    # NoneType: "no value yet"
tags = ["software", "craft"]   # list: ordered, mutable
dims = (14.5, 21.0)            # tuple: ordered, immutable
meta = {"pages": 464}          # dict: key -> value
unique = {1, 2, 2, 3}          # set: no duplicates

for name, value in [("book_id", book_id), ("title", title), ("fine_per_day", fine_per_day),
                    ("available", available), ("isbn", isbn), ("tags", tags),
                    ("dims", dims), ("meta", meta), ("unique", unique)]:
    print(f"{name:13} {type(value).__name__:6} {value!r}")

print(f"Fine for 3 days: R{3 * fine_per_day:.2f}")           # f-string, 2 decimals
print(int("42") + 1, str(7) + "x", float("2.5") * 2)         # conversions
```

```output
book_id       int    1
title         str    'Clean Code'
fine_per_day  float  5.0
available     bool   True
isbn          NoneType None
tags          list   ['software', 'craft']
dims          tuple  (14.5, 21.0)
meta          dict   {'pages': 464}
unique        set    {1, 2, 3}
Fine for 3 days: R15.00
43 7x 5.0
```

### 2.2 Conditions

```python
def loan_status(days_overdue: int, returned: bool) -> str:
    if returned:
        return "closed"
    elif days_overdue > 0:
        return "overdue"
    elif days_overdue == 0:
        return "due today"
    else:
        return "on loan"

for days, returned in [(3, False), (0, False), (-5, False), (9, True)]:
    print(loan_status(days, returned), end=" | ")
print()

role = "librarian"
can_edit = role in ("librarian", "admin")          # membership test
label = "Available" if can_edit else "Read only"   # conditional expression
print(can_edit, label)
```

```output
overdue | due today | on loan | closed
True Available
```

> **Common mistake:** `=` assigns, `==` compares. Also `if x = 5:` is a `SyntaxError` in Python; `elif` not `else if`; indentation (4 spaces) is syntax.

### 2.3 Loops

```python
titles = ["Clean Code", "Refactoring", "The Pragmatic Programmer"]

for i, t in enumerate(titles, start=1):       # index + value
    print(i, t)

for n in range(3):                            # 0, 1, 2
    print("range", n)

count = 0
while count < 3:                              # repeat while condition is true
    count += 1
print("count =", count)

for t in titles:
    if t.startswith("R"):
        print("found:", t)
        break                                 # stop the loop; `continue` skips to next item

print(sum(len(t) for t in titles))            # generator expression
```

```output
1 Clean Code
2 Refactoring
3 The Pragmatic Programmer
range 0
range 1
range 2
count = 3
found: Refactoring
51
```

### 2.4 Functions with validation

```python
FINE_PER_DAY = 5.0

def calculate_fine(days_late: int, fine_per_day: float = FINE_PER_DAY) -> float:
    """Return the fine in rand. Raises ValueError for negative input."""
    if days_late < 0 or fine_per_day < 0:
        raise ValueError("Values cannot be negative")
    return days_late * fine_per_day

print(calculate_fine(3))             # uses default rate
print(calculate_fine(0))
print(calculate_fine(2, 7.5))        # override the rate
try:
    calculate_fine(-1)
except ValueError as e:
    print("Error:", e)
```

```output
15.0
0.0
15.0
Error: Values cannot be negative
```

### 2.5 Input validation helper

Return a **list of messages** so the client sees every problem at once. The same shape is reused in the Node version (§7.3).

```python
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_member(data: dict) -> list[str]:
    errors = []
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name is required")
    email = data.get("email")
    if not isinstance(email, str) or not EMAIL_RE.match(email):
        errors.append("email is invalid")
    cell = data.get("cell_number")                 # optional field
    if cell is not None and not (isinstance(cell, str) and cell.isdigit() and len(cell) == 10):
        errors.append("cell_number must be 10 digits")
    return errors

good = {"name": "Thandi", "email": "thandi@example.com", "cell_number": "0821234567"}
bad = {"name": " ", "email": "not-an-email", "cell_number": "12ab"}
print(validate_member(good))
print(validate_member(bad))
```

```output
[]
['name is required', 'email is invalid', 'cell_number must be 10 digits']
```

### 2.6 Lists and dictionaries (in-memory CRUD)

```python
books = [
    {"book_id": 1, "title": "Clean Code", "available": True},
    {"book_id": 2, "title": "Refactoring", "available": True},
]

books.append({"book_id": 3, "title": "The Pragmatic Programmer", "available": True})  # create
book = next((b for b in books if b["book_id"] == 2), None)    # read (None if missing)
if book:
    book["available"] = False                                  # update
books = [b for b in books if b["book_id"] != 1]                # delete

print([b["title"] for b in books if b["available"]])        # list comprehension + filter
print(sorted(books, key=lambda b: b["title"], reverse=True)[0]["title"])
print(books[0].get("isbn", "no isbn"))                       # .get() avoids KeyError
```

```output
['The Pragmatic Programmer']
The Pragmatic Programmer
no isbn
```

### 2.7 Classes and dataclasses

```python
from dataclasses import dataclass, asdict

class BookUnavailableError(Exception):
    """Raised when a book is already on loan."""

class Book:
    def __init__(self, book_id: int, title: str):
        self.book_id = book_id
        self.title = title
        self.available = True

    def borrow(self) -> None:
        if not self.available:
            raise BookUnavailableError(f"'{self.title}' is already on loan")
        self.available = False

    def __repr__(self) -> str:
        return f"Book({self.book_id}, {self.title!r}, available={self.available})"

@dataclass
class Member:                       # dataclass: __init__, __repr__ and __eq__ generated
    member_id: int
    name: str
    email: str

b = Book(1, "Clean Code")
b.borrow()
print(b)
try:
    b.borrow()
except BookUnavailableError as e:
    print("Error:", e)
print(asdict(Member(7, "Thandi", "thandi@example.com")))
```

```output
Book(1, 'Clean Code', available=False)
Error: 'Clean Code' is already on loan
{'member_id': 7, 'name': 'Thandi', 'email': 'thandi@example.com'}
```

### 2.8 Exception handling

```python
def parse_quantity(text: str) -> int:
    try:
        value = int(text)
    except ValueError:                       # specific exception first
        print(f"  '{text}' is not a whole number")
        return 0
    else:                                    # runs only if no exception occurred
        print(f"  parsed {value}")
        return value
    finally:                                 # always runs (clean-up goes here)
        print("  done")

for raw in ["12", "twelve"]:
    print(f"input={raw!r}")
    parse_quantity(raw)

try:
    {}["missing"]
except KeyError as e:
    print("KeyError:", e)
```

```output
input='12'
  parsed 12
  done
input='twelve'
  'twelve' is not a whole number
  done
KeyError: 'missing'
```

> **Common mistake:** a bare `except:` hides real bugs (even typos). Catch the specific exception you expect.

### 2.9 Files and JSON

```python
import json
from pathlib import Path

folder = Path("data_demo")
folder.mkdir(exist_ok=True)
file = folder / "books.json"

books = [{"book_id": 1, "title": "Clean Code", "available": True}]
file.write_text(json.dumps(books, indent=2), encoding="utf-8")   # write

loaded = json.loads(file.read_text(encoding="utf-8"))            # read
loaded.append({"book_id": 2, "title": "Refactoring", "available": False})

with open(file, "w", encoding="utf-8") as f:                     # `with` closes the file for you
    json.dump(loaded, f, indent=2)

print(file.exists(), len(json.loads(file.read_text())), file.stat().st_size > 0)
try:
    json.loads("{bad json}")
except json.JSONDecodeError as e:
    print("Invalid JSON:", e.msg)
```

```output
True 2 True
Invalid JSON: Expecting property name enclosed in double quotes
```

## 3. REST API design

### 3.1 Anatomy of a request and a response

```http
POST /books HTTP/1.1                      <- method, path, protocol
Host: 127.0.0.1:3000
Content-Type: application/json            <- tells the server how to parse the body
Authorization: Bearer <token>             <- only for protected routes

{"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884"}
```

```http
HTTP/1.1 201 Created                      <- status code + reason
Content-Type: application/json; charset=utf-8
Location: /books/1                        <- where the new resource lives

{"book_id": 1, "title": "Clean Code", "author": "Robert C. Martin",
 "isbn": "9780132350884", "available": true}
```

### 3.2 URL design rules

| Do | Don't | Why |
|---|---|---|
| `GET /books/5` | `GET /getBook?id=5` | Paths name **resources** (nouns); the method is the verb |
| `/books`, `/members` (plural) | `/book`, `/Member` | Consistent, lower case |
| `GET /members/2/loans` | `GET /memberLoans/2` | Nesting shows the relationship |
| `GET /books?available=true&q=code` | `GET /books/available/true` | Filters, search and sorting go in the **query string** |
| `POST /loans/9/return` | `GET /returnBook?loan=9` | Actions that change state are never `GET`; an action without a natural noun is a sub-resource verb |
| `DELETE /books/5` returns 204 | returning 200 with an empty body | 204 means "done, nothing to send" |

### 3.3 PUT versus PATCH versus POST

| | `POST /books` | `PUT /books/5` | `PATCH /books/5` |
|---|---|---|---|
| Purpose | **Create** a new resource; server picks the id | **Replace** the whole resource | **Change selected fields** only |
| Body must contain | All required fields | **All** fields (missing optional ones are reset to null) | Only the fields to change (at least one) |
| Repeating the same call | Creates another one | Same result (idempotent) | Same result if values are absolute |
| Success | 201 | 200 (or 204) | 200 (or 204) |

```text
Stored:  {"book_id": 5, "title": "Clean Code", "author": "R. Martin", "isbn": "9780132350884"}

PUT   /books/5  {"title": "Clean Code 2e", "author": "R. Martin"}   -> isbn becomes null (replaced)
PATCH /books/5  {"title": "Clean Code 2e"}                           -> author and isbn untouched
```

### 3.4 Error response design

Pick one shape and use it everywhere. The Express project returns `{"error": message, "details": [...]}`; FastAPI's built-in shape is `{"detail": ...}` and you can leave it as is.

```json
{ "error": "Validation failed",
  "details": ["title is required (1-100 characters)", "isbn must be 10 or 13 digits"] }
```

```json
{ "error": "Book 99 not found" }
```

```json
{ "error": "Book 3 is already on loan" }
```

> **Exam tip:** Choose the status code by *who is at fault and what kind*: malformed or invalid input → **400** (FastAPI: **422**); not signed in → **401**; signed in but not allowed → **403**; id/route does not exist → **404**; the request is valid but clashes with current state (duplicate, already borrowed) → **409**.

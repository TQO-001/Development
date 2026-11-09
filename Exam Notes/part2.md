## 4. Python + FastAPI

### 4.1 Setup and run

```bash
# macOS / Linux / Git Bash
python -m venv .venv
source .venv/bin/activate
python -m pip install fastapi uvicorn pytest httpx2 email-validator bcrypt pyjwt
python -m uvicorn main:app --reload        # run in the folder that contains main.py
```

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1                 # if blocked: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install fastapi uvicorn pytest httpx2 email-validator bcrypt pyjwt
python -m uvicorn main:app --reload
```

`main:app` means "file `main.py`, object `app`". The API is at `http://127.0.0.1:8000`; **interactive documentation (Swagger UI) is at `/docs`**, where *Try it out* sends real requests. Stop the server with `Ctrl+C`.

> **Common mistake:** `Error loading ASGI app` = wrong folder, wrong filename, or a syntax error in `main.py`. `Address already in use` = a previous server is still running; stop it or use `--port 8001`.

### 4.2 Minimal API with in-memory storage

This is the manual's original starter, corrected: `PATCH` now takes a JSON **body** (not a query parameter), `PUT` was added, and text fields reject blank strings. *Standalone.* Data is lost when the server restarts; do not call it persistent.

**File:** `inmemory_demo/main.py`

```python
from typing import Annotated
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StringConstraints

app = FastAPI(title="Library API (in-memory demo)", version="1.0.0")
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]

class BookCreate(BaseModel):
    title: Text
    author: Text

class BookPatch(BaseModel):                  # every field optional -> partial update
    title: Text | None = None
    author: Text | None = None
    available: bool | None = None

class Book(BookCreate):
    book_id: int
    available: bool = True

books: list[Book] = []                       # temporary storage: resets on restart
next_id = 1

def find_index(book_id: int) -> int:
    for i, b in enumerate(books):
        if b.book_id == book_id:
            return i
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/")
def home():
    return {"message": "Library API is running"}

@app.get("/books", response_model=list[Book])
def list_books():
    return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    return books[find_index(book_id)]

@app.post("/books", response_model=Book, status_code=201)
def create_book(payload: BookCreate):
    global next_id
    book = Book(book_id=next_id, **payload.model_dump())
    books.append(book)
    next_id += 1
    return book

@app.put("/books/{book_id}", response_model=Book)
def replace_book(book_id: int, payload: BookCreate):
    i = find_index(book_id)
    books[i] = Book(book_id=book_id, available=books[i].available, **payload.model_dump())
    return books[i]

@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, payload: BookPatch):
    i = find_index(book_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)  # only what the client sent
    if not changes:
        raise HTTPException(status_code=400, detail="Send at least one field")
    books[i] = books[i].model_copy(update=changes)
    return books[i]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    books.pop(find_index(book_id))
```

Test it with curl (bash). The JSON body is wrapped in single quotes; PowerShell versions are in §11.2.

```bash
H="Content-Type: application/json"
curl -s -X POST localhost:8000/books -H "$H" -d '{"title":"Clean Code","author":"Robert C. Martin"}'
curl -s localhost:8000/books/1
curl -s -X PATCH localhost:8000/books/1 -H "$H" -d '{"available":false}'
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE localhost:8000/books/1
curl -s localhost:8000/books/1
```

```output
{"title":"Clean Code","author":"Robert C. Martin","book_id":1,"available":true}
{"title":"Clean Code","author":"Robert C. Martin","book_id":1,"available":true}
{"title":"Clean Code","author":"Robert C. Martin","book_id":1,"available":false}
204
{"detail":"Book not found"}
```

### 4.3 The SQLite-backed Library API (complete project)

Same endpoints as the Node project (§8). Layout and run command:

```text
library_fastapi/
  schema.sql          <- from section 5.2 (shared with the Node project)
  library_rules.py    pure functions (fine, days late)
  db.py               connection handling
  main.py             models + routes
  tests/              pytest files (section 4.5)
  pytest.ini
```

**File:** `library_fastapi/library_rules.py`

```python
from datetime import date

FINE_PER_DAY = 5.0          # rand per day late

def calculate_fine(days_late: int, fine_per_day: float = FINE_PER_DAY) -> float:
    if days_late < 0 or fine_per_day < 0:
        raise ValueError("Values cannot be negative")
    return days_late * fine_per_day

def days_late(due_on: date, returned_on: date) -> int:
    """Whole days after the due date; 0 when on time or early."""
    return max(0, (returned_on - due_on).days)
```

**File:** `library_fastapi/db.py` *(depends on `schema.sql`, §5.2)*

```python
import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

DB_FILE = os.getenv("DB_FILE", "library.db")        # tests replace this value
SCHEMA = Path(__file__).with_name("schema.sql")

def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, check_same_thread=False)  # `def` routes run in a thread pool
    con.row_factory = sqlite3.Row                             # rows behave like dicts
    con.execute("PRAGMA foreign_keys = ON")                   # OFF by default in SQLite, per connection
    return con

def init_db() -> None:
    con = connect()
    try:
        con.executescript(SCHEMA.read_text(encoding="utf-8"))  # CREATE TABLE IF NOT EXISTS ...
        con.commit()
    finally:
        con.close()

def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one connection per request, always closed afterwards."""
    con = connect()
    try:
        yield con
    finally:
        con.close()
```

**File:** `library_fastapi/main.py` *(depends on `db.py` and `library_rules.py`)*

```python
import sqlite3
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, StringConstraints

from db import get_db, init_db
from library_rules import calculate_fine, days_late

Db = Annotated[sqlite3.Connection, Depends(get_db)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Isbn = Annotated[str, StringConstraints(pattern=r"^\d{10}(\d{3})?$")]
Cell = Annotated[str, StringConstraints(pattern=r"^\d{10}$")]

# ---------- request models (Pydantic validates before your code runs; failures -> 422) ----------
class BookIn(BaseModel):
    title: Text
    author: Text
    isbn: Isbn | None = None

class BookPatch(BaseModel):
    title: Text | None = None
    author: Text | None = None
    isbn: Isbn | None = None

class BookOut(BaseModel):
    book_id: int
    title: str
    author: str
    isbn: str | None
    available: bool

class MemberIn(BaseModel):
    name: Text
    email: EmailStr
    cell_number: Cell | None = None

class LoanIn(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    days: int = Field(default=14, ge=1, le=60)

BOOK_SQL = "SELECT book_id, title, author, isbn, available FROM books"
MEMBER_SQL = "SELECT member_id, name, email, cell_number FROM members"
LOAN_SQL = """SELECT l.loan_id, l.book_id, b.title, l.member_id, m.name AS member_name,
                     l.loaned_on, l.due_on, l.returned_on, l.fine
              FROM loans l JOIN books b ON b.book_id = l.book_id
                           JOIN members m ON m.member_id = l.member_id"""

def get_or_404(con: sqlite3.Connection, sql: str, params: tuple, what: str):
    row = con.execute(sql, params).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{what} not found")
    return row

# ---------- books ----------
books = APIRouter(prefix="/books", tags=["books"])

@books.get("", response_model=list[BookOut])
def list_books(con: Db, q: str | None = None, available: bool | None = None):
    where, params = [], []
    if q:
        where.append("(title LIKE ? OR author LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if available is not None:
        where.append("available = ?")
        params.append(int(available))
    sql = BOOK_SQL + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY title"
    return [dict(r) for r in con.execute(sql, params)]

@books.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, con: Db):
    return dict(get_or_404(con, BOOK_SQL + " WHERE book_id = ?", (book_id,), "Book"))

@books.post("", response_model=BookOut, status_code=201)
def create_book(payload: BookIn, con: Db):
    try:
        with con:                                       # commit on success, roll back on error
            cur = con.execute("INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)",
                              (payload.title, payload.author, payload.isbn))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A book with that ISBN already exists")
    return get_book(cur.lastrowid, con)

@books.put("/{book_id}", response_model=BookOut)
def replace_book(book_id: int, payload: BookIn, con: Db):
    get_book(book_id, con)                              # 404 if missing
    try:
        with con:
            con.execute("UPDATE books SET title = ?, author = ?, isbn = ? WHERE book_id = ?",
                        (payload.title, payload.author, payload.isbn, book_id))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A book with that ISBN already exists")
    return get_book(book_id, con)

@books.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookPatch, con: Db):
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Send at least one field to change")
    get_book(book_id, con)
    assignments = ", ".join(f"{col} = ?" for col in changes)   # column names come from the model only
    try:
        with con:
            con.execute(f"UPDATE books SET {assignments} WHERE book_id = ?",
                        (*changes.values(), book_id))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A book with that ISBN already exists")
    return get_book(book_id, con)

@books.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, con: Db):
    get_book(book_id, con)
    try:
        with con:
            con.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    except sqlite3.IntegrityError:                      # foreign key from loans -> RESTRICT
        raise HTTPException(status_code=409, detail="Book has loan history and cannot be deleted")

# ---------- members ----------
members = APIRouter(prefix="/members", tags=["members"])

@members.get("")
def list_members(con: Db):
    return [dict(r) for r in con.execute(MEMBER_SQL + " ORDER BY name")]

@members.post("", status_code=201)
def create_member(payload: MemberIn, con: Db):
    try:
        with con:
            cur = con.execute("INSERT INTO members (name, email, cell_number) VALUES (?, ?, ?)",
                              (payload.name, payload.email, payload.cell_number))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A member with that email already exists")
    return dict(con.execute(MEMBER_SQL + " WHERE member_id = ?", (cur.lastrowid,)).fetchone())

@members.get("/{member_id}/loans")
def member_loans(member_id: int, con: Db):
    get_or_404(con, "SELECT 1 FROM members WHERE member_id = ?", (member_id,), "Member")
    rows = con.execute(LOAN_SQL + " WHERE l.member_id = ? ORDER BY l.loan_id", (member_id,))
    return [dict(r) for r in rows]

# ---------- loans ----------
loans = APIRouter(prefix="/loans", tags=["loans"])

@loans.get("")
def list_loans(con: Db, active: bool = False):
    where = " WHERE l.returned_on IS NULL" if active else ""
    return [dict(r) for r in con.execute(LOAN_SQL + where + " ORDER BY l.loan_id")]

@loans.post("", status_code=201)
def borrow_book(payload: LoanIn, con: Db):
    get_or_404(con, "SELECT 1 FROM books WHERE book_id = ?", (payload.book_id,), "Book")
    get_or_404(con, "SELECT 1 FROM members WHERE member_id = ?", (payload.member_id,), "Member")
    today = date.today()
    with con:                                  # ONE transaction: both changes happen, or neither
        cur = con.execute("UPDATE books SET available = 0 WHERE book_id = ? AND available = 1",
                          (payload.book_id,))
        if cur.rowcount == 0:                  # nothing updated -> already on loan
            raise HTTPException(status_code=409,
                                detail=f"Book {payload.book_id} is already on loan")
        loan = con.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (?, ?, ?, ?)",
            (payload.book_id, payload.member_id, today.isoformat(),
             (today + timedelta(days=payload.days)).isoformat()))
    return dict(con.execute(LOAN_SQL + " WHERE l.loan_id = ?", (loan.lastrowid,)).fetchone())

@loans.post("/{loan_id}/return")
def return_book(loan_id: int, con: Db):
    loan = get_or_404(con, "SELECT * FROM loans WHERE loan_id = ?", (loan_id,), "Loan")
    if loan["returned_on"] is not None:
        raise HTTPException(status_code=409, detail="Loan was already returned")
    today = date.today()
    late = days_late(date.fromisoformat(loan["due_on"]), today)
    fine = calculate_fine(late)
    with con:
        con.execute("UPDATE loans SET returned_on = ?, fine = ? WHERE loan_id = ?",
                    (today.isoformat(), fine, loan_id))
        con.execute("UPDATE books SET available = 1 WHERE book_id = ?", (loan["book_id"],))
    return {"loan_id": loan_id, "book_id": loan["book_id"], "returned_on": today.isoformat(),
            "days_late": late, "fine": fine}

# ---------- application ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()                                  # create tables on start-up if missing
    yield

app = FastAPI(title="Library API", version="1.0.0", lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Library API is running"}

for router in (books, members, loans):
    app.include_router(router)
```

> **Why `UPDATE ... WHERE available = 1` and check `rowcount`?** "Read the book, see it is free, then update" has a gap in which another request can borrow it (check-then-act race). A single conditional `UPDATE` is atomic: exactly one request gets `rowcount == 1`. The partial unique index in the schema (§5.2) is the database-level safety net.

> **Common mistake:** `with sqlite3.connect(...) as con:` **commits or rolls back but does not close** the connection. Close it yourself (`con.close()` or `contextlib.closing`), as `get_db` does.

Try the flow in `/docs` or with curl (the server creates `library.db` on first start):

```bash
H="Content-Type: application/json"
curl -s -X POST localhost:8000/books -H "$H" \
     -d '{"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884"}'
curl -s -X POST localhost:8000/members -H "$H" -d '{"name":"Thandi Nkosi","email":"thandi@example.com"}'
curl -s -X POST localhost:8000/loans -H "$H" -d '{"book_id":1,"member_id":1}'
curl -s -X POST localhost:8000/loans -H "$H" -d '{"book_id":1,"member_id":1}'      # same book again
curl -s -X POST localhost:8000/books -H "$H" -d '{"title":" ","author":"X","isbn":"abc"}'
curl -s localhost:8000/books/99
```

```output
{"book_id":1,"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884","available":true}
{"member_id":1,"name":"Thandi Nkosi","email":"thandi@example.com","cell_number":null}
{"loan_id":1,"book_id":1,"title":"Clean Code","member_id":1,"member_name":"Thandi Nkosi","loaned_on":"2026-11-02","due_on":"2026-11-16","returned_on":null,"fine":0.0}
{"detail":"Book 1 is already on loan"}
{"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character","input":" ","ctx":{"min_length":1}},{"type":"string_pattern_mismatch","loc":["body","isbn"],"msg":"String should match pattern '^\\d{10}(\\d{3})?$'","input":"abc","ctx":{"pattern":"^\\d{10}(\\d{3})?$"}}]}
{"detail":"Book not found"}
```

### 4.4 Authentication in FastAPI (demo)

*Standalone demo* with an in-memory user dictionary so the security pieces are visible: **bcrypt** hashing, **JWT** access tokens, a **401** guard, and a **403** role guard. Use the `users` table from §5.2 instead of the dictionary in a real project. Run with `JWT_SECRET=change-me python -m uvicorn auth_demo:app` (PowerShell: `$env:JWT_SECRET="change-me"` first).

**File:** `library_fastapi/auth_demo.py`

```python
import os
import time

import bcrypt
import jwt                                            # PyJWT
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:                           # fail fast: never fall back to a default secret
    raise RuntimeError("Set the JWT_SECRET environment variable")

app = FastAPI(title="Auth demo")
bearer = HTTPBearer()                                 # reads "Authorization: Bearer <token>"
users: dict[str, dict] = {}                           # DEMO ONLY: username -> {password_hash, role}

class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=72)    # bcrypt reads at most 72 bytes

def make_token(username: str, role: str) -> str:
    claims = {"sub": username, "role": role, "exp": int(time.time()) + 3600}   # expires in 1 hour
    return jwt.encode(claims, JWT_SECRET, algorithm="HS256")

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:    # verifies signature AND expiry; pinning `algorithms` blocks algorithm-swap attacks
        return jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_role(*roles: str):
    def checker(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission")
        return user
    return checker

@app.post("/auth/register", status_code=201)
def register(c: Credentials):
    if c.username in users:
        raise HTTPException(status_code=409, detail="Username already taken")
    hashed = bcrypt.hashpw(c.password.encode(), bcrypt.gensalt())   # salted, deliberately slow
    users[c.username] = {"password_hash": hashed, "role": "member"}   # role NEVER comes from client
    return {"username": c.username, "role": "member"}

@app.post("/auth/login")
def login(c: Credentials):
    user = users.get(c.username)
    if user is None or not bcrypt.checkpw(c.password.encode(), user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")  # same for both
    return {"access_token": make_token(c.username, user["role"]), "token_type": "bearer"}

@app.get("/auth/me")
def me(user: dict = Depends(current_user)):
    return {"username": user["sub"], "role": user["role"]}

@app.delete("/admin/books/{book_id}", status_code=204,
            dependencies=[Depends(require_role("admin"))])
def admin_delete(book_id: int):
    return None
```

> **Warning:** This is an *educational* example, not a complete production security solution: no refresh tokens or revocation, no login rate limiting, no HTTPS, in-memory users. See §10 for the checklist.

To protect a route in the library project: `from auth_demo import current_user, require_role`, then add `dependencies=[Depends(require_role("librarian", "admin"))]` to the decorator.

### 4.5 Testing FastAPI with pytest

Run `python -m pytest -v` from `library_fastapi/`. Each test gets a **fresh temporary database**, so tests never depend on execution order. `TestClient` needs `httpx2` with current Starlette; older FastAPI/Starlette versions ask for `httpx` instead (the error message names the package).

**File:** `library_fastapi/pytest.ini`

```ini
[pytest]
pythonpath = .
testpaths = tests
```

**File:** `library_fastapi/tests/test_rules.py` *(unit tests, no server needed)*

```python
from datetime import date

import pytest
from library_rules import calculate_fine, days_late

def test_zero_days():
    assert calculate_fine(0, 5.0) == 0.0

def test_three_days():
    assert calculate_fine(3, 5.0) == 15.0

def test_negative_days_rejected():
    with pytest.raises(ValueError):
        calculate_fine(-1, 5.0)

@pytest.mark.parametrize("due, back, expected", [
    (date(2026, 11, 5), date(2026, 11, 3), 0),     # early
    (date(2026, 11, 5), date(2026, 11, 5), 0),     # exactly on the due date
    (date(2026, 11, 5), date(2026, 11, 8), 3),     # three days late
])
def test_days_late(due, back, expected):
    assert days_late(due, back) == expected
```

**File:** `library_fastapi/tests/test_api.py` *(integration tests; depends on `main.py`, `db.py`)*

```python
import pytest
from fastapi.testclient import TestClient

import db
from main import app

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_FILE", str(tmp_path / "test.db"))   # fresh database per test
    db.init_db()
    return TestClient(app)

def make_book(client, **over):
    body = {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", **over}
    return client.post("/books", json=body)

def make_member(client, email="thandi@example.com"):
    return client.post("/members", json={"name": "Thandi Nkosi", "email": email})

def test_home(client):
    assert client.get("/").status_code == 200

def test_create_and_get_book(client):
    r = make_book(client)
    assert r.status_code == 201
    book = r.json()
    assert book["title"] == "Clean Code" and book["available"] is True
    assert client.get(f"/books/{book['book_id']}").json() == book

def test_invalid_book_is_rejected(client):
    r = client.post("/books", json={"title": "  ", "author": "X", "isbn": "abc"})
    assert r.status_code == 422

def test_missing_book_is_404(client):
    assert client.get("/books/999999").status_code == 404

def test_duplicate_isbn_is_409(client):
    make_book(client)
    assert make_book(client).status_code == 409

def test_patch_changes_only_given_fields(client):
    book = make_book(client).json()
    r = client.patch(f"/books/{book['book_id']}", json={"title": "Clean Code 2e"})
    assert r.status_code == 200 and r.json()["author"] == book["author"]
    assert client.patch(f"/books/{book['book_id']}", json={}).status_code == 400

def test_borrow_and_return_flow(client):
    book, member = make_book(client).json(), make_member(client).json()
    payload = {"book_id": book["book_id"], "member_id": member["member_id"]}
    loan = client.post("/loans", json=payload)
    assert loan.status_code == 201
    assert client.get(f"/books/{book['book_id']}").json()["available"] is False
    assert client.post("/loans", json=payload).status_code == 409          # already on loan
    assert len(client.get("/loans?active=true").json()) == 1
    ret = client.post(f"/loans/{loan.json()['loan_id']}/return")
    assert ret.status_code == 200 and ret.json()["fine"] == 0.0
    assert client.get(f"/books/{book['book_id']}").json()["available"] is True
    assert client.post(f"/loans/{loan.json()['loan_id']}/return").status_code == 409

def test_borrow_with_missing_member_changes_nothing(client):
    book = make_book(client).json()
    r = client.post("/loans", json={"book_id": book["book_id"], "member_id": 999})
    assert r.status_code == 404
    assert client.get(f"/books/{book['book_id']}").json()["available"] is True

def test_late_return_is_fined(client):
    book, member = make_book(client).json(), make_member(client).json()
    payload = {"book_id": book["book_id"], "member_id": member["member_id"]}
    loan = client.post("/loans", json=payload).json()
    con = db.connect()                                   # make the loan 3 days overdue in the DB
    with con:
        con.execute("UPDATE loans SET due_on = date('now', '-3 days') WHERE loan_id = ?",
                    (loan["loan_id"],))
    con.close()
    ret = client.post(f"/loans/{loan['loan_id']}/return").json()
    assert ret["days_late"] == 3 and ret["fine"] == 15.0

def test_cannot_delete_book_with_history(client):
    book, member = make_book(client).json(), make_member(client).json()
    client.post("/loans", json={"book_id": book["book_id"], "member_id": member["member_id"]})
    assert client.delete(f"/books/{book['book_id']}").status_code == 409
```

**File:** `library_fastapi/tests/test_auth_demo.py` *(depends on `auth_demo.py`)*

```python
import os
os.environ.setdefault("JWT_SECRET", "test-secret")        # must be set before importing auth_demo

import jwt
from fastapi.testclient import TestClient
from auth_demo import app, users

client = TestClient(app)
CREDS = {"username": "thandi", "password": "S3cure-pass!"}

def login():
    client.post("/auth/register", json=CREDS)
    return client.post("/auth/login", json=CREDS).json()["access_token"]

def test_register_login_and_me():
    token = login()
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200 and r.json() == {"username": "thandi", "role": "member"}

def test_wrong_password_is_401():
    login()
    r = client.post("/auth/login", json={**CREDS, "password": "wrong-password"})
    assert r.status_code == 401

def test_missing_token_is_rejected():
    assert client.get("/auth/me").status_code in (401, 403)    # differs between FastAPI versions

def test_member_cannot_use_admin_route():
    token = login()
    r = client.delete("/admin/books/1", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

def test_admin_can_use_admin_route_and_tampered_token_fails():
    login()
    users["thandi"]["role"] = "admin"                  # promote directly (clients can never do this)
    token = client.post("/auth/login", json=CREDS).json()["access_token"]
    ok = client.delete("/admin/books/1", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 204
    forged = jwt.encode({"sub": "thandi", "role": "admin"}, "wrong-secret", algorithm="HS256")
    bad = client.delete("/admin/books/1", headers={"Authorization": f"Bearer {forged}"})
    assert bad.status_code == 401
```

## 5. SQL and SQLite

### 5.1 SQL in one page

| Group | Commands | Remember |
|---|---|---|
| **DDL** (structure) | `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `CREATE INDEX` | Constraints live here |
| **DML** (data) | `INSERT`, `SELECT`, `UPDATE`, `DELETE` | `UPDATE`/`DELETE` **without `WHERE` hit every row** |
| **TCL** (transactions) | `BEGIN`, `COMMIT`, `ROLLBACK` | Related changes succeed or fail together |
| Constraints | `PRIMARY KEY`, `FOREIGN KEY ... REFERENCES`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT` | The database enforces rules even if the app forgets |

Order of a `SELECT`: `SELECT` columns `FROM` table `JOIN` ... `WHERE` row filter `GROUP BY` ... `HAVING` group filter `ORDER BY` ... `LIMIT`. Use single quotes for text (`'Clean Code'`); `NULL` is tested with `IS NULL`, never `= NULL`.

### 5.2 Shared schema for both projects

**File:** `library_fastapi/schema.sql` *(copy the same file to `library-api/src/schema.sql`)*

```sql
-- SQLite schema. Safe to run repeatedly (IF NOT EXISTS).
CREATE TABLE IF NOT EXISTS books (
    book_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL CHECK (length(trim(title))  > 0),
    author    TEXT    NOT NULL CHECK (length(trim(author)) > 0),
    isbn      TEXT    UNIQUE,                    -- NULL allowed; non-NULL values must differ
    available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1))
);

CREATE TABLE IF NOT EXISTS members (
    member_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL CHECK (length(trim(name)) > 0),
    email       TEXT NOT NULL UNIQUE,
    cell_number TEXT
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(member_id) ON DELETE RESTRICT,
    loaned_on   TEXT NOT NULL,                                  -- ISO date YYYY-MM-DD
    due_on      TEXT NOT NULL,
    returned_on TEXT,                                           -- NULL = still on loan
    fine        REAL NOT NULL DEFAULT 0 CHECK (fine >= 0)
);
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
-- At most ONE active loan per book, enforced by the database itself:
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_loan ON loans(book_id) WHERE returned_on IS NULL;

CREATE TABLE IF NOT EXISTS users (                   -- staff log-ins (used from section 10)
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'librarian', 'admin'))
);
```

> **Warning:** SQLite ignores foreign keys unless every connection runs `PRAGMA foreign_keys = ON;`. Without it, deleting a book with loans silently succeeds and leaves orphan rows. Both projects set it in `connect()` / `openDb()`.

### 5.3 INSERT: seed data

The SQL lab in §5.3–§5.9 is one continuous session; run the blocks in order in `sqlite3 lab.db` (or any SQLite viewer) to reproduce the outputs. Use **parameters (`?`)** instead of literal values whenever the values come from a request (§9.3 and §10.9).

```sql
INSERT INTO books (title, author, isbn) VALUES
  ('Clean Code', 'Robert C. Martin', '9780132350884'),
  ('Refactoring', 'Martin Fowler', '9780134757599'),
  ('The Pragmatic Programmer', 'Andrew Hunt', '9780135957059'),
  ('Python Crash Course', 'Eric Matthes', NULL);

INSERT INTO members (name, email, cell_number) VALUES
  ('Thandi Nkosi', 'thandi@example.com', '0821234567'),
  ('Sipho Dlamini', 'sipho@example.com', NULL);

INSERT INTO loans (book_id, member_id, loaned_on, due_on, returned_on, fine) VALUES
  (1, 1, '2026-10-01', '2026-10-15', '2026-10-20', 25.0),   -- returned 5 days late
  (2, 1, '2026-10-20', '2026-11-03', NULL, 0),              -- still out
  (3, 2, '2026-10-22', '2026-11-05', NULL, 0);              -- still out

UPDATE books SET available = 0 WHERE book_id IN (2, 3);     -- keep books in step with open loans
SELECT COUNT(*) AS books FROM books;
```

```output
SQL_OUT
```

### 5.4 SELECT, WHERE, ORDER BY

```sql
SELECT book_id, title, author
FROM books
WHERE available = 1 AND (title LIKE '%code%' OR isbn IS NULL)   -- LIKE ignores case (ASCII)
ORDER BY title ASC
LIMIT 10;
```

```output
SQL_OUT
```

```sql
SELECT title FROM books WHERE book_id IN (1, 3) OR author LIKE 'Martin%';   -- IN, LIKE prefix
SELECT loan_id, due_on FROM loans
WHERE due_on BETWEEN '2026-11-01' AND '2026-11-30' AND returned_on IS NULL;
```

```output
SQL_OUT
```

### 5.5 UPDATE and DELETE

Always write the `WHERE` first, then check how many rows you touched (`changes()` in SQLite; `rowcount` in Python).

```sql
UPDATE members SET cell_number = '0839876543' WHERE member_id = 2;
SELECT changes() AS rows_updated;
DELETE FROM members WHERE email = 'nobody@example.com';       -- matches nothing
SELECT changes() AS rows_deleted;
SELECT name, cell_number FROM members ORDER BY member_id;
```

```output
SQL_OUT
```

### 5.6 JOIN: combining tables

`INNER JOIN` keeps only matching rows; `LEFT JOIN` keeps every row from the left table and fills the right side with `NULL`.

```sql
-- Current loans with names (the query behind GET /loans?active=true)
SELECT l.loan_id, b.title, m.name AS member, l.due_on
FROM loans l
JOIN books   b ON b.book_id   = l.book_id
JOIN members m ON m.member_id = l.member_id
WHERE l.returned_on IS NULL
ORDER BY l.due_on;
```

```output
SQL_OUT
```

```sql
-- Every book, with the number of times it was borrowed (0 for never borrowed)
SELECT b.title, COUNT(l.loan_id) AS times_borrowed
FROM books b
LEFT JOIN loans l ON l.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY times_borrowed DESC, b.title;
```

```output
SQL_OUT
```

### 5.7 GROUP BY, HAVING and aggregate functions

`WHERE` filters rows *before* grouping; `HAVING` filters groups *after* aggregation.

```sql
SELECT m.name,
       COUNT(*)              AS loans,
       SUM(l.fine)           AS total_fines,
       MAX(l.due_on)         AS latest_due,
       ROUND(AVG(l.fine), 2) AS avg_fine
FROM loans l JOIN members m ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
HAVING COUNT(*) >= 1
ORDER BY loans DESC;
```

```output
SQL_OUT
```

### 5.8 Constraints and foreign keys in action

Each statement below is **meant to fail**; the error text is what you will see in a screenshot or an API log.

```sql
PRAGMA foreign_keys = ON;                                  -- once per connection
-- 1: no such book (FOREIGN KEY)
INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (999, 1, '2026-11-02', '2026-11-16');
-- 2: duplicate ISBN (UNIQUE)
INSERT INTO books (title, author, isbn) VALUES ('Copy', 'Someone', '9780132350884');
-- 3: available must be 0 or 1 (CHECK)
INSERT INTO books (title, author, available) VALUES ('X', 'Y', 5);
-- 4: email is required (NOT NULL)
INSERT INTO members (name, email) VALUES ('No Email', NULL);
-- 5: book 2 has loans (ON DELETE RESTRICT)
DELETE FROM books WHERE book_id = 2;
```

```output
SQL_OUT
```

### 5.9 Transactions

A transaction makes several statements **all-or-nothing**. The first block is the borrow operation (mark unavailable + create loan); the second shows that `ROLLBACK` discards changes.

```sql
PRAGMA foreign_keys = ON;
BEGIN;
UPDATE books SET available = 0 WHERE book_id = 4 AND available = 1;
INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (4, 2, '2026-11-02', '2026-11-16');
COMMIT;
SELECT book_id, available FROM books WHERE book_id = 4;

BEGIN;
UPDATE books SET available = 1 WHERE book_id = 4;
SELECT book_id, available AS inside_transaction FROM books WHERE book_id = 4;
ROLLBACK;                                                           -- undo: the UPDATE is discarded
SELECT book_id, available AS after_rollback FROM books WHERE book_id = 4;
```

```output
SQL_OUT
```

### 5.10 Python sqlite3: the original examples, corrected

*Standalone.* Original rules kept: parameterised SQL, check `WHERE` and `rowcount`. Added: `closing()` because `with connect()` does **not** close the connection, and `PRAGMA foreign_keys`.

```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect("library_demo.db")) as con:          # closing() really closes it
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row                                  # dict-like rows
    with con:                                                      # commit / rollback of this block
        con.execute("DROP TABLE IF EXISTS Books")
        con.execute("""CREATE TABLE Books (
                           book_id INTEGER PRIMARY KEY,
                           title TEXT NOT NULL,
                           author TEXT NOT NULL,
                           available INTEGER NOT NULL CHECK (available IN (0, 1)))""")
        con.execute("INSERT INTO Books (title, author, available) VALUES (?, ?, ?)",
                    ("Clean Code", "Robert C. Martin", 1))
        con.executemany("INSERT INTO Books (title, author, available) VALUES (?, ?, ?)",
                        [("Refactoring", "Martin Fowler", 1),
                         ("Clean Architecture", "Robert C. Martin", 0)])

    for row in con.execute("SELECT book_id, title, author FROM Books ORDER BY title"):
        print(dict(row))

    with con:
        cur = con.execute("UPDATE Books SET available = ? WHERE book_id = ?", (0, 1))
        print("Updated rows:", cur.rowcount)                    # 0 would mean WHERE matched nothing
        cur = con.execute("DELETE FROM Books WHERE book_id = ?", (99,))
        print("Deleted rows:", cur.rowcount)

    one = con.execute("SELECT title FROM Books WHERE book_id = ?", (1,)).fetchone()  # None if no row
    print(one["title"] if one else "not found")
```

```output
PY_OUT
```

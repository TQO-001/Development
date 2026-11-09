# Practical EISA — API & Code Snippet Manual
**SAQA 119458 | NQF Level 6**

Code-heavy refresher for practical exam preparation. Examples use Python, FastAPI, HTTP/JSON and SQLite. Follow the exact stack and instructions in the exam.


## 1. Python essentials

```python
# Variables and types
book_id = 1
title = "Clean Code"
available = True
fine_per_day = 5.0

# Conditions
if available:
    print("Available")
else:
    print("Unavailable")

# Loop
for title in ["Clean Code", "Refactoring"]:
    print(title)

# Function with validation
def calculate_fine(days_late: int, fine_per_day: float) -> float:
    if days_late < 0 or fine_per_day < 0:
        raise ValueError("Values cannot be negative")
    return days_late * fine_per_day
```

## 2. HTTP and REST API quick reference

HTTP methods:
- GET: read data, e.g. GET /books
- POST: create, e.g. POST /books
- PUT: replace a resource
- PATCH: partially update
- DELETE: delete a resource

Status codes:
- 200 OK: successful request
- 201 Created: resource created
- 204 No Content: successful operation, no body
- 400 Bad Request: invalid request/business input
- 401 Unauthorized: missing or invalid authentication
- 403 Forbidden: authenticated but not permitted
- 404 Not Found: resource does not exist
- 409 Conflict: state conflict, e.g. book already borrowed
- 422 Unprocessable Content: validation failed
- 500 Internal Server Error: unexpected server failure

REST convention: use resource nouns and predictable paths:
GET /books
GET /books/5
POST /books
PATCH /books/5
DELETE /books/5
GET /members/2/loans

Request example:
```http
POST /books HTTP/1.1
Content-Type: application/json

{
  "title": "Clean Code",
  "author": "Robert C. Martin"
}
```
Response example:
```json
{
  "book_id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "available": true
}
```

## 3. Build a FastAPI application

Install and run:
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install fastapi uvicorn
python -m uvicorn main:app --reload
```
Save this as `main.py`:
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Library API", version="1.0.0")

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)

class Book(BookCreate):
    book_id: int
    available: bool = True

# Temporary storage only; use a database for persistence.
books: list[Book] = []
next_id = 1

@app.get("/")
def home():
    return {"message": "Library API is running"}

@app.get("/books", response_model=list[Book])
def list_books():
    return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books:
        if book.book_id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", response_model=Book, status_code=201)
def create_book(payload: BookCreate):
    global next_id
    book = Book(
        book_id=next_id,
        title=payload.title,
        author=payload.author,
        available=True,
    )
    books.append(book)
    next_id += 1
    return book

@app.patch("/books/{book_id}", response_model=Book)
def set_availability(book_id: int, available: bool):
    for i, book in enumerate(books):
        if book.book_id == book_id:
            updated = book.model_copy(update={"available": available})
            books[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book.book_id == book_id:
            books.pop(i)
            return
    raise HTTPException(status_code=404, detail="Book not found")
```
Open `http://127.0.0.1:8000/docs` for interactive Swagger UI. Try POST, GET, PATCH and DELETE. The in-memory list resets when the server restarts; this is a learning demo, not production persistence.

## 4. API testing with curl

Create:
```bash
curl.exe -X POST "http://127.0.0.1:8000/books" -H "Content-Type: application/json" -d "{\\"title\\":\\"Clean Code\\",\\"author\\":\\"Robert C. Martin\\"}"
```
List:
```bash
curl.exe "http://127.0.0.1:8000/books"
```
Get one:
```bash
curl.exe "http://127.0.0.1:8000/books/1"
```
Change availability:
```bash
curl.exe -X PATCH "http://127.0.0.1:8000/books/1?available=false"
```
Delete:
```bash
curl.exe -X DELETE "http://127.0.0.1:8000/books/1"
```
You can also test all endpoints in `/docs` using Try it out. A successful create should return 201; requesting a missing ID should return 404.

## 5. Design endpoints for the library scenario

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /books | List books |
| GET | /books/{id} | Get one book |
| POST | /books | Register book |
| PATCH | /books/{id} | Update book |
| DELETE | /books/{id} | Delete book if permitted |
| GET | /members | List members |
| POST | /members | Register member |
| GET | /loans | View loans |
| POST | /loans | Borrow a book |
| POST | /loans/{id}/return | Return a book |

Borrowing business rules:
1. Confirm book exists.
2. Confirm member exists.
3. Confirm book is available.
4. Create loan record.
5. Mark book unavailable.
6. Commit both database changes in one transaction.
7. Return a success response.

A book already borrowed should normally produce HTTP 409 Conflict. Missing book/member should produce 404. Do not update availability if loan creation fails.

## 6. Python + SQLite

Create a table:
```python
import sqlite3

with sqlite3.connect("library.db") as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER NOT NULL CHECK (available IN (0, 1))
        )
    """)
```
Insert safely using parameters:
```python
with sqlite3.connect("library.db") as con:
    con.execute(
        "INSERT INTO Books (title, author, available) VALUES (?, ?, ?)",
        ("Clean Code", "Robert C. Martin", 1),
    )
```
Select:
```python
with sqlite3.connect("library.db") as con:
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT book_id, title, author FROM Books ORDER BY title"
    ).fetchall()
    for row in rows:
        print(dict(row))
```
Update:
```python
with sqlite3.connect("library.db") as con:
    cur = con.execute(
        "UPDATE Books SET available = ? WHERE book_id = ?",
        (0, 1),
    )
    print("Updated rows:", cur.rowcount)
```
Delete:
```python
with sqlite3.connect("library.db") as con:
    cur = con.execute("DELETE FROM Books WHERE book_id = ?", (4,))
    print("Deleted rows:", cur.rowcount)
```
Always use parameterised SQL, not string concatenation. Check the WHERE clause and affected row count.

## 7. API validation and security

Pydantic request validation:
```python
from pydantic import BaseModel, Field, EmailStr

class MemberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    cell_number: str | None = Field(default=None, max_length=10)
```
EmailStr may require: `python -m pip install email-validator`

Security essentials:
- Authentication = who are you?
- Authorisation = what are you allowed to do?
- Hash passwords with a password-hashing algorithm; never store plaintext.
- Use HTTPS in deployed systems.
- Validate every request on the server.
- Apply least privilege and role-based permissions.
- Store secrets outside source code.
- Rate-limit login endpoints.
- Never log passwords or access tokens.
- Use parameterised SQL to prevent SQL injection.
- Return 401 for missing/invalid authentication and 403 for insufficient permission.

Bearer token request header:
```http
Authorization: Bearer ACCESS_TOKEN
```
This is only a format example; a server must verify token signature, expiry and permissions.

## 8. API tests with pytest

Install:
```bash
python -m pip install pytest httpx
```
Test a pure function:
```python
import pytest
from library_rules import calculate_fine

def test_zero_days():
    assert calculate_fine(0, 5.0) == 0.0

def test_three_days():
    assert calculate_fine(3, 5.0) == 15.0

def test_negative_days_rejected():
    with pytest.raises(ValueError):
        calculate_fine(-1, 5.0)
```
FastAPI integration test:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_create_book():
    response = client.post(
        "/books",
        json={"title": "Test Book", "author": "Test Author"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"

def test_missing_book():
    response = client.get("/books/999999")
    assert response.status_code == 404
```
Run: `python -m pytest -v`. Reset test data between tests so they do not depend on execution order.

## 9. Debugging cheat sheet

| Error | Meaning / check |
|---|---|
| SyntaxError | Missing colon, bracket, quote or invalid syntax |
| NameError | Variable/function name not defined |
| TypeError | Wrong type or argument count |
| ValueError | Correct type, invalid value |
| KeyError | Dictionary key missing |
| IndexError | List index out of range |
| HTTP 404 | Wrong route or resource ID does not exist |
| HTTP 405 | Method not supported by route |
| HTTP 422 | Request validation failed |
| HTTP 500 | Unhandled server error; inspect terminal traceback |
| SQL integrity error | PK/FK/UNIQUE/NOT NULL constraint violation |

Debug steps:
1. Reproduce.
2. Compare expected and actual result.
3. Read the complete error.
4. Inspect input values and types.
5. Trace the relevant branch.
6. Fix the root cause.
7. Retest success, failure and boundary cases.

## 10. Practical exam checklist

- [ ] Identify inputs, outputs, business rules and failure cases before coding.
- [ ] Follow the requested language, framework, schema and filenames.
- [ ] Create a small working path before adding complexity.
- [ ] Validate input and handle errors.
- [ ] Use correct HTTP methods and status codes.
- [ ] Use parameterised SQL and transactions for related updates.
- [ ] Test normal, invalid, missing-resource and boundary cases.
- [ ] Capture screenshots showing both commands/queries and results.
- [ ] Document setup, run instructions and API endpoints.
- [ ] Do not claim in-memory demo data is persistent.
- [ ] Save all deliverables and verify they open before submission.


## 8. The Library API in Node.js + Express

A complete, layered Express 5 API on SQLite with the **same endpoints, tables and status codes as §4.3**. Security (login, JWT, roles, rate limiting) is added in §10; tests are in §11.

### 8.1 Project layout and setup

```text
library-api/
  package.json  .env  .gitignore            (section 6.2 and below)
  src/
    schema.sql          copy of the shared schema from section 5.2
    db.js               open the database, enable foreign keys, create tables
    rules.js            pure functions: dates, days late, fine
    errors.js           ApiError, 404 handler, error-handling middleware
    validate.js         input validation helpers
    routes/books.js  routes/members.js  routes/loans.js
    app.js              builds the Express app from a database (createApp)
    server.js           reads .env, opens the database, starts listening
  test/                 automated tests (section 11)
```

```bash
cd library-api
npm install                          # installs everything in package.json (section 6.2)
cp ../library_fastapi/schema.sql src/schema.sql      # or copy the file contents from section 5.2
npm run dev                          # http://localhost:3000   (npm start for a plain run)
```

**File:** `library-api/.env` *(never commit this file; `JWT_SECRET` is used from §10)*

```ini
PORT=3000
DB_FILE=library.db
JWT_SECRET=replace-with-a-long-random-string
```

### 8.2 Database, rules and error handling

**File:** `library-api/src/db.js` *(depends on `src/schema.sql`)*

```javascript
const fs = require('node:fs');
const path = require('node:path');
const Database = require('better-sqlite3');

// Shared by the loan queries: one JOIN, reused by several routes.
const LOAN_SELECT = `
  SELECT l.loan_id, l.book_id, b.title, l.member_id, m.name AS member_name,
         l.loaned_on, l.due_on, l.returned_on, l.fine
  FROM loans l
  JOIN books   b ON b.book_id   = l.book_id
  JOIN members m ON m.member_id = l.member_id`;

function openDb(file = process.env.DB_FILE ?? 'library.db') {
  const db = new Database(file);                   // use ':memory:' for a throw-away test database
  db.pragma('journal_mode = WAL');                 // readers do not block the writer
  db.pragma('foreign_keys = ON');                  // OFF by default in SQLite, per connection
  db.exec(fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8'));   // CREATE TABLE IF NOT EXISTS
  return db;
}

module.exports = { openDb, LOAN_SELECT };
```

**File:** `library-api/src/rules.js`

```javascript
const FINE_PER_DAY = 5.0;                                    // rand per day late
const DAY_MS = 24 * 60 * 60 * 1000;

const today = () => new Date().toLocaleDateString('en-CA');  // local date as YYYY-MM-DD

function addDays(isoDate, days) {
  const d = new Date(`${isoDate}T00:00:00`);                 // local midnight
  d.setDate(d.getDate() + days);
  return d.toLocaleDateString('en-CA');
}

function daysLate(dueOn, returnedOn) {                       // whole days after the due date; 0 if on time
  const diff = (new Date(`${returnedOn}T00:00:00`) - new Date(`${dueOn}T00:00:00`)) / DAY_MS;
  return Math.max(0, Math.round(diff));                      // round() absorbs daylight-saving hours
}

function calculateFine(lateDays, finePerDay = FINE_PER_DAY) {
  if (lateDays < 0 || finePerDay < 0) throw new RangeError('Values cannot be negative');
  return lateDays * finePerDay;
}

module.exports = { FINE_PER_DAY, today, addDays, daysLate, calculateFine };
```

**File:** `library-api/src/errors.js`

```javascript
class ApiError extends Error {                     // thrown anywhere; carries the HTTP status
  constructor(status, message, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

function notFoundHandler(req, res) {               // registered AFTER all routes
  res.status(404).json({ error: `Route not found: ${req.method} ${req.originalUrl}` });
}

// Express recognises error-handling middleware by its FOUR parameters. Register it LAST.
function errorHandler(err, req, res, next) {
  if (err instanceof ApiError) {
    const body = { error: err.message, ...(err.details && { details: err.details }) };
    return res.status(err.status).json(body);
  }
  if (err.type === 'entity.parse.failed') {         // express.json() could not parse the body
    return res.status(400).json({ error: 'Malformed JSON body' });
  }
  if (err.code === 'SQLITE_CONSTRAINT_UNIQUE') {    // duplicate ISBN / e-mail / username
    return res.status(409).json({ error: 'A record with that value already exists' });
  }
  if (err.code === 'SQLITE_CONSTRAINT_FOREIGNKEY') { // delete blocked by loans, or reference to a missing row
    return res.status(409).json({ error: 'Record is referenced by other data or a reference is invalid' });
  }
  console.error(err);                               // full details stay in the server log
  res.status(500).json({ error: 'Internal server error' });   // generic message for the client
}

module.exports = { ApiError, notFoundHandler, errorHandler };
```

**File:** `library-api/src/validate.js`

```javascript
const { ApiError } = require('./errors');

const ISBN_RE = /^\d{10}(\d{3})?$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const isText = (v, max = 100) => typeof v === 'string' && v.trim().length > 0 && v.trim().length <= max;

function finish(errors, value) {                   // throw one 400 listing every problem at once
  if (errors.length) throw new ApiError(400, 'Validation failed', errors);
  return value;
}

function parseId(raw, label = 'id') {              // path parameters arrive as strings
  if (!/^\d+$/.test(raw) || Number(raw) < 1) {
    throw new ApiError(400, `${label} must be a positive whole number`);
  }
  return Number(raw);
}

// partial = true is for PATCH: check only the fields the client sent.
// Only known fields are copied into `value`, so clients cannot set `available` or `book_id`.
function validateBook(body = {}, { partial = false } = {}) {
  const errors = [];
  const value = {};
  const wants = (key) => !partial || body[key] !== undefined;
  if (wants('title')) {
    if (isText(body.title)) value.title = body.title.trim();
    else errors.push('title is required (1-100 characters)');
  }
  if (wants('author')) {
    if (isText(body.author)) value.author = body.author.trim();
    else errors.push('author is required (1-100 characters)');
  }
  if (body.isbn !== undefined) {                   // optional; null clears it
    if (body.isbn === null || (typeof body.isbn === 'string' && ISBN_RE.test(body.isbn))) {
      value.isbn = body.isbn;
    } else errors.push('isbn must be 10 or 13 digits');
  }
  return finish(errors, value);
}

function validateMember(body = {}) {
  const errors = [];
  const value = { cell_number: null };
  if (isText(body.name)) value.name = body.name.trim();
  else errors.push('name is required (1-100 characters)');
  if (typeof body.email === 'string' && EMAIL_RE.test(body.email.trim())) {
    value.email = body.email.trim().toLowerCase();
  } else errors.push('email is invalid');
  if (body.cell_number !== undefined && body.cell_number !== null) {
    if (typeof body.cell_number === 'string' && /^\d{10}$/.test(body.cell_number)) {
      value.cell_number = body.cell_number;
    } else errors.push('cell_number must be 10 digits');
  }
  return finish(errors, value);
}

function validateLoan(body = {}) {
  const errors = [];
  const { book_id, member_id } = body;
  const days = body.days ?? 14;
  if (!Number.isInteger(book_id) || book_id < 1) errors.push('book_id must be a positive whole number');
  if (!Number.isInteger(member_id) || member_id < 1) errors.push('member_id must be a positive whole number');
  if (!Number.isInteger(days) || days < 1 || days > 60) errors.push('days must be a whole number from 1 to 60');
  return finish(errors, { book_id, member_id, days });
}

module.exports = { parseId, validateBook, validateMember, validateLoan };
```

### 8.3 Routes: books (GET, POST, PUT, PATCH, DELETE)

**File:** `library-api/src/routes/books.js` *(depends on `db.js`, `errors.js`, `validate.js`)*

```javascript
const express = require('express');
const { ApiError } = require('../errors');
const { parseId, validateBook } = require('../validate');

module.exports = (db) => {                           // a router factory: it receives the database
  const router = express.Router();
  const toBook = (row) => ({ ...row, available: Boolean(row.available) });   // 0/1 -> false/true
  const findById = db.prepare('SELECT * FROM books WHERE book_id = ?');      // compiled once, reused

  function getBook(rawId) {
    const row = findById.get(parseId(rawId));
    if (!row) throw new ApiError(404, `Book ${rawId} not found`);
    return row;
  }

  router.get('/', (req, res) => {                    // GET /books?q=code&available=true
    const { q, available } = req.query;
    const where = [];
    const params = [];
    if (typeof q === 'string' && q.trim()) {
      where.push('(title LIKE ? OR author LIKE ?)');
      params.push(`%${q.trim()}%`, `%${q.trim()}%`);
    }
    if (available === 'true' || available === 'false') {
      where.push('available = ?');
      params.push(available === 'true' ? 1 : 0);
    }
    const sql = `SELECT * FROM books ${where.length ? 'WHERE ' + where.join(' AND ') : ''} ORDER BY title`;
    res.json(db.prepare(sql).all(...params).map(toBook));
  });

  router.get('/:id', (req, res) => res.json(toBook(getBook(req.params.id))));

  router.post('/', (req, res) => {                   // duplicate ISBN -> SQLITE_CONSTRAINT_UNIQUE -> 409
    const { title, author, isbn = null } = validateBook(req.body);
    const info = db.prepare('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)')
      .run(title, author, isbn);
    res.status(201).location(`/books/${info.lastInsertRowid}`)
      .json(toBook(findById.get(info.lastInsertRowid)));
  });

  router.put('/:id', (req, res) => {                 // REPLACE: title + author required, absent isbn -> NULL
    const book = getBook(req.params.id);
    const { title, author, isbn = null } = validateBook(req.body);
    db.prepare('UPDATE books SET title = ?, author = ?, isbn = ? WHERE book_id = ?')
      .run(title, author, isbn, book.book_id);
    res.json(toBook(findById.get(book.book_id)));
  });

  router.patch('/:id', (req, res) => {               // PARTIAL: change only the fields that were sent
    const book = getBook(req.params.id);
    const changes = validateBook(req.body, { partial: true });
    const columns = Object.keys(changes);            // column names come from validateBook, not the client
    if (columns.length === 0) throw new ApiError(400, 'Send at least one field to change');
    const assignments = columns.map((c) => `${c} = ?`).join(', ');
    db.prepare(`UPDATE books SET ${assignments} WHERE book_id = ?`)
      .run(...Object.values(changes), book.book_id);
    res.json(toBook(findById.get(book.book_id)));
  });

  router.delete('/:id', (req, res) => {              // a book with loans -> FOREIGN KEY -> 409
    const book = getBook(req.params.id);
    db.prepare('DELETE FROM books WHERE book_id = ?').run(book.book_id);
    res.status(204).end();
  });

  return router;
};
```

### 8.4 Routes: members and loans

**File:** `library-api/src/routes/members.js`

```javascript
const express = require('express');
const { ApiError } = require('../errors');
const { LOAN_SELECT } = require('../db');
const { parseId, validateMember } = require('../validate');

module.exports = (db) => {
  const router = express.Router();
  const findById = db.prepare('SELECT * FROM members WHERE member_id = ?');

  function getMember(rawId) {
    const row = findById.get(parseId(rawId));
    if (!row) throw new ApiError(404, `Member ${rawId} not found`);
    return row;
  }

  router.get('/', (req, res) => res.json(db.prepare('SELECT * FROM members ORDER BY name').all()));
  router.get('/:id', (req, res) => res.json(getMember(req.params.id)));

  router.post('/', (req, res) => {                   // duplicate e-mail -> 409 via errorHandler
    const m = validateMember(req.body);
    const info = db.prepare('INSERT INTO members (name, email, cell_number) VALUES (?, ?, ?)')
      .run(m.name, m.email, m.cell_number);
    res.status(201).location(`/members/${info.lastInsertRowid}`).json(findById.get(info.lastInsertRowid));
  });

  router.get('/:id/loans', (req, res) => {           // GET /members/2/loans
    const member = getMember(req.params.id);
    res.json(db.prepare(`${LOAN_SELECT} WHERE l.member_id = ? ORDER BY l.loan_id`).all(member.member_id));
  });

  return router;
};
```

**File:** `library-api/src/routes/loans.js` *(depends on `rules.js`, `db.js`)*

```javascript
const express = require('express');
const { ApiError } = require('../errors');
const { LOAN_SELECT } = require('../db');
const { parseId, validateLoan } = require('../validate');
const { today, addDays, daysLate, calculateFine } = require('../rules');

module.exports = (db) => {
  const router = express.Router();

  // db.transaction(fn): everything inside succeeds together, or ALL of it is undone if anything throws.
  const borrow = db.transaction((bookId, memberId, days) => {
    if (!db.prepare('SELECT 1 FROM books WHERE book_id = ?').get(bookId)) {
      throw new ApiError(404, `Book ${bookId} not found`);
    }
    if (!db.prepare('SELECT 1 FROM members WHERE member_id = ?').get(memberId)) {
      throw new ApiError(404, `Member ${memberId} not found`);
    }
    // Atomic check-and-claim: only one request can flip available from 1 to 0.
    const claimed = db.prepare('UPDATE books SET available = 0 WHERE book_id = ? AND available = 1').run(bookId);
    if (claimed.changes === 0) throw new ApiError(409, `Book ${bookId} is already on loan`);
    const start = today();
    return db.prepare('INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (?, ?, ?, ?)')
      .run(bookId, memberId, start, addDays(start, days)).lastInsertRowid;
  });

  const giveBack = db.transaction((loanId) => {
    const loan = db.prepare('SELECT * FROM loans WHERE loan_id = ?').get(loanId);
    if (!loan) throw new ApiError(404, `Loan ${loanId} not found`);
    if (loan.returned_on !== null) throw new ApiError(409, 'Loan was already returned');
    const returnedOn = today();
    const late = daysLate(loan.due_on, returnedOn);
    const fine = calculateFine(late);
    db.prepare('UPDATE loans SET returned_on = ?, fine = ? WHERE loan_id = ?').run(returnedOn, fine, loanId);
    db.prepare('UPDATE books SET available = 1 WHERE book_id = ?').run(loan.book_id);
    return { loan_id: loanId, book_id: loan.book_id, returned_on: returnedOn, days_late: late, fine };
  });

  router.get('/', (req, res) => {                    // GET /loans?active=true  -> books currently out
    const where = req.query.active === 'true' ? 'WHERE l.returned_on IS NULL' : '';
    res.json(db.prepare(`${LOAN_SELECT} ${where} ORDER BY l.loan_id`).all());
  });

  router.post('/', (req, res) => {
    const { book_id, member_id, days } = validateLoan(req.body);
    const loanId = borrow(book_id, member_id, days);
    res.status(201).location(`/loans/${loanId}`)
      .json(db.prepare(`${LOAN_SELECT} WHERE l.loan_id = ?`).get(loanId));
  });

  router.post('/:id/return', (req, res) => res.json(giveBack(parseId(req.params.id))));

  return router;
};
```

### 8.5 Application and server

**File:** `library-api/src/app.js`

```javascript
const express = require('express');
const { notFoundHandler, errorHandler } = require('./errors');

function createApp(db) {                             // takes the database as a parameter: easy to test
  const app = express();
  app.use(express.json());                           // BEFORE the routes

  app.get('/', (req, res) => res.json({ message: 'Library API is running' }));
  app.get('/health', (req, res) => res.json({ status: 'ok' }));
  app.use('/books', require('./routes/books')(db));
  app.use('/members', require('./routes/members')(db));
  app.use('/loans', require('./routes/loans')(db));

  app.use(notFoundHandler);                          // AFTER the routes
  app.use(errorHandler);                             // LAST
  return app;
}

module.exports = { createApp };
```

**File:** `library-api/src/server.js`

```javascript
const { createApp } = require('./app');
const { openDb } = require('./db');

const db = openDb();                                 // ONE connection for the whole process
const app = createApp(db);
const PORT = Number(process.env.PORT ?? 3000);
const server = app.listen(PORT, () => console.log(`Library API on http://localhost:${PORT}`));

function shutdown() {                                // close cleanly on Ctrl+C or a stop signal
  server.close(() => {
    db.close();
    process.exit(0);
  });
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
```

### 8.6 Using the API: the full flow, PUT versus PATCH, and error cases

Start it with `npm run dev`, then (bash; `-w` shows the status code after each response):

```bash
H="Content-Type: application/json"; W="   -> %{http_code}\n"; A=localhost:3000
curl -s -w "$W" -X POST $A/books -H "$H" -d '{"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884"}'
curl -s -w "$W" -X POST $A/members -H "$H" -d '{"name":"Thandi Nkosi","email":"thandi@example.com"}'
curl -s -w "$W" -X POST $A/loans -H "$H" -d '{"book_id":1,"member_id":1}'
curl -s -w "$W" -X POST $A/loans -H "$H" -d '{"book_id":1,"member_id":1}'
curl -s -w "$W" "$A/loans?active=true"
curl -s -w "$W" -X POST $A/loans/1/return
curl -s -w "$W" $A/members/1/loans
```

```output
LIB_FLOW_OUT
```

`PUT` replaces the whole book (omitting `isbn` clears it); `PATCH` changes only what is sent:

```bash
curl -s -w "$W" -X PATCH $A/books/1 -H "$H" -d '{"title":"Clean Code, 2nd ed."}'
curl -s -w "$W" -X PUT   $A/books/1 -H "$H" -d '{"title":"Clean Code","author":"R. C. Martin"}'
curl -s -w "$W" -X PUT   $A/books/1 -H "$H" -d '{"title":"Clean Code"}'
curl -s -w "$W" -X PATCH $A/books/1 -H "$H" -d '{}'
curl -s -w "$W" -X DELETE $A/books/1
curl -s -w "$W" -X POST $A/books -H "$H" -d '{"title":" ","author":"X","isbn":"abc"}'
curl -s -w "$W" -X POST $A/loans -H "$H" -d '{"book_id":99,"member_id":1}'
curl -s -w "$W" $A/books/abc
```

```output
LIB_ERR_OUT
```

> **Exam tip:** The pattern for every new resource is identical: *validate → look up (404) → check rules (409) → write inside a transaction → return the right status*. To adapt this API to students or inventory, copy `routes/books.js`, rename the table and columns, and change the validator.

## 9. Database integration in Node.js

### 9.1 SQLite with better-sqlite3

```bash
npm install better-sqlite3        # downloads a prebuilt binary for your OS and Node version
```

`better-sqlite3` is **synchronous**: no `await`, results come back directly, and one connection per process is the normal design. If the install fails (no matching prebuilt binary and no C++ build tools), use Node's built-in SQLite in §9.7.

*Standalone.* All the basic operations in one file: create tables, insert, select, update, delete, JOIN, aggregates.

```javascript
const Database = require('better-sqlite3');
const db = new Database(':memory:');                       // a file name such as 'library.db' keeps data
db.pragma('foreign_keys = ON');
db.exec(`
  CREATE TABLE books   (book_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                        author TEXT NOT NULL, isbn TEXT UNIQUE, available INTEGER NOT NULL DEFAULT 1);
  CREATE TABLE members (member_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE);
  CREATE TABLE loans   (loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL REFERENCES books(book_id),
                        member_id INTEGER NOT NULL REFERENCES members(member_id),
                        due_on TEXT NOT NULL, returned_on TEXT);
`);

// INSERT: .run() returns { changes, lastInsertRowid }
const addBook = db.prepare('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)');
console.log('insert:', addBook.run('Clean Code', 'Robert C. Martin', '9780132350884'));
addBook.run('Refactoring', 'Martin Fowler', null);
db.prepare('INSERT INTO members (name, email) VALUES (@name, @email)')      // named parameters
  .run({ name: 'Thandi Nkosi', email: 'thandi@example.com' });
db.prepare('INSERT INTO loans (book_id, member_id, due_on) VALUES (?, ?, ?)').run(1, 1, '2026-11-16');

// SELECT: .get() = one row (undefined if none), .all() = array, .iterate() = one row at a time
console.log('get:', db.prepare('SELECT * FROM books WHERE book_id = ?').get(1));
console.log('all:', db.prepare('SELECT book_id, title FROM books ORDER BY title').all());
console.log('missing:', db.prepare('SELECT * FROM books WHERE book_id = ?').get(99));

// UPDATE / DELETE: .changes says how many rows were touched (0 = WHERE matched nothing)
console.log('updated:', db.prepare('UPDATE books SET available = 0 WHERE book_id = ?').run(1).changes);
console.log('deleted:', db.prepare('DELETE FROM books WHERE book_id = ?').run(99).changes);

// JOIN, aggregate, and .pluck() (return just the first column)
console.log('join:', db.prepare(`SELECT l.loan_id, b.title, m.name AS member FROM loans l
  JOIN books b ON b.book_id = l.book_id JOIN members m ON m.member_id = l.member_id
  WHERE l.returned_on IS NULL`).all());
console.log('count:', db.prepare('SELECT COUNT(*) AS books, SUM(available) AS free FROM books').get());
console.log('pluck:', db.prepare('SELECT COUNT(*) FROM members').pluck().get());
db.close();
```

```output
OUT
```

### 9.2 Prepared statements and SQL injection

A **prepared statement** sends the SQL text and the values separately, so a value can never change the structure of the query. *Standalone.*

```javascript
const Database = require('better-sqlite3');
const db = new Database(':memory:');
db.exec(`CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT, email TEXT);
         INSERT INTO members (name, email) VALUES ('Thandi', 'thandi@example.com'), ('Sipho', 'sipho@example.com');`);

const attack = "nobody' OR '1'='1";                          // what an attacker types into the "email" field

// UNSAFE: user input is glued into the SQL text, so the input becomes SQL.
const unsafeSql = `SELECT * FROM members WHERE email = '${attack}'`;
console.log(unsafeSql);
console.log('unsafe rows:', db.prepare(unsafeSql).all().length);

// SAFE: the value travels separately as a parameter and is always treated as data.
console.log('safe rows:  ', db.prepare('SELECT * FROM members WHERE email = ?').all(attack).length);

// Column or table NAMES cannot be parameters: choose them from a fixed allow-list.
const allowedSort = { name: 'name', email: 'email' };
const sortBy = allowedSort['name; DROP TABLE members'] ?? 'name';      // unknown input falls back
console.log(db.prepare(`SELECT name FROM members ORDER BY ${sortBy}`).all());
```

```output
OUT
```

### 9.3 Foreign keys, constraints and database errors

Each failing statement below throws an error with a **`code`**. Map the code to an HTTP status in your error handler (`errors.js` does this for the first two). *Standalone.*

```javascript
const Database = require('better-sqlite3');
const db = new Database(':memory:');
db.pragma('foreign_keys = ON');                              // without this, foreign keys are not enforced
db.exec(`
  CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, isbn TEXT UNIQUE,
                      available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1)));
  CREATE TABLE loans (loan_id INTEGER PRIMARY KEY,
                      book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT);
  INSERT INTO books (book_id, title, isbn) VALUES (1, 'Clean Code', '111');
  INSERT INTO loans (book_id) VALUES (1);
`);

const attempts = {
  'duplicate isbn':   () => db.prepare('INSERT INTO books (title, isbn) VALUES (?, ?)').run('Copy', '111'),
  'missing title':    () => db.prepare('INSERT INTO books (title) VALUES (?)').run(null),
  'bad available':    () => db.prepare('INSERT INTO books (title, available) VALUES (?, ?)').run('X', 5),
  'unknown book_id':  () => db.prepare('INSERT INTO loans (book_id) VALUES (?)').run(99),
  'delete with loan': () => db.prepare('DELETE FROM books WHERE book_id = ?').run(1),
  'syntax error':     () => db.prepare('SELEC * FROM books'),
};
for (const [label, attempt] of Object.entries(attempts)) {
  try {
    attempt();
  } catch (err) {
    console.log(label.padEnd(16), err.code);
  }
}
```

```output
OUT
```

| `err.code` (SQLite) | Cause | Suggested HTTP status |
|---|---|---|
| `SQLITE_CONSTRAINT_UNIQUE` | Duplicate in a `UNIQUE` column | **409** Conflict |
| `SQLITE_CONSTRAINT_FOREIGNKEY` | Missing parent row, or delete blocked by `RESTRICT` | **409** (or 400/404 if you checked first) |
| `SQLITE_CONSTRAINT_NOTNULL` / `_CHECK` | Validation missed a rule | **400** (fix the validator: the database is the safety net) |
| `SQLITE_ERROR` | Bad SQL, missing table or column | **500** (it is a bug; log it, never show it) |
| `SQLITE_BUSY` | Another connection holds the write lock | **503** or retry |

### 9.4 Transactions in Node

`db.transaction(fn)` wraps `BEGIN` / `COMMIT` / `ROLLBACK`: if `fn` throws, **every** change made inside it is undone. *Standalone.* The failing borrow below marks the book unavailable first, then the loan insert fails, and the book is restored automatically.

```javascript
const Database = require('better-sqlite3');
const db = new Database(':memory:');
db.pragma('foreign_keys = ON');
db.exec(`
  CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, available INTEGER NOT NULL DEFAULT 1);
  CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT);
  CREATE TABLE loans (loan_id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books(book_id),
                      member_id INTEGER NOT NULL REFERENCES members(member_id));
  INSERT INTO books (book_id, title) VALUES (1, 'Clean Code'), (2, 'Refactoring');
  INSERT INTO members VALUES (1, 'Thandi');
`);

const borrow = db.transaction((bookId, memberId) => {
  const claimed = db.prepare('UPDATE books SET available = 0 WHERE book_id = ? AND available = 1').run(bookId);
  if (claimed.changes === 0) throw new Error('book is already on loan');
  db.prepare('INSERT INTO loans (book_id, member_id) VALUES (?, ?)').run(bookId, memberId);
});
const available = (id) => db.prepare('SELECT available FROM books WHERE book_id = ?').pluck().get(id);

borrow(1, 1);
console.log('after good borrow, book 1 available =', available(1));
for (const [bookId, memberId] of [[1, 1], [2, 999]]) {
  try {
    borrow(bookId, memberId);
  } catch (err) {
    console.log(`borrow(${bookId}, ${memberId}) failed: ${err.message}`);
  }
}
console.log('book 2 available =', available(2), '(rolled back)');
console.log('loans rows =', db.prepare('SELECT COUNT(*) FROM loans').pluck().get());
```

```output
OUT
```

### 9.5 Connection management

| Do | Because |
|---|---|
| Open the database **once** at start-up (`server.js`) and pass it to the routers | `better-sqlite3` connections are cheap to use and expensive to keep re-opening |
| Run `PRAGMA foreign_keys = ON` (and `journal_mode = WAL`) right after opening | Foreign keys are off by default; WAL lets reads continue during a write |
| Close it on shutdown (`db.close()` in `SIGINT` / `SIGTERM`) | Flushes the file cleanly |
| Use `':memory:'` for tests | Every test run starts from an empty database |
| For PostgreSQL use a **pool** and release every client you check out (§9.7) | Leaked connections exhaust the pool and the API hangs |

### 9.6 Built-in SQLite without installing anything (`node:sqlite`)

Node 22.5+ includes an **experimental** SQLite module. It is a useful fallback if `npm install better-sqlite3` fails on the exam machine. The API is similar; transactions are manual (`BEGIN` / `COMMIT` / `ROLLBACK` with `exec`). It prints an `ExperimentalWarning` and may change between versions. *Standalone.*

```javascript
const { DatabaseSync } = require('node:sqlite');
const db = new DatabaseSync(':memory:');
db.exec('PRAGMA foreign_keys = ON');
db.exec('CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL)');

console.log(db.prepare('INSERT INTO books (title) VALUES (?)').run('Clean Code'));
console.log(db.prepare('SELECT * FROM books WHERE book_id = ?').get(1));
db.exec('BEGIN');
try {
  db.prepare('INSERT INTO books (title) VALUES (?)').run('Refactoring');
  db.exec('COMMIT');
} catch (err) {
  db.exec('ROLLBACK');
  throw err;
}
console.log(db.prepare('SELECT COUNT(*) AS n FROM books').get());
db.close();
```

```output
OUT
```

### 9.7 PostgreSQL with the pg package

Install and start PostgreSQL (Windows installer, or Docker: `docker run --name pg -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16`), create a database (`createdb library`), then:

```bash
npm install pg
export DATABASE_URL=postgres://postgres:secret@localhost:5432/library      # PowerShell: $env:DATABASE_URL = "..."
```

Differences from SQLite that matter in code:

| | SQLite (`better-sqlite3`) | PostgreSQL (`pg`) |
|---|---|---|
| API style | Synchronous | **Asynchronous**: always `await` |
| Placeholders | `?` | `$1, $2, ...` |
| Auto id | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INTEGER GENERATED ALWAYS AS IDENTITY` |
| Booleans / dates | `INTEGER 0/1`, `TEXT` | `BOOLEAN`, `DATE` / `TIMESTAMPTZ` |
| Result | `.all()` array | `result.rows` array, `result.rowCount` |
| New row back | `lastInsertRowid` | `INSERT ... RETURNING *` |
| Transaction | `db.transaction(fn)` | `client.query('BEGIN')` ... on **one** checked-out client |
| Error code | `err.code = 'SQLITE_CONSTRAINT_UNIQUE'` | `err.code = '23505'` |

PostgreSQL error codes to map: `23505` unique violation (**409**), `23503` foreign-key violation (**409**), `23502` not-null violation and `23514` check violation (**400**), `22P02` invalid input syntax (**400**), `42P01` table does not exist (**500**, a setup bug), `28P01` wrong password.

**File:** `pg_demo/schema.sql` *(PostgreSQL syntax)*

```sqlpostgresql
CREATE TABLE IF NOT EXISTS books (
    book_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title     TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    author    TEXT    NOT NULL CHECK (length(trim(author)) > 0),
    isbn      TEXT    UNIQUE,
    available BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(member_id) ON DELETE RESTRICT,
    loaned_on   DATE NOT NULL DEFAULT CURRENT_DATE,
    due_on      DATE NOT NULL,
    returned_on DATE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_loan ON loans(book_id) WHERE returned_on IS NULL;
```

**File:** `pg_demo/db.js` *(depends on `schema.sql`, `DATABASE_URL`)*

```javascript
const fs = require('node:fs');
const path = require('node:path');
const { Pool, types } = require('pg');

// By default pg turns DATE columns into JavaScript Date objects (time-zone surprises). Keep 'YYYY-MM-DD'.
types.setTypeParser(types.builtins.DATE, (value) => value);

const pool = new Pool({                              // a pool = a set of reusable connections
  connectionString: process.env.DATABASE_URL,
  max: 10,
});

async function init() {                              // several statements are fine when there are no parameters
  await pool.query(fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8'));
}

module.exports = { pool, init };
```

**File:** `pg_demo/library.js`

```javascript
const { pool } = require('./db');

async function addBook(title, author, isbn = null) {
  const { rows } = await pool.query(
    'INSERT INTO books (title, author, isbn) VALUES ($1, $2, $3) RETURNING *',     // RETURNING = the new row
    [title, author, isbn],
  );
  return rows[0];
}

async function getBook(id) {
  const { rows } = await pool.query('SELECT * FROM books WHERE book_id = $1', [id]);
  return rows[0] ?? null;                             // undefined -> null when there is no such book
}

async function borrowBook(bookId, memberId, days = 14) {
  const client = await pool.connect();                // a transaction must stay on ONE connection
  try {
    await client.query('BEGIN');
    const claimed = await client.query(
      'UPDATE books SET available = FALSE WHERE book_id = $1 AND available = TRUE', [bookId]);
    if (claimed.rowCount === 0) throw new Error('Book is not available');
    const { rows } = await client.query(
      'INSERT INTO loans (book_id, member_id, due_on) VALUES ($1, $2, CURRENT_DATE + $3::int) RETURNING *',
      [bookId, memberId, days],
    );
    await client.query('COMMIT');
    return rows[0];
  } catch (err) {
    await client.query('ROLLBACK');                   // undo everything since BEGIN
    throw err;
  } finally {
    client.release();                                 // ALWAYS return the connection to the pool
  }
}

async function activeLoans() {                        // a JOIN across three tables
  const { rows } = await pool.query(`
    SELECT l.loan_id, b.title, m.name AS member
    FROM loans l
    JOIN books b   USING (book_id)
    JOIN members m USING (member_id)
    WHERE l.returned_on IS NULL
    ORDER BY l.due_on`);
  return rows;
}

module.exports = { addBook, getBook, borrowBook, activeLoans };
```

**File:** `pg_demo/demo.js` *(runs everything above; needs a running PostgreSQL and `DATABASE_URL`)*

```javascript
const { pool, init } = require('./db');
const { addBook, getBook, borrowBook, activeLoans } = require('./library');

async function main() {
  await init();
  await pool.query('TRUNCATE loans, books, members RESTART IDENTITY CASCADE');     // clean slate for the demo
  const book = await addBook('Clean Code', 'Robert C. Martin', '9780132350884');
  const { rows: [member] } = await pool.query(
    'INSERT INTO members (name, email) VALUES ($1, $2) RETURNING *', ['Thandi Nkosi', 'thandi@example.com']);
  console.log('book:', book);

  const loan = await borrowBook(book.book_id, member.member_id);
  console.log('loan', loan.loan_id, '-> available now:', (await getBook(book.book_id)).available);
  console.log('active:', await activeLoans());

  const failures = {
    'second borrow': () => borrowBook(book.book_id, member.member_id),
    'duplicate isbn': () => addBook('Copy', 'Someone', '9780132350884'),
    'unknown member': () => addBook('Other', 'Someone', '9780134757599')
      .then((b) => borrowBook(b.book_id, 999)),
  };
  for (const [label, attempt] of Object.entries(failures)) {
    try {
      await attempt();
    } catch (err) {
      console.log(label.padEnd(15), err.code ?? '-', err.constraint ?? err.message);   // 23505, 23503 ...
    }
  }

  const attack = "x' OR '1'='1";                    // parameters make this harmless
  const { rows } = await pool.query('SELECT title FROM books WHERE title = $1', [attack]);
  console.log('injection attempt matched', rows.length, 'rows');
  await pool.end();                                   // close the pool so the process can exit
}
main().catch((err) => { console.error(err); process.exit(1); });
```

```output
PG_DEMO_OUT
```

An Express route on top of the same functions. In Express 5 a rejected promise reaches the error handler automatically; in Express 4 wrap the body in `try { ... } catch (err) { next(err); }`.

**File:** `pg_demo/server.js`

```javascript
const express = require('express');
const { init } = require('./db');
const { addBook, getBook } = require('./library');

const app = express();
app.use(express.json());

app.get('/books/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id < 1) return res.status(400).json({ error: 'id must be a positive whole number' });
  const book = await getBook(id);
  if (!book) return res.status(404).json({ error: `Book ${id} not found` });
  res.json(book);
});

app.post('/books', async (req, res) => {
  const { title, author, isbn = null } = req.body ?? {};
  if (!title || !author) return res.status(400).json({ error: 'title and author are required' });
  res.status(201).json(await addBook(title, author, isbn));
});

app.use((err, req, res, next) => {
  if (err.code === '23505') return res.status(409).json({ error: 'A book with that ISBN already exists' });
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

init().then(() => app.listen(3100, () => console.log('PostgreSQL API on http://localhost:3100')));
```

```bash
H="Content-Type: application/json"; W="   -> %{http_code}\n"
curl -s -w "$W" -X POST localhost:3100/books -H "$H" -d '{"title":"Refactoring","author":"Martin Fowler","isbn":"9780134757599"}'
curl -s -w "$W" -X POST localhost:3100/books -H "$H" -d '{"title":"Copy","author":"X","isbn":"9780134757599"}'
curl -s -w "$W" localhost:3100/books/1
curl -s -w "$W" localhost:3100/books/99
```

```output
PG_CURL_OUT
```

> **Warning (demo versus production):** these examples show the *mechanics*. A production system would add migrations instead of `CREATE TABLE IF NOT EXISTS` at start-up, connection error handling and retry, SSL for remote databases, least-privilege database users, backups, and structured logging.


## 10. API security

### 10.1 What each control protects against

| Concern | Risk | Control in the Library API |
|---|---|---|
| Input validation | Bad data, crashes, oversized input | `validate.js` on every write; database `CHECK` / `NOT NULL`; `express.json({ limit })` |
| SQL injection | Data theft or destruction | **Parameterised queries only** (§9.2) |
| Authentication ("who are you?") | Impersonation | Passwords hashed with **bcrypt**; **JWT** access tokens; **401** when missing or invalid |
| Authorisation ("what may you do?") | Members editing the catalogue | `requireRole('librarian', 'admin')`; **403** when the role is not allowed |
| Mass assignment | A client sends `"role": "admin"` | Only whitelisted fields are copied; registration always creates role `member` |
| Secrets | Leaked signing key | `.env` outside version control; the server refuses to start without `JWT_SECRET` |
| Brute force | Password guessing | **Rate limiting** on `/auth/login` (**429**) |
| Browser cross-origin calls | Another website calling your API with a user's browser | **CORS** allow-list |
| Error leakage | Stack traces and SQL text help attackers | Generic `500` body; details only in the server log |
| Transport | Passwords read on the network | **HTTPS** in any deployed system (usually at a reverse proxy) |
| Weak headers, vulnerable packages | Clickjacking, sniffing, known CVEs | `helmet()`; `npm audit`; commit `package-lock.json` |

> **Warning:** The code below is an *educational* implementation of these controls. It is **not** a complete production security solution: there is no refresh-token or revocation mechanism, no password reset, no account lock-out, no audit log, and no HTTPS. Say so in your README.

### 10.2 Password hashing with bcrypt

Never store or compare plain-text passwords. A bcrypt hash includes its own random **salt** and a **cost** factor that makes each guess slow. `bcryptjs` is pure JavaScript (no compiler needed) and has the same API as the native `bcrypt` package. *Standalone.*

```javascript
const bcrypt = require('bcryptjs');

(async () => {
  const hash = await bcrypt.hash('S3cure-pass!', 10);          // cost 10 = 2^10 rounds; salt generated for you
  console.log(hash.length, hash.startsWith('$2'));              // always 60 characters, "$2b$10$..."
  console.log(await bcrypt.compare('S3cure-pass!', hash));      // true
  console.log(await bcrypt.compare('wrong-pass', hash));        // false
  console.log(hash === await bcrypt.hash('S3cure-pass!', 10));  // false: a new random salt each time
})();
```

```output
OUT
```

### 10.3 JSON Web Tokens (JWT)

A JWT is `header.payload.signature`. The payload is only **encoded**, so anyone can read it: never put secrets in it. The **signature** (made with your secret) proves it was not altered, and `exp` limits its lifetime. *Standalone.*

```javascript
const jwt = require('jsonwebtoken');
const SECRET = 'demo-secret-do-not-use';

const token = jwt.sign({ sub: 7, role: 'librarian' }, SECRET, { expiresIn: '1h' });
console.log(token.split('.').length, 'parts: header.payload.signature');
const claims = jwt.verify(token, SECRET, { algorithms: ['HS256'] });     // pin the algorithm
console.log(claims.sub, claims.role, claims.exp > claims.iat);
const [header, payload, signature] = token.split('.');
console.log('anyone can read the payload:', Buffer.from(payload, 'base64url').toString());

const forged = Buffer.from(JSON.stringify({ sub: 7, role: 'admin' })).toString('base64url');
const attempts = {
  'edited payload': `${header}.${forged}.${signature}`,         // changed role, kept the old signature
  'wrong secret':   jwt.sign({ sub: 7, role: 'admin' }, 'some-other-secret'),
  'expired':        jwt.sign({ sub: 7 }, SECRET, { expiresIn: -10 }),
};
for (const [label, bad] of Object.entries(attempts)) {
  try {
    jwt.verify(bad, SECRET, { algorithms: ['HS256'] });
  } catch (err) {
    console.log(label.padEnd(15), err.message);
  }
}
```

```output
OUT
```

Generate a real secret with `node -e "console.log(require('node:crypto').randomBytes(48).toString('base64url'))"` and put it in `.env` as `JWT_SECRET=...`. Tokens are **stateless**: a role change only takes effect when the user logs in again (their old token keeps the old role until it expires).

### 10.4 Login, JWT middleware and role checks

*Depends on:* §8 (`errors.js`, `db.js`, the `users` table from the shared schema). Authentication returns **401**; authorisation returns **403**.

**File:** `library-api/src/middleware/auth.js`

```javascript
const jwt = require('jsonwebtoken');
const { ApiError } = require('../errors');

const SECRET = process.env.JWT_SECRET;
if (!SECRET) throw new Error('JWT_SECRET is not set');     // fail fast: never use a default secret

const signToken = (user) =>
  jwt.sign({ sub: user.user_id, username: user.username, role: user.role }, SECRET, { expiresIn: '1h' });

function authenticate(req, res, next) {                    // 401: "who are you?"
  const [scheme, token] = (req.get('Authorization') ?? '').split(' ');
  if (scheme !== 'Bearer' || !token) {
    throw new ApiError(401, 'Missing or malformed Authorization header');
  }
  try {
    req.user = jwt.verify(token, SECRET, { algorithms: ['HS256'] });     // checks signature AND expiry
  } catch {
    throw new ApiError(401, 'Invalid or expired token');
  }
  next();
}

const requireRole = (...roles) => (req, res, next) => {    // 403: "I know who you are, but not allowed"
  if (!roles.includes(req.user.role)) throw new ApiError(403, 'You do not have permission to do that');
  next();
};

module.exports = { signToken, authenticate, requireRole };
```

**File:** `library-api/src/routes/auth.js`

```javascript
const express = require('express');
const bcrypt = require('bcryptjs');
const { ApiError } = require('../errors');
const { signToken, authenticate } = require('../middleware/auth');

const COST = 10;                                           // bcrypt work factor: 10-12 is typical
const DUMMY_HASH = bcrypt.hashSync('not-a-real-password', COST);   // used so unknown users cost the same time

module.exports = (db) => {
  const router = express.Router();

  router.post('/register', async (req, res) => {
    const { username, password } = req.body ?? {};
    const errors = [];
    if (typeof username !== 'string' || !/^[A-Za-z0-9_]{3,30}$/.test(username)) {
      errors.push('username must be 3-30 letters, digits or underscores');
    }
    if (typeof password !== 'string' || password.length < 8 || password.length > 72) {
      errors.push('password must be 8-72 characters');         // bcrypt reads at most 72 bytes
    }
    if (errors.length) throw new ApiError(400, 'Validation failed', errors);

    const hash = await bcrypt.hash(password, COST);
    const info = db.prepare('INSERT INTO users (username, password_hash) VALUES (?, ?)')
      .run(username, hash);                                  // UNIQUE username -> 409 via errorHandler
    res.status(201).json({ user_id: info.lastInsertRowid, username, role: 'member' });   // role is fixed
  });

  router.post('/login', async (req, res) => {
    const { username, password } = req.body ?? {};
    if (typeof username !== 'string' || typeof password !== 'string') {
      throw new ApiError(400, 'username and password are required');
    }
    const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
    const matches = await bcrypt.compare(password, user ? user.password_hash : DUMMY_HASH);
    if (!user || !matches) {                                 // same message whichever part was wrong
      throw new ApiError(401, 'Invalid username or password');
    }
    res.json({ access_token: signToken(user), token_type: 'Bearer', expires_in: 3600 });
  });

  router.get('/me', authenticate, (req, res) => {
    res.json({ username: req.user.username, role: req.user.role });
  });

  return router;
};
```

**File:** `library-api/src/app.js` *(replaces the §8.5 version: adds helmet, CORS, rate limiting and the guards)*

```javascript
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { notFoundHandler, errorHandler } = require('./errors');
const { authenticate, requireRole } = require('./middleware/auth');

function createApp(db, { loginLimit = 10 } = {}) {
  const app = express();
  app.use(helmet());                                         // secure response headers
  app.use(cors({ origin: ['http://localhost:5173'] }));      // only this front end may call from a browser
  app.use(express.json({ limit: '100kb' }));                 // refuse huge request bodies

  app.use('/auth/login', rateLimit({                         // slow down password guessing: 429
    windowMs: 15 * 60 * 1000, limit: loginLimit, standardHeaders: true, legacyHeaders: false,
    message: { error: 'Too many login attempts, try again later' },
  }));

  app.get('/', (req, res) => res.json({ message: 'Library API is running' }));
  app.get('/health', (req, res) => res.json({ status: 'ok' }));
  app.use('/auth', require('./routes/auth')(db));

  // Reading the catalogue is public; changing it needs a librarian or admin.
  // These guards register first: if they call next(), the books router below handles the request.
  const staff = [authenticate, requireRole('librarian', 'admin')];
  app.post('/books', ...staff);
  app.put('/books/:id', ...staff);
  app.patch('/books/:id', ...staff);
  app.delete('/books/:id', ...staff);
  app.use('/books', require('./routes/books')(db));

  // Members and loans hold personal data: signed-in staff only.
  app.use('/members', ...staff, require('./routes/members')(db));
  app.use('/loans', ...staff, require('./routes/loans')(db));

  app.use(notFoundHandler);
  app.use(errorHandler);
  return app;
}

module.exports = { createApp };
```

**File:** `library-api/scripts/promote.js` *(clients can never choose a role; an administrator promotes users out-of-band)*

```javascript
// usage: node scripts/promote.js thandi librarian
const Database = require('better-sqlite3');
const [username, role] = process.argv.slice(2);
const db = new Database(process.env.DB_FILE ?? 'library.db');
const { changes } = db.prepare('UPDATE users SET role = ? WHERE username = ?').run(role, username);
console.log(changes ? `${username} is now ${role}` : `No such user: ${username}`);
db.close();
```

With the secured app running (`npm run dev`), the whole flow (bash; the token is read with Node, so `jq` is not needed):

```bash
H="Content-Type: application/json"; W="   -> %{http_code}\n"; A=localhost:3000
login() { curl -s -X POST $A/auth/login -H "$H" -d '{"username":"thandi","password":"S3cure-pass!"}' \
          | node -pe "JSON.parse(require('fs').readFileSync(0, 'utf8')).access_token"; }

curl -s -w "$W" -X POST $A/auth/register -H "$H" -d '{"username":"thandi","password":"S3cure-pass!"}'
curl -s -w "$W" -X POST $A/auth/login -H "$H" -d '{"username":"thandi","password":"wrong-password"}'
AUTH="Authorization: Bearer $(login)"
curl -s -w "$W" $A/auth/me -H "$AUTH"
curl -s -w "$W" $A/members                                                      # no token at all
curl -s -w "$W" -X POST $A/books -H "$H" -H "$AUTH" -d '{"title":"Clean Code","author":"R. Martin"}'
node scripts/promote.js thandi librarian                                        # done by an administrator
AUTH="Authorization: Bearer $(login)"                                           # log in again: new role
curl -s -w "$W" -X POST $A/books -H "$H" -H "$AUTH" -d '{"title":"Clean Code","author":"R. Martin"}'
curl -s -w "$W" $A/books
```

```output
SEC_FLOW_OUT
```

### 10.5 CORS and rate limiting

**CORS** (Cross-Origin Resource Sharing) is enforced by **browsers**, not by your server: it decides whether JavaScript on `https://app.example` may read responses from `https://api.example`. `curl`, Postman and other servers ignore it, so it is **not** a substitute for authentication. Use an allow-list of origins; never `origin: '*'` together with credentials. A *preflight* `OPTIONS` request precedes non-simple calls; the `cors` package answers it for you.

```bash
curl -s -i -X OPTIONS localhost:3000/books -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" | grep -i "^access-control-allow-origin"
curl -s -i -X OPTIONS localhost:3000/books -H "Origin: http://evil.example" \
     -H "Access-Control-Request-Method: POST" | grep -ic "^access-control-allow-origin"
```

```output
CORS_OUT
```

**Rate limiting** (`express-rate-limit`) answers **429 Too Many Requests** once a client exceeds `limit` requests per `windowMs`. It is applied to `/auth/login` above; the tests in §11 prove it. Behind a reverse proxy (nginx, a cloud load balancer) also call `app.set('trust proxy', 1)` so the limiter sees the real client address.

### 10.6 Errors must not leak, and a final checklist

| Do not send the client | Send instead | Where |
|---|---|---|
| `{"error":"SQLITE_ERROR: no such column: titel","stack":"at Database.prepare (...)"}` | `{"error":"Internal server error"}` | `errorHandler` logs the real error with `console.error` |
| "No user called thandi" / "Wrong password for thandi" | `Invalid username or password` (identical for both) | `routes/auth.js` |
| Which constraint failed (`UNIQUE constraint failed: users.username`) | `A record with that value already exists` | `errorHandler` |

- [ ] Every query uses parameters (`?` / `$1`); column names come from an allow-list
- [ ] Passwords are hashed with bcrypt; never logged, never returned
- [ ] `JWT_SECRET` and database passwords live in `.env`, which is listed in `.gitignore`
- [ ] Tokens expire; the algorithm is pinned in `jwt.verify`
- [ ] Role comes from the database, never from the request body
- [ ] Protected routes return 401 (not signed in) or 403 (not allowed), tested with and without a token
- [ ] Login is rate limited; CORS lists specific origins; `helmet()` is on
- [ ] The 500 response is generic; `npm audit` was run

## 11. Testing the API

### 11.1 What to test

| Kind | Example in the Library API | Tool |
|---|---|---|
| Unit test (pure function) | `calculateFine(3)` is 15; negative input throws | `node:test` / `pytest` |
| Success response | `POST /books` returns **201** with the new book | Supertest / `TestClient` |
| Invalid request | Blank title returns **400** (FastAPI **422**) with details | Supertest |
| Missing resource | `GET /books/999999` returns **404** | Supertest |
| Authentication / authorisation | No token **401**; member role **403**; librarian **201** | Supertest |
| Database behaviour | Duplicate ISBN **409**; failed borrow leaves the book available; foreign keys enforced | Supertest + `:memory:` database |
| Manual exploration | Try each endpoint and capture screenshots | curl, Postman |

### 11.2 curl and PowerShell

```bash
curl -i localhost:3000/books/1                        # -i: show status line and headers
curl -s -o /dev/null -w "%{http_code}\n" localhost:3000/books/999     # status code only
curl -X POST localhost:3000/books -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
     --data-binary "@book.json"                       # JSON from a file: no quoting problems
curl -v localhost:3000/health                         # -v: full request and response, for debugging
```

```powershell
# Windows PowerShell: use ConvertTo-Json instead of escaping quotes by hand.
$base  = "http://localhost:3000"
$login = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" `
         -Body (@{ username = "thandi"; password = "S3cure-pass!" } | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$book = @{ title = "Clean Code"; author = "Robert C. Martin" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/books" -Headers $headers -ContentType "application/json" -Body $book
Invoke-RestMethod "$base/books?available=true" | Format-Table book_id, title, author
try { Invoke-RestMethod "$base/books/999" } catch { $_.Exception.Response.StatusCode.value__ }   # 404
```

> **Note:** PowerShell and Postman examples in this manual could not be executed in the environment used to verify it (no PowerShell or Postman available). They follow the documented behaviour of those tools; test them once before the exam.

### 11.3 Postman

1. **New environment** "Library" with variables `baseUrl` = `http://localhost:3000` and an empty `token`. Select it (top right).
2. **New collection** "Library API". Add requests using `{{baseUrl}}/books`, `{{baseUrl}}/loans`, and so on.
3. `POST` requests: *Body* → *raw* → **JSON**; Postman sets `Content-Type` for you.
4. Protected requests: *Authorization* tab → **Bearer Token** → `{{token}}` (set it once on the collection and let requests inherit).
5. *Tests* tab on **POST /auth/login** stores the token; the tests on **POST /books** check the response; *Collection Runner* runs them all in order and shows pass/fail (screenshot it).

```javascript
// Tests tab of  POST {{baseUrl}}/auth/login
pm.test('login returns 200', () => pm.response.to.have.status(200));
const body = pm.response.json();
pm.test('response contains a token', () => pm.expect(body.access_token).to.be.a('string'));
pm.environment.set('token', body.access_token);              // later requests use {{token}}

// Tests tab of  POST {{baseUrl}}/books
pm.test('201 Created with a Location header', () => {
  pm.response.to.have.status(201);
  pm.response.to.have.header('Location');
});
pm.test('body contains the new book', () => {
  const book = pm.response.json();
  pm.expect(book).to.have.property('book_id');
  pm.expect(book.available).to.eql(true);
});
```

### 11.4 Unit tests with the built-in Node test runner

`node --test` finds `test/` folders and `*.test.js` files; no installation needed. *Depends on:* `src/rules.js`.

**File:** `library-api/test/rules.test.js`

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const { daysLate, calculateFine, addDays } = require('../src/rules');

test('calculateFine multiplies days by the daily rate', () => {
  assert.equal(calculateFine(0), 0);
  assert.equal(calculateFine(3, 5), 15);
});

test('calculateFine rejects negative input', () => {
  assert.throws(() => calculateFine(-1), RangeError);
});

test('daysLate is 0 when early or on time, and counts whole days when late', () => {
  assert.equal(daysLate('2026-11-05', '2026-11-03'), 0);
  assert.equal(daysLate('2026-11-05', '2026-11-05'), 0);
  assert.equal(daysLate('2026-11-05', '2026-11-08'), 3);
});

test('addDays crosses month boundaries', () => {
  assert.equal(addDays('2026-10-30', 3), '2026-11-02');
});
```

### 11.5 Database tests

Test the rules the database enforces *itself*, independent of your routes. *Depends on:* `src/db.js`.

**File:** `library-api/test/db.test.js`

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const { openDb } = require('../src/db');

function seeded(t) {
  const db = openDb(':memory:');                               // empty, private to this test
  t.after(() => db.close());
  db.exec(`INSERT INTO books (title, author) VALUES ('Clean Code', 'R. Martin'), ('Refactoring', 'M. Fowler');
           INSERT INTO members (name, email) VALUES ('Thandi', 'thandi@example.com');`);
  return db;
}
const loan = (db, bookId, memberId = 1) => db
  .prepare("INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (?, ?, '2026-11-01', '2026-11-15')")
  .run(bookId, memberId);

test('foreign keys are enforced', (t) => {
  const db = seeded(t);
  assert.throws(() => loan(db, 999), /FOREIGN KEY constraint failed/);
});

test('a book cannot have two active loans (partial unique index)', (t) => {
  const db = seeded(t);
  loan(db, 1);
  assert.throws(() => loan(db, 1), /UNIQUE constraint failed/);
  db.prepare("UPDATE loans SET returned_on = '2026-11-02' WHERE book_id = 1").run();
  assert.doesNotThrow(() => loan(db, 1));                      // allowed again once it was returned
});

test('CHECK constraint rejects a blank title', (t) => {
  const db = seeded(t);
  assert.throws(() => db.prepare("INSERT INTO books (title, author) VALUES ('  ', 'X')").run(), /CHECK constraint failed/);
});

test('a failed transaction rolls everything back', (t) => {
  const db = seeded(t);
  const borrow = db.transaction(() => {
    db.prepare('UPDATE books SET available = 0 WHERE book_id = 2').run();
    loan(db, 2, 999);                                          // member 999 does not exist -> throws
  });
  assert.throws(borrow, /FOREIGN KEY/);
  assert.equal(db.prepare('SELECT available FROM books WHERE book_id = 2').pluck().get(), 1);
});
```

### 11.6 API tests with Supertest

Supertest calls the Express app **directly, without opening a port**. Each test builds a fresh app on an empty in-memory database. *Depends on:* the §8 files plus the §10 files (authentication), and `npm install -D supertest`.

**File:** `library-api/test/api.test.js`

```javascript
process.env.JWT_SECRET ??= 'test-secret';                    // must be set BEFORE the app is loaded
const test = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const jwt = require('jsonwebtoken');
const { openDb } = require('../src/db');
const { createApp } = require('../src/app');
const { today, addDays } = require('../src/rules');

function setup(t) {                                          // fresh app + empty database per test
  const db = openDb(':memory:');
  t.after(() => db.close());
  return { db, app: createApp(db, { loginLimit: 3 }) };
}

async function auth(app, db, role = 'librarian') {           // register, promote in the DB, log in
  const username = `user_${role}`;
  await request(app).post('/auth/register').send({ username, password: 'S3cure-pass!' }).expect(201);
  db.prepare('UPDATE users SET role = ? WHERE username = ?').run(role, username);
  const res = await request(app).post('/auth/login').send({ username, password: 'S3cure-pass!' });
  return { Authorization: `Bearer ${res.body.access_token}` };
}

const BOOK = { title: 'Clean Code', author: 'Robert C. Martin', isbn: '9780132350884' };
const MEMBER = { name: 'Thandi Nkosi', email: 'thandi@example.com' };

test('create a book: 201, Location header and body', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  const res = await request(app).post('/books').set(staff).send(BOOK);
  assert.equal(res.status, 201);
  assert.equal(res.headers.location, '/books/1');
  assert.deepEqual(res.body, { book_id: 1, ...BOOK, available: true });
  assert.equal((await request(app).get('/books/1')).status, 200);       // reading is public
});

test('invalid input: 400 with a list of details', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  const res = await request(app).post('/books').set(staff).send({ title: ' ', author: 'X', isbn: 'abc' });
  assert.equal(res.status, 400);
  assert.equal(res.body.error, 'Validation failed');
  assert.equal(res.body.details.length, 2);
});

test('malformed JSON: 400; unknown id: 404; bad id: 400; unknown route: 404', async (t) => {
  const { app } = setup(t);
  const bad = await request(app).post('/auth/login').set('Content-Type', 'application/json').send('{oops');
  assert.equal(bad.status, 400);
  assert.equal((await request(app).get('/books/999999')).status, 404);
  assert.equal((await request(app).get('/books/abc')).status, 400);
  assert.equal((await request(app).get('/nothing')).status, 404);
});

test('duplicate ISBN: 409', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  await request(app).post('/books').set(staff).send(BOOK).expect(201);
  await request(app).post('/books').set(staff).send(BOOK).expect(409);
});

test('PATCH changes only the fields sent; PUT replaces (isbn reset)', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  await request(app).post('/books').set(staff).send(BOOK);
  const patched = await request(app).patch('/books/1').set(staff).send({ title: 'Clean Code 2e' });
  assert.equal(patched.body.author, BOOK.author);
  assert.equal(patched.body.isbn, BOOK.isbn);
  const put = await request(app).put('/books/1').set(staff).send({ title: 'Clean Code', author: 'R. Martin' });
  assert.equal(put.body.isbn, null);
  await request(app).patch('/books/1').set(staff).send({}).expect(400);
});

test('authentication and authorisation on protected routes', async (t) => {
  const { app, db } = setup(t);
  await request(app).post('/books').send(BOOK).expect(401);                         // no token
  await request(app).get('/members').expect(401);
  const member = await auth(app, db, 'member');
  await request(app).post('/books').set(member).send(BOOK).expect(403);             // wrong role
  const forged = jwt.sign({ sub: 1, role: 'admin' }, 'some-other-secret');
  await request(app).get('/members').set('Authorization', `Bearer ${forged}`).expect(401);
  const staff = await auth(app, db, 'librarian');
  await request(app).get('/members').set(staff).expect(200);
});

test('login: wrong password and unknown user look identical; the limiter returns 429', async (t) => {
  const { app, db } = setup(t);
  await auth(app, db, 'member');
  const wrong = await request(app).post('/auth/login').send({ username: 'user_member', password: 'nope-nope-1' });
  const unknown = await request(app).post('/auth/login').send({ username: 'ghost', password: 'nope-nope-1' });
  assert.equal(wrong.status, 401);
  assert.deepEqual(wrong.body, unknown.body);
  const last = await request(app).post('/auth/login').send({ username: 'ghost', password: 'nope-nope-1' });
  assert.equal(last.status, 429);                                                    // the 4th attempt
});

test('borrow, conflict, return, and the active-loans list', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  await request(app).post('/books').set(staff).send(BOOK);
  await request(app).post('/members').set(staff).send(MEMBER).expect(201);
  const loan = await request(app).post('/loans').set(staff).send({ book_id: 1, member_id: 1 });
  assert.equal(loan.status, 201);
  assert.equal(loan.body.due_on, addDays(today(), 14));
  await request(app).post('/loans').set(staff).send({ book_id: 1, member_id: 1 }).expect(409);
  assert.equal((await request(app).get('/loans?active=true').set(staff)).body.length, 1);
  assert.equal((await request(app).get('/members/1/loans').set(staff)).body.length, 1);
  const back = await request(app).post('/loans/1/return').set(staff);
  assert.deepEqual([back.status, back.body.days_late, back.body.fine], [200, 0, 0]);
  await request(app).post('/loans/1/return').set(staff).expect(409);
  assert.equal((await request(app).get('/loans?active=true').set(staff)).body.length, 0);
});

test('a late return is fined R5 per day', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  await request(app).post('/books').set(staff).send(BOOK);
  await request(app).post('/members').set(staff).send(MEMBER);
  await request(app).post('/loans').set(staff).send({ book_id: 1, member_id: 1 });
  db.prepare('UPDATE loans SET due_on = ? WHERE loan_id = 1').run(addDays(today(), -3));    // 3 days overdue
  const back = await request(app).post('/loans/1/return').set(staff);
  assert.deepEqual([back.body.days_late, back.body.fine], [3, 15]);
});

test('database rules: failed borrow changes nothing; books with history cannot be deleted', async (t) => {
  const { app, db } = setup(t);
  const staff = await auth(app, db);
  await request(app).post('/books').set(staff).send(BOOK);
  await request(app).post('/loans').set(staff).send({ book_id: 1, member_id: 99 }).expect(404);
  assert.equal((await request(app).get('/books/1')).body.available, true);          // rolled back
  await request(app).post('/members').set(staff).send(MEMBER);
  await request(app).post('/loans').set(staff).send({ book_id: 1, member_id: 1 }).expect(201);
  await request(app).delete('/books/1').set(staff).expect(409);
});

test('security headers and CORS allow-list', async (t) => {
  const { app } = setup(t);
  const ok = await request(app).get('/health').set('Origin', 'http://localhost:5173');
  assert.equal(ok.headers['access-control-allow-origin'], 'http://localhost:5173');
  assert.equal(ok.headers['x-content-type-options'], 'nosniff');
  assert.equal(ok.headers['x-powered-by'], undefined);                              // helmet removes it
  const other = await request(app).get('/health').set('Origin', 'http://evil.example');
  assert.equal(other.headers['access-control-allow-origin'], undefined);
});
```

Run all tests (output below is from the full suite; the order of lines may vary):

```bash
npm test          # same as: node --test
```

```output
TEST_OUT
```

> **Common mistake:** tests that share one database or depend on running order. Build the app and an empty `:memory:` database **inside every test**, as `setup()` does. If a test fails with `JWT_SECRET is not set`, the `process.env.JWT_SECRET` line must come before the first `require` of the app.

### 11.7 The same tests in Jest

Jest is an alternative runner with `describe` / `test` / `expect`. Install with `npm install -D jest`, run with `npx jest`. The Jest file below ends in `.spec.js` and sits outside `test/` so that `node --test` does not pick it up. *Depends on:* the same app files and Supertest.

**File:** `library-api/jest_demo/api.spec.js`

```javascript
process.env.JWT_SECRET = 'test-secret';
const request = require('supertest');
const { openDb } = require('../src/db');
const { createApp } = require('../src/app');
const { calculateFine } = require('../src/rules');

let db;
let app;
beforeEach(() => {                                           // fresh database for every test
  db = openDb(':memory:');
  app = createApp(db);
});
afterEach(() => db.close());

describe('fine calculation', () => {
  test('3 days late costs R15', () => expect(calculateFine(3)).toBe(15));
  test('negative days throw', () => expect(() => calculateFine(-1)).toThrow(RangeError));
});

describe('books API', () => {
  test('GET /books is public and starts empty', async () => {
    const res = await request(app).get('/books');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });

  test('POST /books without a token is 401', async () => {
    const res = await request(app).post('/books').send({ title: 'X', author: 'Y' });
    expect(res.status).toBe(401);
    expect(res.body).toHaveProperty('error');
  });

  test('GET /books/999 is 404', async () => {
    expect((await request(app).get('/books/999')).status).toBe(404);
  });
});
```

```bash
npx jest jest_demo
```

```output
JEST_OUT
```

| `node:test` | Jest | Meaning |
|---|---|---|
| `test('name', fn)` | `test('name', fn)` | One test |
| `assert.equal(a, b)` | `expect(a).toBe(b)` | Strict equality |
| `assert.deepEqual(a, b)` | `expect(a).toEqual(b)` | Compare objects/arrays |
| `assert.throws(fn)` | `expect(fn).toThrow()` | An error is expected |
| `t.after(fn)` | `afterEach(fn)` | Clean-up |

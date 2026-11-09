## 6. Node.js fundamentals

### 6.1 What Node.js is, and how it differs from browser JavaScript

Node.js is a JavaScript **runtime** built on Chrome's V8 engine. It runs JavaScript outside the browser, so you can build servers, APIs and command-line tools. Your JavaScript runs on **one thread**; slow work (files, network, database) is *non-blocking*: you start it, Node continues, and your code resumes when the result arrives. That is why you `await` slow operations instead of waiting in a loop.

| | Browser JavaScript | Node.js |
|---|---|---|
| Global object | `window` | `globalThis` (`global`) |
| Page access | `document`, DOM, `alert` | none |
| Files, OS | sandboxed, no direct access | `fs`, `path`, `os`, `process` |
| Servers | cannot listen on a port | `http`, Express, etc. |
| Modules | ES modules (`import`) | CommonJS (`require`) **and** ES modules |
| Packages | CDN / bundler | `npm` and `node_modules` |
| `fetch` | yes | yes (Node 18+) |

```bash
node -v                        # version check (this manual: 22 LTS)
node                           # REPL: type JavaScript; press Ctrl+C twice to quit
node app.js                    # run a file
node --watch app.js            # restart automatically when files change
node --env-file=.env app.js    # load environment variables from .env (Node 20.6+)
node --test                    # built-in test runner: runs test/ folders and *.test.js files
node --check app.js            # syntax check only; runs nothing
```

### 6.2 npm, package.json and package-lock.json

```bash
mkdir library-api && cd library-api
npm init -y                           # create package.json with defaults
npm install express better-sqlite3    # add to "dependencies"; creates node_modules/ and package-lock.json
npm install -D supertest              # -D = "devDependencies": needed only for development and testing
npm install                           # install everything listed in package.json
npm ci                                # clean install of the EXACT versions in package-lock.json
npm start                             # runs the "start" script    (npm run dev / npm test the same way)
npm ls --depth=0                      # list installed top-level packages
```

**File:** `library-api/package.json`

```json
{
  "name": "library-api",
  "version": "1.0.0",
  "private": true,
  "description": "Library Management API (Express 5 + SQLite)",
  "main": "src/server.js",
  "scripts": {
    "start": "node --env-file=.env src/server.js",
    "dev": "node --watch --env-file=.env src/server.js",
    "test": "node --test"
  },
  "dependencies": {
    "bcryptjs": "^3.0.3",
    "better-sqlite3": "^13.0.3",
    "cors": "^2.8.6",
    "express": "^5.3.0",
    "express-rate-limit": "^8.7.3",
    "helmet": "^8.3.0",
    "jsonwebtoken": "^9.0.3"
  },
  "devDependencies": {
    "supertest": "^7.3.1"
  }
}
```

| Item | What it is | Rule |
|---|---|---|
| `dependencies` / `devDependencies` | Packages needed to **run** / only to **develop and test** | Use `npm install -D` for test tools |
| `"^5.3.0"` | Any 5.x version at or above 5.3.0 (`~5.3.0` = patches only) | Major versions can break your code |
| `package-lock.json` | The exact versions and checksums that were installed | Commit it; never edit it by hand; `npm ci` obeys it |
| `node_modules/` | Downloaded packages (can be huge) | **Never commit**; recreate with `npm install` |
| `scripts` | Named commands: `npm start`, `npm test`, `npm run dev` | Put the run and test commands here for your README |

**File:** `library-api/.gitignore`

```text
node_modules/
.env
*.db
```

### 6.3 CommonJS and ES modules

| | CommonJS (this manual's Node project) | ES modules |
|---|---|---|
| Import | `const x = require('./x.js')` | `import x from './x.js'` |
| Export | `module.exports = { add }` | `export function add() {}` / `export default` |
| File type | `.js` (default) or `.cjs` | `.mjs`, or `.js` with `"type": "module"` in `package.json` |
| Current folder | `__dirname`, `__filename` | `import.meta.dirname`, `import.meta.filename` (Node 20.11+) |
| Top-level `await` | not allowed | allowed |
| Relative imports | extension optional | extension **required** |

**File:** `modules_demo/math.cjs`

```javascript
function add(a, b) { return a + b; }
const VAT_RATE = 0.15;
module.exports = { add, VAT_RATE };
```

**File:** `modules_demo/main.cjs`

```javascript
const { add, VAT_RATE } = require('./math.cjs');
const path = require('node:path');                         // built-in modules use the node: prefix
console.log(add(2, 3), VAT_RATE, path.basename(__filename));
```

**File:** `modules_demo/math.mjs`

```javascript
export function add(a, b) { return a + b; }
export const VAT_RATE = 0.15;
```

**File:** `modules_demo/main.mjs`

```javascript
import { add, VAT_RATE } from './math.mjs';                // the extension is REQUIRED in ESM
import path from 'node:path';
console.log(add(2, 3), VAT_RATE, path.basename(import.meta.filename));
```

<!-- run: modules_demo | node main.cjs && node main.mjs -->
```output
OUT
```

> **Common mistake:** `Cannot use import statement outside a module` means an ES-module file is being run as CommonJS: rename it `.mjs` or add `"type": "module"`. `require is not defined in ES module scope` is the opposite mistake.

### 6.4 Variables, functions and arrow functions

*Standalone.*

```javascript
const title = 'Clean Code';           // const: cannot be reassigned (use by default)
let copies = 3;                       // let: can be reassigned (var is legacy: avoid)
copies += 1;

function calculateFine(daysLate, finePerDay = 5) {         // default parameter
  if (daysLate < 0 || finePerDay < 0) throw new RangeError('Values cannot be negative');
  return daysLate * finePerDay;
}
const isOverdue = (due, today) => today > due;             // arrow function, implicit return
const describe = ({ title, available }) =>                  // destructured parameter, template literal
  `${title} is ${available ? 'available' : 'on loan'}`;

console.log(calculateFine(3), isOverdue('2026-11-01', '2026-11-03'));
console.log(describe({ title, available: false }), copies);
console.log(typeof title, 0.1 + 0.2 === 0.3, '5' + 3, '5' - 3, 5 === '5', null ?? 'default');
try { calculateFine(-1); } catch (err) { console.log(`${err.name}: ${err.message}`); }
```

```output
OUT
```

> **Common mistake:** `==` converts types (`5 == '5'` is true); always use `===`. `??` supplies a default only for `null`/`undefined`, whereas `||` also replaces `0` and `''`.

### 6.5 Arrays, objects and destructuring

*Standalone.* These array methods replace most loops in API code.

```javascript
const books = [
  { id: 1, title: 'Clean Code', available: true, pages: 464 },
  { id: 2, title: 'Refactoring', available: false, pages: 448 },
  { id: 3, title: 'The Pragmatic Programmer', available: true, pages: 352 },
];

const titles = books.map((b) => b.title);                       // transform every item
const free = books.filter((b) => b.available);                  // keep matches
const one = books.find((b) => b.id === 2);                      // first match, or undefined
console.log(titles.length, free.length, one.title);
console.log(books.some((b) => b.pages > 450), books.every((b) => b.available));
console.log(books.reduce((sum, b) => sum + b.pages, 0));        // fold into one value

const sorted = [...books].sort((a, b) => a.title.localeCompare(b.title));   // copy first: sort() mutates
const { title, ...rest } = books[0];                            // destructuring + rest
const updated = { ...books[0], available: false };              // spread: copy with a change
console.log(sorted[0].title, title, Object.keys(rest), updated.available, books[0].available);
console.log(books[9]?.title ?? 'no such book');                 // optional chaining: no crash on undefined
for (const [i, b] of books.entries()) if (b.available) console.log(i, b.title);
```

```output
OUT
```

### 6.6 Environment variables

Configuration and secrets belong in the environment, not in source code. *Depends on:* the two files below, in one folder.

**File:** `env_demo/.env`

```ini
PORT=4000
DB_FILE=library.db
JWT_SECRET=change-me-in-real-life
```

**File:** `env_demo/show_env.js`

```javascript
const port = Number(process.env.PORT ?? 3000);          // env values are ALWAYS strings: convert them
const dbFile = process.env.DB_FILE ?? 'library.db';     // default when not set
const secret = process.env.JWT_SECRET;
if (!secret) throw new Error('JWT_SECRET is missing');  // fail fast on required secrets
console.log({ port, dbFile, hasSecret: Boolean(secret) });   // never print the secret itself
console.log('args:', process.argv.slice(2));            // command-line arguments after the filename
```

<!-- run: env_demo | node --env-file=.env show_env.js one two -->
```output
OUT
```

Without a `.env` file, set variables per command: bash `PORT=5000 node app.js`; PowerShell `$env:PORT = "5000"; node app.js`; Windows cmd `set PORT=5000 && node app.js`. On Node older than 20.6, run `npm install dotenv` and put `require('dotenv').config();` on the first line.

### 6.7 Asynchronous JavaScript: promises, async/await, try/catch

*Standalone.* A **Promise** is a value that arrives later. `await` pauses *this function* (not the whole program) until it settles.

```javascript
function fetchBook(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {                                   // pretend this is a database call
      if (id > 0) resolve({ id, title: `Book ${id}` });
      else reject(new Error('invalid id'));
    }, 20);
  });
}

async function main() {                                  // `await` only works inside async functions
  console.log(fetchBook(1));                             // MISTAKE: no await -> a pending Promise
  const a = await fetchBook(1);
  console.log('await:', a.title);

  await fetchBook(2).then((b) => console.log('then:', b.title));    // older .then() style

  const [b, c] = await Promise.all([fetchBook(3), fetchBook(4)]);   // run together, wait for both
  console.log('parallel:', b.title, c.title);

  try {
    await fetchBook(-1);                                 // a rejected promise throws at the await
  } catch (err) {
    console.log('caught:', err.message);
  } finally {
    console.log('finally always runs');
  }
}
main();
```

```output
OUT
```

> **Common mistake:** forgetting `await` gives you a `Promise` object instead of the data (`undefined` properties, `[object Promise]` in output). Also never leave a promise un-awaited without a `.catch()`; in Node 22 an unhandled rejection stops the process.

### 6.8 Working with JSON

*Standalone.*

```javascript
const text = '{"title":"Clean Code","available":true}';
const book = JSON.parse(text);                                // string -> object
console.log(book.title, typeof book.available);
console.log(JSON.stringify({ id: 1, tags: ['a'], skip: undefined, when: new Date(0) }));
console.log(JSON.stringify(book, null, 2));                   // pretty-print with 2 spaces
try {
  JSON.parse('{bad json}');                                   // invalid JSON throws SyntaxError
} catch (err) {
  console.log(err.name);
}
```

```output
OUT
```

### 6.9 File system basics

*Standalone.* Use the promise-based API (`node:fs/promises`) with `await`; build paths with `path.join`.

```javascript
const fs = require('node:fs/promises');
const path = require('node:path');

async function main() {
  const dir = path.join(__dirname, 'data_demo');              // __dirname = this file's folder (CommonJS)
  await fs.mkdir(dir, { recursive: true });                   // no error if it already exists
  const file = path.join(dir, 'books.json');

  await fs.writeFile(file, JSON.stringify([{ id: 1, title: 'Clean Code' }], null, 2), 'utf8');
  const books = JSON.parse(await fs.readFile(file, 'utf8'));
  books.push({ id: 2, title: 'Refactoring' });
  await fs.writeFile(file, JSON.stringify(books, null, 2));   // write back the whole file
  await fs.appendFile(path.join(dir, 'log.txt'), 'started\n');
  console.log((await fs.readdir(dir)).sort(), books.length);

  try {
    await fs.readFile(path.join(dir, 'missing.txt'), 'utf8');
  } catch (err) {
    console.log(err.code);                                    // ENOENT = no such file or directory
  }
  await fs.rm(dir, { recursive: true, force: true });         // clean up
}
main();
```

```output
OUT
```

## 7. Express fundamentals

### 7.1 Create a project and start a server

```bash
mkdir library-api && cd library-api
npm init -y
npm install express           # Express 5.x
```

**File:** `express_demo/hello.js`

```javascript
const express = require('express');
const app = express();                              // 1. create the application
const PORT = process.env.PORT ?? 3000;

app.get('/', (req, res) => {                        // 2. route = method + path + handler(req, res)
  res.json({ message: 'Library API is running' });  //    send JSON (sets Content-Type, status 200)
});

app.listen(PORT, () => console.log(`Listening on http://localhost:${PORT}`));   // 3. start
```

Run `node hello.js`, then in another terminal `curl localhost:3000/`:

```output
HELLO_OUT
```

> **Common mistake:** `EADDRINUSE` = the port is taken (an old server is still running); stop it or change `PORT`. `Cannot GET /thing` = no route for that method and path (check spelling, method and the mount prefix).

### 7.2 Where request data lives

| Data | Express | Example request | You receive |
|---|---|---|---|
| Path parameter | `req.params.id` | `GET /books/5` | `'5'` (a **string**; convert and validate it) |
| Query string | `req.query.q` | `GET /books?q=code&available=true` | `'code'`, `'true'` (strings; repeated keys become arrays) |
| JSON body | `req.body` (after `express.json()`) | `POST` with `Content-Type: application/json` | an object; **`undefined` in Express 5 if no body was sent** |
| Header | `req.get('Authorization')` | `Authorization: Bearer abc` | `'Bearer abc'` |
| Method / URL | `req.method`, `req.originalUrl` | | `'GET'`, `'/books?q=code'` |

| Response | Effect |
|---|---|
| `res.json(obj)` | Send JSON, status 200 unless set before |
| `res.status(201).json(obj)` | Set the status, then send JSON |
| `res.status(204).end()` | Success with no body (use for DELETE) |
| `res.location('/books/7')` | Set the `Location` header (use after 201) |
| `res.set('X-Name', 'v')` | Set any header |
| `res.send('text')` | Send text or HTML |

> **Common mistake:** `Cannot set headers after they are sent` (`ERR_HTTP_HEADERS_SENT`) means a handler sent two responses. When you answer early, write `return res.status(404).json(...)`.

### 7.3 A complete in-memory API: students

A full CRUD API in one file; the same patterns are reused in the library project (§8). *Standalone.*

**File:** `express_demo/students.js`

```javascript
const express = require('express');
const app = express();

app.use(express.json());                                   // 1) parse JSON bodies into req.body
app.use((req, res, next) => {                              // 2) custom middleware: request logger
  res.on('finish', () => console.log(`${req.method} ${req.originalUrl} -> ${res.statusCode}`));
  next();                                                  //    hand control to the next handler
});

class ApiError extends Error {                             // one error type carries the status code
  constructor(status, message, details) { super(message); this.status = status; this.details = details; }
}

let students = [{ id: 1, name: 'Thandi Nkosi', email: 'thandi@example.com', year: 2 }];
let nextId = 2;

function validateStudent(body = {}, { partial = false } = {}) {     // returns the clean value or throws
  const errors = [], value = {};
  const wants = (key) => !partial || body[key] !== undefined;       // PATCH checks only the fields sent
  if (wants('name')) {
    if (typeof body.name !== 'string' || !body.name.trim()) errors.push('name is required');
    else value.name = body.name.trim();
  }
  if (wants('email')) {
    if (typeof body.email !== 'string' || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.email)) {
      errors.push('email is invalid');
    } else value.email = body.email.trim().toLowerCase();
  }
  if (wants('year')) {
    if (!Number.isInteger(body.year) || body.year < 1 || body.year > 6) {
      errors.push('year must be a whole number from 1 to 6');
    } else value.year = body.year;
  }
  if (errors.length) throw new ApiError(400, 'Validation failed', errors);
  return value;
}

function getStudent(rawId) {                               // path params are strings: validate them
  if (!/^\d+$/.test(rawId) || Number(rawId) < 1) throw new ApiError(400, 'id must be a positive whole number');
  const student = students.find((s) => s.id === Number(rawId));
  if (!student) throw new ApiError(404, `Student ${rawId} not found`);
  return student;
}

app.get('/students', (req, res) => {
  const { q } = req.query;                                 // /students?q=thandi
  const list = typeof q === 'string'
    ? students.filter((s) => s.name.toLowerCase().includes(q.toLowerCase()))
    : students;
  res.json(list);
});

app.get('/students/:id', (req, res) => res.json(getStudent(req.params.id)));   // :id -> req.params.id

app.post('/students', (req, res) => {
  const value = validateStudent(req.body);                 // Express 5: req.body may be undefined (handled)
  if (students.some((s) => s.email === value.email)) throw new ApiError(409, 'Email already registered');
  const student = { id: nextId++, ...value };
  students.push(student);
  res.status(201).location(`/students/${student.id}`).json(student);
});

app.put('/students/:id', (req, res) => {                   // PUT = replace: every field required
  const student = getStudent(req.params.id);
  res.json(Object.assign(student, validateStudent(req.body)));
});

app.patch('/students/:id', (req, res) => {                 // PATCH = change only the fields sent
  const student = getStudent(req.params.id);
  const changes = validateStudent(req.body, { partial: true });
  if (Object.keys(changes).length === 0) throw new ApiError(400, 'Send at least one field to change');
  res.json(Object.assign(student, changes));
});

app.delete('/students/:id', (req, res) => {
  const student = getStudent(req.params.id);
  students = students.filter((s) => s !== student);
  res.status(204).end();                                   // 204: success, nothing to send back
});

app.use((req, res) => {                                    // unmatched route -> 404 (registered AFTER routes)
  res.status(404).json({ error: `Route not found: ${req.method} ${req.originalUrl}` });
});

app.use((err, req, res, next) => {                         // 4 parameters = error-handling middleware (LAST)
  if (err instanceof ApiError) {
    return res.status(err.status).json({ error: err.message, ...(err.details && { details: err.details }) });
  }
  if (err.type === 'entity.parse.failed') return res.status(400).json({ error: 'Malformed JSON body' });
  console.error(err);                                      // details stay in the server log...
  res.status(500).json({ error: 'Internal server error' }); // ...clients get a generic message
});

if (require.main === module) app.listen(3000, () => console.log('http://localhost:3000'));
module.exports = app;                                      // tests import the app without opening a port
```

Run `node students.js`, then (bash; `-w` prints the status code after each body):

```bash
H="Content-Type: application/json"; W="   -> %{http_code}\n"
curl -s -w "$W" -X POST localhost:3000/students -H "$H" -d '{"name":"Sipho Dlamini","email":"sipho@example.com","year":3}'
curl -s -w "$W" -X POST localhost:3000/students -H "$H" -d '{"name":"","email":"nope","year":9}'
curl -s -w "$W" -X POST localhost:3000/students -H "$H" -d '{"name":"Dup","email":"sipho@example.com","year":1}'
curl -s -w "$W" -X PATCH localhost:3000/students/2 -H "$H" -d '{"year":4}'
curl -s -w "$W" localhost:3000/students/abc
curl -s -w "$W" localhost:3000/students/99
curl -s -w "$W" -X POST localhost:3000/students -H "$H" -d '{bad json'
curl -s -w "$W" -X DELETE localhost:3000/students/2
curl -s -w "$W" localhost:3000/nothing-here
```

```output
STUDENTS_OUT
```

### 7.4 Middleware, order and error handling

**Middleware** is a function `(req, res, next)` that runs between the request and the route. It must either **send a response** or **call `next()`**; doing neither makes the request hang. Middleware runs **in the order it is registered**.

```text
request -> express.json() -> logger -> /admin guard -> route handler ----------> response
                                          | 401: respond, stop   | throw / next(err)
                                          v                      v
                      no route matched -> 404 handler      error-handling middleware -> response
```

| Rule | Why |
|---|---|
| `app.use(express.json())` **before** the routes | Otherwise `req.body` is `undefined` |
| 404 handler **after** all routes | It catches only what nothing else matched |
| Error-handling middleware **last**, with **4 parameters** | Express recognises it by `(err, req, res, next)` |
| `next(err)` or `throw` jumps straight to the error handler | In Express 5, a rejected promise from an `async` handler does the same |

*Standalone.* This program prints the path each request takes through the stack:

```javascript
const express = require('express');
const app = express();
const trace = [];

app.use((req, res, next) => { trace.push('logger'); next(); });
app.use('/admin', (req, res, next) => {                        // runs only for paths starting with /admin
  trace.push('guard');
  if (req.get('x-token') !== 'secret') return res.status(401).json({ error: 'Missing or bad token' });
  next();
});
app.get('/admin/stats', (req, res) => { trace.push('handler'); res.json({ ok: true }); });
app.get('/boom', async () => { trace.push('handler'); throw new Error('database exploded'); });
app.use((req, res) => { trace.push('404'); res.status(404).json({ error: 'Not found' }); });
app.use((err, req, res, next) => { trace.push('error handler'); res.status(500).json({ error: 'Internal server error' }); });

const server = app.listen(0, async () => {                      // port 0 = any free port
  const base = `http://127.0.0.1:${server.address().port}`;
  const calls = [['/admin/stats', {}], ['/admin/stats', { 'x-token': 'secret' }], ['/boom', {}], ['/nope', {}]];
  for (const [path, headers] of calls) {
    trace.length = 0;
    const r = await fetch(base + path, { headers });
    console.log(r.status, path.padEnd(13), trace.join(' > '));
  }
  server.close();
});
```

```output
OUT
```

### 7.5 Express 5 versus Express 4

`npm install express` now installs **Express 5**. Many tutorials show Express 4. These differences were checked against the version used in this manual:

| Topic | Express 4 | Express 5 |
|---|---|---|
| Errors in `async` handlers | Need `try/catch` + `next(err)` or a wrapper; otherwise the request hangs or the process crashes | Rejected promises go to the error handler automatically |
| `req.body` with no body | `{}` | `undefined`; guard with `req.body ?? {}` or a default parameter |
| Wildcard route | `app.get('*', ...)` | Throws; write `'/*splat'` (a named wildcard) |
| Optional parameter | `'/books/:id?'` | Throws; write `'/books{/:id}'` |
| `req.query` parser | `qs` ("extended"): `?a[b]=1` becomes an object | "simple": `?a[b]=1` stays the literal key `"a[b]"` |
| Removed helpers | `app.del()`, `req.param()`, `res.json(status, obj)` | Use `app.delete()`, `req.params`, `res.status(n).json(obj)` |

> **Exam tip:** If your exam machine has Express 4, the code in this manual still works: the only difference is that an `async` route handler needs its own `try { ... } catch (err) { next(err); }`. For libraries such as Zod or express-validator: they are optional extras; the hand-written validation in this manual needs no extra packages.

# Section 1 — Software Dev Foundations for Industrial IT

## Why this section exists

You already know how to write C#, Python, TypeScript, and SQL — your qualification covered that. What it likely didn't cover in depth is *how those skills get used differently once you're writing software that touches a real business, a real team, and (in this case) potentially real production equipment.* The gap between "I can write code that works" and "I can write code a team trusts, that survives contact with a real environment" is almost entirely made of the things in this section: version control discipline, testing, API/database design done properly, and code review culture. This is the general foundation layer — Sections 2 onward assume you have this.

---

## 1. Version control, done properly (not just "I know git")

You've used Git. The gap is usually in the *workflow*, not the commands.

- **Branching strategy.** The common pattern you'll meet in almost any real team: a stable `main`/`master` branch that's always deployable, feature branches for new work (`feature/historian-export`), and pull requests to merge back into main after review. Never commit directly to main on a real team, even if it "seems faster."
- **Commit messages that mean something.** `fixed bug` tells a future reader (often you, in 6 months) nothing. `Fix off-by-one error in historian date-range query causing last day of month to be excluded` tells them everything. A good habit: write the commit message as if explaining the change to someone who has zero context.
- **Pull requests and code review.** In a real team, code doesn't merge without at least one other person reviewing it — not because you're not trusted, but because a second set of eyes catches things the author is too close to see, and it spreads knowledge of the codebase across the team instead of it living in one person's head.
- **`.gitignore` discipline.** Never commit secrets (API keys, connection strings, passwords), build artifacts, or environment-specific config. This matters *more* in industrial contexts, not less — a leaked connection string to a historian or MES database is a real security incident, not just an embarrassment.

## 2. Testing — why it's not optional once code matters

**Unit tests** — test one small piece of logic (a single function/method) in isolation, fast to run, run constantly during development. **Integration tests** — test that multiple pieces actually work together (e.g., your code really can read from a test database the way you expect). **The pyramid**: lots of fast unit tests, fewer slower integration tests, and a small number of full end-to-end tests — because the fast, cheap tests catch most problems, and the slow expensive ones are reserved for confirming the whole system genuinely works together.

**Why this matters more, not less, in an industrial context:** a bug in a typical business web app might show the wrong number on a report. A bug in code that writes a setpoint to a PLC, or miscalculates a value feeding a control decision, has a much higher-consequence failure mode. You are extremely unlikely to be writing code that writes directly to a PLC as a junior/intern — but you may well be writing code that feeds data *into* decisions people or systems make, and the discipline of "test it before you trust it" carries over regardless of how close to the physical process your specific code sits.

**Practical minimum to actually practice:** for any function with real logic (not a trivial getter/setter), write at least one test for the expected case and one for an edge case (empty input, a boundary value, an unexpected type) before considering the function "done."

## 3. API design — how systems actually talk to each other

You'll build and consume APIs constantly in integration work (Section 2 goes deep on the industrial-specific side of this). The general principles:

- **REST basics done right.** Resources are nouns (`/orders`, `/batches`), not verbs (`/getOrders`); HTTP methods carry the verb (GET to read, POST to create, PUT/PATCH to update, DELETE to remove); status codes mean something specific (200 success, 201 created, 400 bad request from the client, 401/403 auth problems, 404 not found, 500 server error) — and returning 200 with an error message buried in the response body, instead of an honest status code, is a common beginner mistake that makes an API painful for anyone else to consume.
- **Versioning.** APIs change over time; breaking every existing consumer every time you improve something is a fast way to make enemies. Common pattern: `/v1/orders`, `/v2/orders` — old consumers keep working against v1 while new features land in v2.
- **Authentication basics.** API keys (simple, common for service-to-service), OAuth2/tokens (more common for user-facing systems). Know that "no authentication at all" (which you saw is genuinely common in older industrial protocols, Section 6 of the Industrial Deep Dive) is specifically *not* acceptable for anything you build fresh today, even internally.
- **Error handling that helps the caller.** A response body that says `{"error": "Invalid batch ID format — expected GUID, received '12345'"}` is worth ten times a bare `500 Internal Server Error` with no detail, for whoever's trying to debug against your API at 2am.

## 4. Database design — beyond "I know SQL"

You know SELECT/JOIN. The design skill is different:

- **Normalization (the basics).** Avoid storing the same fact in multiple places (a customer's name repeated on every one of their orders, instead of referenced by a customer ID) — because when that fact needs to change, you want to change it in exactly one place, not hunt down every copy.
- **When to denormalize anyway.** Sometimes performance genuinely justifies duplicating data (this comes up a lot with time-series/historian data specifically, covered properly in Section 3) — the skill is knowing it's a deliberate tradeoff, not an accident.
- **Indexes.** A database without the right index on a frequently-queried column can be catastrophically slow once the table has real volume — and industrial data volumes (a historian logging thousands of tags every few seconds) get large fast. Know at least that indexes exist, what they trade off (faster reads, slightly slower writes, more storage), and that "why is this query slow" is very often an indexing question.
- **Transactions.** A transaction groups multiple database operations so they either *all* succeed or *all* roll back together — critical whenever an operation touches more than one table and a partial failure would leave data in an inconsistent state (e.g., recording a completed batch and decrementing raw material inventory — you never want one to happen without the other).

## 5. Hands-On Lab

**Lab 1.1 — A real Git workflow**
1. Create a small project (even a simple one — e.g., a script that reads a CSV of fake sensor readings and prints basic stats).
2. Initialize a Git repo, make your first commit on `main`.
3. Create a feature branch, make a change, commit with a proper descriptive message, then open a pull request against `main` on GitHub (even solo — you can review and merge your own PR, the point is practicing the workflow).
4. Add a `.gitignore` appropriate to your language, and confirm a fake "secrets.env" file you create is correctly ignored, not tracked.

**Lab 1.2 — Write real tests**
Using your CSV-stats script from Lab 1.1 (or any small existing project), pick one function with actual logic and write unit tests for it using a real testing framework (`pytest` for Python, `xUnit`/`NUnit` for C#, `Jest` for TypeScript) — at minimum one normal case and one edge case. Run them and confirm they pass; then deliberately break the function and confirm the test correctly fails.

**Lab 1.3 — Build and document a tiny API**
Build a minimal REST API (a Python Flask/FastAPI app, or a .NET minimal API — pick whichever matches your strongest language) with one endpoint that returns fake sensor data as JSON, following the REST conventions above (correct HTTP method, correct status codes, a versioned path like `/v1/readings`). Test it with a tool like `curl` or Postman/Insomnia, and write a short README describing the endpoint, its parameters, and an example response.

## 6. Autism For Evil — the real-world insider bit

The thing that separates a junior who gets trusted with more responsibility from one who doesn't, almost everywhere, isn't raw coding speed — it's **whether their commits and pull requests are easy for someone else to review.** A PR with a clear description, a sensible commit history, and tests that demonstrate the change actually works gets merged fast and builds trust. A PR that's a giant unexplained diff with a commit message of "updates" gets a reviewer sighing and asking five clarifying questions before they'll even look closely — and that friction quietly shapes who gets handed the more interesting work next. This is one of the fastest, cheapest ways to stand out as an intern, and almost nobody tells you it's this simple.

The other thing worth knowing before you get anywhere near a real industrial system: **in an OT-adjacent software role, "move fast and break things" is not a compliment, it's a resume-ending mistake.** The testing discipline in this section isn't academic box-ticking — a genuinely common, real failure mode for a junior dev given database or integration access is running an untested query or script against a production system "just to check something quickly," and either locking a table an operator-facing screen needed, or writing bad data into a system feeding real decisions. The habit to build now, while the stakes are a personal lab project: **always know whether you're pointed at a test/dev environment or something real, and default to assuming "real" costs you something if you're wrong.**

---

## Done when

- [ ] You can explain why direct commits to `main` are avoided on a real team, in your own words.
- [ ] You can write a commit message that would actually make sense to someone with zero context.
- [ ] You've written at least one real unit test with a passing and a deliberately-failing case (Lab 1.2).
- [ ] You can explain the difference between 400 and 500 status codes, and why burying an error in a 200 response is a bad pattern.
- [ ] You've built and documented the small API in Lab 1.3.

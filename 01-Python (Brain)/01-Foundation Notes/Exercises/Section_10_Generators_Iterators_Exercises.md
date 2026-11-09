## Section 10 Exercises: Generators & Iterators (Deep Dive)

Save each exercise as its own scratch file. Focus on *proving to yourself* that generators are lazy — add `print()` statements inside them to watch execution pause and resume.

---

### 🟢 Warm-Up — `countdown(n)`
**Time:** ~5 min

**Goal:** Write a generator function (not a list) that counts down from `n` to `1`.

- [ ] `def countdown(n):` uses `yield`, not `return`.
- [ ] Manually call `next()` on it 3 times and print each result.
- [ ] Use a `for` loop to exhaust the rest.

**Done when:** The `for` loop prints the remaining numbers down to `1` with no errors, and calling `next()` one more time after the loop raises `StopIteration`.

---

### 🟡 Core — Generator Expression Filter
**Time:** ~10 min

**Goal:** Use a generator expression (parentheses, not brackets) to lazily filter and transform data.

- [ ] Build a generator expression that yields the square of every **even** number from `1` to `50`.
- [ ] Print `next()` on it twice manually.
- [ ] Then convert it to a `list()` and print the full result.
- [ ] In a comment, explain why writing this with `[]` instead of `()` would behave differently in terms of memory.

**Done when:** You can articulate the memory difference in your own words, not just copy the notes.

---

### 🟡 Core — Custom `Fibonacci` Iterator (class-based)
**Time:** ~20 min

**Goal:** Implement the full Iterator Protocol (`__iter__` + `__next__`) for a class that yields Fibonacci numbers, capped at `n` terms — mirroring the `Countdown` class in your notes (10.5).

- [ ] `class Fibonacci:` stores `n` (term limit) and tracks current state (`a`, `b`, `count`).
- [ ] `__iter__(self): return self`
- [ ] `__next__(self):` returns the next Fibonacci number, raises `StopIteration` once `count >= n`.
- [ ] Test with `for num in Fibonacci(10): print(num)`.

**Done when:** `Fibonacci(10)` prints exactly 10 numbers: `0, 1, 1, 2, 3, 5, 8, 13, 21, 34`.

---

### 🟠 Applied — Lazy File Reader
**Time:** ~15 min

**Goal:** Build the production pattern from notes 10.8 — read a file line-by-line without loading it all into memory.

- [ ] Create a small text file (`sample_log.txt`) with ~15 lines, where some lines contain the word `"ERROR"`.
- [ ] Write `def read_logs(filepath):` as a generator that yields each stripped line.
- [ ] Add a `print(f"Reading: {line}")` *inside* the generator, right before each `yield`, so you can visually see it only processes one line at a time when you call `next()` manually (don't use a `for` loop for this part).

**Done when:** Calling `next()` three separate times prints exactly one "Reading:" line each call — proof the rest of the file hasn't been touched yet.

---

### 🟠 Applied — Mini ETL Pipeline (Chained Generators)
**Time:** ~20 min

**Goal:** Chain three generators together — this is the real-world pattern behind data pipelines and log processors.

- [ ] `read_logs(filepath)` — yields raw lines (reuse from the previous exercise).
- [ ] `filter_errors(lines)` — takes a generator, yields only lines containing `"ERROR"`.
- [ ] `extract_messages(lines)` — takes a generator, yields just the text after the `ERROR:` prefix (strip it off).
- [ ] Chain them: `for msg in extract_messages(filter_errors(read_logs("sample_log.txt"))):`
- [ ] Print each final message.

**Done when:** Only the error messages print, with the `"ERROR:"` prefix stripped, and no intermediate list was ever created.

---

### 🔴 Challenge — Infinite Generator + `itertools.islice`
**Time:** ~10 min

**Goal:** Combine an infinite generator with `itertools.islice` to safely pull a finite slice from it.

- [ ] Write `def infinite_counter(start, step):` that yields forever, incrementing by `step` each time (like `infinite_mana` in your notes 10.7).
- [ ] Import `islice` from `itertools`.
- [ ] Use `islice(infinite_counter(0, 5), 8)` to safely grab exactly the first 8 values without writing your own counter or risking an infinite loop.
- [ ] Print the result as a list.

**Done when:** You get exactly `[0, 5, 10, 15, 20, 25, 30, 35]` and your program terminates (doesn't hang).

---

### 💀 BOSS — Lazy Pagination Simulator
**Time:** ~25–30 min

**Goal:** Simulate how real APIs paginate large datasets lazily — a pattern you'll use directly when working with APIs in FastAPI/Emlindweni-style projects.

**Requirements:**
- [ ] Create a list of 47 fake "records" — e.g. `[{"id": i, "name": f"Item {i}"} for i in range(47)]`.
- [ ] Write `def paginate(data, page_size):` — a generator that yields successive **pages** (lists) of `page_size` records at a time. The last page may be smaller.
- [ ] Add a `print(f"Fetching page starting at index {i}...")` inside `paginate` right before each `yield`, to prove pages are only built when requested.
- [ ] Write `def flatten_pages(pages):` — a second generator that takes the page generator and yields individual records one at a time (flattening).
- [ ] Chain them: loop over `flatten_pages(paginate(data, page_size=10))` and print each record's `id`.
- [ ] Manually call `next()` on the chained generator just **twice**, and confirm in the printed output that only the **first page** was fetched — not all 5 pages.

**Done when:** You can show (via the print statements) that calling `next()` twice only triggers ONE "Fetching page..." message, proving the whole pipeline stays lazy end-to-end.

---

### ✅ Section Progress
- [ ] Warm-Up: `countdown(n)`
- [ ] Core: Generator expression filter
- [ ] Core: `Fibonacci` iterator class
- [ ] Applied: Lazy file reader
- [ ] Applied: Chained mini ETL pipeline
- [ ] Challenge: Infinite generator + `islice`
- [ ] 💀 BOSS: Lazy pagination simulator

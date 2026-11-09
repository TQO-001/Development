## PostgreSQL with Python

These notes cover how to talk to a PostgreSQL database from Python code. The library we use is `psycopg2` — the most widely used PostgreSQL adapter for Python. If you've worked through the SQL notes, you already know the SQL side. These notes focus on the Python side: how to connect, send queries, handle results, and do it all safely and cleanly.

By the end of these notes you'll be able to build a proper data access layer for a project like Navy.

---

## Section 1: Connecting to PostgreSQL

Before you can do anything, you need to install psycopg2 and open a connection to your database.

```bash
pip install psycopg2-binary
```

`psycopg2-binary` bundles everything you need in one package — perfect for development. For production deployments, the plain `psycopg2` package (which requires PostgreSQL headers) is preferred, but `psycopg2-binary` works fine throughout these notes.

### 1.1 Making a Connection

```python
import psycopg2

# Connect using individual keyword arguments
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="game_db",
    user="admin",
    password="secret"
)

# Or connect using a single connection string (called a DSN)
# Format: postgresql://user:password@host:port/database
conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")

# Always close the connection when you're done with it
conn.close()
```

### 1.2 Always Clean Up With try/finally

A connection is a resource — like an open file. If something goes wrong before you call `conn.close()`, you'll leave a connection open and waste server resources. The safe pattern is `try/finally`.

```python
import psycopg2

conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")

try:
    # All your database work goes here
    pass
finally:
    conn.close()  # This runs whether the code above succeeded or crashed
```

> [!NOTE]
> A `psycopg2` connection is **not** thread-safe. If your application handles multiple requests at the same time (e.g., a web server), each thread needs its own separate connection. Section 7 (Connection Pooling) handles this properly.

---

**Practice:** Write a Python script that connects to your local PostgreSQL database, prints `"Connected to game_db successfully!"`, then closes the connection cleanly using `try/finally`.

---

## Section 2: Executing Queries

To send SQL to the database, you need a **cursor**. A cursor is the object that actually sends your query and gives you the results back. Think of the connection as your workspace and the cursor as your pen — it's what you use to read and write.

### 2.1 Basic Query Execution

```python
conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")
cursor = conn.cursor()

# Send a SQL query
cursor.execute("SELECT id, name, level FROM players;")

# fetchone() — gets the very next single row as a tuple
row = cursor.fetchone()
print(row)  # Output: (1, 'Arthur', 15)

cursor.close()
conn.close()
```

### 2.2 Fetching Multiple Rows

```python
cursor.execute("SELECT id, name, level FROM players;")

# fetchall() — gets every remaining row as a list of tuples
rows = cursor.fetchall()
for row in rows:
    print(row)
# (1, 'Arthur', 15)
# (2, 'Merlin', 22)
# (3, 'Lancelot', 18)

# fetchmany(n) — gets the next n rows only
cursor.execute("SELECT name FROM players;")
batch = cursor.fetchmany(2)  # Gets first 2 rows
print(batch)  # [('Arthur',), ('Merlin',)]
```

### 2.3 Getting Column Names

After executing a query, the cursor's `description` attribute tells you the column names. This is useful when you want to work with the data by column name rather than by position.

```python
cursor.execute("SELECT name, level, gold FROM players LIMIT 1;")

# description is a tuple of tuples — one per column
# The first element of each inner tuple is the column name
column_names = [desc[0] for desc in cursor.description]
print(column_names)  # ['name', 'level', 'gold']
```

---

**Practice:**
1. Write a query that fetches all players and prints each one on its own line in the format: `"Arthur — Level 15"`.
2. Use `cursor.description` to print the column names as a header before printing the rows.

---

## Section 3: Parameterized Queries — Staying Safe

**Never** build a SQL string by pasting user input directly into it. This is called **SQL injection** and it's one of the most serious security vulnerabilities in software. An attacker can craft input that changes the meaning of your entire query.

```python
# ❌ DANGEROUS — NEVER DO THIS
user_input = "Arthur"
cursor.execute(f"SELECT * FROM players WHERE name = '{user_input}'")

# If user_input is: ' OR '1'='1
# The query becomes: SELECT * FROM players WHERE name = '' OR '1'='1'
# That condition is always true — it returns every player in the database
```

The fix is **parameterized queries**. You put a `%s` placeholder where the value goes, and pass the value separately as a tuple. psycopg2 handles escaping it safely — the user's input can never break out of its position.

```python
# ✅ SAFE — always use this pattern
player_name = "Arthur"

cursor.execute(
    "SELECT * FROM players WHERE name = %s;",
    (player_name,)   # Note the trailing comma — psycopg2 requires a tuple, even with one value
)
row = cursor.fetchone()
print(row)
```

### 3.1 Multiple Parameters

Each `%s` matches the value at the same position in your tuple:

```python
cursor.execute(
    "SELECT name, level FROM players WHERE role = %s AND level > %s;",
    ("Mage", 10)   # First %s = 'Mage', second %s = 10
)
```

### 3.2 Named Parameters

For queries with many parameters, named placeholders using `%(name)s` are easier to read:

```python
cursor.execute(
    "SELECT * FROM players WHERE role = %(role)s AND level > %(min_level)s;",
    {"role": "Warrior", "min_level": 12}   # Pass a dict instead of a tuple
)
```

> [!NOTE]
> psycopg2 uses `%s` as its placeholder — not `?` (SQLite) and not `:name` (SQLite named params). This trips people up when switching between database libraries, so it's worth memorising.

---

**Practice:**
1. Write a function `get_player_by_name(name: str)` that safely queries for a player by name using a parameterized query.
2. Write a function `get_players_by_role_and_min_level(role: str, min_level: int)` that filters by both.

---

## Section 4: Inserting, Updating & Deleting

For any query that changes data — `INSERT`, `UPDATE`, `DELETE` — you must call `conn.commit()` after `cursor.execute()` to make the changes permanent. Without `commit()`, the changes exist only inside your current transaction and will be lost when you disconnect.

### 4.1 INSERT

```python
conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO players (name, level, gold, role) VALUES (%s, %s, %s, %s);",
    ("Percival", 8, 300, "Knight")
)

# Commit makes the insert permanent
conn.commit()

cursor.close()
conn.close()
```

### 4.2 Getting the ID of the New Row

Add `RETURNING id` to your SQL to get back the auto-generated ID of the row you just created:

```python
cursor.execute(
    "INSERT INTO players (name, level, role) VALUES (%s, %s, %s) RETURNING id;",
    ("Percival", 8, "Knight")
)

new_id = cursor.fetchone()[0]   # fetchone() gives a tuple, [0] grabs the id
print(f"Created player with ID: {new_id}")

conn.commit()
```

### 4.3 UPDATE

```python
cursor.execute(
    "UPDATE players SET gold = gold + %s WHERE id = %s;",
    (500, 1)
)
conn.commit()

# cursor.rowcount tells you how many rows were actually affected
print(f"Updated {cursor.rowcount} row(s)")
```

### 4.4 DELETE

```python
cursor.execute(
    "DELETE FROM players WHERE id = %s;",
    (3,)
)
conn.commit()
print(f"Deleted {cursor.rowcount} row(s)")
```

> [!NOTE]
> `cursor.rowcount` is very useful for checking whether your `UPDATE` or `DELETE` actually did anything. If your `WHERE` clause matched nothing, `rowcount` will be `0` — you can use this to detect "player not found" situations without a separate `SELECT`.

---

**Practice:**
1. Write a function `create_player(name, level, role)` that inserts a new player and returns their new `id`.
2. Write a function `award_gold(player_id, amount)` that adds `amount` to a player's gold and returns `True` if the player was found (i.e. `rowcount > 0`).

---

## Section 5: Transactions in Python

psycopg2 automatically starts a transaction whenever you execute your first query on a connection. You have to either `commit()` to save, or `rollback()` to undo — nothing is permanent until you commit.

### 5.1 Manual Commit and Rollback

```python
conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")
cursor = conn.cursor()

try:
    # Step 1: deduct gold from the buyer
    cursor.execute("UPDATE players SET gold = gold - 500 WHERE id = %s;", (1,))

    # Step 2: add the item to their inventory
    cursor.execute(
        "INSERT INTO inventory (player_id, item_name) VALUES (%s, %s);",
        (1, "Enchanted Sword")
    )

    # Both steps worked — make it permanent
    conn.commit()
    print("Purchase complete!")

except Exception as e:
    # Something went wrong — undo both steps
    conn.rollback()
    print(f"Purchase failed: {e}. Nothing was changed.")

finally:
    cursor.close()
    conn.close()
```

### 5.2 Using `with conn:` for Automatic Commit/Rollback

psycopg2 supports using the connection as a context manager with `with`. If the block finishes without an error, it commits automatically. If an exception is raised, it rolls back automatically.

```python
conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")

with conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET gold = gold - 500 WHERE id = %s;", (1,))
    cursor.execute(
        "INSERT INTO inventory (player_id, item_name) VALUES (%s, %s);",
        (1, "Enchanted Sword")
    )
    # Exits cleanly → commits automatically
    # Raises an exception → rolls back automatically

conn.close()  # 'with conn:' handles commit/rollback but NOT closing the connection
```

> [!NOTE]
> The `with conn:` block handles transaction management — commit on success, rollback on failure. But it does **not** close the connection when it exits. You still need `conn.close()` (or a connection pool — see Section 7) to fully clean up.

---

**Practice:**
1. Write a function `transfer_gold(from_id, to_id, amount)` that moves `amount` of gold from one player to another inside a transaction. If either the deduction or the addition fails, the whole thing should roll back.

---

## Section 6: Mapping Results to Dictionaries

By default, psycopg2 returns rows as plain tuples: `(1, 'Arthur', 15)`. That works for simple queries, but for anything more complex you'll want to access values by name: `player['name']`, `player['level']`. It's much clearer and far less error-prone.

### 6.1 RealDictCursor

The easiest way is to pass `cursor_factory=RealDictCursor` when creating your cursor. It makes every row come back as a dictionary-like object.

```python
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute("SELECT id, name, level, gold FROM players;")
rows = cursor.fetchall()

for player in rows:
    print(f"{player['name']} is Level {player['level']} with {player['gold']} gold.")

cursor.close()
conn.close()
```

### 6.2 Building Dictionaries Manually

If you prefer not to use `RealDictCursor`, you can build dictionaries yourself by combining the column names from `cursor.description` with each row's values.

```python
cursor.execute("SELECT id, name, level FROM players;")

# Get the column names
columns = [desc[0] for desc in cursor.description]

# zip() pairs each column name with the matching value in each row
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

print(rows)
# [{'id': 1, 'name': 'Arthur', 'level': 15}, {'id': 2, 'name': 'Merlin', 'level': 22}, ...]
```

---

**Practice:**
1. Write a function `get_all_players()` that returns a list of dictionaries. Each dict should have `id`, `name`, `level`, and `gold` keys. Use `RealDictCursor`.

---

## Section 7: Connection Pooling

Opening a database connection takes time and server resources. If you open a fresh connection for every single query — especially in a web server handling many requests per second — the overhead adds up fast.

A **connection pool** keeps a set of connections open and ready. When your code needs one, it borrows it from the pool. When it's done, it returns it for the next piece of code to use. No new connection overhead — just borrow and return.

### 7.1 SimpleConnectionPool

```python
from psycopg2 import pool

# Create the pool once at startup — open between 2 and 10 connections
connection_pool = pool.SimpleConnectionPool(
    minconn=2,
    maxconn=10,
    dsn="postgresql://admin:secret@localhost:5432/game_db"
)

def get_all_players():
    conn = connection_pool.getconn()   # Borrow a connection
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level FROM players;")
        return cursor.fetchall()
    finally:
        connection_pool.putconn(conn)  # Always return it — even if something crashed

# When your application shuts down, close everything cleanly
connection_pool.closeall()
```

> [!NOTE]
> The critical rule with pooling: **always return the connection**. Wrapping `putconn()` inside a `finally` block is the safest way — if your code raises an exception, the connection still gets returned instead of leaking.

### 7.2 ThreadedConnectionPool

If your application uses multiple threads (for example, a Flask development server), use `ThreadedConnectionPool` instead. It's the same API, but safe across threads.

```python
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=20,
    dsn="postgresql://admin:secret@localhost:5432/game_db"
)
```

---

**Practice:**
1. Set up a `SimpleConnectionPool` with a minimum of 1 and maximum of 5 connections.
2. Write a helper function `query(sql, params=None)` that borrows a connection from the pool, runs a query, returns the results, and always puts the connection back.

---

## Section 8: Handling PostgreSQL Errors in Python

When something goes wrong in PostgreSQL — a duplicate entry, a missing row, a broken foreign key — psycopg2 raises a Python exception. Catching specific exceptions lets you respond gracefully instead of letting the whole program crash.

### 8.1 Catching Specific Database Errors

```python
import psycopg2
from psycopg2 import errors   # Named error classes for specific PostgreSQL errors

conn = psycopg2.connect("postgresql://admin:secret@localhost:5432/game_db")
cursor = conn.cursor()

try:
    cursor.execute(
        "INSERT INTO players (name, level) VALUES (%s, %s);",
        ("Arthur", 15)   # 'Arthur' already exists and has a UNIQUE constraint
    )
    conn.commit()

except errors.UniqueViolation:
    conn.rollback()
    print("A player with that name already exists.")

except errors.ForeignKeyViolation:
    conn.rollback()
    print("The referenced row doesn't exist in the parent table.")

except errors.NotNullViolation:
    conn.rollback()
    print("A required field was left empty.")

except psycopg2.OperationalError as e:
    # Connection-level issues — server down, wrong credentials, timeout
    print(f"Could not reach the database: {e}")

except psycopg2.Error as e:
    # Catch-all for any other psycopg2 error
    conn.rollback()
    print(f"Database error: {e}")
```

### 8.2 Common PostgreSQL Error Types

| psycopg2 exception | When it fires |
|---|---|
| `errors.UniqueViolation` | Inserting a duplicate value into a UNIQUE column |
| `errors.ForeignKeyViolation` | Inserting a value that doesn't exist in the referenced table |
| `errors.NotNullViolation` | Leaving a NOT NULL column empty |
| `errors.CheckViolation` | Breaking a CHECK constraint |
| `errors.UndefinedTable` | Querying a table that doesn't exist |
| `psycopg2.OperationalError` | Connection issues — server unreachable, timeout, bad credentials |

### 8.3 Reading the Raw Error Details

Every psycopg2 exception carries the raw PostgreSQL error code and message if you need them:

```python
except psycopg2.Error as e:
    print(f"Error code:    {e.pgcode}")   # e.g. '23505' (unique violation)
    print(f"Error message: {e.pgerror}")  # The full PostgreSQL error text
```

---

**Practice:**
1. Write a function `safe_create_player(name, level)` that catches a `UniqueViolation` and returns a human-readable error message rather than crashing.

---

## Section 9: Bulk Operations

Inserting thousands of rows one at a time with thousands of individual `cursor.execute()` calls is slow — each one is a round-trip to the database. Bulk operations let you push large amounts of data in a single shot.

### 9.1 executemany() — Simple Bulk Insert

`executemany()` runs the same SQL once for each item in a list. It's cleaner than a manual loop, though it still sends individual queries under the hood.

```python
new_players = [
    ("Gawain",   12, "Warrior"),
    ("Tristan",  10, "Archer"),
    ("Isolde",   14, "Mage"),
    ("Bedivere",  9, "Knight"),
]

cursor.executemany(
    "INSERT INTO players (name, level, role) VALUES (%s, %s, %s);",
    new_players
)
conn.commit()
```

### 9.2 execute_values() — Fast Bulk Insert

`execute_values()` from `psycopg2.extras` is significantly faster because it sends all the data in a single SQL statement rather than one per row. For large inserts, this makes a substantial difference.

```python
from psycopg2.extras import execute_values

new_players = [
    ("Gawain",   12, "Warrior"),
    ("Tristan",  10, "Archer"),
    ("Isolde",   14, "Mage"),
]

# The %s here represents the entire set of value groups — not just one row
execute_values(
    cursor,
    "INSERT INTO players (name, level, role) VALUES %s;",
    new_players
)
conn.commit()
```

### 9.3 Bulk Update with execute_values

You can use `execute_values` for bulk updates too, by joining against a temporary values list:

```python
from psycopg2.extras import execute_values

# (gold_to_add, player_id) pairs
updates = [
    (500, 1),
    (300, 2),
    (750, 3),
]

execute_values(
    cursor,
    """
    UPDATE players AS p
    SET gold = p.gold + v.amount
    FROM (VALUES %s) AS v(amount, id)
    WHERE p.id = v.id;
    """,
    updates
)
conn.commit()
```

> [!NOTE]
> For inserting very large datasets — millions of rows — look into PostgreSQL's `COPY` command, exposed in psycopg2 via `cursor.copy_expert()`. It's the fastest possible way to load bulk data because it bypasses normal query parsing entirely.

---

**Practice:**
1. Write a function `bulk_insert_inventory(items: list)` that accepts a list of `(player_id, item_name, quantity)` tuples and inserts them all at once using `execute_values()`.

---

## Section 10: Working with JSON and Arrays

PostgreSQL supports JSON and array column types natively — you can store structured data inside a column and query fields within it directly from SQL.

### 10.1 JSON Columns

PostgreSQL has two JSON types: `JSON` (stores raw text) and `JSONB` (stores binary — faster to query). Use `JSONB` almost always.

```sql
-- A table with a JSONB column for flexible character stats
CREATE TABLE characters (
    id        SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    class     VARCHAR(50),
    stats     JSONB
);
```

```python
from psycopg2.extras import Json

# The Json() wrapper handles converting your Python dict to a format psycopg2 can send
character_stats = {
    "strength":    18,
    "dexterity":   14,
    "intelligence": 10,
    "abilities":   ["Slash", "Block", "Shield Bash"]
}

cursor.execute(
    "INSERT INTO characters (player_id, class, stats) VALUES (%s, %s, %s) RETURNING id;",
    (1, "Warrior", Json(character_stats))
)
conn.commit()
```

Querying JSON fields directly in SQL:

```python
# ->> returns the value as text
cursor.execute(
    "SELECT stats->>'strength' AS strength FROM characters WHERE player_id = %s;",
    (1,)
)
strength = cursor.fetchone()[0]
print(f"Strength: {strength}")  # Output: Strength: 18

# -> returns the value as JSON (useful for nested data)
cursor.execute(
    "SELECT stats->'abilities' AS abilities FROM characters WHERE player_id = %s;",
    (1,)
)
```

### 10.2 Array Columns

```sql
CREATE TABLE spells (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100),
    tags TEXT[]   -- An array of text values
);
```

```python
# Inserting an array — just pass a Python list
cursor.execute(
    "INSERT INTO spells (name, tags) VALUES (%s, %s);",
    ("Fireball", ["fire", "aoe", "offensive"])
)
conn.commit()

# psycopg2 automatically converts PostgreSQL arrays to Python lists when fetching
cursor.execute(
    "SELECT name, tags FROM spells WHERE %s = ANY(tags);",
    ("fire",)   # ANY() checks if the value exists anywhere in the array
)
for name, tags in cursor.fetchall():
    print(f"{name}: {tags}")   # tags is already a Python list here
```

---

**Practice:**
1. Create a `player_profiles` table with a `JSONB` column called `preferences` (to store things like `{"theme": "dark", "notifications": True}`).
2. Write a Python function that inserts a new profile and then fetches it back, printing just the `theme` value from the JSON.

---

## Section 11: Building a Data Access Layer

As a project grows, having raw `cursor.execute()` calls scattered throughout your application becomes a mess. A **Data Access Layer (DAL)** — sometimes called a **Repository** — is a class that wraps all database operations for one table into one organised place.

This is the exact pattern used in Navy.

### 11.1 The Repository Pattern

```python
import psycopg2
from psycopg2.extras import RealDictCursor

class PlayerRepository:
    """
    Handles all database operations for the players table.
    All SQL for players lives here — nowhere else in the codebase.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    def _connect(self):
        """Returns a fresh connection. In production, use a pool instead."""
        return psycopg2.connect(self.dsn)

    def get_all(self) -> list[dict]:
        """Returns all players, ordered by level descending."""
        with self._connect() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, name, level, gold, role FROM players ORDER BY level DESC;"
            )
            return cursor.fetchall()

    def get_by_id(self, player_id: int) -> dict | None:
        """Returns one player by ID, or None if they don't exist."""
        with self._connect() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM players WHERE id = %s;",
                (player_id,)
            )
            return cursor.fetchone()

    def create(self, name: str, level: int, role: str) -> int:
        """Creates a new player and returns their new ID."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO players (name, level, role) VALUES (%s, %s, %s) RETURNING id;",
                (name, level, role)
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def update_gold(self, player_id: int, amount: int) -> bool:
        """
        Adjusts a player's gold by `amount` (positive to add, negative to subtract).
        Returns True if the player existed, False if they weren't found.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET gold = gold + %s WHERE id = %s;",
                (amount, player_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, player_id: int) -> bool:
        """Deletes a player. Returns True if they were found and deleted."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE id = %s;", (player_id,))
            conn.commit()
            return cursor.rowcount > 0
```

### 11.2 Using the Repository

```python
DSN = "postgresql://admin:secret@localhost:5432/game_db"

players = PlayerRepository(DSN)

# Create a new player
new_id = players.create("Percival", 8, "Knight")
print(f"Created player with ID: {new_id}")

# Award them some gold
awarded = players.update_gold(new_id, 500)
print(f"Gold awarded: {awarded}")

# List all players
for player in players.get_all():
    print(f"{player['name']} — Level {player['level']}, {player['gold']} gold")

# Clean up
players.delete(new_id)
```

> [!NOTE]
> The Repository Pattern means your application code never touches SQL directly — it just calls repository methods. If you ever need to change how data is stored (e.g. swap PostgreSQL for SQLite in tests), you only change the repository class, not every file in your project.

---

**Practice:**
1. Build a `QuestRepository` class with at minimum: `get_all()`, `get_by_id(id)`, `create(title, difficulty)`, and `mark_complete(quest_id, player_id)`.
2. `mark_complete` should set the quest's `status` to `'complete'` and record which player completed it — wrap both updates in a transaction.

---

## Section 12: Async PostgreSQL with asyncpg

`psycopg2` is synchronous — while it waits for the database to respond, it blocks the entire thread. For async web frameworks like **FastAPI**, this is a problem. The solution is `asyncpg` — an async PostgreSQL library built for Python's `asyncio`.

```bash
pip install asyncpg
```

### 12.1 Connecting and Querying Asynchronously

```python
import asyncio
import asyncpg

async def get_all_players():
    # await pauses this function until the connection is ready
    conn = await asyncpg.connect("postgresql://admin:secret@localhost:5432/game_db")

    # fetch() returns a list of Record objects — they work like dicts
    rows = await conn.fetch(
        "SELECT id, name, level FROM players ORDER BY level DESC;"
    )

    for row in rows:
        print(f"{row['name']} — Level {row['level']}")

    await conn.close()

asyncio.run(get_all_players())
```

### 12.2 Parameterized Queries in asyncpg

asyncpg uses `$1`, `$2`, `$3` placeholders — **not** `%s` like psycopg2. The number corresponds to the position of the argument in the list.

```python
async def get_player_by_name(name: str):
    conn = await asyncpg.connect("postgresql://admin:secret@localhost:5432/game_db")

    # $1 = first argument, $2 = second, etc.
    row = await conn.fetchrow(
        "SELECT * FROM players WHERE name = $1;",
        name
    )

    await conn.close()
    return dict(row) if row else None
```

The different fetch methods in asyncpg:
- `conn.fetch()` — all rows as a list
- `conn.fetchrow()` — one row (or `None`)
- `conn.fetchval()` — one single value (e.g. a count or an ID)
- `conn.execute()` — run a command that doesn't return rows (INSERT, UPDATE, DELETE)

### 12.3 Connection Pools with asyncpg

Opening a new connection for every query is wasteful in asyncpg just as it is in psycopg2. Use a pool at the application level.

```python
import asyncpg

# Create the pool once when the application starts
async def create_pool():
    return await asyncpg.create_pool(
        "postgresql://admin:secret@localhost:5432/game_db",
        min_size=2,
        max_size=10
    )

async def get_all_players(pool):
    # async with pool.acquire() borrows a connection, releases it when done
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, level FROM players;")
        return [dict(row) for row in rows]

# In FastAPI, you'd create the pool in the startup event:
# app.state.db = await create_pool()
```

### 12.4 Inserting and Modifying Data with asyncpg

```python
async def create_player(pool, name: str, level: int, role: str) -> int:
    async with pool.acquire() as conn:
        # fetchval() gets back the single value from RETURNING
        new_id = await conn.fetchval(
            "INSERT INTO players (name, level, role) VALUES ($1, $2, $3) RETURNING id;",
            name, level, role
        )
        return new_id

async def award_gold(pool, player_id: int, amount: int) -> bool:
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE players SET gold = gold + $1 WHERE id = $2;",
            amount, player_id
        )
        # execute() returns a string like "UPDATE 1" — split and check the count
        rows_affected = int(result.split()[-1])
        return rows_affected > 0
```

### 12.5 psycopg2 vs asyncpg — When to Use Which

| | psycopg2 | asyncpg |
|---|---|---|
| **Use with** | Flask, scripts, CLI tools, data pipelines | FastAPI, aiohttp, async web servers |
| **Parameters** | `%s` | `$1`, `$2`, `$3`... |
| **Rows return as** | Tuples (or dicts with RealDictCursor) | Record objects (dict-like by default) |
| **Speed** | Fast | Faster (uses PostgreSQL binary protocol) |
| **Syntax for RETURNING** | `cursor.fetchone()[0]` | `conn.fetchval(...)` |

> [!NOTE]
> Your Navy project currently uses `postgres.js` — the Node.js equivalent of asyncpg. If you ever build the Python version of Navy, asyncpg is the natural match: async, fast, and very similar in feel. For Python scripts and data tooling, stick with psycopg2 — it's simpler and more than fast enough.

---

**Practice:**
1. Write an async function `fetch_top_players(pool, n: int)` using asyncpg that returns the top `n` players by level as a list of plain Python dicts.
2. Write an async function `bulk_award_guild_gold(pool, guild_id: int, amount: int)` that gives every player in a specific guild the same gold bonus, using a single `UPDATE` statement with `$1` and `$2` parameters.

---

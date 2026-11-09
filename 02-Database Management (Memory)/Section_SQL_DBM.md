## SQL & Database Management

SQL (Structured Query Language) is the language you use to talk to a relational database. Think of it like Python for data — instead of writing logic that runs on your machine, you write instructions that the database executes against your stored data.

These notes take you from the basics (what even is a table?) all the way through to advanced topics like window functions and query optimization. Work through them in order — each section builds on the last.

---

## Section 1: What is a Database?

A database is an organised collection of data. The software that controls it — storing, retrieving, and protecting that data — is called a **Database Management System (DBMS)**. PostgreSQL, MySQL, and SQLite are all examples of DBMS software.

**Relational databases** (the type these notes focus on) organise everything into tables. Think of each table like a tab in a spreadsheet. Each table holds one type of thing, and tables can be linked together — that linking is where the real power comes from.

### 1.1 Tables, Rows & Columns

| Term | What it means | Game example |
|---|---|---|
| **Table** | A collection of related data | The `players` list |
| **Row** | One record — one thing | Arthur's entry |
| **Column** | One property of each thing | The player's `name` or `level` |
| **Schema** | The blueprint for all your tables | The game's database design document |

```sql
-- This is what a players table looks like when you picture it:
-- +----+----------+-------+--------+
-- | id |   name   | level |  gold  |
-- +----+----------+-------+--------+
-- |  1 | Arthur   |    15 |  2500  |
-- |  2 | Merlin   |    22 |   800  |
-- |  3 | Lancelot |    18 |  1200  |
-- +----+----------+-------+--------+
```

### 1.2 Primary Keys & Foreign Keys

A **Primary Key** is a column that uniquely identifies each row. No two rows can ever share the same primary key. Think of it like a player's unique ID card.

A **Foreign Key** is a column in one table that points to the primary key of another. It's how you link two tables together — for example, an inventory item pointing to the player it belongs to.

```sql
-- The 'id' column is the PRIMARY KEY — every player has a unique one
-- players table:
-- +----+----------+-------+
-- | id |   name   | level |
-- +----+----------+-------+
-- |  1 | Arthur   |    15 |
-- |  2 | Merlin   |    22 |
-- +----+----------+-------+

-- The 'player_id' column is a FOREIGN KEY — it references players.id
-- inventory table:
-- +----+-----------+-----------+
-- | id | player_id | item_name |
-- +----+-----------+-----------+
-- |  1 |     1     | Sword     |  <- belongs to Arthur (id = 1)
-- |  2 |     1     | Potion    |  <- also belongs to Arthur
-- |  3 |     2     | Staff     |  <- belongs to Merlin (id = 2)
-- +----+-----------+-----------+
```

### 1.3 Types of Relationships

| Type | What it means | Example |
|---|---|---|
| **One-to-One** | One row in Table A links to exactly one in Table B | One player has one character profile |
| **One-to-Many** | One row in Table A links to many rows in Table B | One player has many inventory items |
| **Many-to-Many** | Many rows in Table A link to many rows in Table B | Players join many guilds; guilds have many players |

> [!NOTE]
> Many-to-Many relationships need a **junction table** in between. For example, a `guild_members` table would have a `player_id` column and a `guild_id` column — linking the two sides together.

---

**Practice:** Sketch out the tables you'd need for a simple RPG game. Include at least `players`, `quests`, and `inventory`. Write down what columns each table would have and mark which column is the primary key in each.

---

## Section 2: Your First SELECT Statement

`SELECT` is how you read data from a database. You'll write `SELECT` more than any other SQL statement — it's the foundation of everything.

### 2.1 Basic SELECT

```sql
-- Get ALL columns from the players table (the * means "everything")
SELECT * FROM players;

-- Get only specific columns — this is almost always better than *
SELECT name, level FROM players;

-- Give a column a temporary nickname using AS (called an alias)
-- The original column name in the table is unchanged — this is just for display
SELECT name AS player_name, level AS current_level FROM players;
```

### 2.2 DISTINCT — Remove Duplicates

```sql
-- If multiple players have the same role, this only returns each role once
SELECT DISTINCT role FROM players;
```

### 2.3 Building Strings From Columns

```sql
-- You can combine text and column values using || (the concatenation operator)
SELECT name || ' is Level ' || level AS description FROM players;
-- Output: "Arthur is Level 15"
```

> [!NOTE]
> `SELECT *` is fine when you're exploring data, but in real code you should always name the columns you need. It makes your intent clear and means you won't accidentally pull in columns that were added to the table later.

---

**Practice:**
1. Write a query that returns only the `name` and `gold` columns from a `players` table.
2. Write a query that returns each unique `role` from a `characters` table, with no duplicates.
3. Write a query that returns `name` aliased as `"Hero Name"` and `level` aliased as `"Power Level"`.

---

## Section 3: Filtering with WHERE

`WHERE` lets you describe which rows you want. Without it, `SELECT` returns every single row. With it, you get only what matches your condition.

### 3.1 Basic Comparisons

```sql
-- Exact match
SELECT * FROM players WHERE name = 'Arthur';

-- Not equal
SELECT * FROM players WHERE role != 'Mage';

-- Numeric comparisons
SELECT * FROM players WHERE level > 10;
SELECT * FROM players WHERE gold <= 500;
SELECT * FROM players WHERE level >= 15;
```

### 3.2 Combining Conditions

```sql
-- AND — both conditions must be true for a row to be included
SELECT * FROM players WHERE level > 10 AND guild = 'Knights of Camelot';

-- OR — at least one condition must be true
SELECT * FROM players WHERE role = 'Warrior' OR role = 'Paladin';

-- NOT — flips the condition
SELECT * FROM players WHERE NOT role = 'Mage';
```

### 3.3 BETWEEN, IN, LIKE

```sql
-- BETWEEN — checks if a value falls within a range (both ends are included)
SELECT * FROM players WHERE level BETWEEN 10 AND 20;

-- IN — checks if a value matches any item in a list
SELECT * FROM players WHERE role IN ('Warrior', 'Paladin', 'Knight');

-- NOT IN — the opposite of IN
SELECT * FROM players WHERE role NOT IN ('Mage', 'Warlock');

-- LIKE — pattern matching
-- % means "zero or more of any character"
-- _ means "exactly one of any character"
SELECT * FROM players WHERE name LIKE 'A%';      -- starts with A
SELECT * FROM players WHERE name LIKE '%ur';     -- ends with 'ur'
SELECT * FROM players WHERE name LIKE 'Art___';  -- "Art" + exactly 3 more characters
```

### 3.4 NULL Values

`NULL` means "no value" — it is not zero, it is not an empty string. It's the complete absence of data. You can't check for it with `=` — you use `IS NULL` instead.

```sql
-- Find players who haven't joined a guild yet
SELECT * FROM players WHERE guild_id IS NULL;

-- Find players who have a guild
SELECT * FROM players WHERE guild_id IS NOT NULL;
```

> [!NOTE]
> `NULL = NULL` doesn't evaluate to `TRUE` in SQL. It evaluates to nothing at all (`UNKNOWN`). That's why `= NULL` will never find anything — you must always use `IS NULL`.

---

**Practice:**
1. Find all players with a `level` between 12 and 20 (inclusive) using `BETWEEN`.
2. Find all players whose `role` is either `'Mage'` or `'Archer'` using `IN`.
3. Find all players whose `name` starts with the letter `'M'`.
4. Find all players who have no `guild_id` set.

---

## Section 4: Sorting & Limiting Results

Once you've selected and filtered your data, you can control the order it comes back in and how many rows you see at once.

### 4.1 ORDER BY

```sql
-- Sort by level, lowest first (ASC = ascending, which is the default)
SELECT name, level FROM players ORDER BY level ASC;

-- Sort by level, highest first
SELECT name, level FROM players ORDER BY level DESC;

-- Sort by multiple columns: first by guild, then by level within each guild
SELECT name, guild, level FROM players ORDER BY guild ASC, level DESC;
```

### 4.2 LIMIT

```sql
-- Get only the top 5 players by level
SELECT name, level FROM players ORDER BY level DESC LIMIT 5;

-- Get just the single highest-level player
SELECT name, level FROM players ORDER BY level DESC LIMIT 1;
```

### 4.3 OFFSET — Skipping Rows (Pagination)

`OFFSET` tells the database how many rows to skip before returning results. Combined with `LIMIT`, this is how you build pagination — page 1, page 2, page 3, and so on.

```sql
-- Page 1: the first 10 players
SELECT name, level FROM players ORDER BY level DESC LIMIT 10 OFFSET 0;

-- Page 2: the next 10
SELECT name, level FROM players ORDER BY level DESC LIMIT 10 OFFSET 10;

-- Page 3
SELECT name, level FROM players ORDER BY level DESC LIMIT 10 OFFSET 20;
```

> [!NOTE]
> The formula for any page is: `OFFSET = (page_number - 1) * page_size`. So page 3 with 10 per page = `OFFSET 20`.

---

**Practice:**
1. Write a query to get the names and gold of the 3 richest players.
2. Write a query to get page 2 of players sorted alphabetically by name, with 5 players per page.

---

## Section 5: Aggregate Functions & Grouping

Aggregate functions crunch multiple rows down into a single answer. They're how you answer questions like "what's the total gold?" or "how many players are in each guild?"

### 5.1 The Core Aggregate Functions

```sql
-- COUNT — how many rows are there?
SELECT COUNT(*) FROM players;                -- Total number of players
SELECT COUNT(guild_id) FROM players;         -- Only counts rows where guild_id is not NULL

-- SUM — add up all values in a column
SELECT SUM(gold) FROM players;               -- Total gold across all players

-- AVG — the average value
SELECT AVG(level) FROM players;              -- Average player level

-- MIN and MAX — the smallest and largest value
SELECT MIN(level) FROM players;              -- Lowest level player
SELECT MAX(gold) FROM players;               -- The most gold any one player has
```

### 5.2 GROUP BY — Grouping Your Results

`GROUP BY` splits your rows into groups and runs an aggregate on each group. Think of it as sorting your players into piles by role, then counting how many are in each pile.

```sql
-- How many players have each role?
SELECT role, COUNT(*) AS player_count
FROM players
GROUP BY role;

-- Average level and highest level per role
SELECT role, AVG(level) AS avg_level, MAX(level) AS max_level
FROM players
GROUP BY role
ORDER BY avg_level DESC;
```

### 5.3 HAVING — Filtering Your Groups

`WHERE` filters individual rows before grouping happens. `HAVING` filters groups after the aggregation is done. If you want to filter based on the result of an aggregate function, you need `HAVING`.

```sql
-- Only show guilds with more than 5 members
SELECT guild, COUNT(*) AS member_count
FROM players
GROUP BY guild
HAVING COUNT(*) > 5;

-- Only show guilds where the average level is above 15
SELECT guild, AVG(level) AS avg_level
FROM players
GROUP BY guild
HAVING AVG(level) > 15
ORDER BY avg_level DESC;
```

> [!NOTE]
> **WHERE vs HAVING:** `WHERE` filters rows before grouping — you cannot use aggregate functions here. `HAVING` filters groups after aggregation — you can use aggregate functions here. If you're ever unsure which to use, ask yourself: "am I filtering a row, or am I filtering a group?"

---

**Practice:**
1. Count how many players have each `role` (e.g., 5 Warriors, 3 Mages...).
2. Find the total `gold` held by players in each `guild`.
3. Find all guilds where the total gold held by members is more than 10,000.

---

## Section 6: JOINs — Combining Tables

A JOIN lets you pull data from two or more tables at the same time by connecting them on a shared column — usually a foreign key. This is where the power of a relational database really shows.

### 6.1 INNER JOIN

Returns only rows where there's a match in **both** tables. If a player has no guild, they won't appear. Think of a Venn diagram — you only get the overlapping centre.

```sql
-- Get each player's name and the name of their guild
SELECT players.name, guilds.guild_name
FROM players
INNER JOIN guilds ON players.guild_id = guilds.id;
-- Players without a guild_id won't appear in these results at all
```

### 6.2 LEFT JOIN

Returns **all rows from the left table** (players), plus any matching data from the right table (guilds). If a player has no guild, they still appear — the guild columns just show `NULL`.

```sql
-- Get ALL players, and show their guild name if they have one
SELECT players.name, guilds.guild_name
FROM players
LEFT JOIN guilds ON players.guild_id = guilds.id;
-- Players without a guild still appear, with NULL in the guild_name column
```

### 6.3 RIGHT JOIN

The mirror of LEFT JOIN — returns **all rows from the right table**, with matching data from the left. Less commonly used than LEFT JOIN.

```sql
-- Get all guilds, including empty ones with no members
SELECT players.name, guilds.guild_name
FROM players
RIGHT JOIN guilds ON players.guild_id = guilds.id;
```

### 6.4 FULL OUTER JOIN

Returns everything from both tables. Rows with no match on either side still appear — the missing side just shows `NULL`.

```sql
-- Get all players AND all guilds, whether they're linked or not
SELECT players.name, guilds.guild_name
FROM players
FULL OUTER JOIN guilds ON players.guild_id = guilds.id;
```

### 6.5 Joining Multiple Tables

You can chain JOINs to pull data from three or more tables at once.

```sql
-- Player name, their guild, and their inventory items — all in one query
SELECT
    p.name    AS player,
    g.guild_name AS guild,
    i.item_name  AS item
FROM players p
LEFT JOIN guilds    g ON p.guild_id = g.id
LEFT JOIN inventory i ON i.player_id = p.id
ORDER BY p.name;
```

Notice the short aliases: `p` for players, `g` for guilds, `i` for inventory. This keeps things readable when you're joining several tables.

> [!NOTE]
> **Quick JOIN guide:** Only matched rows from both sides → `INNER JOIN`. All rows from the left, matched or not → `LEFT JOIN` (most common). Everything from both sides, matched or not → `FULL OUTER JOIN`.

---

**Practice:**
1. Write a query that returns every player's name and the name of their guild. Use `LEFT JOIN` so players without a guild still appear.
2. Write a query that lists every quest name and the name of the player who accepted it. Include quests that haven't been accepted yet.

---

## Section 7: Modifying Data

Reading data is only half the job. `INSERT`, `UPDATE`, and `DELETE` are how you add, change, and remove rows.

### 7.1 INSERT — Adding New Rows

```sql
-- Insert a single row
INSERT INTO players (name, level, gold, role)
VALUES ('Percival', 8, 300, 'Knight');

-- Insert multiple rows in one statement
INSERT INTO players (name, level, gold, role)
VALUES
    ('Gawain',  12, 750, 'Warrior'),
    ('Tristan', 10, 500, 'Archer'),
    ('Isolde',  14, 920, 'Mage');
```

### 7.2 UPDATE — Changing Existing Rows

```sql
-- Update Arthur's gold
UPDATE players
SET gold = 3000
WHERE name = 'Arthur';

-- Update multiple columns at the same time
UPDATE players
SET level = 16, gold = gold + 500
WHERE name = 'Arthur';
```

> [!NOTE]
> **Always include a `WHERE` clause on UPDATE.** Without it, you update every row in the table. `UPDATE players SET gold = 0` would zero out every single player's gold.

### 7.3 DELETE — Removing Rows

```sql
-- Delete one specific player
DELETE FROM players WHERE name = 'Percival';

-- Delete all players below level 5
DELETE FROM players WHERE level < 5;
```

> [!NOTE]
> **Always include `WHERE` on DELETE too.** `DELETE FROM players` with no condition wipes every row in the table.

### 7.4 TRUNCATE — Emptying a Table Fast

`TRUNCATE` removes all rows from a table immediately, without scanning them one by one. It's much faster than `DELETE` on large tables.

```sql
-- Clear the entire combat_log table instantly
TRUNCATE TABLE combat_log;

-- Use DELETE if you need the operation to be rollback-able row by row,
-- or if you need row-level triggers to fire.
-- Use TRUNCATE when you just want the table empty, fast.
```

---

**Practice:**
1. Insert a new player named `'Bedivere'` with `level = 9`, `gold = 450`, and `role = 'Knight'`.
2. Give every player with the role `'Mage'` a 10% gold bonus: `gold = gold * 1.10`.
3. Delete all players whose `level` is 1.

---

## Section 8: Table Design & Constraints

A well-designed table doesn't just hold data — it actively prevents bad data from being stored. Constraints are rules you bake into the table structure, and the database enforces them automatically.

### 8.1 CREATE TABLE

```sql
CREATE TABLE players (
    id         SERIAL PRIMARY KEY,        -- Auto-incrementing unique ID (1, 2, 3...)
    name       VARCHAR(100) NOT NULL,     -- Text up to 100 characters, required
    level      INTEGER DEFAULT 1,         -- Whole number, defaults to 1 if not provided
    gold       NUMERIC(10, 2) DEFAULT 0,  -- Decimal number with 2 decimal places
    role       VARCHAR(50),               -- Text, optional (can be NULL)
    guild_id   INTEGER,                   -- Will link to the guilds table
    created_at TIMESTAMP DEFAULT NOW()    -- Auto-filled with the current date and time
);
```

### 8.2 Common Data Types

| Type | Use it for | Example values |
|---|---|---|
| `SERIAL` | Auto-incrementing IDs | 1, 2, 3, 4... |
| `INTEGER` | Whole numbers | `15`, `-3`, `0` |
| `NUMERIC(p, s)` | Exact decimals — money, stats | `19.99`, `1200.50` |
| `VARCHAR(n)` | Text with a maximum length | `'Arthur'`, `'Knight'` |
| `TEXT` | Unlimited length text | Long quest descriptions |
| `BOOLEAN` | True/False | `TRUE`, `FALSE` |
| `DATE` | A date, no time | `2025-06-15` |
| `TIMESTAMP` | Date and time together | `2025-06-15 14:30:00` |

### 8.3 Constraints

```sql
CREATE TABLE quests (
    id          SERIAL PRIMARY KEY,

    -- NOT NULL: this column must always have a value — it can never be empty
    title       VARCHAR(200) NOT NULL,

    -- UNIQUE: no two rows can share the same value in this column
    quest_code  VARCHAR(20) UNIQUE,

    -- DEFAULT: if no value is provided, use this fallback
    status      VARCHAR(20) DEFAULT 'open',

    -- CHECK: only accept values that pass this condition
    difficulty  INTEGER CHECK (difficulty BETWEEN 1 AND 10),

    -- FOREIGN KEY: the value must exist in the players table's id column
    -- ON DELETE SET NULL: if that player is deleted, set this column to NULL
    accepted_by INTEGER REFERENCES players(id) ON DELETE SET NULL
);
```

### 8.4 ON DELETE Behaviour for Foreign Keys

When you delete a row, what happens to other rows that reference it?

| Option | What happens |
|---|---|
| `ON DELETE CASCADE` | Automatically deletes the child rows too |
| `ON DELETE SET NULL` | Sets the foreign key column to `NULL` |
| `ON DELETE RESTRICT` | Blocks the delete if child rows exist (the default) |

### 8.5 Changing an Existing Table

```sql
-- Add a new column to an existing table
ALTER TABLE players ADD COLUMN email VARCHAR(255);

-- Remove a column
ALTER TABLE players DROP COLUMN email;

-- Change a column's data type
ALTER TABLE players ALTER COLUMN name TYPE TEXT;

-- Add a constraint after the table already exists
ALTER TABLE players ADD CONSTRAINT unique_player_name UNIQUE (name);

-- Delete the entire table (permanent — cannot be undone)
DROP TABLE players;

-- Safer version: only drop it if it actually exists
DROP TABLE IF EXISTS players;
```

---

**Practice:**
1. Write a `CREATE TABLE` statement for an `inventory` table with: `id` (primary key), `player_id` (foreign key referencing `players`), `item_name` (required text), `quantity` (integer, default 1), and `equipped` (boolean, default false).
2. Add a `CHECK` constraint to `quantity` ensuring it can never go below 0.

---

## Section 9: Subqueries & CTEs

Sometimes one `SELECT` isn't enough. Subqueries and CTEs let you build queries where the answer to one question feeds into another — like using an intermediate result as the input for your main query.

### 9.1 Subqueries in WHERE

A subquery inside `WHERE` filters rows based on the result of another query running alongside it.

```sql
-- Find all players whose level is above the average level
SELECT name, level
FROM players
WHERE level > (SELECT AVG(level) FROM players);

-- Find all players who have accepted at least one quest
SELECT name
FROM players
WHERE id IN (SELECT accepted_by FROM quests WHERE accepted_by IS NOT NULL);
```

### 9.2 Scalar Subqueries in SELECT

A scalar subquery returns exactly one value, and you can use it as a calculated column in your `SELECT`.

```sql
-- Show each player's level and how far they are behind the top player
SELECT
    name,
    level,
    (SELECT MAX(level) FROM players) AS highest_level,
    (SELECT MAX(level) FROM players) - level AS levels_behind_leader
FROM players
ORDER BY level DESC;
```

### 9.3 Subqueries in FROM (Derived Tables)

You can use the result of a subquery as if it were a table inside your `FROM` clause.

```sql
-- Get the average gold of only the top 10 players by level
SELECT AVG(top_players.gold) AS avg_gold_of_top_10
FROM (
    SELECT gold FROM players ORDER BY level DESC LIMIT 10
) AS top_players;
```

### 9.4 CTEs — Making Complex Queries Readable

A CTE (Common Table Expression) is like giving a subquery a name. Instead of one giant nested query, you write it as a sequence of clearly named steps using the `WITH` keyword.

```sql
-- Step 1: name the subquery so it's reusable and readable
WITH high_level_players AS (
    SELECT id, name, level, gold
    FROM players
    WHERE level >= 15
)
-- Step 2: use it like a table in the main query
SELECT
    h.name,
    h.level,
    g.guild_name
FROM high_level_players h
LEFT JOIN guilds g ON h.guild_id = g.id
ORDER BY h.level DESC;
```

You can chain multiple CTEs together — each one can reference the ones above it:

```sql
WITH
-- Step 1: find guilds with more than 5 members
large_guilds AS (
    SELECT guild_id, COUNT(*) AS member_count
    FROM players
    WHERE guild_id IS NOT NULL
    GROUP BY guild_id
    HAVING COUNT(*) > 5
),
-- Step 2: get the names of those guilds
guild_details AS (
    SELECT g.guild_name, lg.member_count
    FROM guilds g
    INNER JOIN large_guilds lg ON g.id = lg.guild_id
)
-- Main query
SELECT guild_name, member_count
FROM guild_details
ORDER BY member_count DESC;
```

> [!NOTE]
> CTEs don't make your query run faster by themselves. They make it easier to read and reason about. Think of each CTE as a labelled step in a recipe — instead of one unreadable wall of nested SQL, you get named, logical steps.

### 9.5 Recursive CTEs

A recursive CTE can reference itself. This is how you query hierarchical data — like a skill tree where skills unlock other skills.

```sql
-- Each skill can have a parent skill (the one that must be learned first)
WITH RECURSIVE skill_tree AS (
    -- Starting point: top-level skills (no parent)
    SELECT id, skill_name, parent_skill_id, 1 AS depth
    FROM skills
    WHERE parent_skill_id IS NULL

    UNION ALL

    -- Recursive step: find skills unlocked by the ones we already found
    SELECT s.id, s.skill_name, s.parent_skill_id, st.depth + 1
    FROM skills s
    INNER JOIN skill_tree st ON s.parent_skill_id = st.id
)
SELECT skill_name, depth
FROM skill_tree
ORDER BY depth, skill_name;
```

---

**Practice:**
1. Write a query that finds all players whose `gold` is above the overall average gold.
2. Rewrite that query as a CTE using `WITH` — give it a readable name.

---

## Section 10: Indexes

An index is like the index at the back of a book. Without one, the database reads every single row in the table to find what you're looking for. With one on the right column, it jumps straight to the answer.

### 10.1 Creating a Basic Index

```sql
-- Create an index on the name column
-- This speeds up queries like: WHERE name = 'Arthur' or ORDER BY name
CREATE INDEX idx_players_name ON players(name);

-- Always index foreign key columns — joins and lookups on them are very common
CREATE INDEX idx_inventory_player_id ON inventory(player_id);
```

### 10.2 Unique Indexes

A unique index both speeds up lookups AND enforces uniqueness — no two rows can have the same value in that column.

```sql
-- No two players can share the same email address
CREATE UNIQUE INDEX idx_players_email ON players(email);
```

> [!NOTE]
> When you add `UNIQUE` to a column in `CREATE TABLE`, PostgreSQL automatically creates a unique index behind the scenes. These two approaches achieve the same thing.

### 10.3 Composite Indexes

You can index multiple columns together. This is most useful when your queries filter by two specific columns at the same time.

```sql
-- Speeds up queries like: WHERE role = 'Mage' AND level > 10
CREATE INDEX idx_players_role_level ON players(role, level);
```

> [!NOTE]
> Column order matters in composite indexes. `(role, level)` helps queries that filter on `role` alone, or on `role + level` together. But it won't help a query that only filters on `level` alone — you'd need a separate index for that.

### 10.4 When NOT to Add an Index

More indexes isn't always better. Every index:
- **Speeds up reads** (SELECT, WHERE, JOIN, ORDER BY)
- **Slows down writes** (INSERT, UPDATE, DELETE all have to update the index too)
- **Takes up disk space**

Don't index:
- Small tables — the database will just read the whole thing anyway
- Columns you rarely search or sort by
- Boolean columns or columns with very few distinct values (e.g. `is_alive` — true/false only — an index here gives you nothing useful)

```sql
-- See existing indexes on a table in PostgreSQL
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'players';

-- Remove an index you no longer need
DROP INDEX idx_players_name;
```

---

**Practice:**
1. Create an index on the `status` column of a `quests` table.
2. Create a composite index on `(guild_id, level)` for the `players` table.
3. Think about it: would you add an index to an `is_alive` boolean column? Why or why not?

---

## Section 11: Transactions

A transaction is a group of SQL statements that are treated as a single unit. Either all of them succeed, or none of them do. This protects your data when something goes wrong mid-operation.

### 11.1 Why Transactions Matter

Imagine a player buying an item from the shop. Two things need to happen:
1. Deduct 500 gold from the player
2. Add the item to their inventory

If step 1 succeeds but step 2 crashes, the player loses gold and gets nothing. A transaction prevents this — if anything fails, the whole thing is rolled back as if it never happened.

### 11.2 BEGIN, COMMIT, ROLLBACK

```sql
-- Start the transaction
BEGIN;

-- Do your work
UPDATE players SET gold = gold - 500 WHERE id = 1;
INSERT INTO inventory (player_id, item_name) VALUES (1, 'Enchanted Sword');

-- Everything worked — make it permanent
COMMIT;
```

```sql
-- Start the transaction
BEGIN;

UPDATE players SET gold = gold - 500 WHERE id = 1;

-- Something went wrong — undo everything since BEGIN
ROLLBACK;
-- The gold deduction is reversed, as if it never happened
```

### 11.3 SAVEPOINT — Partial Rollbacks

A `SAVEPOINT` marks a point inside a transaction that you can roll back to, without losing all the work you've done before it.

```sql
BEGIN;

UPDATE players SET gold = gold - 500 WHERE id = 1;
SAVEPOINT before_item_insert;

INSERT INTO inventory (player_id, item_name) VALUES (1, 'Enchanted Sword');

-- Problem with the insert — roll back to just before it
ROLLBACK TO SAVEPOINT before_item_insert;

-- The gold deduction is still in place, but the failed insert is gone
-- Now try again with corrected data
INSERT INTO inventory (player_id, item_name, quantity) VALUES (1, 'Enchanted Sword', 1);

COMMIT;
```

### 11.4 ACID Properties

ACID is the set of guarantees every transaction in a proper database provides:

| Property | Simple version |
|---|---|
| **Atomicity** | All or nothing — any failure rolls back everything |
| **Consistency** | Data always stays valid — constraints are never broken |
| **Isolation** | Two transactions running at the same time don't step on each other |
| **Durability** | Once committed, the data survives even if the server crashes |

> [!NOTE]
> In PostgreSQL, every SQL statement you run is automatically wrapped in its own implicit transaction. You only need `BEGIN` and `COMMIT` when you want to group multiple statements together as one atomic unit.

---

**Practice:**
1. Write a transaction that transfers 200 gold from player `id = 1` to player `id = 2`. Include both the deduction and the addition.
2. Add a `SAVEPOINT` between the deduction and the addition.

---

## Section 12: Window Functions

Window functions are one of SQL's most powerful features. They let you run a calculation across a set of related rows — without collapsing those rows into one like `GROUP BY` does. Every row stays visible; the window function just adds a calculated value alongside it.

### 12.1 The OVER() Clause

The `OVER()` clause is what makes a function a window function. Compare:

```sql
-- Without OVER: aggregate — collapses all rows down to one result
SELECT AVG(level) FROM players;
-- Returns: one number (e.g. 16.7)

-- With OVER: window function — adds the result as a column on every row
SELECT name, level, AVG(level) OVER() AS overall_avg_level
FROM players;
-- Returns: all players, each with the overall average shown on their row
```

### 12.2 PARTITION BY — Grouped Windows

`PARTITION BY` divides the rows into groups before calculating. It's like `GROUP BY` — but all the rows are still visible in the result.

```sql
-- Show each player's level AND the average level for their specific role
SELECT
    name,
    role,
    level,
    AVG(level) OVER (PARTITION BY role) AS avg_level_in_their_role
FROM players
ORDER BY role, level;
-- Mages see the Mage average; Warriors see the Warrior average
```

### 12.3 ROW_NUMBER() — Assigning a Position

`ROW_NUMBER()` gives each row a unique sequential number within its partition. No ties — every row gets its own number.

```sql
-- Rank each player within their guild by level (highest = rank 1)
SELECT
    name,
    guild_id,
    level,
    ROW_NUMBER() OVER (PARTITION BY guild_id ORDER BY level DESC) AS rank_in_guild
FROM players;
```

### 12.4 RANK() and DENSE_RANK() — Handling Ties

Both of these handle ties differently from `ROW_NUMBER()`. When two rows are equal:
- `RANK()` gives them the same number, then skips the next number(s)
- `DENSE_RANK()` gives them the same number, then continues without skipping

```sql
SELECT
    name,
    level,
    RANK()       OVER (ORDER BY level DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY level DESC) AS dense_rank
FROM players;

-- If two players are both Level 20:
-- RANK():       1, 1, 3, 4...   (skips 2 because two people share rank 1)
-- DENSE_RANK(): 1, 1, 2, 3...   (no gaps — the next distinct level is rank 2)
```

### 12.5 LAG() and LEAD() — Looking at Neighbouring Rows

`LAG()` looks at the row before the current one. `LEAD()` looks at the row after. Both are relative to the ordering you specify.

```sql
-- For each combat log entry, show the previous damage dealt alongside it
SELECT
    fight_id,
    damage_dealt,
    LAG(damage_dealt, 1) OVER (ORDER BY fight_id) AS previous_damage,
    damage_dealt - LAG(damage_dealt, 1) OVER (ORDER BY fight_id) AS change_from_last
FROM combat_log
WHERE player_id = 1;
-- The first row will have NULL for previous_damage — there's no row before it
```

### 12.6 Running Totals with SUM() OVER

```sql
-- Track Arthur's cumulative gold earned quest by quest
SELECT
    quest_name,
    gold_reward,
    SUM(gold_reward) OVER (
        PARTITION BY player_id
        ORDER BY completed_at
    ) AS total_gold_earned_so_far
FROM completed_quests
WHERE player_id = 1;
```

> [!NOTE]
> Window functions run after `WHERE` filters the rows, but before the final `ORDER BY` sorts them. They can only appear in the `SELECT` list or `ORDER BY` — not inside `WHERE` or `GROUP BY`.

---

**Practice:**
1. Write a query that ranks all players globally by their `gold`, highest first, using `RANK()`.
2. Write a query that shows each player's `level` and the average level within their `guild`, using `PARTITION BY`.

---

## Section 13: Stored Procedures, Functions & Triggers

SQL lets you store reusable logic directly inside the database. Functions and stored procedures work like Python functions — but they live in your database rather than your code. Triggers are functions that fire automatically when something happens to a table.

### 13.1 Functions

A function takes inputs, does something, and returns a result. You create one with `CREATE OR REPLACE FUNCTION` (the `OR REPLACE` means it's safe to re-run when you update it).

```sql
-- A function that calculates a player's level-up bonus gold
CREATE OR REPLACE FUNCTION calculate_level_bonus(player_level INTEGER)
RETURNS INTEGER AS $$
BEGIN
    -- Every 5 levels earned = 100 bonus gold
    RETURN (player_level / 5) * 100;
END;
$$ LANGUAGE plpgsql;

-- Using the function in a query — it works like any other expression
SELECT name, level, calculate_level_bonus(level) AS bonus_gold
FROM players;
```

The `$$` markers are how PostgreSQL wraps the function body. `LANGUAGE plpgsql` is the procedural language used for writing logic with variables, loops, and `IF` statements inside PostgreSQL.

### 13.2 Stored Procedures

A procedure is similar to a function but is designed for running a sequence of actions — it doesn't have to return a value. You call it with `CALL` instead of using it inside a `SELECT`.

```sql
-- A procedure that levels up a player and rewards them with gold
CREATE OR REPLACE PROCEDURE level_up_player(p_player_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE players
    SET
        level = level + 1,
        gold  = gold + calculate_level_bonus(level + 1)
    WHERE id = p_player_id;

    INSERT INTO combat_log (player_id, event, created_at)
    VALUES (p_player_id, 'Level Up!', NOW());
END;
$$;

-- Call it like this — not SELECT
CALL level_up_player(1);
```

### 13.3 Triggers

A trigger is a function that the database calls automatically when a specific event happens on a table — an `INSERT`, `UPDATE`, or `DELETE`. You never call a trigger manually.

A trigger needs two parts:
1. A **trigger function** — the logic that runs
2. A **trigger declaration** — which attaches that function to a table and event

```sql
-- PART 1: The trigger function
-- This logs to an audit table whenever a player's gold changes
CREATE OR REPLACE FUNCTION log_gold_change()
RETURNS TRIGGER AS $$
BEGIN
    -- NEW is the row AFTER the update; OLD is the row BEFORE
    IF OLD.gold != NEW.gold THEN
        INSERT INTO gold_audit_log (player_id, old_gold, new_gold, changed_at)
        VALUES (NEW.id, OLD.gold, NEW.gold, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PART 2: Attach the trigger to the players table
CREATE TRIGGER trigger_log_gold_change
AFTER UPDATE ON players
FOR EACH ROW
EXECUTE FUNCTION log_gold_change();

-- Now whenever this runs...
UPDATE players SET gold = gold + 500 WHERE id = 1;
-- ...the trigger fires automatically and writes to gold_audit_log
```

### 13.4 BEFORE vs AFTER Triggers

| Type | When it runs | Common use case |
|---|---|---|
| `BEFORE` | Before the row is written | Validate or modify data before it's saved |
| `AFTER` | After the row is written | Log changes, update related tables |

> [!NOTE]
> Triggers run invisibly in the background, which makes them hard to debug if something goes wrong. Keep trigger logic simple and document what each one does. If a trigger is doing complex business logic, that work is usually better handled in your application code where it's easier to test and trace.

---

**Practice:**
1. Write a function `is_high_level(player_level INTEGER)` that returns `TRUE` if the level is 20 or above, and `FALSE` otherwise. (`RETURNS BOOLEAN`)
2. Write a trigger that automatically sets `updated_at = NOW()` on any row in the `players` table when it's updated.

---

## Section 14: Query Optimization

Once your tables hold thousands or millions of rows, some queries start getting slow. Query optimization is the skill of finding out why a query is slow and fixing it.

### 14.1 EXPLAIN — Reading the Query Plan

`EXPLAIN` shows you the plan the database will use to execute your query, without actually running it. It's how you see what's happening behind the scenes.

```sql
EXPLAIN SELECT * FROM players WHERE level > 10;
```

The two terms you'll see most in `EXPLAIN` output:

| Term | What it means |
|---|---|
| **Seq Scan** (Sequential Scan) | The database is reading the entire table row by row. Slow on large tables. |
| **Index Scan** | The database is using an index to jump directly to the relevant rows. Fast. |

### 14.2 EXPLAIN ANALYZE — Running It and Measuring It

`EXPLAIN ANALYZE` actually runs the query and shows real timing data alongside the plan.

```sql
EXPLAIN ANALYZE SELECT * FROM players WHERE level > 10;

-- Sample output:
-- Seq Scan on players  (cost=0.00..25.00 rows=500 width=100)
--                      (actual time=0.02..1.45 rows=487 loops=1)
-- Planning Time: 0.08 ms
-- Execution Time: 1.52 ms
```

- `cost` — a relative estimate of work, not milliseconds
- `actual time` — real milliseconds it took on your machine
- `rows` — how many rows were returned

### 14.3 Common Slow Query Patterns

```sql
-- SLOW: Using a function on a column inside WHERE prevents index use
SELECT * FROM players WHERE LOWER(name) = 'arthur';
-- FAST: Match the format your data is already stored in
SELECT * FROM players WHERE name = 'Arthur';

-- SLOW: Wildcard at the START of LIKE can't use an index
SELECT * FROM players WHERE name LIKE '%thur';
-- FAST: Wildcard only at the END can use an index
SELECT * FROM players WHERE name LIKE 'Art%';

-- SLOW: SELECT * when you only need 2 columns — fetches far more data than needed
SELECT * FROM players WHERE guild_id = 5;
-- FAST: Only fetch the columns you actually need
SELECT id, name FROM players WHERE guild_id = 5;

-- SLOW: Comparing an INTEGER column to a string causes a type mismatch
SELECT * FROM players WHERE level = '15';
-- FAST: Match the correct data type
SELECT * FROM players WHERE level = 15;
```

### 14.4 Using EXPLAIN to Decide Whether an Index Helps

```sql
-- Run EXPLAIN ANALYZE before adding an index
EXPLAIN ANALYZE SELECT * FROM players WHERE guild_id = 3;
-- If you see "Seq Scan", no index is being used

-- Add an index
CREATE INDEX idx_players_guild_id ON players(guild_id);

-- Run EXPLAIN ANALYZE again — you should now see "Index Scan"
EXPLAIN ANALYZE SELECT * FROM players WHERE guild_id = 3;
```

> [!NOTE]
> A Seq Scan isn't always a problem. On small tables, reading everything is genuinely faster than using an index. Only investigate Seq Scans when your table is large and the query is noticeably slow.

---

**Practice:**
1. Run `EXPLAIN ANALYZE` on a `SELECT` that filters by `level` on the `players` table. Note whether it shows Seq Scan or Index Scan.
2. Create an index on `level`, then run the same `EXPLAIN ANALYZE` again. Did the plan change?

---

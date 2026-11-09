## DBM Section 17: Zero-Downtime Operations

Schema changes in production are one of the riskiest moments in database management. A naive `ALTER TABLE` on a large table can lock it for minutes or hours, taking your application offline. This section covers how to make every common schema change safely, with zero downtime.

### 17.1 Why Schema Changes Are Dangerous

Most DDL operations (`ALTER TABLE`, `CREATE INDEX`, etc.) acquire an **AccessExclusiveLock** — the strongest lock in PostgreSQL. While this lock is held, no other query can read or write the table. On a table with millions of rows and a busy application, this can mean minutes of downtime and a pile-up of waiting connections that eventually overwhelms the connection limit.

### 17.2 Adding a Column Safely

**The naive approach — don't do this on a busy table:**

```sql
-- ❌ RISKY on large tables — rewrites the entire table if there's a non-null default
ALTER TABLE players ADD COLUMN last_active TIMESTAMP NOT NULL DEFAULT NOW();
```

**The safe three-step approach:**

```sql
-- Step 1: Add the column as nullable — instant, no table rewrite
ALTER TABLE players ADD COLUMN last_active TIMESTAMP;

-- Step 2: Backfill in small batches (not one giant UPDATE that locks everything)
-- Run this repeatedly until all rows are updated
DO $$
DECLARE
    batch_size INT := 10000;
    min_id INT;
    max_id INT;
BEGIN
    SELECT MIN(id), MAX(id) INTO min_id, max_id FROM players WHERE last_active IS NULL;
    WHILE min_id <= max_id LOOP
        UPDATE players
        SET last_active = created_at
        WHERE id BETWEEN min_id AND min_id + batch_size - 1
          AND last_active IS NULL;
        min_id := min_id + batch_size;
        PERFORM pg_sleep(0.1);  -- Brief pause between batches to reduce I/O pressure
    END LOOP;
END $$;

-- Step 3: Add the NOT NULL constraint (fast in PostgreSQL 12+ if all values are filled)
ALTER TABLE players ALTER COLUMN last_active SET NOT NULL;
ALTER TABLE players ALTER COLUMN last_active SET DEFAULT NOW();
```

### 17.3 CREATE INDEX CONCURRENTLY

Regular index creation locks the table for writes for the entire build time. `CONCURRENTLY` removes this lock.

```sql
-- ❌ Blocks all writes while the index is built
CREATE INDEX idx_players_level ON players(level);

-- ✅ Table stays fully writable throughout the build
-- Takes roughly twice as long, but zero downtime
CREATE INDEX CONCURRENTLY idx_players_level ON players(level);
```

`CREATE INDEX CONCURRENTLY` has two restrictions:
- Cannot run inside a transaction block (`BEGIN...COMMIT`)
- If it fails partway through, it leaves an invalid index — check with:

```sql
-- Find invalid indexes left by interrupted CONCURRENTLY builds
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'players'
  AND NOT pg_get_indexdef(indexrelid::regclass) ~ 'VALID';

-- Or query pg_stat_user_indexes
SELECT indexrelname FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%invalid%';

-- Clean up an invalid index and rebuild
DROP INDEX CONCURRENTLY idx_players_level;
CREATE INDEX CONCURRENTLY idx_players_level ON players(level);
```

### 17.4 Renaming Columns or Tables Safely

Renaming a column immediately breaks any application code that references the old name. The safe approach uses a view as a compatibility shim.

```sql
-- Goal: rename 'hp' to 'health_points' in the characters table

-- Step 1: Add the new column
ALTER TABLE characters ADD COLUMN health_points INTEGER;

-- Step 2: Keep them in sync with a trigger during the migration
CREATE OR REPLACE FUNCTION sync_hp_columns()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        IF NEW.hp IS DISTINCT FROM OLD.hp THEN
            NEW.health_points := NEW.hp;
        ELSIF NEW.health_points IS DISTINCT FROM OLD.health_points THEN
            NEW.hp := NEW.health_points;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sync_hp
BEFORE INSERT OR UPDATE ON characters
FOR EACH ROW EXECUTE FUNCTION sync_hp_columns();

-- Step 3: Backfill the new column
UPDATE characters SET health_points = hp WHERE health_points IS NULL;

-- Step 4: Migrate application code to use 'health_points' instead of 'hp'
-- Step 5: Once all application code is updated:
DROP TRIGGER trg_sync_hp ON characters;
ALTER TABLE characters DROP COLUMN hp;
```

### 17.5 Dropping Columns Safely

PostgreSQL marks dropped columns as invisible immediately — no table rewrite happens. But:
- The space isn't reclaimed until the table is vacuumed or rewritten
- Any views, functions, or application code referencing the column break immediately

```sql
-- Before dropping: search for references
SELECT routine_name, routine_definition
FROM information_schema.routines
WHERE routine_definition ILIKE '%old_column_name%';

SELECT viewname, definition
FROM pg_views
WHERE definition ILIKE '%old_column_name%';

-- Safe to drop once references are cleared
ALTER TABLE players DROP COLUMN IF EXISTS old_unused_column;
```

---

**Practice:**
1. On a test table with a few thousand rows, add a nullable column, backfill it in two batches, then add the `NOT NULL` constraint. Verify no errors at each step.
2. Create an index with `CREATE INDEX CONCURRENTLY`. Then drop it with `DROP INDEX CONCURRENTLY`.
3. Simulate a column rename using the trigger-based sync approach: add a new column, create the sync trigger, backfill, then drop the old one.

---

## DBM Section 18: Connection Pooling in Depth (PgBouncer)

You know from Section 12 why connection pooling matters — PostgreSQL opens a process per connection, and that doesn't scale. PgBouncer is the standard solution. This section covers how to configure it, size the pool correctly, and monitor it in production.

### 18.1 PgBouncer Architecture

```
Application (100s of connections)
        ↓
    PgBouncer (listens on port 6432)
        ↓
  PostgreSQL (20-30 actual connections, port 5432)
```

PgBouncer multiplexes many application connections onto a much smaller set of real PostgreSQL connections. Applications connect to PgBouncer exactly as if it were PostgreSQL — the same connection string, same protocol, same SQL.

### 18.2 Pooling Modes

| Mode | Connection released back to pool | Compatible with |
|---|---|---|
| **Session** | When the client disconnects | Everything — prepared statements, advisory locks, `SET LOCAL`, temp tables |
| **Transaction** | When the transaction ends | Most web applications. No prepared statements, no session-level settings |
| **Statement** | After each statement | Only simple, stateless queries. No multi-statement transactions |

**Transaction pooling** is the sweet spot for most web applications. One connection can serve many different application clients as long as each client releases it between transactions.

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
game_db = host=127.0.0.1 port=5432 dbname=game_db

[pgbouncer]
listen_port = 6432
listen_addr = *

; Security
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

; Pooling behaviour
pool_mode = transaction          ; transaction pooling mode
max_client_conn = 500            ; Max connections from applications to PgBouncer
default_pool_size = 25           ; Real PostgreSQL connections per database

; Safety limits
reserve_pool_size = 5            ; Extra connections held in reserve for spikes
reserve_pool_timeout = 3         ; Seconds to wait before using the reserve pool
server_connect_timeout = 5       ; Fail fast if PostgreSQL is unreachable
client_idle_timeout = 600        ; Close idle application connections after 10 minutes
```

### 18.3 Sizing the Pool

The right pool size depends on your PostgreSQL server's CPU cores and your query patterns.

A rough but practical formula:
```
optimal_pool_size = (number_of_cpu_cores * 2) + number_of_disk_spindles
```

For a 4-core server with SSDs: `(4 × 2) + 1 = 9`. In practice, start at 10–25 and tune based on observed wait times.

Signs the pool is too small:
- Application connections frequently wait for a pool connection
- `cl_waiting` in PgBouncer's stats is consistently above 0

Signs the pool is too large:
- PostgreSQL CPU usage is high even during low traffic
- Query times are slow despite high connection counts (thrashing)

### 18.4 Monitoring PgBouncer

PgBouncer exposes stats through a virtual database called `pgbouncer`:

```bash
# Connect to PgBouncer's admin interface
psql -h 127.0.0.1 -p 6432 -U pgbouncer pgbouncer
```

```sql
-- Pool statistics: the most important monitoring query
SHOW POOLS;
-- Key columns:
-- cl_active:   Application connections currently executing a query
-- cl_waiting:  Application connections waiting for a pool slot (BAD if consistently > 0)
-- sv_active:   PostgreSQL connections currently in use
-- sv_idle:     PostgreSQL connections available in the pool
-- sv_used:     Connections released but not yet cleaned up

-- Current client connections
SHOW CLIENTS;

-- Current server (PostgreSQL) connections
SHOW SERVERS;

-- Cumulative statistics since last reset
SHOW STATS;
```

### 18.5 Transaction Pooling Limitations

Transaction pooling doesn't support session-level features — they're reset when the connection is returned to the pool:

```python
# ❌ Prepared statements don't work with transaction pooling
cursor.execute("PREPARE my_query AS SELECT * FROM players WHERE id = $1")
cursor.execute("EXECUTE my_query (1)")
# The PREPARE is lost when the connection returns to the pool

# ✅ Use parameterized queries instead (Section 13.4 Python notes)
cursor.execute("SELECT * FROM players WHERE id = %s", (1,))

# ❌ Advisory locks acquired per-session are lost between transactions
# ✅ Use advisory transaction locks: pg_advisory_xact_lock() (released at transaction end)

# ❌ SET LOCAL and temporary tables only last for the session
# ✅ Use explicit transaction blocks and pass state through your application
```

---

**Practice:**
1. Install PgBouncer locally and configure it in transaction pooling mode pointing at your PostgreSQL instance. Connect through PgBouncer and run a query.
2. Run `SHOW POOLS;` against the PgBouncer admin interface. Identify `cl_active`, `sv_active`, and `sv_idle`.
3. Calculate the optimal pool size for a server with 8 CPU cores and SSDs. Explain your reasoning.

---

## DBM Section 19: Full-Text Search

Section 15 showed GIN indexes for full-text search. This section goes deeper into how the full-text search system actually works, how to make searches more relevant, and how to handle common production requirements like multi-language support and phrase matching.

### 19.1 tsvector and tsquery — The Core Types

A **tsvector** is a sorted list of lexemes (normalised word forms) with position information. A **tsquery** is a search expression that can be matched against a tsvector.

```sql
-- Convert a string to a tsvector
SELECT to_tsvector('english', 'Arthur cast three powerful Fireball spells');
-- Result: 'arthur':1 'cast':2 'fireball':5 'powerful':4 'spell':6 'three':3
-- Note: 'spells' → 'spell' (stemmed), 'three' kept, stop words removed

-- Convert a search query to tsquery
SELECT to_tsquery('english', 'fireball & powerful');
-- Result: 'fireball' & 'powerful'

SELECT plainto_tsquery('english', 'powerful fireball spells');
-- Result: 'powerful' & 'fireball' & 'spell'  (& between words automatically)

SELECT phraseto_tsquery('english', 'cast fireball');
-- Result: 'cast' <-> 'fireball'  (<-> means adjacent, in order)

SELECT websearch_to_tsquery('english', 'powerful fireball -ice');
-- Result: 'powerful' & 'fireball' & !'ice'  (google-style syntax)
```

### 19.2 Ranking Results

`ts_rank` scores how well a document matches the query, so you can order results by relevance.

```sql
-- Full text search with relevance ranking
SELECT
    title,
    ts_rank(search_vector, query)    AS rank,
    ts_rank_cd(search_vector, query) AS rank_cd  -- Considers word proximity (cover density)
FROM quests, to_tsquery('english', 'dragon & defeat') query
WHERE search_vector @@ query
ORDER BY rank_cd DESC
LIMIT 10;
```

### 19.3 Highlighting Matches

`ts_headline` returns an excerpt of the original text with matching words highlighted.

```sql
SELECT
    title,
    ts_headline(
        'english',
        description,
        to_tsquery('english', 'dragon & defeat'),
        'StartSel=<b>, StopSel=</b>, MaxWords=30, MinWords=15, ShortWord=3'
    ) AS excerpt
FROM quests
WHERE search_vector @@ to_tsquery('english', 'dragon & defeat')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'dragon & defeat')) DESC;
```

### 19.4 Multi-Language Full-Text Search

```sql
-- Different languages need different text search configurations
SELECT to_tsvector('english', 'The Warrior runs quickly');
-- 'quickli':4 'run':3 'warrior':2  (English stemming)

SELECT to_tsvector('french', 'Le guerrier court rapidement');
-- French stemming rules applied

-- Store the language alongside the search vector for multi-language content
ALTER TABLE quests ADD COLUMN lang REGCONFIG DEFAULT 'english';
ALTER TABLE quests DROP COLUMN search_vector;
ALTER TABLE quests ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (to_tsvector(lang, title || ' ' || COALESCE(description, ''))) STORED;
```

---

**Practice:**
1. Add a `search_vector` generated column to your `quests` table and create a GIN index on it. Run a full-text search and verify it uses the index.
2. Add relevance ranking with `ts_rank_cd` to the search query and order results by rank. Compare results for different search terms.
3. Use `ts_headline` to return an excerpt with matching words wrapped in `<b>` tags.

---

## DBM Section 20: JSONB & Semi-Structured Data at Scale

PostgreSQL's JSONB type lets you store flexible, schema-less data inside a relational database. This is powerful, but it comes with trade-offs. This section covers when it makes sense, how to query it efficiently, and when to prefer a proper relational model instead.

### 20.1 JSONB Operators in Depth

```sql
-- Sample: characters table with a JSONB 'stats' column
-- stats: {"strength": 18, "dexterity": 14, "spells": ["Fireball", "Ice Shard"]}

-- -> returns JSONB (preserves type)
SELECT stats->'strength' FROM characters;          -- Returns: 18 (as JSON number)

-- ->> returns TEXT
SELECT stats->>'strength' FROM characters;         -- Returns: "18" (as text)

-- #> path operator: navigate nested structure
SELECT stats#>'{spells, 0}' FROM characters;       -- First spell: "Fireball"
SELECT stats#>>'{spells, 0}' FROM characters;      -- As text: Fireball

-- @> containment: does the left JSONB contain the right?
SELECT * FROM characters WHERE stats @> '{"strength": 18}';

-- ? key existence: does the key exist at the top level?
SELECT * FROM characters WHERE stats ? 'spells';

-- ?| any key exists
SELECT * FROM characters WHERE stats ?| ARRAY['spells', 'abilities'];

-- ?& all keys exist
SELECT * FROM characters WHERE stats ?& ARRAY['strength', 'dexterity'];

-- jsonb_each: expand top-level keys as rows
SELECT key, value FROM characters, jsonb_each(stats) WHERE id = 1;
-- Returns: (strength, 18), (dexterity, 14), (spells, ["Fireball","Ice Shard"])

-- jsonb_array_elements: expand a JSON array as rows
SELECT jsonb_array_elements_text(stats->'spells') AS spell
FROM characters WHERE id = 1;
-- Returns: Fireball, Ice Shard
```

### 20.2 Indexing JSONB

A GIN index on the whole JSONB column supports containment (`@>`) and key existence (`?`) operators:

```sql
-- GIN on the entire column — supports @>, ?, ?|, ?&
CREATE INDEX idx_characters_stats_gin ON characters USING GIN (stats);

-- Now this runs fast even with millions of rows
SELECT * FROM characters WHERE stats @> '{"class": "Warrior"}';

-- For exact path lookups, a more targeted expression index is more efficient
CREATE INDEX idx_characters_strength ON characters ((stats->>'strength'));
-- Speeds up: WHERE stats->>'strength' = '18'
-- More selective than a full GIN scan when querying a specific field often
```

### 20.3 Updating JSONB

```sql
-- Replace a specific key value
UPDATE characters
SET stats = jsonb_set(stats, '{strength}', '20')
WHERE id = 1;

-- Add a new key
UPDATE characters
SET stats = stats || '{"constitution": 16}'::jsonb
WHERE id = 1;

-- Remove a key
UPDATE characters
SET stats = stats - 'old_stat'
WHERE id = 1;

-- Append to a JSON array
UPDATE characters
SET stats = jsonb_set(
    stats,
    '{spells}',
    (stats->'spells') || '"Chain Lightning"'::jsonb
)
WHERE id = 1;
```

### 20.4 When JSONB Makes Sense vs When It Doesn't

| ✅ Good fit for JSONB | ❌ Bad fit for JSONB |
|---|---|
| Truly variable schema (each row has different keys) | Data you regularly filter, sort, or join on |
| Configuration or preferences that differ by entity | Data with known, fixed structure |
| Storing external API responses as-is | Data that needs referential integrity |
| Rapid prototyping before you know the full schema | Columns you'll frequently aggregate (SUM, AVG, etc.) |
| Metadata, tags, feature flags | High-cardinality data with many distinct values |

JSONB queries are slower than equivalent relational queries on indexed columns. Use JSONB where the flexibility it provides justifies that cost — not as a shortcut to avoid designing a proper schema.

```sql
-- If you find yourself doing this often, it's time to extract the field into a real column
SELECT stats->>'strength' FROM characters WHERE (stats->>'strength')::int > 15;
-- This is a sign that 'strength' should be a proper column: WHERE strength > 15
```

---

**Practice:**
1. Create a `characters` table with a JSONB `stats` column. Insert three rows with different stat sets. Query for characters where `stats` contains `{"class": "Warrior"}` using `@>`.
2. Create a GIN index on the `stats` column. Verify with `EXPLAIN ANALYZE` that the containment query uses it.
3. Write an `UPDATE` using `jsonb_set` to change one specific key in a row's JSONB without overwriting the rest of the column. Then remove a key using the `-` operator.

---

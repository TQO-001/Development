## DBM Section 3: Advanced Schema Design

Once you've got normalisation right, the next step is making your schema easier to use — for your application code, for your colleagues, and for yourself six months from now. Views, materialized views, sequences, generated columns, and partitioning are the tools that make a well-designed schema genuinely pleasant to work with.

### 3.1 Views — Virtual Tables

A **view** is a stored query that behaves like a table. You query it exactly like you'd query a table, but it has no data of its own — every time you query it, the underlying SQL runs and returns fresh results.

Views are useful for:
- Hiding complexity (pre-joining several tables into one clean interface)
- Restricting access (expose only certain columns to certain users)
- Creating a stable API surface (the underlying table structure can change without breaking queries against the view)

```sql
-- Create a view that presents a clean, joined summary of each player
CREATE OR REPLACE VIEW player_summary AS
SELECT
    p.id,
    p.name,
    p.level,
    p.gold,
    g.guild_name,
    COUNT(i.id) AS item_count
FROM players p
LEFT JOIN guilds g   ON p.guild_id = g.id
LEFT JOIN inventory i ON i.player_id = p.id
GROUP BY p.id, p.name, p.level, p.gold, g.guild_name;

-- Now application code can query this as if it were a table
SELECT name, guild_name, item_count
FROM player_summary
WHERE level > 10
ORDER BY level DESC;

-- Drop a view
DROP VIEW IF EXISTS player_summary;
```

Views are transparent — the database substitutes the view's SQL into your query at runtime. This means they're always up-to-date, but they also inherit any performance characteristics of the underlying query.

### 3.2 Materialized Views — Cached Query Results

A **materialized view** is a view that actually stores its results on disk. Unlike a regular view, it doesn't re-run the underlying query every time you query it. Instead, you refresh it manually (or on a schedule), and queries against it read from the stored snapshot.

Use materialized views when:
- The underlying query is expensive (lots of joins, aggregations, or heavy computation)
- Slightly stale data is acceptable (e.g., a leaderboard that updates every hour)

```sql
-- Create a materialized view of the guild leaderboard
-- (calculated once, stored, fast to query)
CREATE MATERIALIZED VIEW guild_leaderboard AS
SELECT
    g.guild_name,
    COUNT(p.id)      AS member_count,
    AVG(p.level)     AS avg_level,
    SUM(p.gold)      AS total_gold
FROM guilds g
LEFT JOIN players p ON p.guild_id = g.id
GROUP BY g.id, g.guild_name
ORDER BY total_gold DESC;

-- Querying it is instant — no joins, no aggregations at query time
SELECT guild_name, total_gold FROM guild_leaderboard LIMIT 10;

-- Refresh it when you need up-to-date data
REFRESH MATERIALIZED VIEW guild_leaderboard;

-- Refresh without locking reads (concurrent mode — table must have a UNIQUE index)
CREATE UNIQUE INDEX ON guild_leaderboard(guild_name);
REFRESH MATERIALIZED VIEW CONCURRENTLY guild_leaderboard;
```

> [!NOTE]
> `REFRESH MATERIALIZED VIEW` (without CONCURRENTLY) locks the view for the entire refresh — no one can read it until it's done. For large views or production systems, use `CONCURRENTLY` so reads keep working during the refresh. This requires a unique index on the materialized view.

### 3.3 Sequences — Standalone Auto-Increment

A **sequence** is a database object that generates a unique, ever-increasing integer. `SERIAL` and `BIGSERIAL` in `CREATE TABLE` are just shortcuts for creating a sequence and linking it to a column. But you can create and use sequences independently too.

```sql
-- Create a standalone sequence
CREATE SEQUENCE quest_id_seq
    START WITH 1000    -- First value produced
    INCREMENT BY 1
    NO MAXVALUE        -- Runs forever
    CACHE 10;          -- Pre-allocates 10 values for speed

-- Get the next value
SELECT nextval('quest_id_seq');    -- Returns 1000, then 1001, 1002...

-- See the current value without advancing it
SELECT currval('quest_id_seq');    -- Returns the last value THIS SESSION got

-- Peek at the next value without consuming it
SELECT lastval();                  -- Same as currval but without naming the sequence

-- Use it in an INSERT
INSERT INTO quests (id, title) VALUES (nextval('quest_id_seq'), 'Slay the Dragon');

-- Reset a sequence (useful after bulk loads or test data cleanup)
ALTER SEQUENCE quest_id_seq RESTART WITH 1;
```

> [!NOTE]
> Sequences are **not transactional**. If a transaction inserts a row, gets sequence value 42, and then rolls back, that value 42 is gone — the next transaction gets 43. This is intentional: locking a sequence until a transaction commits would create a bottleneck. Gaps in your IDs are completely normal and expected behaviour.

### 3.4 Generated Columns — Computed Values Stored on Disk

A **generated column** is a column whose value is always computed from other columns in the same row. You define the formula once in `CREATE TABLE`, and PostgreSQL maintains it automatically on every insert and update.

```sql
CREATE TABLE characters (
    id          SERIAL PRIMARY KEY,
    player_id   INTEGER REFERENCES players(id),
    base_hp     INTEGER NOT NULL,
    con_bonus   INTEGER NOT NULL DEFAULT 0,

    -- Generated column: max_hp is always base_hp + (con_bonus * 10)
    -- STORED means the value is computed and saved to disk (not recalculated on every read)
    max_hp      INTEGER GENERATED ALWAYS AS (base_hp + (con_bonus * 10)) STORED,

    base_name   VARCHAR(100) NOT NULL,
    title       VARCHAR(50),
    full_title  TEXT GENERATED ALWAYS AS (
        CASE
            WHEN title IS NOT NULL THEN base_name || ', ' || title
            ELSE base_name
        END
    ) STORED
);

-- Inserting — you never provide values for generated columns
INSERT INTO characters (player_id, base_hp, con_bonus, base_name, title)
VALUES (1, 100, 5, 'Arthur', 'King of Camelot');

-- Querying — the generated values are always correct
SELECT base_name, full_title, max_hp FROM characters WHERE player_id = 1;
-- Output: Arthur | Arthur, King of Camelot | 150
```

### 3.5 Table Partitioning — Overview

**Partitioning** splits one large logical table into multiple smaller physical pieces, called partitions. To your application code, it looks like one table — but behind the scenes, PostgreSQL can skip entire partitions during a query, dramatically reducing how much data it has to scan.

There are three partitioning strategies:

| Strategy | Split the data by... | Best for |
|---|---|---|
| **RANGE** | A range of values | Dates, timestamps — e.g. one partition per month |
| **LIST** | Specific values | Categories — e.g. one partition per region |
| **HASH** | A hash of a column | Distributing rows evenly with no natural split |

```sql
-- Range partitioning: split combat_log by month
CREATE TABLE combat_log (
    id           BIGSERIAL,
    player_id    INTEGER NOT NULL,
    event        TEXT NOT NULL,
    damage       INTEGER,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions for each month
CREATE TABLE combat_log_2025_01
    PARTITION OF combat_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE combat_log_2025_02
    PARTITION OF combat_log
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Insert works exactly the same — PostgreSQL routes the row to the right partition
INSERT INTO combat_log (player_id, event, damage)
VALUES (1, 'Killed Goblin', 45);

-- Query works the same too — but PostgreSQL only scans the relevant partitions
SELECT * FROM combat_log
WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01';
-- Reads only the January partition — all other partitions are skipped entirely
```

Partitioning gets its own full section (DBM Section 14) in the Level 3 notes. For now, the key idea is: it's a schema-level performance tool for tables that grow very large over time.

---

**Practice:**
1. Create a view called `active_quests` that joins `quests` and `players` and shows quest title, difficulty, and the name of the player who accepted it. Include only quests with status `'open'`.
2. Create a materialized view called `player_stats_snapshot` that aggregates total gold and average level per guild. Then refresh it and query it.
3. Create a `combat_log` table partitioned by month and insert a few rows. Check which partition they ended up in by querying the partition directly by name.

---

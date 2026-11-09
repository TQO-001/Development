## DBM Section 14: Advanced Partitioning

Section 3 introduced partitioning as a concept. This section goes deep: how partition pruning actually works, how to maintain partitions over time, indexes on partitioned tables, and how to handle data that doesn't fit any partition.

### 14.1 Partition Pruning

Partition pruning is the reason partitioning gives you performance gains. When a query's `WHERE` clause filters on the partition key, PostgreSQL skips entire partitions without reading them.

```sql
-- Range-partitioned combat_log table from Section 3
-- The optimizer sees: WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01'
-- and knows to only scan the January partition
EXPLAIN SELECT * FROM combat_log
WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01';

-- Output should show:
-- Append
--   -> Seq Scan on combat_log_2025_01
-- (Other partitions are NOT listed — they were pruned)
```

Pruning only happens when the filter is on the **partition key column** directly — not on a derived value:

```sql
-- ✅ Pruning works — filtering directly on the partition key
SELECT * FROM combat_log WHERE created_at >= '2025-06-01';

-- ❌ Pruning FAILS — the function wraps the column, hiding it from the planner
SELECT * FROM combat_log WHERE DATE_TRUNC('month', created_at) = '2025-06-01';
-- This causes a full scan of ALL partitions
```

### 14.2 Hash Partitioning for Even Distribution

When there's no natural range or list to split on, hash partitioning distributes rows evenly across a fixed number of partitions based on a hash of the partition key.

```sql
-- Distribute the players table across 4 partitions based on player ID
CREATE TABLE players (
    id         BIGSERIAL,
    name       VARCHAR(100) NOT NULL,
    level      INTEGER DEFAULT 1,
    gold       NUMERIC DEFAULT 0
) PARTITION BY HASH (id);

-- Create the partitions (modulus = total partitions, remainder = this partition's slot)
CREATE TABLE players_p0 PARTITION OF players FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE players_p1 PARTITION OF players FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE players_p2 PARTITION OF players FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE players_p3 PARTITION OF players FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Inserts are automatically routed to the correct partition
INSERT INTO players (name, level) VALUES ('Arthur', 15);
-- PostgreSQL hashes Arthur's id and puts the row in the right partition
```

### 14.3 List Partitioning for Categorical Data

```sql
-- Partition quests by region
CREATE TABLE quests (
    id       BIGSERIAL,
    title    VARCHAR(200) NOT NULL,
    region   VARCHAR(50)  NOT NULL,
    reward   INTEGER
) PARTITION BY LIST (region);

CREATE TABLE quests_camelot   PARTITION OF quests FOR VALUES IN ('Camelot', 'Avalon');
CREATE TABLE quests_north      PARTITION OF quests FOR VALUES IN ('Northlands', 'Tundra');
CREATE TABLE quests_south      PARTITION OF quests FOR VALUES IN ('Southmarsh', 'Desert');

-- Queries filtering by region only scan the relevant partition
SELECT * FROM quests WHERE region = 'Camelot';
```

### 14.4 Default Partitions

A **default partition** catches rows that don't match any other partition's definition. Without one, inserting a row with an unmapped value fails with an error.

```sql
-- Default partition catches any region not explicitly listed
CREATE TABLE quests_other PARTITION OF quests DEFAULT;

-- This now succeeds (goes to quests_other)
INSERT INTO quests (title, region, reward) VALUES ('Lost Map', 'Unknown Lands', 500);
```

> [!NOTE]
> Be careful with default partitions if you plan to add more specific partitions later. Before you can add a partition for a value that's currently going to the default, you must move those rows out of the default partition first — which can require a full scan of it.

### 14.5 Indexes on Partitioned Tables

Creating an index on the parent table automatically creates matching indexes on all existing partitions, and will create one on any new partition you add.

```sql
-- Index the created_at column on the parent table
CREATE INDEX idx_combat_log_player ON combat_log(player_id);

-- PostgreSQL creates:
-- idx_combat_log_player_2025_01 on combat_log_2025_01
-- idx_combat_log_player_2025_02 on combat_log_2025_02
-- ... and so on for all partitions

-- Primary keys and unique constraints must include the partition key
ALTER TABLE combat_log ADD PRIMARY KEY (id, created_at);
-- (id alone cannot be unique across partitions unless created_at is included)
```

### 14.6 Partition Maintenance

For time-based partitions, you need to create new partitions before data arrives for that period, and drop old ones when data ages out.

```sql
-- Create next month's partition (run this monthly via pg_cron or a cron job)
CREATE TABLE combat_log_2025_07
    PARTITION OF combat_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

-- Archive old data: detach the partition (the data is still there, just not in the main table)
ALTER TABLE combat_log DETACH PARTITION combat_log_2024_01;
-- The table combat_log_2024_01 now exists independently — archive it, copy it, or drop it

-- Or drop it entirely (permanent — cannot be undone)
DROP TABLE combat_log_2024_01;
```

---

**Practice:**
1. Create a `combat_log` table partitioned by month (RANGE on `created_at`). Create 3 monthly partitions. Insert rows into each and run `EXPLAIN` to confirm partition pruning is working.
2. Create a `players` table partitioned by HASH across 4 partitions. Insert 20 rows and check which partition each landed in by querying each partition directly.
3. Add a default partition to a LIST-partitioned table and verify that unmatched values land there.

---

## DBM Section 15: Advanced Indexing Strategies

Section 5 covered the index types. This section covers the more nuanced decisions: when covering indexes are worth adding, how to index expressions, how to make full-text search fast, and how multi-column index ordering affects what the optimizer can use.

### 15.1 Covering Indexes — Eliminating Heap Access

You already know covering indexes (`INCLUDE`) from Section 5. Here's how to identify when they're worth adding.

Look for queries where `EXPLAIN` shows an Index Scan but you want Index Only Scan:

```sql
-- This query uses an index on level but still has to hit the heap for 'name' and 'gold'
EXPLAIN ANALYZE
SELECT name, gold FROM players WHERE level > 15 ORDER BY level DESC;
-- Shows: Index Scan using idx_players_level (heap fetches: 847)

-- Add covering index that includes the columns the query needs
CREATE INDEX idx_players_level_cover ON players(level DESC) INCLUDE (name, gold);

-- Now the same query needs zero heap access
EXPLAIN ANALYZE
SELECT name, gold FROM players WHERE level > 15 ORDER BY level DESC;
-- Shows: Index Only Scan (heap fetches: 0)
```

Index Only Scans are dramatically faster on large tables because the heap is not read at all. Worth the extra index size when the query is frequent and performance critical.

### 15.2 Functional (Expression) Indexes

Index the result of an expression rather than a raw column value. Use this when queries regularly apply a function to a column in `WHERE` or `ORDER BY`.

```sql
-- Queries that do case-insensitive search
SELECT * FROM players WHERE LOWER(name) = 'arthur';
-- Without a functional index: full table scan + LOWER() on every row

-- Create an index on LOWER(name)
CREATE INDEX idx_players_name_lower ON players (LOWER(name));

-- Now this query uses the index
SELECT * FROM players WHERE LOWER(name) = 'arthur';

-- Other useful expression indexes
CREATE INDEX idx_players_created_month ON players (DATE_TRUNC('month', created_at));
CREATE INDEX idx_players_active ON players (id) WHERE deleted_at IS NULL;  -- Partial
CREATE INDEX idx_quests_title_length ON quests (LENGTH(title));
```

### 15.3 Multi-Column Index Column Order

The order of columns in a composite index determines which queries can use it. PostgreSQL can use the index if the query filters on a **prefix** of the index columns — meaning the leading columns, in order.

```sql
CREATE INDEX idx_players_guild_level_role ON players(guild_id, level, role);

-- ✅ Can use the index (filters on the leading column)
SELECT * FROM players WHERE guild_id = 5;

-- ✅ Can use the index (filters on leading two columns)
SELECT * FROM players WHERE guild_id = 5 AND level > 10;

-- ✅ Can use the index (all three columns)
SELECT * FROM players WHERE guild_id = 5 AND level > 10 AND role = 'Warrior';

-- ❌ CANNOT use this index (skips guild_id)
SELECT * FROM players WHERE level > 10 AND role = 'Warrior';
-- Needs a separate index starting with level or role
```

**Column ordering rules:**
1. Put equality conditions (`=`) before range conditions (`>`, `<`, `BETWEEN`) — ranges stop the index from being used for columns further right
2. Put the most selective column first (the one that eliminates the most rows)
3. Match the `ORDER BY` clause if you want to avoid a sort step

```sql
-- This index can both filter AND sort without a separate Sort node
CREATE INDEX idx_players_guild_level_desc ON players(guild_id, level DESC);

-- Benefits this query perfectly: filter on guild_id, return in level order
SELECT name, level FROM players WHERE guild_id = 5 ORDER BY level DESC LIMIT 10;
EXPLAIN -- Shows: Index Only Scan (no Sort node)
```

### 15.4 GIN Indexes for Full-Text Search

Full-text search converts words in your text into **lexemes** (root forms: "casting" → "cast", "running" → "run") and indexes those. GIN makes full-text search fast.

```sql
-- Add a tsvector column to avoid recomputing it on every search
ALTER TABLE quests ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english', title || ' ' || COALESCE(description, ''))
    ) STORED;

-- Index the pre-computed vector
CREATE INDEX idx_quests_fts ON quests USING GIN (search_vector);

-- Fast full-text search
SELECT title, ts_rank(search_vector, query) AS rank
FROM quests, to_tsquery('english', 'dragon & slay') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- Highlight matching terms in results
SELECT
    title,
    ts_headline('english', description, to_tsquery('english', 'dragon & slay'),
        'MaxWords=20, MinWords=5') AS excerpt
FROM quests
WHERE search_vector @@ to_tsquery('english', 'dragon & slay');
```

---

**Practice:**
1. Run `EXPLAIN` on a query using `LOWER(name) = 'arthur'`. Note the Seq Scan. Create a functional index on `LOWER(name)` and re-run. Confirm it switches to an Index Scan.
2. Create a three-column composite index. Write three queries that each use a different prefix of the index, and one that can't use it. Verify with `EXPLAIN`.
3. Add a `search_vector` generated column to a `quests` table and create a GIN index on it. Write a full-text search query using `to_tsquery` and verify it uses the index.

---

## DBM Section 16: Schema Design Patterns

Good schema design isn't just about normalization. These are patterns for handling common real-world requirements: tracking every change, keeping history, marking records as deleted without losing them, and serving multiple tenants from one database.

### 16.1 Audit Tables — Who Changed What and When

A comprehensive audit trail records the complete before/after state of every row change.

```sql
CREATE TABLE players_audit (
    audit_id    BIGSERIAL PRIMARY KEY,
    player_id   INTEGER       NOT NULL,
    operation   TEXT          NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    changed_by  TEXT          NOT NULL DEFAULT current_user,
    old_data    JSONB,         -- NULL on INSERT
    new_data    JSONB          -- NULL on DELETE
);

CREATE OR REPLACE FUNCTION audit_player_changes()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO players_audit (player_id, operation, old_data, new_data)
    VALUES (
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE to_jsonb(OLD) END,
        CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE to_jsonb(NEW) END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_audit_players
AFTER INSERT OR UPDATE OR DELETE ON players
FOR EACH ROW EXECUTE FUNCTION audit_player_changes();

-- Query the audit log: full change history for one player
SELECT operation, changed_at, changed_by,
       old_data->>'gold' AS gold_before,
       new_data->>'gold' AS gold_after
FROM players_audit
WHERE player_id = 1
ORDER BY changed_at;
```

### 16.2 Temporal / Versioned Data

When you need to track a complete history of row values over time — not just who changed it, but what the value was at any specific point — use a **versioned history table** pattern.

```sql
CREATE TABLE player_gold_history (
    id          BIGSERIAL PRIMARY KEY,
    player_id   INTEGER       NOT NULL REFERENCES players(id),
    gold        INTEGER       NOT NULL,
    valid_from  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    valid_to    TIMESTAMPTZ            -- NULL means this is the current version
);

-- When gold changes: close the old version, open a new one
CREATE OR REPLACE FUNCTION version_gold_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.gold IS DISTINCT FROM NEW.gold THEN
        -- Close the previous version
        UPDATE player_gold_history
        SET valid_to = NOW()
        WHERE player_id = NEW.id AND valid_to IS NULL;

        -- Open a new version
        INSERT INTO player_gold_history (player_id, gold)
        VALUES (NEW.id, NEW.gold);
    END IF;
    RETURN NEW;
END;
$$;

-- Query: what was Arthur's gold at a specific point in time?
SELECT gold FROM player_gold_history
WHERE player_id = 1
  AND valid_from <= '2025-06-01 14:00:00'
  AND (valid_to IS NULL OR valid_to > '2025-06-01 14:00:00');
```

### 16.3 Multi-Tenancy Schemas

If you're building a product that serves multiple clients (guilds, organisations, game servers), you need to decide how to isolate their data.

**Option 1: Shared schema with a tenant_id column** — all tenants in the same tables, row-level security separates them.

```sql
-- Add tenant_id to every table
ALTER TABLE players  ADD COLUMN tenant_id INTEGER NOT NULL REFERENCES tenants(id);
ALTER TABLE guilds   ADD COLUMN tenant_id INTEGER NOT NULL REFERENCES tenants(id);
ALTER TABLE quests   ADD COLUMN tenant_id INTEGER NOT NULL REFERENCES tenants(id);

-- Row-level security enforces isolation automatically
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON players
    USING (tenant_id = current_setting('app.current_tenant_id')::INTEGER);

-- Application sets the tenant context at the start of each request
SET app.current_tenant_id = '42';

-- Now all queries on players automatically filter to tenant 42
SELECT * FROM players;  -- Only returns tenant 42's players
```

**Option 2: Separate schema per tenant** — each tenant gets their own PostgreSQL schema (namespace).

```sql
-- Create a schema for a new tenant
CREATE SCHEMA tenant_42;

-- Create all tables inside their schema
CREATE TABLE tenant_42.players (id SERIAL PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE tenant_42.guilds  (id SERIAL PRIMARY KEY, guild_name TEXT NOT NULL);

-- Connect as that tenant and set the search path
SET search_path TO tenant_42, public;

-- Now plain table names resolve to tenant_42.tablename
SELECT * FROM players;  -- Queries tenant_42.players
```

| Approach | Best for | Trade-off |
|---|---|---|
| Shared schema + tenant_id | Hundreds or thousands of tenants | Harder to give each tenant their own backup/restore |
| Schema per tenant | Tens of tenants with strong isolation needs | Schema proliferation; migrations must run N times |

---

**Practice:**
1. Add the `players_audit` trigger to a test table. Make a few updates and deletions, then query the audit log to reconstruct the history.
2. Implement the versioned gold history pattern. Insert a player, update their gold three times, then query the history table to see all three versions.
3. Add a `tenant_id` column to your `players` table, enable RLS, and write a policy that isolates rows by tenant. Test it by setting `app.current_tenant_id` to two different values and confirming only the correct rows are returned each time.

---

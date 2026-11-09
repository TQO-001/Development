## DBM Section 6: Query Planning & The Optimizer

When you send a SQL query to PostgreSQL, it doesn't just run it immediately. First it hands the query to the **query planner** (also called the optimizer), which figures out the most efficient way to execute it. The planner tries different strategies — which indexes to use, which tables to join first, whether to sort in memory or on disk — and picks the one it estimates will cost the least. Understanding how it thinks is what separates "I added an index and hope it helps" from actually knowing whether it helps.

### 6.1 How the Planner Estimates Cost

The planner doesn't know how long a query will take in seconds. Instead it assigns an abstract **cost** to each possible execution plan — a relative number that reflects estimated work. Lower cost = better plan. The final cost of a query is made up of two parts:

- **Startup cost** — the work done before the first row can be returned (e.g., sorting an entire result set)
- **Total cost** — the work done to return all rows

Cost numbers aren't milliseconds. They're unitless estimates useful only for comparison between plans, not as absolute predictions.

The planner's estimates rely on **statistics** — counts and histograms about your data stored in `pg_statistic`. These statistics are updated by `ANALYZE` (which runs automatically via autovacuum). When statistics are stale or missing, the planner makes poor estimates and often picks a slow plan.

```sql
-- Update statistics for a specific table (or all tables with no argument)
ANALYZE players;
ANALYZE;

-- See the statistics PostgreSQL has collected for a column
SELECT
    attname         AS column_name,
    n_distinct,     -- Estimated number of distinct values (-1 means all unique)
    correlation     -- How physically ordered the column is (1.0 = perfectly ordered)
FROM pg_stats
WHERE tablename = 'players';
```

### 6.2 Reading EXPLAIN Output

`EXPLAIN` shows the plan as a tree of **nodes**. Each node is one step the database takes, and nodes are nested — inner nodes feed results to outer ones. The indentation shows this nesting.

```sql
EXPLAIN SELECT p.name, g.guild_name
FROM players p
LEFT JOIN guilds g ON p.guild_id = g.id
WHERE p.level > 10;
```

Sample output:

```
Hash Left Join  (cost=12.35..38.20 rows=320 width=40)
  Hash Cond: (p.guild_id = g.id)
  ->  Seq Scan on players p  (cost=0.00..22.50 rows=320 width=24)
        Filter: (level > 10)
  ->  Hash  (cost=8.60..8.60 rows=140 width=20)
        ->  Seq Scan on guilds g  (cost=0.00..8.60 rows=140 width=20)
```

Reading this:
- `Seq Scan on players` — reading the entire players table (no index being used)
- `Filter: (level > 10)` — filtering rows after reading them
- `Hash` — building a hash table from guilds
- `Hash Left Join` — combining the results using the hash table
- `cost=12.35..38.20` — startup cost of 12.35, total cost of 38.20 (estimated)
- `rows=320` — the planner estimates 320 rows will come out of this node
- `width=40` — estimated average row size in bytes

### 6.3 EXPLAIN ANALYZE — Real Numbers

`EXPLAIN ANALYZE` actually runs the query and reports both estimated and actual numbers. The difference between estimated and actual rows is where to look for problems.

```sql
EXPLAIN ANALYZE SELECT p.name, g.guild_name
FROM players p
LEFT JOIN guilds g ON p.guild_id = g.id
WHERE p.level > 10;
```

Sample output:

```
Hash Left Join  (cost=12.35..38.20 rows=320 width=40)
               (actual time=0.42..2.18 rows=287 loops=1)
  ->  Seq Scan on players p  (cost=0.00..22.50 rows=320 width=24)
                             (actual time=0.02..0.85 rows=287 loops=1)
        Filter: (level > 10)
        Rows Removed by Filter: 43
  ->  Hash  (cost=8.60..8.60 rows=140 width=20)
            (actual time=0.18..0.18 rows=120 loops=1)
        ->  Seq Scan on guilds g  (cost=0.00..8.60 rows=140 width=20)
                                  (actual time=0.02..0.09 rows=120 loops=1)
Planning Time: 0.28 ms
Execution Time: 2.31 ms
```

Key comparisons:
- `rows=320` (estimated) vs `rows=287` (actual) — close enough, the planner had good statistics
- `rows=140` (estimated) vs `rows=120` (actual) — slight overestimate for guilds, still fine
- `Rows Removed by Filter: 43` — 43 rows were read but discarded (a full scan then filtered)

When estimates are wildly off — hundreds estimated, tens of thousands actual — that's when you need to investigate stale statistics or a schema design issue.

### 6.4 Common Node Types

| Node | What it means |
|---|---|
| **Seq Scan** | Reading the entire table. Fine for small tables; slow for large ones without indexes. |
| **Index Scan** | Following an index to the heap. Fast for selective queries. |
| **Index Only Scan** | Reading entirely from the index — the heap is not touched. Very fast. |
| **Bitmap Index Scan** | Using an index to build a bitmap of pages to read, then fetching those pages. Used when many rows match. |
| **Nested Loop** | For each row in the outer side, look up matching rows in the inner side. Fast when the inner side is small. |
| **Hash Join** | Build a hash table from the smaller side, probe it with the larger side. Good for large equi-joins. |
| **Merge Join** | Sort both sides, then merge. Good when both sides are already sorted. |
| **Sort** | Sorts results. Can spill to disk if the sort exceeds `work_mem`. |

### 6.5 Why the Planner Gets It Wrong

The planner uses statistics, but statistics are approximations. A few common situations where it misestimates:

**Multiple correlated conditions:**

```sql
-- The planner assumes 'role' and 'guild_id' are independent
-- If all Mages happen to be in guild 5, the planner underestimates rows
SELECT * FROM players WHERE role = 'Mage' AND guild_id = 5;
-- Fix: CREATE STATISTICS to tell PostgreSQL these columns are correlated
CREATE STATISTICS players_role_guild ON role, guild_id FROM players;
ANALYZE players;
```

**Non-uniform distributions:**

```sql
-- The planner estimates based on average distribution
-- If 90% of quests have status='completed' and 10% are 'open',
-- but statistics only show 4 distinct values, estimates can be way off
-- Fix: increase statistics target for that column
ALTER TABLE quests ALTER COLUMN status SET STATISTICS 500;
ANALYZE quests;
```

**Functions inside WHERE clauses:**

```sql
-- The planner has no idea how many rows LOWER(name) = 'arthur' will return
-- It can't use the statistics on 'name' because the function transforms the value
SELECT * FROM players WHERE LOWER(name) = 'arthur';
-- Fix: create a functional index so the planner has statistics for this expression
CREATE INDEX idx_players_name_lower ON players(LOWER(name));
ANALYZE players;
```

> [!NOTE]
> `EXPLAIN ANALYZE` runs the query for real. On a slow query or one that modifies data, wrap it in a transaction and roll back: `BEGIN; EXPLAIN ANALYZE UPDATE ...; ROLLBACK;` — this gives you the timing without actually committing the change.

---

**Practice:**
1. Run `EXPLAIN ANALYZE` on a `SELECT` that filters on an unindexed column. Note the Seq Scan. Add an index, run `ANALYZE`, then re-run `EXPLAIN ANALYZE`. What changed?
2. Find a query where the estimated row count is significantly different from the actual row count. Run `ANALYZE` on the relevant table and check whether the estimate improves.
3. Write a query with a join between `players` and `guilds` and explain its plan. Identify which join algorithm PostgreSQL chose and why it probably made that choice.

---

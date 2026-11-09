## DBM Section 5: Indexes in Depth

The SQL notes introduced indexes as "the book index" — a lookup structure that helps the database jump to the right rows instead of reading everything. That analogy holds, but there are many different types of indexes built for different kinds of data and queries. Knowing which type to reach for, and when, separates a developer who occasionally adds indexes from one who actually understands them.

### 5.1 B-Tree — The Default Index

When you run `CREATE INDEX`, PostgreSQL builds a **B-tree** (balanced tree) index by default. A B-tree organises its data in a sorted, branching tree structure where every lookup takes roughly the same amount of time, regardless of where in the tree the value lives.

B-trees work well for:
- Exact matches: `WHERE name = 'Arthur'`
- Range queries: `WHERE level BETWEEN 10 AND 20`
- Sorting: `ORDER BY created_at DESC`
- Prefix matches: `WHERE name LIKE 'Art%'` (only when the wildcard is at the end)

```sql
-- Standard B-tree index (this is what CREATE INDEX always creates by default)
CREATE INDEX idx_players_name  ON players(name);
CREATE INDEX idx_players_level ON players(level);

-- B-tree naturally supports range scans — this query can use idx_players_level
SELECT name, level FROM players WHERE level BETWEEN 10 AND 20;

-- Multi-column B-tree: useful when queries filter on both columns together
-- Column order matters: put the most selective or most-filtered column first
CREATE INDEX idx_players_guild_level ON players(guild_id, level);
-- Helps: WHERE guild_id = 5 AND level > 10
-- Helps: WHERE guild_id = 5   (can use the leading column)
-- Does NOT help: WHERE level > 10  (can't use an index that starts with guild_id)
```

### 5.2 Hash Indexes

A **Hash index** stores a hash of each indexed value. This makes exact equality lookups very fast — but that's all it's good for. Hash indexes can't do range queries, sorting, or prefix matching.

```sql
-- Hash index: only useful for = comparisons, not <, >, BETWEEN, LIKE, ORDER BY
CREATE INDEX idx_players_name_hash ON players USING HASH (name);

-- This query can use the hash index
SELECT * FROM players WHERE name = 'Arthur';

-- These queries CANNOT use the hash index
SELECT * FROM players WHERE name LIKE 'Art%';
SELECT * FROM players WHERE name > 'Lancelot';
SELECT * FROM players ORDER BY name;
```

In practice, B-tree handles equality just as efficiently as Hash for most workloads. Hash indexes are only worth considering on very large tables where the equality-only lookup has a measurable performance advantage.

### 5.3 GIN — For Arrays, JSONB, and Full-Text Search

**GIN** (Generalised Inverted Index) is designed for columns that contain multiple values — arrays, JSONB documents, and full-text search vectors. It creates an index entry for each element inside the value, not for the value as a whole.

Think of it as an index of every word in a document, rather than the document itself.

```sql
-- GIN index on an array column
CREATE INDEX idx_spells_tags ON spells USING GIN (tags);

-- Now these array operators can use the index efficiently
SELECT * FROM spells WHERE tags @> ARRAY['fire'];      -- contains 'fire'
SELECT * FROM spells WHERE tags && ARRAY['aoe', 'fire']; -- overlaps with these tags

-- GIN index on a JSONB column
CREATE INDEX idx_characters_stats ON characters USING GIN (stats);

-- Now JSONB containment queries can use the index
SELECT * FROM characters WHERE stats @> '{"class": "Warrior"}';

-- GIN for full-text search
CREATE INDEX idx_quest_description_fts ON quests
    USING GIN (to_tsvector('english', description));

SELECT title FROM quests
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'dragon & slaying');
```

### 5.4 GiST — For Geometric and Range Types

**GiST** (Generalised Search Tree) is a flexible index type for data that doesn't fit neatly into a B-tree. Common uses:
- Geometric types (points, polygons, circles) — for spatial queries
- Range types (`int4range`, `tsrange`, `daterange`) — for overlap and containment checks
- The exclusion constraints from Section 4.2 use GiST internally

```sql
-- GiST on a range column — speeds up overlap and containment queries
CREATE INDEX idx_booking_time_range ON quest_bookings
    USING GIST (tsrange(start_time, end_time));

-- Now range overlap queries are fast
SELECT * FROM quest_bookings
WHERE tsrange(start_time, end_time) && tsrange('2025-06-01', '2025-06-02');
```

### 5.5 BRIN — For Naturally Ordered, Very Large Tables

**BRIN** (Block Range Index) is a tiny, lightweight index designed for very large tables where values are naturally ordered by insertion order — like a timestamp column in a log table that always gets new rows appended to the end.

BRIN stores the minimum and maximum value for each range of pages on disk. When a query filters on that column, PostgreSQL skips entire page ranges that can't possibly contain matching values.

```sql
-- BRIN on a timestamp column in a huge log table
-- (works because rows are always inserted in chronological order)
CREATE INDEX idx_combat_log_created_brin ON combat_log
    USING BRIN (created_at) WITH (pages_per_range = 128);

-- A range query can now skip most of the table without scanning it
SELECT * FROM combat_log
WHERE created_at BETWEEN '2025-06-01' AND '2025-06-02';
```

BRIN indexes are tiny compared to B-tree (sometimes 1000x smaller) and very cheap to maintain. But they only work well when the data is physically ordered the same way as the query's filter — which is naturally true for append-only timestamp columns.

### 5.6 Partial Indexes

A **partial index** only indexes rows that satisfy a `WHERE` condition. This makes it much smaller than a full index and faster to maintain, and it means the database only uses it for queries that match that same condition.

```sql
-- Only index active quests (not completed or cancelled ones)
-- If 90% of quests are completed, this index is 10x smaller than a full index
CREATE INDEX idx_quests_open ON quests(difficulty)
    WHERE status = 'open';

-- The index is only used when the query includes the same filter
SELECT * FROM quests WHERE status = 'open' AND difficulty > 5;  -- uses index
SELECT * FROM quests WHERE difficulty > 5;                       -- does NOT use it

-- Partial unique index: each player can only have one active quest at a time
CREATE UNIQUE INDEX idx_one_active_quest_per_player ON quest_assignments(player_id)
    WHERE status = 'active';
```

### 5.7 Covering Indexes (INCLUDE)

A **covering index** includes extra columns that aren't part of the lookup key but are included in the index itself. When a query needs only these columns, PostgreSQL can answer it entirely from the index without touching the heap (the actual table). This is called an **index-only scan** and is extremely fast.

```sql
-- Index on level, but also include name and gold in the index itself
CREATE INDEX idx_players_level_covering ON players(level)
    INCLUDE (name, gold);

-- This query can be answered entirely from the index — zero table access needed
SELECT name, gold FROM players WHERE level > 15 ORDER BY level DESC;

-- The EXPLAIN output will show "Index Only Scan" instead of "Index Scan"
EXPLAIN SELECT name, gold FROM players WHERE level > 15 ORDER BY level DESC;
```

### 5.8 Index Bloat

Indexes can grow bloated over time — dead index entries from updated and deleted rows accumulate, just like dead tuples in the heap. Bloated indexes waste disk space and make queries slower.

```sql
-- Check index bloat (requires the pgstattuple extension)
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT * FROM pgstattuple('idx_players_name');
-- Look at: dead_tuple_percent — if it's high, the index has significant bloat

-- Rebuild an index to reclaim wasted space
REINDEX INDEX idx_players_name;

-- Rebuild without locking reads/writes (safer for production)
REINDEX INDEX CONCURRENTLY idx_players_name;
```

### 5.9 Index Type Quick Reference

| Index type | Best for | Not good for |
|---|---|---|
| **B-tree** | Equality, ranges, sorting, LIKE 'prefix%' | Arrays, full-text, JSON containment |
| **Hash** | Equality only (`=`) | Ranges, sorting, patterns |
| **GIN** | Arrays, JSONB, full-text search | Simple equality, ranges |
| **GiST** | Geometric, range types, exclusion constraints | Simple equality lookups |
| **BRIN** | Huge naturally-ordered tables (logs, timestamps) | Random-access patterns, unordered data |

---

**Practice:**
1. Create a GIN index on a `JSONB` column in a table. Write a query using the `@>` containment operator and verify it uses the index via `EXPLAIN`.
2. Create a partial index on the `quests` table that only indexes rows with `status = 'open'`. Write a query that uses it and one that doesn't.
3. Create a covering index on `players(level) INCLUDE (name, gold)` and write a query that produces an Index Only Scan (check with `EXPLAIN ANALYZE`).

---

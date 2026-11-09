## DBM Section 10: Monitoring & Health

You can't improve what you can't see. PostgreSQL ships with a rich set of system views that tell you what's happening inside your database right now — what queries are running, which tables are bloated, where indexes are being used, and whether connections are running low. Checking these regularly is how problems get caught before they become outages.

### 10.1 pg_stat_activity — What's Running Right Now

`pg_stat_activity` shows every current connection and what it's doing.

```sql
-- See all active connections
SELECT
    pid,
    usename         AS username,
    application_name,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    query_start,
    NOW() - query_start AS query_duration,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Find queries that have been running longer than 5 minutes
SELECT
    pid,
    usename,
    NOW() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY duration DESC;

-- Kill a specific query by PID (ask first before you kill anything in production)
SELECT pg_terminate_backend(12345);  -- Terminates the connection entirely
SELECT pg_cancel_backend(12345);     -- Sends a cancel signal (gentler — query stops, connection stays)
```

### 10.2 pg_stat_user_tables — Table Health

```sql
-- Which tables are doing the most work?
SELECT
    relname                     AS table_name,
    seq_scan                    AS full_table_scans,
    idx_scan                    AS index_scans,
    n_live_tup                  AS live_rows,
    n_dead_tup                  AS dead_rows,
    ROUND(n_dead_tup::numeric /
        NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY seq_scan DESC;
```

The key things to watch:
- **High `seq_scan` with large `n_live_tup`** — a large table being fully scanned repeatedly. Likely needs an index.
- **High `dead_pct`** — too many dead tuples. Run `VACUUM ANALYZE table_name;`.
- **`last_autovacuum` is NULL or very old** — autovacuum may not be running on this table.

### 10.3 pg_stat_user_indexes — Which Indexes Are Actually Used

```sql
-- See index usage statistics
SELECT
    relname             AS table_name,
    indexrelname        AS index_name,
    idx_scan            AS times_used,
    idx_tup_read        AS rows_read_via_index,
    idx_tup_fetch       AS rows_fetched_via_index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Find indexes that have NEVER been used
-- (Candidates for removal — but check if the table was recently created or repopulated)
SELECT
    schemaname,
    relname         AS table_name,
    indexrelname    AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS wasted_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public';
```

### 10.4 Connection Monitoring

PostgreSQL has a hard limit on simultaneous connections (`max_connections`, usually 100 by default). Running out causes new connections to fail — which brings down your application.

```sql
-- How many connections are in use vs the maximum?
SELECT
    COUNT(*)                                          AS current_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max_connections,
    ROUND(COUNT(*)::numeric /
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') * 100, 1) AS pct_used
FROM pg_stat_activity;

-- Connection breakdown by state
SELECT state, COUNT(*) AS count
FROM pg_stat_activity
GROUP BY state
ORDER BY count DESC;
-- States: 'active', 'idle', 'idle in transaction', 'idle in transaction (aborted)'

-- Long-running idle transactions are dangerous — they prevent VACUUM from cleaning up
SELECT pid, usename, state, xact_start, NOW() - xact_start AS open_duration
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND xact_start < NOW() - INTERVAL '10 minutes'
ORDER BY open_duration DESC;
```

### 10.5 Table and Index Size

```sql
-- Size of each table (including indexes and TOAST)
SELECT
    relname                                              AS table_name,
    pg_size_pretty(pg_total_relation_size(relid))        AS total_size,
    pg_size_pretty(pg_relation_size(relid))              AS table_only,
    pg_size_pretty(pg_indexes_size(relid))               AS indexes_size,
    pg_size_pretty(pg_total_relation_size(relid)
        - pg_relation_size(relid)
        - pg_indexes_size(relid))                        AS toast_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Size of a specific table and all its indexes
SELECT pg_size_pretty(pg_total_relation_size('players'));
```

### 10.6 A Simple Health Check Query

Run this regularly (or on a schedule) to get a fast overview of your database's condition:

```sql
SELECT
    'Connections' AS metric,
    COUNT(*)::text AS value
FROM pg_stat_activity
UNION ALL
SELECT 'Total tables', COUNT(*)::text FROM pg_stat_user_tables
UNION ALL
SELECT 'Idle in transaction', COUNT(*)::text FROM pg_stat_activity WHERE state = 'idle in transaction'
UNION ALL
SELECT 'Long queries (>1min)', COUNT(*)::text FROM pg_stat_activity
    WHERE state = 'active' AND query_start < NOW() - INTERVAL '1 minute'
UNION ALL
SELECT 'Tables needing vacuum', COUNT(*)::text FROM pg_stat_user_tables
    WHERE n_dead_tup > 1000 AND (n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0)) > 0.1;
```

---

**Practice:**
1. Run the `pg_stat_activity` query and identify any long-running or idle-in-transaction connections on your instance.
2. Run the table health query from Section 10.2. Find the table with the most dead tuples and run `VACUUM ANALYZE` on it.
3. Run the unused indexes query from Section 10.3. If any indexes have never been used, investigate whether they're candidates for removal.

---

## DBM Section 11: Database Migrations

A **migration** is a script that changes your database schema in a controlled, versioned way. Instead of connecting to the database and typing `ALTER TABLE` directly, you write migrations that can be run, tracked, reviewed, and rolled back. This is how professional teams manage schema changes across development, staging, and production environments.

### 11.1 Why Migrations Matter

Without migrations:
- Your dev schema, staging schema, and production schema drift apart over time
- You can't know exactly what version of the schema production is on
- Schema changes can't be code-reviewed or tracked in git
- Rolling back a bad change requires guesswork

With migrations, schema changes are code — stored in version control, reviewable in pull requests, auditable, and repeatable.

### 11.2 Migration File Conventions

A migration is typically a numbered SQL file with an `up` direction (apply the change) and a `down` direction (reverse it).

```
migrations/
├── 0001_create_players.sql
├── 0002_create_guilds.sql
├── 0003_add_guild_id_to_players.sql
├── 0004_create_inventory.sql
└── 0005_add_soft_delete_to_players.sql
```

A simple migration file format:

```sql
-- Migration: 0005_add_soft_delete_to_players.sql
-- Description: Add deleted_at column to players for soft-delete support
-- Author: Damian
-- Date: 2025-06-01

-- UP: Apply this migration
ALTER TABLE players ADD COLUMN deleted_at TIMESTAMP;
CREATE INDEX idx_players_deleted_at ON players(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE OR REPLACE VIEW active_players AS SELECT * FROM players WHERE deleted_at IS NULL;

-- DOWN: Reverse this migration
-- DROP VIEW active_players;
-- DROP INDEX idx_players_deleted_at;
-- ALTER TABLE players DROP COLUMN deleted_at;
```

Keep `DOWN` migrations as comments rather than separate files — they're rarely run and it's easier to keep up and down together.

### 11.3 Tracking Applied Migrations

You need a way to know which migrations have already run on a given database, so you don't apply them twice.

```sql
-- A simple migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    id          SERIAL PRIMARY KEY,
    filename    VARCHAR(255) NOT NULL UNIQUE,
    applied_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    checksum    VARCHAR(64)   -- Optional: MD5 of the file content, to detect tampering
);

-- Before applying a migration, check if it's already been applied
SELECT EXISTS(
    SELECT 1 FROM schema_migrations WHERE filename = '0005_add_soft_delete_to_players.sql'
);

-- After successfully applying, record it
INSERT INTO schema_migrations (filename)
VALUES ('0005_add_soft_delete_to_players.sql');
```

### 11.4 Risky Migration Operations

Some schema changes are riskier than others in production. Knowing which ones require extra care prevents outages.

**Adding a NOT NULL column without a default — dangerous:**

```sql
-- ❌ This rewrites every row in the table immediately — locks the table for the duration
ALTER TABLE players ADD COLUMN last_login TIMESTAMP NOT NULL;

-- ✅ Safe approach: add as nullable first, backfill, then add the constraint
-- Step 1: Add as nullable
ALTER TABLE players ADD COLUMN last_login TIMESTAMP;

-- Step 2: Backfill existing rows in batches (not one giant UPDATE)
UPDATE players SET last_login = created_at WHERE last_login IS NULL AND id BETWEEN 1 AND 10000;
UPDATE players SET last_login = created_at WHERE last_login IS NULL AND id BETWEEN 10001 AND 20000;
-- ... continue in batches to avoid long-running locks

-- Step 3: Add the NOT NULL constraint (PostgreSQL 12+ can do this without a table rewrite
-- if all existing values are NOT NULL)
ALTER TABLE players ALTER COLUMN last_login SET NOT NULL;
```

**Dropping a column — moderate risk:**

```sql
-- PostgreSQL marks the column as dropped but doesn't immediately reclaim space
-- The column becomes invisible to queries immediately
ALTER TABLE players DROP COLUMN IF EXISTS old_unused_column;
-- Space is reclaimed only when the table is VACUUMed or rewritten (VACUUM FULL / pg_repack)
```

**Renaming a column or table — high risk:**

```sql
-- Renaming breaks any application code that references the old name
-- Safe approach: add a new column, mirror writes to both, swap, remove old
-- OR: use a view with the old name while migrating application code

-- Create a view with the old name as a transition alias
CREATE VIEW player_profiles AS SELECT * FROM characters;
-- Application still works, then migrate code to use 'characters', then DROP VIEW
```

### 11.5 Zero-Downtime Index Creation

Creating a regular index locks the table against writes for the entire build — unacceptable in production for large tables.

```sql
-- ❌ Blocks all writes to players during the entire index build
CREATE INDEX idx_players_level ON players(level);

-- ✅ CONCURRENTLY builds the index without blocking writes
-- Takes longer, but the table stays writable throughout
CREATE INDEX CONCURRENTLY idx_players_level ON players(level);
```

> [!NOTE]
> `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block (`BEGIN...COMMIT`). It must be run as a standalone statement. If it fails partway through, it leaves an invalid index — clean it up with `DROP INDEX CONCURRENTLY idx_players_level;` before trying again.

### 11.6 Migration Tools

Manual SQL migration files work well for small teams. Larger projects use tools that automate tracking, ordering, and running migrations:

| Tool | Language | Key feature |
|---|---|---|
| **Flyway** | Java/JVM | Version-based migrations, works with any SQL |
| **Liquibase** | Java/JVM | XML/YAML/SQL migrations, rollback support |
| **Alembic** | Python | Built for SQLAlchemy projects |
| **golang-migrate** | Go | Lightweight, supports many drivers |
| **Sqitch** | Perl/Any | Git-like change tracking |

All of them ultimately do the same thing: track which SQL files have been applied and run the new ones in order.

---

**Practice:**
1. Write a migration file `0001_create_players.sql` with a proper `CREATE TABLE` statement. Write a rollback comment showing the `DROP TABLE` that would undo it.
2. Create a `schema_migrations` table and write a small shell script (or Python script) that reads migration files from a directory, checks which ones haven't been applied, and runs the new ones in order.
3. Practice the safe column addition workflow: add a nullable column to a table, backfill it with an `UPDATE`, then add the `NOT NULL` constraint.

---

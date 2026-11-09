## DBM Section 12: Performance Tuning & Configuration

PostgreSQL ships with conservative default settings designed to run on modest hardware without crashing. On a real server with real workloads, tuning the configuration to match your hardware and usage patterns can make a dramatic difference. This section covers the settings that have the most impact, plus how to keep your tables healthy over time.

### 12.1 Key postgresql.conf Settings

These are stored in `postgresql.conf` (usually in `/etc/postgresql/<version>/main/` on Ubuntu). After changing most settings, run `SELECT pg_reload_conf();`. A few require a full restart — they're marked below.

```ini
# ─── MEMORY SETTINGS ───────────────────────────────────────────────────────

# shared_buffers: PostgreSQL's shared memory cache for pages
# Rule of thumb: 25% of total RAM
# Example for a 16 GB server: 4GB
shared_buffers = 4GB                       # Requires restart

# work_mem: memory for each sort or hash operation PER QUERY (not per connection!)
# If a query has 5 sort operations and 50 connections run it concurrently: 5 × 50 × work_mem
# Keep this conservative unless you have headroom
# Rule of thumb: (Total RAM - shared_buffers) / (max_connections × 2)
work_mem = 64MB

# maintenance_work_mem: used by VACUUM, CREATE INDEX, ALTER TABLE
# Higher = faster index builds and vacuums
maintenance_work_mem = 512MB

# effective_cache_size: tells the planner how much RAM the OS uses for caching
# Does NOT allocate memory — just hints to the planner
# Rule of thumb: 75% of total RAM
effective_cache_size = 12GB

# ─── CONNECTION SETTINGS ───────────────────────────────────────────────────

# max_connections: maximum concurrent connections
# Don't set this high — use a connection pooler (PgBouncer) instead
# Each connection uses ~5–10 MB RAM
max_connections = 100                      # Requires restart

# ─── WAL SETTINGS ──────────────────────────────────────────────────────────

# wal_buffers: memory for WAL writes before flushing to disk
# Good default: 16MB or 1/32 of shared_buffers
wal_buffers = 64MB                         # Requires restart

# checkpoint_completion_target: spread checkpoint writes over this fraction
# of the checkpoint interval (reduces I/O spikes)
checkpoint_completion_target = 0.9

# ─── QUERY PLANNER ─────────────────────────────────────────────────────────

# Tell the planner whether your storage is an SSD or spinning disk
# SSDs make random reads much cheaper relative to sequential reads
random_page_cost = 1.1     # SSD (default 4.0 is for spinning disk)
seq_page_cost = 1.0        # Leave at default

# ─── LOGGING ───────────────────────────────────────────────────────────────

# Log queries that take longer than this (great for finding slow queries)
log_min_duration_statement = 1000   # Log queries over 1 second (in ms, -1 = disable)
log_line_prefix = '%t [%p]: '       # Timestamp + PID prefix for each log line
```

### 12.2 VACUUM and Autovacuum

Remember from Section 1: updated and deleted rows leave dead tuples behind. VACUUM is the process that cleans them up. PostgreSQL has an **autovacuum** daemon that does this automatically, but it needs to be tuned for high-activity tables.

```sql
-- Run VACUUM manually on a specific table
VACUUM players;

-- VACUUM ANALYZE: cleans AND updates statistics in one pass
VACUUM ANALYZE players;

-- VACUUM FULL: reclaims space back to the OS (locks the table — use pg_repack instead in production)
VACUUM FULL players;

-- Check autovacuum status for all tables
SELECT
    relname,
    last_autovacuum,
    last_autoanalyze,
    autovacuum_count,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY last_autovacuum NULLS FIRST;
```

**Tuning autovacuum for a high-write table:**

The default autovacuum kicks in when dead tuples exceed `autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * table_size`. For a large, busy table this can mean autovacuum waits too long.

```sql
-- Override autovacuum settings for a specific high-write table
-- (instead of changing the global postgresql.conf settings)
ALTER TABLE combat_log SET (
    autovacuum_vacuum_scale_factor = 0.01,    -- Trigger at 1% dead (default 20%)
    autovacuum_vacuum_threshold = 100,         -- Or 100 dead tuples, whichever comes first
    autovacuum_analyze_scale_factor = 0.01,
    autovacuum_vacuum_cost_delay = 2           -- Run faster (less I/O throttling)
);
```

### 12.3 Connection Pooling Overview

PostgreSQL opens a new process for every connection. At 200 connections, that's 200 processes — even if most are idle. Each process uses memory, and the scheduler overhead adds up.

**PgBouncer** is a lightweight connection pooler that sits between your application and PostgreSQL. Your application opens many connections to PgBouncer; PgBouncer maintains a smaller pool of actual PostgreSQL connections and multiplexes requests across them.

```
App (200 connections) → PgBouncer → PostgreSQL (20 actual connections)
```

PgBouncer has three pooling modes:

| Mode | What "one connection" means | Use when |
|---|---|---|
| **Session** | One PostgreSQL connection per application session | Using prepared statements, advisory locks, SET LOCAL |
| **Transaction** | One PostgreSQL connection per transaction | Most web applications — the sweet spot |
| **Statement** | One PostgreSQL connection per statement | Only for simple, stateless queries with no transactions |

A basic PgBouncer config (`pgbouncer.ini`):

```ini
[databases]
game_db = host=localhost port=5432 dbname=game_db

[pgbouncer]
listen_port = 6432
listen_addr = *
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 200      # Max connections from applications
default_pool_size = 20     # Connections PgBouncer keeps open to PostgreSQL
```

The Level 3 notes (DBM Section 18) cover PgBouncer configuration and sizing in much more detail.

### 12.4 Useful Maintenance Queries

```sql
-- Force an immediate checkpoint (flushes all dirty pages to disk)
CHECKPOINT;

-- Reset statistics counters (useful to start fresh after schema or config changes)
SELECT pg_stat_reset();
SELECT pg_stat_reset_single_table_counters('players'::regclass);

-- Identify the oldest transaction (if this is very old, it's blocking vacuum)
SELECT pid, usename, xact_start, NOW() - xact_start AS age
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start ASC
LIMIT 5;

-- Find tables that haven't been vacuumed in over a week
SELECT relname, last_autovacuum, last_vacuum
FROM pg_stat_user_tables
WHERE (last_autovacuum < NOW() - INTERVAL '7 days' OR last_autovacuum IS NULL)
  AND (last_vacuum < NOW() - INTERVAL '7 days' OR last_vacuum IS NULL);
```

---

**Practice:**
1. Check your current `shared_buffers` and `work_mem` settings with `SHOW shared_buffers;`. Look up your server's total RAM and calculate what the recommended values would be.
2. Run `VACUUM ANALYZE` on your busiest table and check `pg_stat_user_tables` before and after to see the `n_dead_tup` count drop.
3. Read your `postgresql.conf` file and identify whether `random_page_cost` has been tuned for SSD or is still at the spinning-disk default of 4.0.

---

## DBM Section 13: Replication & High Availability

**Replication** means keeping one or more copies of your database in sync with the primary, so that if the primary fails, another copy can take over — and so that read-heavy workloads can be spread across multiple servers.

### 13.1 Why Replication?

- **High availability (HA)** — if the primary server fails, a replica can be promoted to primary, minimising downtime
- **Horizontal read scaling** — send read queries to replicas, write queries to the primary
- **Disaster recovery** — a replica in a different location provides geographic redundancy
- **Zero-downtime maintenance** — failover to a replica, maintain the primary, fail back

### 13.2 Streaming Replication

**Streaming replication** is PostgreSQL's built-in physical replication mechanism. The primary sends a continuous stream of WAL data to one or more standby servers. Each standby replays that WAL to stay in sync.

```
Primary → WAL stream → Standby 1 (replica)
                    → Standby 2 (replica)
```

Setting up a streaming replica:

```bash
# On the standby server: take a base backup from the primary
pg_basebackup -h primary-server -U replicator -D /var/lib/postgresql/data -P -R
# The -R flag creates a standby.signal file and writes the primary connection info
# to postgresql.auto.conf automatically
```

```sql
-- On the primary: create a dedicated replication role
CREATE ROLE replicator REPLICATION LOGIN PASSWORD 'secure_password';
```

```ini
# On the primary, in postgresql.conf:
wal_level = replica              # Minimum setting for replication
max_wal_senders = 5              # Max simultaneous streaming connections
```

```sql
-- On the primary: check replication status
SELECT
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_size_pretty(
        pg_wal_lsn_diff(sent_lsn, replay_lsn)
    ) AS replication_lag
FROM pg_stat_replication;
```

### 13.3 Synchronous vs Asynchronous Replication

By default, streaming replication is **asynchronous** — the primary commits a transaction and continues without waiting for the standby to confirm it received the WAL. This means a standby might be slightly behind.

**Synchronous replication** makes the primary wait for at least one standby to confirm before the commit is visible to clients. This guarantees zero data loss but adds latency to every write.

```ini
# postgresql.conf on the primary — wait for standby 'replica1' to confirm
synchronous_standby_names = 'replica1'
synchronous_commit = on          # Default — wait for standby to flush WAL
# synchronous_commit = remote_write  # Weaker: wait for standby to receive, not flush
# synchronous_commit = off           # Don't wait at all (async — may lose last few transactions on crash)
```

### 13.4 Logical Replication

**Logical replication** replicates individual tables or publications rather than the entire database. It decodes WAL changes back into SQL-like operations (INSERT, UPDATE, DELETE) and applies them on the subscriber side.

Use cases:
- Replicating a subset of tables (not the whole database)
- Replicating between different PostgreSQL major versions
- Sending data to a different database for reporting without affecting the primary

```sql
-- On the publisher (primary):
-- Create a publication for specific tables
CREATE PUBLICATION game_data_pub
    FOR TABLE players, guilds, quests;

-- Or publish all tables
CREATE PUBLICATION all_tables_pub FOR ALL TABLES;
```

```sql
-- On the subscriber (replica):
CREATE SUBSCRIPTION game_data_sub
    CONNECTION 'host=primary-server dbname=game_db user=replicator password=xxx'
    PUBLICATION game_data_pub;

-- Check subscription status
SELECT * FROM pg_stat_subscription;
```

### 13.5 Failover and Promotion

When a primary fails, a standby can be promoted to become the new primary.

```bash
# Promote a standby to primary
pg_ctl promote -D /var/lib/postgresql/data
# Or in PostgreSQL 12+:
```

```sql
-- In SQL (PostgreSQL 12+)
SELECT pg_promote();
```

After promotion, the former primary (if it comes back online) becomes a stale standby. It needs to be resynced before it can rejoin as a replica.

### 13.6 Connection Routing

Your application needs to know which server to send writes to (primary) and which to send reads to (replicas). Two common approaches:

**Virtual IP / DNS failover** — a floating IP address or DNS record points to the current primary. On failover, it's updated to point to the new primary. Application connection strings don't change.

**PgBouncer / Patroni** — tools like Patroni automate the detection and promotion process, and PgBouncer can be updated to point to the new primary automatically.

```python
# Application code pattern: separate read and write connection strings
import os

WRITE_DSN = os.environ["DB_PRIMARY_URL"]   # Always points to the primary
READ_DSN  = os.environ["DB_REPLICA_URL"]   # Points to a replica

# Use write connection for mutations
def create_player(name, level):
    with psycopg2.connect(WRITE_DSN) as conn:
        ...

# Use read connection for queries
def get_leaderboard():
    with psycopg2.connect(READ_DSN) as conn:
        ...
```

> [!NOTE]
> Replicas have replication lag — they're slightly behind the primary. For queries that need to see data that was just written (e.g., immediately after a signup, reading the user's own profile), always use the primary. Using a replica for those cases produces the confusing "I just signed up but the page says I don't exist" bug.

---

**Practice:**
1. If you have two PostgreSQL instances available, set up streaming replication between them using `pg_basebackup` and verify it's working with `pg_stat_replication`.
2. On a single instance, create a publication and a subscription on the same server (using a different database as the subscriber) and verify data from the published tables appears on the subscriber.
3. Look up the `synchronous_commit` options and write one sentence explaining the trade-off for each: `on`, `remote_write`, and `off`.

---

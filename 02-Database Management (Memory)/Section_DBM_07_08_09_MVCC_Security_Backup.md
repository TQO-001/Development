## DBM Section 7: MVCC & Concurrency Control

Databases are almost never used by just one person at a time. Multiple connections read and write simultaneously. MVCC is how PostgreSQL keeps them from interfering with each other — without locking readers and writers out of each other's way.

### 7.1 What MVCC Is

**MVCC** stands for Multi-Version Concurrency Control. The core idea is simple: instead of one version of each row, PostgreSQL can keep multiple versions simultaneously. Each transaction sees a consistent snapshot of the database as it was at the moment that transaction started — without being blocked by other transactions writing to the same rows.

When you update a row, PostgreSQL doesn't overwrite it. It writes a new version of the row and marks the old version as "dead" (invisible to new transactions). The old version sticks around until `VACUUM` cleans it up.

```sql
-- Two sessions running at the same time:

-- Session A (starts first):
BEGIN;
SELECT gold FROM players WHERE id = 1;  -- Sees: 2500

-- Session B (runs while A is open):
BEGIN;
UPDATE players SET gold = 3000 WHERE id = 1;
COMMIT;

-- Session A (still in its transaction):
SELECT gold FROM players WHERE id = 1;  -- Still sees: 2500 (its snapshot is from before B's commit)
COMMIT;
```

This is why PostgreSQL readers never block writers and writers never block readers — they're working with different row versions.

### 7.2 Transaction Isolation Levels

MVCC gives you control over what a transaction can "see" from other concurrent transactions. You choose this with the isolation level.

| Isolation Level | Dirty reads | Non-repeatable reads | Phantom reads |
|---|---|---|---|
| **READ COMMITTED** (default) | Not possible | Possible | Possible |
| **REPEATABLE READ** | Not possible | Not possible | Not possible in PostgreSQL |
| **SERIALIZABLE** | Not possible | Not possible | Not possible |

- **Dirty read** — reading uncommitted changes from another transaction (never possible in PostgreSQL)
- **Non-repeatable read** — reading the same row twice in one transaction and getting different values (because another transaction committed a change between your reads)
- **Phantom read** — running the same query twice in one transaction and getting different rows (because another transaction inserted or deleted rows between your reads)

```sql
-- Set isolation level for a single transaction
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- All reads in this transaction see the same consistent snapshot
SELECT gold FROM players WHERE level > 10;  -- Snapshot taken here
-- ... do other work ...
SELECT gold FROM players WHERE level > 10;  -- Same results as above, even if other transactions committed changes
COMMIT;

-- Serializable: the strongest guarantee
-- Transactions behave as if they ran one after another, even though they ran concurrently
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

In practice, **READ COMMITTED** is fine for most application queries. Use **REPEATABLE READ** when a transaction needs to read data multiple times and must see a consistent picture. Use **SERIALIZABLE** only when you have complex business logic where concurrent transactions could interfere with each other in subtle ways.

### 7.3 Locking

MVCC handles the read/write conflict, but PostgreSQL also uses explicit locks for write/write conflicts.

```sql
-- Row-level lock: lock specific rows while working with them
BEGIN;
SELECT * FROM players WHERE id = 1 FOR UPDATE;
-- This row is now locked — other transactions trying to lock or update it will wait
UPDATE players SET gold = gold - 100 WHERE id = 1;
COMMIT;

-- Lock without waiting (fail immediately if already locked)
SELECT * FROM players WHERE id = 1 FOR UPDATE NOWAIT;

-- Skip already-locked rows instead of waiting
SELECT * FROM players WHERE guild_id = 5 FOR UPDATE SKIP LOCKED;
-- Useful for job queues — each worker grabs rows no one else has locked
```

### 7.4 Deadlocks

A deadlock happens when two transactions each hold a lock the other one needs, and both are waiting for the other to release. Neither can proceed.

```
Transaction A locks players row 1, wants to lock players row 2
Transaction B locks players row 2, wants to lock players row 1
Both transactions wait forever — deadlock
```

PostgreSQL detects deadlocks automatically and kills one of the transactions, letting the other proceed. The killed transaction gets an error:

```
ERROR: deadlock detected
DETAIL: Process 12345 waits for ShareLock on transaction 67890; blocked by process 78901.
```

The best way to avoid deadlocks is to always acquire locks in the same order across all transactions. If transaction A always locks row 1 before row 2, and transaction B does the same, they can never deadlock.

### 7.5 Advisory Locks

Advisory locks are application-level locks — they don't protect database objects directly. Your application code asks for a lock by number, and PostgreSQL holds it. Other connections asking for the same number will wait.

```sql
-- Acquire an advisory lock (by an arbitrary integer key your application defines)
-- This blocks until the lock is available
SELECT pg_advisory_lock(12345);

-- Try to acquire without blocking (returns true/false)
SELECT pg_try_advisory_lock(12345);

-- Release it when done
SELECT pg_advisory_unlock(12345);

-- Session-scoped: automatically released when the connection closes
-- Transaction-scoped: automatically released when the transaction ends
SELECT pg_advisory_xact_lock(12345);  -- Released at end of transaction
```

Advisory locks are useful for ensuring only one process does a specific job at a time — like a scheduled task that shouldn't run twice concurrently.

---

**Practice:**
1. Open two psql sessions. In session A, start a transaction and lock a player row with `FOR UPDATE`. Try to update that row from session B. Observe what happens, then commit session A.
2. Deliberately create a deadlock: have two sessions each lock one row, then try to lock the other's row. Observe PostgreSQL's error message.
3. Use `pg_try_advisory_lock(42)` in two sessions — confirm only the first one returns `true`.

---

## DBM Section 8: User Management & Security

PostgreSQL's security model is built around **roles**. Everything that can connect to or act on a database is a role. Granting and revoking privileges on roles controls who can see and touch what.

### 8.1 Roles — Users and Groups Are the Same Thing

PostgreSQL doesn't distinguish between users and groups. Both are just roles. A role can log in (it's a "user"), hold privileges, and be a member of other roles (it's a "group"). These are all just properties on the same object.

```sql
-- Create a login role (a "user")
CREATE ROLE arthur LOGIN PASSWORD 'excalibur123';

-- Create a group role (no login — it's a bucket of permissions)
CREATE ROLE game_readers;
CREATE ROLE game_writers;

-- Grant group membership — arthur now inherits game_readers' privileges
GRANT game_readers TO arthur;

-- Remove membership
REVOKE game_readers FROM arthur;

-- See all roles
SELECT rolname, rolcanlogin, rolsuper FROM pg_roles;

-- Drop a role
DROP ROLE arthur;
```

### 8.2 Granting Privileges

Privileges control what actions a role can perform on specific objects.

```sql
-- Grant SELECT on a table to the game_readers role
GRANT SELECT ON players TO game_readers;
GRANT SELECT ON players, guilds, quests TO game_readers;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO game_readers;

-- Grant write access
GRANT INSERT, UPDATE, DELETE ON players TO game_writers;

-- Grant everything
GRANT ALL PRIVILEGES ON players TO game_writers;

-- Revoke access
REVOKE DELETE ON players FROM game_writers;

-- Grant on sequences (needed for INSERT with SERIAL columns)
GRANT USAGE, SELECT ON SEQUENCE players_id_seq TO game_writers;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO game_writers;
```

### 8.3 Schemas as Access Boundaries

A schema is a namespace inside a database. You can use schemas to partition your objects and grant access at the schema level, rather than table by table.

```sql
-- Create a schema
CREATE SCHEMA game_data;
CREATE SCHEMA analytics;

-- Move a table to a schema
ALTER TABLE players SET SCHEMA game_data;

-- Grant usage on the schema (required to access any object inside it)
GRANT USAGE ON SCHEMA game_data TO game_readers;
GRANT SELECT ON ALL TABLES IN SCHEMA game_data TO game_readers;

-- Default privileges: automatically apply grants to future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA game_data
GRANT SELECT ON TABLES TO game_readers;
```

### 8.4 Row-Level Security (RLS)

Row-Level Security lets you define policies that control which rows a given role can see or modify. The same `SELECT * FROM players` returns different rows depending on who's asking.

```sql
-- Enable RLS on a table
ALTER TABLE players ENABLE ROW LEVEL SECURITY;

-- Policy: each player can only see their own row
-- current_user matches against a 'username' column on the players table
CREATE POLICY player_can_see_own_row
    ON players
    FOR SELECT
    USING (username = current_user);

-- Policy: guild leaders can see all members of their own guild
CREATE POLICY guild_leader_sees_members
    ON players
    FOR SELECT
    USING (
        guild_id = (SELECT guild_id FROM players WHERE username = current_user)
    );

-- Superusers bypass RLS by default. To enforce RLS even for the table owner:
ALTER TABLE players FORCE ROW LEVEL SECURITY;
```

### 8.5 pg_hba.conf — Connection Authentication

`pg_hba.conf` (Host-Based Authentication) controls which hosts can connect to which databases as which users, and how they authenticate. It's the first line of defence.

```
# TYPE    DATABASE    USER         ADDRESS          METHOD
local     all         postgres                      peer       # Local postgres user via peer auth
local     game_db     arthur                        scram-sha-256
host      game_db     game_readers 10.0.0.0/8       scram-sha-256
host      all         all          0.0.0.0/0         reject     # Block all other remote connections
```

After editing, reload without restarting: `SELECT pg_reload_conf();`

---

**Practice:**
1. Create two roles: `reader_role` and `writer_role`. Grant `reader_role` SELECT on all tables, and `writer_role` INSERT/UPDATE/DELETE.
2. Create a login user and grant them `reader_role`. Connect as that user and verify you can SELECT but not INSERT.
3. Enable Row-Level Security on a `notes` table and create a policy so each user can only see rows where `owner = current_user`.

---

## DBM Section 9: Backup & Recovery

If you're not backing up, you're not managing a database — you're gambling with it. This section covers the two types of backups, how to run them, and what to do when you need to use one.

### 9.1 Logical vs Physical Backups

| Type | What it contains | Best for |
|---|---|---|
| **Logical** | SQL statements to recreate the data | Migrating between PostgreSQL versions, selective restores, sharing data |
| **Physical** | A copy of the raw data files | Full server restores, large databases, Point-In-Time Recovery |

### 9.2 pg_dump — Logical Backup

`pg_dump` exports a single database as SQL statements or a binary archive.

```bash
# Dump a database to a plain SQL file
pg_dump -U postgres -d game_db -f game_db_backup.sql

# Dump to a custom binary format (can be restored selectively, faster)
pg_dump -U postgres -d game_db -Fc -f game_db_backup.dump

# Dump only specific tables
pg_dump -U postgres -d game_db -t players -t guilds -Fc -f partial_backup.dump

# Dump the schema only (no data)
pg_dump -U postgres -d game_db --schema-only -f schema_only.sql

# Dump data only (no schema)
pg_dump -U postgres -d game_db --data-only -f data_only.sql
```

### 9.3 pg_dumpall — Backup Everything Including Roles

`pg_dump` only backs up one database. `pg_dumpall` dumps all databases AND all roles and global settings.

```bash
# Dump everything
pg_dumpall -U postgres -f full_cluster_backup.sql
```

### 9.4 pg_restore — Restoring a Backup

```bash
# Restore from a custom-format dump to an existing (empty) database
pg_restore -U postgres -d game_db_restored game_db_backup.dump

# Restore only specific tables
pg_restore -U postgres -d game_db_restored -t players game_db_backup.dump

# Restore and create the database automatically
pg_restore -U postgres -C -d postgres game_db_backup.dump
```

### 9.5 Point-In-Time Recovery (PITR)

Physical backups combined with WAL archiving let you restore a database to any specific moment in time — not just when the backup was taken. This is critical for recovering from accidental data deletion, where you need to restore to "just before the mistake happened."

The setup involves three pieces:
1. A **base backup** — a snapshot of the data files (taken with `pg_basebackup`)
2. **WAL archiving** — continuously copying WAL files to safe storage
3. **Recovery** — restoring the base backup and replaying WAL files up to the target time

```bash
# Take a base backup
pg_basebackup -U postgres -D /backup/base -Ft -z -P

# In postgresql.conf, enable WAL archiving:
# archive_mode = on
# archive_command = 'cp %p /backup/wal/%f'
# wal_level = replica
```

Restoring to a specific point:

```bash
# 1. Restore the base backup to a new data directory
tar -xf /backup/base/base.tar.gz -C /var/lib/postgresql/data_restored/

# 2. Create a recovery.signal file (tells PostgreSQL to enter recovery mode)
touch /var/lib/postgresql/data_restored/recovery.signal

# 3. In postgresql.conf (or recovery.conf for older versions):
# restore_command = 'cp /backup/wal/%f %p'
# recovery_target_time = '2025-06-15 14:30:00'
```

### 9.6 Backup Strategy Fundamentals

Every backup strategy involves a trade-off between two things:

- **RTO** (Recovery Time Objective) — how long is acceptable to be down while restoring?
- **RPO** (Recovery Point Objective) — how much data loss is acceptable? (i.e., how old can the backup be?)

| Strategy | Frequency | RTO | RPO |
|---|---|---|---|
| Daily logical backup only | Every 24 hours | Hours | Up to 24 hours of data |
| Daily physical + WAL archiving | Continuous | Minutes–hours | Near zero (seconds) |
| Streaming replica (Section 13) | Real-time | Seconds | Near zero |

> [!NOTE]
> A backup you've never tested restoring from is not a reliable backup. Schedule regular restore drills — restore to a test environment, verify the data is intact. Finding out your backup is broken when production is down is the worst possible moment to discover it.

---

**Practice:**
1. Use `pg_dump` to export your game database to both a `.sql` file and a `.dump` (custom format) file.
2. Create a new empty database and use `pg_restore` to restore the `.dump` file into it. Verify the tables and data are intact.
3. Do a schema-only dump and a data-only dump. Check that the schema dump contains no `INSERT` statements and the data dump contains no `CREATE TABLE` statements.

---

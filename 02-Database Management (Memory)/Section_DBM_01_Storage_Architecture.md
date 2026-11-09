## DBM Section 1: How Databases Store Data

Before you can tune a database, design a schema well, or understand why a query is slow, you need a mental picture of where your data actually lives — physically, on disk. Most developers never think about this, and that's exactly why so many performance problems catch them off guard. This section is about building that picture.

### 1.1 Pages — The Basic Unit of Storage

A database doesn't store data one row at a time. It reads and writes data in fixed-size chunks called **pages** (also called blocks). In PostgreSQL, every page is exactly **8 KB**.

Think of the database's storage like a library. The rows in your `players` table are individual scrolls. But the library doesn't retrieve scrolls one by one — it moves entire shelving units at a time. Each shelving unit holds several scrolls. That shelving unit is the page.

This has a big consequence: even if you only `SELECT` one row, the database may need to read the entire 8 KB page that row sits on. If the rows you need are scattered across many pages (because of inserts, updates, and deletes over time), the database has to fetch many pages — even for a small result set.

```sql
-- PostgreSQL's page size (almost always 8192 bytes = 8 KB)
SHOW block_size;
-- Result: 8192

-- How many pages does the players table occupy?
SELECT
    relname       AS table_name,
    relpages      AS total_pages,
    relpages * 8  AS total_kb
FROM pg_class
WHERE relname = 'players';
```

### 1.2 Heap Files — Where Rows Actually Live

The main storage file for a table is called the **heap**. This is where PostgreSQL stores your actual row data. Rows within a page are called **tuples**, and each tuple has a header containing visibility information (which transactions can see this row — more on that in the MVCC section).

Rows inside a page aren't necessarily ordered. When you insert a row, PostgreSQL places it in the first page with enough free space. When you update a row, PostgreSQL doesn't modify the existing tuple in place — it writes a new tuple and marks the old one as dead (visible to no one). This is the foundation of how concurrency works, and it's why regular `VACUUM` is needed to reclaim that dead space.

```sql
-- See how "bloated" a table has become from dead tuples
-- (requires pg_stat_user_tables to be populated — happens after some activity)
SELECT
    relname                         AS table_name,
    n_live_tup                      AS live_rows,
    n_dead_tup                      AS dead_rows,
    ROUND(n_dead_tup::numeric /
        NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY dead_pct DESC NULLS LAST;
```

### 1.3 TOAST — Handling Big Values

PostgreSQL has a strict rule: a single row tuple must fit within one page (8 KB). But what if Arthur's character backstory is 50 KB of text? Or a `JSONB` column holds a massive document?

PostgreSQL handles this with **TOAST** (The Oversized Attribute Storage Technique). When a value is too large to fit in a regular page, PostgreSQL automatically:
1. Compresses it (if compression helps)
2. If still too large, moves it to a separate **TOAST table** stored alongside the main table
3. Stores a pointer to it in the original row

This happens transparently — your queries don't need to do anything differently. But it's worth knowing about because:
- Large `TEXT`, `BYTEA`, `JSONB`, and `XML` values live in the TOAST table
- Fetching TOASTed values requires an extra lookup, which can slow queries on columns with large values

```sql
-- See a table's associated TOAST table
SELECT
    c.relname            AS main_table,
    t.relname            AS toast_table,
    t.relpages * 8       AS toast_size_kb
FROM pg_class c
LEFT JOIN pg_class t ON c.reltoastrelid = t.oid
WHERE c.relname = 'characters'
  AND c.relkind = 'r';
```

### 1.4 The Write-Ahead Log (WAL)

The **WAL** is one of the most important concepts in database reliability. Every change to your data — every INSERT, UPDATE, DELETE — is first written to the WAL before it's written to the actual data files on disk.

Think of the WAL as a captain's log: every action is recorded in the log before it's carried out. If the ship sinks mid-voyage (server crash), the new crew can read the log and know exactly what was done, what was in progress, and what needs to be finished or undone.

This gives PostgreSQL two guarantees:
- **Durability** — once a transaction is committed, the WAL record exists on disk. Even if the server crashes immediately after, the data won't be lost.
- **Crash recovery** — on restart after a crash, PostgreSQL reads the WAL and replays any committed changes that didn't make it to the data files yet.

The WAL is also the foundation of replication (Section 13) and point-in-time recovery (Section 9).

```sql
-- See the current WAL write position
SELECT pg_current_wal_lsn();
-- Returns something like: 0/3A7F2B8 (a WAL location identifier)

-- See how much WAL has been generated since a point in time
-- (useful for estimating replication lag or backup size)
SELECT pg_size_pretty(
    pg_wal_lsn_diff(pg_current_wal_lsn(), '0/3A7F2B8')
);
```

### 1.5 Why This Matters for Performance

| Storage concept | What it means for performance |
|---|---|
| **Page size (8 KB)** | Reading one row costs the same as reading ~100 small rows on the same page |
| **Heap layout** | Rows scattered across many pages = many disk reads = slow queries |
| **Dead tuples** | Too many dead tuples wastes pages, making scans slower — vacuum regularly |
| **TOAST** | Querying large columns adds extra lookups — avoid `SELECT *` on wide tables |
| **WAL writes** | Every write generates WAL — heavy write workloads can be WAL-bound |

> [!NOTE]
> You don't need to manage any of this manually. But understanding it explains *why* things like `VACUUM`, indexes, and selective `SELECT` columns matter. Most "magic" performance advice starts making sense once you picture what's happening on disk.

---

**Practice:**
1. Run `SHOW block_size;` on your PostgreSQL instance and confirm the page size.
2. On any table you have with some data, query `pg_class` to find out how many pages it uses and estimate its total size in KB.
3. Run the dead tuple query from Section 1.2 on your database. If you see a table with a high `dead_pct`, run `VACUUM ANALYZE table_name;` and check the numbers again.

---

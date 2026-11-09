## DBM Section 4: Data Integrity Beyond Basic Constraints

You already know the standard constraints — `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`. Those are the basics and they handle most cases. This section covers what to reach for when the basics aren't enough: constraints that need to be checked at the end of a transaction rather than immediately, constraints that prevent overlapping ranges, and patterns for tracking and recovering data that changes over time.

### 4.1 Deferred Constraints

By default, PostgreSQL checks constraints immediately after every statement. If a check fails, the statement is rolled back right away. But sometimes you need constraints checked at the **end of the transaction** rather than after each individual statement. This is called a **deferred constraint**.

The classic case: you have two rows that reference each other (a circular foreign key), and you need to insert both. Checking immediately would fail — row A references row B, which doesn't exist yet.

```sql
-- Create a constraint that can be deferred until COMMIT
CREATE TABLE locations (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    connects_to INTEGER  -- Links to another location
        REFERENCES locations(id)
        DEFERRABLE INITIALLY DEFERRED  -- Check at end of transaction, not after each statement
);

-- Now we can insert both locations in the same transaction without ordering problems
BEGIN;

INSERT INTO locations (id, name, connects_to) VALUES (1, 'Camelot', 2);
-- This would normally fail immediately — location id=2 doesn't exist yet
-- But with DEFERRABLE, the check waits until COMMIT

INSERT INTO locations (id, name, connects_to) VALUES (2, 'Avalon', 1);

COMMIT;
-- NOW PostgreSQL checks the constraints — both rows exist, both pass
```

You can also flip a constraint's timing within a transaction on the fly:

```sql
-- Temporarily defer all deferrable constraints in this transaction
SET CONSTRAINTS ALL DEFERRED;

-- Or defer a specific one by name
SET CONSTRAINTS fk_locations_connects_to DEFERRED;
```

### 4.2 Exclusion Constraints

An exclusion constraint is like a generalised unique constraint — instead of requiring "no two rows have the same value in column X", it lets you say "no two rows satisfy condition Y together". The most useful application is preventing overlapping ranges.

```sql
-- Prevent a player from being booked in two quests at the same time
-- Requires the btree_gist extension (ships with PostgreSQL)
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE quest_bookings (
    id         SERIAL PRIMARY KEY,
    player_id  INTEGER NOT NULL REFERENCES players(id),
    quest_id   INTEGER NOT NULL REFERENCES quests(id),
    start_time TIMESTAMP NOT NULL,
    end_time   TIMESTAMP NOT NULL,

    -- Reject any INSERT or UPDATE that would result in the same player having
    -- two overlapping bookings (start_time, end_time ranges that overlap)
    CONSTRAINT no_double_booking
        EXCLUDE USING GIST (
            player_id WITH =,                            -- same player
            tsrange(start_time, end_time) WITH &&        -- overlapping time range
        )
);

-- This insert succeeds
INSERT INTO quest_bookings (player_id, quest_id, start_time, end_time)
VALUES (1, 10, '2025-06-01 09:00', '2025-06-01 12:00');

-- This insert fails — same player, overlapping time
INSERT INTO quest_bookings (player_id, quest_id, start_time, end_time)
VALUES (1, 11, '2025-06-01 11:00', '2025-06-01 14:00');
-- ERROR: conflicting key value violates exclusion constraint "no_double_booking"
```

### 4.3 Triggers for Data Integrity

`CHECK` constraints work on a single row in isolation. But some integrity rules span multiple rows or tables — and for those, triggers are the right tool. Unlike the audit triggers from Section 13 of the SQL notes, these triggers exist purely to enforce a rule.

```sql
-- Rule: a guild can have at most 10 members
CREATE OR REPLACE FUNCTION check_guild_capacity()
RETURNS TRIGGER AS $$
DECLARE
    current_members INTEGER;
    max_members INTEGER := 10;
BEGIN
    -- Count how many players are already in this guild
    SELECT COUNT(*) INTO current_members
    FROM players
    WHERE guild_id = NEW.guild_id;

    IF current_members >= max_members THEN
        RAISE EXCEPTION 'Guild % is full (max % members)', NEW.guild_id, max_members;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_guild_capacity
BEFORE INSERT OR UPDATE OF guild_id ON players
FOR EACH ROW
WHEN (NEW.guild_id IS NOT NULL)
EXECUTE FUNCTION check_guild_capacity();
```

### 4.4 Audit Tables — Tracking Every Change

An audit trail records what changed, who changed it, and when. This is a legal requirement in some industries and a debugging lifesaver in most others.

```sql
-- Audit table: stores a snapshot of the row before every change
CREATE TABLE players_audit (
    audit_id     BIGSERIAL PRIMARY KEY,
    player_id    INTEGER NOT NULL,
    operation    VARCHAR(10) NOT NULL,  -- 'INSERT', 'UPDATE', or 'DELETE'
    changed_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    changed_by   VARCHAR(100) DEFAULT current_user,
    old_data     JSONB,  -- The row BEFORE the change (NULL on INSERT)
    new_data     JSONB   -- The row AFTER the change (NULL on DELETE)
);

-- Trigger function that writes to the audit table on every change
CREATE OR REPLACE FUNCTION audit_players()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_players
AFTER INSERT OR UPDATE OR DELETE ON players
FOR EACH ROW EXECUTE FUNCTION audit_players();
```

### 4.5 Soft Deletes

A **soft delete** means rows are never physically removed from the database. Instead, a `deleted_at` timestamp column is set when a record is "deleted". The row remains in the table — it's just filtered out of normal queries.

This is useful when you need to:
- Recover accidentally deleted records
- Keep a history for compliance
- Maintain referential integrity across related records

```sql
-- Add a soft-delete column to the players table
ALTER TABLE players ADD COLUMN deleted_at TIMESTAMP;

-- "Delete" a player (soft delete — just marks them as deleted)
UPDATE players SET deleted_at = NOW() WHERE id = 1;

-- The player is still in the database, just marked
SELECT * FROM players WHERE id = 1;  -- Still returns the row

-- In all normal queries, filter out deleted rows
SELECT * FROM players WHERE deleted_at IS NULL;

-- Create a view so application code doesn't have to remember to add the filter
CREATE OR REPLACE VIEW active_players AS
SELECT * FROM players WHERE deleted_at IS NULL;

-- Hard restore: un-delete a player
UPDATE players SET deleted_at = NULL WHERE id = 1;
```

> [!NOTE]
> Soft deletes require discipline — every query your application runs must filter by `deleted_at IS NULL`, or you'll accidentally return deleted records. The view approach solves this cleanly. Just make sure your team always queries the view, not the underlying table directly.

---

**Practice:**
1. Create a `deferrable` foreign key and demonstrate inserting two mutually-referencing rows in a single transaction.
2. Add an audit trigger to your `players` table that records every UPDATE to a `players_audit` table, capturing the old and new JSONB values.
3. Add a `deleted_at` column to a table and create an `active_players` view that filters soft-deleted rows automatically.

---

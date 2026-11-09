## DBM Section 2: Database Design Principles

A well-designed database is one of the best investments you can make in a project. A badly designed one creates bugs, performance problems, and contradictory data that are almost impossible to fix later — especially once there's real data in production. This section covers how to design schemas that stay clean and correct as they grow.

### 2.1 The Goal: One Fact in One Place

The core principle of relational database design is simple: every piece of information should be stored in exactly one place. If Arthur's guild name appears in both the `players` table and the `inventory` table, and you rename the guild, you have to update it in two places. Miss one, and your data now contradicts itself.

The formal system for achieving "one fact in one place" is called **normalisation**. It's a series of rules (called Normal Forms) that progressively eliminate redundancy and ambiguity from your schema.

### 2.2 First Normal Form (1NF)

A table is in 1NF when:
- Every column holds a single, atomic value (no lists, no comma-separated values, no repeating groups)
- Every row is uniquely identifiable (there's a primary key)

```sql
-- ❌ VIOLATES 1NF — multiple values in one column
-- +----+----------+---------------------------+
-- | id |   name   |         skills            |
-- +----+----------+---------------------------+
-- |  1 | Arthur   | "Slash, Block, Parry"     |  <- comma-separated list in one cell
-- |  2 | Merlin   | "Fireball, Teleport"      |
-- +----+----------+---------------------------+

-- ✅ SATISFIES 1NF — one value per cell
-- players table:         player_skills table:
-- +----+----------+      +----+-----------+------------+
-- | id |   name   |      | id | player_id | skill_name |
-- +----+----------+      +----+-----------+------------+
-- |  1 | Arthur   |      |  1 |     1     | Slash      |
-- |  2 | Merlin   |      |  2 |     1     | Block      |
--                        |  3 |     1     | Parry      |
--                        |  4 |     2     | Fireball   |
--                        |  5 |     2     | Teleport   |

CREATE TABLE player_skills (
    id         SERIAL PRIMARY KEY,
    player_id  INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL
);
```

### 2.3 Second Normal Form (2NF)

A table is in 2NF when it's in 1NF AND every non-key column depends on the **entire** primary key — not just part of it. This only applies to tables with composite primary keys (keys made of more than one column).

```sql
-- ❌ VIOLATES 2NF — 'guild_name' depends only on 'guild_id', not on the whole key
-- quest_assignments table (composite PK: player_id + quest_id):
-- +----+-----------+----------+------------+
-- | id | player_id | quest_id | guild_name |  <- guild_name only depends on player_id!
-- +----+-----------+----------+------------+
-- This means guild_name is stored once per quest assignment, not once per player

-- ✅ SATISFIES 2NF — move guild_name to the players table where it belongs
-- quest_assignments: (player_id, quest_id, assigned_at)
-- players:           (id, name, guild_id, ...)
-- guilds:            (id, guild_name, ...)
```

### 2.4 Third Normal Form (3NF)

A table is in 3NF when it's in 2NF AND no non-key column depends on another non-key column. In other words: non-key columns should depend on the primary key, not on each other.

```sql
-- ❌ VIOLATES 3NF — guild_leader depends on guild_name, not on player_id
-- players table:
-- +----+----------+------------------+--------------+
-- | id |   name   |    guild_name    | guild_leader |
-- +----+----------+------------------+--------------+
-- |  1 | Arthur   | Knights of Camelot | Arthur     |  <- guild_leader is a property
-- |  2 | Lancelot | Knights of Camelot | Arthur     |     of the guild, not the player
-- |  3 | Merlin   | Order of the Arc  | Merlin      |

-- ✅ SATISFIES 3NF — extract guilds into their own table
CREATE TABLE guilds (
    id           SERIAL PRIMARY KEY,
    guild_name   VARCHAR(100) NOT NULL UNIQUE,
    guild_leader VARCHAR(100)
);

CREATE TABLE players (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    guild_id  INTEGER REFERENCES guilds(id)
);
```

### 2.5 Boyce-Codd Normal Form (BCNF)

BCNF is a slightly stricter version of 3NF. A table is in BCNF when every "determinant" (a column or set of columns that determines another column's value) is a candidate key. In practice, most tables that are in 3NF are also in BCNF. The differences are subtle and rarely cause issues in application databases, but it's worth knowing the term exists.

### 2.6 Normalisation Summary

| Normal Form | Rule in plain English |
|---|---|
| **1NF** | One value per cell. Every row has a unique identifier. |
| **2NF** | Every column depends on the whole primary key, not just part of it. |
| **3NF** | No column depends on another non-key column. |
| **BCNF** | Every determinant is a candidate key. |

The practical target for most application databases is **3NF**. It eliminates the most common sources of data inconsistency without making your schema so fragmented that queries become painful.

### 2.7 When to Denormalise Deliberately

Normalisation is the correct default. But sometimes, for performance or simplicity, you deliberately break the rules. This is called **denormalisation**, and it's a conscious trade-off — not a mistake.

Common reasons to denormalise:
- **Read performance** — a highly normalised schema might need 5 JOINs to answer a common query. Storing a pre-joined result can be faster, at the cost of some redundancy.
- **Reporting and analytics** — OLAP (analytics) workloads often benefit from denormalised "wide tables" that avoid joins entirely.
- **Caching a derived value** — storing a `total_gold` column that's recalculated on every update avoids a slow `SUM()` query on every read.

```sql
-- Example: denormalised 'total_items' on the players table
-- Instead of always running: SELECT COUNT(*) FROM inventory WHERE player_id = 1;
-- We store it directly:
ALTER TABLE players ADD COLUMN total_items INTEGER DEFAULT 0;

-- A trigger keeps it in sync (so it never goes stale)
CREATE OR REPLACE FUNCTION sync_item_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE players SET total_items = total_items + 1 WHERE id = NEW.player_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE players SET total_items = total_items - 1 WHERE id = OLD.player_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_item_count
AFTER INSERT OR DELETE ON inventory
FOR EACH ROW EXECUTE FUNCTION sync_item_count();
```

> [!NOTE]
> Always normalise first, then denormalise only where you have a measured performance problem. Premature denormalisation creates maintenance headaches and inconsistency bugs that are much harder to fix than a slow query.

### 2.8 Entity-Relationship (ER) Diagrams

An ER diagram is a visual map of your tables and how they relate. Before writing any `CREATE TABLE` statements, sketching an ER diagram helps you find design mistakes while they're still cheap to fix.

Key symbols (using crow's foot notation — the most common style):
- A rectangle = a table
- Lines between rectangles = relationships
- The end of the line shows cardinality (how many)

```
players ————< inventory       (one player has many inventory items)
players >———< guilds          (many players, many guilds — needs junction table)
quests ——|—— quest_rewards    (one quest has exactly one rewards record)
```

Reading the line ends:
- `|` = exactly one
- `<` or `>` = many
- `O` = zero (optional)

A sketch on paper before coding saves hours of painful migrations later.

---

**Practice:**
1. Take a table in your own project that stores comma-separated values in a single column (or imagine one). Redesign it to satisfy 1NF.
2. Draw a rough ER diagram for a game database with `players`, `guilds`, `quests`, and `inventory`. Mark the cardinality on each relationship.
3. Identify one place in a schema you've worked on (or the game example) where a 3NF violation exists — a non-key column that depends on another non-key column — and redesign it.

---

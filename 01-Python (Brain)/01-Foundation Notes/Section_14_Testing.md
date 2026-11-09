## Section 14: Testing with pytest

Writing code without tests is like building a dungeon without checking if the floor holds. Everything looks fine until someone walks on it. Testing is how you prove your code does what you think it does — and more importantly, how you prove it *keeps* doing that after every change you make.

`pytest` is the standard testing library for Python. It's simple to start with, and powerful enough to handle complex scenarios.

```bash
pip install pytest pytest-mock
```

### 14.1 Writing Your First Test

pytest discovers tests automatically by looking for files named `test_*.py` and functions named `test_*`. No classes required, no boilerplate — just write a function and call `assert`.

```python
# File: test_combat.py

def calculate_damage(base_attack: int, multiplier: float) -> int:
    """Calculates damage dealt."""
    return int(base_attack * multiplier)

# pytest finds this because it starts with 'test_'
def test_basic_damage():
    result = calculate_damage(50, 1.5)
    assert result == 75

def test_zero_multiplier():
    result = calculate_damage(50, 0.0)
    assert result == 0

def test_large_values():
    result = calculate_damage(9999, 2.0)
    assert result == 19998
```

```bash
# Run all tests
pytest

# Run tests in a specific file
pytest test_combat.py

# Run with verbose output (shows each test name)
pytest -v

# Stop after the first failure
pytest -x
```

Output:

```
test_combat.py::test_basic_damage     PASSED
test_combat.py::test_zero_multiplier  PASSED
test_combat.py::test_large_values     PASSED

3 passed in 0.04s
```

### 14.2 Testing Exceptions

When you expect a function to raise an exception, use `pytest.raises()` as a context manager.

```python
import pytest

def buy_item(gold: int, cost: int) -> int:
    if cost > gold:
        raise ValueError(f"Not enough gold. Have {gold}, need {cost}.")
    return gold - cost

def test_insufficient_gold_raises():
    with pytest.raises(ValueError) as exc_info:
        buy_item(gold=100, cost=500)

    # You can inspect the exception message
    assert "Not enough gold" in str(exc_info.value)

def test_exact_gold_succeeds():
    remaining = buy_item(gold=500, cost=500)
    assert remaining == 0
```

### 14.3 Fixtures — Reusable Setup Code

A **fixture** is a function marked with `@pytest.fixture` that provides a reusable piece of test setup. Instead of writing the same setup code in every test, you write it once as a fixture and reference it by name in your test function parameters.

```python
import pytest

class Player:
    def __init__(self, name: str, gold: int, level: int):
        self.name = name
        self.gold = gold
        self.level = level

    def level_up(self):
        self.level += 1
        self.gold += self.level * 100

# Fixture: creates a fresh Player for each test that needs one
@pytest.fixture
def arthur():
    return Player(name="Arthur", gold=2500, level=15)

# Any test that names 'arthur' as a parameter gets a fresh Player automatically
def test_level_up_increases_level(arthur):
    arthur.level_up()
    assert arthur.level == 16

def test_level_up_awards_gold(arthur):
    initial_gold = arthur.gold
    arthur.level_up()
    # Level 16 * 100 = 1600 gold awarded
    assert arthur.gold == initial_gold + 1600

def test_player_name_unchanged(arthur):
    arthur.level_up()
    assert arthur.name == "Arthur"  # Name never changes
```

Fixtures have **scope** — by default they run fresh for each test. You can make them run once per module or session for expensive setup (like a database connection):

```python
@pytest.fixture(scope="module")  # Runs once for all tests in the file
def db_connection():
    conn = create_test_connection()
    yield conn          # 'yield' means this is also teardown code
    conn.close()        # This runs after all tests in the module finish
```

### 14.4 Parametrize — Testing Multiple Cases at Once

`@pytest.mark.parametrize` lets you run the same test with different input/output combinations. Much cleaner than copying the same test three times.

```python
import pytest

def get_status(health: int) -> str:
    if health >= 75:   return "Healthy"
    if health >= 40:   return "Wounded"
    if health > 0:     return "Critical"
    return "Dead"

@pytest.mark.parametrize("health, expected_status", [
    (100, "Healthy"),
    (75,  "Healthy"),
    (74,  "Wounded"),
    (40,  "Wounded"),
    (39,  "Critical"),
    (1,   "Critical"),
    (0,   "Dead"),
    (-10, "Dead"),
])
def test_get_status(health, expected_status):
    assert get_status(health) == expected_status
```

pytest runs this as 8 separate tests and reports each one individually:

```
PASSED test_player.py::test_get_status[100-Healthy]
PASSED test_player.py::test_get_status[75-Healthy]
PASSED test_player.py::test_get_status[74-Wounded]
...
```

### 14.5 Mocking — Replacing Real Dependencies in Tests

A **mock** is a fake object that stands in for a real dependency (a database, an external API, a file) during testing. You're testing your code's logic, not the real dependency's behaviour.

```python
from unittest.mock import MagicMock, patch
import pytest

def get_player_from_db(player_id: int) -> dict:
    """In real code, this hits the database."""
    raise NotImplementedError("Real DB call")

def get_player_display_name(player_id: int) -> str:
    """Gets a player and formats their display name."""
    player = get_player_from_db(player_id)
    return f"{player['name']} (Level {player['level']})"

# Mock the database call so the test doesn't need a real database
def test_display_name_format(monkeypatch):
    # monkeypatch replaces get_player_from_db with a function that returns fake data
    def fake_db_call(player_id):
        return {"name": "Arthur", "level": 15, "gold": 2500}

    monkeypatch.setattr("__main__.get_player_from_db", fake_db_call)

    result = get_player_display_name(1)
    assert result == "Arthur (Level 15)"
```

Using `unittest.mock.patch` (more common in larger codebases):

```python
from unittest.mock import patch, MagicMock

def test_display_name_with_patch():
    with patch("__main__.get_player_from_db") as mock_db:
        mock_db.return_value = {"name": "Merlin", "level": 22}

        result = get_player_display_name(2)

        assert result == "Merlin (Level 22)"
        mock_db.assert_called_once_with(2)  # Verify it was called with the right argument
```

### 14.6 Testing Database Code

For tests that involve a real database, use a test database (never your dev or prod database) and roll back after each test so tests don't affect each other.

```python
import psycopg2
import pytest

TEST_DSN = "postgresql://test_user:password@localhost/test_game_db"

@pytest.fixture
def db_conn():
    """Provides a database connection that rolls back after each test."""
    conn = psycopg2.connect(TEST_DSN)
    conn.autocommit = False  # Everything goes into a transaction
    yield conn
    conn.rollback()          # Undo everything the test did
    conn.close()

def test_insert_player(db_conn):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO players (name, level, gold) VALUES (%s, %s, %s) RETURNING id;",
        ("TestArthur", 1, 0)
    )
    new_id = cursor.fetchone()[0]
    assert new_id is not None

    # Verify the insert actually worked within this transaction
    cursor.execute("SELECT name FROM players WHERE id = %s;", (new_id,))
    name = cursor.fetchone()[0]
    assert name == "TestArthur"

    # After this test, db_conn fixture rolls back — no test data pollutes the database
```

### 14.7 Organising Tests

```
project/
├── src/
│   ├── combat.py
│   ├── players.py
│   └── quests.py
└── tests/
    ├── conftest.py          ← Shared fixtures available to all test files
    ├── test_combat.py
    ├── test_players.py
    └── test_quests.py
```

`conftest.py` is special — pytest automatically loads it. Put shared fixtures there:

```python
# tests/conftest.py
import pytest
import psycopg2

@pytest.fixture(scope="session")
def db_conn():
    """One connection for the entire test session."""
    conn = psycopg2.connect("postgresql://test_user:password@localhost/test_db")
    yield conn
    conn.close()
```

---

**Practice:**
1. Write a function `calculate_xp_to_next_level(current_level)` that returns `current_level * 100`. Write at least 3 parametrized tests covering level 1, level 10, and level 50.
2. Write a function that raises `ValueError` if a player name is shorter than 3 characters. Write a test using `pytest.raises()` to verify the exception is raised with the right message.
3. Write a test for a function that calls an external API (mock it with `monkeypatch` or `patch`). The mock should return a fixed response, and your test should verify the function processes it correctly.

---

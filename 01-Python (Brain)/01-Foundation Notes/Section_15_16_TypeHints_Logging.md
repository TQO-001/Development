## Section 15: Type Hints & Pydantic

Python's type hints don't change how your code runs — Python still ignores them at runtime. But they do three very useful things: they make your code's intent clearer to anyone reading it, they let your IDE catch type mismatches before you even run anything, and with Pydantic, they power automatic validation and serialization of data coming into your application.

```bash
pip install pydantic
```

### 15.1 Full Type Hints

You've already seen basic type hints (`name: str`, `level: int`). Here are the more advanced patterns you'll use constantly in real codebases:

```python
from typing import Optional, Union, Any
from collections.abc import Sequence, Callable

# Optional: the value can be the stated type OR None
def find_player(player_id: int) -> Optional[dict]:
    ...  # Returns a dict if found, None if not

# Union: accepts multiple types
def parse_id(raw_id: str | int) -> int:  # Python 3.10+ union syntax
    return int(raw_id)

# Lists, dicts, tuples with typed contents
def get_scores() -> list[int]: ...
def get_player_map() -> dict[str, int]: ...  # str keys, int values
def get_coords() -> tuple[float, float]: ...  # exactly (x, y)

# Callable: a function as an argument
def apply_to_all(items: list[int], func: Callable[[int], int]) -> list[int]:
    return [func(item) for item in items]

# Sequence: any ordered collection (list, tuple, etc.) — more flexible than list
def process_names(names: Sequence[str]) -> list[str]:
    return [name.upper() for name in names]

# TypeVar: for generic functions that preserve the type
from typing import TypeVar
T = TypeVar('T')

def first_or_default(items: list[T], default: T) -> T:
    return items[0] if items else default

result: int = first_or_default([1, 2, 3], 0)    # Returns int
result2: str = first_or_default([], "unknown")    # Returns str
```

### 15.2 Pydantic Models — Validated Data Classes

A Pydantic `BaseModel` is a class where every attribute is type-checked and validated automatically when the model is created. If the data doesn't match, Pydantic raises a clear error with a helpful message — before that bad data ever touches your business logic.

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class Player(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    level: int = Field(ge=1, le=100)      # ge=greater-or-equal, le=less-or-equal
    gold: int = Field(default=0, ge=0)
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Custom validator for a specific field
    @field_validator('name')
    @classmethod
    def name_cannot_be_reserved(cls, v: str) -> str:
        reserved = {'admin', 'root', 'system'}
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved name.")
        return v.strip()  # Always strip whitespace from names

# Valid data — creates the model cleanly
arthur = Player(name="Arthur", level=15, gold=2500, role="Warrior")
print(arthur.model_dump())
# {'name': 'Arthur', 'level': 15, 'gold': 2500, 'role': 'Warrior', 'created_at': datetime(...)}

# Invalid data — raises ValidationError with a clear message
try:
    bad_player = Player(name="X", level=150, gold=-100)
except Exception as e:
    print(e)
# 3 validation errors for Player
# name: String should have at least 3 characters
# level: Input should be less than or equal to 100
# gold: Input should be greater than or equal to 0
```

### 15.3 Nested Models and Serialization

```python
from pydantic import BaseModel
from typing import Optional

class Guild(BaseModel):
    id: int
    name: str

class PlayerWithGuild(BaseModel):
    name: str
    level: int
    guild: Optional[Guild] = None

# Nested models are validated recursively
player = PlayerWithGuild(
    name="Arthur",
    level=15,
    guild={"id": 1, "name": "Knights of Camelot"}  # Dict is coerced to Guild model
)
print(player.guild.name)  # "Knights of Camelot"

# Serialize to a dict
player.model_dump()
# {'name': 'Arthur', 'level': 15, 'guild': {'id': 1, 'name': 'Knights of Camelot'}}

# Serialize to JSON
player.model_dump_json()
# '{"name":"Arthur","level":15,"guild":{"id":1,"name":"Knights of Camelot"}}'

# Create a model from JSON
json_string = '{"name": "Merlin", "level": 22, "guild": null}'
merlin = PlayerWithGuild.model_validate_json(json_string)
```

### 15.4 Pydantic Settings — Configuration Management

`pydantic-settings` lets you define your application's config as a Pydantic model. It automatically reads from environment variables and `.env` files, with full validation.

```bash
pip install pydantic-settings
```

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    # Field names match environment variable names (case-insensitive)
    database_url: str = Field(
        description="Full PostgreSQL connection string"
    )
    secret_key: SecretStr = Field(
        description="JWT signing secret — never log this"
    )
    debug: bool = False
    max_connections: int = Field(default=10, ge=1, le=100)
    app_name: str = "Game API"

    model_config = SettingsConfigDict(
        env_file=".env",           # Load from .env file in the project root
        env_file_encoding="utf-8",
        case_sensitive=False       # DATABASE_URL and database_url both work
    )

# Single instance shared across the app
settings = Settings()

# Usage
print(settings.app_name)
print(settings.max_connections)
# settings.secret_key.get_secret_value()  — SecretStr hides the value in logs
```

```ini
# .env file
DATABASE_URL=postgresql://admin:secret@localhost/game_db
SECRET_KEY=supersecretjwtsigningkey
DEBUG=false
MAX_CONNECTIONS=20
```

### 15.5 Response Schemas for APIs

In FastAPI (Section 17), Pydantic models serve as request and response schemas. You'll define separate models for creating, reading, and updating resources:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# What the client sends to CREATE a player
class PlayerCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    role: Optional[str] = None

# What the API returns when READING a player (includes server-generated fields)
class PlayerResponse(BaseModel):
    id: int
    name: str
    level: int
    gold: int
    role: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}  # Allows creating from ORM objects or dicts
```

---

**Practice:**
1. Create a `Quest` Pydantic model with `title` (min 5 chars), `difficulty` (1–10), `reward_gold` (≥0), and `status` (one of: `'open'`, `'active'`, `'complete'`). Test that invalid inputs raise `ValidationError`.
2. Add a `@field_validator` to your Quest model that rejects any title containing the word `"test"` (case-insensitive).
3. Create a `Settings` class using `pydantic-settings` with `DATABASE_URL` and `DEBUG` fields. Load them from a `.env` file and print them.

---

## Section 16: Structured Logging & Observability

`print()` is not logging. Print statements disappear in production, can't be filtered, can't be sent to a log aggregator, and give you no context about when, where, or at what severity something happened. Python's `logging` module — used properly — gives you all of that.

### 16.1 The logging Module Basics

```python
import logging

# Get a logger for this module — use __name__ so logs show where they came from
logger = logging.getLogger(__name__)

# Log at different severity levels
logger.debug("Calculated damage: %s", 42)     # Detailed debug info (not shown by default)
logger.info("Player %s logged in", "Arthur")   # Normal operations
logger.warning("Gold below threshold: %d", 5)  # Something unusual, not an error
logger.error("Failed to load save file: %s", "slot_1.txt")  # An error occurred
logger.critical("Database connection lost")    # The application cannot continue
```

Log levels in order of severity: `DEBUG < INFO < WARNING < ERROR < CRITICAL`.

### 16.2 Configuring Logging Properly

Configuration belongs at the application entry point — not inside library modules. Library code only creates loggers; the entry point decides where logs go and at what level.

```python
# main.py — application entry point
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the entire application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),     # Print to terminal
            logging.FileHandler("game_api.log"),   # Also write to file
        ]
    )

setup_logging("INFO")
```

### 16.3 Structured JSON Logging

Plain text logs are hard to search and filter programmatically. In production, you want **structured logs** — each log entry is a JSON object where fields like `level`, `message`, and `request_id` are separate keys, not buried in a string.

```bash
pip install python-json-logger
```

```python
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_json_logging() -> None:
    logger = logging.getLogger()
    handler = logging.StreamHandler()

    # Format every log record as JSON
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Output looks like:
# {"asctime": "2025-06-01T14:23:01", "levelname": "INFO", "name": "game.players",
#  "message": "Player logged in", "player_id": 1, "ip": "10.0.0.1"}
```

### 16.4 Adding Context to Log Records

The most useful logs include context — who was making the request, what they were doing, and what the outcome was.

```python
import logging

logger = logging.getLogger(__name__)

def process_purchase(player_id: int, item_id: int, cost: int) -> bool:
    """Process a player buying an item."""
    log_context = {"player_id": player_id, "item_id": item_id, "cost": cost}

    logger.info("Purchase started", extra=log_context)

    try:
        # ... do the purchase ...
        logger.info("Purchase complete", extra={**log_context, "status": "success"})
        return True

    except InsufficientGoldError as e:
        logger.warning(
            "Purchase failed: insufficient gold",
            extra={**log_context, "status": "failed", "reason": str(e)}
        )
        return False

    except Exception as e:
        logger.error(
            "Purchase failed: unexpected error",
            extra={**log_context, "status": "error"},
            exc_info=True   # Includes the full traceback in the log entry
        )
        raise
```

### 16.5 What to Log and What Not To

| Log | Don't log |
|---|---|
| Request received (method, path, status code) | Passwords, tokens, API keys |
| External call outcomes (DB query, API call) | Full request/response bodies (may contain PII) |
| Business events (purchase, level-up, signup) | Debug output left from development |
| Errors with full traceback (`exc_info=True`) | High-volume routine operations at INFO level |
| Slow operations with their duration | Anything that identifies a specific person unnecessarily |

---

**Practice:**
1. Set up logging for a small Python script using `basicConfig`. Run the script and confirm you see INFO and above, but not DEBUG messages.
2. Add a `FileHandler` so logs are written to both the terminal and a `game.log` file.
3. Write a function that logs an INFO entry at the start, a WARNING if a condition is met, and an ERROR with `exc_info=True` if an exception is caught.

---

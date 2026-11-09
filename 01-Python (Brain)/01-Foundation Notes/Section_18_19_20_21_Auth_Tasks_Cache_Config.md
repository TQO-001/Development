## Section 18: Authentication & Security

Authentication is how your API knows who's making a request. Authorization is how it decides what that person is allowed to do. This section covers password hashing, JWT tokens, and how to protect FastAPI routes.

```bash
pip install passlib[bcrypt] python-jose[cryptography]
```

### 18.1 Password Hashing

Never store passwords in plain text — not even in a test database. Always hash them. **bcrypt** is the standard: it's slow by design (to make brute-force attacks expensive) and includes a random salt automatically.

```python
from passlib.context import CryptContext

# Create a context that uses bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """Returns a hashed version of the password — safe to store."""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Returns True if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Usage
hashed = hash_password("excalibur123")
print(hashed)  # $2b$12$... (a bcrypt hash — different every time, even for the same input)

print(verify_password("excalibur123", hashed))  # True
print(verify_password("wrong_password", hashed)) # False
```

### 18.2 JWT Tokens

A **JWT** (JSON Web Token) is a signed, self-contained token your server issues after a successful login. The client sends it in every subsequent request, and your server verifies the signature to know who the client is — without hitting the database every time.

A JWT has three parts (separated by `.`): a header, a payload (the data), and a signature. The server keeps the signing secret — only it can create valid tokens.

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key-keep-this-safe"  # In production: load from env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    """Creates a signed JWT token that expires in 30 minutes."""
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodes and verifies a JWT. Raises JWTError if invalid or expired."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# Create a token for Arthur
token = create_access_token({"sub": "arthur", "player_id": 1, "role": "admin"})
print(token)  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Verify and read it
payload = decode_access_token(token)
print(payload["sub"])        # "arthur"
print(payload["player_id"])  # 1
```

### 18.3 Login Endpoint and Protected Routes in FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

# This tells FastAPI where clients send their token — used by Swagger UI automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Login: accept username + password, return a token
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In real code: look up user in DB, verify password
    if form_data.username != "arthur" or form_data.password != "excalibur123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": form_data.username, "player_id": 1})
    return {"access_token": token, "token_type": "bearer"}

# Dependency: extract and validate the token from the Authorization header
def get_current_player(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Protected route: requires a valid token
@app.get("/players/me")
def get_my_profile(current_player: dict = Depends(get_current_player)):
    return {"player_id": current_player["player_id"], "name": current_player["sub"]}

# Role-based access: only admins can access this
def require_admin(current_player: dict = Depends(get_current_player)) -> dict:
    if current_player.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_player

@app.delete("/players/{player_id}")
def delete_player(player_id: int, admin: dict = Depends(require_admin)):
    return {"message": f"Player {player_id} deleted by {admin['sub']}"}
```

---

**Practice:**
1. Build a `/auth/login` endpoint that accepts a username and password, verifies them (hardcode one valid user for now), and returns a JWT on success.
2. Create a `get_current_player` dependency that reads and validates the token from the `Authorization: Bearer` header. Add it to a `GET /me` route.
3. Add a role-based dependency `require_admin` and protect a `DELETE /players/{id}` route with it.

---

## Section 19: Background Tasks & Job Queues

Some work doesn't need to happen before you respond to the client. Sending a welcome email, generating a report, updating leaderboards — these can happen after the response is sent. Background tasks are how you do that.

### 19.1 FastAPI BackgroundTasks — Simple In-Process Tasks

FastAPI has built-in `BackgroundTasks` for lightweight work that runs after the response is returned. The client gets their response immediately; the task runs after.

```python
from fastapi import FastAPI, BackgroundTasks
import time
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

def send_level_up_notification(player_name: str, new_level: int):
    """Runs after the response is sent. Simulates sending a notification."""
    time.sleep(2)  # Simulate slow work
    logger.info("Notification sent to %s: reached level %d!", player_name, new_level)

@app.post("/players/{player_id}/level-up")
def level_up_player(player_id: int, background_tasks: BackgroundTasks):
    # Do the main work synchronously (update the database)
    # ... database update here ...
    new_level = 16  # Result from DB

    # Schedule the notification to run AFTER we return the response
    background_tasks.add_task(send_level_up_notification, "Arthur", new_level)

    # Client gets this response immediately — notification happens in the background
    return {"player_id": player_id, "new_level": new_level, "status": "levelled up"}
```

> [!NOTE]
> `BackgroundTasks` run in the same process as your web server. If the server restarts, any queued tasks are lost. For tasks that absolutely must complete — emails, payments, reports — use a proper job queue (Section 19.2).

### 19.2 asyncio Tasks — Concurrent Background Work

For async code, you can fire-and-forget a coroutine using `asyncio.create_task()`.

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

async def update_guild_leaderboard(guild_id: int):
    """Expensive recalculation — run in the background."""
    await asyncio.sleep(5)  # Simulate heavy computation
    logger.info("Leaderboard updated for guild %d", guild_id)

async def process_purchase(player_id: int, item_id: int):
    # Do the main work
    logger.info("Purchase complete for player %d, item %d", player_id, item_id)

    # Fire off the leaderboard update without waiting for it
    task = asyncio.create_task(update_guild_leaderboard(guild_id=5))

    # Store the reference — if you don't, and the task raises an exception,
    # the error is silently discarded
    task.add_done_callback(lambda t: t.exception() and logger.error("Leaderboard task failed"))

    return {"status": "purchase complete"}
```

### 19.3 Job Queues — When Tasks Must Survive Restarts

For reliable background work that must complete even if the server restarts, you need a **job queue** — a separate process that picks up tasks and runs them independently.

**Redis Queue (RQ)** is the simplest option:

```bash
pip install rq redis
```

```python
# tasks.py — the work that runs in the background worker
import time
import logging

logger = logging.getLogger(__name__)

def send_quest_completion_email(player_email: str, quest_title: str):
    """This runs in a separate worker process — not in the web server."""
    time.sleep(1)  # Simulate email sending
    logger.info("Email sent to %s for completing '%s'", player_email, quest_title)
    return {"status": "sent"}
```

```python
# In your FastAPI app: enqueue the task
from redis import Redis
from rq import Queue
from tasks import send_quest_completion_email

redis_conn = Redis()
q = Queue(connection=redis_conn)

@app.post("/quests/{quest_id}/complete")
def complete_quest(quest_id: int):
    # Mark quest complete in DB...

    # Enqueue the email — it runs in a separate worker process
    job = q.enqueue(
        send_quest_completion_email,
        "arthur@camelot.co.za",
        "Slay the Dragon"
    )
    return {"quest_id": quest_id, "status": "complete", "notification_job": job.id}
```

```bash
# Start a worker (separate terminal)
rq worker
```

---

**Practice:**
1. Add a `BackgroundTasks` parameter to a FastAPI endpoint and use it to log a message 3 seconds after the response is returned.
2. Write a standalone async function and call `asyncio.create_task()` to run it in the background within an async route. Verify the route returns before the task finishes.

---

## Section 20: Caching Strategies

Caching stores the result of an expensive operation and returns the stored result on subsequent calls, instead of doing the work again. Done correctly, it's one of the biggest performance wins available.

### 20.1 In-Memory Caching with `functools.lru_cache`

For pure functions — functions whose output depends only on their inputs — Python's built-in `lru_cache` is the easiest caching option. It stores up to `maxsize` results and evicts the least recently used when full.

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)  # Cache up to 128 different results
def get_spell_damage_formula(spell_class: str, spell_tier: int) -> int:
    """Expensive calculation — imagine this hitting a config DB."""
    time.sleep(0.5)  # Simulates a slow lookup
    return spell_tier * (100 if spell_class == "fire" else 75)

# First call: slow (0.5 seconds)
result = get_spell_damage_formula("fire", 3)

# Second call with same args: instant (from cache)
result = get_spell_damage_formula("fire", 3)

# See cache stats
print(get_spell_damage_formula.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)

# Clear the cache (e.g., when underlying data changes)
get_spell_damage_formula.cache_clear()
```

`lru_cache` only works for hashable arguments. For async functions, use `asyncio`'s `@lru_cache` equivalent or a library like `aiocache`.

### 20.2 Redis Caching

For caches that need to survive a server restart, be shared across multiple processes, or have TTL (time-to-live) expiry, **Redis** is the standard tool.

```bash
pip install redis
```

```python
import redis
import json
from typing import Optional

cache = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_player_cache_key(player_id: int) -> str:
    return f"player:{player_id}"

def get_player(player_id: int) -> Optional[dict]:
    """Get player from cache first, fall back to database."""
    key = get_player_cache_key(player_id)

    # Check cache
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

    # Cache miss — fetch from database
    player = fetch_player_from_db(player_id)  # Your DB function
    if player:
        # Store in cache for 5 minutes (300 seconds)
        cache.setex(key, 300, json.dumps(player))

    return player

def invalidate_player_cache(player_id: int) -> None:
    """Call this whenever a player's data is updated."""
    cache.delete(get_player_cache_key(player_id))
```

### 20.3 Cache Invalidation Patterns

The hardest part of caching is knowing when to clear it. Stale cache data is often worse than no cache at all.

```python
# Pattern: invalidate on write
def update_player_gold(player_id: int, new_gold: int) -> None:
    """Update the database AND clear the cache."""
    # Update DB
    with get_db() as cursor:
        cursor.execute("UPDATE players SET gold = %s WHERE id = %s", (new_gold, player_id))

    # Invalidate cache so the next read goes to the DB
    invalidate_player_cache(player_id)

# Pattern: TTL-based expiry — just let it expire naturally
# Good for data that changes infrequently and where slight staleness is acceptable
# (e.g., leaderboards, statistics, config values)

# Pattern: cache versioning — change the cache key to effectively invalidate everything
VERSION = "v2"
def get_versioned_key(player_id: int) -> str:
    return f"{VERSION}:player:{player_id}"
```

---

**Practice:**
1. Add `@lru_cache` to a function that takes a `spell_type` string and returns a damage multiplier. Call it multiple times and check `cache_info()` to confirm hits are being served from cache.
2. Set up a Redis connection and write a `cache_get` and `cache_set` helper. Use them to cache a player lookup with a 60-second TTL.
3. Write a `update_player` function that updates the database AND invalidates the relevant cache key.

---

## Section 21: Configuration & Environment Management

Hard-coded config values are one of the most common sources of production bugs. A database URL in your source code gets committed to git, shared with the whole team, and ends up in environments it was never meant for. The right pattern: every environment-specific value lives in an environment variable or a secret manager, never in code.

### 21.1 os.environ — The Basics

```python
import os

# Read an environment variable
db_url = os.environ.get("DATABASE_URL")
debug = os.environ.get("DEBUG", "false").lower() == "true"  # Default if not set

# Fail loudly if a required variable is missing
db_url = os.environ["DATABASE_URL"]  # Raises KeyError if not set — fast failure is good
```

### 21.2 python-dotenv — Loading .env Files

```bash
pip install python-dotenv
```

```python
# Load .env file variables into the environment at startup
from dotenv import load_dotenv
import os

load_dotenv()  # Reads .env from the current directory

DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY   = os.environ["SECRET_KEY"]
DEBUG        = os.environ.get("DEBUG", "false").lower() == "true"
```

```ini
# .env (never commit this to git — add it to .gitignore)
DATABASE_URL=postgresql://admin:secret@localhost/game_db
SECRET_KEY=dev-secret-key-change-in-prod
DEBUG=true
```

### 21.3 Multi-Environment Config Pattern

```python
# config.py — one config object, multiple environments
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    env:           str = Field(default="development")
    database_url:  str
    secret_key:    str
    debug:         bool = False
    log_level:     str = "INFO"
    max_connections: int = 10

    class Config:
        env_file = f".env.{os.environ.get('APP_ENV', 'development')}"
        # Loads .env.development, .env.staging, or .env.production
        # depending on the APP_ENV environment variable

settings = Settings()
```

```ini
# .env.development
DATABASE_URL=postgresql://dev_user:dev_pass@localhost/game_db_dev
SECRET_KEY=dev-insecure-key
DEBUG=true
LOG_LEVEL=DEBUG

# .env.production
DATABASE_URL=postgresql://prod_user:STRONG_PASS@prod-db.internal/game_db
SECRET_KEY=${SECRET_KEY}     # Loaded from the actual OS environment in production
DEBUG=false
LOG_LEVEL=WARNING
```

### 21.4 Never Hardcode Secrets — A Checklist

```python
# ❌ NEVER DO ANY OF THESE
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"
SECRET_KEY = "abc123"
API_KEY = "sk-live-xxxxxxxx"

# ✅ ALWAYS DO THIS
import os
DATABASE_URL = os.environ["DATABASE_URL"]    # Crash fast if not set — intentional
SECRET_KEY   = os.environ["SECRET_KEY"]
API_KEY      = os.environ["THIRD_PARTY_API_KEY"]
```

Your `.gitignore` should always contain:

```
.env
.env.*
!.env.example    # Keep a template with placeholder values — commit this
```

---

**Practice:**
1. Create a `.env` file with `DATABASE_URL`, `SECRET_KEY`, and `DEBUG`. Write a `config.py` using `pydantic-settings` that loads them.
2. Add a `.env.example` file to your project with placeholder values (no real secrets). This is what you commit to git so others can set up their own config.
3. Make the app crash immediately on startup if `DATABASE_URL` is not set, with a clear error message.

---

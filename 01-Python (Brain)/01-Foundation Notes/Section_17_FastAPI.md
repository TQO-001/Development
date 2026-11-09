## Section 17: Building APIs with FastAPI

FastAPI is the modern standard for building Python web APIs. It's fast (built on Starlette and async), it uses your Pydantic models (Section 15) for automatic request validation and response serialization, and it generates interactive documentation automatically. Most importantly, it reads like clean Python — not framework boilerplate.

```bash
pip install fastapi uvicorn[standard]
```

### 17.1 Your First FastAPI App

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="Game API",
    description="REST API for the Camelot game server",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Game API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

```bash
# Run the server (auto-reloads on code changes)
uvicorn main:app --reload

# Visit these in your browser:
# http://localhost:8000/         — your API
# http://localhost:8000/docs     — interactive Swagger UI (free, auto-generated)
# http://localhost:8000/redoc    — alternative docs UI
```

### 17.2 Path Parameters and Query Parameters

```python
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

# Fake data for examples
players_db = {
    1: {"id": 1, "name": "Arthur",   "level": 15, "gold": 2500},
    2: {"id": 2, "name": "Merlin",   "level": 22, "gold": 800},
    3: {"id": 3, "name": "Lancelot", "level": 18, "gold": 1200},
}

# Path parameter: {player_id} in the URL path
@app.get("/players/{player_id}")
def get_player(player_id: int):                   # FastAPI validates it's an int
    player = players_db.get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found.")
    return player

# Query parameters: everything after the ? in the URL
# GET /players?min_level=10&role=Warrior&limit=5
@app.get("/players")
def list_players(
    min_level: int = 1,
    role: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    results = list(players_db.values())
    results = [p for p in results if p["level"] >= min_level]
    if role:
        results = [p for p in results if p.get("role") == role]
    return results[offset : offset + limit]
```

### 17.3 Request Bodies with Pydantic

For `POST`, `PUT`, and `PATCH` endpoints, the request body is defined as a Pydantic model.

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class PlayerCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    role: Optional[str] = None

class PlayerResponse(BaseModel):
    id: int
    name: str
    level: int
    gold: int
    role: Optional[str]

# POST /players — create a new player
@app.post("/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(player_data: PlayerCreate):
    # In real code, this would write to the database
    new_player = {
        "id": 99,
        "name": player_data.name,
        "level": 1,
        "gold": 0,
        "role": player_data.role
    }
    return new_player  # FastAPI validates this against PlayerResponse automatically

# PUT /players/{player_id} — full update
class PlayerUpdate(BaseModel):
    name: str
    role: Optional[str] = None

@app.put("/players/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, update: PlayerUpdate):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found.")
    players_db[player_id].update(update.model_dump(exclude_unset=True))
    return players_db[player_id]

# DELETE /players/{player_id}
@app.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found.")
    del players_db[player_id]
```

### 17.4 Dependency Injection

FastAPI's dependency injection system lets you share logic across multiple routes cleanly — database connections, authentication checks, pagination parameters, and more.

```python
from fastapi import FastAPI, Depends
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()
DATABASE_URL = "postgresql://admin:secret@localhost/game_db"

# A dependency that provides a database cursor and cleans up after the request
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cursor          # The route gets the cursor
        conn.commit()         # Commit on success
    except Exception:
        conn.rollback()       # Rollback on error
        raise
    finally:
        cursor.close()
        conn.close()          # Always close

# Any route can declare the dependency with Depends()
@app.get("/players/{player_id}")
def get_player(player_id: int, db=Depends(get_db)):
    db.execute("SELECT * FROM players WHERE id = %s;", (player_id,))
    player = db.fetchone()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")
    return player

@app.get("/guilds")
def list_guilds(db=Depends(get_db)):
    db.execute("SELECT * FROM guilds ORDER BY guild_name;")
    return db.fetchall()
```

### 17.5 Router — Splitting a Large App Into Files

```python
# routers/players.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/players", tags=["Players"])

@router.get("/")
def list_players():
    return []

@router.get("/{player_id}")
def get_player(player_id: int):
    raise HTTPException(status_code=404, detail="Not found.")
```

```python
# routers/quests.py
from fastapi import APIRouter

router = APIRouter(prefix="/quests", tags=["Quests"])

@router.get("/")
def list_quests():
    return []
```

```python
# main.py
from fastapi import FastAPI
from routers import players, quests

app = FastAPI()

app.include_router(players.router)
app.include_router(quests.router)
```

### 17.6 Global Error Handling

Instead of writing the same try/except in every route, register exception handlers at the app level.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class InsufficientGoldError(Exception):
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available

@app.exception_handler(InsufficientGoldError)
async def insufficient_gold_handler(request: Request, exc: InsufficientGoldError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "INSUFFICIENT_GOLD",
            "message": f"Need {exc.required} gold, have {exc.available}.",
        }
    )

# Catch-all for unexpected errors — log them and return a safe response
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s", request.method, request.url, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "message": "Something went wrong."}
    )
```

---

**Practice:**
1. Build a FastAPI app with a `GET /quests` endpoint (returns a list) and a `GET /quests/{quest_id}` endpoint (returns one quest or 404).
2. Add a `POST /quests` endpoint that accepts a `QuestCreate` Pydantic model with `title`, `difficulty`, and `reward_gold`, and returns a `QuestResponse` model with an additional `id` and `status` field.
3. Create a reusable dependency `get_pagination(limit: int = 20, offset: int = 0)` that can be injected into any list endpoint with `Depends()`.

---

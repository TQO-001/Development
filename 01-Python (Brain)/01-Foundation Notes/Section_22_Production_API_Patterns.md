## Section 22: Production API Patterns

This section covers the patterns that separate a working API from a production-grade one. These aren't optional nice-to-haves — they're the features every consumer of your API will eventually need, and retrofitting them later is far more painful than building them in from the start.

### 22.1 Consistent Error Response Format

Every error your API returns should look the same. When error formats are inconsistent, client developers have to write different error-handling code for every endpoint.

Define one error shape and use it everywhere:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
import uuid

app = FastAPI()

# Every error response follows this exact shape
class ErrorResponse(BaseModel):
    error_code: str          # Machine-readable: "PLAYER_NOT_FOUND", "INVALID_INPUT"
    message: str             # Human-readable description
    request_id: str          # Unique ID for this request — helps with log correlation
    details: Optional[Any] = None  # Extra info (validation errors, etc.)

# Custom exception class for predictable errors
class AppError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400, details=None):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details

# Register a handler that converts AppError to the standard format
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            request_id=str(uuid.uuid4()),
            details=exc.details
        ).model_dump()
    )

# Usage in a route
@app.get("/players/{player_id}")
def get_player(player_id: int):
    player = None  # Imagine a DB lookup here
    if not player:
        raise AppError(
            error_code="PLAYER_NOT_FOUND",
            message=f"No player exists with id {player_id}.",
            status_code=404
        )
    return player
```

All errors now look like:

```json
{
    "error_code": "PLAYER_NOT_FOUND",
    "message": "No player exists with id 99.",
    "request_id": "a7f3b2c1-...",
    "details": null
}
```

### 22.2 Standardised List Responses with Pagination

Every list endpoint should return total count alongside the results, so clients can build pagination UI without making a second request.

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int           # Total matching records (ignoring limit/offset)
    limit: int
    offset: int
    items: List[T]

# Reusable pagination dependency
from fastapi import Depends

class Pagination:
    def __init__(self, limit: int = 20, offset: int = 0):
        self.limit = min(limit, 100)  # Cap at 100 to prevent huge responses
        self.offset = offset

@app.get("/players", response_model=PaginatedResponse)
def list_players(page: Pagination = Depends()):
    # In real code: query DB with LIMIT and OFFSET, and a separate COUNT(*) query
    total = 350  # Total players in DB
    items = []   # Slice of players for this page

    return PaginatedResponse(
        total=total,
        limit=page.limit,
        offset=page.offset,
        items=items
    )
```

### 22.3 API Versioning

APIs change over time. Versioning lets you evolve your API without breaking existing clients.

The most common approach: URL prefix versioning (`/v1/`, `/v2/`).

```python
from fastapi import FastAPI
from fastapi import APIRouter

app = FastAPI()

# v1 router
v1 = APIRouter(prefix="/v1")

@v1.get("/players")
def list_players_v1():
    return {"version": "v1", "players": []}

# v2 router (adds new features, keeps v1 working)
v2 = APIRouter(prefix="/v2")

@v2.get("/players")
def list_players_v2():
    return {"version": "v2", "players": [], "total": 0}  # v2 adds pagination

app.include_router(v1)
app.include_router(v2)
```

When you release a breaking change:
1. Create a `/v2/` version
2. Keep `/v1/` running (frozen — no new features)
3. Communicate a deprecation timeline
4. Remove `/v1/` only after clients have migrated

### 22.4 CORS — Cross-Origin Resource Sharing

If your frontend (running on `localhost:3000` or a different domain) calls your API, the browser blocks the request by default unless your API explicitly allows it. CORS headers are the permission system for this.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",         # Local frontend dev server
        "https://game.laughtale.co.za",  # Production frontend
    ],
    allow_credentials=True,   # Allow cookies/auth headers
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)
```

> [!NOTE]
> Never use `allow_origins=["*"]` (wildcard) in production for APIs that use cookies or authentication headers. The wildcard disables the security model entirely. List your actual domains explicitly.

### 22.5 Health Check Endpoint

Health check endpoints let your infrastructure (load balancers, container orchestrators, uptime monitors) confirm the service is alive and functioning.

```python
import psycopg2
from datetime import datetime

@app.get("/health")
def health_check():
    """Basic health check — is the service running?"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/ready")
def readiness_check():
    """Readiness check — can the service handle requests? (DB connected?)"""
    try:
        conn = psycopg2.connect(settings.database_url)
        conn.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    overall = "ok" if db_status == "ok" else "degraded"
    status_code = 200 if overall == "ok" else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={"status": overall, "database": db_status}
    )
```

### 22.6 Request ID Middleware

Every request should get a unique ID. This makes it possible to trace a single request through your logs, even when many requests are happening concurrently.

```python
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import Response
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Assigns a unique ID to every request and adds it to the response headers."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    logger.info(
        "Request started",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path}
    )

    response: Response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request complete",
        extra={"request_id": request_id, "status_code": response.status_code}
    )

    return response
```

### 22.7 Rate Limiting Concept

Rate limiting prevents any one client from overwhelming your API. In production this is usually handled by your reverse proxy (Nginx, Caddy) or API gateway. In Python, `slowapi` adds it directly to FastAPI:

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/players")
@limiter.limit("60/minute")  # Max 60 requests per minute per IP
async def list_players(request: Request):
    return []
```

---

**Practice:**
1. Add the `ErrorResponse` model and `AppError` exception handler to a FastAPI app. Test it by raising `AppError` from a route and confirming the response matches the standard format.
2. Add a `PaginatedResponse` wrapper to a list endpoint and implement the `Pagination` dependency. Return fake total/items data to confirm the shape is correct.
3. Add a `/health` and `/health/ready` endpoint. The readiness endpoint should attempt a DB connection and return `503` if it fails.

---

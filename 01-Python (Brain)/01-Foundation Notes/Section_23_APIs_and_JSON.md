## Section 23: Working with APIs & JSON

Most real applications don't live in isolation. They talk to other services — fetching player data from a remote game server, sending webhook events, pulling quest updates from a third-party API. The `requests` library is how Python talks to the outside world over HTTP. JSON is the universal language those services speak.

```bash
pip install requests
```

### 23.1 Making a GET Request

`GET` requests fetch data. They're read-only — nothing on the server changes.

```python
import requests

# Basic GET request
response = requests.get("https://api.github.com/users/TQO-001")

# The response object carries everything back
print(response.status_code)   # 200 = success, 404 = not found, 500 = server error
print(response.headers)       # Response headers (Content-Type, etc.)
print(response.text)          # Raw response body as a string
print(response.json())        # Parse the body as JSON → returns a Python dict
```

### 23.2 Query Parameters

Query parameters are the values after the `?` in a URL. Instead of building them into the string yourself, pass a dictionary and let `requests` handle the encoding.

```python
# Without requests help — messy and error-prone
url = "https://api.example.com/quests?status=open&min_reward=500&page=1"

# With requests — clean and safe
params = {
    "status": "open",
    "min_reward": 500,
    "page": 1
}
response = requests.get("https://api.example.com/quests", params=params)

# requests builds the URL for you:
# https://api.example.com/quests?status=open&min_reward=500&page=1
print(response.url)
```

### 23.3 Headers — Authentication and Content Type

Headers carry metadata with a request. The most common use is authentication — sending an API key or token to prove who you are.

```python
# Bearer token authentication (JWT — you'll use this with your own FastAPI endpoints)
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs...",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
response = requests.get("https://api.example.com/players/me", headers=headers)

# API key authentication (common in third-party APIs)
headers = {"X-API-Key": "your-api-key-here"}
response = requests.get("https://api.example.com/data", headers=headers)
```

### 23.4 POST, PUT, and DELETE Requests

`POST` creates something. `PUT` replaces something. `DELETE` removes something. For any request that sends data, pass it as `json=` and `requests` will serialise it and set the `Content-Type` header automatically.

```python
# POST — create a new quest
quest_data = {
    "title": "Retrieve the Holy Grail",
    "difficulty": 9,
    "reward_gold": 5000
}
response = requests.post("https://api.example.com/quests", json=quest_data)
created_quest = response.json()
print(created_quest["id"])   # The new quest's ID from the server

# PUT — update an entire resource
updated_data = {"title": "The Grail Quest", "difficulty": 10, "reward_gold": 7500}
response = requests.put(f"https://api.example.com/quests/{created_quest['id']}", json=updated_data)

# PATCH — update only specific fields (partial update)
response = requests.patch(
    f"https://api.example.com/quests/{created_quest['id']}",
    json={"reward_gold": 6000}   # Only update gold, leave everything else as-is
)

# DELETE
response = requests.delete(f"https://api.example.com/quests/{created_quest['id']}")
print(response.status_code)   # 204 = deleted successfully (no content)
```

### 23.5 Error Handling

A request can fail at the network level (timeout, no connection) or the HTTP level (404, 500). Handle both separately.

```python
import requests

def fetch_player(player_id: int) -> dict | None:
    """Fetches a player from the game API. Returns None if not found."""
    try:
        response = requests.get(
            f"https://api.example.com/players/{player_id}",
            timeout=5   # Always set a timeout — default is to wait forever
        )
        response.raise_for_status()  # Raises HTTPError for 4xx and 5xx responses
        return response.json()

    except requests.exceptions.Timeout:
        print("Request timed out — the server took too long to respond.")
        return None

    except requests.exceptions.ConnectionError:
        print("Could not connect — check the URL or your network connection.")
        return None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Player {player_id} was not found.")
        else:
            print(f"Server returned an error: {e.response.status_code}")
        return None

    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests error
        print(f"Unexpected error: {e}")
        return None
```

### 23.6 Sessions — Reusing Connections and Headers

A `Session` object persists headers, cookies, and TCP connections across multiple requests. If you're making several requests to the same API, a Session is more efficient and lets you set shared headers once.

```python
with requests.Session() as session:
    # Set auth headers once — applies to every request through this session
    session.headers.update({
        "Authorization": "Bearer my-token",
        "Accept": "application/json"
    })

    # All of these reuse the same connection and carry the same headers
    players = session.get("https://api.example.com/players").json()
    quests  = session.get("https://api.example.com/quests").json()
    guilds  = session.get("https://api.example.com/guilds").json()
```

---

### 23.7 The json Module

The `json` module converts between Python objects and JSON strings. You don't need `requests` for this — it's used anywhere JSON appears (files, databases, message queues).

```python
import json

# Parse a JSON string into a Python dict/list
json_string = '{"name": "Arthur", "level": 15, "skills": ["Slash", "Block"]}'
data = json.loads(json_string)   # 'loads' = load from string
print(data["name"])              # "Arthur"
print(data["skills"][0])         # "Slash"

# Convert a Python dict/list into a JSON string
player = {
    "name": "Merlin",
    "level": 22,
    "skills": ["Fireball", "Teleport"]
}
json_string = json.dumps(player)           # Compact: '{"name": "Merlin", ...}'
pretty_json = json.dumps(player, indent=2) # Human-readable, with indentation

print(pretty_json)
# {
#   "name": "Merlin",
#   "level": 22,
#   "skills": [
#     "Fireball",
#     "Teleport"
#   ]
# }
```

### 23.8 Reading and Writing JSON Files

```python
import json
from pathlib import Path

# Read JSON from a file
save_file = Path("game_save.json")
with open(save_file, "r", encoding="utf-8") as f:
    save_data = json.load(f)    # 'load' = load from file object

print(save_data["player_name"])

# Write JSON to a file
save_data = {
    "player_name": "Arthur",
    "level": 15,
    "gold": 2500,
    "inventory": ["Excalibur", "Shield of Valor", "Health Potion"]
}
with open("game_save.json", "w", encoding="utf-8") as f:
    json.dump(save_data, f, indent=2)    # 'dump' = dump to file object

# Common pitfall: not all Python objects are JSON serialisable
from datetime import datetime
data = {"name": "Arthur", "last_played": datetime.now()}

# This raises TypeError: Object of type datetime is not JSON serializable
# json.dumps(data)

# Fix: convert non-serialisable types manually or use a custom encoder
data = {"name": "Arthur", "last_played": datetime.now().isoformat()}  # Convert to string
json.dumps(data)  # Works fine
```

> [!NOTE]
> JSON supports six types: string, number, boolean, null, array, and object. Python's `datetime`, `set`, `tuple`, and custom class instances are not JSON-serialisable out of the box. Convert them to strings or lists first, or use Pydantic's `.model_dump_json()` (Section 15) which handles this automatically.

---

**Practice:**
1. Use `requests.get()` to fetch your own GitHub profile (`https://api.github.com/users/<your-username>`). Print your public repo count and follower count from the response.
2. Write a function `post_quest(title, difficulty, reward)` that sends a `POST` request with those values as JSON. Print the status code and the response body.
3. Write a function `save_to_json(data, filepath)` and `load_from_json(filepath)` using the `json` module. Test them by saving and reloading a player dictionary with a `datetime` field (convert it to a string first).

---

## DSA Section 04: Hash Tables — Hash Functions, Sets & Maps

A hash table is the single most powerful lookup structure in DSA. It delivers `O(1)` average-case access, insertion, and deletion regardless of how many items it holds — by completely avoiding the need to search through anything.

### 4.1 How Hash Tables Work

A hash table is backed by an array of "buckets". When you store a key-value pair, a **hash function** converts the key into an integer index, and the value is stored in that bucket.

```
hash("Arthur") → 42   → store at bucket[42]
hash("Merlin") → 17   → store at bucket[17]
hash("Lancelot") → 42 → COLLISION! bucket[42] already has Arthur
```

Lookup is equally direct: `hash("Arthur")` → `42` → go straight to bucket 42. No searching.

**Collisions** happen when two keys hash to the same bucket. The most common solution is **chaining** — each bucket holds a small list of all keys that map to it. As long as collisions are rare (achieved by a good hash function and a sensibly sized table), lookups stay close to `O(1)`.

When a hash table gets too full (high **load factor**), it doubles in size and rehashes everything — exactly like a dynamic array. This is why all operations are `O(1)` amortised, not always.

### 4.2 Python's dict — The Hash Map

```python
# dict is a hash table mapping keys to values
player = {
    "name":  "Arthur",
    "level": 15,
    "guild": "Knights of Camelot"
}

# O(1) average — all of these
player["level"]              # Access — direct hash lookup
player["gold"] = 2500        # Insert new key
player["level"] = 16         # Update existing key
del player["guild"]          # Delete
"name" in player             # Membership check — O(1)! (not O(n) like a list)
player.get("mana", 0)        # Safe access with default — no KeyError
```

**Common interview patterns with dict:**

```python
# Pattern 1: Frequency counting
kills = ["Goblin", "Orc", "Goblin", "Dragon", "Goblin", "Orc"]

freq = {}
for enemy in kills:
    freq[enemy] = freq.get(enemy, 0) + 1
# {'Goblin': 3, 'Orc': 2, 'Dragon': 1}

# Shorter with Counter
from collections import Counter
freq = Counter(kills)

# Pattern 2: "Have I seen this before?" — the most common hash map use
def two_sum(numbers: list[int], target: int) -> tuple[int, int]:
    """Find two indices that sum to target — O(n) with a hash map."""
    seen = {}  # value → index
    for i, num in enumerate(numbers):
        complement = target - num
        if complement in seen:        # O(1) lookup
            return seen[complement], i
        seen[num] = i
    return -1, -1

# Pattern 3: Grouping items by a property
players = [
    {"name": "Arthur",   "role": "Warrior"},
    {"name": "Merlin",   "role": "Mage"},
    {"name": "Lancelot", "role": "Warrior"},
]

by_role = {}
for p in players:
    role = p["role"]
    by_role.setdefault(role, []).append(p["name"])
# {"Warrior": ["Arthur", "Lancelot"], "Mage": ["Merlin"]}

# Or with defaultdict
from collections import defaultdict
by_role = defaultdict(list)
for p in players:
    by_role[p["role"]].append(p["name"])
```

### 4.3 Python's set — The Hash Set

A `set` is a hash table that stores only keys — no values. It's optimised purely for membership testing and deduplication, at `O(1)` average.

```python
# Deduplicate a list — O(n)
names = ["Arthur", "Merlin", "Arthur", "Lancelot", "Merlin"]
unique = set(names)   # {"Arthur", "Merlin", "Lancelot"} — order not guaranteed

# Membership check — O(1) for set, O(n) for list
visited_rooms = {"dungeon_1", "dungeon_3"}
if "dungeon_2" not in visited_rooms:   # O(1)
    explore("dungeon_2")
    visited_rooms.add("dungeon_2")

# Set operations — extremely useful in interviews
party_a = {"Arthur", "Merlin", "Lancelot"}
party_b = {"Merlin", "Gawain", "Percival"}

both_parties = party_a & party_b   # Intersection: {"Merlin"}
either_party = party_a | party_b   # Union: all unique members
only_in_a    = party_a - party_b   # Difference: {"Arthur", "Lancelot"}
```

**dict vs set — when to use which:**

| I need to... | Use |
|---|---|
| Check if an item exists | `set` |
| Count occurrences | `dict` (or `Counter`) |
| Associate data with a key | `dict` |
| Deduplicate a collection | `set` |
| Track "visited" nodes | `set` |
| Map inputs to outputs (memoisation) | `dict` |

### 4.4 Hash Table Complexity

| Operation | Average Case | Worst Case |
|---|---|---|
| Access / Lookup | **O(1)** | O(n) (all keys collide) |
| Insert | **O(1)** amortised | O(n) (resize) |
| Delete | **O(1)** | O(n) |
| `x in dict/set` | **O(1)** | O(n) |

The worst case is theoretical — a properly implemented hash function with a reasonable load factor makes it effectively `O(1)` in practice.

---

**Practice:**
1. Write a function `count_enemy_kills(kills: list[str]) -> dict` that counts how many times each enemy type appears. Use a `dict`, not `Counter`.
2. Write a function `find_duplicate(players: list[str]) -> str` that returns the first player name that appears more than once. Use a `set` for O(n) total time.
3. Write `two_sum(numbers, target)` — return the two indices that add up to target. Solve it in O(n) using a dict.

---

## DSA Section 05: Stacks & Queues

Stacks and queues are restricted arrays — they only allow access through specific ends. This restriction is exactly what makes them powerful: the access pattern (LIFO or FIFO) is an intentional constraint that matches certain problem shapes perfectly.

### 5.1 Stacks — Last In, First Out (LIFO)

A stack works like a pile of plates. You can only add or remove from the top. The last thing you put in is the first thing you get back out.

```
Push: [Arthur] → [Arthur][Merlin] → [Arthur][Merlin][Lancelot]
Pop:  [Arthur][Merlin][Lancelot] → [Arthur][Merlin] (Lancelot popped)
```

```python
# Python's list as a stack — both operations are O(1)
stack = []
stack.append("Arthur")      # Push — O(1)
stack.append("Merlin")      # Push — O(1)
stack.append("Lancelot")    # Push — O(1)

print(stack[-1])             # Peek at top without removing — O(1)
last = stack.pop()           # Pop — O(1)   returns "Lancelot"
```

**Recognise a stack problem when you see:**
- "Undo the last action"
- "Match opening and closing brackets/parentheses"
- "Reverse a sequence"
- "Track the path back through a maze (DFS)"
- Any problem where you process things in reverse order

**Classic pattern: Matching brackets:**

```python
def is_valid_brackets(s: str) -> bool:
    """Returns True if all brackets are matched and properly nested."""
    stack = []
    matching = {")": "(", "]": "[", "}": "{"}

    for char in s:
        if char in "([{":
            stack.append(char)       # Push opening bracket
        elif char in ")]}":
            if not stack or stack[-1] != matching[char]:
                return False         # No matching opener
            stack.pop()              # Matched — pop the opener

    return len(stack) == 0           # Stack empty = all matched

is_valid_brackets("({[Arthur]})")   # True
is_valid_brackets("({Merlin}")      # False — { not closed
```

**Classic pattern: Largest rectangle in histogram (monotonic stack):**

```python
def daily_temperatures(temps: list[int]) -> list[int]:
    """For each day, how many days until a warmer temperature?"""
    result = [0] * len(temps)
    stack = []  # Stack of indices

    for i, temp in enumerate(temps):
        while stack and temps[stack[-1]] < temp:
            j = stack.pop()
            result[j] = i - j      # Days to wait for warmth
        stack.append(i)

    return result
# Input:  [73, 74, 75, 71, 69, 72, 76, 73]
# Output: [ 1,  1,  4,  2,  1,  1,  0,  0]
```

### 5.2 Queues — First In, First Out (FIFO)

A queue works like a line at a dungeon entrance. The first person to join the line is the first to enter. New players join at the back; the front player goes next.

```
Enqueue: [Arthur] → [Arthur][Merlin] → [Arthur][Merlin][Lancelot]
Dequeue: Arthur leaves: [Merlin][Lancelot]
```

```python
from collections import deque

# Always use collections.deque for queues — NOT a plain list
# list.pop(0) is O(n); deque.popleft() is O(1)

queue = deque()
queue.append("Arthur")         # Enqueue at back — O(1)
queue.append("Merlin")         # Enqueue at back — O(1)
queue.append("Lancelot")       # Enqueue at back — O(1)

front = queue[0]               # Peek at front without removing — O(1)
first = queue.popleft()        # Dequeue from front — O(1)  returns "Arthur"
```

**Recognise a queue problem when you see:**
- "Process items in the order they arrived"
- "Breadth-first search" (explore level by level)
- "Minimum steps / shortest path" (covered in Graphs section)
- "Rate limiting / buffering"

**Classic queue pattern — BFS with a queue:**

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    """Visit all nodes reachable from start, level by level."""
    visited = set()
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()       # Dequeue — O(1)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                queue.append(neighbour)   # Enqueue — O(1)

    return order
```

### 5.3 Stack vs Queue — Side by Side

| Property | Stack | Queue |
|---|---|---|
| Order | LIFO — last in, first out | FIFO — first in, first out |
| Add | `push` / `append` | `enqueue` / `append` |
| Remove | `pop` (from top) | `dequeue` / `popleft` (from front) |
| Python structure | `list` | `collections.deque` |
| Time for add/remove | O(1) | O(1) |
| Typical use | DFS, undo, brackets | BFS, scheduling, buffers |

### 5.4 The Monotonic Stack — A Power Pattern

A **monotonic stack** maintains elements in a strictly increasing or decreasing order. Useful for "next greater element", "span" problems, and histogram problems.

```python
def next_greater(players_power: list[int]) -> list[int]:
    """For each player, find the next player with greater power."""
    result = [-1] * len(players_power)   # Default: no greater element
    stack = []  # Stack of indices, maintained in decreasing order of power

    for i, power in enumerate(players_power):
        # Pop any player weaker than the current one — current is their "next greater"
        while stack and players_power[stack[-1]] < power:
            j = stack.pop()
            result[j] = power
        stack.append(i)

    return result

# Input:  [3, 1, 4, 1, 5, 9, 2, 6]
# Output: [4, 4, 5, 5, 9, -1, 6, -1]
```

---

**Practice:**
1. Implement a stack using a Python list with `push(val)`, `pop()`, `peek()`, and `is_empty()` methods.
2. Write `is_valid_brackets(s: str) -> bool` that returns `True` if all parentheses, brackets, and braces in the string are properly matched and nested.
3. Write a function `bfs_shortest_path(graph, start, end)` that finds the shortest path from `start` to `end` in an unweighted graph, using a queue. Return the path as a list of nodes.

---

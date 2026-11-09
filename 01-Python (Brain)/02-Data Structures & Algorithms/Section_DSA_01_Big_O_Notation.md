## DSA Section 01: Time & Space Complexity — Big O Notation

Before you can talk about data structures and algorithms, you need a shared language for comparing them. Big O notation is that language. It answers one question: **as the input gets larger, how does the work grow?** It's not about measuring seconds — it's about understanding the shape of how a solution scales.

### 1.1 What Big O Actually Means

Imagine your kingdom has `n` players on a roster. You need to find Arthur.

- If you search through every player one by one: **the work grows with n** — double the players, double the search time.
- If the roster is sorted and you split it in half repeatedly: **the work grows with log n** — double the players, only one extra step.
- If you check every player against every other player: **the work grows with n²** — double the players, four times the work.

Big O captures this shape. Constants and small terms are dropped because they don't matter at scale. `O(3n + 7)` simplifies to `O(n)` — the `3` and `7` are irrelevant when n is a million.

**Big O is worst-case unless stated otherwise.** It's a ceiling — the most work an algorithm will ever do on an input of size n.

### 1.2 The Common Complexities — Fastest to Slowest

| Notation | Name | Example |
|---|---|---|
| **O(1)** | Constant | Looking up a value by index or dictionary key |
| **O(log n)** | Logarithmic | Binary search, halving a problem each step |
| **O(n)** | Linear | One pass through a list |
| **O(n log n)** | Log-linear | Merge sort, heap sort |
| **O(n²)** | Quadratic | Nested loops over the same input |
| **O(2ⁿ)** | Exponential | Brute-force recursion (all subsets, Fibonacci without caching) |
| **O(n!)** | Factorial | Generating all permutations |

The order above is from best to worst. An `O(log n)` algorithm on 1,000,000 items does about 20 operations. An `O(n²)` algorithm does 1,000,000,000,000.

### 1.3 Reading Algorithms — Pattern Recognition

**Single loop → O(n):**

```python
# Check if any player has more than 1000 gold
players = ["Arthur", "Merlin", "Lancelot"]  # n players

for player in players:        # Runs n times
    if player.gold > 1000:
        return True
# O(n) — one pass through the list
```

**Nested loop over the same input → O(n²):**

```python
# Check if any two players share the same name (naive approach)
for i in range(len(players)):       # n iterations
    for j in range(len(players)):   # n iterations for EACH i
        if i != j and players[i].name == players[j].name:
            return True
# O(n²) — n × n = n² comparisons total
```

**Halving the problem each step → O(log n):**

```python
# Binary search in a sorted list
left, right = 0, len(players) - 1
while left <= right:
    mid = (left + right) // 2       # Each step cuts the search space in half
    if players[mid] == target:
        return mid
    elif players[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
# O(log n) — 1,000,000 players → ~20 steps
```

**Recursive branching with no memoisation → O(2ⁿ):**

```python
# Naive Fibonacci — every call branches into two more
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)   # Two recursive calls at each level
# O(2^n) — grows exponentially fast
```

**Two separate loops (not nested) → O(n + m):**

```python
# Process two separate lists
for player in players:      # O(n)
    process(player)

for quest in quests:        # O(m)
    log(quest)

# O(n + m) — usually simplified to O(n) if m ≈ n
```

### 1.4 Dropping Constants and Non-Dominant Terms

Big O keeps only the dominant term — the one that grows fastest:

```
O(2n)          → O(n)      (constants dropped)
O(n² + n)      → O(n²)     (n is dominated by n² for large n)
O(n + 500)     → O(n)      (constant 500 becomes irrelevant)
O(n log n + n) → O(n log n)(n is dominated)
O(n² + 2ⁿ)    → O(2ⁿ)     (n² is dominated by 2ⁿ)
```

### 1.5 Space Complexity

Big O also describes memory usage. Some algorithms trade extra space for speed.

```python
# O(1) space — only a few variables, no extra data structure
def find_max(players: list) -> int:
    max_gold = 0
    for p in players:
        if p.gold > max_gold:
            max_gold = p.gold
    return max_gold
# Space used: just max_gold — doesn't grow with input size

# O(n) space — creates a new structure proportional to input
def get_names(players: list) -> list:
    return [p.name for p in players]   # New list, same size as input

# O(n) space — recursion depth
def sum_recursive(n: int) -> int:
    if n == 0: return 0
    return n + sum_recursive(n - 1)
# Each recursive call adds a frame to the call stack — n frames total
```

**Common space complexities:**

| Space | Example |
|---|---|
| **O(1)** | A few variables, in-place swaps |
| **O(log n)** | Recursive binary search (call stack depth) |
| **O(n)** | A copy of the input, a hash map of all elements, recursion on n |
| **O(n²)** | A 2D grid/matrix of size n × n |

### 1.6 Recognising Complexity on Sight

```python
# O(1) — direct access
print(players[0])
print(player_map["Arthur"])

# O(log n) — look for: "while left <= right" with "mid = (left+right)//2"
# or "divide in half each step"

# O(n) — one loop over n elements
for p in players: ...

# O(n log n) — sorting, or a loop that calls a log-n operation
players.sort()            # Python's sort is O(n log n)
for p in players:
    bisect.insort(sorted_list, p)  # O(n log n) total

# O(n²) — two nested loops over the same collection
for i in range(n):
    for j in range(n): ...

# O(2^n) — recursive branching with two calls per level
def f(n): return f(n-1) + f(n-2)  # Each call spawns 2 more

# O(n!) — generating all orderings
from itertools import permutations
list(permutations(players))   # n! results
```

---

**Practice:**
1. What is the Big O time complexity of the following? Write your answer and explain why:
   - A single `for` loop over `n` items that does `O(1)` work per item.
   - A loop from `0` to `n` containing another loop from `0` to `n`.
   - A function that prints `players[0]` every time, regardless of n.
   - `fib(n)` implemented with two recursive calls and no cache.
2. Given `O(3n² + 5n + 100)`, what is the simplified Big O? Explain why you dropped each term.
3. A function reads a list of `n` players and creates a dictionary mapping each name to their level. What is its time complexity? Space complexity?

---

## DSA Section 02: Static Arrays, Dynamic Arrays & Strings

Arrays are the most fundamental data structure. Every other structure either wraps an array, replaces an array, or is built on top of the ideas an array introduces. Understanding how arrays actually work in memory — not just how to use them — is what lets you reason about why certain operations are fast and others are slow.

### 2.1 Static Arrays — The Foundation

A static array is a fixed-size, contiguous block of memory allocated once. "Contiguous" means the elements are stored back-to-back in memory with no gaps. Because of this layout, the address of any element can be calculated instantly:

```
address of element[i] = base_address + (i × element_size)
```

There's no searching — just arithmetic. This is why index access is `O(1)`.

```
Memory: [100] [101] [102] [103] [104] [105] [106]  ← memory addresses
Values: [Art] [Mer] [Lan] [ 0 ] [ 0 ] [ 0 ] [ 0 ]  ← 7 slots, 3 used

players[0] → address 100  (instant)
players[2] → address 102  (instant — no matter how large the array)
```

Static arrays are the mental model for in-place array manipulation problems. Languages like C expose them directly. Python, Java, and most modern languages wrap them in something more convenient.

**Static Array Operation Complexities:**

| Operation | Complexity | Why |
|---|---|---|
| Access by index `arr[i]` | **O(1)** | Direct address calculation |
| Search (unsorted) | **O(n)** | Must check every element |
| Insert at end (if space) | **O(1)** | Just write to the next slot |
| Insert at middle/front | **O(n)** | Must shift everything after the insertion point |
| Delete at middle/front | **O(n)** | Must shift everything after the deletion point |

### 2.2 Dynamic Arrays — Python's list

A dynamic array wraps a static array but grows automatically. Python's `list` is a dynamic array. When you `.append()` to a list that's already full, Python:

1. Allocates a **new, larger** static array (typically double the size)
2. Copies all existing elements to the new block
3. Adds the new element
4. Frees the old block

This "doubling" strategy means resize operations are rare. Most `.append()` calls are `O(1)`. The occasional resize is `O(n)` — but spread across all the appends that came before it, the average (amortised) cost per append is still `O(1)`.

```python
# Python list — dynamic array under the hood
players = []                      # Starts empty
players.append("Arthur")          # O(1) amortised — might trigger a resize
players.append("Merlin")          # O(1) amortised
players.append("Lancelot")        # O(1) amortised

# O(1) operations
first = players[0]                # Direct index access — O(1)
last  = players[-1]               # Same — O(1)
players[-1] = "Bedivere"          # Overwrite by index — O(1)
players.append("Percival")        # Append to end — O(1) amortised
players.pop()                     # Remove from end — O(1)

# O(n) operations — everything that shifts elements
players.insert(0, "Galahad")      # Insert at front — shifts ALL elements right → O(n)
players.insert(2, "Gawain")       # Insert at index 2 — shifts elements 2..end → O(n)
players.pop(0)                    # Remove from front — shifts ALL elements left → O(n)
players.remove("Merlin")          # Linear search + shift → O(n)

# O(n) operations — must scan the whole list
"Arthur" in players               # Membership check (unsorted list) → O(n)
players.index("Lancelot")         # Find index → O(n)

# Slicing — O(k) where k is the length of the slice
subset = players[1:4]             # Creates a new list with 3 elements → O(3) = O(k)
```

**Dynamic Array Operation Complexities:**

| Operation | Complexity |
|---|---|
| `arr[i]` (read/write by index) | O(1) |
| `arr.append(x)` | O(1) amortised |
| `arr.pop()` (from end) | O(1) |
| `arr.insert(i, x)` | O(n) |
| `arr.pop(i)` or `arr.remove(x)` | O(n) |
| `x in arr` (unsorted) | O(n) |
| `arr[i:j]` (slice of length k) | O(k) |
| `len(arr)` | O(1) — length is stored separately |

> [!NOTE]
> Inserting at the front of a Python list (`list.insert(0, x)`) is always `O(n)` — every element shifts right. If you frequently need fast insertion at both ends, use `collections.deque` instead, which gives `O(1)` at both ends.

### 2.3 Common Dynamic Array Patterns in Interviews

```python
# Pattern 1: Two-pass — one pass to collect, one to process
def get_above_average(levels: list[int]) -> list[int]:
    avg = sum(levels) / len(levels)          # O(n)
    return [l for l in levels if l > avg]    # O(n)
# Total: O(n) — two linear passes, not O(n²)

# Pattern 2: In-place modification with a write pointer
def remove_zeros(arr: list[int]) -> int:
    """Removes zeros in place. Returns the new length."""
    write = 0
    for read in range(len(arr)):
        if arr[read] != 0:
            arr[write] = arr[read]
            write += 1
    return write  # Elements 0..write-1 are the result
# O(n) time, O(1) space — classic in-place pattern

# Pattern 3: Prefix sums — precompute cumulative sums for O(1) range queries
levels = [5, 3, 8, 2, 9, 1]
prefix = [0] * (len(levels) + 1)
for i in range(len(levels)):
    prefix[i + 1] = prefix[i] + levels[i]

# Now: sum of levels[l..r] is prefix[r+1] - prefix[l]  ← O(1) per query
```

### 2.4 Strings — Immutability Is the Trap

Strings behave like arrays of characters — `s[0]`, `s[1:5]`, `len(s)` all work the same way. But Python strings are **immutable**: once created, they cannot be changed. Every string operation that looks like a modification actually creates a new string.

```python
quest_name = "Slay the Goblin"

# These all look like mutations but they all CREATE NEW STRINGS
upper = quest_name.upper()          # New string — original unchanged
replaced = quest_name.replace("Goblin", "Dragon")  # New string

# This is the performance trap — concatenation in a loop
# Each iteration creates a BRAND NEW string and copies everything
result = ""
for word in ["Retrieve", "the", "Holy", "Grail"]:
    result = result + " " + word    # 4 new string objects created → O(n²) total
```

**Why it's O(n²):** In the first iteration, you copy 1 word. In the second, you copy 2 words. In the third, 3. After n iterations you've copied `1 + 2 + 3 + ... + n = n(n+1)/2` characters — that's `O(n²)`.

**The fix: build a list, join at the end:**

```python
# O(n) — the join happens once, copies everything exactly once
parts = []
for word in ["Retrieve", "the", "Holy", "Grail"]:
    parts.append(word)   # O(1) per append
result = " ".join(parts) # One copy at the end → O(n) total
```

**String Operation Complexities:**

| Operation | Complexity | Note |
|---|---|---|
| `s[i]` (read by index) | O(1) | |
| `len(s)` | O(1) | Stored separately |
| `s[i:j]` (slice of length k) | O(k) | Creates a new string |
| `s + t` (concatenation) | O(n + m) | Creates a new string each time |
| `" ".join(parts)` | O(total chars) | One allocation — always prefer this |
| `s.find(sub)` | O(n·m) | n = len(s), m = len(sub) |
| `sub in s` | O(n·m) | Same as find |
| `s.split()` | O(n) | |
| `s.lower()` / `s.upper()` | O(n) | |

```python
# Common string interview patterns

# Frequency count — O(n) time, O(k) space where k is alphabet size
from collections import Counter
quest_title = "slay the goblin king"
freq = Counter(quest_title.replace(" ", ""))
# freq = {'l': 2, 'i': 2, 'g': 2, 's': 1, ...}

# Anagram check — same character frequencies
def is_anagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)    # O(n)

# Palindrome check using two pointers
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
# O(n) time, O(1) space — no new string created
```

---

**Practice:**
1. You have a list of 1000 player names. What is the Big O of: appending a name, removing the first name, checking if "Arthur" is in the list?
2. A function builds a result string by doing `result += char` inside a loop over `n` characters. What is the time complexity? Rewrite it to be `O(n)`.
3. Write a function `reverse_string(s: str) -> str` in `O(n)` time and `O(n)` space without using Python's built-in `[::-1]`. Then write a version that checks palindrome in `O(1)` space.

---

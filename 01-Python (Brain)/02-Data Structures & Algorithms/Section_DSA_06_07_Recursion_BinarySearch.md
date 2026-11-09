## DSA Section 06: Recursion — Call Stacks & Recursive Algorithms

Recursion is when a function calls itself with a smaller version of the same problem, until it reaches a stopping point simple enough to answer directly. Every recursive solution follows the same two-part structure: a **base case** (the stopping condition) and a **recursive case** (the self-call that shrinks the problem).

### 6.1 The Call Stack

When a function calls itself, Python creates a new stack frame for each call — its own set of local variables. These frames pile up like plates. When the base case is hit, frames start resolving from top to bottom, each returning its result to the frame below it.

```python
def countdown(n: int):
    if n == 0:                # Base case — stop here
        print("GO!")
        return
    print(n)
    countdown(n - 1)          # Recursive case — smaller problem

countdown(3)
# Prints: 3, 2, 1, GO!

# Call stack as countdown(3) runs:
# Frame 1: countdown(3) — prints 3, calls countdown(2)
#   Frame 2: countdown(2) — prints 2, calls countdown(1)
#     Frame 3: countdown(1) — prints 1, calls countdown(0)
#       Frame 4: countdown(0) — base case, prints GO!, returns
#     Frame 3 returns
#   Frame 2 returns
# Frame 1 returns
```

Too many recursive calls before a base case is hit causes Python to raise `RecursionError: maximum recursion depth exceeded`. Python's default stack depth limit is ~1000 frames.

### 6.2 The Recursive Template

Every recursive function fits this shape:

```python
def solve(problem):
    # 1. Base case — simplest possible input, answer directly
    if is_base_case(problem):
        return base_answer

    # 2. Recursive case — shrink the problem and trust the recursion
    smaller = make_smaller(problem)
    sub_result = solve(smaller)
    return combine(sub_result)
```

### 6.3 Classic Recursive Examples

**Factorial — O(n) time, O(n) space (call stack):**

```python
def factorial(n: int) -> int:
    if n == 0:              # Base case: 0! = 1
        return 1
    return n * factorial(n - 1)   # n! = n × (n-1)!

factorial(5)  # 5 × 4 × 3 × 2 × 1 = 120
```

**Fibonacci — naive O(2ⁿ) time:**

```python
def fib(n: int) -> int:
    if n <= 1:              # Base cases: fib(0)=0, fib(1)=1
        return n
    return fib(n - 1) + fib(n - 2)

# The problem: fib(5) calls fib(4) AND fib(3).
# fib(4) calls fib(3) AND fib(2).
# fib(3) is computed TWICE — exponential tree of redundant calls.
# fib(40) makes over 300 million calls. Fixed in Section 15 (DP).
```

**Sum of a list — O(n) time, O(n) space:**

```python
def recursive_sum(arr: list[int], i: int = 0) -> int:
    if i == len(arr):       # Base case: nothing left to sum
        return 0
    return arr[i] + recursive_sum(arr, i + 1)   # Add current + rest
```

**Power function — O(log n) time with fast exponentiation:**

```python
def power(base: int, exp: int) -> int:
    if exp == 0: return 1          # x^0 = 1
    if exp % 2 == 0:               # Even exponent: x^n = (x^(n/2))²
        half = power(base, exp // 2)
        return half * half         # Only ONE recursive call, not two
    return base * power(base, exp - 1)  # Odd: x^n = x × x^(n-1)
# halves the problem each even step → O(log n)
```

### 6.4 Thinking Recursively — The Mental Model

The hardest part of recursion is **trusting** that the recursive call works correctly. Don't trace through every level mentally. Instead:

1. **Define** what your function does precisely
2. **Write** the base case
3. **Assume** the recursive call works on the smaller input
4. **Use** that assumed result to construct the full answer

```python
def flatten(nested: list) -> list:
    """Returns a flat list from a nested list like [1, [2, [3, 4]], 5]."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))   # Trust: flatten works on smaller lists
        else:
            result.append(item)
    return result

flatten([1, [2, [3, 4]], 5])   # [1, 2, 3, 4, 5]
```

---

**Practice:**
1. Write a recursive function `sum_digits(n: int) -> int` that returns the sum of a number's digits (e.g., `sum_digits(1234) → 10`). Identify the base case.
2. Write a recursive function `count_quests(tree: dict) -> int` where the tree is a nested dict `{"quest": "...", "subquests": [...]}`. Count all quests at every level.
3. What is the time complexity of the naive `fib(n)` without caching? Draw the call tree for `fib(4)` and count total function calls.

---

## DSA Section 07: Binary Search — Traditional & Condition-Based

Binary search is the clearest example of `O(log n)` thinking. Instead of checking every element, you eliminate half the remaining possibilities with each comparison. On 1,000,000 elements, binary search takes at most 20 steps.

**The precondition:** the data must be sorted (or the answer space must be monotonic). Apply binary search to unsorted data and you'll get wrong answers silently.

### 7.1 Traditional Binary Search

```python
def binary_search(arr: list[int], target: int) -> int:
    """Returns the index of target in sorted arr, or -1 if not found."""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2   # Avoid overflow vs (left+right)//2 is fine in Python

        if arr[mid] == target:
            return mid               # Found it
        elif arr[mid] < target:
            left = mid + 1           # Target is in the RIGHT half
        else:
            right = mid - 1          # Target is in the LEFT half

    return -1   # Not found

players_sorted = [1, 5, 8, 12, 18, 23, 35, 42]
binary_search(players_sorted, 18)   # Returns 4 (index)
binary_search(players_sorted, 99)   # Returns -1
```

Tracing through `binary_search([1,5,8,12,18,23,35,42], 18)`:

```
left=0, right=7, mid=3  → arr[3]=12 < 18 → left=4
left=4, right=7, mid=5  → arr[5]=23 > 18 → right=4
left=4, right=4, mid=4  → arr[4]=18 = 18 → return 4
```

Three steps, not eight. That's `O(log n)`.

### 7.2 Find First and Last Position

```python
def find_first(arr: list[int], target: int) -> int:
    """Returns the first (leftmost) index of target, or -1."""
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid        # Found one, but keep searching LEFT for an earlier one
            right = mid - 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

def find_last(arr: list[int], target: int) -> int:
    """Returns the last (rightmost) index of target, or -1."""
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid        # Found one, but keep searching RIGHT for a later one
            left = mid + 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

### 7.3 Using Python's bisect Module

```python
import bisect

arr = [1, 5, 8, 12, 18, 23, 35, 42]

bisect.bisect_left(arr, 18)    # 4 — leftmost position where 18 can be inserted
bisect.bisect_right(arr, 18)   # 5 — rightmost position where 18 can be inserted
bisect.insort(arr, 20)         # Insert 20 in sorted order — O(n) due to shifting
```

### 7.4 Condition-Based Binary Search — The Advanced Form

This is the harder, more powerful form. Instead of searching an array for a value, you **search a range of possible answers** for the minimum (or maximum) value that satisfies a condition.

The condition must be **monotonic**: the answer is `False` for low values and `True` for high values (or vice versa), with exactly one boundary between them. You binary search for that boundary.

```
          ← False | True →
  1 2 3 4 5 6 7 8 9 10
                ↑
           search this line
```

**Recognise this pattern when a problem says:** "What is the *minimum* X such that condition Y is satisfied?" or "What is the *maximum* X such that condition Z still holds?"

**Classic example: Minimum pages per day to finish books in D days:**

```python
def can_finish(pages: list[int], daily_limit: int, days: int) -> bool:
    """Can we finish all books if we read at most daily_limit pages per day?"""
    current_day_pages = 0
    days_needed = 1
    for p in pages:
        if current_day_pages + p > daily_limit:
            days_needed += 1      # Start a new day
            current_day_pages = 0
        current_day_pages += p
    return days_needed <= days

def min_pages_per_day(books: list[int], days: int) -> int:
    """
    Binary search the ANSWER (pages per day), not the input array.
    The answer must be at least max(books) — you must read the biggest book.
    The answer is at most sum(books) — read everything in one day.
    """
    left  = max(books)     # Minimum possible answer
    right = sum(books)     # Maximum possible answer

    while left < right:
        mid = (left + right) // 2
        if can_finish(books, mid, days):
            right = mid          # mid works — try smaller
        else:
            left = mid + 1       # mid doesn't work — try larger

    return left  # The minimum value where can_finish() becomes True

books = [3, 2, 4, 1, 5]
min_pages_per_day(books, days=3)   # 5 (optimal split: [3,2], [4,1], [5])
```

### 7.5 Binary Search Template

```python
# Template: find the leftmost position where condition(mid) is True
def binary_search_condition(lo: int, hi: int) -> int:
    while lo < hi:
        mid = (lo + hi) // 2
        if condition(mid):
            hi = mid          # mid works; look left for a smaller answer
        else:
            lo = mid + 1      # mid doesn't work; go right
    return lo  # lo == hi == the boundary point
```

---

**Practice:**
1. Implement `binary_search(arr, target)` from scratch and test it on a sorted list of 10 integers. Trace through the steps for one search.
2. Using condition-based binary search, write `min_speed(distances, hours)` — what's the minimum integer speed needed to travel a list of distances within `hours` time? (Each segment takes `ceil(distance/speed)` hours.)
3. Python's `bisect.bisect_left(arr, x)` returns the leftmost index where `x` can be inserted to keep `arr` sorted. Write your own version without importing `bisect`.

---

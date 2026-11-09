## DSA Section 14: Recursive Backtracking

Backtracking is a systematic way to explore a tree of decisions. You build a solution choice by choice, and the moment a partial solution can't possibly lead to a valid answer, you **undo the last choice** and try the next option. This "undo" step is what distinguishes backtracking from plain recursion.

Think of it like navigating a dungeon: you walk down a corridor, and if you hit a dead end, you retrace your steps to the last fork and try a different direction. You explore systematically, cutting off branches early when you know they lead nowhere.

### 14.1 The Backtracking Template

Every backtracking solution follows this three-step pattern:

```python
def backtrack(state, choices):
    if is_complete(state):          # BASE CASE: found a valid solution
        record(state)
        return

    for choice in choices:
        if is_valid(state, choice): # PRUNE: skip invalid choices
            make_choice(state, choice)    # 1. CHOOSE
            backtrack(state, next_choices)  # 2. EXPLORE
            undo_choice(state, choice)    # 3. UNCHOOSE (backtrack)
```

The "unchoose" step restores the state to exactly what it was before the choice — so the next iteration of the loop starts from the same clean state.

### 14.2 Generating All Subsets

```python
def subsets(nums: list[int]) -> list[list[int]]:
    """Generate all 2^n subsets of nums."""
    result = []

    def backtrack(start: int, current: list):
        result.append(current[:])   # Record a copy of the current subset

        for i in range(start, len(nums)):
            current.append(nums[i])           # CHOOSE: add nums[i]
            backtrack(i + 1, current)         # EXPLORE: continue from next index
            current.pop()                     # UNCHOOSE: remove nums[i]

    backtrack(0, [])
    return result

subsets([1, 2, 3])
# [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
# 2^3 = 8 subsets total
```

### 14.3 Generating All Permutations

```python
def permutations(nums: list[int]) -> list[list[int]]:
    """Generate all n! permutations of nums."""
    result = []

    def backtrack(current: list, remaining: list):
        if not remaining:               # BASE CASE: nothing left to add
            result.append(current[:])
            return

        for i in range(len(remaining)):
            current.append(remaining[i])                        # CHOOSE
            backtrack(current, remaining[:i] + remaining[i+1:]) # EXPLORE (without chosen)
            current.pop()                                       # UNCHOOSE

    backtrack([], nums)
    return result

permutations([1, 2, 3])
# [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]] — 3! = 6
```

### 14.4 Combinations

```python
def combinations(n: int, k: int) -> list[list[int]]:
    """All C(n,k) combinations of k numbers chosen from 1..n."""
    result = []

    def backtrack(start: int, current: list):
        if len(current) == k:           # BASE CASE: picked exactly k numbers
            result.append(current[:])
            return

        for i in range(start, n + 1):
            current.append(i)           # CHOOSE
            backtrack(i + 1, current)   # EXPLORE (only pick larger numbers → no duplicates)
            current.pop()               # UNCHOOSE

    backtrack(1, [])
    return result

combinations(4, 2)   # [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
```

### 14.5 Classic: Generate Valid Parentheses

```python
def generate_parentheses(n: int) -> list[str]:
    """Generate all valid combinations of n pairs of parentheses."""
    result = []

    def backtrack(current: str, open_count: int, close_count: int):
        if len(current) == 2 * n:      # BASE CASE: used all 2n brackets
            result.append(current)
            return

        if open_count < n:             # Can add '(' if we haven't used n yet
            backtrack(current + "(", open_count + 1, close_count)

        if close_count < open_count:   # Can add ')' only if it won't exceed '('
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
    return result

generate_parentheses(3)
# ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

### 14.6 Pruning — The Power of Backtracking

Without pruning, backtracking degenerates to brute force. Pruning cuts off branches of the decision tree the moment they become invalid — before exploring any further.

```python
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """Find all combinations that sum to target (can reuse elements)."""
    result = []
    candidates.sort()   # Sort first so we can prune early

    def backtrack(start: int, current: list, remaining: int):
        if remaining == 0:             # Found a valid combination
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                  # PRUNE: sorted, so all later candidates also too large
            current.append(c)
            backtrack(i, current, remaining - c)   # i (not i+1) allows reuse
            current.pop()

    backtrack(0, [], target)
    return result

combination_sum([2, 3, 6, 7], target=7)
# [[2, 2, 3], [7]]
```

### 14.7 Complexity of Backtracking

Backtracking explores an exponential search space, but pruning reduces actual work:

| Problem type | Without pruning | With pruning |
|---|---|---|
| Subsets of n items | O(2^n) | O(2^n) — can't avoid |
| Permutations of n items | O(n!) | O(n!) — can't avoid |
| N-Queens | O(n^n) | O(n!) with constraint pruning |
| Combination sum | O(k^n) | Much less with early break |

The "pruning" is what makes backtracking practical — a brute-force exponential tree, with most branches cut short.

---

**Practice:**
1. Write `subsets([1,2,3])` from scratch using backtracking. Trace the call tree for the first three calls.
2. Write `combination_sum([2,3,5], target=8)` — find all combinations that sum to 8 with reuse allowed.
3. Write `permutations([1,2,3])` and count the output. Confirm it matches 3! = 6 permutations.

---

## DSA Section 15: Dynamic Programming

Dynamic Programming (DP) solves problems by breaking them into **overlapping subproblems** and storing each subproblem's result so it's never computed twice. The two signals that a problem calls for DP:

1. **Optimal substructure** — the optimal answer to the full problem can be built from optimal answers to subproblems.
2. **Overlapping subproblems** — the same subproblem is solved many times in a naive recursive solution.

### 15.1 The Problem with Naive Recursion

```python
def fib_naive(n: int) -> int:
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# fib_naive(6):
# fib(6) → fib(5) + fib(4)
# fib(5) → fib(4) + fib(3)   ← fib(4) computed TWICE at this level alone
# fib(4) → fib(3) + fib(2)   ← fib(3) computed multiple times
# The tree doubles at every level → O(2^n)
```

### 15.2 Top-Down Memoisation — Cache the Recursion

Add a cache (dict or list). Before computing, check if the answer is already stored.

```python
def fib_memo(n: int, memo: dict = {}) -> int:
    if n in memo: return memo[n]    # Cache hit — skip recomputation
    if n <= 1:    return n

    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

# Now each value is computed exactly once → O(n) time, O(n) space
fib_memo(50)   # Instant. Naive takes ~trillion operations.

# Using functools.lru_cache — cleaner syntax
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

### 15.3 Bottom-Up Tabulation — Build From Smallest Subproblems

Start from the smallest subproblem and fill a table upward. No recursion — avoids call stack overhead and stack overflow risk.

```python
def fib_bottom_up(n: int) -> int:
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]  # Use previously computed values
    return dp[n]
# O(n) time, O(n) space

# Space-optimised: you only need the last two values
def fib_optimised(n: int) -> int:
    if n <= 1: return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
# O(n) time, O(1) space
```

### 15.4 Classic DP Problems

**Climbing Stairs (how many ways to reach step n, taking 1 or 2 steps at a time):**

```python
def climb_stairs(n: int) -> int:
    """Number of distinct ways to climb n stairs."""
    if n <= 2: return n
    # To reach step i: come from step i-1 (one step) OR step i-2 (two steps)
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]   # Exactly Fibonacci!
    return dp[n]

climb_stairs(5)   # 8 ways
```

**0/1 Knapsack (maximum value within weight capacity):**

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """Maximum value achievable with items that fit in capacity."""
    n = len(weights)
    # dp[i][w] = max value using first i items with weight limit w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Option 1: Don't take item i
            dp[i][w] = dp[i-1][w]
            # Option 2: Take item i (if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w],
                               dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][capacity]

knapsack([2, 3, 4, 5], [3, 4, 5, 6], capacity=5)   # 7
```

**Longest Common Subsequence (LCS):**

```python
def lcs(s1: str, s2: str) -> int:
    """Length of the longest common subsequence of s1 and s2."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1   # Characters match — extend LCS
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # Take the better of skip

    return dp[m][n]

lcs("Arthur", "Arthurian")   # 6 — "Arthur" is a common subsequence
```

**Coin Change (minimum coins to make amount):**

```python
def coin_change(coins: list[int], amount: int) -> int:
    """Minimum number of coins to make amount. Returns -1 if impossible."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0   # 0 coins needed to make amount 0

    for coin in coins:
        for amt in range(coin, amount + 1):
            dp[amt] = min(dp[amt], dp[amt - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1

coin_change([1, 5, 10, 25], amount=41)   # 4 coins: 25+10+5+1
```

### 15.5 Top-Down vs Bottom-Up

| | Top-Down (Memoisation) | Bottom-Up (Tabulation) |
|---|---|---|
| Code style | Recursive + cache | Iterative + table |
| Starting point | Full problem → subproblems | Smallest → full problem |
| Stack risk | Yes (deep recursion) | No |
| Speed | Slightly slower (function calls) | Slightly faster |
| Which to learn first | **This one** — mirrors the recurrence naturally | Once you understand top-down |

**Process for any DP problem:**
1. Define what `dp[i]` (or `dp[i][j]`) means precisely
2. Write the recurrence relation (how `dp[i]` depends on smaller values)
3. Identify base cases
4. Fill the table (bottom-up) or add a cache (top-down)

---

**Practice:**
1. Implement `fib(n)` three ways: naive recursion, top-down memoisation, bottom-up tabulation. Time all three for `n=40`.
2. Solve `climb_stairs(10)` bottom-up. Then optimise it to `O(1)` space.
3. Implement `coin_change([1,2,5], amount=11)`. Trace through the dp table manually for `amount=5`.

---

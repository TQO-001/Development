# DSA Mastery: 124 Exercises
## Sections 01–16 | Big O → Bit Manipulation

**Same format as the Python exercise set. No changes, no surprises.**

```
### [emoji] #N — Title
**Time:** ~X min | **Concept:** one-liner

- Task line

**✓ Done when:** specific test case with expected output.
> 💡 Hint (only where needed)
```

**Difficulty scale**
| Emoji | Level | Time |
|---|---|---|
| 🟢 | Warm-Up | 5–10 min |
| 🟡 | Core | 10–20 min |
| 🟠 | Applied | 15–25 min |
| 🔴 | Challenge | 20–35 min |
| 💀 | Boss | 35–50 min |

**Rule:** Every exercise must be coded and run — no "think through it" answers. Write the code. See the output.

---

## 🏁 Master Checklist

**Arc 1 — Big O (6):** `1☐ 2☐ 3☐ 4☐ 5☐ 6☐`

**Arc 2 — Arrays & Strings (8):** `7☐ 8☐ 9☐ 10☐ 11☐ 12☐ 13☐ 14☐`

**Arc 3 — Linked Lists (8):** `15☐ 16☐ 17☐ 18☐ 19☐ 20☐ 21☐ 22☐`

**Arc 4 — Hash Tables (8):** `23☐ 24☐ 25☐ 26☐ 27☐ 28☐ 29☐ 30☐`

**Arc 5 — Stacks & Queues (8):** `31☐ 32☐ 33☐ 34☐ 35☐ 36☐ 37☐ 38☐`

**Arc 6 — Recursion (8):** `39☐ 40☐ 41☐ 42☐ 43☐ 44☐ 45☐ 46☐`

**Arc 7 — Binary Search (8):** `47☐ 48☐ 49☐ 50☐ 51☐ 52☐ 53☐ 54☐`

**Arc 8 — Trees & BST (8):** `55☐ 56☐ 57☐ 58☐ 59☐ 60☐ 61☐ 62☐`

**Arc 9 — Heaps (8):** `63☐ 64☐ 65☐ 66☐ 67☐ 68☐ 69☐ 70☐`

**Arc 10 — Sorting (8):** `71☐ 72☐ 73☐ 74☐ 75☐ 76☐ 77☐ 78☐`

**Arc 11 — Graphs (8):** `79☐ 80☐ 81☐ 82☐ 83☐ 84☐ 85☐ 86☐`

**Arc 12 — Two Pointers (8):** `87☐ 88☐ 89☐ 90☐ 91☐ 92☐ 93☐ 94☐`

**Arc 13 — Sliding Window (6):** `95☐ 96☐ 97☐ 98☐ 99☐ 100☐`

**Arc 14 — Backtracking (8):** `101☐ 102☐ 103☐ 104☐ 105☐ 106☐ 107☐ 108☐`

**Arc 15 — Dynamic Programming (8):** `109☐ 110☐ 111☐ 112☐ 113☐ 114☐ 115☐ 116☐`

**Arc 16 — Bit Manipulation (8):** `117☐ 118☐ 119☐ 120☐ 121☐ 122☐ 123☐ 124☐`

---

# ARC 1 — Big O Notation
## 6 Exercises | Classify → Drop → Predict → Measure

---

### 🟢 #1 — Classify Six Snippets
**Time:** ~8 min | **Concept:** pattern-matching loops to complexities

Write a Python file with these six functions — each does something trivial. Below each, write a comment stating its time complexity and why:

```python
def a(n): return n * 2                              # ?
def b(arr): return arr[0]                           # ?
def c(arr):
    for x in arr:
        for y in arr: pass                          # ?
def d(n):
    i = n
    while i > 1: i //= 2                           # ?
def e(arr):
    for x in arr: pass
    for x in arr: pass                              # ?
def f(n):
    if n <= 1: return 1
    return f(n-1) + f(n-1)                         # ?
```

**✓ Done when:** All 6 complexities correct: O(1), O(1), O(n²), O(log n), O(n), O(2ⁿ).

---

### 🟢 #2 — Drop the Constants
**Time:** ~5 min | **Concept:** simplification rules

Write a function for each expression, simplify it in a comment, and confirm by writing `# Simplifies to O(?)`:
- `O(3n² + 7n + 12)`
- `O(n log n + n²)`
- `O(n + 500)`
- `O(2^n + n!)`
- `O(n/2)`

**✓ Done when:** Simplified answers: O(n²), O(n²), O(n), O(n!), O(n) — each with a one-sentence justification.

---

### 🟡 #3 — Space Complexity Analysis
**Time:** ~10 min | **Concept:** measuring memory growth, not time

For each function below, write its **space** complexity and why:

```python
def alpha(arr):
    total = 0
    for x in arr: total += x
    return total

def beta(arr):
    return [x * 2 for x in arr]

def gamma(n):
    if n == 0: return 0
    return n + gamma(n - 1)

def delta(n):
    grid = [[0] * n for _ in range(n)]
    return grid
```

**✓ Done when:** Answers are O(1), O(n), O(n) (call stack), O(n²) — each with one sentence.

---

### 🟡 #4 — Count Operations Empirically
**Time:** ~15 min | **Concept:** measuring actual operation counts to confirm Big O

- Write a linear search `find_linear(arr, target)` with a `count` variable that increments on each comparison.
- Write a binary search `find_binary(arr, target)` with the same counter.
- Run both on a sorted list of 1000 elements, searching for the last element.
- Print both counts.

**✓ Done when:** Linear prints ~1000 comparisons; binary prints ~10. The ratio confirms `O(n)` vs `O(log n)`.

---

### 🔴 #5 — Nested Complexity Prediction
**Time:** ~15 min | **Concept:** non-obvious nested complexities

Predict the complexity of each, then run with a counter to verify:

```python
# A: outer loop n, inner loop log n
for i in range(n):
    j = n
    while j > 1: j //= 2

# B: outer loop n, inner loop i (not n)
for i in range(n):
    for j in range(i): pass

# C: loop where i doubles each step
i = 1
while i < n: i *= 2
```

**✓ Done when:** A is O(n log n), B is O(n²), C is O(log n) — confirmed by counter output.
> 💡 For B: sum of 0+1+2+...+(n-1) = n(n-1)/2 → O(n²).

---

### 💀 #6 — BOSS: Predict, Run, and Explain Divergence
**Time:** ~35 min | **Concept:** Big O is asymptotic — small n can mislead

- Write all three: linear search, binary search, bubble sort on a list of size `n`.
- For each n in `[10, 100, 1000, 5000]`: time all three using `time.perf_counter`.
- Print a table: n | linear_time | binary_time | bubble_time.
- In comments below the table, explain: at what n does binary search visibly outperform linear? Why does bubble sort diverge most sharply?

**✓ Done when:** Table has 4 rows × 3 columns; your explanation correctly attributes the divergence pattern to the O-class of each algorithm.

---

# ARC 2 — Arrays & Strings
## 8 Exercises | In-Place → Prefix Sums → String Traps

---

### 🟢 #7 — List Operation Timing
**Time:** ~10 min | **Concept:** proving O(1) vs O(n) through measurement

- Use `timeit` to time: `list.append(x)`, `list.insert(0, x)`, `x in list`, `list[0]`.
- Run each on lists of size 100, 1000, 10000.
- Print the times. Which ones stay flat as n grows? Which scale with n?

**✓ Done when:** `append` and `list[0]` stay nearly constant; `insert(0, x)` and `x in list` grow linearly with n.

---

### 🟢 #8 — In-Place Write Pointer
**Time:** ~10 min | **Concept:** overwrite elements without extra space

- Write `remove_zeros(arr: list[int]) -> int` — removes all zeros in place; returns new length.
- Use a `write` pointer and a `read` pointer — no slicing, no new list.
- Test: `arr = [0, 1, 0, 3, 0, 12]` → after call, `arr[:result]` should be `[1, 3, 12]`.

**✓ Done when:** `remove_zeros([0,1,0,3,0,12])` returns `3`; first 3 elements of the modified array are `[1, 3, 12]`. O(n) time, O(1) space.

---

### 🟡 #9 — Prefix Sum Array
**Time:** ~15 min | **Concept:** O(1) range sum queries after O(n) preprocessing

- Build `prefix_sum(arr)` that returns a prefix array where `prefix[i] = sum(arr[:i])` (prefix[0] = 0).
- Build `range_sum(prefix, l, r)` returning sum of `arr[l..r]` in O(1).
- Test: `arr = [3, 1, 4, 1, 5, 9, 2]` → `range_sum(prefix, 2, 5)` should be `4+1+5+9 = 19`.

**✓ Done when:** `range_sum` returns `19` for the given inputs; no loop inside `range_sum` (just subtraction of two prefix values).

---

### 🟡 #10 — Two-Pass Average Filter
**Time:** ~12 min | **Concept:** two O(n) passes, not one O(n²) nested loop

- Write `above_average(arr: list[float]) -> list[float]` — returns a new list of only the values above the mean.
- Pass 1: compute the mean.
- Pass 2: filter.
- Confirm this is O(n) not O(n²) with a comment explaining why.

**✓ Done when:** `above_average([1, 2, 3, 4, 5, 6])` returns `[4, 5, 6]` (mean = 3.5).

---

### 🟠 #11 — String Concatenation Trap
**Time:** ~15 min | **Concept:** O(n²) vs O(n) string building

- Write `bad_join(words: list[str]) -> str` — builds result with `result += word + " "` in a loop.
- Write `good_join(words: list[str]) -> str` — builds result using a list accumulator and `"".join()`.
- Time both on a list of 10,000 one-word strings using `timeit`.
- Print both times.

**✓ Done when:** `good_join` is measurably faster (often 10-100x); both produce the same output string.

---

### 🟠 #12 — Anagram Check
**Time:** ~12 min | **Concept:** frequency counting with a hash map

- Write `is_anagram(s: str, t: str) -> bool` — returns True if s and t are anagrams (same characters, same frequencies, different order).
- Solve it twice: once with `sorted()` (O(n log n)), once with a `Counter` or manual dict (O(n)).
- Test: `is_anagram("listen", "silent")` → `True`; `is_anagram("hello", "world")` → `False`.

**✓ Done when:** Both versions return correct results; you can state the complexity of each in a comment.

---

### 🔴 #13 — Rotate Array In-Place
**Time:** ~20 min | **Concept:** in-place array rotation without extra O(n) space

- Write `rotate(arr: list[int], k: int)` — rotates the array to the right by `k` steps, in place, O(1) extra space.
- The trick: reverse the whole array, then reverse the first k elements, then reverse the rest.
- Test: `arr = [1,2,3,4,5,6,7]`, `k=3` → `arr` becomes `[5,6,7,1,2,3,4]`.

**✓ Done when:** The array is modified in place (no return value); result matches `[5,6,7,1,2,3,4]`.
> 💡 Three reversal calls. `reverse(arr, 0, n-1)` then `reverse(arr, 0, k-1)` then `reverse(arr, k, n-1)`.

---

### 💀 #14 — BOSS: Longest Substring Without Repeating Characters
**Time:** ~40 min | **Concept:** sliding window on a string using a set

- Write `length_of_longest_substring(s: str) -> int`.
- Use a set to track characters in the current window; two pointers `left` and `right`.
- When `s[right]` is already in the set, shrink from `left` until the duplicate is removed.
- Test cases: `"abcabcbb"` → 3; `"bbbbb"` → 1; `"pwwkew"` → 3; `""` → 0.

**✓ Done when:** All four test cases pass. O(n) time, O(min(n, alphabet)) space.

---

# ARC 3 — Linked Lists
## 8 Exercises | Build → Reverse → Cycle → Merge

---

### 🟢 #15 — Build a Singly Linked List
**Time:** ~12 min | **Concept:** Node class, head pointer, append

- Write `Node` class with `value` and `next`.
- Write `SinglyLinkedList` with `append(value)` and `print_list()`.
- Build: `[10 → 20 → 30 → 40 → None]` and call `print_list`.

**✓ Done when:** `print_list()` outputs `10 → 20 → 30 → 40 → None`.

---

### 🟢 #16 — Prepend and Delete
**Time:** ~12 min | **Concept:** pointer rewiring at head and middle

- Add `prepend(value)` — inserts at head in O(1).
- Add `delete(value)` — removes first node with that value; handle head deletion separately.
- Test: build `[10→20→30]`, prepend `5`, delete `20`.

**✓ Done when:** Final list prints as `5 → 10 → 30 → None`.

---

### 🟡 #17 — Reverse In Place
**Time:** ~15 min | **Concept:** three-pointer reversal, O(1) space

- Write `reverse(head: Node) -> Node` — reverses the list in place using `prev`, `current`, `next_node` pointers.
- Return the new head.
- Test: `[1→2→3→4→5]` → reversed → `[5→4→3→2→1]`.

**✓ Done when:** `print_list` after reversal shows `5 → 4 → 3 → 2 → 1 → None`.

---

### 🟡 #18 — Find the Middle Node
**Time:** ~12 min | **Concept:** fast/slow pointer technique

- Write `find_middle(head: Node) -> Node` — uses a fast pointer (2 steps) and slow pointer (1 step).
- When fast reaches the end, slow is at the middle.
- Test: `[1→2→3→4→5]` → returns node with value `3`. `[1→2→3→4]` → returns node with value `2` or `3` (document which one your implementation returns).

**✓ Done when:** Odd-length list returns the exact middle; even-length list returns consistently the first or second middle (your choice — document it).

---

### 🟠 #19 — Detect a Cycle
**Time:** ~15 min | **Concept:** Floyd's fast/slow pointer algorithm

- Write `has_cycle(head: Node) -> bool`.
- Fast pointer moves 2 steps, slow moves 1. If they meet, there's a cycle.
- Build a test list manually: 4 nodes, connect the last node's `next` back to node 2 to create a cycle.
- Also test on a non-cyclic list to confirm `False`.

**✓ Done when:** Cyclic list returns `True`; non-cyclic returns `False`.

---

### 🟠 #20 — Remove N-th Node From End
**Time:** ~18 min | **Concept:** two-pointer gap technique

- Write `remove_nth_from_end(head: Node, n: int) -> Node`.
- Use two pointers: advance the first pointer `n` steps ahead, then move both together until the first hits the end — the second is now at the node before the target.
- Test: `[1→2→3→4→5]`, `n=2` → removes `4` → `[1→2→3→5]`.

**✓ Done when:** `print_list` after removal shows `1 → 2 → 3 → 5 → None`.
> 💡 Use a dummy head node to handle edge cases like removing the first node.

---

### 🔴 #21 — Doubly Linked List
**Time:** ~25 min | **Concept:** bidirectional pointers, O(1) known-node deletion

- Build `DoublyNode` with `value`, `next`, `prev`.
- Build `DoublyLinkedList` with `append`, `prepend`, `delete_node(node)` (given the node, O(1) deletion), and `print_forward` / `print_backward`.
- Test: append 1, 2, 3; delete the node holding 2; print forward and backward.

**✓ Done when:** Forward prints `1 ↔ 3 → None`; backward prints `3 ↔ 1 → None`.

---

### 💀 #22 — BOSS: Merge Two Sorted Linked Lists
**Time:** ~40 min | **Concept:** pointer manipulation without extra space

- Write `merge_sorted(l1: Node, l2: Node) -> Node` — merges two sorted singly linked lists into one sorted list.
- In-place (no new nodes); rewire `next` pointers only.
- Use a dummy head node to simplify edge cases.
- Test: `[1→3→5]` and `[2→4→6]` → `[1→2→3→4→5→6]`.
- Also test: `[]` and `[1→2]` → `[1→2]`.

**✓ Done when:** Both test cases produce correct merged output. O(n+m) time, O(1) space.

---

# ARC 4 — Hash Tables
## 8 Exercises | Count → Deduplicate → Two Sum → Group

---

### 🟢 #23 — Frequency Counter
**Time:** ~8 min | **Concept:** building a dict from an iterable

- Write `count_freq(items: list) -> dict` — counts occurrences of each item using a plain `dict` (no `Counter`).
- Use `dict.get(key, 0)` for safe increment.
- Test: `count_freq(["a","b","a","c","b","a"])` → `{"a": 3, "b": 2, "c": 1}`.

**✓ Done when:** Output matches expected dict exactly.

---

### 🟢 #24 — First Duplicate
**Time:** ~8 min | **Concept:** O(n) membership testing with a set

- Write `first_duplicate(arr: list) -> any` — returns the first element that appears more than once, or `None` if no duplicates.
- Use a `set` to track seen values — O(1) lookup per item.
- Test: `first_duplicate([1, 3, 4, 2, 2])` → `2`; `first_duplicate([1, 2, 3])` → `None`.

**✓ Done when:** Both test cases pass. O(n) time, O(n) space.

---

### 🟡 #25 — Two Sum (O(n))
**Time:** ~12 min | **Concept:** complement lookup in a hash map

- Write `two_sum(nums: list[int], target: int) -> tuple[int, int]` — returns the indices of two numbers that add to target.
- Use a dict `seen = {value: index}` for O(1) complement lookup.
- Test: `two_sum([2, 7, 11, 15], 9)` → `(0, 1)`; `two_sum([3, 2, 4], 6)` → `(1, 2)`.

**✓ Done when:** Both test cases return correct index pairs. O(n) time, O(n) space.

---

### 🟡 #26 — Group By Property
**Time:** ~12 min | **Concept:** `defaultdict(list)` for grouping

- Write `group_by_length(words: list[str]) -> dict[int, list[str]]` — groups words by their length.
- Use `collections.defaultdict(list)`.
- Test: `group_by_length(["hi", "hello", "hey", "world"])` → `{2: ["hi"], 5: ["hello", "world"], 3: ["hey"]}`.

**✓ Done when:** Output groups match expected (order within groups matches input order).

---

### 🟠 #27 — Two Lists Intersection
**Time:** ~12 min | **Concept:** set intersection vs dict-based intersection

- Write `intersection(a: list, b: list) -> list` — returns elements present in BOTH lists, without duplicates.
- Solve it twice: once with `set(a) & set(b)`, once with a manual dict approach.
- Test: `intersection([1,2,3,4], [2,4,6,8])` → `[2, 4]` (order doesn't matter).

**✓ Done when:** Both versions return `[2, 4]` (or `[4, 2]`); you can state the complexity of each.

---

### 🟠 #28 — Longest Consecutive Sequence
**Time:** ~20 min | **Concept:** O(n) using a set — no sorting

- Write `longest_consecutive(nums: list[int]) -> int` — finds the length of the longest sequence of consecutive integers.
- Put all values in a `set`. For each `n` where `n-1` is NOT in the set (i.e., n is a sequence start), count forward.
- Test: `longest_consecutive([100, 4, 200, 1, 3, 2])` → `4` (sequence: 1,2,3,4).

**✓ Done when:** Returns `4`. O(n) time — confirm no nested loop over the full array.
> 💡 The "only start from sequence beginnings" condition is what keeps it O(n).

---

### 🔴 #29 — Top K Frequent Elements
**Time:** ~20 min | **Concept:** combining frequency dict with sorting or heap

- Write `top_k_frequent(nums: list[int], k: int) -> list[int]` — returns the `k` most frequent elements.
- Use a frequency dict first; then either `sorted()` by frequency (O(n log n)) or a heap (O(n log k)).
- Test: `top_k_frequent([1,1,1,2,2,3], k=2)` → `[1, 2]`.

**✓ Done when:** Returns `[1, 2]`. Implement both approaches; comment the complexity of each.

---

### 💀 #30 — BOSS: Subarray Sum Equals K
**Time:** ~40 min | **Concept:** prefix sum + hash map, O(n) — the hardest hash map pattern

- Write `subarray_sum(nums: list[int], k: int) -> int` — count the number of contiguous subarrays whose sum equals exactly k.
- Naive approach: O(n²) with two loops — implement and confirm it works first.
- Optimal: keep a running `prefix_sum`; if `prefix_sum - k` exists in a dict of previously seen prefix sums, those subarrays sum to k.
- Test: `subarray_sum([1, 1, 1], 2)` → `2`; `subarray_sum([1, 2, 3], 3)` → `2`.

**✓ Done when:** Both test cases return correct answers from the O(n) version. Comment why `prefix_sum - k` being in the dict proves a subarray sums to k.

---

# ARC 5 — Stacks & Queues
## 8 Exercises | LIFO → Brackets → Min Stack → BFS

---

### 🟢 #31 — Stack Class
**Time:** ~8 min | **Concept:** wrapping a list with stack semantics

- Write `class Stack:` with `push(val)`, `pop() -> any`, `peek() -> any`, `is_empty() -> bool`, `size() -> int`.
- `pop()` and `peek()` on empty stack should raise `IndexError`.
- Test: push 1, 2, 3; peek → 3; pop → 3; size → 2.

**✓ Done when:** All operations behave correctly; empty stack operations raise `IndexError`.

---

### 🟢 #32 — Valid Brackets
**Time:** ~12 min | **Concept:** stack-based matching

- Write `is_valid(s: str) -> bool` — returns True if all `(`, `[`, `{` are properly closed in correct order.
- Use a stack: push openers, pop and match on closers.
- Test: `"({[]})"` → `True`; `"({[}"` → `False`; `"((("` → `False`; `""` → `True`.

**✓ Done when:** All four test cases return correct booleans.

---

### 🟡 #33 — Min Stack (O(1) Minimum)
**Time:** ~15 min | **Concept:** auxiliary stack to track minimums

- Write `class MinStack:` with `push(val)`, `pop()`, `top() -> int`, `get_min() -> int` — all O(1).
- Maintain a second `min_stack` that tracks the current minimum at every level.
- Test sequence: push 5, push 3, push 7, push 1; `get_min()` → 1; pop; `get_min()` → 3.

**✓ Done when:** `get_min()` returns correct minimum after each pop without scanning the stack.

---

### 🟡 #34 — Queue with Deque
**Time:** ~10 min | **Concept:** `collections.deque` for O(1) front/back operations

- Write `class Queue:` wrapping `collections.deque` with `enqueue(val)`, `dequeue() -> any`, `front() -> any`, `is_empty() -> bool`.
- Confirm `dequeue()` is O(1) — not `list.pop(0)`.
- Test: enqueue 1, 2, 3; dequeue → 1; dequeue → 2; front → 3.

**✓ Done when:** FIFO order confirmed; `dequeue()` removes from front, not back.

---

### 🟠 #35 — BFS Level-by-Level
**Time:** ~18 min | **Concept:** queue-driven breadth-first traversal recording depth

- Write `bfs_levels(graph: dict, start: str) -> list[list[str]]` — returns a list of lists, each inner list being all nodes at one depth.
- Use a deque; process all nodes at the current level before moving to the next.
- Test on the graph `{"A": ["B","C"], "B": ["D"], "C": ["D","E"], "D": [], "E": []}` from start `"A"`.

**✓ Done when:** Returns `[["A"], ["B","C"], ["D","E"]]` (order within levels may vary).

---

### 🟠 #36 — Next Greater Element
**Time:** ~18 min | **Concept:** monotonic stack

- Write `next_greater(nums: list[int]) -> list[int]` — for each element, find the next element to its right that is greater; -1 if none.
- Use a stack of indices; pop when current element exceeds the element at the top index.
- Test: `next_greater([2, 1, 2, 4, 3])` → `[4, 2, 4, -1, -1]`.

**✓ Done when:** Output matches expected. O(n) — each element pushed and popped at most once.

---

### 🔴 #37 — Evaluate Reverse Polish Notation
**Time:** ~20 min | **Concept:** stack for expression evaluation

- Write `eval_rpn(tokens: list[str]) -> int` — evaluates a postfix (RPN) expression.
- Numbers push onto the stack; operators pop two, compute, push result.
- Test: `["2","1","+","3","*"]` → `9`; `["4","13","5","/","+"]` → `6`.

**✓ Done when:** Both test cases return correct integer results. Note: division truncates toward zero.

---

### 💀 #38 — BOSS: Daily Temperatures
**Time:** ~40 min | **Concept:** monotonic stack for "next warmer day" pattern

- Write `daily_temperatures(temps: list[int]) -> list[int]` — for each day, how many days until a warmer temperature? 0 if no warmer day comes.
- Use a monotonic stack of indices; pop when a warmer day is found.
- Test: `[73,74,75,71,69,72,76,73]` → `[1,1,4,2,1,1,0,0]`.

**✓ Done when:** Output matches exactly. O(n) — explain in a comment why each index is pushed and popped at most once.

---

# ARC 6 — Recursion
## 8 Exercises | Base Case → Call Stack → Tree Recursion → Divide & Conquer

---

### 🟢 #39 — Factorial
**Time:** ~8 min | **Concept:** base case + one recursive call

- Write `factorial(n: int) -> int` recursively.
- Add a `print(f"computing factorial({n})")` before the return to see the call stack unwind.
- Test: `factorial(5)` → `120`. Count the print lines — confirm exactly 5 calls.

**✓ Done when:** Returns 120; exactly 5 "computing..." lines print.

---

### 🟢 #40 — Sum of Digits
**Time:** ~8 min | **Concept:** reducing a problem by one digit per call

- Write `sum_digits(n: int) -> int` — recursively sums all digits of a non-negative integer.
- Base case: `n < 10`.
- Test: `sum_digits(1234)` → `10`; `sum_digits(9999)` → `36`.

**✓ Done when:** Both test cases return correct sums. State the time complexity in a comment.

---

### 🟡 #41 — Power Function (O(log n))
**Time:** ~15 min | **Concept:** halving the problem at each even exponent

- Write `power(base: int, exp: int) -> int` recursively using fast exponentiation.
- Even exp: `half = power(base, exp//2); return half * half`.
- Odd exp: `return base * power(base, exp - 1)`.
- Add a call counter to confirm it makes O(log n) calls, not O(n).
- Test: `power(2, 10)` → `1024`; `power(3, 5)` → `243`.

**✓ Done when:** Both correct; counter shows ≤ 10 calls for `power(2, 10)`.

---

### 🟡 #42 — Flatten Nested List
**Time:** ~15 min | **Concept:** recursion on unknown-depth structure

- Write `flatten(nested: list) -> list` — flattens any depth of nesting.
- For each item: if it's a list, recurse; otherwise append directly.
- Test: `flatten([1, [2, [3, 4]], 5, [6]])` → `[1, 2, 3, 4, 5, 6]`.

**✓ Done when:** Returns `[1, 2, 3, 4, 5, 6]`. Works on arbitrary nesting depth.

---

### 🟠 #43 — Count Nodes in Nested Dict
**Time:** ~15 min | **Concept:** recursion on tree-like dict structure

- Write `count_nodes(tree: dict) -> int` — counts total nodes in a tree where each dict has `"value"` and `"children": [...]`.
- Each child is the same structure.
- Test tree:
  ```python
  tree = {"value": "root", "children": [
      {"value": "a", "children": [
          {"value": "c", "children": []}
      ]},
      {"value": "b", "children": []}
  ]}
  ```
- Expected: `count_nodes(tree)` → `4`.

**✓ Done when:** Returns `4` for the test tree.

---

### 🟠 #44 — Tower of Hanoi
**Time:** ~20 min | **Concept:** three-peg recursion, 2^n - 1 moves

- Write `hanoi(n: int, source: str, target: str, auxiliary: str)` — prints each move to solve Tower of Hanoi for `n` disks.
- Base case: n == 1 → print the single move.
- Test: `hanoi(3, "A", "C", "B")` — verify exactly 7 moves are printed (2³-1).
- Add a counter; confirm the count matches `2^n - 1`.

**✓ Done when:** 7 moves print for n=3; count is exactly 7.

---

### 🔴 #45 — Binary Search (Recursive)
**Time:** ~15 min | **Concept:** divide-and-conquer search via recursion

- Write `binary_search_recursive(arr: list, target: int, left: int, right: int) -> int` — returns index or -1.
- The recursive call either goes left half or right half, never both.
- Test: `binary_search_recursive([1,3,5,7,9,11], 7, 0, 5)` → `3`.
- Add call count; confirm it's at most ⌈log₂(n)⌉ + 1 calls.

**✓ Done when:** Returns index `3`; call count ≤ 4 for a 6-element array.

---

### 💀 #46 — BOSS: Merge Sort (Recursive)
**Time:** ~40 min | **Concept:** divide-and-conquer, O(n log n) guaranteed

- Implement `merge_sort(arr: list[int]) -> list[int]` from scratch.
- Implement `merge(left, right)` separately — O(n) merge of two sorted lists.
- Add `depth` tracking to `merge_sort`: print `f"Depth {depth}: splitting {arr}"` at each recursive call.
- Test: `merge_sort([38, 27, 43, 3, 9, 82, 10])` → `[3, 9, 10, 27, 38, 43, 82]`.
- Count total `merge` calls — confirm it matches `n-1` for n elements.

**✓ Done when:** Sorted output correct; depth trace visible; merge call count is `n-1 = 6` for 7 elements.

---

# ARC 7 — Binary Search
## 8 Exercises | Classic → Find First/Last → Condition-Based → Answer Space

---

### 🟢 #47 — Classic Binary Search
**Time:** ~10 min | **Concept:** eliminate half the search space each step

- Write `binary_search(arr: list[int], target: int) -> int` — returns index or -1.
- Add a `steps` counter; print `f"Step {steps}: left={left}, right={right}, mid={mid}, arr[mid]={arr[mid]}"`.
- Test: `binary_search([1,5,8,12,18,23,35,42], 18)` — trace all steps; confirm 3 steps total.

**✓ Done when:** Returns index `4` in exactly 3 steps.

---

### 🟢 #48 — Find First and Last Position
**Time:** ~15 min | **Concept:** biasing the search direction after finding a match

- Write `find_first(arr: list[int], target: int) -> int` — when target found, keep searching LEFT (`right = mid - 1`).
- Write `find_last(arr: list[int], target: int) -> int` — when target found, keep searching RIGHT (`left = mid + 1`).
- Test: `arr = [1, 2, 2, 2, 3, 4]` → `find_first(arr, 2)` → `1`; `find_last(arr, 2)` → `3`.

**✓ Done when:** Both functions return correct boundary indices.

---

### 🟡 #49 — My `bisect_left`
**Time:** ~15 min | **Concept:** find insertion point, not exact match

- Write `my_bisect_left(arr: list[int], x: int) -> int` — returns the leftmost index where `x` can be inserted to keep `arr` sorted.
- If `x` already exists, return the index of its first occurrence.
- Test against `bisect.bisect_left` on 5 different inputs — outputs must match exactly.

**✓ Done when:** Your implementation matches `bisect.bisect_left` on all 5 test cases.

---

### 🟡 #50 — Search in Rotated Sorted Array
**Time:** ~20 min | **Concept:** binary search on a non-uniformly sorted array

- Write `search_rotated(arr: list[int], target: int) -> int` — finds target in a rotated sorted array (e.g., `[4,5,6,7,0,1,2]`).
- At each step, determine which half is sorted; check if target is in that half; narrow accordingly.
- Test: `search_rotated([4,5,6,7,0,1,2], 0)` → `4`; `search_rotated([4,5,6,7,0,1,2], 3)` → `-1`.

**✓ Done when:** Both test cases return correct results. O(log n).
> 💡 If `arr[left] <= arr[mid]`, the left half is sorted. Check if target is in that range.

---

### 🟠 #51 — Condition-Based: Minimum Speed
**Time:** ~20 min | **Concept:** binary search on the answer space

- Write `min_speed(distances: list[float], hours: float) -> int` — minimum integer speed to travel all distances in `hours` time.
- Each distance takes `ceil(dist / speed)` hours (except the last, which takes exactly `dist / speed`).
- Binary search speed from 1 to `max(distances)`.
- Test: `min_speed([1, 3, 2], 6)` → `1`; `min_speed([1, 3, 2], 2.7)` → `3`.

**✓ Done when:** Both test cases return correct minimum speeds.

---

### 🟠 #52 — Koko Eating Bananas
**Time:** ~20 min | **Concept:** condition-based binary search with a `can_finish` helper

- Write `koko(piles: list[int], h: int) -> int` — minimum eating speed k so Koko finishes all piles in h hours.
- Each pile takes `ceil(pile / k)` hours.
- Binary search k from 1 to `max(piles)`.
- Test: `koko([3,6,7,11], 8)` → `4`; `koko([30,11,23,4,20], 5)` → `30`.

**✓ Done when:** Both test cases return correct minimum k.

---

### 🔴 #53 — Capacity to Ship Packages
**Time:** ~20 min | **Concept:** condition-based binary search, greedy feasibility check

- Write `ship_capacity(weights: list[int], days: int) -> int` — minimum ship capacity to ship all packages in `days` days (packages must stay in order).
- Feasibility check: greedily pack as many as fit in the current day; count days needed.
- Binary search capacity from `max(weights)` to `sum(weights)`.
- Test: `ship_capacity([1,2,3,4,5,6,7,8,9,10], 5)` → `15`.

**✓ Done when:** Returns `15`. O(n log(sum-max)) time.

---

### 💀 #54 — BOSS: Split Array Largest Sum
**Time:** ~45 min | **Concept:** hardest form of binary search on answer space

- Write `split_array(nums: list[int], k: int) -> int` — split `nums` into exactly `k` subarrays to minimise the maximum subarray sum.
- Feasibility: given a maximum allowed sum, greedily count how many subarrays you need.
- Binary search the answer from `max(nums)` (smallest possible maximum) to `sum(nums)`.
- Test: `split_array([7,2,5,10,8], 2)` → `18`; `split_array([1,2,3,4,5], 2)` → `9`.

**✓ Done when:** Both test cases return correct minimised maximums. Write a comment explaining why this is binary search on the answer space, not on an array.

---

# ARC 8 — Trees & Binary Search Trees
## 8 Exercises | Build → Traverse → Height → Balance → BST → LCA

---

### 🟢 #55 — Build a Tree + Preorder Traversal
**Time:** ~10 min | **Concept:** TreeNode construction, recursive preorder

- Write `TreeNode` with `value`, `left`, `right`.
- Manually build:
  ```
       1
      / \
     2   3
    / \
   4   5
  ```
- Write `preorder(node)` — prints Root → Left → Right.

**✓ Done when:** `preorder(root)` prints `1 2 4 5 3`.

---

### 🟢 #56 — Inorder and Postorder
**Time:** ~10 min | **Concept:** the three DFS orderings

- Using the same tree from #55, write `inorder(node)` and `postorder(node)`.
- Print results of all three traversals side by side.

**✓ Done when:** Inorder prints `4 2 5 1 3`; postorder prints `4 5 2 3 1`.

---

### 🟡 #57 — Level-Order (BFS)
**Time:** ~15 min | **Concept:** queue-driven level-by-level output

- Write `level_order(root: TreeNode) -> list[list[int]]` — returns values grouped by level.
- Use a deque; track level size with `len(queue)` at the start of each level.
- Test on the same tree.

**✓ Done when:** Returns `[[1], [2, 3], [4, 5]]`.

---

### 🟡 #58 — Height and Node Count
**Time:** ~12 min | **Concept:** classic recursive tree problems

- Write `height(node: TreeNode) -> int` — max depth from node to any leaf. Empty tree = 0.
- Write `count_nodes(node: TreeNode) -> int` — total number of nodes.
- Test on the tree from #55: height → `3`; count → `5`.

**✓ Done when:** Both return correct values. State O(n) for each in a comment.

---

### 🟠 #59 — Is Balanced
**Time:** ~18 min | **Concept:** single-pass balance check with -1 sentinel

- Write `is_balanced(root: TreeNode) -> bool` — returns True if every node's left and right subtrees differ in height by at most 1.
- Use an inner function that returns -1 when imbalance is detected (avoiding a second pass).
- Test: balanced tree → `True`; manually build a skewed tree → `False`.

**✓ Done when:** Balanced tree returns `True`; skewed chain of 4 nodes returns `False`. O(n) — no redundant height calls.

---

### 🟠 #60 — BST Insert and Search
**Time:** ~18 min | **Concept:** BST invariant — left < node < right

- Write `class BST` with `insert(value)` and `search(value) -> bool`.
- Insert `[15, 8, 22, 4, 12, 18, 25]`.
- Call `inorder_sorted()` — should return `[4, 8, 12, 15, 18, 22, 25]`.
- Search for `12` → `True`; search for `99` → `False`.

**✓ Done when:** Inorder output is sorted; both searches return correct booleans.

---

### 🔴 #61 — Lowest Common Ancestor (BST)
**Time:** ~20 min | **Concept:** using BST property to find LCA in O(log n)

- Write `lca(root: TreeNode, p: int, q: int) -> int` — finds lowest common ancestor of nodes with values p and q in a BST.
- If both p and q are less than root → go left. Both greater → go right. Otherwise → root is LCA.
- Test with the BST from #60: `lca(root, 4, 12)` → `8`; `lca(root, 8, 25)` → `15`.

**✓ Done when:** Both LCA calls return correct ancestor values.

---

### 💀 #62 — BOSS: Serialize and Deserialize a Binary Tree
**Time:** ~45 min | **Concept:** convert a tree to a string and back without losing structure

- Write `serialize(root: TreeNode) -> str` — converts the tree to a string (e.g., preorder with "null" for missing children: `"1,2,4,null,null,5,null,null,3,null,null"`).
- Write `deserialize(data: str) -> TreeNode` — reconstructs the tree from the string.
- Test: serialize → get a string → deserialize → serialize again → same string.

**✓ Done when:** `serialize(deserialize(serialize(tree)))` returns the same string as the first `serialize(tree)`.

---

# ARC 9 — Heaps & Priority Queues
## 8 Exercises | heapq → Max-Heap → Top-K → Two-Heap Median

---

### 🟢 #63 — heapq Basics
**Time:** ~10 min | **Concept:** push, pop, peek on a Python min-heap

- Start with `[15, 8, 22, 4, 12, 18, 25]`.
- `heapq.heapify()` — print the resulting list. Note: it's heap-ordered, not sorted.
- Push `6` with `heappush`. Pop minimum twice. Peek at current minimum.
- Print after each operation.

**✓ Done when:** Each pop returns the current minimum; heap order maintained throughout.

---

### 🟢 #64 — Max-Heap via Negation
**Time:** ~10 min | **Concept:** negating values to simulate a max-heap

- Build a max-heap from `[5, 1, 8, 3, 9, 2]` by negating all values before pushing.
- Pop three times, negating results back.
- Confirm pops return `9, 8, 5` (the three largest).

**✓ Done when:** First three pops yield `9, 8, 5` in that order.

---

### 🟡 #65 — Priority Queue with Tuples
**Time:** ~12 min | **Concept:** `(priority, item)` tuples for custom ordering

- Push 5 tasks as `(priority, task_name)` tuples onto a heap.
- Pop all 5 in priority order (lowest number = highest priority).
- Test: priorities 3, 1, 4, 1, 5 → pops should respect numeric order; for ties, alphabetical by task name.

**✓ Done when:** Tasks print in correct priority order with ties broken alphabetically.

---

### 🟡 #66 — K Largest Elements
**Time:** ~15 min | **Concept:** min-heap of size k; evict when overflow

- Write `k_largest(nums: list[int], k: int) -> list[int]` — returns k largest values.
- Maintain a MIN-heap of max size k; pop smallest when size exceeds k.
- What remains is the k largest.
- Test: `k_largest([3,1,8,22,5,14,2], 3)` → `[8, 14, 22]` (any order).

**✓ Done when:** Returns exactly the 3 largest values. O(n log k) time, O(k) space.

---

### 🟠 #67 — K Closest Points to Origin
**Time:** ~18 min | **Concept:** custom key in heap using distance²

- Write `k_closest(points: list[tuple], k: int) -> list[tuple]` — finds k points closest to `(0, 0)`.
- Use a max-heap of size k with `(-distance², point)` tuples; evict when size exceeds k.
- Test: `k_closest([(1,3),(-2,2),(5,8),(0,1)], 2)` → `[(-2,2), (0,1)]` (any order).

**✓ Done when:** Returns the 2 closest points. Distance² avoids floating-point sqrt.

---

### 🟠 #68 — Merge K Sorted Lists
**Time:** ~20 min | **Concept:** heap as a merge cursor across multiple lists

- Write `merge_k_sorted(lists: list[list[int]]) -> list[int]` — merges k sorted lists into one.
- Use a min-heap initialised with the first element of each list as `(value, list_index, element_index)`.
- Pop minimum, push next element from that list; repeat until heap empty.
- Test: `merge_k_sorted([[1,4,7],[2,5,8],[3,6,9]])` → `[1,2,3,4,5,6,7,8,9]`.

**✓ Done when:** Returns fully merged sorted list. O(n log k) where n = total elements.

---

### 🔴 #69 — Find Median from a Data Stream
**Time:** ~25 min | **Concept:** two-heap balance — max-heap left, min-heap right

- Write `class MedianFinder:` with `add_num(num)` and `find_median() -> float`.
- Maintain `low` (max-heap, negated) and `high` (min-heap).
- After each add: rebalance so `|len(low) - len(high)| <= 1`.
- Median: if equal sizes, average of tops; otherwise top of larger half.
- Test: add 1, 2; median → 1.5; add 3; median → 2.0.

**✓ Done when:** Both medians correct after each addition.

---

### 💀 #70 — BOSS: Task Scheduler
**Time:** ~45 min | **Concept:** greedy + max-heap for CPU scheduling

- Write `task_scheduler(tasks: list[str], n: int) -> int` — given CPU tasks (letters) and cooldown `n`, find minimum time to complete all tasks.
- Strategy: always pick the most frequent remaining task. If cooldown prevents it, insert an idle.
- Use a max-heap (negated counts) and a cooldown queue of `(next_available_time, count)`.
- Test: `task_scheduler(["A","A","A","B","B","B"], 2)` → `8`; `task_scheduler(["A","A","A","B","B","B"], 0)` → `6`.

**✓ Done when:** Both test cases return correct minimum times.

---

# ARC 10 — Sorting
## 8 Exercises | O(n²) → O(n log n) → O(n+k) → Hybrid Problems

---

### 🟢 #71 — Bubble Sort with Early Exit
**Time:** ~10 min | **Concept:** adjacent swaps, stable, O(n) best case

- Implement `bubble_sort(arr: list[int]) -> list[int]` with the `swapped` flag for early exit.
- Count total swaps.
- Test on `[64,34,25,12,22,11,90]` — print swap count.
- Also test on `[1,2,3,4,5]` — confirm zero swaps and only one pass (early exit working).

**✓ Done when:** Sorted list correct; nearly-sorted input exits in O(n).

---

### 🟢 #72 — Insertion Sort
**Time:** ~10 min | **Concept:** sorted prefix growth, efficient on nearly-sorted data

- Implement `insertion_sort(arr: list[int]) -> list[int]`.
- Add a `comparisons` counter inside the while loop.
- Test `[12,11,13,5,6]` — print final sorted array and comparison count.
- Explain in a comment why nearly-sorted input gives fewer comparisons than random input.

**✓ Done when:** Returns `[5,6,11,12,13]`; comparison count printed and commented.

---

### 🟡 #73 — Merge Sort (Iterative Trace)
**Time:** ~20 min | **Concept:** divide-and-conquer, guaranteed O(n log n)

- Implement `merge_sort(arr)` and `merge(left, right)` from scratch.
- Print `f"Merging {left} and {right} → {result}"` inside `merge`.
- Test: `[38, 27, 43, 3, 9, 82, 10]` — read the full merge trace to understand the bottom-up build.

**✓ Done when:** Sorted output `[3,9,10,27,38,43,82]` correct; trace shows all 6 merge operations.

---

### 🟡 #74 — Quick Sort with Random Pivot
**Time:** ~20 min | **Concept:** partition-based sort, O(n log n) average

- Implement `quick_sort(arr, lo, hi)` and `partition(arr, lo, hi)`.
- Use a randomised pivot: swap a random index with `arr[hi]` before partitioning.
- Test on sorted input `[1,2,3,4,5]` — confirm it still sorts correctly (random pivot avoids worst case).

**✓ Done when:** Sorted input and random input both produce correct output.

---

### 🟠 #75 — Counting Sort
**Time:** ~15 min | **Concept:** non-comparison sort, O(n+k)

- Implement `counting_sort(arr: list[int]) -> list[int]`.
- Test: `[4,2,2,8,3,3,1]` → `[1,2,2,3,3,4,8]`.
- Also test on negative numbers — handle by shifting with `min_val`.
- State the time and space complexity and the restriction (integers only, bounded range).

**✓ Done when:** Handles both positive-only and mixed-sign inputs correctly.

---

### 🟠 #76 — Sort Custom Objects
**Time:** ~12 min | **Concept:** `key=` parameter, lambda, multiple criteria

- Given `records = [{"name": "Charlie", "score": 85}, {"name": "Alice", "score": 92}, {"name": "Bob", "score": 85}]`:
- Sort by score descending; ties broken by name ascending.
- Use `sorted()` with a `key=` lambda and `reverse` — NOT implementing a sort yourself.

**✓ Done when:** Order is Alice (92), Bob (85), Charlie (85). One line of sort code.

---

### 🔴 #77 — Sort Colors (Dutch National Flag)
**Time:** ~20 min | **Concept:** three-way partition with O(1) space

- Write `sort_colors(arr: list[int])` — given an array with only 0s, 1s, and 2s, sort in place in one pass.
- Use three pointers: `low`, `mid`, `high`.
- Test: `[2,0,2,1,1,0]` → `[0,0,1,1,2,2]`.

**✓ Done when:** Array sorted in one pass, O(n) time, O(1) space — no counting, no comparison sort.
> 💡 `low` tracks where next 0 goes, `high` where next 2 goes, `mid` is the current element.

---

### 💀 #78 — BOSS: Merge K Sorted Arrays (Heap + Sort Comparison)
**Time:** ~45 min | **Concept:** comparing approaches, understanding trade-offs

You have `k = 5` sorted arrays, each of length `n = 200` (generate with `sorted(random.sample(range(1000), 200))`):
- Approach A: concatenate all arrays, then `sorted()` — time it.
- Approach B: use a min-heap to merge (from Arc 9 #68) — time it.
- Approach C: successive `merge(a, b)` (2-way merge) — time it.
- Print all three times and the final element counts to confirm correctness.
- In a comment: which is theoretically fastest? Does your timing agree? Explain any discrepancy.

**✓ Done when:** All three produce the same sorted output; timing printed; explanation written.

---

# ARC 11 — Graphs
## 8 Exercises | Representations → DFS → BFS → Cycle → Topology

---

### 🟢 #79 — Build All Three Representations
**Time:** ~12 min | **Concept:** edge list, adjacency matrix, adjacency list

Using this graph: nodes `{A,B,C,D}`, edges `A-B, A-C, B-D, C-D`:
- Build it as an edge list.
- Build it as an adjacency matrix (use a dict-of-dicts or 2D list with index mapping).
- Build it as an adjacency list (dict of lists).
- For each: answer "is there an edge between B and C?" and note the complexity.

**✓ Done when:** All three representations built; B-C query returns `False` from each with correct complexity noted.

---

### 🟢 #80 — DFS Recursive
**Time:** ~12 min | **Concept:** depth-first traversal, visited set

- Write `dfs(graph: dict, node: str, visited: set = None) -> list` — returns nodes in DFS order.
- Add `print(f"Visiting {node}")` inside to see traversal order.
- Test on: `{"A":["B","C"],"B":["D"],"C":["D","E"],"D":[],"E":[]}` from start `"A"`.

**✓ Done when:** All 5 nodes visited exactly once; deep nodes visited before wide ones.

---

### 🟡 #81 — BFS with Level Tracking
**Time:** ~15 min | **Concept:** queue-based traversal, shortest path distances

- Write `bfs_distances(graph: dict, start: str) -> dict[str, int]` — returns the minimum number of edges from `start` to every reachable node.
- Use a deque; distance to start = 0; each neighbour = parent_dist + 1.
- Test: `bfs_distances(graph_from_79, "A")` → `{"A":0,"B":1,"C":1,"D":2,"E":2}`.

**✓ Done when:** All distances match expected. O(V+E).

---

### 🟡 #82 — Has Path (DFS)
**Time:** ~12 min | **Concept:** reachability check

- Write `has_path(graph: dict, start: str, end: str) -> bool` — returns True if any path exists from start to end.
- Handle cycles with a `visited` set.
- Test: in the graph from #79, `has_path(graph, "A", "E")` → `True`; `has_path(graph, "D", "A")` → `False` (directed graph).

**✓ Done when:** Both return correct booleans. Directed vs undirected distinction noted in a comment.

---

### 🟠 #83 — Count Connected Components
**Time:** ~18 min | **Concept:** outer loop over all nodes, inner DFS marks the component

- Write `count_components(graph: dict) -> int` — counts connected components in an undirected graph.
- Loop over all nodes; if not visited, run DFS and increment component count.
- Test graph: `{"A":["B"],"B":["A"],"C":["D"],"D":["C"],"E":[]}` → `3` components.

**✓ Done when:** Returns `3`. Works for graphs with isolated nodes.

---

### 🟠 #84 — Cycle Detection (Directed Graph)
**Time:** ~20 min | **Concept:** DFS with rec_stack to catch back edges

- Write `has_cycle(graph: dict) -> bool` — detects a cycle in a directed graph.
- Use `visited` and `rec_stack` (nodes currently on the recursion path).
- If a neighbour is already in `rec_stack` → back edge → cycle.
- Test: graph with cycle `A→B→C→A` → `True`; DAG `A→B→C` → `False`.

**✓ Done when:** Both test cases return correct booleans. Note: `rec_stack` is not the same as `visited`.

---

### 🔴 #85 — Topological Sort
**Time:** ~20 min | **Concept:** DFS post-order on a DAG

- Write `topological_sort(graph: dict) -> list[str]` — returns nodes in topological order (all dependencies before dependents).
- DFS: add node to a stack AFTER recursing on all its neighbours.
- Reverse the stack at the end.
- Test: course prerequisites graph `{"A":[],"B":["A"],"C":["A"],"D":["B","C"]}` → valid order where `A` comes first and `D` comes last.

**✓ Done when:** `A` is first, `D` is last in the output; any valid order between is accepted.

---

### 💀 #86 — BOSS: BFS Shortest Path with Reconstruction
**Time:** ~45 min | **Concept:** path tracking in BFS, not just distances

- Write `shortest_path(graph: dict, start: str, end: str) -> list[str] | None` — returns the actual path (list of nodes) of minimum length, or `None` if no path.
- Track paths directly in the queue (queue of lists), OR track a `parent` dict and reconstruct.
- Build a larger test graph (6+ nodes, some dead ends).
- Test: find path from node furthest from start; also test an unreachable node.

**✓ Done when:** Returns correct path list for reachable node; `None` for unreachable. O(V+E).

---

# ARC 12 — Two Pointers
## 8 Exercises | Converging → Fast/Slow → Read/Write → Classic Problems

---

### 🟢 #87 — Two Sum (Sorted Array)
**Time:** ~10 min | **Concept:** converging pointers on sorted data

- Write `two_sum_sorted(arr: list[int], target: int) -> tuple[int, int]` — returns indices of pair summing to target. Array is sorted.
- Start `left=0`, `right=len-1`; move based on whether sum is too small or too large.
- Test: `two_sum_sorted([2,7,11,15], 9)` → `(0,1)`; `two_sum_sorted([2,3,4], 6)` → `(0,2)`.

**✓ Done when:** Both return correct index pairs. O(n) time, O(1) space.

---

### 🟢 #88 — Palindrome Check
**Time:** ~8 min | **Concept:** converging from both ends

- Write `is_palindrome(s: str) -> bool` — O(n) time, O(1) space — no slicing, no reversal.
- Left pointer starts at 0, right at end; move inward comparing characters.
- Test: `"racecar"` → `True`; `"hello"` → `False`; `"a"` → `True`; `""` → `True`.

**✓ Done when:** All four test cases correct. No reversed string created.

---

### 🟡 #89 — Remove Duplicates In-Place
**Time:** ~12 min | **Concept:** read/write pointer pattern on sorted array

- Write `remove_duplicates(arr: list[int]) -> int` — removes duplicates from a sorted array in place; returns new length.
- `write=1`; `read` scans from 1; when `arr[read] != arr[read-1]`, copy to `write`.
- Test: `arr=[1,1,2,3,3,3,4]` → returns `4`; `arr[:4]` is `[1,2,3,4]`.

**✓ Done when:** Returns `4`; first 4 elements are `[1,2,3,4]`. O(n) time, O(1) space.

---

### 🟡 #90 — Container with Most Water
**Time:** ~15 min | **Concept:** converging pointers, always move shorter wall

- Write `max_water(heights: list[int]) -> int` — given wall heights, find two walls forming the container with maximum water.
- Always move the pointer at the shorter wall (the bottleneck).
- Test: `max_water([1,8,6,2,5,4,8,3,7])` → `49`.

**✓ Done when:** Returns `49`. Write a comment explaining WHY moving the shorter wall is always optimal.

---

### 🟠 #91 — Three Sum
**Time:** ~20 min | **Concept:** sort + two-pointer for the inner pair

- Write `three_sum(nums: list[int]) -> list[list[int]]` — finds all unique triplets summing to 0.
- Sort first. Fix one element; use two pointers for the remaining pair.
- Skip duplicates at each level to avoid duplicate triplets in output.
- Test: `three_sum([-1,0,1,2,-1,-4])` → `[[-1,-1,2],[-1,0,1]]`.

**✓ Done when:** Returns exactly those 2 triplets (order within and between may vary). O(n²).

---

### 🟠 #92 — Move Zeros
**Time:** ~12 min | **Concept:** read/write pointer, non-zero elements moved forward

- Write `move_zeros(arr: list[int])` — moves all zeros to the end, preserving relative order of non-zeros.
- In place, O(n) time, O(1) space.
- Test: `arr=[0,1,0,3,12]` → `arr` becomes `[1,3,12,0,0]`.

**✓ Done when:** Non-zero elements maintain order; all zeros at end. Single pass.

---

### 🔴 #93 — Valid Palindrome II
**Time:** ~20 min | **Concept:** two pointers with one allowed mismatch

- Write `valid_palindrome_ii(s: str) -> bool` — returns True if you can remove at most one character to make it a palindrome.
- When `s[left] != s[right]`: try skipping left character OR right character; check if either remaining substring is a palindrome.
- Test: `"abca"` → `True` (remove 'b' or 'c'); `"abc"` → `False`.

**✓ Done when:** Both test cases correct. Write a helper `is_palindrome(s, l, r)` for the sub-check.

---

### 💀 #94 — BOSS: Trapping Rain Water
**Time:** ~45 min | **Concept:** two-pointer tracking of max heights from each side

- Write `trap(height: list[int]) -> int` — given an elevation map, compute total water trapped.
- Track `left_max` and `right_max`; process the side with the shorter max (it determines water level).
- Naive O(n²): for each bar, find max left and max right — implement first to verify logic.
- Optimal O(n), O(1): converging pointers with running maxes — then implement this.
- Test: `trap([0,1,0,2,1,0,1,3,2,1,2,1])` → `6`.

**✓ Done when:** Both versions return `6`; O(n) version uses no extra array. Comment explains why the pointer with smaller max processes first.

---

# ARC 13 — Sliding Window
## 6 Exercises | Fixed → Variable → Prefix Sum Variant

---

### 🟢 #95 — Max Sum Fixed Window
**Time:** ~10 min | **Concept:** add new element, remove old element, track maximum

- Write `max_sum_fixed(arr: list[int], k: int) -> int` — maximum sum of any contiguous subarray of exactly length k.
- Build first window with `sum(arr[:k])`; slide by adding `arr[i]` and subtracting `arr[i-k]`.
- Test: `max_sum_fixed([2,1,5,1,3,2], 3)` → `9`; `max_sum_fixed([2,3,4,1,5], 2)` → `7`.

**✓ Done when:** Both test cases correct. O(n) — no re-summing the window each step.

---

### 🟡 #96 — Longest Substring No Repeat
**Time:** ~15 min | **Concept:** variable window with a character set

- Write `longest_no_repeat(s: str) -> int` — longest substring without repeating characters.
- Use a set for the current window; shrink from left when a duplicate enters from the right.
- Test: `"abcabcbb"` → `3`; `"bbbbb"` → `1`; `"pwwkew"` → `3`.

**✓ Done when:** All three test cases return correct lengths. O(n).

---

### 🟡 #97 — Max Consecutive Ones with K Flips
**Time:** ~18 min | **Concept:** variable window, track zeros inside window

- Write `longest_ones(arr: list[int], k: int) -> int` — given binary array, find longest subarray of 1s if you can flip at most k zeros.
- Track `zero_count` in the window; shrink from left when `zero_count > k`.
- Test: `longest_ones([1,1,0,0,1,1,1,0,1], 2)` → `7`; `longest_ones([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3)` → `10`.

**✓ Done when:** Both test cases return correct maximum lengths.

---

### 🟠 #98 — Minimum Window Substring
**Time:** ~25 min | **Concept:** variable window with two frequency dicts

- Write `min_window(s: str, t: str) -> str` — smallest substring of `s` containing all characters of `t`.
- Track `need` (freq of t), `have` (freq in current window), `formed` (count of satisfied chars).
- Expand right until all chars satisfied; shrink left to minimise; record minimum.
- Test: `min_window("ADOBECODEBANC", "ABC")` → `"BANC"`.

**✓ Done when:** Returns `"BANC"`. O(n). Empty string if no valid window exists.

---

### 🔴 #99 — Count Subarrays with Sum = K
**Time:** ~20 min | **Concept:** prefix sum + hash map (sliding window variant)

- Write `count_subarrays(nums: list[int], k: int) -> int` — count contiguous subarrays summing to exactly k.
- Maintain a running `prefix_sum`; if `prefix_sum - k` seen before, those subarrays sum to k.
- Use `prefix_counts = {0: 1}` to handle subarrays starting at index 0.
- Test: `count_subarrays([1,1,1], 2)` → `2`; `count_subarrays([1,2,3], 3)` → `2`.

**✓ Done when:** Both test cases return correct counts. Explain in a comment why `prefix_sum - k` being in the map means a subarray sums to k.

---

### 💀 #100 — BOSS: Longest Substring with K Distinct Characters
**Time:** ~40 min | **Concept:** variable window with a frequency dict controlling window validity

- Write `longest_k_distinct(s: str, k: int) -> int` — longest substring with at most k distinct characters.
- Track char frequencies in the window; when distinct chars exceed k, shrink from left until valid.
- Test: `longest_k_distinct("araaci", 2)` → `4`; `longest_k_distinct("cbbebi", 3)` → `5`.

**✓ Done when:** Both test cases return correct lengths. O(n) — each char enters and leaves the window at most once.

---

# ARC 14 — Backtracking
## 8 Exercises | Subsets → Permutations → Pruning → N-Queens

---

### 🟢 #101 — All Subsets
**Time:** ~12 min | **Concept:** choose/explore/unchoose template

- Write `subsets(nums: list[int]) -> list[list[int]]` — generates all 2ⁿ subsets.
- Use backtracking: at each index, choose to include or skip; record a copy of `current` at every call.
- Test: `subsets([1,2,3])` → 8 subsets including `[]` and `[1,2,3]`.

**✓ Done when:** Returns exactly 8 subsets; output includes both `[]` and `[1,2,3]`.

---

### 🟢 #102 — All Permutations
**Time:** ~12 min | **Concept:** remaining elements as choices at each step

- Write `permutations(nums: list[int]) -> list[list[int]]` — generates all n! permutations.
- At each call: loop over remaining elements, choose one, recurse with it removed from remaining.
- Test: `permutations([1,2,3])` → 6 permutations.

**✓ Done when:** Returns exactly 6 permutations; all are present with no duplicates.

---

### 🟡 #103 — Combinations (n Choose k)
**Time:** ~15 min | **Concept:** start index prevents re-picking earlier elements

- Write `combinations(n: int, k: int) -> list[list[int]]` — all k-element combinations from 1 to n.
- Pass `start` index to only pick numbers ≥ start (avoids duplicates).
- Test: `combinations(4, 2)` → `[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]` — exactly 6.

**✓ Done when:** Returns exactly those 6 combinations in any order.

---

### 🟡 #104 — Combination Sum (Reuse Allowed)
**Time:** ~15 min | **Concept:** same index allowed in recursive call + pruning

- Write `combination_sum(candidates: list[int], target: int) -> list[list[int]]`.
- Candidates may be reused; sort first for pruning.
- Prune: if `candidate > remaining`, break (all further candidates are also too large).
- Test: `combination_sum([2,3,6,7], 7)` → `[[2,2,3],[7]]`.

**✓ Done when:** Returns exactly those 2 combinations.

---

### 🟠 #105 — Generate Valid Parentheses
**Time:** ~18 min | **Concept:** constraint-guided backtracking, no explicit undo

- Write `generate_parentheses(n: int) -> list[str]` — all valid combinations of n pairs.
- Rules: add `(` if open_count < n; add `)` if close_count < open_count.
- No explicit undo needed (strings are immutable — pass `current + "("` not a mutable list).
- Test: `generate_parentheses(3)` → exactly 5 strings.

**✓ Done when:** Returns all 5 valid combinations for n=3.

---

### 🟠 #106 — Combination Sum II (No Reuse)
**Time:** ~20 min | **Concept:** skip duplicates at the same level to avoid duplicate results

- Write `combination_sum_ii(candidates: list[int], target: int) -> list[list[int]]` — each candidate may be used at most once; no duplicate result sets.
- Sort first. Skip `candidates[i]` if `i > start and candidates[i] == candidates[i-1]`.
- Test: `combination_sum_ii([10,1,2,7,6,1,5], 8)` → `[[1,1,6],[1,2,5],[1,7],[2,6]]`.

**✓ Done when:** Returns exactly those 4 unique combinations. No duplicate result sets.

---

### 🔴 #107 — Word Search in a Grid
**Time:** ~25 min | **Concept:** DFS backtracking on a 2D grid

- Write `word_search(board: list[list[str]], word: str) -> bool` — returns True if word exists in the grid following adjacent (up/down/left/right) cells, each cell used at most once.
- DFS from each cell; mark visited by temporarily replacing with `"#"`; restore after.
- Test:
  ```
  board = [["A","B","C","E"],
           ["S","F","C","S"],
           ["A","D","E","E"]]
  word_search(board, "ABCCED") → True
  word_search(board, "SEE")    → True
  word_search(board, "ABCB")   → False
  ```

**✓ Done when:** All three test cases return correct booleans.

---

### 💀 #108 — BOSS: N-Queens
**Time:** ~50 min | **Concept:** the canonical backtracking problem

- Write `n_queens(n: int) -> list[list[str]]` — returns all distinct solutions to placing n queens on an n×n board such that no two queens attack each other.
- Represent each solution as a list of strings (one per row), `"Q"` for queens, `"."` for empty.
- Track `cols`, `diag1` (row-col), `diag2` (row+col) as sets for O(1) conflict checking.
- Test: `len(n_queens(4))` → `2`; `len(n_queens(8))` → `92`.

**✓ Done when:** Returns correct number of solutions for n=4 and n=8.

---

# ARC 15 — Dynamic Programming
## 8 Exercises | Fibonacci → Climbing → Knapsack → Edit Distance

---

### 🟢 #109 — Fibonacci Three Ways
**Time:** ~15 min | **Concept:** naive vs memoised vs tabulated

- Implement `fib_naive(n)`, `fib_memo(n, cache={})`, `fib_bottom_up(n)`.
- Time all three on `n=40` using `time.perf_counter`.
- Print all times; confirm they return the same value.

**✓ Done when:** All three return `102334155`; naive is visibly slowest; memoised and bottom-up are near-instant.

---

### 🟢 #110 — Climbing Stairs
**Time:** ~12 min | **Concept:** DP recurrence from a word problem

- Write `climb_stairs(n: int) -> int` — count distinct ways to climb n stairs (1 or 2 steps at a time).
- Build bottom-up `dp` array; `dp[i] = dp[i-1] + dp[i-2]`.
- Test: `climb_stairs(5)` → `8`; `climb_stairs(10)` → `89`.
- Optimise to O(1) space (only two variables needed).

**✓ Done when:** Both test cases correct; O(1) space version works.

---

### 🟡 #111 — House Robber
**Time:** ~15 min | **Concept:** cannot rob adjacent houses — skip-or-take recurrence

- Write `rob(houses: list[int]) -> int` — maximum money from non-adjacent houses.
- `dp[i] = max(dp[i-1], dp[i-2] + houses[i])`.
- Optimise to O(1) space.
- Test: `rob([1,2,3,1])` → `4`; `rob([2,7,9,3,1])` → `12`.

**✓ Done when:** Both test cases return correct maximums.

---

### 🟡 #112 — Coin Change
**Time:** ~18 min | **Concept:** unbounded knapsack variant, fill table from 0 to amount

- Write `coin_change(coins: list[int], amount: int) -> int` — minimum coins to make amount; -1 if impossible.
- `dp[0] = 0`; for each coin, for each amount from coin to target: `dp[amt] = min(dp[amt], dp[amt-coin] + 1)`.
- Test: `coin_change([1,5,10,25], 41)` → `4`; `coin_change([2], 3)` → `-1`.

**✓ Done when:** Both test cases return correct values. Trace the dp table manually for `amount=11, coins=[1,2,5]`.

---

### 🟠 #113 — 0/1 Knapsack
**Time:** ~20 min | **Concept:** 2D dp table, items can only be used once

- Write `knapsack(weights: list[int], values: list[int], capacity: int) -> int`.
- `dp[i][w]` = max value using first i items with weight limit w.
- For each item: either skip it (`dp[i-1][w]`) or take it if it fits (`dp[i-1][w-weight[i]] + value[i]`).
- Test: `knapsack([2,3,4,5],[3,4,5,6], 5)` → `7`.

**✓ Done when:** Returns `7`. Print the full dp table for the test case.

---

### 🟠 #114 — Longest Common Subsequence
**Time:** ~20 min | **Concept:** 2D dp, matching vs best-of-skip

- Write `lcs(s1: str, s2: str) -> int`.
- If `s1[i-1] == s2[j-1]`: `dp[i][j] = dp[i-1][j-1] + 1`. Else: `max(dp[i-1][j], dp[i][j-1])`.
- Test: `lcs("abcde", "ace")` → `3`; `lcs("abc", "abc")` → `3`; `lcs("abc", "def")` → `0`.

**✓ Done when:** All three test cases return correct lengths.

---

### 🔴 #115 — Longest Increasing Subsequence
**Time:** ~22 min | **Concept:** O(n²) DP or O(n log n) patience sorting

- Write `lis(nums: list[int]) -> int` — length of the longest strictly increasing subsequence.
- O(n²): `dp[i]` = LIS ending at index i; for each j < i where `nums[j] < nums[i]`: `dp[i] = max(dp[i], dp[j]+1)`.
- O(n log n): maintain a `tails` array; binary search for the insertion position of each element.
- Test: `lis([10,9,2,5,3,7,101,18])` → `4`; `lis([0,1,0,3,2,3])` → `4`.

**✓ Done when:** Both approaches return correct lengths on both test cases. Comment the complexity of each.

---

### 💀 #116 — BOSS: Edit Distance (Levenshtein)
**Time:** ~45 min | **Concept:** 2D DP, three operations (insert, delete, replace)

- Write `edit_distance(word1: str, word2: str) -> int` — minimum operations (insert, delete, replace) to transform word1 into word2.
- `dp[i][j]` = edit distance between `word1[:i]` and `word2[:j]`.
- If chars match: `dp[i][j] = dp[i-1][j-1]`. Else: `1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`.
- Test: `edit_distance("horse", "ros")` → `3`; `edit_distance("intention", "execution")` → `5`.
- Print the full DP table for the first test case.

**✓ Done when:** Both test cases return correct values; DP table printed and you can trace the path of operations that achieves the minimum.

---

# ARC 16 — Bit Manipulation
## 8 Exercises | Binary Rep → Bit Tricks → XOR Patterns → Bitmask Subsets

---

### 🟢 #117 — Binary Representation Drill
**Time:** ~10 min | **Concept:** converting between decimal and binary

For each of `[0, 1, 5, 13, 42, 127, 255]`:
- Print `bin(n)`, `format(n, '08b')`, and `int(format(n, 'b'), 2)` (convert back).
- Manually verify `13 = 8 + 4 + 0 + 1 = 1101` by adding up bit-position values.

**✓ Done when:** All `int(format(n, 'b'), 2)` results match the original `n`; you can mentally read `1101` as `13`.

---

### 🟢 #118 — Get, Set, Clear, Toggle
**Time:** ~12 min | **Concept:** four fundamental bit operations

Implement all four from scratch:
- `get_bit(n, i)` → `(n >> i) & 1`
- `set_bit(n, i)` → `n | (1 << i)`
- `clear_bit(n, i)` → `n & ~(1 << i)`
- `toggle_bit(n, i)` → `n ^ (1 << i)`

Test each on `n=13 (1101)` at bit positions 0, 1, 2, 3. Print binary before and after each operation.

**✓ Done when:** All 16 operations (4 functions × 4 positions) produce expected binary results — verify by inspection.

---

### 🟡 #119 — Is Power of Two
**Time:** ~10 min | **Concept:** `n & (n-1) == 0` trick

- Write `is_power_of_two(n: int) -> bool` using the single bitwise expression.
- Test on: `1, 2, 4, 8, 16, 1024` → all `True`; `0, 3, 6, 12, 100` → all `False`.
- In a comment, explain WHY `n & (n-1)` clears the lowest set bit, and why that means powers of two become 0.

**✓ Done when:** All 10 test cases correct; comment explains the why, not just the what.

---

### 🟡 #120 — Count Set Bits (Brian Kernighan)
**Time:** ~12 min | **Concept:** `n &= (n-1)` clears the lowest set bit each iteration

- Write `count_bits(n: int) -> int` using the `n &= n-1` loop.
- Test: `count_bits(13)` → `3` (1101); `count_bits(255)` → `8`; `count_bits(0)` → `0`.
- Confirm with Python's built-in: `bin(n).count('1')` should match.
- Count iterations — should equal the number of set bits, not the bit length.

**✓ Done when:** All three test cases correct; iteration count equals set-bit count (not total bit length).

---

### 🟠 #121 — Single Number (XOR)
**Time:** ~12 min | **Concept:** XOR cancellation — duplicates vanish, unique survives

- Write `single_number(nums: list[int]) -> int` — every element appears exactly twice except one.
- XOR all elements together; duplicates cancel (`x^x=0`); unique remains (`x^0=x`).
- Test: `single_number([4,1,2,1,2])` → `4`; `single_number([2,2,1])` → `1`.
- Add a trace: print the running XOR value after each element.

**✓ Done when:** Both test cases correct; trace shows cancellation happening. O(n) time, O(1) space.

---

### 🟠 #122 — Generate All Subsets via Bitmask
**Time:** ~15 min | **Concept:** each bit represents inclusion of one element

- Given `elements = ["a", "b", "c"]`, loop `mask` from `0` to `(1 << len(elements)) - 1`.
- For each mask: build the subset by checking `mask & (1 << i)` for each position i.
- Print `f"{mask:03b}: {subset}"` for all 8 masks.

**✓ Done when:** All 8 subsets printed with correct binary masks; `111` maps to `["a","b","c"]`, `000` maps to `[]`.

---

### 🔴 #123 — Reverse Bits of a 32-Bit Integer
**Time:** ~18 min | **Concept:** build the result bit by bit from LSB to MSB

- Write `reverse_bits(n: int) -> int` — reverses all 32 bits.
- Loop 32 times: shift result left, OR in the LSB of n, right-shift n.
- Test: `reverse_bits(0b00000010100101000001111010011100)` → `964176192` (the known reversed value).
- Also test `reverse_bits(43261596)` → `964176192`.

**✓ Done when:** Returns correct reversed integer for the standard test case.
> 💡 `result = (result << 1) | (n & 1); n >>= 1`.

---

### 💀 #124 — BOSS: Find Two Unique Numbers
**Time:** ~45 min | **Concept:** XOR + bit partitioning to separate two different uniques

Every number in `nums` appears exactly twice except for **two** numbers which appear once. Find both in O(n) time and O(1) space.

- XOR all elements → result is `a ^ b` where a and b are the two uniques.
- Find any set bit in `a ^ b` (use `xor & (-xor)` to isolate the lowest set bit).
- Use that bit to partition `nums` into two groups; XOR each group separately → one group gives a, the other gives b.
- Test: `find_two_unique([1,2,1,3,2,5])` → `{3, 5}`.

**✓ Done when:** Returns both unique numbers in any order. Write a step-by-step comment explaining why the partition correctly separates the two uniques.

---

## 🏁 Final Checklist

**Arc 1 — Big O (6):** `1☐ 2☐ 3☐ 4☐ 5☐ 6☐`

**Arc 2 — Arrays & Strings (8):** `7☐ 8☐ 9☐ 10☐ 11☐ 12☐ 13☐ 14☐`

**Arc 3 — Linked Lists (8):** `15☐ 16☐ 17☐ 18☐ 19☐ 20☐ 21☐ 22☐`

**Arc 4 — Hash Tables (8):** `23☐ 24☐ 25☐ 26☐ 27☐ 28☐ 29☐ 30☐`

**Arc 5 — Stacks & Queues (8):** `31☐ 32☐ 33☐ 34☐ 35☐ 36☐ 37☐ 38☐`

**Arc 6 — Recursion (8):** `39☐ 40☐ 41☐ 42☐ 43☐ 44☐ 45☐ 46☐`

**Arc 7 — Binary Search (8):** `47☐ 48☐ 49☐ 50☐ 51☐ 52☐ 53☐ 54☐`

**Arc 8 — Trees & BST (8):** `55☐ 56☐ 57☐ 58☐ 59☐ 60☐ 61☐ 62☐`

**Arc 9 — Heaps (8):** `63☐ 64☐ 65☐ 66☐ 67☐ 68☐ 69☐ 70☐`

**Arc 10 — Sorting (8):** `71☐ 72☐ 73☐ 74☐ 75☐ 76☐ 77☐ 78☐`

**Arc 11 — Graphs (8):** `79☐ 80☐ 81☐ 82☐ 83☐ 84☐ 85☐ 86☐`

**Arc 12 — Two Pointers (8):** `87☐ 88☐ 89☐ 90☐ 91☐ 92☐ 93☐ 94☐`

**Arc 13 — Sliding Window (6):** `95☐ 96☐ 97☐ 98☐ 99☐ 100☐`

**Arc 14 — Backtracking (8):** `101☐ 102☐ 103☐ 104☐ 105☐ 106☐ 107☐ 108☐`

**Arc 15 — Dynamic Programming (8):** `109☐ 110☐ 111☐ 112☐ 113☐ 114☐ 115☐ 116☐`

**Arc 16 — Bit Manipulation (8):** `117☐ 118☐ 119☐ 120☐ 121☐ 122☐ 123☐ 124☐`

---
*Total: 124 DSA exercises. Combined with the 139 Python exercises: 263 exercises total.*

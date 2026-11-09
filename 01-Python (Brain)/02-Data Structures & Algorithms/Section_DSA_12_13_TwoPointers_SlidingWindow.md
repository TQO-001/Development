## DSA Section 12: Two Pointers Algorithm

The two pointers technique uses two index variables moving through a sequence — either toward each other from opposite ends, or both moving forward at different speeds. Instead of the `O(n²)` you'd get from checking every pair with nested loops, two pointers solve the same problems in a single `O(n)` pass.

**The core insight:** If the data has a useful structural property (usually sortedness), you can move one pointer based on the comparison result, rather than checking every combination.

### 12.1 Converging Pointers — Working From Both Ends

Start one pointer at the left, one at the right. Move them toward each other based on what you find.

**Pattern: Two Sum in a sorted array:**

```python
def two_sum_sorted(numbers: list[int], target: int) -> tuple[int, int]:
    """Return indices of two numbers that sum to target. Array must be sorted."""
    left, right = 0, len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]

        if current_sum == target:
            return left, right          # Found it
        elif current_sum < target:
            left += 1                   # Sum too small — move left pointer right
        else:
            right -= 1                  # Sum too large — move right pointer left

    return -1, -1   # Not found

two_sum_sorted([2, 7, 11, 15], target=9)   # (0, 1) — 2+7=9
```

Why this works: the array is sorted, so if the current sum is too small, the left value is too small — increase it. If too large, the right value is too large — decrease it. You never need to check every pair.

**Pattern: Palindrome check:**

```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left  += 1
        right -= 1
    return True

is_palindrome("racecar")   # True
is_palindrome("hello")     # False
```

**Pattern: Container with Most Water:**

```python
def max_water(heights: list[int]) -> int:
    """Given n walls, find two walls that hold the most water."""
    left, right = 0, len(heights) - 1
    max_area = 0

    while left < right:
        width  = right - left
        height = min(heights[left], heights[right])
        max_area = max(max_area, width * height)

        # Move the pointer pointing at the shorter wall
        # (the shorter wall is the bottleneck — keeping it can't help)
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return max_area
```

### 12.2 Fast and Slow Pointers (Floyd's Technique)

Two pointers moving forward at different speeds. The fast pointer moves 2 steps per iteration, slow moves 1. If they ever meet, there's a cycle.

```python
# Detect cycle in a linked list (covered in Section 03)
def has_cycle(head) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast: return True
    return False

# Find the middle of a linked list
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # When fast reaches end, slow is at middle

# Happy number — does repeatedly summing squared digits reach 1?
def is_happy(n: int) -> bool:
    def next_num(x):
        return sum(int(d) ** 2 for d in str(x))

    slow, fast = n, next_num(n)
    while fast != 1 and slow != fast:
        slow = next_num(slow)
        fast = next_num(next_num(fast))

    return fast == 1
```

### 12.3 Same-Direction Pointers — Read/Write

Both pointers move forward, but at different rates. The "write" pointer marks where the next valid element should go; the "read" pointer scans ahead.

```python
def remove_duplicates_sorted(arr: list[int]) -> int:
    """Remove duplicates in place from a sorted array. Return new length."""
    if not arr: return 0
    write = 1   # Position to write the next unique element
    for read in range(1, len(arr)):
        if arr[read] != arr[read - 1]:   # Found a new unique element
            arr[write] = arr[read]
            write += 1
    return write   # arr[:write] contains the unique elements

arr = [1, 1, 2, 3, 3, 3, 4]
k = remove_duplicates_sorted(arr)
print(arr[:k])   # [1, 2, 3, 4]

# Remove all instances of a value (in place)
def remove_element(arr: list[int], val: int) -> int:
    write = 0
    for read in range(len(arr)):
        if arr[read] != val:
            arr[write] = arr[read]
            write += 1
    return write
```

### 12.4 Recognising Two Pointer Problems

Ask yourself:

1. Does the problem involve a **sorted** array or string?
2. Does it ask about **pairs** of elements?
3. Does it involve finding a **palindrome**?
4. Does it involve **in-place** modification of an array?
5. Does it involve **cycles** in a linked list?

If yes to any of these → two pointers is likely the right approach.

---

**Practice:**
1. Given a sorted array and a target sum, write `three_sum(arr, target)` that finds all unique triplets summing to target. Use a two-pointer approach for the inner loop.
2. Write `valid_palindrome_ii(s)` — given a string, return `True` if you can remove at most one character to make it a palindrome.
3. Write `move_zeros(arr)` in O(n) time and O(1) space — move all zeros to the end while preserving the order of non-zero elements.

---

## DSA Section 13: Sliding Window Algorithm

The sliding window technique maintains a contiguous subrange of a sequence using two pointers that define the window's boundaries. Instead of recomputing the window's state from scratch every time it shifts, you **add what came in and remove what fell out** — turning an `O(n·k)` or `O(n²)` solution into a single `O(n)` pass.

### 13.1 Fixed-Length Window

The window has a fixed size `k`. It slides one step at a time: add the new right element, remove the old left element.

```python
def max_sum_subarray(arr: list[int], k: int) -> int:
    """Find the maximum sum of any contiguous subarray of length k."""
    n = len(arr)
    if n < k: return 0

    # Build the first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide the window — O(n)
    for i in range(k, n):
        window_sum += arr[i]       # Add new right element
        window_sum -= arr[i - k]   # Remove old left element
        max_sum = max(max_sum, window_sum)

    return max_sum

max_sum_subarray([2, 1, 5, 1, 3, 2], k=3)
# Windows: [2,1,5]=8, [1,5,1]=7, [5,1,3]=9, [1,3,2]=6
# Returns: 9
```

**Average of all subarrays of size k:**

```python
def sliding_window_averages(arr: list[int], k: int) -> list[float]:
    result = []
    window_sum = sum(arr[:k])
    result.append(window_sum / k)

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]   # Add new, remove old
        result.append(window_sum / k)

    return result
```

### 13.2 Variable-Length Window

The window expands by moving the right pointer, and **contracts** by moving the left pointer when a condition is violated. The window size changes dynamically — you're looking for the longest or shortest subarray satisfying a condition.

```python
def longest_substring_no_repeat(s: str) -> int:
    """Longest substring without repeating characters."""
    char_set = set()
    left = 0
    max_length = 0

    for right in range(len(s)):
        # Window violates condition: s[right] already in window
        while s[right] in char_set:
            char_set.remove(s[left])   # Shrink from left until valid
            left += 1

        char_set.add(s[right])         # Expand window to include s[right]
        max_length = max(max_length, right - left + 1)

    return max_length

longest_substring_no_repeat("abcabcbb")   # 3 ("abc")
longest_substring_no_repeat("pwwkew")     # 3 ("wke")
```

**Minimum window containing all required characters:**

```python
from collections import Counter

def min_window_substring(s: str, t: str) -> str:
    """Smallest substring of s that contains all characters of t."""
    if not t or not s: return ""

    need = Counter(t)        # How many of each char we still need
    have = {}
    formed = 0               # How many unique chars are satisfied
    required = len(need)

    left = 0
    min_len = float('inf')
    result = ""

    for right in range(len(s)):
        char = s[right]
        have[char] = have.get(char, 0) + 1

        if char in need and have[char] == need[char]:
            formed += 1      # This char's requirement is now met

        # All required chars met — try to shrink from left
        while formed == required:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right + 1]

            # Remove left character and shrink
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1

    return result

min_window_substring("ADOBECODEBANC", "ABC")   # "BANC"
```

### 13.3 The Variable Window Template

```python
def sliding_window_template(arr, condition_params):
    left = 0
    state = {}          # Track window state (char counts, sum, etc.)
    best = 0            # Or worst, depending on the problem

    for right in range(len(arr)):
        # 1. EXPAND: add arr[right] to the window state
        update_state(state, arr[right])

        # 2. SHRINK: while the window violates the condition
        while violates_condition(state, condition_params):
            remove_from_state(state, arr[left])
            left += 1

        # 3. RECORD: current window [left..right] is valid
        best = max(best, right - left + 1)   # Or compute answer differently

    return best
```

### 13.4 Recognising Sliding Window Problems

Look for these phrases in the problem statement:
- "contiguous subarray" or "contiguous substring"
- "longest/shortest/minimum/maximum subarray that..."
- "subarray with sum equal to k"
- "window of size k"

And this structure in a brute-force solution:
- Two nested loops where the inner loop starts near where the outer loop is
- Recomputing a running total from scratch on each outer iteration

If you see either of these → sliding window, not brute force.

---

**Practice:**
1. Write `max_sum_fixed_window(arr, k)` — maximum sum of any contiguous subarray of exactly length `k`. Test on `[2, 1, 5, 1, 3, 2]` with `k=3`.
2. Write `longest_ones(arr, k)` — given a binary array, find the length of the longest subarray containing at most `k` zeros (you can flip k zeros to ones). Use a variable-length window.
3. Write `count_subarrays_with_sum(arr, target)` — count all contiguous subarrays with a sum exactly equal to target. Use a sliding window with a hash map for the prefix sum variant.

---

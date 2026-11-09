## DSA Section 10: Sorting Algorithms

Sorting is one of the most studied problems in computer science. Six algorithms cover every interview question you'll face — each with a different time/space trade-off, and each illustrating a different problem-solving technique (in-place swapping, divide and conquer, non-comparison counting).

Python's built-in `sort()` is Timsort — `O(n log n)` guaranteed, stable, and almost always the right choice in real code. You study the others to understand *why* they work, what trade-offs look like, and because interviewers test them directly.

### 10.1 Bubble Sort — O(n²)

Repeatedly steps through the list, swapping adjacent out-of-order elements. After each pass, the largest unsorted element "bubbles" to its correct position at the end.

```python
def bubble_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):   # Last i elements already sorted
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break   # Already sorted — O(n) best case with early exit
    return arr

bubble_sort([64, 34, 25, 12, 22, 11, 90])
# Pass 1: [34, 25, 12, 22, 11, 64, 90] ← 90 bubbled to end
# Pass 2: [25, 12, 22, 11, 34, 64, 90] ← 64 bubbled to end
# ...
# Final:  [11, 12, 22, 25, 34, 64, 90]
```

| Metric | Value |
|---|---|
| Time (best) | O(n) — already sorted, early exit |
| Time (average/worst) | O(n²) |
| Space | O(1) — in-place |
| Stable | ✅ Yes — equal elements never swap |

**Use it when:** Teaching sorting basics. Almost never in production.

### 10.2 Insertion Sort — O(n²), O(n) best

Builds a sorted prefix one element at a time. Each new element is shifted backward through the sorted prefix until it finds its correct position — exactly how you sort playing cards in your hand.

```python
def insertion_sort(arr: list[int]) -> list[int]:
    for i in range(1, len(arr)):
        key = arr[i]            # The element to insert
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]   # Shift larger elements right
            j -= 1
        arr[j + 1] = key          # Insert key in its correct position
    return arr

insertion_sort([12, 11, 13, 5, 6])
# i=1: key=11, shift 12 right → [11, 12, 13, 5, 6]
# i=2: key=13, no shift       → [11, 12, 13, 5, 6]
# i=3: key=5,  shift 13,12,11 → [5, 11, 12, 13, 6]
# i=4: key=6,  shift 13,12,11 → [5, 6, 11, 12, 13]
```

| Metric | Value |
|---|---|
| Time (best) | O(n) — nearly sorted input, few shifts |
| Time (average/worst) | O(n²) |
| Space | O(1) — in-place |
| Stable | ✅ Yes |

**Use it when:** The array is nearly sorted (fastest among comparison sorts in that case), or the dataset is very small (< 20 elements). Production `sort()` implementations switch to insertion sort below a size threshold.

### 10.3 Selection Sort — O(n²) always

Repeatedly finds the minimum of the unsorted portion and swaps it into place. Unlike bubble sort, it does at most `n` swaps regardless of input — useful when writes are expensive.

```python
def selection_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):       # Find min in unsorted portion
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]   # Swap into place
    return arr
```

| Metric | Value |
|---|---|
| Time (all cases) | O(n²) — always scans the full unsorted portion |
| Space | O(1) — in-place |
| Stable | ❌ No — distant swaps can reorder equal elements |
| Swaps | At most n — minimum possible writes |

**Use it when:** Swap cost is very high (e.g., writing to flash storage), and minimising writes matters more than time.

### 10.4 Merge Sort — O(n log n) guaranteed

Divide and conquer: recursively split the list in half until each piece has one element, then **merge** sorted halves by comparing their fronts. Guarantees `O(n log n)` on all inputs because the split and merge steps are fixed regardless of data order.

```python
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr   # Base case: a list of 0 or 1 is already sorted

    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])    # Sort left half
    right = merge_sort(arr[mid:])    # Sort right half
    return merge(left, right)        # Merge the two sorted halves

def merge(left: list[int], right: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])    # Append any remaining elements
    result.extend(right[j:])
    return result

merge_sort([38, 27, 43, 3, 9, 82, 10])
# Split:  [38,27,43] and [3,9,82,10]
# Split:  [38],[27,43] and [3,9],[82,10]
# Merge:  [27,38] and [3,9],[10,82]
# Merge:  [27,38,43] and [3,9,10,82]
# Merge:  [3, 9, 10, 27, 38, 43, 82]
```

| Metric | Value |
|---|---|
| Time (all cases) | **O(n log n)** — guaranteed |
| Space | O(n) — needs auxiliary space for merging |
| Stable | ✅ Yes — equal elements maintain relative order |

**Use it when:** You need guaranteed `O(n log n)` (quicksort's worst case is `O(n²)`), stability matters, or you're sorting a linked list (sequential access fits merge naturally).

### 10.5 Quick Sort — O(n log n) average, O(n²) worst

Picks a **pivot**, partitions the array so everything smaller goes left and everything larger goes right, then recursively sorts each side. No extra space for merging — it sorts in-place.

```python
def quick_sort(arr: list[int], lo: int = 0, hi: int = None) -> list[int]:
    if hi is None: hi = len(arr) - 1

    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quick_sort(arr, lo, pivot_idx - 1)   # Sort left of pivot
        quick_sort(arr, pivot_idx + 1, hi)   # Sort right of pivot
    return arr

def partition(arr: list[int], lo: int, hi: int) -> int:
    pivot = arr[hi]   # Use the last element as pivot
    i = lo - 1        # i = boundary between smaller and larger elements

    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]   # Swap smaller to left side

    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]   # Place pivot in final position
    return i + 1

# Randomised pivot — avoids worst case on sorted input
import random
def partition_random(arr, lo, hi):
    rand_idx = random.randint(lo, hi)
    arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]   # Swap random → last
    return partition(arr, lo, hi)
```

| Metric | Value |
|---|---|
| Time (average) | **O(n log n)** |
| Time (worst) | O(n²) — sorted input with bad pivot |
| Space | O(log n) — call stack depth |
| Stable | ❌ No |

**Use it when:** You need the fastest general-purpose sort in practice. Most standard library sorts use quicksort (or introsort — quicksort + heapsort fallback). Always randomise or use median-of-three pivot selection.

### 10.6 Counting Sort — O(n + k)

Not a comparison sort. Instead of comparing elements, it counts how many times each distinct value appears, then reconstructs the sorted output from those counts. Breaks the `O(n log n)` comparison-sort lower bound — but only works for integers in a known, bounded range.

```python
def counting_sort(arr: list[int]) -> list[int]:
    if not arr: return arr
    max_val = max(arr)
    min_val = min(arr)
    range_size = max_val - min_val + 1

    counts = [0] * range_size
    for num in arr:
        counts[num - min_val] += 1   # Count each value

    result = []
    for i, count in enumerate(counts):
        result.extend([i + min_val] * count)   # Reconstruct sorted output
    return result

counting_sort([4, 2, 2, 8, 3, 3, 1])
# counts: index 1→1, 2→2, 3→2, 4→1, 8→1
# result: [1, 2, 2, 3, 3, 4, 8]
```

| Metric | Value |
|---|---|
| Time | **O(n + k)** where k = value range size |
| Space | O(k) — the counts array |
| Stable | ✅ Yes (with proper implementation) |
| Restriction | Integers only, bounded range |

**Use it when:** Sorting a large number of small integers with a known range — exam scores (0–100), character frequencies, ages.

### 10.7 Sort Comparison Table

| Algorithm | Best | Average | Worst | Space | Stable | Use when... |
|---|---|---|---|---|---|---|
| Bubble | O(n) | O(n²) | O(n²) | O(1) | ✅ | Learning only |
| Insertion | O(n) | O(n²) | O(n²) | O(1) | ✅ | Nearly sorted / tiny datasets |
| Selection | O(n²) | O(n²) | O(n²) | O(1) | ❌ | Minimise swaps |
| Merge | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ | Need guaranteed O(n log n), stability |
| Quick | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | General purpose, fastest in practice |
| Counting | O(n+k) | O(n+k) | O(n+k) | O(k) | ✅ | Small integer range |

---

**Practice:**
1. Implement `merge_sort` from scratch and test it on `[38, 27, 43, 3, 9, 82, 10]`. Trace through the recursive calls for the first two splits.
2. Implement `quick_sort` with a randomised pivot. Test it on a sorted input like `[1, 2, 3, 4, 5]` and confirm it still works correctly.
3. Given a list of player levels all between 1 and 100, write `counting_sort` to sort them. What is the time complexity? How does it compare to merge sort for this input?

---

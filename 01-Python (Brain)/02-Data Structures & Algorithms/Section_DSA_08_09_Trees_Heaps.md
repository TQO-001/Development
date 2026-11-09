## DSA Section 08: Binary Trees & Binary Search Trees

A tree organises data hierarchically. Unlike arrays and linked lists (which are linear), trees branch. The **binary tree** is the most important tree structure in DSA — each node has at most two children, and almost every tree algorithm is a variation of "visit this node, then recurse on left and right."

### 8.1 The Tree Node

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left  = None   # Left child
        self.right = None   # Right child
```

Visualised:

```
            Arthur (root)
           /              \
        Merlin           Lancelot
        /    \            /
    Galahad  Gawain   Percival
```

- **Root**: the topmost node (Arthur)
- **Leaf**: a node with no children (Galahad, Gawain, Percival)
- **Height**: the number of edges from root to the deepest leaf
- **Depth** of a node: edges from root to that node

### 8.2 Tree Traversals

The order you visit nodes determines what the algorithm produces. The three depth-first traversals differ only in **when** you process the current node.

```python
def preorder(node: TreeNode):
    """Process node BEFORE its children. Root → Left → Right."""
    if not node: return
    print(node.value)        # Process NOW
    preorder(node.left)      # Then left subtree
    preorder(node.right)     # Then right subtree
# Used for: copying a tree, serialising a tree, prefix expressions

def inorder(node: TreeNode):
    """Process node BETWEEN its children. Left → Root → Right."""
    if not node: return
    inorder(node.left)       # Left subtree first
    print(node.value)        # Process NOW
    inorder(node.right)      # Then right subtree
# Used for: BST traversal (produces sorted output), finding kth smallest

def postorder(node: TreeNode):
    """Process node AFTER its children. Left → Right → Root."""
    if not node: return
    postorder(node.left)     # Left subtree first
    postorder(node.right)    # Right subtree second
    print(node.value)        # Process LAST
# Used for: deleting a tree, evaluating expression trees

def level_order(root: TreeNode) -> list[list]:
    """BFS — visit all nodes at one depth before moving to the next."""
    from collections import deque
    if not root: return []
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.value)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(current_level)

    return result
# Used for: level-by-level output, finding shortest path, serialisation
```

**When to choose which traversal:**

| Traversal | Use it when... |
|---|---|
| Preorder | You need to process the root before subtrees (copy, prefix expression) |
| Inorder | You're working with a BST (gives sorted order) |
| Postorder | Children must be processed before their parent (delete tree, folder size) |
| Level-order | Problem involves levels/depth (min depth, right side view, zigzag) |

### 8.3 Common Tree Algorithms

```python
def height(node: TreeNode) -> int:
    """Max depth from this node to a leaf. O(n) — visits all nodes."""
    if not node: return 0
    return 1 + max(height(node.left), height(node.right))

def count_nodes(node: TreeNode) -> int:
    """Total number of nodes. O(n)."""
    if not node: return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

def is_balanced(node: TreeNode) -> bool:
    """A balanced tree: left and right subtree heights differ by at most 1."""
    def check(node):
        if not node: return 0
        left_h  = check(node.left)
        right_h = check(node.right)
        if left_h == -1 or right_h == -1: return -1  # Already unbalanced
        if abs(left_h - right_h) > 1:    return -1  # Unbalanced here
        return 1 + max(left_h, right_h)
    return check(node) != -1
```

### 8.4 Binary Search Trees (BST)

A BST adds one invariant to a binary tree: for every node, **all values in its left subtree are smaller**, and **all values in its right subtree are larger**. This invariant enables `O(log n)` search on a balanced tree.

```python
class BST:
    def __init__(self): self.root = None

    def insert(self, value: int):
        """O(log n) average, O(n) worst case (skewed tree)."""
        def _insert(node, val):
            if not node: return TreeNode(val)
            if val < node.value:
                node.left  = _insert(node.left, val)
            elif val > node.value:
                node.right = _insert(node.right, val)
            return node
        self.root = _insert(self.root, value)

    def search(self, value: int) -> bool:
        """O(log n) average."""
        node = self.root
        while node:
            if value == node.value: return True
            node = node.left if value < node.value else node.right
        return False

    def inorder_sorted(self) -> list:
        """Inorder traversal of a BST always yields sorted output."""
        result = []
        def _inorder(node):
            if not node: return
            _inorder(node.left)
            result.append(node.value)
            _inorder(node.right)
        _inorder(self.root)
        return result


bst = BST()
for level in [15, 8, 22, 4, 12, 18, 25]:
    bst.insert(level)

#         15
#        /  \
#       8    22
#      / \  /  \
#     4  12 18  25

bst.search(12)         # True — O(log n)
bst.inorder_sorted()   # [4, 8, 12, 15, 18, 22, 25] — sorted!
```

**BST Complexity:**

| Operation | Average (balanced) | Worst (skewed) |
|---|---|---|
| Search | **O(log n)** | O(n) |
| Insert | **O(log n)** | O(n) |
| Delete | **O(log n)** | O(n) |
| Inorder traversal | O(n) | O(n) |

The worst case (O(n)) happens when you insert already-sorted data — the tree degenerates into a linked list. Self-balancing trees (AVL, Red-Black) fix this in production systems.

---

**Practice:**
1. Build a BST by inserting `[10, 5, 15, 3, 7, 12, 20]`. Write `inorder_sorted()` and verify it returns the sorted list.
2. Write a recursive function `max_depth(root)` that returns the maximum depth of a binary tree. What is its time and space complexity?
3. Write `level_order(root)` returning a list of lists — each inner list holds the values at one depth level. Use a deque as the queue.

---

## DSA Section 09: Heaps & Priority Queues

A **heap** is a complete binary tree (filled top-to-bottom, left-to-right) with one key property: every parent is smaller than its children (min-heap) or larger (max-heap). The most important consequence: **the root is always the minimum (or maximum)**, retrievable in `O(1)`.

### 9.1 Min-Heap and Max-Heap

```
Min-Heap:           Max-Heap:
     1                  25
    / \                /   \
   5   3             20    22
  / \ / \           / \   /  \
 8  7 6  4         4   8  6   3
```

In a min-heap: every parent ≤ both children. Root = global minimum.
In a max-heap: every parent ≥ both children. Root = global maximum.

### 9.2 Heaps Stored in Arrays

Heaps are stored compactly in an array (no pointers needed):

```
Array: [1, 5, 3, 8, 7, 6, 4]
Index:  0  1  2  3  4  5  6

For node at index i:
  Parent:      (i - 1) // 2
  Left child:  2 * i + 1
  Right child: 2 * i + 2
```

### 9.3 Heapify — Restoring the Heap Property

**Sift-up (after insert):** Add the new element at the end, then repeatedly swap it with its parent while it's smaller than its parent.

**Sift-down (after remove):** Replace the root with the last element, then repeatedly swap it with the smaller of its children until it's in the right place.

Both operations are `O(log n)` — the tree height limits how many swaps are needed.

### 9.4 Python's heapq — The Built-In Min-Heap

Python implements a min-heap directly on a plain list via `heapq`.

```python
import heapq

# Build a heap from a list — O(n), more efficient than n insertions
player_levels = [15, 8, 22, 4, 12, 18, 25]
heapq.heapify(player_levels)
# player_levels is now heap-ordered: [4, 8, 18, 15, 12, 22, 25]

# Push — O(log n)
heapq.heappush(player_levels, 6)

# Pop the minimum — O(log n)
smallest = heapq.heappop(player_levels)   # Returns 4, smallest removed

# Peek at minimum — O(1)
minimum = player_levels[0]

# Push then pop in one step (more efficient than two calls)
heapq.heappushpop(player_levels, 10)

# nsmallest and nlargest — O(n log k)
smallest_3 = heapq.nsmallest(3, player_levels)
largest_3  = heapq.nlargest(3, player_levels)
```

**Max-heap trick — negate the values:**

```python
# heapq is min-heap only. For max-heap, negate all values.
max_heap = []
heapq.heappush(max_heap, -15)
heapq.heappush(max_heap, -8)
heapq.heappush(max_heap, -22)

largest = -heapq.heappop(max_heap)   # Returns 22 (after negating back)
```

**Heaps with tuples — priority queues in practice:**

```python
# Push (priority, item) tuples — heapq orders by the first element
task_queue = []
heapq.heappush(task_queue, (3, "Patrol the walls"))   # priority 3
heapq.heappush(task_queue, (1, "Defend the king"))    # priority 1 — highest
heapq.heappush(task_queue, (2, "Gather supplies"))    # priority 2

priority, task = heapq.heappop(task_queue)
print(task)   # "Defend the king" — lowest number = highest priority
```

### 9.5 Heap Sort — O(n log n)

```python
def heap_sort(arr: list[int]) -> list[int]:
    """Sort using a heap. O(n log n) time, O(n) space for the heap."""
    heapq.heapify(arr)              # O(n) — build heap
    return [heapq.heappop(arr) for _ in range(len(arr))]
    # Each pop is O(log n), n pops → O(n log n) total

heap_sort([15, 3, 8, 1, 22, 7])   # [1, 3, 7, 8, 15, 22]
```

### 9.6 Top-K Pattern — The Most Common Heap Interview Problem

"Find the K largest/smallest elements" — reach for a heap immediately.

```python
def k_largest(numbers: list[int], k: int) -> list[int]:
    """Returns the k largest numbers. O(n log k) time, O(k) space."""
    # Use a MIN-heap of size k. When it fills up, pop the smallest.
    # Whatever remains at the end is the k largest.
    min_heap = []
    for num in numbers:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)   # Remove the smallest — it's not top-k

    return sorted(min_heap, reverse=True)

k_largest([3, 1, 8, 22, 5, 14, 2], k=3)   # [22, 14, 8]
```

**Heap Complexity Summary:**

| Operation | Complexity |
|---|---|
| `heapify(arr)` | O(n) |
| `heappush(heap, x)` | O(log n) |
| `heappop(heap)` | O(log n) |
| `heap[0]` (peek min) | O(1) |
| `nsmallest(k, arr)` | O(n log k) |

---

**Practice:**
1. Use `heapq` to implement a task scheduler: push 5 tasks with different priorities and pop them in priority order, printing each task name.
2. Write `k_largest(numbers, k)` using a min-heap of size k. Verify it works on `[10, 4, 3, 50, 23, 1]` with `k=3`.
3. Implement `heap_sort(arr)` and verify it produces sorted output. What is its time complexity and how does it compare to Python's built-in `sort()`?

---

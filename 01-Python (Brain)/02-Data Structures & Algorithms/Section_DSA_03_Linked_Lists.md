## DSA Section 03: Linked Lists — Singly & Doubly Linked

A linked list stores elements as individual **nodes**, each containing a value and a pointer to the next node. Unlike an array, nodes are scattered anywhere in memory — they don't need to be next to each other. The list is just the chain of pointers connecting them.

This makes insertion and deletion at a known point `O(1)` — you only rewire a couple of pointers. The trade-off is that you lose direct index access: to reach the 5th node, you must walk the chain from the start, one step at a time.

### 3.1 The Node — The Building Block

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None    # Pointer to the next node (None = end of list)
```

Visualised:

```
[Arthur|→] → [Merlin|→] → [Lancelot|→] → [None]
   head
```

Each box has two parts: a value and an arrow (pointer). The head is the entry point to the list. The last node points to `None`.

### 3.2 Singly Linked List

In a **singly linked list**, each node only knows about the node ahead of it. You can only travel forward.

```python
class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def prepend(self, value):
        """Insert at the front — O(1)."""
        new_node = Node(value)
        new_node.next = self.head   # New node points to old head
        self.head = new_node        # Head is now the new node

    def append(self, value):
        """Insert at the back — O(n) since we must walk to the end."""
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:         # Walk until the last node
            current = current.next
        current.next = new_node     # Last node points to new node

    def delete(self, value):
        """Remove the first node with this value — O(n) to find it."""
        if not self.head:
            return

        # Special case: deleting the head
        if self.head.value == value:
            self.head = self.head.next
            return

        # Walk until we find the node BEFORE the one to delete
        current = self.head
        while current.next and current.next.value != value:
            current = current.next

        if current.next:
            current.next = current.next.next   # Skip over the deleted node
            # O(1) to delete once found — just rewire the pointer

    def find(self, value) -> bool:
        """Search for a value — O(n): must walk from head."""
        current = self.head
        while current:
            if current.value == value:
                return True
            current = current.next
        return False

    def print_list(self):
        """Print all values — O(n)."""
        values = []
        current = self.head
        while current:
            values.append(str(current.value))
            current = current.next
        print(" → ".join(values) + " → None")


# Usage
party = SinglyLinkedList()
party.append("Arthur")
party.append("Merlin")
party.append("Lancelot")
party.prepend("Galahad")    # Galahad goes to the front

party.print_list()
# Galahad → Arthur → Merlin → Lancelot → None

party.delete("Arthur")
party.print_list()
# Galahad → Merlin → Lancelot → None
```

### 3.3 Singly Linked List — Complexity Summary

| Operation | Complexity | Why |
|---|---|---|
| Prepend (insert at head) | **O(1)** | Just rewire head pointer |
| Append (insert at tail) | **O(n)** | Must walk to the end |
| Delete (by value) | **O(n)** | Must search first |
| Find (search) | **O(n)** | Must walk the chain |
| Access by index | **O(n)** | No shortcuts — walk from head |

> [!NOTE]
> If you store a **tail pointer** alongside the head, `append` becomes `O(1)`. Most production linked list implementations do this.

### 3.4 Common Interview Techniques on Linked Lists

**Reversing a singly linked list — O(n) time, O(1) space:**

```python
def reverse(head: Node) -> Node:
    prev = None
    current = head
    while current:
        next_node = current.next    # Save the next node
        current.next = prev         # Reverse the pointer
        prev = current              # Advance prev
        current = next_node         # Advance current
    return prev  # prev is now the new head
```

**Detecting a cycle (Floyd's algorithm — fast and slow pointers):**

```python
def has_cycle(head: Node) -> bool:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next        # Moves 1 step
        fast = fast.next.next   # Moves 2 steps
        if slow == fast:        # They meet → cycle exists
            return True
    return False
# If no cycle, fast reaches None. If cycle, fast laps slow and they meet.
```

**Finding the middle node (fast and slow pointers):**

```python
def find_middle(head: Node) -> Node:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # When fast reaches end, slow is at the middle
```

### 3.5 Doubly Linked List

A **doubly linked list** adds a `prev` pointer to each node, so you can walk both forward and backward. This makes deletion at a known node truly `O(1)` — you don't need to walk from the head to find the node before it.

```python
class DoublyNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None   # Points backward
```

Visualised:

```
None ← [Galahad|↔] ↔ [Arthur|↔] ↔ [Merlin|→] → None
         head                          tail
```

```python
class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, value):
        """Insert at tail — O(1) since we have a tail pointer."""
        new_node = DoublyNode(value)
        if not self.head:
            self.head = self.tail = new_node
            return
        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node

    def delete_node(self, node: DoublyNode):
        """Delete a specific node — O(1) once you have the reference.
        No need to walk from head to find the predecessor."""
        if node.prev:
            node.prev.next = node.next   # Skip over this node (forward)
        else:
            self.head = node.next        # Deleting the head

        if node.next:
            node.next.prev = node.prev   # Skip over this node (backward)
        else:
            self.tail = node.prev        # Deleting the tail

    def prepend(self, value):
        """Insert at head — O(1)."""
        new_node = DoublyNode(value)
        if not self.head:
            self.head = self.tail = new_node
            return
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node
```

### 3.6 Doubly Linked List — Complexity Summary

| Operation | Complexity | vs Singly |
|---|---|---|
| Prepend | **O(1)** | Same |
| Append | **O(1)** | Better (tail pointer) |
| Delete known node | **O(1)** | Better (no need to find prev) |
| Delete by value | **O(n)** | Same (search still required) |
| Find by value | **O(n)** | Same |
| Traverse backward | **O(n)** | Only doubly can do this |

### 3.7 When to Use a Linked List

| Use case | Best choice |
|---|---|
| Need O(1) prepend/delete-at-head | Singly linked list |
| Need O(1) at both ends | Doubly linked list (or `collections.deque`) |
| Need index access | Dynamic array (list) |
| LRU Cache implementation | Doubly linked list + hash map |
| Reversing, cycle detection | Singly linked list (fast/slow pointer technique) |

> [!NOTE]
> Python's `collections.deque` is a doubly linked list under the hood and gives `O(1)` append and pop at both ends. For most practical purposes, use `deque` instead of writing your own doubly linked list.

```python
from collections import deque

quest_chain = deque()
quest_chain.appendleft("Find the Grail")   # O(1) insert at front
quest_chain.append("Slay the Dragon")       # O(1) insert at back
quest_chain.popleft()                       # O(1) remove from front
quest_chain.pop()                           # O(1) remove from back
```

---

**Practice:**
1. Implement a singly linked list with `prepend`, `append`, `delete`, and `print_list`. Test it by building a chain of 4 quest names, deleting the middle one, and printing the result.
2. Write a function `reverse_linked_list(head)` that reverses a singly linked list in place and returns the new head. Test it.
3. Write a function `has_cycle(head)` using Floyd's fast-and-slow pointer algorithm. Create a cycle manually in a test list (set `tail.next = head`) and verify detection works.

---

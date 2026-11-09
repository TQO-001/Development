## DSA Section 11: Graph Theory

A graph is a set of **nodes** (also called vertices) connected by **edges**. Unlike trees, graphs have no root, no hierarchy, and edges can go in any direction — or both directions at once. Almost any network problem maps to a graph: dungeon rooms connected by doors, players connected by friendships, cities connected by roads.

**Directed graph:** edges have a direction (A → B doesn't mean B → A). Undirected: edges go both ways. **Weighted:** edges carry a value (distance, cost). **Unweighted:** all edges are equal.

### 11.1 Graph Representations

The same graph can be stored in three ways. Each has different memory and time trade-offs.

**The example graph (undirected, unweighted):**

```
    Camelot ── Avalon
       |    \    |
    Glaston  Tintagel
```

Nodes: `{Camelot, Avalon, Glaston, Tintagel}`
Edges: `(Camelot-Avalon), (Camelot-Glaston), (Camelot-Tintagel), (Avalon-Tintagel)`

### 11.2 Edge List — O(E) Space

A flat list of `(source, destination)` pairs. Simple to build, but checking if two nodes are connected requires scanning the entire list.

```python
# Edge list
edges = [
    ("Camelot",  "Avalon"),
    ("Camelot",  "Glaston"),
    ("Camelot",  "Tintagel"),
    ("Avalon",   "Tintagel"),
]

# O(E) to check if an edge exists — must scan everything
def are_connected(edges, a, b):
    return (a, b) in edges or (b, a) in edges   # O(E)

# Use it when: you only need to iterate all edges once
# (e.g., Kruskal's MST algorithm sorts edges by weight)
edges_sorted = sorted(edges, key=lambda e: e[2] if len(e) > 2 else 0)
```

| Operation | Complexity |
|---|---|
| Store | O(E) space |
| Check if edge exists | O(E) |
| Get all neighbours of node | O(E) |

### 11.3 Adjacency Matrix — O(V²) Space

A 2D grid of size V×V where `matrix[i][j] = 1` (or the weight) if an edge exists between node i and j.

```python
# Map node names to indices
nodes = ["Camelot", "Avalon", "Glaston", "Tintagel"]
idx = {name: i for i, name in enumerate(nodes)}

V = len(nodes)
matrix = [[0] * V for _ in range(V)]

# Add edges (undirected — set both directions)
def add_edge(a, b, weight=1):
    matrix[idx[a]][idx[b]] = weight
    matrix[idx[b]][idx[a]] = weight

add_edge("Camelot",  "Avalon")
add_edge("Camelot",  "Glaston")
add_edge("Camelot",  "Tintagel")
add_edge("Avalon",   "Tintagel")

# matrix[0][1] = 1  (Camelot ↔ Avalon)
# matrix[0][2] = 1  (Camelot ↔ Glaston)
# etc.

# O(1) edge check — direct index lookup
def are_connected(a, b): return matrix[idx[a]][idx[b]] != 0

# O(V) to get all neighbours of a node — scan the full row
def neighbours(a): return [nodes[j] for j in range(V) if matrix[idx[a]][j] != 0]
```

| Operation | Complexity |
|---|---|
| Store | **O(V²) space** — always, even for sparse graphs |
| Check if edge exists | **O(1)** — direct lookup |
| Get all neighbours | O(V) — scan full row |
| Add / remove edge | O(1) |

**Use it when:** The graph is **dense** (many edges, close to V² total) or you need constant-time edge existence checks. Avoid for sparse graphs — the wasted space is prohibitive.

### 11.4 Adjacency List — O(V + E) Space (Default Choice)

Each node maps to a list of its direct neighbours. Only stores edges that actually exist.

```python
# Using a dict of lists — most flexible Python representation
graph = {
    "Camelot":  ["Avalon", "Glaston", "Tintagel"],
    "Avalon":   ["Camelot", "Tintagel"],
    "Glaston":  ["Camelot"],
    "Tintagel": ["Camelot", "Avalon"],
}

# O(degree) to check if edge exists — scan the neighbour list
def are_connected(a, b): return b in graph[a]

# O(degree) to get all neighbours — direct access
def neighbours(a): return graph[a]

# For weighted graphs, store (neighbour, weight) tuples
weighted_graph = {
    "Camelot":  [("Avalon", 5), ("Glaston", 3), ("Tintagel", 8)],
    "Avalon":   [("Camelot", 5), ("Tintagel", 4)],
    "Glaston":  [("Camelot", 3)],
    "Tintagel": [("Camelot", 8), ("Avalon", 4)],
}
```

| Operation | Complexity |
|---|---|
| Store | **O(V + E)** — only existing edges |
| Check if edge exists | O(degree of node) |
| Get all neighbours | O(degree) — very fast |
| Add edge | O(1) |

**Use it for almost everything** — most real graphs are sparse, and DFS/BFS need "give me this node's neighbours" constantly.

### 11.5 Depth-First Search (DFS)

Explores as far as possible down one path before backtracking. Uses a stack — either the call stack (recursive) or an explicit stack (iterative). Visits every reachable node and edge exactly once: **O(V + E)**.

```python
# Recursive DFS — natural and clean
def dfs_recursive(graph: dict, node: str, visited: set = None) -> list:
    if visited is None: visited = set()
    visited.add(node)
    result = [node]
    for neighbour in graph[node]:
        if neighbour not in visited:
            result.extend(dfs_recursive(graph, neighbour, visited))
    return result

dfs_recursive(graph, "Camelot")
# One possible order: ['Camelot', 'Avalon', 'Tintagel', 'Glaston']

# Iterative DFS — use when recursion depth is a concern
def dfs_iterative(graph: dict, start: str) -> list:
    visited = set()
    stack = [start]
    result = []
    while stack:
        node = stack.pop()            # LIFO — depth-first
        if node in visited: continue
        visited.add(node)
        result.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                stack.append(neighbour)
    return result
```

**DFS applications:**

```python
# 1. Detect a cycle in a directed graph
def has_cycle_directed(graph: dict) -> bool:
    visited  = set()
    rec_stack = set()   # Nodes in the CURRENT recursion path

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                if dfs(neighbour): return True
            elif neighbour in rec_stack:
                return True   # Back edge = cycle
        rec_stack.remove(node)
        return False

    return any(dfs(n) for n in graph if n not in visited)

# 2. Count connected components (undirected)
def count_components(graph: dict) -> int:
    visited = set()
    count = 0
    for node in graph:
        if node not in visited:
            dfs_recursive(graph, node, visited)
            count += 1
    return count

# 3. Topological sort (directed acyclic graph — DAG)
def topological_sort(graph: dict) -> list:
    visited = set()
    stack = []
    def dfs(node):
        visited.add(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                dfs(neighbour)
        stack.append(node)     # Add to stack AFTER processing all children
    for node in graph:
        if node not in visited: dfs(node)
    return stack[::-1]         # Reverse = topological order
```

### 11.6 Breadth-First Search (BFS)

Explores level by level — all direct neighbours of the start, then all their neighbours, and so on. Uses a **queue**. The first time BFS reaches a node is always via the shortest path (in an unweighted graph): **O(V + E)**.

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    visited = set([start])
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()      # FIFO — breadth-first
        result.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return result

# BFS shortest path — returns the path, not just True/False
def bfs_shortest_path(graph: dict, start: str, end: str) -> list | None:
    if start == end: return [start]
    visited = set([start])
    queue = deque([[start]])   # Store paths, not just nodes

    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbour in graph[node]:
            if neighbour == end:
                return path + [neighbour]   # Found it — this IS the shortest path
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(path + [neighbour])

    return None  # No path exists

bfs_shortest_path(graph, "Glaston", "Tintagel")
# ['Glaston', 'Camelot', 'Tintagel']
```

### 11.7 DFS vs BFS — When to Use Which

| | DFS | BFS |
|---|---|---|
| Data structure | Stack (call stack or explicit) | Queue (`deque`) |
| Traversal order | Deep before wide | Level by level |
| Memory | O(V) stack depth | O(V) queue width |
| Shortest path | ❌ Not guaranteed | ✅ Guaranteed (unweighted) |
| Detect cycles | ✅ Natural fit | Possible but awkward |
| Topological sort | ✅ Natural fit | Possible (Kahn's algorithm) |
| Connected components | ✅ Natural fit | ✅ Both work |
| Level-based problems | ❌ | ✅ (e.g., minimum steps) |

---

**Practice:**
1. Build the Camelot graph as an adjacency list. Run DFS from "Glaston" and BFS from "Glaston". Compare the visiting orders.
2. Write `has_path(graph, start, end)` using DFS that returns `True` if any path exists between two nodes.
3. Write `bfs_shortest_path(graph, start, end)` that returns the actual path (as a list of nodes) or `None` if no path exists.

---

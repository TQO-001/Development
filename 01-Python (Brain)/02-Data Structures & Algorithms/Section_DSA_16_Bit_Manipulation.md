## DSA Section 16: Binary Numbers & Bit Manipulation

Every integer in your program is stored as a sequence of bits (0s and 1s) in memory. Bit manipulation lets you work directly with those bits using special operators. These operations run in `O(1)` at the hardware level — no loops, no data structures, just direct hardware arithmetic. They're used for flags, optimisations, subset generation, and problems that would otherwise need `O(n)` or `O(n²)` solutions.

### 16.1 Binary Representation

The number `13` in binary is `1101`:

```
Bit position:  3   2   1   0
Binary digit:  1   1   0   1
Value:         8 + 4 + 0 + 1 = 13
```

Each bit at position `i` represents `2^i`. The rightmost bit is position 0 (least significant bit, LSB). The leftmost is the most significant bit (MSB).

```python
# Convert between decimal and binary in Python
bin(13)        # '0b1101'  — Python's binary string
bin(255)       # '0b11111111'
int('1101', 2) # 13  — convert binary string to int
format(13, 'b')# '1101'  — without '0b' prefix
format(13, '08b') # '00001101' — padded to 8 bits

# Python integers have arbitrary precision — no fixed-size overflow
big = 2 ** 100   # Works fine
```

### 16.2 The Six Bitwise Operators

```python
a = 0b1100   # 12
b = 0b1010   # 10

# AND (&) — bit is 1 only if BOTH bits are 1
print(a & b)          # 0b1000 = 8   (1100 & 1010 = 1000)

# OR (|) — bit is 1 if EITHER bit is 1
print(a | b)          # 0b1110 = 14  (1100 | 1010 = 1110)

# XOR (^) — bit is 1 if bits are DIFFERENT
print(a ^ b)          # 0b0110 = 6   (1100 ^ 1010 = 0110)

# NOT (~) — flips all bits (returns -(n+1) due to two's complement)
print(~a)             # -13  (in Python's arbitrary precision integers)

# Left shift (<<) — shifts bits left by n positions (multiply by 2^n)
print(a << 1)         # 0b11000 = 24 = 12 × 2
print(a << 2)         # 0b110000 = 48 = 12 × 4

# Right shift (>>) — shifts bits right by n positions (floor divide by 2^n)
print(a >> 1)         # 0b110 = 6 = 12 // 2
print(a >> 2)         # 0b11 = 3 = 12 // 4
```

**Visualised:**

```
a = 1100  (12)
b = 1010  (10)

a & b: 1000  (8)   ← only bits where BOTH are 1
a | b: 1110  (14)  ← bits where EITHER is 1
a ^ b: 0110  (6)   ← bits where they DIFFER
a << 1: 11000 (24) ← everything shifted one position left
a >> 1: 0110  (6)  ← everything shifted one position right
```

### 16.3 Essential Bit Tricks

These patterns appear constantly in interview problems:

```python
n = 13   # 1101

# Check if n is even or odd — O(1)
n & 1 == 0   # True if even (last bit is 0)
n & 1 == 1   # True if odd  (last bit is 1)
# Faster than n % 2 == 0

# Multiply or divide by powers of 2 — O(1)
n << 3   # n × 8   (shift left 3 = multiply by 2^3)
n >> 2   # n // 4  (shift right 2 = divide by 2^2)

# Get the value of bit at position i
def get_bit(n: int, i: int) -> int:
    return (n >> i) & 1   # Shift bit i to position 0, then mask with 1
get_bit(13, 2)   # (1101 >> 2) & 1 = 11 & 1 = 1 ✓ bit 2 of 13 is 1

# Set bit at position i to 1
def set_bit(n: int, i: int) -> int:
    return n | (1 << i)   # Create a mask with only bit i set, then OR
set_bit(13, 1)   # 1101 | 0010 = 1111 = 15

# Clear bit at position i (set to 0)
def clear_bit(n: int, i: int) -> int:
    return n & ~(1 << i)   # Mask with all bits set EXCEPT bit i
clear_bit(13, 0)   # 1101 & 1110 = 1100 = 12

# Toggle bit at position i
def toggle_bit(n: int, i: int) -> int:
    return n ^ (1 << i)   # XOR with a mask — flips only that bit
toggle_bit(13, 1)   # 1101 ^ 0010 = 1111 = 15

# Check if n is a power of 2 — O(1)
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0
# Powers of 2 in binary: 0001, 0010, 0100, 1000
# n-1 flips all trailing zeros and the lowest 1 bit
# n & (n-1) clears the lowest set bit — if n is a power of 2, nothing remains

is_power_of_two(8)    # 1000 & 0111 = 0000 → True
is_power_of_two(12)   # 1100 & 1011 = 1000 → False

# Clear the lowest set bit (lowest 1 bit)
def clear_lowest_bit(n: int) -> int:
    return n & (n - 1)
clear_lowest_bit(12)   # 1100 & 1011 = 1000 = 8

# Count set bits (popcount) — Brian Kernighan's algorithm
def count_set_bits(n: int) -> int:
    count = 0
    while n:
        n &= n - 1    # Clear the lowest set bit each iteration
        count += 1
    return count
count_set_bits(13)   # 1101 has 3 set bits
count_set_bits(255)  # 11111111 has 8 set bits
# Python built-in: bin(n).count('1') or int.bit_count() (Python 3.10+)
```

### 16.4 XOR — The Magic Operator

XOR has three powerful properties that make it uniquely useful:

```
1. x ^ x = 0         — a number XOR'd with itself is 0
2. x ^ 0 = x         — a number XOR'd with 0 is unchanged
3. XOR is commutative and associative (order doesn't matter)
```

These properties solve otherwise tricky problems in O(n) time and O(1) space:

```python
# Find the single non-duplicate in a list where every other appears twice
def single_number(nums: list[int]) -> int:
    result = 0
    for n in nums:
        result ^= n   # Duplicates cancel out (x^x=0), unique remains
    return result

single_number([4, 1, 2, 1, 2])   # 4 → only 4 appears once
# 0 ^ 4 ^ 1 ^ 2 ^ 1 ^ 2
# = 0 ^ 4 ^ (1^1) ^ (2^2)
# = 0 ^ 4 ^ 0 ^ 0 = 4

# Swap two numbers without a temp variable
a, b = 10, 20
a ^= b   # a = a XOR b
b ^= a   # b = b XOR (a XOR b) = original a
a ^= b   # a = (a XOR b) XOR a = original b
# a=20, b=10
```

### 16.5 Bitmasks — Representing Subsets

Each bit of an integer can represent whether a particular element is "included" or not. An integer with `n` bits can represent all `2^n` subsets of a set with `n` elements.

```python
# Represent which of 4 skills Arthur has equipped
# Bit 0 = Slash, Bit 1 = Block, Bit 2 = Parry, Bit 3 = Riposte

skills = 0b0000   # No skills equipped
SLASH   = 1 << 0  # 0001 = 1
BLOCK   = 1 << 1  # 0010 = 2
PARRY   = 1 << 2  # 0100 = 4
RIPOSTE = 1 << 3  # 1000 = 8

# Equip Slash and Parry
skills |= SLASH    # 0001
skills |= PARRY    # 0101

# Check if Block is equipped
(skills & BLOCK) != 0   # False — bit 1 is not set

# Unequip Parry
skills &= ~PARRY   # 0001

# Generate all subsets of [0, 1, 2] using bitmasks
elements = [0, 1, 2]
n = len(elements)
for mask in range(1 << n):   # 0 to 2^n - 1 = 0 to 7
    subset = [elements[i] for i in range(n) if mask & (1 << i)]
    print(f"{mask:03b}: {subset}")
# 000: []
# 001: [0]
# 010: [1]
# 011: [0, 1]
# 100: [2]
# 101: [0, 2]
# 110: [1, 2]
# 111: [0, 1, 2]
```

### 16.6 Common Bit Manipulation Patterns

```python
# Number of bits needed to represent n
def bit_length(n: int) -> int:
    return n.bit_length()   # Python 3 built-in

bit_length(13)   # 4 (1101 needs 4 bits)
bit_length(255)  # 8

# Reverse bits of a 32-bit integer
def reverse_bits(n: int) -> int:
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)   # Take LSB of n, append to result
        n >>= 1
    return result

# Find the position of the highest set bit
import math
def highest_bit_pos(n: int) -> int:
    return int(math.log2(n))   # Or: n.bit_length() - 1

# Check if two numbers have opposite signs
def opposite_signs(a: int, b: int) -> bool:
    return (a ^ b) < 0   # XOR sign bits: different signs → MSB of result is 1
```

### 16.7 Bit Manipulation Quick Reference

| Operation | Code | Notes |
|---|---|---|
| Check if even | `n & 1 == 0` | |
| Multiply by 2^k | `n << k` | |
| Divide by 2^k | `n >> k` | Floor division |
| Get bit i | `(n >> i) & 1` | |
| Set bit i | `n \| (1 << i)` | |
| Clear bit i | `n & ~(1 << i)` | |
| Toggle bit i | `n ^ (1 << i)` | |
| Clear lowest bit | `n & (n - 1)` | |
| Check power of 2 | `n > 0 and (n & (n-1)) == 0` | |
| Count set bits | `bin(n).count('1')` | Or Brian Kernighan's loop |
| Find unique element | XOR all elements | Duplicates cancel |
| Generate all subsets | Loop `mask` from 0 to `(1<<n)-1` | |

---

**Practice:**
1. Write `count_set_bits(n)` using Brian Kernighan's algorithm (the `n & (n-1)` trick). Test it on `n=255` (should be 8) and `n=13` (should be 3).
2. Write `single_number(nums)` that finds the one element that appears once while all others appear exactly twice. Solve it in O(n) time and O(1) space using XOR.
3. Given an integer `n`, generate all subsets of the list `[0, 1, ..., n-1]` using bitmasks. Print each subset alongside its binary mask.

---

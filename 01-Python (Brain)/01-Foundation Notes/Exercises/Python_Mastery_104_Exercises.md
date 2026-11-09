# Python Mastery: 104 Exercises
## Zero to Senior — Sections 1–13

**Format is identical for every exercise. No exceptions.**

```
### [emoji] #N — Title
**Time:** ~X min | **Concept:** one-liner

- Task line
- Task line

**✓ Done when:** concrete, testable criterion.
> 💡 Hint (only where genuinely needed)
```

**Difficulty scale**
| Emoji | Level | Time |
|---|---|---|
| 🟢 | Warm-Up | 5–10 min |
| 🟡 | Core | 10–20 min |
| 🟠 | Applied | 15–25 min |
| 🔴 | Challenge | 20–35 min |
| 💀 | Boss | 35–50 min |

**File naming:** save each scratch file as `arcN-exNN.py` (e.g. `arc1-ex03.py`).

---

## 🏁 Master Checklist

**Arc 1 — OOP (24):** `1☐ 2☐ 3☐ 4☐ 5☐ 6☐ 7☐ 8☐ 9☐ 10☐ 11☐ 12☐ 13☐ 14☐ 15☐ 16☐ 17☐ 18☐ 19☐ 20☐ 21☐ 22☐ 23☐ 24☐`

**Arc 2 — Decorators (16):** `25☐ 26☐ 27☐ 28☐ 29☐ 30☐ 31☐ 32☐ 33☐ 34☐ 35☐ 36☐ 37☐ 38☐ 39☐ 40☐`

**Arc 3 — Generators & Iterators (16):** `41☐ 42☐ 43☐ 44☐ 45☐ 46☐ 47☐ 48☐ 49☐ 50☐ 51☐ 52☐ 53☐ 54☐ 55☐ 56☐`

**Arc 4 — Context Managers (12):** `57☐ 58☐ 59☐ 60☐ 61☐ 62☐ 63☐ 64☐ 65☐ 66☐ 67☐ 68☐`

**Arc 5 — Async & Modules (16):** `69☐ 70☐ 71☐ 72☐ 73☐ 74☐ 75☐ 76☐ 77☐ 78☐ 79☐ 80☐ 81☐ 82☐ 83☐ 84☐`

**Arc 6 — Foundations Stress Test (12):** `85☐ 86☐ 87☐ 88☐ 89☐ 90☐ 91☐ 92☐ 93☐ 94☐ 95☐ 96☐`

**Arc 7 — Synthesis (8):** `97☐ 98☐ 99☐ 100☐ 101☐ 102☐ 103☐ 104☐`

---

# ARC 1 — OOP Deep Cuts
## 24 Exercises | Classes → Inheritance → Dunders → Descriptors

---

### 🟢 #1 — The Bare Class
**Time:** ~5 min | **Concept:** class definition, `__init__`, instance attributes

- Define `BankAccount` with `__init__(self, owner: str, balance: float = 0.0)`.
- Create two instances with different owners.
- Print both `owner` and `balance` attributes directly.

**✓ Done when:** `acc = BankAccount("Thulani", 500.0); print(acc.balance)` outputs `500.0`.

---

### 🟢 #2 — Instance Methods
**Time:** ~8 min | **Concept:** methods that modify `self`

- Add `deposit(self, amount: float)` — adds to balance.
- Add `withdraw(self, amount: float)` — subtracts from balance; print a warning if it would go negative, don't allow it.
- Test: deposit 200, withdraw 50, try to withdraw 1000 (should be blocked).

**✓ Done when:** balance stays non-negative and the blocking message prints.

---

### 🟢 #3 — Class Attribute
**Time:** ~8 min | **Concept:** class-level vs instance-level attributes

- Add a class attribute `transaction_count = 0` directly in the class body (not in `__init__`).
- Increment it by 1 inside both `deposit` and `withdraw` (even when withdrawal is blocked, don't count it).
- Create two accounts, make 3 transactions total, print `BankAccount.transaction_count`.

**✓ Done when:** `BankAccount.transaction_count` equals the total transactions across ALL instances.

---

### 🟡 #4 — `__str__` and `__repr__`
**Time:** ~10 min | **Concept:** dunder display methods

- Add `__str__` returning a human-readable summary, e.g. `"Account(Thulani) — R500.00"`.
- Add `__repr__` returning a developer-readable version, e.g. `"BankAccount(owner='Thulani', balance=500.0)"`.
- Test `print(acc)`, `repr(acc)`, and inspect how it looks in a list: `print([acc])`.

**✓ Done when:** `print(acc)` uses `__str__` and `repr(acc)` uses `__repr__` — they are visibly different strings.

---

### 🟡 #5 — `@property` (Read-Only)
**Time:** ~10 min | **Concept:** computed/controlled attribute access

- Remove direct `self.balance` storage. Instead store it as `self._balance`.
- Add a `@property` called `balance` that returns `self._balance`.
- Try `acc.balance = 999` — it should raise `AttributeError` because there's no setter.

**✓ Done when:** Reading `acc.balance` works; assigning `acc.balance = 999` raises `AttributeError`.
> 💡 A `@property` with no `@balance.setter` is read-only by default.

---

### 🟡 #6 — `@property` + `@setter` with Validation
**Time:** ~12 min | **Concept:** validated attribute assignment

- Add `@balance.setter` that raises `ValueError` if the new value is negative.
- Now use the setter inside `deposit` and `withdraw` instead of directly modifying `_balance`.
- Test setting a negative balance directly: `acc.balance = -100` should raise.

**✓ Done when:** Direct assignment of negative balance raises `ValueError`; deposits and withdrawals still work correctly.

---

### 🟡 #7 — `@classmethod` Alternative Constructor
**Time:** ~12 min | **Concept:** factory class methods

- Add `@classmethod from_dict(cls, data: dict) -> "BankAccount"` that accepts `{"owner": ..., "balance": ...}`.
- Add `@classmethod zero_balance(cls, owner: str) -> "BankAccount"` that creates an account with balance 0.
- Create one account with each method; print both.

**✓ Done when:** Both class methods return proper `BankAccount` instances without calling `__init__` directly.

---

### 🟡 #8 — `@staticmethod`
**Time:** ~8 min | **Concept:** utility functions scoped to a class

- Add `@staticmethod is_valid_owner(name: str) -> bool` — returns `True` if `len(name) >= 2` and `name.isalpha()`.
- Call it WITHOUT instantiating an account: `BankAccount.is_valid_owner("T")` → `False`.
- Use it inside `__init__` to guard against bad owner names (raise `ValueError` if invalid).

**✓ Done when:** `BankAccount("X", 100)` raises `ValueError`; `BankAccount("Thulani", 100)` works fine.

---

### 🟠 #9 — `__eq__`
**Time:** ~10 min | **Concept:** equality comparison between objects

- Add `__eq__(self, other)` — two accounts are equal if both `owner` AND `balance` match.
- Test: two accounts with same owner + balance → `True`; different balance → `False`.
- Without `__eq__`, Python compares by object identity (memory address). Confirm this by checking the default before you add `__eq__`.

**✓ Done when:** Two separately created accounts with identical data return `True` for `==`.

---

### 🟠 #10 — `__lt__` and `sorted()`
**Time:** ~10 min | **Concept:** rich comparison enabling sort

- Add `__lt__(self, other)` that compares accounts by `balance`.
- Create a list of 4 accounts with different balances; call `sorted(accounts)` on it.
- Print the sorted list using your `__str__`.

**✓ Done when:** `sorted()` works on a list of `BankAccount` objects without passing a `key=` argument.
> 💡 `sorted()` uses `__lt__` under the hood.

---

### 🟠 #11 — `__len__` (Transaction History)
**Time:** ~12 min | **Concept:** `len()` on custom objects

- Add `self._history = []` in `__init__`.
- Every completed deposit/withdrawal appends the amount to `_history`.
- Add `__len__` returning `len(self._history)`.
- Test: `len(acc)` should equal the number of completed transactions.

**✓ Done when:** `len(acc)` works and matches the actual count of transactions performed.

---

### 🟠 #12 — `__contains__`
**Time:** ~10 min | **Concept:** `in` operator on custom objects

- Add `__contains__(self, amount)` — returns `True` if `amount` appears in `self._history`.
- Test: `200 in acc` after a deposit of 200 → `True`; `999 in acc` → `False`.

**✓ Done when:** The `in` keyword works naturally on a `BankAccount` instance.

---

### 🟠 #13 — `__iter__`
**Time:** ~10 min | **Concept:** making objects iterable

- Add `__iter__(self)` — returns `iter(self._history)`.
- Use it in a `for amount in acc:` loop to print every transaction.
- Also confirm `list(acc)` returns a copy of the history list.

**✓ Done when:** `for tx in acc: print(tx)` prints each transaction without accessing `_history` directly.

---

### 🟠 #14 — Inheritance Basics
**Time:** ~15 min | **Concept:** subclassing, extending parent behavior

- Create `SavingsAccount(BankAccount)` with an extra attribute `interest_rate: float`.
- Add `apply_interest(self)` — increases balance by `balance * interest_rate`.
- Test: create a SavingsAccount, deposit, apply interest, check balance.
- Confirm `isinstance(savings, BankAccount)` returns `True`.

**✓ Done when:** `SavingsAccount` inherits all `BankAccount` methods AND has its own `apply_interest`.

---

### 🔴 #15 — `super()` and Override
**Time:** ~15 min | **Concept:** calling parent methods, overriding behavior

- Override `withdraw` in `SavingsAccount`: deny any withdrawal that would bring balance below `100.0` (a minimum reserve), raise `ValueError` if attempted.
- Use `super().__init__()` in `SavingsAccount.__init__` — don't re-implement the parent setup.
- Test: try withdrawing past the reserve; confirm the parent's version of `withdraw` is NOT called when your override rejects the amount.

**✓ Done when:** Withdrawing past minimum raises `ValueError`; valid withdrawals still work.

---

### 🔴 #16 — MRO: Method Resolution Order
**Time:** ~15 min | **Concept:** diamond inheritance, MRO chain

- Define: `class A:` → has `speak()` returning `"A"`. `class B(A):` → `speak()` returning `"B"`. `class C(A):` → `speak()` returning `"C"`. `class D(B, C):` — inherits from both.
- Print `D.__mro__` and read the full chain.
- Call `D().speak()` — note which class's method wins and why.
- Write a comment predicting the MRO *before* running it, then compare.

**✓ Done when:** Your comment's predicted MRO order matches the real `D.__mro__` output.

---

### 🟠 #17 — Abstract Base Classes
**Time:** ~15 min | **Concept:** enforcing interface contracts

- `from abc import ABC, abstractmethod`.
- Define `abstract class Account(ABC):` with abstract method `calculate_interest(self) -> float`.
- Try instantiating `Account()` — confirm it raises `TypeError`.
- Create two concrete subclasses: `FixedAccount` (flat rate) and `TieredAccount` (rate based on balance). Both implement `calculate_interest`.

**✓ Done when:** `Account()` raises `TypeError`; both subclasses instantiate and return different interest values.

---

### 🟠 #18 — `@dataclass`
**Time:** ~12 min | **Concept:** auto-generated `__init__`, `__repr__`, `__eq__`

- Rewrite a minimal `Transaction` class as a `@dataclass` with fields: `amount: float`, `type: str`, `timestamp: str`.
- Note what you get for free (no need to write `__init__`, `__repr__`, or `__eq__`).
- Use `field(default_factory=...)` to set `timestamp` to the current time automatically.
- Test equality between two identical transactions.

**✓ Done when:** Two `Transaction` objects with the same fields are `==` without writing `__eq__`.
> 💡 `from dataclasses import dataclass, field; from datetime import datetime`

---

### 🔴 #19 — `__slots__`
**Time:** ~15 min | **Concept:** memory optimization, attribute restriction

- Add `__slots__ = ("owner", "_balance", "_history")` to `BankAccount`.
- Try adding a new attribute dynamically: `acc.nickname = "main"` — confirm `AttributeError`.
- Use `tracemalloc` to snapshot memory: instantiate 100,000 objects with `__slots__` vs 100,000 without (use two separate classes). Compare peak memory.

**✓ Done when:** Dynamic attribute assignment raises; the memory snapshot shows `__slots__` version uses meaningfully less RAM.

---

### 🔴 #20 — `__call__`
**Time:** ~10 min | **Concept:** making objects callable

- Create a standalone class `InterestCalculator` with `__init__(self, rate: float)`.
- Implement `__call__(self, balance: float) -> float` — returns `balance * self.rate`.
- Use it like a function: `calc = InterestCalculator(0.07); print(calc(1000))` → `70.0`.

**✓ Done when:** `calc(1000)` works; `callable(calc)` returns `True`.

---

### 🔴 #21 — Object as Context Manager
**Time:** ~12 min | **Concept:** `__enter__` / `__exit__` on a regular class

- Add `__enter__(self)` to `BankAccount` — prints `"Opening session for {self.owner}"` and returns `self`.
- Add `__exit__(self, exc_type, exc_val, exc_tb)` — prints `"Closing session. Final balance: {self.balance}"` and returns `False`.
- Use it: `with BankAccount("Thulani", 500) as acc: acc.deposit(200)`.

**✓ Done when:** Both messages print automatically; an exception inside the block still propagates (returns `False`).

---

### 🔴 #22 — Mixin Pattern
**Time:** ~15 min | **Concept:** composing behavior from multiple classes

- Write `class LogMixin:` with `log(self, msg: str)` — prints `f"[{self.__class__.__name__}] {msg}"`.
- Create `class LoggedAccount(LogMixin, BankAccount):` — override `deposit` to call `self.log(f"Deposit: {amount}")` then call `super().deposit(amount)`.
- Confirm that `LoggedAccount` correctly uses MRO so `super().deposit()` hits `BankAccount.deposit`.

**✓ Done when:** Depositing into a `LoggedAccount` prints both the log line and completes the deposit.

---

### 💀 #23 — BOSS A: Full Vehicle Hierarchy
**Time:** ~40 min | **Concept:** multi-level inheritance, mixins, isinstance, super()

Build a hierarchy:
- `Vehicle(ABC)` — abstract, has `make`, `model`, `year`; abstract method `fuel_type() -> str`; `__repr__`; `age` property.
- `Car(Vehicle)` — concrete, adds `num_doors`; implements `fuel_type() -> "petrol"`.
- `Truck(Vehicle)` — adds `payload_kg`; `fuel_type() -> "diesel"`.
- `ElectricMixin` — adds `battery_kwh`; overrides `fuel_type() -> "electric"`.
- `ElectricCar(ElectricMixin, Car)` — inherits both; `fuel_type()` must return `"electric"` (mixin wins).
- Verify: `isinstance(ElectricCar(...), Vehicle)` is `True`; `isinstance(ElectricCar(...), Car)` is `True`.
- Print `ElectricCar.__mro__` and confirm `ElectricMixin` appears before `Car`.

**✓ Done when:** All 5 classes work; MRO is correct; `isinstance` checks all pass; `__repr__` is readable on all.

---

### 💀 #24 — BOSS B: Descriptor
**Time:** ~40 min | **Concept:** `__get__`, `__set__`, `__delete__`, descriptor protocol

- Write a `PositiveNumber` descriptor class with `__set_name__`, `__get__`, `__set__`, `__delete__`.
- `__set__` raises `ValueError` if value `<= 0`.
- Apply it to a `Circle` class: `radius = PositiveNumber()` and `Circle.area` property using `math.pi * self.radius ** 2`.
- Apply it to a `Rectangle` class: both `width = PositiveNumber()` and `height = PositiveNumber()`.
- Test valid values work; test `circle.radius = -5` raises `ValueError`; test `del circle.radius` triggers `__delete__`.

**✓ Done when:** The same descriptor class enforces the constraint on two different classes without any duplication.

---

# ARC 2 — Decorator Mastery
## 16 Exercises | Wrapping → Factories → Class-Based → Advanced

---

### 🟢 #25 — Bare Wrapper
**Time:** ~8 min | **Concept:** basic decorator structure

- Write `def log_call(func):` — `wrapper` prints `f"Calling {func.__name__}..."` before calling `func()`.
- Apply it to `def greet(): print("Hello!")`.
- Confirm the log line appears before "Hello!".

**✓ Done when:** `greet()` prints the log line first, then "Hello!".

---

### 🟢 #26 — `@wraps` and Metadata
**Time:** ~8 min | **Concept:** preserving function identity

- Add `from functools import wraps` and `@wraps(func)` inside the decorator from #25.
- Without `@wraps`: print `greet.__name__` — it shows `"wrapper"`. With `@wraps`: it shows `"greet"`.
- Also check `greet.__doc__` before and after adding `@wraps`.

**✓ Done when:** `greet.__name__` is `"greet"` and `greet.__doc__` is the original docstring after adding `@wraps`.

---

### 🟡 #27 — Return Value Passthrough
**Time:** ~10 min | **Concept:** not dropping the return value

- Write `@validate_output` — calls `func(*args, **kwargs)`, captures result; if result is `None`, raises `ValueError("Function returned None")`.
- Apply to `def divide(a, b): return a / b if b != 0 else None`.
- Test: `divide(10, 2)` → returns `5.0`; `divide(10, 0)` → decorator raises `ValueError`.

**✓ Done when:** The non-None result passes through; the None result triggers the decorator's raise.

---

### 🟡 #28 — Decorator Factory `@repeat(n)`
**Time:** ~12 min | **Concept:** decorator that takes an argument

- Write `def repeat(n):` returning a decorator that runs `func` exactly `n` times.
- `@repeat(3) def say_hi(): print("Hi!")` — calling `say_hi()` prints "Hi!" three times.
- Structure: outer(n) → decorator(func) → wrapper() — three levels, not two.

**✓ Done when:** `say_hi()` prints exactly `n` lines; changing `n` changes the count.
> 💡 The extra nesting is what makes it a decorator factory vs a plain decorator.

---

### 🟡 #29 — `@count_calls` with State
**Time:** ~12 min | **Concept:** closure-captured mutable state

- Write `@count_calls` — tracks how many times the decorated function has been called; stores count as an attribute ON the wrapper function itself (`wrapper.call_count = 0`).
- Apply to any function; after 5 calls print `func.call_count`.

**✓ Done when:** `my_func.call_count` accurately reflects the number of calls made.

---

### 🟠 #30 — Class-Based Decorator
**Time:** ~15 min | **Concept:** `__init__` + `__call__` as decorator

- Rewrite `@count_calls` as a class: `class CountCalls:` with `__init__(self, func)` and `__call__(self, *args, **kwargs)`.
- Track call count as `self.call_count`.
- Apply with `@CountCalls` syntax — no parentheses needed here.
- Confirm `my_func.call_count` still works after wrapping.

**✓ Done when:** Class-based version behaves identically to the closure-based one in #29.

---

### 🟠 #31 — `@clamp(low, high)`
**Time:** ~15 min | **Concept:** decorator factory that post-processes the return value

- Write `@clamp(low, high)` — wraps any function that returns a number; if the return value falls outside `[low, high]`, clamp it to the boundary.
- Apply to `def compute(x): return x * 3` with `@clamp(0, 100)`.
- Test: `compute(5)` → `15` (in range); `compute(50)` → `100` (clamped); `compute(-10)` → `0` (clamped).

**✓ Done when:** All three test cases produce the expected clamped values.

---

### 🟠 #32 — `@memoize_with_limit(maxsize)`
**Time:** ~20 min | **Concept:** LRU-style cache from scratch using `OrderedDict`

- Write `@memoize_with_limit(maxsize=4)` using `collections.OrderedDict` as the cache.
- On a cache hit: move the key to the end (most recently used) and return stored value.
- On a cache miss: if cache is at maxsize, pop the FIRST item (oldest); store and return the new result.
- Apply to a `time.sleep(0.5)` function; prove hits return instantly.

**✓ Done when:** After filling the cache to 4 entries, the 5th unique call evicts the oldest; cache hits are fast.
> 💡 `OrderedDict.move_to_end(key)` and `OrderedDict.popitem(last=False)` are the key methods.

---

### 🔴 #33 — Async Decorator: `@async_timer`
**Time:** ~15 min | **Concept:** decorating async functions

- Write `def async_timer(func):` — the wrapper must be `async def wrapper(*args, **kwargs):`; use `time.perf_counter()` around `await func(*args, **kwargs)`.
- Apply to `async def slow_fetch(): await asyncio.sleep(0.3); return "data"`.
- Run with `asyncio.run(slow_fetch())`.

**✓ Done when:** Timing line prints automatically; result `"data"` is still returned correctly.
> 💡 Forgetting `await` inside the wrapper is the most common mistake here.

---

### 🔴 #34 — Argument Normalizer
**Time:** ~15 min | **Concept:** inspecting and modifying arguments before function runs

- Write `@normalize_strings` — before calling `func`, apply `.strip().lower()` to every argument that is a `str`.
- Apply to `def lookup(key: str, table: str): print(f"Looking up '{key}' in '{table}'")`
- Test: `lookup("  HELLO  ", "  MY_TABLE  ")` should print with stripped, lowercased strings.

**✓ Done when:** All str args are cleaned before the function body ever sees them.
> 💡 Iterate over `args`, rebuild a new tuple, same for `kwargs`.

---

### 🔴 #35 — Stacking Order Proof
**Time:** ~20 min | **Concept:** decorator application order (bottom-up)

- Write three decorators: `@log` (prints name), `@timer` (prints time), `@retry_once` (retries once on any exception).
- Stack them in order A: `@log / @timer / @retry_once` on a function.
- Stack in order B: `@retry_once / @timer / @log` on the same function.
- Run both and compare printed output carefully.
- In a comment, write out the exact execution order for each stack.

**✓ Done when:** Your comment accurately predicts the order for both stacks before you run them.

---

### 🔴 #36 — `@enforce_types`
**Time:** ~20 min | **Concept:** runtime type checking via `inspect`

- Write `@enforce_types` — uses `inspect.signature(func).parameters` and `func.__annotations__` to check each passed argument against its annotated type.
- If a type mismatch is found, raise `TypeError(f"Argument '{name}' expected {expected}, got {actual}")`.
- Apply to `def add(a: int, b: int) -> int: return a + b`.
- Test: `add(1, 2)` works; `add(1, "two")` raises `TypeError`.

**✓ Done when:** Annotated type violations raise `TypeError` with a clear message; unannotated args are ignored.

---

### 💀 #37 — BOSS A: `@cache_to_disk`
**Time:** ~40 min | **Concept:** persistent caching across program runs

- Write `@cache_to_disk(path="cache.json")` — stores results keyed by `f"{func.__name__}:{args}"` in a JSON file.
- On each call: load the JSON (or start with `{}`); check for a key hit; if miss, call `func`, store result, save JSON.
- Apply to `def slow_computation(n): time.sleep(1); return n ** 2`.
- First run: computes and saves. Second run (re-run the script): loads from file — no sleep delay.

**✓ Done when:** The second program run returns instantly for the same arguments, with no `time.sleep` delay observed.

---

### 💀 #38 — BOSS B: Decorator Registry
**Time:** ~35 min | **Concept:** decorators as registration mechanisms

- Write a `Registry` class with `self._store = {}`.
- `@registry.register("name")` stores the decorated function under `"name"`.
- `registry.run("name", *args, **kwargs)` looks up and calls the function.
- `registry.list()` prints all registered function names.
- Register 4 functions: `add`, `subtract`, `multiply`, `shout` (str.upper).
- Run all 4 through the registry.

**✓ Done when:** `registry.run("shout", "hello")` returns `"HELLO"` and `registry.list()` prints all 4 names.

---

### 🟡 #39 — Decorator Order: `@uppercase` + `@strip`
**Time:** ~12 min | **Concept:** decorators compose differently depending on order

- Write `@uppercase` — calls `func`, returns result `.upper()`.
- Write `@strip` — calls `func`, returns result `.strip()`.
- Apply `@uppercase / @strip` to a function returning `"  hello  "`.
- Apply `@strip / @uppercase` to the same function.
- Print both outputs and explain the difference in a comment.

**✓ Done when:** The two outputs are different and your comment correctly explains why.

---

### 🟠 #40 — `@singleton`
**Time:** ~15 min | **Concept:** class instantiation control via a decorator

- Write `@singleton` — ensures only one instance of the decorated class ever exists; subsequent calls to `ClassName()` return the original instance.
- Apply to a `Config` class with an `__init__` that prints `"Config initialized"`.
- Call `Config()` 3 times and confirm `"Config initialized"` prints only once.
- Confirm all 3 returned objects are `is` the same object.

**✓ Done when:** `Config() is Config()` is `True` and `"Config initialized"` appears exactly once.

---

# ARC 3 — Generator & Iterator Mastery
## 16 Exercises | yield → Protocol → send() → Pipelines

---

### 🟢 #41 — First `yield`
**Time:** ~5 min | **Concept:** generator function vs regular function

- Write `def count_up(n):` that `yield`s integers from 1 to `n`.
- Get a generator object: `g = count_up(3)`.
- Call `next(g)` three times manually. Then call it a fourth time and catch `StopIteration`.

**✓ Done when:** Three values come out, then `StopIteration` is raised (don't let it crash — catch it).

---

### 🟢 #42 — Generator vs `return`
**Time:** ~8 min | **Concept:** lazy evaluation — values aren't produced until asked

- Write `def gen_with_print(n):` — before each `yield`, print `f"Producing {i}"`.
- Create the generator object; notice NOTHING prints yet.
- Call `next()` once — only ONE "Producing..." line appears.
- Explain in a comment why the prints are lazy.

**✓ Done when:** Creating the generator produces zero output; each `next()` produces exactly one print.

---

### 🟡 #43 — Infinite Counter
**Time:** ~10 min | **Concept:** infinite generator, `itertools.islice`

- Write `def counter(start=0, step=1):` that `yield`s forever.
- Use `from itertools import islice` to safely take the first 10 values.
- Print as a list.

**✓ Done when:** `list(islice(counter(0, 5), 10))` → `[0, 5, 10, ..., 45]` and the program terminates.

---

### 🟡 #44 — `sys.getsizeof()` Comparison
**Time:** ~10 min | **Concept:** memory difference between list and generator

- Create a list comprehension for `x**2` for `x` in `range(1_000_000)`.
- Create a generator expression for the same.
- `import sys; print(sys.getsizeof(list_version), sys.getsizeof(gen_version))`.
- In a comment, explain the size difference using your own words.

**✓ Done when:** The list size is in megabytes; the generator size is under 200 bytes; you can explain why.

---

### 🟡 #45 — Filtering Generator
**Time:** ~10 min | **Concept:** conditional `yield`

- Write `def only_evens(iterable):` — yields only even numbers from any iterable.
- Test it with `range(20)`, with a list of mixed numbers, and with another generator.
- Do NOT use a list comprehension inside it — raw `for` + `if` + `yield` only.

**✓ Done when:** `list(only_evens(range(10)))` → `[0, 2, 4, 6, 8]`.

---

### 🟡 #46 — Three-Stage Generator Pipeline
**Time:** ~15 min | **Concept:** chaining generators without intermediate lists

- `def produce(n):` yields integers 1 to n.
- `def square(iterable):` takes a generator, yields each value squared.
- `def keep_large(iterable, threshold):` yields only values above threshold.
- Chain: `for val in keep_large(square(produce(20)), 200): print(val)`.
- Add a `print("processing...")` inside each generator to prove laziness.

**✓ Done when:** The prints interleave (one from each stage per value) instead of all stage-1 prints happening first.

---

### 🟠 #47 — `yield from` (Flatten)
**Time:** ~12 min | **Concept:** delegating to a sub-generator

- Write `def flatten(nested):` that flattens ONE level of nesting using `yield from`.
- Input: `[[1, 2], [3, 4], [5, 6]]` → yields `1, 2, 3, 4, 5, 6`.
- Do it in a single `for item in nested: yield from item` pattern.
- Also try it with tuples nested inside a list.

**✓ Done when:** `list(flatten([[1,2],[3,4]]))` → `[1, 2, 3, 4]`.

---

### 🟠 #48 — Custom Iterator Class
**Time:** ~18 min | **Concept:** `__iter__` + `__next__` iterator protocol

- Write `class Range2:` with `__init__(self, start, stop, step=1)`.
- Implement `__iter__(self): return self`.
- Implement `__next__(self):` advancing by `step`, raising `StopIteration` when `>= stop`.
- Confirm `for i in Range2(0, 10, 2): print(i)` works identically to `range(0, 10, 2)`.

**✓ Done when:** `list(Range2(1, 10, 3))` → `[1, 4, 7]`.

---

### 🟠 #49 — `send()` into a Generator
**Time:** ~18 min | **Concept:** two-way communication with generators

- Write `def running_total():` — starts at 0; each `yield` returns the current total; each `send(value)` adds value to the total.
- Usage pattern:
  ```python
  gen = running_total()
  next(gen)          # Prime the generator (required first step)
  gen.send(10)       # → 10
  gen.send(25)       # → 35
  gen.send(5)        # → 40
  ```

**✓ Done when:** Each `send()` returns the updated running total correctly.
> 💡 The first `next()` is mandatory — you must advance the generator to the first `yield` before you can `send()`.

---

### 🟠 #50 — Generator `.close()` and `GeneratorExit`
**Time:** ~12 min | **Concept:** generator lifecycle, cleanup on early termination

- Write a generator that catches `GeneratorExit` inside a `try/finally` and prints `"Generator cleaned up."` in the `finally` block.
- Create the generator, call `next()` twice, then call `.close()`.
- Confirm the cleanup message appears.

**✓ Done when:** `.close()` triggers the `finally` block and prints the cleanup message.

---

### 🔴 #51 — Sentinel Value via `send()`
**Time:** ~18 min | **Concept:** stopping a generator via a signal

- Write a generator `def controlled_counter():` that yields incrementing integers; if `send("stop")` is called, it breaks its internal loop and returns (causing `StopIteration`).
- Test: send normal values (they're ignored, counter just increments); send `"stop"` — generator exits cleanly.

**✓ Done when:** `gen.send("stop")` causes the generator to exit and subsequent `next()` raises `StopIteration`.

---

### 🔴 #52 — `tee()` Replacement
**Time:** ~20 min | **Concept:** shared buffer between multiple independent iterators

- Write `def my_tee(iterable, n=2):` that returns `n` independent iterators over the same data.
- Internally: consume from the original iterator one item at a time; maintain `n` separate `deque` buffers; each iterator reads from its own buffer.
- Test: `a, b = my_tee([1, 2, 3, 4])` — advance `a` twice, then advance `b` four times; both see all values.

**✓ Done when:** Both iterators produced from `my_tee` see all original values independently, even when advanced at different rates.
> 💡 `from collections import deque` is your buffer. Each of `n` outputs has its own deque.

---

### 🔴 #53 — Paginated Generator
**Time:** ~15 min | **Concept:** chunking data lazily

- Write `def paginate(data, page_size):` yielding successive sublists of `page_size` items.
- Last page may be smaller than `page_size`.
- Add `print(f"Fetching page {page_num}")` before each `yield` to prove laziness.
- Test with 47 items and `page_size=10`.

**✓ Done when:** Calling `next()` once shows exactly one "Fetching page" message; converting to `list()` shows 5 pages (4 full + 1 partial).

---

### 🔴 #54 — Memory Benchmark: List vs Generator
**Time:** ~15 min | **Concept:** quantifying the memory benefit with real numbers

- Use `tracemalloc` to measure peak memory for:
  - (a) Building `[x**2 for x in range(500_000)]` in a list.
  - (b) Iterating `(x**2 for x in range(500_000))` via a loop that sums values.
- Print peak memory for each in KB. Print the ratio.

**✓ Done when:** You have two real memory numbers and can state the ratio in a comment.

---

### 💀 #55 — BOSS A: Lazy CSV Reader
**Time:** ~40 min | **Concept:** production-grade lazy file processing

- Create a CSV file with a header row and 20 data rows; include 3 deliberately malformed rows (wrong number of columns).
- Write `def read_csv(filepath):` — a generator that:
  - Reads the file lazily line by line.
  - Parses the first line as headers.
  - For each subsequent line: splits by comma; if column count doesn't match header count, `print(f"Skipping malformed row: {line}")` and `continue`.
  - Yields each valid row as a `dict` keyed by header names.
- Confirm only valid rows are yielded; malformed rows log and skip.

**✓ Done when:** Generator yields exactly 17 valid dict rows; 3 malformed rows log a skip message.

---

### 💀 #56 — BOSS B: Producer / Consumer with Lazy Generators
**Time:** ~40 min | **Concept:** generator-based data pipeline with visible execution flow

- `def producer(n):` — yields `n` task strings like `"task_1"`, `"task_2"`, etc. Prints `"Producing task_N"` before each yield.
- `def consumer(source, limit):` — takes at most `limit` items from `source`; for each: prints `"Processing task_N"`; yields the reversed string.
- Chain them: `for result in consumer(producer(20), 7): print(f"Result: {result}")`.
- The execution trace should interleave: produce → consume → produce → consume.

**✓ Done when:** The printed trace shows interleaving (not all produces first, then all consumes); exactly 7 tasks are processed.

---

# ARC 4 — Context Manager Mastery
## 12 Exercises | Class-Based → @contextmanager → ExitStack → Async

---

### 🟢 #57 — Simplest CM
**Time:** ~8 min | **Concept:** `__enter__` and `__exit__` structure

- Write `class Greeter:` with `__enter__` printing `"Entering"` and returning `self`; `__exit__` printing `"Exiting"`.
- Use it: `with Greeter(): print("Inside")`.
- Deliberately raise an exception inside the block — confirm `"Exiting"` still prints.

**✓ Done when:** `"Exiting"` appears whether the block completes normally or raises.

---

### 🟢 #58 — `@contextmanager` Hello World
**Time:** ~8 min | **Concept:** generator-based context manager

- Rewrite `Greeter` as a `@contextmanager` function (4 lines or fewer: print, yield, print).
- Confirm behavior is identical to #57.
- Look at the result of `type()` on the context manager object — note it's not your function.

**✓ Done when:** Behavior is identical to #57; the implementation uses no class, only `@contextmanager` + `yield`.

---

### 🟡 #59 — File CM with Exception Test
**Time:** ~12 min | **Concept:** resource cleanup under exceptions

- Write a class-based CM `SafeReader` that opens a file in `__enter__`; closes in `__exit__`.
- `__exit__` prints whether it closed cleanly or after an exception.
- Test 1: clean read — confirm file is closed after block.
- Test 2: raise `ValueError` inside block — confirm file is still closed.

**✓ Done when:** File closes in both test cases; the `__exit__` message correctly identifies which path was taken.

---

### 🟡 #60 — Mock DB Transaction CM
**Time:** ~15 min | **Concept:** commit/rollback pattern without a real database

- `@contextmanager def transaction(db: dict):` — `db` is a plain Python dict representing a database.
- On entry: snapshot `db` state (deepcopy).
- `yield db` — the block may modify `db` freely.
- On clean exit: commit (leave changes in place), print `"Committed"`.
- On exception: restore snapshot, print `"Rolled back"`, re-raise.

**✓ Done when:** Clean block keeps changes; excepting block restores original state exactly.

---

### 🟠 #61 — `suppress_errors` CM
**Time:** ~12 min | **Concept:** selective exception suppression

- Write `@contextmanager def suppress_errors(*exc_types):` — catches only the listed exception types and returns `True` (swallows them); all other exceptions propagate.
- Test 1: `with suppress_errors(ValueError): int("bad")` — no crash.
- Test 2: `with suppress_errors(ValueError): 1 / 0` — `ZeroDivisionError` still propagates.

**✓ Done when:** Test 1 runs silently; Test 2 raises, even though it's inside a `suppress_errors` block.

---

### 🟠 #62 — Profiling CM
**Time:** ~15 min | **Concept:** timing + optional memory tracking

- Write `@contextmanager def profile_block(label, track_memory=False):`.
- If `track_memory=True`: start/stop `tracemalloc`, print peak KB.
- Always print `f"[{label}] Time: {elapsed_ms:.2f}ms"`.
- Test with two blocks: one list build (with memory) and one pure compute (without).

**✓ Done when:** Both blocks print timing; only the memory-tracked one prints peak RAM.

---

### 🟠 #63 — Temporary Directory CM
**Time:** ~15 min | **Concept:** file system resource management

- `@contextmanager def temp_dir(prefix="tmp_"):` — creates a temp directory on enter (using `tempfile.mkdtemp`); yields its `Path`; deletes the directory recursively in `finally` (using `shutil.rmtree`).
- Inside the block: create a file inside it and read it back.
- After the block: confirm the directory no longer exists.

**✓ Done when:** Directory exists during block; `Path(dir).exists()` is `False` immediately after.

---

### 🔴 #64 — `ExitStack` for Dynamic Files
**Time:** ~20 min | **Concept:** variable number of context managers

- Build a list of 5 filenames dynamically.
- Use `with ExitStack() as stack:` and `stack.enter_context(open(path, "w"))` in a loop.
- Write a line to each; confirm all are written and closed after the block.
- Without `ExitStack`, prove this can't be done cleanly with static `with` statements when the file count is dynamic.

**✓ Done when:** All 5 files are written and properly closed; the code works regardless of how many filenames are in the list.

---

### 🔴 #65 — Reusable CM
**Time:** ~12 min | **Concept:** CM instances can be reused

- Write a class-based `Counter` CM that increments `self.enter_count` in `__enter__`.
- Use it in two separate `with` blocks:
  ```python
  cm = Counter()
  with cm: pass
  with cm: pass
  print(cm.enter_count)  # Should be 2
  ```

**✓ Done when:** `cm.enter_count` is 2 after two `with` uses, proving `__enter__` ran twice.

---

### 🔴 #66 — CM That Returns and Validates a Value
**Time:** ~20 min | **Concept:** `__enter__` returning data; `__exit__` validating it

- Write a CM whose `__enter__` returns an empty dict.
- In `__exit__`: if no exception occurred, check the dict has `"name"` and `"value"` keys. If missing, raise `KeyError`.
- Test 1: block sets both keys → exits cleanly.
- Test 2: block sets only `"name"` → `__exit__` raises.
- Test 3: block raises `RuntimeError` → `__exit__` skips validation and propagates original.

**✓ Done when:** All three test cases behave as specified.

---

### 💀 #67 — BOSS A: Async Context Manager
**Time:** ~35 min | **Concept:** `__aenter__` / `__aexit__`, async with

- Write `class AsyncTimer:` with `async def __aenter__(self)` and `async def __aexit__(self, ...)`.
- On enter: record start time. On exit: print elapsed time in ms.
- Use it: `async with AsyncTimer(): await asyncio.sleep(0.2)`.
- Also implement via `@asynccontextmanager` (from `contextlib`) and confirm both work identically.

**✓ Done when:** Both class-based and `@asynccontextmanager` versions print the elapsed time for an `async with` block.

---

### 💀 #68 — BOSS B: Audit Log CM
**Time:** ~40 min | **Concept:** logging + selective suppression + exception propagation

- Write `@contextmanager def audit_log(label):` that:
  - Prints `f"[{timestamp}] ENTER: {label}"` on entry.
  - Prints `f"[{timestamp}] EXIT OK: {label}"` on clean exit.
  - Prints `f"[{timestamp}] EXIT ERROR ({exc_type.__name__}): {label}"` on exception.
  - Suppresses `PermissionError` only (returns True for it) — prints a special `"SUPPRESSED"` log line.
  - Propagates all other exceptions.
- Test all three paths: clean, `PermissionError`, `ValueError`.

**✓ Done when:** Clean exits and `PermissionError` both allow the script to continue; `ValueError` propagates.

---

# ARC 5 — Async & Modules
## 16 Exercises | Coroutines → Gather → Queue → Packages

---

### 🟢 #69 — First Coroutine
**Time:** ~8 min | **Concept:** `async def`, `await`, `asyncio.run()`

- Write `async def hello():` — prints `"Starting"`, `await asyncio.sleep(1)`, prints `"Done"`.
- Run with `asyncio.run(hello())`.
- Note that `asyncio.sleep` is NOT the same as `time.sleep` — it doesn't block the event loop.

**✓ Done when:** "Starting" and "Done" print with a ~1 second gap; no `RuntimeError`.

---

### 🟢 #70 — Sequential vs Concurrent (setup)
**Time:** ~10 min | **Concept:** seeing the difference between `await` in a loop vs `gather`

- Write two coroutines: `fast()` sleeps 1s, `slow()` sleeps 2s.
- Run them **sequentially** with two `await` calls; time total with `time.perf_counter`. It should take ~3s.
- Note down the time — you'll compare it in #71.

**✓ Done when:** Total time is ~3 seconds (1+2).

---

### 🟡 #71 — `asyncio.gather()`
**Time:** ~10 min | **Concept:** true concurrency via gather

- Take the same `fast()` and `slow()` coroutines from #70.
- Run them with `await asyncio.gather(fast(), slow())`.
- Time the total — it should be ~2s (the slower one), not ~3s.
- Print both return values from `gather` (it returns a list).

**✓ Done when:** Total time is ~2s; both results are captured from `gather`'s return value.

---

### 🟡 #72 — `asyncio.create_task()`
**Time:** ~12 min | **Concept:** scheduling tasks explicitly

- Write `async def main():` — creates two tasks with `asyncio.create_task()`, then `await`s both.
- Add `print("Task created")` after each `create_task` — confirm they don't start immediately.
- Add `print("Starting")` at the top of each coroutine — confirm they start only when awaited.

**✓ Done when:** You can explain the difference between `create_task` (schedules) and `await` (runs).

---

### 🟡 #73 — `asyncio.wait_for()` Timeout
**Time:** ~12 min | **Concept:** bounding how long you wait for a coroutine

- Write `async def slow_op(): await asyncio.sleep(5); return "done"`.
- Wrap it in `await asyncio.wait_for(slow_op(), timeout=1.0)`.
- Catch `asyncio.TimeoutError` and print `"Operation timed out."`.
- Confirm the total script runtime is ~1s, not ~5s.

**✓ Done when:** `TimeoutError` is caught; script ends in ~1 second.

---

### 🟠 #74 — `asyncio.Semaphore` Rate Limiting
**Time:** ~15 min | **Concept:** limiting concurrent coroutines

- Create 10 coroutines, each sleeping 1 second.
- Without a semaphore: all 10 run at once, total ~1s.
- With `asyncio.Semaphore(3)`: only 3 run at once, total ~4s (10/3 rounded up).
- Print which coroutine is running and when (with a timestamp or counter).

**✓ Done when:** With semaphore=3, total time is ~4s and at most 3 "Running..." messages appear per second.

---

### 🟠 #75 — `asyncio.Queue`: Producer / Consumer
**Time:** ~18 min | **Concept:** async producer-consumer pattern

- `async def producer(queue):` — puts 10 items into the queue with `await queue.put(item)`.
- `async def consumer(queue):` — loops `await queue.get()` 10 times; prints each item; calls `queue.task_done()`.
- Run both concurrently via `asyncio.gather`.
- Use `asyncio.Queue()` (no maxsize) — so producer runs freely.

**✓ Done when:** All 10 items are produced and consumed; both coroutines complete without deadlock.

---

### 🟠 #76 — Error Handling in `gather`
**Time:** ~15 min | **Concept:** partial failures in concurrent tasks

- Create 3 coroutines: 2 succeed, 1 raises `ValueError`.
- Default `gather` behavior: the exception propagates immediately. Show this.
- With `return_exceptions=True`: all results come back; the exception is returned as a value in the list instead of propagating. Show this.
- Filter the results to separate successes from exceptions.

**✓ Done when:** You demonstrate both behaviors and can filter out exception objects from the results list.

---

### 🔴 #77 — Async Generator
**Time:** ~18 min | **Concept:** `async def` with `yield`, `async for`

- Write `async def ticker(n, delay):` — an async generator that yields integers 1 to n with `await asyncio.sleep(delay)` between each.
- Consume it with `async for val in ticker(5, 0.5): print(val)`.
- Confirm each number prints ~0.5s apart.

**✓ Done when:** 5 numbers print with ~0.5s gaps between them, using `async for`, not `next()`.

---

### 🔴 #78 — `run_in_executor`
**Time:** ~15 min | **Concept:** offloading blocking sync code to a thread pool

- Write `def blocking_task(n):` — `time.sleep(n); return f"done after {n}s"`.
- Without executor: calling it from async code blocks the entire event loop.
- With executor: `await loop.run_in_executor(None, blocking_task, 2)` — other coroutines still run during the sleep.
- Prove it: run `run_in_executor` AND a concurrent `asyncio.sleep(0.5)` task at the same time; confirm the 0.5s task finishes first.

**✓ Done when:** The concurrent coroutine finishes before the blocking task completes, proving the event loop wasn't blocked.

---

### 🔴 #79 — Threading vs Asyncio Comparison
**Time:** ~20 min | **Concept:** when to use each concurrency model

- Implement "10 fake HTTP requests" (each `sleep(1)`) in two ways:
  - (a) `threading.Thread` — 10 threads.
  - (b) `asyncio.gather` — 10 coroutines.
- Time both. Both should take ~1s total.
- In a 5-bullet comment, list the tradeoffs of each approach based on what you observed.

**✓ Done when:** Both approaches complete in ~1s AND you have a written comparison comment.

---

### 🟠 #80 — `__all__` in a Module
**Time:** ~12 min | **Concept:** controlling public API of a module

- Create `mymodule.py` with 5 functions: `alpha`, `beta`, `gamma`, `_private`, `helper`.
- Define `__all__ = ["alpha", "beta", "gamma"]` (exclude `_private` and `helper`).
- In a test script: `from mymodule import *` — confirm only `alpha`, `beta`, `gamma` are available.
- Also test `from mymodule import helper` directly — confirm that DOES work (star import vs direct import are different).

**✓ Done when:** `dir()` after `import *` shows only the 3 listed names; `helper` is still importable directly.

---

### 🟠 #81 — Relative Imports in a Package
**Time:** ~15 min | **Concept:** `.` and `..` relative import syntax

- Build: `pkg/__init__.py`, `pkg/config.py` (constant `VERSION = "2.0"`), `pkg/utils/formatter.py`.
- In `formatter.py`: import `VERSION` from `config.py` using `from ..config import VERSION`.
- From outside `pkg/`, run `from pkg.utils.formatter import format_thing` (or similar) and confirm `VERSION` is accessible inside the function.
- Try running `python pkg/utils/formatter.py` directly — observe the error and explain it in a comment.

**✓ Done when:** Package-level execution works; direct-file execution produces the expected relative import error.

---

### 🔴 #82 — `importlib` Dynamic Import
**Time:** ~15 min | **Concept:** importing modules by string name at runtime

- Have a dict: `{"json": "json", "math": "math", "random": "random"}`.
- Loop over it; for each: `module = importlib.import_module(name)`.
- Call one function from each imported module (e.g. `json.dumps`, `math.sqrt`, `random.randint`).
- Print results.

**✓ Done when:** All three modules are imported and called dynamically without any static `import` statement.

---

### 💀 #83 — BOSS A: Async Job Queue Pipeline
**Time:** ~45 min | **Concept:** full async producer-consumer with semaphore and timing

Build a complete async pipeline:
- `producer(queue, n)` — puts n jobs into the queue.
- `worker(worker_id, queue, results, semaphore)` — acquires semaphore; processes one job (`await asyncio.sleep(0.3)`); appends result; releases.
- `main()` — creates queue, 3 workers, and `asyncio.Semaphore(3)`; runs producer and 3 workers concurrently; waits for queue to drain.
- Wrap the full `asyncio.run(main())` in your `profile_block` CM.

**✓ Done when:** 20 jobs processed by 3 workers; total time ~2-3s (not 6s sequential); profiler prints timing.

---

### 💀 #84 — BOSS B: Package with Lazy Submodule Imports
**Time:** ~40 min | **Concept:** deferred imports for performance

- Build `toolkit/__init__.py`, `toolkit/heavy_a.py`, `toolkit/heavy_b.py`.
- Each heavy module has `print(f"heavy_X loaded")` at module level (so you can see when it loads).
- In `__init__.py`: do NOT import `heavy_a` or `heavy_b` at the top level.
- Instead expose two functions: `run_a()` and `run_b()` — each uses `importlib.import_module` internally to load its module only when called.
- From a test script: `import toolkit` (no print appears); `toolkit.run_a()` → only "heavy_a loaded" appears; `toolkit.run_b()` → only "heavy_b loaded" now appears.

**✓ Done when:** No heavy module loads at import time; each loads exactly once, only when its function is first called.

---

# ARC 6 — Foundations Stress Test
## 12 Exercises | Fast Reps on Everything That Feels Uncertain

> These are timed drills. No scaffolding. Read the spec, build it, check it. Move on.

---

### 🟢 #85 — Comprehension Drill (All Three Types)
**Time:** ~8 min | **Concept:** list / dict / set comprehension with filter

In one file, write:
- List: squares of odd numbers from 1 to 20.
- Dict: `{word: len(word)}` for words in a sentence, only words longer than 4 chars.
- Set: unique first letters of a list of names, uppercased.
- No `for` loops allowed — comprehensions only.

**✓ Done when:** All three produce correct results with no regular loop syntax.

---

### 🟢 #86 — Unpacking Drill
**Time:** ~8 min | **Concept:** tuple unpacking, `*rest`, nested unpacking

Write 5 examples:
1. Standard: `a, b, c = (1, 2, 3)`.
2. `*rest`: `first, *rest = [1, 2, 3, 4, 5]`.
3. Skip a value: `a, _, c = (10, 99, 30)`.
4. Nested: `(a, b), c = (1, 2), 3`.
5. Swap: `x, y = y, x`.

**✓ Done when:** All 5 unpackings work and produce the expected variable values.

---

### 🟢 #87 — Exception Flow Mapping
**Time:** ~10 min | **Concept:** try / except / else / finally execution paths

Write one `try` block that:
- Has `except ValueError`, `except ZeroDivisionError`, `else`, and `finally`.
- Run it 3 times with different inputs that trigger each path.
- Print which clause runs each time.

**✓ Done when:** You can predict exactly which clauses run for each input before you run the code.

---

### 🟡 #88 — Exception Chaining (`raise ... from ...`)
**Time:** ~12 min | **Concept:** `__cause__` and exception transparency

- Catch a `ValueError` and re-raise as a `RuntimeError` using `raise RuntimeError("context failed") from original`.
- In the outer handler: catch the `RuntimeError`; access `e.__cause__` and print the original exception.

**✓ Done when:** The outer catch prints the original `ValueError` via `e.__cause__`.

---

### 🟡 #89 — String Formatting Benchmark
**Time:** ~12 min | **Concept:** four formatting approaches, timing comparison

Produce the same string `"Hello, Thulani! You are 25 years old."` using:
1. `%` formatting.
2. `.format()`.
3. f-string.
4. `string.Template`.

Time all four with `timeit.timeit(..., number=100_000)` and print the results ranked fastest to slowest.

**✓ Done when:** All four produce identical strings; timing results are printed and ranked.

---

### 🟡 #90 — `collections` Module Drill
**Time:** ~15 min | **Concept:** five `collections` types, one use case each

In one file, use each of these exactly once in a practical example:
- `Counter` — count word frequency in a sentence.
- `defaultdict` — group names by their first letter.
- `OrderedDict` — show insertion order is preserved (compare to dict if needed).
- `namedtuple` — define a `Point(x, y)` and access fields by name.
- `deque` — implement a simple fixed-length history (maxlen=3).

**✓ Done when:** All five are used, imported from `collections`, and produce non-trivial output.

---

### 🟠 #91 — `functools` Drill
**Time:** ~15 min | **Concept:** `partial`, `reduce`, `lru_cache`

One practical use of each:
- `partial` — create `double = partial(operator.mul, 2)`; call `double(7)` → `14`.
- `reduce` — compute the product of a list using `reduce(operator.mul, [1,2,3,4,5])`.
- `lru_cache` — apply to a recursive Fibonacci function; prove the cache works by comparing timed calls.

**✓ Done when:** All three work and the `lru_cache` Fibonacci is measurably faster on repeat calls.

---

### 🟠 #92 — Walrus Operator (`:=`)
**Time:** ~12 min | **Concept:** assignment expression in conditions

Rewrite these three patterns using `:=`:
1. A `while` loop that reads lines from a list until it finds one starting with `"STOP"`.
2. A list comprehension that filters AND processes: `[y for x in data if (y := transform(x)) is not None]`.
3. A `while (chunk := file.read(1024)):` style file reader (mock with a string and `.read(1024)` simulation).

**✓ Done when:** All three use `:=` to eliminate the "assign, then check" pattern.

---

### 🟠 #93 — `*args` and `**kwargs` Forwarding Chain
**Time:** ~12 min | **Concept:** argument tunneling through multiple layers

- Write 4 functions: A calls B calls C calls D.
- Each passes `*args, **kwargs` unchanged to the next.
- D is the only one that actually uses the arguments.
- Call the chain: `A(1, 2, x=3, y=4)`.
- Confirm D receives `(1, 2)` and `{'x': 3, 'y': 4}`.

**✓ Done when:** `D` receives the exact arguments passed to `A`, unchanged through all intermediaries.

---

### 🔴 #94 — `__slots__` Memory Benchmark
**Time:** ~15 min | **Concept:** quantifying the memory benefit of `__slots__`

- Define `class WithDict:` (no `__slots__`) with 3 attributes.
- Define `class WithSlots:` with `__slots__ = ("a", "b", "c")`.
- Instantiate 500,000 of each.
- Use `tracemalloc` to compare peak memory.
- Print the memory difference in MB.

**✓ Done when:** You have two concrete peak memory numbers and the `__slots__` version is significantly lower.

---

### 🔴 #95 — `Protocol` (Structural Subtyping)
**Time:** ~18 min | **Concept:** duck typing formalized with typing.Protocol

- `from typing import Protocol, runtime_checkable`.
- Define `@runtime_checkable class Drawable(Protocol): def draw(self) -> str: ...`.
- Write two classes that have `draw()` but do NOT inherit from `Drawable`.
- Confirm `isinstance(obj, Drawable)` returns `True` for both.
- Write a function `render(shape: Drawable)` and call it with both objects.

**✓ Done when:** `isinstance` returns `True` for both objects despite no inheritance; `render()` works on both.

---

### 💀 #96 — BOSS: Debug the Broken Script
**Time:** ~45 min | **Concept:** finding real bugs in real Python

Write the following buggy script yourself (copy exactly, bugs included), then find and fix all 8 bugs:

```python
# BUG HUNT — 8 bugs in this file. Find them all.

def mutable_default(items=[]):    # Bug 1
    items.append("x")
    return items

def wrong_scope():
    total = 0
    def add(n):
        total += n              # Bug 2
    add(5)
    return total

class Counter:
    count = 0
    def increment(self):
        Counter.count = +1      # Bug 3

def compute_all(numbers):
    evens = [x for x in numbers if x % 2 = 0]   # Bug 4
    return evens

def safe_divide(a, b):
    try:
        return a / b
    except:                     # Bug 5
        pass

def get_names(data):
    return [item["name"] for item in data]
# Bug 6: no handling when "name" key is missing

def type_check(x):
    if type(x) == int or type(x) == float:   # Bug 7
        return True

result = compute_all([1,2,3,4,5])
print(result)
print(type_check(True))         # Bug 8: True is an int — is this intended?
```

**✓ Done when:** You've identified, named, and fixed all 8 bugs with a comment explaining what was wrong and why.

---

# ARC 7 — Synthesis
## 8 Exercises | Combining Everything

> These exercises combine multiple concepts from Arcs 1–6. No single-section solution exists.

---

### 🔴 #97 — Decorator + Generator: `@lazy_map`
**Time:** ~20 min | **Concept:** decorator that transforms a function to return a generator

- Write `@lazy_map` — wraps a function `f(x)` and returns a new function `lazy_f(iterable)` that yields `f(x)` for each item lazily.
- `@lazy_map def double(x): return x * 2` — now `double([1,2,3,4])` returns a generator (not a list).
- Prove it's lazy: add `print(f"doubling {x}")` inside `double` and call `next()` manually.

**✓ Done when:** `double([1,2,3])` returns a generator; values are only produced when iterated.

---

### 🔴 #98 — CM + OOP: Cursor-Like Pattern
**Time:** ~20 min | **Concept:** context manager returning a rich object

- Write `class Session:` as a CM whose `__enter__` returns a `Cursor` object.
- `Cursor` has `execute(sql: str)` (prints the SQL), `fetchall()` (returns a fixed list), and `close()` (prints "cursor closed").
- `Session.__exit__` calls `self.cursor.close()` and prints "session closed".
- Test: `with Session() as cursor: cursor.execute("SELECT *"); rows = cursor.fetchall()`.

**✓ Done when:** The cursor is usable inside the block; both close messages print on exit.

---

### 🔴 #99 — OOP + Async: Async Iterator
**Time:** ~20 min | **Concept:** `__aiter__` + `__anext__`, `async for`

- Write `class AsyncCounter:` with `__init__(self, n)`, `__aiter__(self)`, and `async def __anext__(self)`.
- `__anext__` waits 0.1s (using `await asyncio.sleep(0.1)`) then returns the next integer; raises `StopAsyncIteration` when done.
- Use it: `async for num in AsyncCounter(5): print(num)`.

**✓ Done when:** 5 numbers print with ~0.1s gaps using `async for` syntax.

---

### 🔴 #100 — Generator + CM: Self-Closing Generator
**Time:** ~18 min | **Concept:** generators that clean up after themselves

- Write a `@contextmanager` called `managed_sequence(data)` that yields an iterator over `data` and logs `"Sequence opened"` and `"Sequence closed"` in the `try/finally`.
- Use it: `with managed_sequence([1,2,3]) as seq: for item in seq: print(item)`.
- Deliberately break out of the loop early with `break` — confirm `"Sequence closed"` still prints.

**✓ Done when:** `"Sequence closed"` prints on both normal completion AND early `break`.

---

### 🔴 #101 — Decorator + Async + Module
**Time:** ~25 min | **Concept:** async retry decorator in its own importable module

- Create `retry_mod.py` with `@async_retry(times=3, delay=0.1)`.
- The decorator wraps an `async` function; retries up to `times` on any exception; waits `delay` seconds between retries.
- In `main.py`: `from retry_mod import async_retry`; apply it to a `flaky_async()` that raises ~60% of the time.
- Print attempt numbers as they happen.

**✓ Done when:** `async_retry` is in its own module, imported cleanly, and retries the async function correctly.

---

### 💀 #102 — BOSS A: Mini Logging System
**Time:** ~45 min | **Concept:** Logger class + @log_to_file decorator + CM all working together

Build:
- `class Logger:` — with `level` (DEBUG/INFO/WARNING/ERROR), `log(level, msg)` method that filters by level; writes to an internal list.
- `@contextmanager def managed_log_file(path):` — opens file on entry, flushes and closes on exit; yields a write-compatible object.
- `def log_to_file(path):` — a decorator factory; wraps a function; uses `managed_log_file` to append an entry/exit record to the file each call.
- Wire them together: decorate a business function with `@log_to_file("app.log")`; inside it, use the `Logger` for level-filtered messages.

**✓ Done when:** Calling the decorated function writes timestamped entry/exit lines to the log file AND internal Logger messages respect the configured level filter.

---

### 💀 #103 — BOSS B: Full Async Pipeline
**Time:** ~50 min | **Concept:** asyncio + semaphore + async generator + CM output + decorator timing

Build a complete 50-line pipeline:
- `@async_timer` — times the full run (from Arc 2 exercise #33).
- `async def generate_data(n):` — async generator yielding n records with a small random delay each.
- `asyncio.Semaphore(4)` — limits concurrent processing to 4 at a time.
- `@contextmanager def output_file(path):` — manages writing results to a file.
- `async def process(record):` — transforms the record (e.g. uppercase its string field).
- `@async_timer async def run_pipeline(n):` — wires everything together; collects results; writes to output via the CM.

**✓ Done when:** Pipeline runs end-to-end; timer prints; output file contains all processed records; at most 4 coroutines run simultaneously (verify with prints).

---

### 💀 #104 — FINAL BOSS: The Interview File
**Time:** ~60 min | **Concept:** demonstrating senior-level Python understanding in one cohesive file

Create `senior_python.py` — a single, well-structured file with 10 functions/classes, each demonstrating one mastery concept. Each must have a docstring explaining WHY it's written the way it is (not just what it does).

Cover exactly these 10 concepts, one each:

1. **Type hints + Protocol** — a `Serializable` Protocol; a class that satisfies it.
2. **Dataclass + `__post_init__`** — validation logic after auto-generated `__init__`.
3. **Property + Descriptor** — reuse a descriptor across multiple classes.
4. **Generator pipeline** — three chained generators; one infinite.
5. **Decorator factory** — `@retry(times, exceptions)` that handles specific exception types.
6. **Context manager** — with proper `try/finally`; returns a rich object from `__enter__`.
7. **`asyncio.gather` + Semaphore** — concurrent async tasks with rate limiting.
8. **`functools.lru_cache` vs manual `@memoize`** — show both; comment on tradeoffs.
9. **`__slots__` + `__repr__` + `__eq__`** — a complete, efficient value object.
10. **Exception chaining** — `raise X from Y`; access `__cause__` in the handler.

**✓ Done when:** The file runs without errors; every function/class has a docstring explaining the design decision, not just the behavior; a senior developer reading it could see your reasoning.

---

## 🏁 Final Checklist

**Arc 1 — OOP (24):** `1☐ 2☐ 3☐ 4☐ 5☐ 6☐ 7☐ 8☐ 9☐ 10☐ 11☐ 12☐ 13☐ 14☐ 15☐ 16☐ 17☐ 18☐ 19☐ 20☐ 21☐ 22☐ 23☐ 24☐`

**Arc 2 — Decorators (16):** `25☐ 26☐ 27☐ 28☐ 29☐ 30☐ 31☐ 32☐ 33☐ 34☐ 35☐ 36☐ 37☐ 38☐ 39☐ 40☐`

**Arc 3 — Generators (16):** `41☐ 42☐ 43☐ 44☐ 45☐ 46☐ 47☐ 48☐ 49☐ 50☐ 51☐ 52☐ 53☐ 54☐ 55☐ 56☐`

**Arc 4 — Context Managers (12):** `57☐ 58☐ 59☐ 60☐ 61☐ 62☐ 63☐ 64☐ 65☐ 66☐ 67☐ 68☐`

**Arc 5 — Async & Modules (16):** `69☐ 70☐ 71☐ 72☐ 73☐ 74☐ 75☐ 76☐ 77☐ 78☐ 79☐ 80☐ 81☐ 82☐ 83☐ 84☐`

**Arc 6 — Foundations (12):** `85☐ 86☐ 87☐ 88☐ 89☐ 90☐ 91☐ 92☐ 93☐ 94☐ 95☐ 96☐`

**Arc 7 — Synthesis (8):** `97☐ 98☐ 99☐ 100☐ 101☐ 102☐ 103☐ 104☐`

---
*Total: 104 new exercises. Combined with the previous 35 (Sections 9–13 deep dives): 139 exercises total.*

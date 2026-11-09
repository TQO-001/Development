# ---------------- 11.1 Custom Context Managers (class-based) ---------------- #
class CombatArenaContext:
    def __init__(self, location):
        self.location = location

    def __enter__(self):
        print(f"[Setup] Entering the {self.location}! Clear the arena flags.")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Handles teardown. The arguments capture errors if something crashed inside.
        print(f"[Teardown] Leaving the {self.location}. Cleaning uo footprints and healing units.")
        # Returning True here would silence exceptions; returning False/None lets them propagate.

# Executing our custom context manager
with CombatArenaContext("Pietermaritzburg Colosseum") as arena:
    print(f"Gladiators are actively dueling in {arena.location}!")

# -------------------------- 11.2 Using `contextlib` ------------------------- #
from contextlib import contextmanager

@contextmanager
def simple_arena_context(location):
    # This runs on entry
    print(f"[Setup] Entering {location}")
    try:
        yield f"Instance of {location}" # Hands control over to the 'with' block
    finally:
        # This runs on exit, even if code inside crashes
        print(f"[Teardown] Cleaning {location}")

with simple_arena_context("Shadow Dungeon") as dungeon:
    print(f"Exploring the {dungeon}...")

# ----------------- 11.3 Practical Example: Timing Execution ----------------- #
import time

class SpeedTracker:
    def __enter__(self):
        print("[Start Execution]")
        self.start_time = time.time() # Capture exact system start time
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time() # Capture stop time
        elapsed = self.end_time - self.start_time
        print("[End Execution]")
        print(f"\n[Execution Time]: Complete in {elapsed:.6f} seconds.")

# Testing the speed of our system execution
with SpeedTracker():
    # Simulate a small system processing workload
    sum_value = sum(x for x in range(1, 1_000_000))
    print(sum_value)
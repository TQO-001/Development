## Section 24: Python for Automation

Python is one of the best languages for automation — scripting repetitive system tasks, managing files in bulk, scheduling work, or wrapping command-line tools. This section covers the three standard library modules that power most automation scripts: `subprocess` for running shell commands, `os` and `shutil` for file system work, and `datetime`/`time` for working with dates and scheduling.

### 24.1 subprocess — Running System Commands

`subprocess` lets you launch any command-line program from Python and capture its output. Think of it as Python reaching out and typing a command in a terminal on your behalf.

```python
import subprocess

# Run a command and wait for it to finish
result = subprocess.run(["ls", "-l"])
# On Windows: subprocess.run(["dir"], shell=True)

# Capture the output instead of printing it directly
result = subprocess.run(
    ["ls", "-l"],
    capture_output=True,   # Capture stdout and stderr
    text=True              # Decode bytes to str automatically
)
print(result.stdout)       # Command's standard output
print(result.stderr)       # Command's standard error (empty if no errors)
print(result.returncode)   # 0 = success, anything else = error

# Check if a command failed and handle it
result = subprocess.run(["git", "status"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Command failed: {result.stderr}")

# Run a command with shell=True (lets you use shell features like pipes and wildcards)
# Use this carefully — never pass untrusted user input with shell=True
result = subprocess.run("ps aux | grep python", shell=True, capture_output=True, text=True)
print(result.stdout)
```

### 24.2 Running Commands with Input and Timeouts

```python
import subprocess

# Pass input to a command (like typing something at a prompt)
result = subprocess.run(
    ["grep", "ERROR"],
    input="INFO: Player logged in\nERROR: Connection failed\nINFO: Retry...\n",
    capture_output=True,
    text=True
)
print(result.stdout)  # ERROR: Connection failed

# Set a timeout — raise an exception if the command takes too long
try:
    result = subprocess.run(
        ["ping", "-c", "10", "google.com"],
        capture_output=True,
        text=True,
        timeout=5       # Kill after 5 seconds
    )
except subprocess.TimeoutExpired:
    print("Command took too long and was cancelled.")

# Check=True raises CalledProcessError automatically if the command fails
try:
    subprocess.run(["ls", "/nonexistent/path"], check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit code {e.returncode}: {e.stderr}")
```

### 24.3 Running Background Processes

`subprocess.Popen` launches a process and returns immediately, without waiting for it to finish — useful for long-running background tasks.

```python
import subprocess

# Start a process in the background
process = subprocess.Popen(
    ["python", "long_running_script.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Do other work while the process runs
print("Process started, doing other things...")

# Wait for it to finish and collect the output
stdout, stderr = process.communicate()
print(f"Process finished with code: {process.returncode}")
print(stdout.decode())
```

> [!NOTE]
> Use `subprocess.run()` for most cases — it's simpler and blocks until the command finishes. Use `subprocess.Popen()` when you need to interact with the process while it runs, or run it truly in the background.

---

### 24.4 os and shutil — File System Operations

`pathlib` (Section 6) is the modern way to work with paths. But `os` and `shutil` are still the standard tools for many file operations — copying, moving, deleting, and walking directory trees.

```python
import os
import shutil
from pathlib import Path

# Create a directory (exist_ok=True means no error if it already exists)
os.makedirs("game_data/saves", exist_ok=True)

# List all files and folders in a directory
files = os.listdir("game_data")
for item in files:
    print(item)

# Get the full path of the current working directory
print(os.getcwd())

# Change the current working directory
os.chdir("/tmp")

# Check if a path exists
print(os.path.exists("game_data/saves"))   # True or False
print(os.path.isfile("config.json"))       # True if it's a file
print(os.path.isdir("game_data"))          # True if it's a directory
```

### 24.5 Copying, Moving, and Deleting

```python
import shutil
import os

# Copy a single file (preserves content, not metadata like permissions)
shutil.copy("saves/slot_1.json", "saves/slot_1_backup.json")

# Copy and preserve metadata (timestamps, permissions)
shutil.copy2("saves/slot_1.json", "saves/slot_1_backup.json")

# Copy an entire directory tree
shutil.copytree("saves", "saves_backup")

# Move a file or directory (works as rename if on the same filesystem)
shutil.move("saves/old_save.json", "archive/old_save.json")

# Delete a single file
os.remove("saves/slot_1_backup.json")

# Delete an empty directory
os.rmdir("empty_folder")

# Delete a directory and everything inside it (be careful — permanent)
shutil.rmtree("saves_backup")

# Get file size in bytes
size = os.path.getsize("saves/slot_1.json")
print(f"Save file is {size} bytes")
```

### 24.6 Walking Directory Trees

`os.walk()` traverses a directory recursively, yielding each folder and its contents. Use it when you need to process all files matching a pattern, regardless of how deeply nested they are.

```python
import os

# Walk the entire game_data directory, finding all .json save files
for root, dirs, files in os.walk("game_data"):
    # root   = current folder path
    # dirs   = list of subdirectory names in root
    # files  = list of filenames in root

    for filename in files:
        if filename.endswith(".json"):
            full_path = os.path.join(root, filename)
            print(f"Found save file: {full_path}")

# Example: find all Python files larger than 10 KB
for root, dirs, files in os.walk("."):
    # Skip hidden directories (like .git)
    dirs[:] = [d for d in dirs if not d.startswith(".")]

    for filename in files:
        if filename.endswith(".py"):
            full_path = os.path.join(root, filename)
            if os.path.getsize(full_path) > 10 * 1024:
                print(f"Large file: {full_path} ({os.path.getsize(full_path)} bytes)")
```

### 24.7 Environment Variables

Environment variables are how you pass configuration into a running process from the outside — without hardcoding values in your script.

```python
import os

# Read an environment variable (returns None if not set)
home_dir = os.environ.get("HOME")
path = os.environ.get("PATH")

# Read with a default fallback
log_level = os.environ.get("LOG_LEVEL", "INFO")

# Read a required variable — crash immediately if it's missing
db_url = os.environ["DATABASE_URL"]  # Raises KeyError if not set

# Set an environment variable for the current process (and its children)
os.environ["MY_APP_VAR"] = "some_value"
```

---

### 24.8 datetime and time — Working with Dates

Python's `datetime` module handles everything time-related. `time` is the lower-level module for timestamps and pausing execution.

```python
from datetime import datetime, date, timedelta
import time

# Current date and time
now = datetime.now()          # Local time
utc_now = datetime.utcnow()   # UTC time (use this for storage)

print(now)                    # 2025-06-15 14:23:01.456789

# Formatting a datetime as a string
print(now.strftime("%Y-%m-%d"))           # 2025-06-15
print(now.strftime("%d/%m/%Y %H:%M"))     # 15/06/2025 14:23
print(now.strftime("%A, %d %B %Y"))       # Sunday, 15 June 2025

# Parsing a string into a datetime
date_str = "2025-06-15 14:23:01"
dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print(dt.year)    # 2025
print(dt.month)   # 6
print(dt.hour)    # 14
```

### 24.9 Date Arithmetic with timedelta

```python
from datetime import datetime, timedelta

now = datetime.now()

# Add or subtract time
tomorrow     = now + timedelta(days=1)
next_week    = now + timedelta(weeks=1)
two_hours    = now + timedelta(hours=2)
thirty_mins  = now + timedelta(minutes=30)
yesterday    = now - timedelta(days=1)

# Calculate the difference between two datetimes
quest_started  = datetime(2025, 6, 1, 9, 0)
quest_finished = datetime(2025, 6, 1, 11, 45)
duration = quest_finished - quest_started    # Returns a timedelta
print(duration)                              # 2:45:00
print(duration.total_seconds())             # 9900.0
print(f"Quest took {duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m")
# Quest took 2h 45m

# Check if a deadline has passed
deadline = datetime(2025, 12, 31, 23, 59)
if datetime.now() > deadline:
    print("Quest deadline has passed!")
```

### 24.10 time.sleep and Unix Timestamps

```python
import time

# Pause execution (useful in polling loops, rate limiting, retry logic)
print("Starting quest...")
time.sleep(2)     # Wait 2 seconds
print("Quest complete!")

# Unix timestamp — seconds since 1 January 1970 UTC
timestamp = time.time()    # Returns a float, e.g. 1750000000.123
print(f"Current timestamp: {int(timestamp)}")

# Convert a Unix timestamp back to a datetime
from datetime import datetime
dt = datetime.fromtimestamp(timestamp)
print(dt)  # 2025-06-15 14:23:01.123456

# Measure how long something takes
start = time.perf_counter()
# ... do work ...
time.sleep(0.5)  # Simulating work
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f} seconds")
```

### 24.11 A Practical Automation Script

Putting it all together — a script that archives old save files:

```python
import os
import shutil
from datetime import datetime, timedelta

def archive_old_saves(saves_dir: str, archive_dir: str, days_old: int = 30) -> int:
    """
    Moves save files older than `days_old` days into the archive directory.
    Returns the number of files moved.
    """
    os.makedirs(archive_dir, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=days_old)
    moved = 0

    for root, dirs, files in os.walk(saves_dir):
        for filename in files:
            if not filename.endswith(".json"):
                continue

            full_path = os.path.join(root, filename)
            modified_at = datetime.fromtimestamp(os.path.getmtime(full_path))

            if modified_at < cutoff:
                destination = os.path.join(archive_dir, filename)
                shutil.move(full_path, destination)
                print(f"Archived: {filename} (last modified {modified_at.strftime('%Y-%m-%d')})")
                moved += 1

    print(f"Done. {moved} file(s) archived.")
    return moved

archive_old_saves("game_data/saves", "game_data/archive", days_old=30)
```

---

**Practice:**
1. Use `subprocess.run()` to run `git status` in your project directory and print the output. Check the return code and print a message if the directory isn't a git repo.
2. Write a script that uses `os.walk()` to find all `.md` files in a directory tree and prints their file names and sizes in KB.
3. Write a function `days_until(target_date_str: str) -> int` that parses a date string like `"2025-12-31"` and returns how many days until that date.

---

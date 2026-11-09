## Section 6: File I/O

File I/O (Input/Output) is how your program reads from and writes to the filesystem. Python makes this simple with the built-in `open()` function, but production code always uses the context manager (`with`) to guarantee safe resource cleanup.

### 6.1 Opening & Reading Files

The `open()` function takes a filepath and a mode, and returns a file object.

```Python
# Basic open — avoid this pattern (resource leak risk if an exception occurs)
f = open("server_log.txt", "r")
content = f.read()
f.close()  # If an exception occurs before this line, the file is never closed
```

File reading methods:

```Python
# Using a context manager (always preferred — see 6.2)
with open("server_log.txt", "r") as f:

    content = f.read()              # Read the entire file as one string
    lines   = f.readlines()         # Read all lines into a list of strings
    line    = f.readline()          # Read one line at a time

# Iterating line by line (memory-efficient — no list is created)
with open("server_log.txt", "r") as f:
    for line in f:                  # The file object IS an iterator
        print(line.strip())
```

### 6.2 Context Manager (`with`)

The `with` statement automatically calls `close()` on the file when the block exits — even if an exception is raised inside the block.

```Python
# Reading
with open("notes.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# The file is guaranteed to be closed here — no f.close() needed
```

This is the clean, safe, expected pattern in all professional Python. It's powered by the context manager protocol, which gets a full explanation in Section 11.

### 6.3 File Modes

| Mode | Description |
|---|---|
| `"r"` | Read (default) — file must exist |
| `"w"` | Write — creates the file or **overwrites** existing content |
| `"a"` | Append — creates the file or adds to the end |
| `"x"` | Exclusive create — fails if the file already exists |
| `"b"` | Binary mode — combine with others: `"rb"`, `"wb"` |
| `"+"` | Read+Write — combine with others: `"r+"`, `"w+"` |

```Python
# Always specify encoding for text files, to avoid platform differences
with open("save_data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

### 6.4 Writing & Appending

```Python
# Writing — creates the file if it doesn't exist, OVERWRITES if it does
with open("save_game.txt", "w", encoding="utf-8") as f:
    f.write("Player: Arthur\n")
    f.write("Level: 15\n")
    f.write("Gold: 2500\n")

# Appending — adds to the end of the file, creates it if it doesn't exist
with open("combat_log.txt", "a", encoding="utf-8") as f:
    f.write("[14:23:01] Arthur defeated Goblin King (+250 XP)\n")
    f.write("[14:23:45] Arthur found Enchanted Sword\n")

# Writing multiple lines at once using writelines()
log_entries = [
    "Session started\n",
    "Player logged in: Arthur\n",
    "Dungeon entered: Shadow Keep\n"
]
with open("session.log", "w", encoding="utf-8") as f:
    f.writelines(log_entries)
```

### 6.5 Working with Binary Files

Binary mode (`"b"`) reads and writes raw bytes — used for images, audio, compiled data, or anything that isn't plain text.

```Python
# Reading binary data
with open("character_portrait.png", "rb") as f:
    image_data = f.read()
    print(f"File size: {len(image_data)} bytes")

# Writing binary data
with open("save_slot_1.bin", "wb") as f:
    f.write(b"\x00\x01\x02\x03")  # The b"..." prefix denotes a bytes literal

# Copying a file byte-by-byte (works for any file type)
with open("character_portrait.png", "rb") as source:
    with open("character_portrait_backup.png", "wb") as dest:
        dest.write(source.read())
```

### 6.6 File Paths with `pathlib`

`pathlib.Path` is the modern, object-oriented way to handle file paths. It works correctly across Windows (`\`), macOS, and Linux (`/`) without you having to manually manipulate strings.

```Python
from pathlib import Path

# Building paths safely (cross-platform)
base_dir   = Path("game_data")
saves_dir  = base_dir / "saves"           # The "/" operator joins paths
save_file  = saves_dir / "slot_1.txt"

print(save_file)               # game_data/saves/slot_1.txt (on Linux/Mac)

# Useful Path properties
print(save_file.name)          # "slot_1.txt"
print(save_file.stem)          # "slot_1"
print(save_file.suffix)        # ".txt"
print(save_file.parent)        # game_data/saves
print(save_file.exists())      # True or False

# Create directories safely
saves_dir.mkdir(parents=True, exist_ok=True)
# parents=True  → creates all intermediate directories
# exist_ok=True → no error if the directory already exists

# Listing files
for file in base_dir.iterdir():
    print(file)

# Reading and writing using Path directly
content = save_file.read_text(encoding="utf-8")
save_file.write_text("New content", encoding="utf-8")
```

### 6.7 Practice Project Reference: File Creator (6B)

In your `6B-File-IO-Practice.py`, you built a terminal program that dynamically creates `.md` and `.txt` files. The key patterns from that project:

```Python
from pathlib import Path

# Pattern 1: Getting a file type from a dictionary
file_types = {"Markdown": "md", "Text": "txt"}
extensions = list(file_types.values())  # ["md", "txt"]

# Pattern 2: Writing multi-line user input to a file
file_name    = "my_notes"
extension    = "md"
file_content = ""

# Accumulate lines until a sentinel value is entered
while True:
    line = input()
    if line == "[FILE CLOSE]":
        break
    file_content += line + "\n"

# Pattern 3: Writing the file
with open(f"{file_name}.{extension}", "w", encoding="utf-8") as f:
    f.write(file_content)

print(f"Created: {file_name}.{extension}")
```

That project also used `try/except` with a `CustomError` class (Section 5.4) to validate user menu choices — a good example of how Sections 5 and 6 work together in practice.

---

**Practice:**
1. Write a script that writes three lines to a file called `quest_log.txt` using `with open(...)`.
2. Read that same file back with a `for line in f:` loop, printing each line stripped of whitespace.
3. Use `pathlib.Path` to build a path to `saves/slot_1.txt`, check whether it already exists, and create the parent directory if it doesn't.

---

## Section 25: Regular Expressions

A regular expression (regex) is a pattern that describes a set of strings. Instead of writing custom Python code to find all email addresses in a document, or validate that a quest code matches a specific format, you write a compact pattern and let the `re` module do the matching work. Once you understand the syntax, regexes handle in one line what would otherwise take 20.

```python
import re
```

### 25.1 The Core Idea — Patterns and Strings

A regex pattern is a string that describes what you're looking for. You write the pattern, then test it against text.

```python
import re

# Does this string contain the word "dragon"?
text = "Arthur slew the dragon in the Northern Keep."

match = re.search(r"dragon", text)   # r"..." = raw string (avoids backslash issues)
if match:
    print("Found it!")
    print(match.group())    # "dragon"
    print(match.start())    # 21 — character position where the match starts
    print(match.end())      # 27 — character position where the match ends
```

### 25.2 Special Characters — The Pattern Language

The real power comes from special characters that match more than just a fixed string:

| Pattern | Matches | Example |
|---|---|---|
| `.` | Any single character (except newline) | `h.t` matches `hat`, `hit`, `hot` |
| `\d` | Any digit (0–9) | `\d\d\d` matches `123` |
| `\w` | Any word character (letter, digit, underscore) | `\w+` matches `Arthur` |
| `\s` | Any whitespace (space, tab, newline) | `\s+` matches one or more spaces |
| `\D`, `\W`, `\S` | The OPPOSITE of the above | `\D+` matches non-digits |
| `^` | Start of string (or line) | `^Arthur` only matches if it starts with Arthur |
| `$` | End of string (or line) | `Camelot$` only matches if it ends with Camelot |
| `[abc]` | Any one of: a, b, or c | `[aeiou]` matches any vowel |
| `[^abc]` | Any character NOT in the set | `[^aeiou]` matches any consonant |
| `[a-z]` | Any lowercase letter | `[A-Za-z]` matches any letter |
| `\b` | Word boundary | `\bcat\b` matches `cat` but not `catch` |

Quantifiers control how many times a pattern repeats:

| Quantifier | Means | Example |
|---|---|---|
| `*` | Zero or more | `go*ld` matches `gld`, `gold`, `goold` |
| `+` | One or more | `go+ld` matches `gold`, `goold` but NOT `gld` |
| `?` | Zero or one (optional) | `colou?r` matches `color` and `colour` |
| `{3}` | Exactly 3 | `\d{3}` matches exactly 3 digits |
| `{2,5}` | Between 2 and 5 | `\d{2,5}` matches 2 to 5 digits |
| `{3,}` | 3 or more | `\d{3,}` matches 3 or more digits |

### 25.3 The Four Main Functions

```python
import re

log_line = "2025-06-15 14:23:01 [ERROR] Player 'Arthur' failed to load save slot_3"

# re.search() — find the FIRST match anywhere in the string
# Returns a Match object or None
match = re.search(r"\[(\w+)\]", log_line)
if match:
    print(match.group())   # "[ERROR]"
    print(match.group(1))  # "ERROR" — group(1) = first set of parentheses

# re.match() — match only at the START of the string
# Returns a Match object or None
match = re.match(r"\d{4}-\d{2}-\d{2}", log_line)
if match:
    print(match.group())   # "2025-06-15"

# re.findall() — find ALL matches, returns a list of strings
# If the pattern has groups, returns a list of tuples
errors = re.findall(r"\[(\w+)\]", "INFO: ok [INFO] done [ERROR] failed [WARNING] slow")
print(errors)  # ['INFO', 'ERROR', 'WARNING']

# re.sub() — substitute matches with a replacement string
sanitised = re.sub(r"'Arthur'", "[REDACTED]", log_line)
print(sanitised)  # 2025-06-15 14:23:01 [ERROR] Player '[REDACTED]' failed...

# Replace with a count limit
sanitised = re.sub(r"\d", "X", "Call 12345 for help", count=3)
print(sanitised)  # "Call XXX45 for help"
```

### 25.4 Groups — Capturing Parts of a Match

Parentheses in a pattern create **groups** — sections of the match you can extract individually.

```python
import re

# Parse a log timestamp
log_line = "2025-06-15 14:23:01 [ERROR] Something went wrong"

# Three groups: date, time, level
pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) \[(\w+)\]"
match = re.search(pattern, log_line)

if match:
    date  = match.group(1)   # "2025-06-15"
    time  = match.group(2)   # "14:23:01"
    level = match.group(3)   # "ERROR"

    # Or get all groups at once as a tuple
    print(match.groups())    # ('2025-06-15', '14:23:01', 'ERROR')
```

### 25.5 Named Groups — Cleaner Extraction

Named groups (`(?P<name>...)`) give each group a name instead of a number. Makes complex patterns much easier to read and maintain.

```python
import re

log_line = "2025-06-15 14:23:01 [ERROR] Player 'Arthur' failed login from 192.168.1.42"

pattern = r"""
    (?P<date>\d{4}-\d{2}-\d{2})         # Date
    \s
    (?P<time>\d{2}:\d{2}:\d{2})         # Time
    \s
    \[(?P<level>\w+)\]                  # Log level
    \s
    .*?                                 # Any text in between
    (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})  # IP address at the end
"""

match = re.search(pattern, log_line, re.VERBOSE)  # re.VERBOSE ignores whitespace and comments
if match:
    print(match.group("date"))   # "2025-06-15"
    print(match.group("level"))  # "ERROR"
    print(match.group("ip"))     # "192.168.1.42"

    # Access as a dict
    print(match.groupdict())
    # {'date': '2025-06-15', 'time': '14:23:01', 'level': 'ERROR', 'ip': '192.168.1.42'}
```

### 25.6 Compiling Patterns for Reuse

If you're using the same pattern in a loop or called repeatedly, compile it once and reuse the compiled object. It's slightly faster and keeps things clean.

```python
import re

# Compile once
LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\] "
    r"(?P<message>.+)"
)

# Use many times
log_lines = [
    "2025-06-15 14:23:01 [ERROR] Failed to connect to database",
    "2025-06-15 14:23:02 [INFO] Retrying connection...",
    "2025-06-15 14:23:03 [INFO] Connection established",
]

for line in log_lines:
    match = LOG_PATTERN.match(line)
    if match:
        print(f"[{match.group('level')}] {match.group('message')}")
```

### 25.7 Common Useful Patterns

```python
import re

# Email address
email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# IP address (basic — not full validation)
ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

# URL
url_pattern = re.compile(r"https?://[^\s]+")

# Date in YYYY-MM-DD format
date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

# Extracting all IPs from a log file
log_content = """
192.168.1.1 - GET /api/players
10.0.0.42 - POST /api/quests
192.168.1.1 - GET /api/guilds
"""
all_ips = ip_pattern.findall(log_content)
unique_ips = set(all_ips)
print(unique_ips)  # {'192.168.1.1', '10.0.0.42'}

# Validate a quest code format: QST-XXXX (letters and digits, exactly 4)
quest_code_pattern = re.compile(r"^QST-[A-Z0-9]{4}$")
print(bool(quest_code_pattern.match("QST-A3B7")))   # True
print(bool(quest_code_pattern.match("QST-ab")))      # False
print(bool(quest_code_pattern.match("QUEST-A3B7")))  # False
```

### 25.8 Practical Example: Log Analysis

```python
import re
from collections import Counter

def analyse_log(filepath: str) -> dict:
    """
    Parses a log file and returns a summary of:
    - Count of each log level
    - All unique IP addresses found
    - Lines containing errors
    """
    level_pattern    = re.compile(r"\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]")
    ip_pattern       = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
    failed_attempts  = re.compile(r"Failed password for (\w+)")

    level_counts     = Counter()
    ip_addresses     = set()
    error_lines      = []
    failed_logins    = Counter()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            # Count log levels
            level_match = level_pattern.search(line)
            if level_match:
                level_counts[level_match.group(1)] += 1

            # Collect IPs
            ips = ip_pattern.findall(line)
            ip_addresses.update(ips)

            # Collect error lines
            if "[ERROR]" in line or "[CRITICAL]" in line:
                error_lines.append(line.strip())

            # Count failed login attempts per user
            login_match = failed_attempts.search(line)
            if login_match:
                failed_logins[login_match.group(1)] += 1

    return {
        "level_counts":   dict(level_counts),
        "unique_ips":     list(ip_addresses),
        "error_lines":    error_lines,
        "failed_logins":  dict(failed_logins),
    }
```

---

**Practice:**
1. Write a regex that extracts all dates in `YYYY-MM-DD` format from a string. Test it against a paragraph containing mixed text and several dates.
2. Write a pattern that validates a player name: 3–20 characters, only letters, digits, and underscores, must start with a letter. Use `re.match()` and test it against valid and invalid names.
3. Using the log analysis function as a starting point, write a function that reads a log file and returns a list of unique IP addresses that appear more than 5 times (potential suspicious activity).

---

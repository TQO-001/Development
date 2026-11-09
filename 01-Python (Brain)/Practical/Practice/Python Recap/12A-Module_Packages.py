# -------------------------- 12.1 Importing Modules -------------------------- #
import json
from json import loads
import json as j
from json import loads, dumps
from json import *

# ------------------------------- 12.3 Packages ------------------------------ #
# 1. Imports

import logging
import re
from datetime import datetime
from pathlib import Path 
from typing import Generator

# 2. Module-level Constants (not mutable globals)
LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] "
    r"(?P<message>.+)$"
)

# 3. Public Functions and Classes
def parse_log_line(line: str) -> dict | None:
    """
    Parses a single log line matching the format:
        2024-01-15 14:23:01 [ERROR] Connection refused

    Returns:
        dict with 'timestamp', 'level', 'message' keys,
        or None if the line doesn't match the expected format.
    """
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return {
        "timestamp": datetime.fromisoformat(match.group("timestamp")),
        "level": match.group("level"),
        "message": match.group("message"),
    }

def stream_errors(filepath: str | Path) -> Generator[dict, None, None]:
    """
    Memory-safe generator that streams only ERROR-level log entries
    from a file of any size.

    Args:
        filepath: Path to the log file.
    Yields:
        Parsed log entry dicts for ERROR-level lines only.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed and parsed["level"] == "ERROR":
                yield parsed

# 4. GUARD: code that only runs when executed directly
if __name__ == "__main__":
    # This block runs when you do: python log_utils.py
    # It does NOT run when you do: import log_utils
    import sys

    if len(sys.argv) < 2:
        print("Usage: python log_utils.py <logfile>")
        sys.exit(1)

    for entry in stream_errors(sys.argv[1]):
        print(f"[{entry['timestamp']}] {entry['message']}")

        

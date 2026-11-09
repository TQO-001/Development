## Section 26: Security & Cryptography

This section covers Python's built-in security tools: generating cryptographically secure random values with `secrets`, computing checksums and hashes with `hashlib`, monitoring files for tampering, and using `socket` for low-level network operations. These tools underpin everything from file integrity checking to writing your own port scanner.

### 26.1 secrets — Cryptographically Secure Randomness

Python's `random` module is fine for games and statistics, but **never use it for security**. Its output is predictable if an attacker knows enough about the state. `secrets` uses the operating system's cryptographically secure random number generator instead — the same source your OS uses for generating encryption keys.

```python
import secrets
import string

# Generate a secure random token (useful for password reset links, API keys, etc.)
token = secrets.token_hex(32)        # 64-character hex string
print(token)                          # e.g. 'a3f8b2c1...'

token_url = secrets.token_urlsafe(32) # URL-safe base64 (no + or / characters)
print(token_url)                      # e.g. 'Abc1De2Fg3...'

token_bytes = secrets.token_bytes(16) # Raw 16 bytes

# Generate a secure random password
alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
password = "".join(secrets.choice(alphabet) for _ in range(20))
print(password)   # e.g. 'xK9!mP2qB@r4jN6sW1tZ'

# Secure random integer in a range
pin = secrets.randbelow(10000)   # Random int from 0 to 9999
print(f"{pin:04d}")              # Zero-padded to 4 digits: e.g. "0742"

# Timing-safe string comparison (prevents timing attacks)
# Use this instead of == when comparing tokens or hashes
user_token = "abc123"
stored_token = "abc123"
if secrets.compare_digest(user_token, stored_token):
    print("Tokens match!")
```

> [!NOTE]
> `secrets.compare_digest()` takes the same amount of time whether the strings match or don't. A regular `==` comparison stops as soon as it finds a difference — this timing difference can be exploited to guess tokens character by character. Always use `compare_digest()` when comparing security-sensitive values.

### 26.2 Password Strength Validation

Generating and storing passwords correctly is covered in Section 18 (bcrypt). This is the complementary piece: checking whether a password meets your complexity requirements before you hash and store it.

```python
import re

def check_password_strength(password: str) -> dict:
    """
    Checks password against common strength requirements.
    Returns a dict of requirements and whether each passes.
    """
    checks = {
        "min_length":     len(password) >= 12,
        "has_uppercase":  bool(re.search(r"[A-Z]", password)),
        "has_lowercase":  bool(re.search(r"[a-z]", password)),
        "has_digit":      bool(re.search(r"\d", password)),
        "has_special":    bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password)),
        "no_spaces":      " " not in password,
    }
    checks["is_strong"] = all(checks.values())
    return checks

result = check_password_strength("Excalibur9!")
for requirement, passed in result.items():
    status = "✅" if passed else "❌"
    print(f"{status} {requirement}")
```

### 26.3 hashlib — Checksums and File Integrity

`hashlib` computes cryptographic hashes. A hash is a fixed-size fingerprint of any data — the same input always produces the same output, but even one changed byte produces a completely different hash. This makes hashes useful for detecting tampering, verifying downloads, and deduplicating files.

```python
import hashlib

# Hash a string
text = "Arthur is the rightful king"
digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
print(digest)   # a64-character hex string — changes completely if even one character changes

# Common hash algorithms
hashlib.md5(text.encode()).hexdigest()        # 32 chars — fast but NOT cryptographically safe
hashlib.sha1(text.encode()).hexdigest()       # 40 chars — deprecated for security use
hashlib.sha256(text.encode()).hexdigest()     # 64 chars — the standard choice
hashlib.sha512(text.encode()).hexdigest()     # 128 chars — stronger, larger

# List all available algorithms on your system
print(hashlib.algorithms_available)
```

> [!NOTE]
> **hashlib is NOT for password storage.** It's too fast — a modern GPU can compute billions of SHA-256 hashes per second, making brute-force attacks trivial. For passwords, always use bcrypt, scrypt, or Argon2 via `passlib` (Section 18). Use hashlib for file integrity, checksums, and data fingerprinting — not passwords.

### 26.4 Hashing Files for Integrity Checking

A file's SHA-256 hash acts as its fingerprint. Store the hash when the file is trusted; recompute it later to detect any modification.

```python
import hashlib

def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """
    Computes the hash of a file without loading the whole file into memory.
    Reads in 64 KB chunks — safe for files of any size.
    """
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_file(filepath: str, expected_hash: str, algorithm: str = "sha256") -> bool:
    """Returns True if the file's hash matches the expected value."""
    actual_hash = hash_file(filepath, algorithm)
    return secrets.compare_digest(actual_hash, expected_hash)   # Timing-safe comparison

# Usage
original_hash = hash_file("game_data/config.json")
print(f"Config hash: {original_hash}")

# Later — check nothing has changed
if verify_file("game_data/config.json", original_hash):
    print("Config file is intact.")
else:
    print("⚠️ Config file has been modified!")
```

### 26.5 Directory Integrity Monitoring

Monitor a folder and alert when any file changes, is added, or is deleted:

```python
import hashlib
import os
import time
import json
from pathlib import Path

def snapshot_directory(directory: str) -> dict[str, str]:
    """Returns a dict of {filepath: sha256_hash} for every file in the directory."""
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # Skip hidden dirs
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                snapshot[filepath] = hash_file(filepath)
            except (PermissionError, OSError):
                pass  # Skip files we can't read
    return snapshot

def compare_snapshots(before: dict, after: dict) -> dict:
    """Returns a summary of what changed between two snapshots."""
    changes = {"added": [], "deleted": [], "modified": []}

    for path, hash_val in after.items():
        if path not in before:
            changes["added"].append(path)
        elif before[path] != hash_val:
            changes["modified"].append(path)

    for path in before:
        if path not in after:
            changes["deleted"].append(path)

    return changes

def monitor_directory(directory: str, interval_seconds: int = 60):
    """Continuously monitors a directory for changes."""
    print(f"Starting monitor on {directory} (checking every {interval_seconds}s)...")
    baseline = snapshot_directory(directory)

    while True:
        time.sleep(interval_seconds)
        current = snapshot_directory(directory)
        changes = compare_snapshots(baseline, current)

        if any(changes.values()):
            for path in changes["added"]:
                print(f"✅ New file:      {path}")
            for path in changes["deleted"]:
                print(f"🗑️  Deleted:       {path}")
            for path in changes["modified"]:
                print(f"⚠️  Modified:      {path}")
            baseline = current  # Update baseline for next comparison
        else:
            print(f"[{time.strftime('%H:%M:%S')}] No changes detected.")
```

### 26.6 socket — Low-Level Network Access

`socket` is Python's interface to the operating system's network stack. It's the foundation that libraries like `requests` are built on. Direct socket usage is useful for port scanning, building simple servers, and working with raw network protocols.

```python
import socket

# Get your machine's hostname and local IP
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(f"Hostname: {hostname}, IP: {local_ip}")

# DNS lookup — resolve a hostname to an IP address
ip = socket.gethostbyname("github.com")
print(f"github.com → {ip}")

# Reverse lookup — IP address to hostname
hostname, _, _ = socket.gethostbyaddr("8.8.8.8")
print(f"8.8.8.8 → {hostname}")   # dns.google
```

### 26.7 Port Scanning

A port scanner checks which TCP ports on a target host are accepting connections. This is standard network diagnostics — exactly the kind of thing you'd use for CompTIA Network+ lab work or troubleshooting connectivity.

```python
import socket
import concurrent.futures
from typing import Optional

def scan_port(host: str, port: int, timeout: float = 1.0) -> tuple[int, bool, str]:
    """
    Attempts a TCP connection to host:port.
    Returns (port, is_open, service_name).
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))   # 0 = connected (open), non-zero = failed
        sock.close()

        is_open = result == 0
        service = ""
        if is_open:
            try:
                service = socket.getservbyport(port)  # Lookup well-known service name
            except OSError:
                service = "unknown"

        return port, is_open, service
    except (socket.error, OSError):
        return port, False, ""

def scan_host(host: str, ports: list[int], max_workers: int = 50) -> list[dict]:
    """
    Scans multiple ports concurrently using a thread pool.
    Returns a list of open ports with their service names.
    """
    open_ports = []

    # ThreadPoolExecutor runs up to max_workers scans concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, host, port): port for port in ports}

        for future in concurrent.futures.as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append({"port": port, "service": service})

    return sorted(open_ports, key=lambda x: x["port"])

# Scan common ports on a host
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443]

results = scan_host("192.168.1.1", COMMON_PORTS)
print(f"\nOpen ports on 192.168.1.1:")
for port_info in results:
    print(f"  {port_info['port']:5d}  {port_info['service']}")
```

> [!NOTE]
> Only scan hosts you own or have explicit written permission to scan. Unauthorised port scanning is illegal in many jurisdictions, regardless of intent. For practice, scan `localhost` or a virtual machine you control.

### 26.8 Simple TCP Client and Server

```python
import socket

# --- TCP CLIENT ---
def send_message(host: str, port: int, message: str) -> str:
    """Connects to a TCP server, sends a message, reads the response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(message.encode("utf-8"))
        response = sock.recv(4096)  # Read up to 4096 bytes
        return response.decode("utf-8")

# --- TCP SERVER (simple echo server) ---
def run_echo_server(host: str = "127.0.0.1", port: int = 9999):
    """Accepts one connection at a time and echoes messages back."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(5)
        print(f"Server listening on {host}:{port}")

        while True:
            client_sock, client_addr = server_sock.accept()
            print(f"Connection from {client_addr}")
            with client_sock:
                data = client_sock.recv(4096)
                if data:
                    client_sock.sendall(data)  # Echo the message back
```

---

**Practice:**
1. Use `secrets.token_urlsafe(32)` to generate a password reset token. Store it in a variable and write a verification check using `secrets.compare_digest()`.
2. Write a script that hashes three different files using `hash_file()` and stores the results in a JSON file as a baseline. Then modify one of the files and run the comparison function to detect the change.
3. Write a port scanner that scans ports 20–1024 on `localhost` using `concurrent.futures.ThreadPoolExecutor`. Print only the open ports with their service names.

---

# Technical Stack & Competency Map
### Senior Engineering Mentor & Systems Architect Edition

> **How to use this document:** Every section follows the same structure — real-world context, a concrete project, step-by-step technical breakdown, and a measurable mastery metric. Read ***Autism For Evil*** once to anchor the concept, then live inside the Practice Project until the Senior-Level Metric
> is true.

# Table of Contents

1. [Python — The Brain 🧠](#1-python--the-brain-)
   1.1 [AI Automation & LLM Agents](#capability-11--ai-automation--llm-agents)  
   1.2 [Data Orchestration & ETL Pipelines](#capability-12--data-orchestration--etl-pipelines)  
   1.3 [Asynchronous Programming](#capability-13--asynchronous-programming)

2. [C# / .NET — The Brawn ⚙️](#2-c--net--the-brawn-️)
   2.1 [Memory Management & Performance](#capability-21--memory-management--performance)  
   2.2 [Enterprise Logic & Async Patterns](#capability-22--enterprise-logic--async-patterns)

3. [PowerShell — The Glue 🔧](#3-powershell--the-glue-)
   3.1 [System Hardening & Security Auditing](#capability-31--system-hardening--security-auditing)  
   3.2 [Infrastructure Automation (IaC via PowerShell DSC)](#capability-32--infrastructure-automation-iac-via-powershell-dsc)

4. [PostgreSQL — The Memory 🗄️](#4-postgresql--the-memory-️)
   4.1 [Query Optimisation & Index Strategy](#capability-41--query-optimisation--index-strategy)  
   4.2 [Data Integrity & Audit Logging](#capability-42--data-integrity--audit-logging)

5. [TypeScript — The Face 🖥️](#5-typescript--the-face-️)
   5.1 [API Contracts & Runtime Validation](#capability-51--api-contracts--runtime-validation)

6. [The Hireable Developer Checklist ✅](#the-hireable-developer-checklist-)

7. [Systems Engineering Roadmap](#systems-engineering-roadmap)
---

## The Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE FIVE-LAYER STACK                         │
│                                                                 │
│  🖥️  TypeScript  ──  The Face     (Contract, UI Reliability)    │
│        ↕  consumes OpenAPI types from Python                    │
│  🧠  Python      ──  The Brain    (AI, Orchestration, ETL)      │
│        ↕  reads/writes to PostgreSQL                            │
│  🗄️  PostgreSQL  ──  The Memory   (Persistence, Integrity)      │
│        ↕  queried by C# services and Python pipelines           │
│  ⚙️  C#/.NET    ──  The Brawn    (Performance, Enterprise)      │
│        ↕  managed and deployed by PowerShell                    │
│  🔧  PowerShell  ──  The Glue     (Infra, Hardening, Cloud)     │
└─────────────────────────────────────────────────────────────────┘
```

> **The System Rule:** Python orchestrates. C# performs. PowerShell manages. PostgreSQL persists. TypeScript displays. No layer does another layer's job.

---

# 1. Python — The Brain 🧠
> *"Python is the orchestrator. It doesn't care how the hardware works or how the OS manages permissions — it only cares about logic, data flow, and connecting systems together."*

---

## Capability 1.1 — AI Automation & LLM Agents

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> In production, you don't *write* the AI — you write the *logic that talks to the AI*. Python's role is to be the **middle layer**: it ingests raw data (from a scraper or API), applies business logic to clean and filter it, sends it to an LLM with a structured prompt, and routes the response to a database or downstream service. The critical insight is that Python's strength here is not speed — it is **expressiveness and library depth**. Every major AI SDK (Anthropic, OpenAI, Hugging Face) has a Python-first interface. C# cannot match this ecosystem. TypeScript has no server-side AI pipeline story. Python owns this layer.

**The Data Flow:**
```
Raw Source (Web/API) → Python Logic Filter → LLM (Anthropic/OpenAI) → PostgreSQL / Action
```

### Practice Project: The AI Log Triage Agent
**Context:** Your production server generates 10,000 log lines per day. You are tired of manually scanning for `ERROR` entries. Build an agent that reads logs, identifies errors, queries the LLM for a plain-English remediation suggestion, and writes the triage report to PostgreSQL.

### The How-To Breakdown

**Step 1 — Read and Filter the Raw Data**
```python
# Read a log file line by line using a generator (never load a 1GB file into RAM)
def error_lines(filepath: str):
    with open(filepath, "r") as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()
```
- Learn: `open()` in read mode, `for` loops over file handles, `yield` for memory-safe generators.
- Why: A synchronous `readlines()` on a large file causes an OOM crash in production. The generator pattern is the correct approach regardless of file size.

**Step 2 — Send to the LLM with a Structured Prompt**
```python
import anthropic

client = anthropic.Anthropic()

def triage_error(error_line: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"You are a senior DevOps engineer. Explain this error and suggest a fix in 3 bullet points:\n\n{error_line}"
        }]
    )
    return message.content[0].text
```
- Learn: `anthropic` SDK, structured prompts, `.messages.create()`, extracting `.content[0].text`.
- Why: The prompt is the engineering artifact here. A vague prompt produces a vague answer. A structured prompt with a role and output constraint produces a usable remediation note.

**Step 3 — Store the Result in PostgreSQL**
```python
import psycopg2

def save_triage(conn, raw_error: str, suggestion: str):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO triage_log (raw_error, suggestion, created_at) VALUES (%s, %s, NOW())",
            (raw_error, suggestion)
        )
    conn.commit()
```
- Learn: `psycopg2` parameterised queries (`%s` placeholders — never f-strings in SQL), `conn.commit()`, context managers for cursor cleanup.
- Why: String-interpolated SQL (`f"INSERT ... VALUES ('{raw_error}')"`) is SQL injection. Parameterised queries are not optional. This is OWASP A03:2021.

**Step 4 — Wire it Together with Rate Limiting**
```python
import time

def run_pipeline(log_path: str, db_conn):
    for i, line in enumerate(error_lines(log_path)):
        suggestion = triage_error(line)
        save_triage(db_conn, line, suggestion)
        if i % 10 == 0:
            time.sleep(1)  # Respect the LLM API rate limit
        print(f"Processed: {i+1} errors")
```
- Learn: Rate limiting with `time.sleep()`, enumerate for progress tracking, composing the pipeline from the individual steps.

### Senior-Level Metric
> ✅ **You have mastered this when:** The pipeline processes a 500-line error log without crashing, without hitting the LLM rate limit, without loading the entire file into RAM (tracemalloc confirms peak usage < 10MB), and the PostgreSQL table contains clean, deduplicated rows. Every database call uses parameterised queries — a code review finds zero string-interpolated SQL.

---

## Capability 1.2 — Data Orchestration & ETL Pipelines

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> Data Orchestration is the production name for "getting data from A to B without losing any of it, duplicating any of it, or crashing when the source is unreliable." In an engineering team, raw scraped data is worthless — it has missing fields, duplicates, and schema inconsistencies. Python's job is to be the **transformation layer**: extract from source, validate the shape (Pydantic/Pandera), clean (normalise, deduplicate), and load into PostgreSQL in an **idempotent** way. Idempotency means you can run the pipeline twice and the database ends up in the same state as running it once. This is the difference between an amateur script and production infrastructure.

### Practice Project: Job Listings ETL Pipeline
**Context:** Scrape 200 job listings from a public jobs API, validate the schema, deduplicate by URL, and upsert into PostgreSQL. The pipeline must be re-runnable without creating duplicate rows.

### The How-To Breakdown

**Step 1 — Extract (Fetch with Retry Logic)**
```python
import httpx
import time

def fetch_listings(url: str, retries: int = 3) -> list[dict]:
    for attempt in range(retries):
        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return []
```
- Learn: `httpx` (the modern replacement for `requests`), `.raise_for_status()`, exponential backoff.
- Why: Networks fail. A pipeline with no retry logic is a pipeline that breaks every Tuesday at 3AM.

**Step 2 — Transform (Validate with Pydantic)**
```python
from pydantic import BaseModel, HttpUrl
from typing import Optional

class JobListing(BaseModel):
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: HttpUrl

def validate_listings(raw: list[dict]) -> list[JobListing]:
    valid = []
    for item in raw:
        try:
            valid.append(JobListing(**item))
        except Exception as e:
            print(f"Skipped invalid row: {e}")
    return valid
```
- Learn: Pydantic `BaseModel`, `Optional`, `HttpUrl`, validation errors without crashing the pipeline.
- Why: Pydantic is your **data contract**. It catches schema drift — when the upstream API adds or removes a field — before bad data reaches PostgreSQL.

**Step 3 — Load (Idempotent Upsert)**
```python
def upsert_listings(conn, listings: list[JobListing]):
    with conn.cursor() as cur:
        for job in listings:
            cur.execute("""
                INSERT INTO job_listings (title, company, location, salary_min, salary_max, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    salary_min = EXCLUDED.salary_min,
                    salary_max = EXCLUDED.salary_max,
                    updated_at = NOW()
            """, (job.title, job.company, job.location, job.salary_min, job.salary_max, str(job.url)))
    conn.commit()
```
- Learn: `ON CONFLICT (url) DO UPDATE` — PostgreSQL's upsert syntax. `EXCLUDED` refers to the row that *would have been inserted*.
- Why: Run this pipeline 10 times. The database has exactly 200 rows, not 2000. That is idempotency. Without `ON CONFLICT`, every pipeline run multiplies your data.

### Senior-Level Metric
> ✅ **You have mastered this when:** Running the pipeline 5 times in a row produces exactly the same number of rows in PostgreSQL as running it once. The Pydantic validator catches and logs at least one malformed row from a deliberately broken test fixture. The pipeline completes 200 records in under 30 seconds.

---

## Capability 1.3 — Asynchronous Programming

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> Synchronous code blocks execution. If your script makes 100 HTTP requests sequentially and each takes 500ms, the total runtime is 50 seconds — and your CPU is idle for 49.9 of those seconds, just waiting for network responses. Async programming solves this: instead of waiting for one request to finish before starting the next, the event loop manages hundreds of in-flight requests simultaneously, using a single thread. This is how modern web scrapers, data pipelines, and API clients achieve 10–100× throughput gains with zero additional hardware.

### Practice Project: Async Price Aggregator
**Context:** Fetch current prices from 5 cryptocurrency APIs simultaneously. Measure the wall-clock time difference between synchronous and async implementations.

### The How-To Breakdown

**Step 1 — The Synchronous Baseline (The Proof of the Problem)**
```python
import httpx, time

APIS = [
    "https://api.coinbase.com/v2/prices/BTC-USD/spot",
    "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
    # ... 3 more
]

def fetch_sync():
    results = []
    for url in APIS:
        r = httpx.get(url, timeout=5)
        results.append(r.json())
    return results

start = time.perf_counter()
fetch_sync()
print(f"Sync: {time.perf_counter() - start:.2f}s")
```

**Step 2 — The Async Replacement**
```python
import asyncio, httpx, time

async def fetch_one(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url, timeout=5)
    return response.json()

async def fetch_all():
    async with httpx.AsyncClient() as client:
        tasks = [fetch_one(client, url) for url in APIS]
        return await asyncio.gather(*tasks, return_exceptions=True)

start = time.perf_counter()
asyncio.run(fetch_all())
print(f"Async: {time.perf_counter() - start:.2f}s")
```
- Learn: `async def`, `await`, `asyncio.gather()`, `httpx.AsyncClient`, `return_exceptions=True` (one failure does not abort all).
- Why: `return_exceptions=True` is the production signal. Without it, one network timeout kills the entire batch.

**Step 3 — Add a Semaphore for Rate Limiting**
```python
async def fetch_all_limited(max_concurrent: int = 3):
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(client, url):
        async with sem:
            return await fetch_one(client, url)

    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_limit(client, url) for url in APIS]
        return await asyncio.gather(*tasks, return_exceptions=True)
```
- Learn: `asyncio.Semaphore` as a concurrency limiter, `async with sem` for automatic acquire/release.
- Why: Without a semaphore, `asyncio.gather(1000 tasks)` sends 1000 requests simultaneously. Most APIs will rate-limit or ban you. The semaphore is the politeness layer.

### Senior-Level Metric
> ✅ **You have mastered this when:** Your async version completes in roughly the time of the single slowest request (not the sum of all requests). You can articulate why `asyncio.gather` with `return_exceptions=True` is safer than without. You can explain why async does NOT help CPU-bound work — and know that `multiprocessing.Pool` is the correct solution for that case.

---

# 2. C# / .NET — The Brawn ⚙️
> *"C# is where the theory meets the hardware. The CLR makes memory layout, garbage collection, and concurrency physically observable — use the debugger and profiler, not just unit tests."*

---

## Capability 2.1 — Memory Management & Performance

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> Every Python and TypeScript developer operates with a mental model of "objects just exist." In C#, you are forced to confront the truth: objects are bytes in RAM, allocated on either the Stack (fast, automatic, fixed size) or the Heap (flexible, GC-managed, expensive). The **Garbage Collector** does not run on demand — it runs on its own schedule, and it pauses your application when it does. A service handling 50,000 requests/second cannot afford a 200ms GC pause. Senior .NET engineers write code that minimises allocations, reuses buffers, and keeps the GC in Gen 0 where collections are cheap and fast.

### Practice Project: The Memory-Safe HTTP Parser
**Context:** Parse raw HTTP request lines (`GET /api/users?page=2 HTTP/1.1`) into structured components (method, path, query string, version) using zero heap allocations.

### The How-To Breakdown

**Step 1 — The Naive Allocation-Heavy Version (The Baseline)**
```csharp
public record HttpRequestLine(string Method, string Path, string QueryString, string Version);

public HttpRequestLine ParseNaive(string rawLine)
{
    // string.Split allocates a new string[] AND new string instances for each segment
    var parts = rawLine.Split(' ');
    var pathParts = parts[1].Split('?');
    return new HttpRequestLine(
        Method: parts[0],
        Path: pathParts[0],
        QueryString: pathParts.Length > 1 ? pathParts[1] : string.Empty,
        Version: parts[2]
    );
}
```

**Step 2 — The Zero-Allocation Span Version**
```csharp
public ref struct HttpRequestLineParsed
{
    public ReadOnlySpan<char> Method;
    public ReadOnlySpan<char> Path;
    public ReadOnlySpan<char> QueryString;
    public ReadOnlySpan<char> Version;
}

public HttpRequestLineParsed ParseWithSpan(ReadOnlySpan<char> rawLine)
{
    // Span<T> slices the SAME memory — no new strings allocated
    int firstSpace  = rawLine.IndexOf(' ');
    int secondSpace = rawLine[(firstSpace + 1)..].IndexOf(' ') + firstSpace + 1;

    var pathAndQuery = rawLine[(firstSpace + 1)..secondSpace];
    int questionMark = pathAndQuery.IndexOf('?');

    return new HttpRequestLineParsed
    {
        Method      = rawLine[..firstSpace],
        Path        = questionMark >= 0 ? pathAndQuery[..questionMark] : pathAndQuery,
        QueryString = questionMark >= 0 ? pathAndQuery[(questionMark + 1)..] : ReadOnlySpan<char>.Empty,
        Version     = rawLine[(secondSpace + 1)..]
    };
}
```
- Learn: `ReadOnlySpan<char>`, slice syntax `[start..end]`, `ref struct` (stack-only, cannot be boxed to the heap).
- Why: `Span<T>` is how ASP.NET Core's Kestrel parses millions of HTTP requests per second. No allocations means no GC pressure.

**Step 3 — Prove it with BenchmarkDotNet**
```csharp
using BenchmarkDotNet.Attributes;

[MemoryDiagnoser]
public class ParserBenchmark
{
    private const string Line = "GET /api/users?page=2&limit=50 HTTP/1.1";

    [Benchmark(Baseline = true)]
    public HttpRequestLine Naive() => ParseNaive(Line);

    [Benchmark]
    public HttpRequestLineParsed WithSpan() => ParseWithSpan(Line.AsSpan());
}
```
- Learn: `[MemoryDiagnoser]` attribute, `[Benchmark]`, interpreting the Allocated column.
- Why: The naive version shows ~200 bytes allocated per call. The Span version shows **0 bytes**. This is not a micro-optimisation for hot paths — it is the difference between a service that runs for days and one that generates GC pressure until it becomes unstable.

### Senior-Level Metric
> ✅ **You have mastered this when:** BenchmarkDotNet shows the `Span<T>` version allocates exactly 0 bytes. You can explain why `ref struct` cannot be used as a field in a regular class (it would escape to the heap). You can point to the exact GC generation that the naive version's `string[]` allocation lands in (Gen 0), and explain why thousands of short-lived Gen 0 allocations cause frequent collection pauses.

---

## Capability 2.2 — Enterprise Logic & Async Patterns

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> Enterprise C# code is not just "C# that runs in a big company." It means code designed for **long-running services**, **concurrent access**, and **graceful failure**. The most common catastrophic mistake is calling `.Result` or `.Wait()` on an async method from a synchronous context — this creates a **deadlock** that silently freezes a thread. In an ASP.NET application, this can starve the ThreadPool and bring down the service under load. Senior .NET engineers understand that `async` is a colour — once you mark a method `async`, every caller must also be `async`, all the way to the top of the call stack.

### Practice Project: The Payment Processor with Circuit Breaker
**Context:** Build a payment processing service using an `IPaymentProcessor` interface. Wrap it with a circuit breaker that opens after 3 consecutive failures, rejecting all calls for 30 seconds before attempting recovery.

### The How-To Breakdown

**Step 1 — Define the Contract (Interface-Driven Design)**
```csharp
public record PaymentResult(bool Success, string TransactionId, string? ErrorMessage);

public interface IPaymentProcessor
{
    Task<PaymentResult> ProcessPaymentAsync(decimal amount, string currency, CancellationToken ct = default);
}

public class StripeProcessor : IPaymentProcessor
{
    public async Task<PaymentResult> ProcessPaymentAsync(decimal amount, string currency, CancellationToken ct)
    {
        // Real implementation calls the Stripe API
        await Task.Delay(50, ct); // Simulate latency
        return new PaymentResult(true, Guid.NewGuid().ToString(), null);
    }
}
```
- Learn: `interface`, `record` for immutable data types, `Task<T>` return types, `CancellationToken`.
- Why: The calling code never knows if it is talking to Stripe or PayFast. Swapping processors is a one-line change. This is SOLID's Open/Closed principle — open for extension, closed for modification.

**Step 2 — The Circuit Breaker Decorator**
```csharp
public class CircuitBreakerProcessor : IPaymentProcessor
{
    private readonly IPaymentProcessor _inner;
    private int _consecutiveFailures;
    private DateTime _openUntil = DateTime.MinValue;
    private readonly int _threshold;
    private readonly TimeSpan _resetPeriod;

    public CircuitBreakerProcessor(IPaymentProcessor inner, int threshold = 3, int resetSeconds = 30)
    {
        _inner = inner;
        _threshold = threshold;
        _resetPeriod = TimeSpan.FromSeconds(resetSeconds);
    }

    public async Task<PaymentResult> ProcessPaymentAsync(decimal amount, string currency, CancellationToken ct)
    {
        if (DateTime.UtcNow < _openUntil)
            return new PaymentResult(false, string.Empty, "Circuit open — service unavailable");

        try
        {
            var result = await _inner.ProcessPaymentAsync(amount, currency, ct);
            _consecutiveFailures = 0;
            return result;
        }
        catch (Exception ex)
        {
            if (++_consecutiveFailures >= _threshold)
                _openUntil = DateTime.UtcNow.Add(_resetPeriod);
            return new PaymentResult(false, string.Empty, ex.Message);
        }
    }
}
```
- Learn: Decorator pattern, `DateTime.UtcNow` (always UTC in distributed systems), pre-increment `++_consecutiveFailures`.
- Why: The Decorator pattern means the circuit breaker wraps **any** `IPaymentProcessor` — you can stack decorators: `new CircuitBreakerProcessor(new RetryProcessor(new StripeProcessor()))`. Each decorator adds one concern without modifying the others.

**Step 3 — Wire it with Dependency Injection**
```csharp
// In Program.cs (ASP.NET Core minimal API):
builder.Services.AddSingleton<IPaymentProcessor>(sp =>
    new CircuitBreakerProcessor(
        new StripeProcessor(),
        threshold: 3,
        resetSeconds: 30
    )
);
```
- Learn: `AddSingleton`, `AddScoped`, `AddTransient` — understand the lifetime differences.
- Why: The DI container means you can swap `StripeProcessor` for a `MockProcessor` in tests without changing any business logic. This is testability by design.

### Senior-Level Metric
> ✅ **You have mastered this when:** You can reproduce the classic ASP.NET deadlock by calling `.Result` on an async method from a synchronous context inside a controller, then fix it three ways: `ConfigureAwait(false)`, async-all-the-way-up, and `Task.Run()`. You can explain which fix is appropriate in which scenario. The circuit breaker correctly rejects calls during the open period and recovers after the reset timeout.

---

# 3. PowerShell — The Glue 🔧
> *"PowerShell is not a shell with scripting bolted on — it is a .NET runtime with a shell interface. It pipes objects, not text. It enforces state, not steps."*

---

## Capability 3.1 — System Hardening & Security Auditing

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> In a production Windows environment, the hardening of a server is not a one-time task — it is a **continuously enforced state**. Attackers look for: SUID-equivalent binaries with elevated privileges, services running as SYSTEM without justification, open ports no one knows about, and accounts whose passwords haven't been changed since the Obama administration. PowerShell is the tool that automates the detection and remediation of all of these — at scale, across hundreds of machines, without a single RDP session. The senior signal is the `-WhatIf` parameter: every destructive script must support dry-run mode before it touches production.

### Practice Project: The Security Posture Audit Script
**Context:** Build a script that audits a Windows machine and produces a JSON risk report: inactive users, services running as SYSTEM, open ports, and missing Windows updates. Run it with `-WhatIf` to preview and `-Remediate` to fix.

### The How-To Breakdown

**Step 1 — Gather System State (Object Pipeline)**
```powershell
function Get-InactiveUsers {
    $threshold = (Get-Date).AddDays(-90)
    Get-LocalUser |
        Where-Object { $_.Enabled -and $_.LastLogon -lt $threshold } |
        Select-Object Name, LastLogon,
            @{Name='DaysSinceLogin'; Expression={((Get-Date) - $_.LastLogon).Days}},
            @{Name='RiskScore'; Expression={
                if ($_.PasswordNeverExpires) { 'HIGH' } else { 'MEDIUM' }
            }}
}
```
- Learn: `Get-LocalUser`, `Where-Object`, calculated properties (`@{Name=...; Expression=...}`), `Select-Object`.
- Why: PowerShell returns objects with typed properties — you filter on `.LastLogon` (a `DateTime` object), not on a parsed string. This is the pipeline's advantage over Bash.

**Step 2 — Audit Open Ports with Process Mapping**
```powershell
function Get-SuspiciousListeners {
    Get-NetTCPConnection -State Listen |
        Where-Object { $_.LocalPort -notin @(80, 443, 3389, 5985) } |
        ForEach-Object {
            $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            [PSCustomObject]@{
                Port        = $_.LocalPort
                PID         = $_.OwningProcess
                ProcessName = $process?.Name ?? 'Unknown'
                RiskLevel   = if ($_.LocalPort -lt 1024) { 'HIGH' } else { 'LOW' }
            }
        }
}
```
- Learn: `Get-NetTCPConnection`, `ForEach-Object`, `[PSCustomObject]`, null-conditional `?` operator.
- Why: An open port with an unknown process name is an immediate incident. This script surfaces that in seconds across any machine.

**Step 3 — Output as JSON and Support `-WhatIf`**
```powershell
function Invoke-SecurityAudit {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$OutputPath = ".\security_report.json",
        [switch]$Remediate
    )

    $report = @{
        Timestamp      = (Get-Date -Format 'o')
        InactiveUsers  = @(Get-InactiveUsers)
        SuspiciousPorts = @(Get-SuspiciousListeners)
    }

    if ($Remediate) {
        foreach ($user in $report.InactiveUsers | Where-Object RiskScore -eq 'HIGH') {
            if ($PSCmdlet.ShouldProcess($user.Name, "Disable-LocalUser")) {
                Disable-LocalUser -Name $user.Name
            }
        }
    }

    $report | ConvertTo-Json -Depth 5 | Set-Content $OutputPath
    Write-Host "Report written to: $OutputPath"
}
```
- Learn: `[CmdletBinding(SupportsShouldProcess)]`, `$PSCmdlet.ShouldProcess()`, `-WhatIf` parameter, `ConvertTo-Json -Depth`.
- Why: `ShouldProcess` is not optional for destructive operations. Every script that disables accounts, modifies the registry, or changes firewall rules must respect `-WhatIf`. This is what separates a production script from a dangerous one.

### Senior-Level Metric
> ✅ **You have mastered this when:** Running the script with `-WhatIf` prints a complete list of every action it *would* take without executing any of them. The JSON output loads cleanly into Python (`json.load()`) for further processing. You can explain why `$ErrorActionPreference = 'Stop'` must be set at the top of every production script (without it, errors are non-terminating and the script continues silently after failures).

---

## Capability 3.2 — Infrastructure Automation (IaC via PowerShell DSC)

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> Provisioning a server manually takes an engineer 2 hours and is unrepeatable — the second server is never exactly the same as the first. PowerShell DSC (Desired State Configuration) solves this with a fundamentally different model: instead of writing *steps* (imperative), you write *state* (declarative). You say "IIS should be installed, this application pool should exist, this firewall port should be open" — and the DSC engine works out the difference between the current state and the desired state and applies only the necessary changes. This is idempotency at the infrastructure level, and it is the Windows equivalent of Terraform or Ansible.

### Practice Project: The Idempotent Web Server Bootstrap
**Context:** Write a DSC configuration that provisions a Windows Server 2022 node as a web server: IIS installed, a specific app pool created, the correct firewall rules open, and a monitoring service account configured. Run it 3 times — the server must be in the exact same state after every run.

### The How-To Breakdown

**Step 1 — Write the DSC Configuration**
```powershell
Configuration WebServerBaseline {
    param ([string[]]$NodeName = 'localhost')

    Import-DscResource -ModuleName PSDesiredStateConfiguration

    Node $NodeName {

        WindowsFeature IIS {
            Name   = 'Web-Server'
            Ensure = 'Present'
        }

        WindowsFeature AspNet45 {
            Name      = 'Web-Asp-Net45'
            Ensure    = 'Present'
            DependsOn = '[WindowsFeature]IIS'
        }

        Service AppPoolMonitor {
            Name        = 'W3SVC'
            StartupType = 'Automatic'
            State       = 'Running'
            DependsOn   = '[WindowsFeature]IIS'
        }

        Firewall WebPort80 {
            Name      = 'HTTP-Inbound'
            Direction = 'Inbound'
            Protocol  = 'TCP'
            LocalPort = '80'
            Action    = 'Allow'
            Ensure    = 'Present'
        }
    }
}
```
- Learn: `Configuration` block, `Node` block, `Import-DscResource`, `DependsOn`, `Ensure = 'Present'/'Absent'`.
- Why: `DependsOn` is the dependency graph. DSC resolves the order of operations automatically — you declare what must exist before what, not the sequence of commands.

**Step 2 — Compile and Apply**
```powershell
# Compile the configuration to a MOF file
WebServerBaseline -OutputPath "C:\DSC\WebServer"

# Apply the configuration
Start-DscConfiguration -Path "C:\DSC\WebServer" -Wait -Verbose -Force
```

**Step 3 — Verify Idempotency**
```powershell
# Test: returns True if the system is in the desired state, False if it needs changes
$result = Test-DscConfiguration -Detailed

$result.ResourcesNotInDesiredState | ForEach-Object {
    Write-Warning "Not in desired state: $($_.ResourceId)"
}

if ($result.InDesiredState) {
    Write-Host "✅ All resources are in the desired state." -ForegroundColor Green
}
```
- Learn: `Test-DscConfiguration`, `Start-DscConfiguration -Wait -Verbose`, `Get-DscConfigurationStatus`.
- Why: `Test-DscConfiguration` is your **infrastructure unit test**. Run it after every deployment. If it returns `False`, something deviated from the declared baseline — either a manual change or a failed deployment.

### Senior-Level Metric
> ✅ **You have mastered this when:** Running `Start-DscConfiguration` three times in a row produces no changes on the second and third runs — `Test-DscConfiguration` returns `InDesiredState: True` after the first application. You can explain the difference between `Push` mode (you apply manually) and `Pull` mode (nodes periodically self-heal from a DSC pull server).

---

# 4. PostgreSQL — The Memory 🗄️
> *"PostgreSQL is not just a data store. It is the single source of truth for the entire system. Every other layer — Python, C#, TypeScript, PowerShell — is a temporary consumer. PostgreSQL is the permanent record."*

---

## Capability 4.1 — Query Optimisation & Index Strategy

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> A missing index on a production table with 10 million rows is not a performance problem — it is a **user experience disaster**. A 50ms query with the right index becomes a 5-second sequential scan without it. The difference is invisible in development (where tables have 100 rows) and catastrophic in production. `EXPLAIN ANALYSE` is not an advanced tool — it is the first thing a senior engineer runs on any query that touches a large table. The query plan shows you exactly what PostgreSQL is doing: whether it found a useful index, how many rows it scanned, and where the time was spent.

### Practice Project: The Job Search Performance Tuner
**Context:** You have a `job_listings` table with 1 million rows. Write a query to find Python jobs in Johannesburg with a salary above R30,000. Profile it with `EXPLAIN ANALYSE`, identify the bottleneck, add the correct index, and prove the improvement.

### The How-To Breakdown

**Step 1 — Create the Table and Insert Test Data**
```sql
CREATE TABLE job_listings (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    company     TEXT NOT NULL,
    city        TEXT NOT NULL,
    salary_min  INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Insert 1,000,000 test rows
INSERT INTO job_listings (title, company, city, salary_min)
SELECT
    CASE (random() * 4)::int
        WHEN 0 THEN 'Python Developer'
        WHEN 1 THEN 'Java Engineer'
        WHEN 2 THEN 'DevOps Engineer'
        ELSE 'Frontend Developer'
    END,
    'Company ' || (random() * 1000)::int,
    CASE (random() * 3)::int
        WHEN 0 THEN 'Johannesburg'
        WHEN 1 THEN 'Cape Town'
        ELSE 'Durban'
    END,
    (random() * 80000 + 10000)::int
FROM generate_series(1, 1000000);
```

**Step 2 — Profile the Query (Before Index)**
```sql
EXPLAIN ANALYSE
SELECT id, title, company, salary_min
FROM job_listings
WHERE city = 'Johannesburg'
  AND title ILIKE '%python%'
  AND salary_min > 30000
ORDER BY salary_min DESC
LIMIT 20;
```
- Read the plan: look for `Seq Scan on job_listings`. This means PostgreSQL reads **every row** in the table. For 1M rows, this is the problem.

**Step 3 — Add the Correct Index**
```sql
-- Composite index: city first (high selectivity), then salary_min
CREATE INDEX idx_jobs_city_salary ON job_listings (city, salary_min DESC)
WHERE salary_min IS NOT NULL;

-- GIN index for full-text matching (more efficient than ILIKE for production scale)
CREATE INDEX idx_jobs_title_trgm ON job_listings
USING gin (title gin_trgm_ops);

-- Enable the pg_trgm extension first
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```
- Learn: Composite index column order (high-selectivity column first), partial indexes (`WHERE salary_min IS NOT NULL`), GIN indexes for text search, `pg_trgm` extension.
- Why: The `city` filter eliminates ~67% of rows immediately. The `salary_min` sort benefits from the descending index order. The GIN trigram index makes `ILIKE '%python%'` use an index instead of a sequential scan.

**Step 4 — Re-Profile and Compare**
```sql
EXPLAIN (ANALYSE, BUFFERS, FORMAT TEXT)
SELECT id, title, company, salary_min
FROM job_listings
WHERE city = 'Johannesburg'
  AND title ILIKE '%python%'
  AND salary_min > 30000
ORDER BY salary_min DESC
LIMIT 20;
```
- Look for the plan to change from `Seq Scan` to `Index Scan` or `Bitmap Index Scan`.
- Look for `Buffers: shared hit` to increase relative to `shared read` — this means the index pages are being cached.

### Senior-Level Metric
> ✅ **You have mastered this when:** `EXPLAIN ANALYSE` shows the query drops from a ~800ms sequential scan to a ~3ms index scan. You can explain why putting `salary_min` as the leading column in the composite index would perform worse for this specific query (because `city` eliminates more rows per lookup than `salary_min` does). You can read the `cost` and `actual rows` values in the plan and identify when the planner's estimate diverges from reality (a sign that `ANALYSE` needs to be run to update statistics).

---

## Capability 4.2 — Data Integrity & Audit Logging

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> In a financial or compliance-sensitive system, "who changed what and when" is not optional metadata — it is a legal requirement. PostgreSQL's trigger system lets you enforce audit logging at the **database layer**, meaning it cannot be bypassed by any application bug, rogue API call, or direct database connection. A trigger fires on `INSERT`, `UPDATE`, or `DELETE` and writes a row to an audit table before the change is committed. This is the only truly reliable audit mechanism: application-layer logging can be disabled or bypassed, but a database trigger cannot be turned off without a schema migration that itself gets logged.

### Practice Project: The Immutable Audit Log
**Context:** Add an audit log to the `job_listings` table. Every `UPDATE` and `DELETE` must write the old row's data to an `audit_log` table as JSONB, along with the operation type, timestamp, and database user who made the change.

### The How-To Breakdown

**Step 1 — Create the Audit Table**
```sql
CREATE TABLE audit_log (
    id           BIGSERIAL PRIMARY KEY,
    table_name   TEXT NOT NULL,
    operation    TEXT NOT NULL CHECK (operation IN ('UPDATE', 'DELETE')),
    old_data     JSONB NOT NULL,
    changed_by   TEXT NOT NULL DEFAULT current_user,
    changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast lookups by table and time
CREATE INDEX idx_audit_table_time ON audit_log (table_name, changed_at DESC);
```

**Step 2 — Write the Trigger Function**
```sql
CREATE OR REPLACE FUNCTION fn_audit_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(OLD));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$;
```
- Learn: `TG_OP` (the operation type), `TG_TABLE_NAME` (the table being modified), `OLD` (the row before the change), `to_jsonb(OLD)` (serialise the entire row as JSONB).
- Why: `to_jsonb(OLD)` captures the full state of the row at the moment of the change, including all columns — even ones added later. This future-proofs the audit log.

**Step 3 — Attach the Trigger**
```sql
CREATE TRIGGER trg_audit_job_listings
AFTER UPDATE OR DELETE ON job_listings
FOR EACH ROW
EXECUTE FUNCTION fn_audit_changes();
```

**Step 4 — Verify and Query**
```sql
-- Make a change and verify it was captured
UPDATE job_listings SET salary_min = 99999 WHERE id = 1;
DELETE FROM job_listings WHERE id = 2;

-- Query the audit trail for a specific row
SELECT
    operation,
    old_data ->> 'title'      AS old_title,
    (old_data ->> 'salary_min')::int AS old_salary,
    changed_by,
    changed_at
FROM audit_log
WHERE old_data ->> 'id' = '1'
ORDER BY changed_at DESC;
```
- Learn: JSONB `->>` operator (extract as text), `::int` cast, filtering on JSONB fields.

### Senior-Level Metric
> ✅ **You have mastered this when:** Every `UPDATE` and `DELETE` on `job_listings` produces an audit row with the complete previous state as JSONB — including future columns added after the trigger was created. You can reconstruct the full history of a row by querying `audit_log WHERE old_data ->> 'id' = 'X' ORDER BY changed_at`. You can explain why `AFTER` triggers (which fire after the change) are safer than `BEFORE` triggers for audit logging (the change is guaranteed to succeed before the audit row is written).

---

# 5. TypeScript — The Face 🖥️
> *"TypeScript is the compiler that finds bugs introduced by your Python backend before they reach the user. Types are not documentation — they are executable contracts."*

---

## Capability 5.1 — API Contracts & Runtime Validation

> [!tip] ### ***Autism For Evil*** (Real-World Context)
> TypeScript's types exist only at compile time — they are erased when the code runs. This means that if your Python FastAPI returns a JSON object with a field named `salary_min` and your TypeScript code expects `salaryMin`, you will not get a compile error. You will get `undefined` silently at runtime, and a React component that renders nothing. **Zod** solves this by providing runtime validation that mirrors your TypeScript types. The workflow is: define a Zod schema → derive the TypeScript type from it (`z.infer<typeof schema>`) → validate every API response through the schema at the boundary. This is the contract between the Python Brain and the TypeScript Face.

### Practice Project: The Type-Safe Job Board
**Context:** Build a Next.js page that fetches job listings from the Python FastAPI, validates the response shape with Zod at runtime, and renders the listings. A schema mismatch must produce a clear error, not a silent `undefined`.

### The How-To Breakdown

**Step 1 — Define the Zod Schema (Single Source of Truth)**
```typescript
import { z } from 'zod';

// This schema is both the runtime validator AND the TypeScript type definition
export const JobListingSchema = z.object({
  id:         z.number().int().positive(),
  title:      z.string().min(1),
  company:    z.string().min(1),
  city:       z.string(),
  salary_min: z.number().int().nullable().optional(),
  created_at: z.string().datetime(),
});

// TypeScript type inferred from the schema — no duplication
export type JobListing = z.infer<typeof JobListingSchema>;

export const JobListingsResponseSchema = z.object({
  items: z.array(JobListingSchema),
  total: z.number(),
  page:  z.number(),
});

export type JobListingsResponse = z.infer<typeof JobListingsResponseSchema>;
```
- Learn: `z.object()`, `z.string()`, `z.number()`, `.nullable()`, `.optional()`, `z.infer<>`, `z.array()`.
- Why: `z.infer<typeof JobListingSchema>` means your TypeScript type and your runtime validator are **the same object**. When you update the schema, the type updates automatically. No risk of them drifting apart.

**Step 2 — The Type-Safe Fetch Function**
```typescript
import { z } from 'zod';
import { JobListingsResponseSchema, type JobListingsResponse } from './schemas';

type Result<T> = { ok: true; data: T } | { ok: false; error: string };

async function fetchJobs(page: number = 1): Promise<Result<JobListingsResponse>> {
  try {
    const response = await fetch(`/api/jobs?page=${page}`);
    if (!response.ok) {
      return { ok: false, error: `HTTP ${response.status}: ${response.statusText}` };
    }

    const rawJson = await response.json();

    // Runtime validation — this is where the Python/TypeScript contract is enforced
    const parsed = JobListingsResponseSchema.safeParse(rawJson);
    if (!parsed.success) {
      console.error('Schema validation failed:', parsed.error.flatten());
      return { ok: false, error: 'API response shape has changed — contact backend team' };
    }

    return { ok: true, data: parsed.data };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : 'Unknown error' };
  }
}
```
- Learn: `safeParse()` (returns `{ success, data, error }` instead of throwing), `.flatten()` for human-readable error output, the `Result<T>` discriminated union for typed error handling.
- Why: `.parse()` throws on invalid data. `.safeParse()` returns a typed result you can handle cleanly. In a UI, throwing is catastrophic — the entire component tree crashes. `safeParse` lets you show a user-friendly error instead.

**Step 3 — Render with Full Type Safety (React Component)**
```typescript
import { useEffect, useState } from 'react';
import type { JobListingsResponse } from './schemas';

type PageState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; data: JobListingsResponse };

export function JobBoard() {
  const [state, setState] = useState<PageState>({ status: 'idle' });

  useEffect(() => {
    setState({ status: 'loading' });
    fetchJobs().then(result => {
      if (result.ok) {
        setState({ status: 'success', data: result.data });
      } else {
        setState({ status: 'error', message: result.error });
      }
    });
  }, []);

  // Exhaustive handling — TypeScript errors if you miss a case
  switch (state.status) {
    case 'idle':    return null;
    case 'loading': return <p>Loading...</p>;
    case 'error':   return <p className="text-red-500">Error: {state.message}</p>;
    case 'success': return (
      <ul>
        {state.data.items.map(job => (
          <li key={job.id}>
            <strong>{job.title}</strong> at {job.company} — {job.city}
            {job.salary_min && ` · R${job.salary_min.toLocaleString()}`}
          </li>
        ))}
      </ul>
    );
  }
}
```
- Learn: Discriminated union for component state, `useEffect`, `useState<PageState>`, exhaustive `switch` with TypeScript ensuring every state is handled.
- Why: The `PageState` discriminated union means TypeScript knows that inside `case 'success':`, `state.data` is guaranteed to be a `JobListingsResponse`. You cannot accidentally access `state.data.items` in the `loading` case — the compiler prevents it.

### Senior-Level Metric
> ✅ **You have mastered this when:** You deliberately change the Python Pydantic model to rename `salary_min` to `salaryMin`. The Zod validator catches the mismatch at runtime and logs a clear error message. The React component renders an error state instead of crashing. The TypeScript type updates to reflect the new field name only after you update the Zod schema — not before. This is the contract enforcement cycle working correctly.

---

# The Hireable Developer Checklist ✅

> **What a hiring manager at a systems engineering firm actually wants to see from a junior-to-mid candidate.** This is not a list of technologies — it is a list of engineering behaviours.

---

### System Design

- [ ] **01 — Defined API contracts before writing code.** Every endpoint has a documented request/response schema (Pydantic on the Python side, Zod on the TypeScript side) before any implementation begins. Schema drift is caught at the boundary, not 3 hours into debugging.

- [ ] **02 — Error handling is explicit at every layer boundary.** Errors are not `print()` statements or silent `None` returns. Each layer has typed error responses (`Result<T, E>` pattern), HTTP status codes are meaningful (400 vs 422 vs 500), and the user always sees a descriptive error — never an uncaught exception stack trace.

- [ ] **03 — Data flows in one direction.** Python writes to PostgreSQL. TypeScript reads from Python's API. TypeScript never writes directly to the database. PostgreSQL never calls TypeScript. The architecture diagram has arrows, and those arrows have directions.

---

### Discipline

- [ ] **04 — Every commit follows Conventional Commits.** `feat(api): add salary filter to job search endpoint` — not `fixed stuff` or `updates`. Commit history tells the story of the feature without needing to read the diff. Employers read commit history in interviews.

- [ ] **05 — Every major decision has an ADR.** Why PostgreSQL over MongoDB? Why Zod over Yup? Why async/await over threading? Architecture Decision Records capture the reasoning, the alternatives considered, and the trade-offs accepted. Future you — and your team — will thank present you.

- [ ] **06 — READMEs pass the Stranger Test.** Give your README to someone who has never seen the project. They must be able to clone it, install dependencies, run it, and understand what it does — in under 5 minutes, without asking you anything. If they get stuck, the README has a bug.

---

### Security

- [ ] **07 — Zero string-interpolated SQL.** Every database query uses parameterised placeholders (`%s` in psycopg2, `@param` in Npgsql, `?` in SQLite). The word `f"SELECT * FROM users WHERE id = {user_id}"` does not exist in any file, anywhere. OWASP A03:2021 is not a theoretical risk.

- [ ] **08 — No secrets in code or version control.** API keys, database passwords, and connection strings live in `.env` files (excluded from `.gitignore`), environment variables, or a secrets manager (HashiCorp Vault). Running `git log -p | grep -i password` on the repository returns nothing.

- [ ] **09 — Dependencies are audited.** `pip-audit` (Python) and `dotnet list package --vulnerable` (C#) run as part of the CI pipeline. The candidate knows what `CVE` stands for and has patched at least one dependency vulnerability as a result of a scanner finding.

---

### Professionalism

- [ ] **10 — Projects have measurable success metrics.** Not "I built a scraper." But: "The scraper processes 500 URLs in under 60 seconds (measured with `time.perf_counter()`), maintains peak RAM usage below 50MB (measured with `tracemalloc`), and has zero duplicate rows in PostgreSQL after 10 consecutive pipeline runs (verified by query)." Claims are supported by numbers. Numbers are produced by tools, not estimates.

---

> *"Hireable developers don't just write code that works. They write code that the next developer — or their future self — can understand, extend, and trust."*

---

*Systems Engineering Roadmap · laughtale.co.za · Damian Thulani · Zero to Senior Engineer*

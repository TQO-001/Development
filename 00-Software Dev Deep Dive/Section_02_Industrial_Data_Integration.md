# Section 2 — Industrial Data Integration

## Why this section exists

This is where the general foundation from Section 1 meets the industrial world from `03-Industrial Deep Dive`. A huge chunk of real industrial software dev work isn't writing new control logic (that's the automation engineers' job, mostly at Level 1) — it's **getting data out of, or into, the systems described in that track's Section 2 and 4 (Purdue Model, MES/SCADA/Historian)**, reliably, safely, and without breaking anything OT depends on. This is "system integration" from the motivation letter, made concrete.

---

## 1. The golden rule: read from OT, don't write to OT (until you really know what you're doing)

Nearly all industrial data integration work a junior/intern touches is **pulling data out** of OT systems (historian values, batch records, alarm history) for use in dashboards, reports, or business systems — not pushing commands or setpoints back in. This isn't a technicality, it's the practical version of everything Section 3 (Segmentation) and Section 2 (Purdue Model, Availability-first) taught you in the Industrial Deep Dive: a bad read query can slow a report; a bad write can genuinely disrupt production. Default assumption for any new integration task: **you're building a read path unless someone explicitly and deliberately tells you otherwise, and a write path gets far more scrutiny, testing, and sign-off before it ever touches anything real.**

## 2. Talking to a historian

Historians (Section 2/4 of the Industrial Deep Dive — e.g., OSIsoft/AVEVA PI, Ignition's historian) expose their data through:
- **A SQL-like query interface** — many historians offer an interface that looks like SQL (e.g., PI's "PI SQL" / AF SDK, or a historian's ODBC driver) even though the underlying storage is specialized time-series, not a relational database — this lets a dev query it with mostly-familiar SQL knowledge.
- **A REST/Web API** — modern historians increasingly expose a REST API (e.g., PI Web API) so you can query tag history over HTTP and get JSON back, fitting naturally into the API patterns from Section 1.
- **Time-range and interpolation concepts you need to actually understand, not just the syntax:** a historian query isn't just "give me all rows" — you specify a start time, end time, and often an **interpolation interval** (e.g., "give me this tag's value every 60 seconds between these two timestamps," even if the tag was actually only recorded irregularly) or ask for **raw/recorded values only** (every value actually stored, whenever it changed). Getting this wrong (e.g., accidentally requesting raw data for a wide time range across thousands of fast-changing tags) is a classic way a new dev accidentally hammers a historian with a much bigger query than intended.

## 3. Talking to MES / production systems

MES systems (Section 2/4 of the Industrial Deep Dive) typically expose integration points via:
- **A relational database you're allowed to read from** (often a dedicated reporting/replica database, deliberately separate from the live transactional database the MES application itself uses — so your queries can't accidentally slow down the actual production system).
- **A vendor-specific or custom REST API** for both reading (work order status, batch results) and, in controlled cases, writing (e.g., an external system confirming a shipment, which MES needs to know about).
- **Message queues / event-driven integration** — instead of your code polling "has anything changed?" repeatedly, the MES publishes events (e.g., "batch completed") to a queue (RabbitMQ, Azure Service Bus, Kafka) that your integration subscribes to — more efficient and more real-time than polling, and increasingly the preferred pattern for anything time-sensitive.

## 4. OPC-UA from the developer's side

You met OPC-UA conceptually in the Industrial Deep Dive (Section 2/5/6) as the modern, secure, self-describing industrial data standard. From a dev's side, connecting to it means using an **OPC-UA client library** in your language of choice (e.g., `python-opcua`/`asyncua` for Python, `OPCFoundation.NetStandard.Opc.Ua` for .NET) to:
1. **Connect and authenticate** to an OPC-UA server (a PLC, a SCADA system, or a gateway aggregating multiple PLCs) using the certificate/credential-based security OPC-UA has built in.
2. **Browse the address space** — because OPC-UA is self-describing, you can programmatically discover what tags/nodes are available rather than needing a hand-maintained list, though in practice you'll often still be given a specific list of node IDs to read.
3. **Read (and, rarely, subscribe to live-updating) values** by node ID, getting back a properly typed value (a float, an integer, a boolean) with a timestamp and a quality flag (OPC-UA values carry a "Good/Bad/Uncertain" quality indicator — always check it; a numerically valid-looking value with "Bad" quality means the sensor/source itself is reporting a problem, and code that ignores quality flags can silently work with garbage data).

## 5. Integration patterns and where they sit in the Purdue Model

Every integration you build should have an honest answer to "which Purdue levels does this cross, and does it correctly go through the DMZ pattern from Section 3 of the Industrial Deep Dive?"

- **Polling from IT into a DMZ replica** — your dashboard/report reads from a DMZ-hosted historian replica or MES reporting database, never directly from the live Level 3 system. This is the safe, standard pattern for most reporting/analytics work.
- **Event-driven via a message broker in the DMZ** — a message queue sitting in the DMZ, with OT publishing events one-way and IT-side integrations subscribing, mirrors the one-way historian replication pattern from Section 3.
- **The pattern to be suspicious of:** any integration where your IT-side code is given direct credentials to query a live Level 2/3 system in real time, with no DMZ/replica layer in between. It might be genuinely fine for a low-risk read — but it's exactly the kind of shortcut that grows into a real problem later, and it's worth asking (professionally, as a junior learning the ropes) why the DMZ pattern wasn't used, rather than assuming it's fine because it works today.

## 6. Hands-On Lab

**Lab 2.1 — Query a real historian, safely**
If you built Ignition in the Industrial Deep Dive (Section 4 lab), Ignition includes a built-in historian for whatever tags you were logging. Use Ignition's SQL Bridge / query capability (or its REST endpoints if you enabled them) to pull a time range of historical values for one of your simulated tags into a script — practice specifying a bounded time range and an interpolation interval, and observe the difference in row count/shape between raw and interpolated queries.

**Lab 2.2 — Connect to OPC-UA from code**
1. Using `python-opcua`/`asyncua` (or the .NET OPC-UA client library), write a small script that connects to your OpenPLC or Ignition OPC-UA simulator server from the Industrial Deep Dive.
2. Browse the address space and print the discovered nodes.
3. Read a specific tag's value, print its value, timestamp, and quality flag.
4. Deliberately handle the case where the quality flag isn't "Good" — print a warning instead of silently trusting the value.

**Lab 2.3 — Build a tiny "safe" integration**
Combine Sections 1-2: build a small REST API (from Lab 1.3's pattern) that, when called, reads the latest value of your OPC-UA tag from Lab 2.2 and returns it as JSON, including the quality flag in the response — a miniature but realistic version of "a dashboard backend polling live OT data through a controlled interface," done the honest, quality-aware way.

## 7. Autism For Evil — the real-world insider bit

The single most common real mistake juniors make in industrial data integration isn't a security mistake, it's a **volume mistake**: writing a query or a polling loop that seemed totally reasonable against a small test system, then pointing it at the real historian/MES with real production tag counts and real history depth, and discovering it takes 40 minutes to run, or worse, that running it repeatedly on a schedule quietly degrades performance for the operators actually depending on that system for real-time visibility. The professional habit: **always ask "what's the realistic data volume this will actually run against in production, not in my test," before you consider a query design finished** — and when in doubt, test against a copy/replica first, exactly like the DMZ replica pattern in this section exists to protect against exactly this class of mistake at the architecture level, not just the query level.

The other thing worth knowing: quality flags (OPC-UA's Good/Bad/Uncertain) and their historian equivalents (many historians tag stored values as Good/Bad/Substituted/etc.) are one of those details that separates code written by someone who's actually worked with real industrial data from code written by someone who's only ever worked with clean database rows. Real sensors fail, get disconnected for maintenance, or read garbage during a startup transient — and industrial systems are *built* to flag that explicitly, precisely so downstream code doesn't have to guess. Code that ignores the quality flag and just uses the raw number "because it's usually fine" will eventually produce a wrong report, a wrong dashboard, or a wrong analysis at exactly the moment it matters most (during an actual process upset, which is usually also when sensors are most likely to be reporting bad quality). Checking it isn't paranoia, it's using information the system is specifically handing you for free.

---

## Done when

- [ ] You can explain why "read from OT, don't write to OT" is the safe default for a junior dev, and what would justify an exception.
- [ ] You can explain the difference between a raw/recorded historian query and an interpolated one, and why the distinction matters for query size.
- [ ] You've completed Lab 2.2 and can point to real code that checks an OPC-UA quality flag before trusting a value.
- [ ] You can explain, for any integration you build, which Purdue levels it crosses and whether it correctly uses a DMZ/replica pattern.
- [ ] You've completed Lab 2.3 — a working API that returns live OT data with its quality flag included.

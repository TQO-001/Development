# Section 4 — SCADA/MES Scripting & Automation

## Why this section exists

Sections 2-3 covered getting data out and analyzing it from the outside. This section is about working **inside** the platforms that actually run the plant floor — most modern SCADA and MES platforms are themselves extensible with real scripting (usually Python or a vendor-specific scripting language), and a huge amount of practical "software dev in an industrial IT role" is writing scripts and automations *inside* these platforms, not building entirely separate systems around them.

---

## 1. Why platforms like this are scriptable at all

SCADA/MES vendors learned long ago that no out-of-the-box product can anticipate every plant's specific needs — so modern platforms expose a scripting layer for customization: custom logic on a button press, calculated/derived tags (values computed from other tags rather than read directly from a sensor), custom report generation, and integration glue connecting the platform to the outside world (tying directly back to Section 2). This is a deliberate design choice, not a workaround — vendors *want* you extending their platform this way rather than building brittle external hacks around it.

## 2. Ignition scripting (Python-based) — a concrete, learnable example

Since you've already got Ignition installed from the Industrial Deep Dive labs, it's a genuinely good concrete example, and its scripting is real Jython (Python running on the Java Virtual Machine) — your existing Python knowledge transfers directly, with a few platform-specific concepts layered on:

- **Event scripts** — code that runs in response to something happening: a button's `actionPerformed` script runs when an operator clicks it; a tag's `valueChanged` script runs whenever that tag's value updates; a **Gateway startup script** runs once when the Ignition server itself starts up. Understanding *when* a script runs (client-side, on a button click, vs. gateway-side, running continuously on the server) matters a lot — gateway-side scripts run regardless of whether any operator screen is even open, client-side scripts only run while a specific user's session is active.
- **Tag scripting / expression tags** — a tag whose value is computed from other tags via a script or expression, rather than read directly from a device — e.g., an "Overall Line Efficiency" tag computed from several underlying machine-status tags, refreshing automatically as those change. This is a very common, high-value pattern: turning raw sensor data into a business-meaningful calculated value, available anywhere in the platform just like a real tag.
- **Named queries** — Ignition's structured way of writing parameterized, reusable SQL queries that can be called from scripts or bound directly to UI components, instead of building raw SQL strings by hand scattered through your code (which is both a maintainability problem and, if done carelessly with string concatenation instead of parameters, a SQL injection risk).
- **Perspective / Vision scripting for custom UI logic** — beyond simple button actions, you can build genuinely custom logic for validating operator input before it's accepted, showing conditional UI elements based on system state, or driving a custom workflow a stock component wouldn't support.

## 3. The same pattern generalizes beyond Ignition

Whatever specific SCADA/MES platform you actually end up working with (Wonderware/AVEVA, WinCC, a custom in-house MES), the *shape* of the work is consistent enough to recognize:
- Most platforms have **some** scripting/extension layer (VBScript historically, increasingly Python or .NET-based today, or a vendor-specific expression language).
- Most support **calculated/derived values** in some form.
- Most support **custom reporting** (often via a report designer + scripting for anything the designer can't do natively — Crystal Reports and SSRS show up a lot in this space historically, alongside more modern web-based reporting).
- Most support **database integration** for reading configuration/reference data in, and writing results/logs out.

Learning one platform's scripting deeply (Ignition, in your case, since it's what you've already got installed) gives you transferable pattern-recognition for whatever platform a real employer actually uses.

## 4. A concrete example, end to end

Imagine you're asked: "operators want an alert if a batch's average temperature over its run is outside spec, shown right on the batch summary screen." The realistic build, combining everything above:
1. A **tag script or expression tag** computes the running average temperature for the current batch as it progresses.
2. When the batch completes, an **event script** compares that average against spec limits (pulled via a **named query** from a reference table of spec limits per product) and writes a pass/fail result to the database.
3. A **UI component** on the batch summary screen (bound to that result) shows a clear pass/fail indicator, styled per the ISA-101 high-performance HMI principles from the Industrial Deep Dive (color reserved for the abnormal case).
4. Optionally, a **scheduled script** rolls up a daily summary of pass/fail rates into the kind of report/dashboard covered in Section 3.

Every piece of this is something you're now equipped to actually build.

## 5. Hands-On Lab

**Lab 4.1 — Event scripting**
In your Ignition install, build a button on a Vision or Perspective screen whose `actionPerformed` script writes a value to a memory tag and shows a popup confirmation — practice the basic event-script pattern before building anything more complex.

**Lab 4.2 — A calculated/expression tag**
Create two simple memory tags representing two machine statuses (e.g., booleans for "Line A running" and "Line B running"), then create a third **expression tag** that computes "Overall Running" as true only if both are true — confirm it updates live as you toggle the underlying tags.

**Lab 4.3 — Named query + database write**
1. Set up a simple database connection in Ignition to a local PostgreSQL/SQLite database with one table (e.g., `batch_results` with columns for batch ID, average temperature, and pass/fail).
2. Write a Named Query that inserts a row into it.
3. Call that named query from a script (e.g., triggered by a button) with hardcoded test values, and confirm the row actually lands in the database.

**Lab 4.4 — Build the end-to-end example**
Using Labs 4.1-4.3 as building blocks, build a simplified version of the "batch temperature spec check" example from Section 4.4: a memory tag simulating a batch's average temperature, a button simulating "batch complete" that checks it against a hardcoded spec limit, writes a pass/fail result to your database table via a named query, and updates a UI indicator (colored per ISA-101 principles — grey/neutral by default, a clear alert color only on fail) showing the result.

## 6. Autism For Evil — the real-world insider bit

The thing that trips up devs coming from a pure software background into platform scripting like this: **the scripting layer is genuinely powerful, and that power is exactly what makes it easy to build something that works great on your test screen and then causes real problems once it's actually running continuously against live production data.** A gateway-side `valueChanged` script that does something even moderately expensive (a slow database query, a loop that isn't tightly bounded) can fire *constantly* if it's attached to a fast-changing tag, and unlike a typical web app request that ends when the page unloads, a gateway script runs as long as the server does — a genuinely inefficient script here is a slow, silent drain rather than an obvious crash, and it can be genuinely hard to trace back to "oh, it's that one script" without knowing to look. The practical habit: be deliberate about which tags/events you attach scripts to, keep event scripts fast and simple, and push anything slow or heavy (like a real database write, or a calculation over a lot of historical data) to a scheduled/background script rather than something firing on every single value change.

The other real-world thing: platform scripting knowledge (Ignition specifically, but the pattern generally) is **genuinely underrated as a career skill** relative to how in-demand it actually is — a lot of "real" software engineers look down on platform scripting as not being "real programming," while plants desperately need people who can both write good code *and* understand the specific platform their production systems actually run on. Being the person who can competently do both, rather than purely general software dev *or* purely SCADA configuration with no real coding ability, is a genuinely narrower, more valuable niche than either half alone — and it's exactly the niche this whole track is quietly building you toward.

---

## Done when

- [ ] You can explain the difference between a client-side event script and a gateway-side script, and why that distinction matters for what's safe to put in each.
- [ ] You can explain what an expression/calculated tag is and give a real example of when you'd use one instead of reading a raw sensor value directly.
- [ ] You can explain why Named Queries (parameterized) are safer than building raw SQL strings by hand.
- [ ] You've completed Lab 4.4 — a working end-to-end example combining a calculated value, a database write, and a status indicator styled per ISA-101 principles.
- [ ] You can explain, in your own words, why an inefficient gateway-side script is a different (and sneakier) kind of problem than a slow web request.

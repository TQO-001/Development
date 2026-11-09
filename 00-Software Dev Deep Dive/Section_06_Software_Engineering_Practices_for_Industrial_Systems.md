# Section 6 — Software Engineering Practices for Industrial Systems

## Why this section exists

This section closes the loop, deliberately last. Sections 1-5 gave you skills; this section is about the *discipline* that turns those skills into work a real organization can trust with something that matters — documentation, change control, and the specific challenge of working with legacy and safety-adjacent code, which you will encounter constantly in this field whether or not you ever touch a PLC directly.

---

## 1. Documentation — not an afterthought, a deliverable

In a typical personal project, documentation is optional polish. In an industrial context, it's frequently a genuine requirement, not a nicety — for three real reasons:
- **Continuity.** Plants run for decades; the person who wrote a piece of integration code may well have left the company by the time it needs modifying. Undocumented code in this context isn't just inconvenient, it can become genuinely unmaintainable — nobody left who remembers *why* a specific decision was made.
- **Audits and compliance.** Many industrial sectors have real regulatory/quality requirements (traceability requirements tie directly back to MES genealogy from the Industrial Deep Dive) that extend to the software supporting them — being able to show *what* a system does and *why* it was built that way is sometimes a literal compliance requirement, not just good practice.
- **Handoff between IT and OT.** Given the whole IT/OT split theme running through this entire two-track curriculum, documentation is often the actual bridge between two teams with different backgrounds and vocabularies — a well-written README or design doc lets an automation engineer understand what your integration does without needing to read your C#/Python line by line.

**What "good enough" documentation actually looks like, practically:** a README for any real project that answers — what does this do, how do I run/deploy it, what are its dependencies (including which OT systems it talks to and how), and what would someone need to know before changing it. Inline comments explaining *why* a non-obvious decision was made (not restating *what* the code obviously does) are worth far more than comments on every line.

## 2. Change control for code, not just for OT changes

Section 5 covered MOC for changes affecting production systems generally — this is the code-specific layer underneath that: every change should be traceable to *why* it happened. Practically:
- **Link commits/PRs to a ticket/issue** describing the actual business or technical reason for the change, not just the technical diff — so six months later, "why did we do this" has an answer beyond "the code changed on this date."
- **Changelogs** — a running, human-readable log of what changed between versions, distinct from raw git history, aimed at someone who needs to know "what's different since the last release" without reading every commit.
- **Semantic versioning basics** (`MAJOR.MINOR.PATCH`) — a widely-used convention where a MAJOR bump signals a breaking change, MINOR signals new backward-compatible functionality, and PATCH signals a bug fix — worth knowing even informally, because it communicates risk at a glance to anyone deciding whether to update to a new version.

## 3. Working with legacy code and systems — a near-certainty in this field

Given industrial equipment/systems commonly run for 15-25+ years (Industrial Deep Dive Section 2), you will very likely encounter genuinely old code, old database schemas, or old integration points with little to no documentation, written by someone long gone, in a style/language that may not match current practice. This is not a rare edge case in this field — it's close to the default state, and it's a genuinely different skill from greenfield development:

- **Understand before you change.** Resist the urge to "clean up" or rewrite something you don't yet fully understand — legacy code that looks messy often has non-obvious reasons for its specific quirks (a workaround for a bug in some other system, a fix for an edge case that isn't obvious from the code alone), and a confident rewrite that doesn't account for those reasons is a classic way to reintroduce a bug that was already solved once.
- **Add tests before refactoring, not after.** If you're going to change legacy code with no existing tests, writing tests that capture its *current* behavior first (even if that behavior seems weird) gives you a safety net to confirm your change didn't break something you didn't realize you were relying on.
- **Small, reversible changes over big rewrites**, especially early in your time at any organization — a small, well-tested, easily-reviewed change builds trust; a large rewrite that goes wrong in a system nobody fully understood yet is a genuinely damaging way to start.

## 4. Safety-adjacent code — a different bar, even for non-safety-critical work

You will very likely not be writing actual safety-instrumented-system code as a junior/intern (that's a specialized, credentialed discipline with its own standards, e.g., IEC 61508/61511) — but you may well be writing code that's *adjacent* to safety-relevant systems (a dashboard an operator partly relies on, a report feeding a safety-related decision, an integration touching data that includes alarm/safety event history). The practical takeaway: **when you're not sure whether something you're building is safety-adjacent, ask, rather than assuming it's "just a dashboard."** The cost of asking a question that turns out to be unnecessary is small; the cost of treating something safety-adjacent as low-stakes because nobody told you otherwise can be genuinely serious.

## 5. Hands-On Lab

**Lab 6.1 — Write a real README**
Pick your most complete project from this whole track (the Lab 4.4 end-to-end Ignition example is a good candidate) and write a proper README: what it does, how to set it up/run it, what it depends on (including which simulated OT systems it talks to), and a short "before you change this" section noting anything non-obvious a future maintainer would need to know.

**Lab 6.2 — Reverse-engineer "legacy" code**
Find (or deliberately write, then set aside for a day and come back to) a script or small program with zero comments and unclear variable names. Practice reading it cold: write down what you *think* it does, then verify by running it or tracing through it carefully, and note anywhere your first guess was wrong. This is deliberately practicing the "understand before you change" muscle in a low-stakes setting.

**Lab 6.3 — Add tests to un-tested code before changing it**
Take the Lab 6.2 code (or any small existing project you haven't written tests for yet), write tests that capture its current behavior first, confirm they pass against the existing code, *then* make a change, and confirm your tests still pass (or correctly show you what your change affected).

**Lab 6.4 — Write a changelog**
For your Lab 4.4 project (or any project with a few real commits), write a short CHANGELOG.md summarizing 3-4 real changes you made across this whole track, in human-readable form, as if a colleague needed to know what changed without reading your git history.

## 6. Autism For Evil — the real-world insider bit

The honest thing about documentation and change discipline: **almost everyone agrees it's important, and almost every real codebase has less of it than it should, because it's the thing that's easiest to skip when a deadline is close.** The people who genuinely stand out aren't the ones who lecture others about documentation — they're the ones who quietly keep doing it consistently even under time pressure, and whose code other people therefore *want* to work on, because it doesn't cost extra effort to understand. In a field with as much inherited legacy complexity as industrial IT, being known as "the person whose stuff is actually documented" is a genuinely rare and valued reputation to build early, and it compounds — people hand you more responsibility, not less, when they trust that what you build won't become an undocumented mystery for the next person.

On legacy code specifically: the instinct to "just rewrite this mess" is one of the most common and most costly mistakes junior developers make across *any* industry, but it's especially costly here, because a legacy integration touching a real production system that gets confidently rewritten and turns out to have a subtle behavioral difference from the original can cause a real production problem — not a "we'll patch it tomorrow" bug, but potentially a "this affected today's batch" problem. The senior instinct, the one worth building now while stakes are low: **curiosity about why something weird exists, before judgment that it's wrong.** Nine times out of ten, the weird thing has a reason. Finding that reason first is what makes you trustworthy with the tenth case, where the weird thing really was just a bug.

---

## Done when

- [ ] You can explain the three real reasons documentation matters more in this field, not just "it's good practice."
- [ ] You've written a genuinely complete README for a real project (Lab 6.1).
- [ ] You can explain "understand before you change" and "small reversible changes over big rewrites," with a real consequence for ignoring each.
- [ ] You've completed Lab 6.3 — writing tests for existing untested code before modifying it.
- [ ] You can explain why you'd ask whether something is safety-adjacent rather than assuming it isn't, even for "just a dashboard."

---

## Track complete

You've now built both halves of the internship's likely paths: `03-Industrial Deep Dive` (the networking/OT infrastructure side) and this track (the software dev side, general foundation plus the industrial-specific layer). Whichever way the rotation actually goes, or if it genuinely stays open until you choose, you're not walking in cold on either one.

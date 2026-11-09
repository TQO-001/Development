# 04-Software Dev Deep Dive: Index & Progress Tracker

Standalone track, parallel to `03-Industrial Deep Dive`. This one's for the internship's other rotation option — the Software Dev path — built as a general foundation layer first, then an industrial-specific layer on top, so you're prepared whichever way the rotation actually goes.

Assumes you're already coming in with your existing stack (C#/.NET, Python, TypeScript, PostgreSQL/SQL Server) from your qualification — this track doesn't re-teach syntax, it teaches **how that stack gets used specifically inside an industrial/manufacturing IT environment**, which is a genuinely different flavor of software dev from a typical web/business-app job.

| # | File | Topic | Layer | Status |
|---|---|---|---|---|
| 1 | `Section_01_Software_Dev_Foundations_for_Industrial_IT.md` | Foundations — version control, testing, APIs, DB design, done properly for enterprise/industrial work | General | ✅ Built |
| 2 | `Section_02_Industrial_Data_Integration.md` | System Integration — talking to OPC-UA, historians, MES/ERP over real interfaces | Industrial | ✅ Built |
| 3 | `Section_03_Industrial_Data_Analytics.md` | Data Analytics — time-series data, dashboards, Python for process data | Industrial | ✅ Built |
| 4 | `Section_04_SCADA_MES_Scripting_and_Automation.md` | Scripting & Automation inside SCADA/MES platforms | Industrial | ✅ Built |
| 5 | `Section_05_DevOps_and_Digital_Transformation_in_OT.md` | DevOps, CI/CD, and change management, adapted for OT constraints | Industrial | ✅ Built |
| 6 | `Section_06_Software_Engineering_Practices_for_Industrial_Systems.md` | Engineering discipline — documentation, change control, working with legacy/safety-critical code | General + Industrial | ✅ Built |
| — | `Glossary_Quick_Reference.md` | Cross-section glossary / print-reference table | — | ✅ Built |

**How to work through each file:** same as `03-Industrial Deep Dive` — read the notes in full, do the lab, then the exercises in order (Warm-Up → Core → Applied → Challenge → 💀 BOSS), tick boxes here as you go.

---

### 🏁 Master Progress Tracker

**Section 1 — Software Dev Foundations for Industrial IT**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

**Section 2 — Industrial Data Integration**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

**Section 3 — Industrial Data Analytics**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

**Section 4 — SCADA/MES Scripting and Automation**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

**Section 5 — DevOps and Digital Transformation in OT**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

**Section 6 — Software Engineering Practices for Industrial Systems**
- [ ] Read notes · [ ] Lab · [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied · [ ] Challenge · [ ] 💀 BOSS

---

### Why this order

Section 1 makes sure your existing general skills are actually enterprise-shaped (not just "I can write a script" but "I can write a script the way a team would accept it"). Sections 2-4 are the industrial-specific core, in the order data actually flows in a real plant: first *get* the data (Integration), then *understand* it (Analytics), then *act on it inside the platforms that run the plant* (SCADA/MES scripting). Section 5 zooms out to how change gets managed safely once you're touching systems that run production. Section 6 closes the loop with the engineering discipline that separates "a working script" from "code a team can actually trust in a regulated, safety-relevant environment" — deliberately last, because it means more once you've felt the weight of Sections 2-5.

This track and `03-Industrial Deep Dive` share concepts on purpose (Purdue Model, OPC-UA, MES, historians) — if a term feels unfamiliar here, it's very likely fully explained over there; this track builds on it rather than re-explaining it from scratch.

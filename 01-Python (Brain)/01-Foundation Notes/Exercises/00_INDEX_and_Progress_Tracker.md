## 120-Day Curriculum: Deep-Dive Practice Set (Sections 9–13)

Five exercise files, one per section. Each has 7 exercises: Warm-Up → Core (×2) → Applied (×2) → Challenge → 💀 BOSS. No solutions are provided on purpose — specs, hints, and "Done when" checks only.

| File | Topic | Exercises | Est. Time |
|---|---|---|---|
| `Section_09_Decorators_Exercises.md` | Decorators | 7 | ~1.5–2 hrs |
| `Section_10_Generators_Iterators_Exercises.md` | Generators & Iterators | 7 | ~1.5–2 hrs |
| `Section_11_Context_Managers_Exercises.md` | Context Managers | 7 | ~2 hrs |
| `Section_12_Modules_Packages_Exercises.md` | Modules & Packages | 7 | ~2 hrs |
| `Section_13_Advanced_Performance_Exercises.md` | GIL / asyncio / Performance / DB Safety | 7 | ~2 hrs |

**Suggested order:** as listed above — it follows your notes' sequence and each BOSS challenge reuses skills from earlier sections (the Section 13 BOSS uses asyncio + generators + context managers together).

**How to work through each file:**
1. Make a scratch folder per section (e.g. `9_decorators_practice/`).
2. Build one exercise at a time, in order — don't skip to BOSS first.
3. Check the "Done when" line before moving on — that's your pass/fail signal, not "it ran without errors."
4. Tick the checkbox in the file's own progress tracker AND in the master tracker below.

---

### 🏁 Master Progress Tracker

**Section 9 — Decorators**
- [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied 1 · [ ] Applied 2 · [ ] Challenge · [ ] 💀 BOSS

**Section 10 — Generators & Iterators**
- [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied 1 · [ ] Applied 2 · [ ] Challenge · [ ] 💀 BOSS

**Section 11 — Context Managers**
- [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied 1 · [ ] Applied 2 · [ ] Challenge · [ ] 💀 BOSS

**Section 12 — Modules & Packages**
- [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied 1 · [ ] Applied 2 · [ ] Challenge · [ ] 💀 BOSS

**Section 13 — GIL / asyncio / Performance / DB Safety**
- [ ] Warm-Up · [ ] Core 1 · [ ] Core 2 · [ ] Applied 1 · [ ] Applied 2 · [ ] Challenge · [ ] 💀 BOSS

---

### Notes on Scope

All exercises run on the standard library only — no `pip install` needed, even for the asyncio/DB exercises in Section 13 (network and database calls are mocked with `asyncio.sleep` and a fake `execute()` function so the concurrency/safety lessons are still real and measurable, without the setup overhead).

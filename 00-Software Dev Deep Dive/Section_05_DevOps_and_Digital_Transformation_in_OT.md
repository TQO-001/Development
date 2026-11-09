# Section 5 — DevOps & Digital Transformation in OT

## Why this section exists

Standard DevOps practice (CI/CD, automated deployment, "ship fast, fail fast, roll forward") comes almost entirely out of a pure-IT/web-software world where a bad deploy means a rollback and an apology. This section is about how those same underlying ideas — automation, repeatability, controlled change — get *adapted*, not abandoned, when the systems you're touching are connected to a real production process. This is the "digital transformation" piece from the motivation letter, and it's genuinely one of the more interesting tensions in industrial software work.

---

## 1. Why standard CI/CD doesn't just transplant into OT

Standard CI/CD assumes: deployments are cheap and frequent, rollback is fast and safe, and a failed deploy mostly costs time/embarrassment. In an OT-adjacent context, none of those assumptions fully hold:
- **Deployments often require a maintenance window**, not "whenever the pipeline finishes" — you can't push a change to a system feeding a live production line at 2pm on a Tuesday just because your tests passed, if that system genuinely can't tolerate the brief interruption a restart causes.
- **Rollback isn't always simple.** A software rollback might be a one-command revert; a change that also touched a device configuration, a recipe, or a database schema might not have a clean automatic undo.
- **The blast radius of a mistake is different.** A bug in a typical web app might show a wrong number to a user. A bug in code that's part of the plant's operational chain (even just the reporting/analytics layer from Sections 2-3) can mean wrong decisions get made on the plant floor, or an operator loses trust in a tool they need to actually use.

None of this means "don't automate" — it means the automation has to be built with these constraints as first-class requirements, not as an afterthought bolted onto a standard web-dev pipeline.

## 2. What DOES transfer well, adapted

- **Automated testing** — arguably transfers *unchanged*, and matters more here, not less (this is Section 1's testing discipline, applied). Automated tests catching a bug before deployment is strictly more valuable when a deployment mistake is more expensive.
- **Infrastructure as Code (IaC)** — defining server/environment configuration in version-controlled files (e.g., using tools like Ansible, Terraform, or even well-organized PowerShell/scripts) rather than manual click-through setup — genuinely valuable in OT-adjacent server infrastructure (Section 1 of the Industrial Deep Dive) too, because it makes environments reproducible and auditable, which matters a lot when a regulator or an auditor asks "how do you know this system is configured the way you say it is?"
- **Staged environments (Dev → Test/UAT → Production)** — completely standard DevOps practice, and *more* rigorously enforced in industrial contexts: changes get built and tested in a dev environment, validated in a test environment that mirrors production as closely as possible, and only then promoted to production — usually with a formal sign-off step, not an automatic promotion, before that last stage.
- **Monitoring and alerting on deployed systems** — knowing something broke *immediately*, rather than finding out from an angry phone call, is just as valuable here as anywhere else — arguably more so, since the person finding out first-hand might be an operator relying on your dashboard mid-shift.

**What typically doesn't transfer as-is:** fully automatic, no-human-approval deployment straight to a production-adjacent OT system. Even a mature, DevOps-fluent industrial IT team almost always keeps an explicit human approval gate before that last promotion step, precisely because of the blast-radius asymmetry above.

## 3. Change management — the formal side of "don't break production"

Real plants run a **Management of Change (MOC)** process — a formal, documented procedure for reviewing, approving, and tracking any change to a system that could affect safety, quality, or production, often required by regulatory/quality standards specific to the industry. For software-adjacent changes, this typically means: a documented description of the change and its purpose, a risk assessment (what could go wrong, and how bad would it be), a defined test/validation plan, a specific approval from someone with authority over that system, and a scheduled implementation window — often tracked in a ticketing system rather than just "I merged the PR."

**Why this matters for you specifically:** the instinct from a pure-software background is often "why can't we just deploy it, it's tested, it works" — and the honest answer is that MOC exists because "it worked in my testing" and "it's safe to deploy to a system that's part of a real, running, safety-relevant process" are genuinely different bars, and the second one deserves a documented decision by someone accountable for that system, not just a green CI checkmark.

## 4. IIoT and cloud — the newer, genuinely exciting layer

"Digital transformation" in a modern industrial context increasingly means connecting plant-floor data to cloud platforms for wider analytics, cross-site comparison, or predictive maintenance — this is where MQTT/Sparkplug B (Industrial Deep Dive Section 5) and cloud IIoT platforms (Azure IoT Hub, AWS IoT Core) come in:
- The **pattern**: OT-side data (via OPC-UA locally, Section 2 of this track) gets bridged out over MQTT to a cloud IIoT platform, which then feeds cloud-based analytics/ML/dashboards — deliberately one-way where possible, mirroring the DMZ one-way-replication pattern from the Industrial Deep Dive, just extended out to the cloud instead of just the corporate network.
- **Predictive maintenance** is the flagship "digital transformation" use case worth knowing by name: using historical sensor data (vibration, temperature, current draw) and machine learning to predict a failure *before* it happens, instead of either reactive maintenance (fix it when it breaks) or purely scheduled maintenance (replace it on a fixed calendar regardless of actual condition) — genuinely valuable when done well, and a common first "digital transformation" pilot project at plants starting this journey.

## 5. Hands-On Lab

**Lab 5.1 — Build a real CI pipeline with a staged gate**
1. Take your project from Section 1 (or the API from Lab 1.3/2.3) and set up a CI pipeline using GitHub Actions (free for public repos) that automatically runs your tests on every push.
2. Configure it so that merging to `main` requires the tests to pass (a "required status check") — practice the mechanism, not just the concept.
3. Add a second, manually-triggered stage representing "deploy to production" that only runs on manual approval (GitHub Actions supports "environments" with required reviewers) — deliberately practicing the human-approval-gate pattern from Section 5.3, not full auto-deploy.

**Lab 5.2 — Write a real MOC document**
Pick any change from your labs so far (e.g., the batch spec-check logic from Section 4's Lab 4.4) and write a short, real MOC-style document for it: what the change is, why it's needed, what could go wrong, how you'd test it, and who (in a real org) would need to approve it before it went live. This is a genuinely realistic artifact you might actually be asked to produce early in a real role.

**Lab 5.3 — IaC basics**
Write a simple Ansible playbook or PowerShell DSC script (pick whichever fits your stack better) that installs and configures one piece of software (even something simple, like ensuring a specific Python package is installed and a config file has specific contents) — practice the "environment defined in code, not manual steps" pattern at a small scale.

## 6. Autism For Evil — the real-world insider bit

Here's the honest tension nobody resolves cleanly, and you should walk in expecting it rather than being surprised by it: **IT-side people pushing modern DevOps practice into a plant often genuinely underestimate how much MOC-style rigor exists for good, hard-earned reasons** — plants have real incident histories, sometimes serious ones, that shaped why the rigor exists. At the same time, **OT-side resistance to any change to "how we've always deployed things" sometimes really is just inertia, not a genuine risk concern** — and telling the two apart, case by case, rather than assuming either side is automatically right, is a skill that takes real judgment and is exactly the kind of judgment a good manager notices in a junior. The move that works: ask *specifically* what risk the existing process is protecting against, for *this* particular change, rather than either blindly following "that's how we've always done it" or blindly pushing "but CI/CD best practice says..." — the specific answer usually reveals whether the rigor is earned for this case or just habit.

On predictive maintenance specifically: it's a genuinely hyped term right now, and a lot of "digital transformation" pitches oversell what's realistically achievable with the data actually available — a predictive maintenance model is only as good as the sensor data and failure-history data feeding it, and a lot of real plants don't yet have either at the quality/quantity a genuinely predictive model needs. Knowing this going in means you can be a realistic, credible voice in a project like this rather than either an uncritical hype-follower or an unhelpful skeptic — both of which are common failure modes for people newer to this specific corner of the field.

---

## Done when

- [ ] You can explain, specifically, why fully automatic production deployment doesn't fit most OT-adjacent contexts, in terms of blast radius and rollback complexity — not just "it's risky."
- [ ] You can explain what an MOC process is and why "it passed CI" isn't the same bar as "approved to deploy" in this context.
- [ ] You've completed Lab 5.1 with a working test-gated CI pipeline and a manual-approval deployment stage.
- [ ] You've written a real MOC-style document (Lab 5.2) for a real change you actually made.
- [ ] You can explain what predictive maintenance is, and one honest limitation of it (data quality/quantity dependency), not just the sales pitch.

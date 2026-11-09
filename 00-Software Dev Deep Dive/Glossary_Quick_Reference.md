# Software Dev Deep Dive — Glossary & Quick Reference

Companion to `03-Industrial Deep Dive`'s glossary — terms already defined there (Purdue Model, MES, Historian, OPC-UA, etc.) aren't repeated here unless used in a new way.

| Term | What | Why it matters | Section |
|---|---|---|---|
| Feature branch | A Git branch for one piece of work, merged via PR | Keeps `main` always stable/deployable | 1 |
| Unit test | Tests one small piece of logic in isolation | Fast, cheap, catches most bugs early | 1 |
| Integration test | Tests multiple pieces working together | Slower, fewer, confirms the whole system actually connects | 1 |
| REST | Convention for designing HTTP APIs (nouns as resources, verbs as HTTP methods) | Predictable, consumable by other systems/devs | 1 |
| Normalization | Avoiding duplicate storage of the same fact in a database | One place to update a fact, avoids inconsistency | 1 |
| Transaction | Groups multiple DB operations to all-succeed or all-rollback together | Prevents inconsistent partial writes | 1 |
| Quality flag | Good/Bad/Uncertain indicator attached to an OPC-UA or historian value | Flags sensor/source problems; ignoring it risks using garbage data | 2 |
| Interpolated query | Historian query returning values at fixed intervals, not just recorded changes | Prevents accidentally requesting huge raw datasets | 2 |
| Message queue | Broker-based async communication (RabbitMQ, Kafka, Azure Service Bus) | Event-driven integration alternative to polling | 2 |
| DMZ replica pattern | Reading from a DMZ-hosted copy, never the live OT system directly | The safe default for IT-side integration reads | 2 |
| Resampling | Changing a time-series' interval (e.g., to hourly averages) | Makes wide time ranges viewable/performant | 3 |
| Rolling average | Smoothing noise while keeping the original interval | Reveals underlying trend in a noisy signal | 3 |
| Anomaly detection | Flagging values outside expected range/pattern | Ranges from simple thresholds to full ML models | 3 |
| Grafana | Open-source dashboarding tool, strong time-series/alerting support | Common for operational, near-real-time plant dashboards | 3 |
| Power BI | Microsoft BI tool, strong business-side reporting | Common for executive/business-facing reporting | 3 |
| Predictive maintenance | Using sensor + failure history data to predict failures before they happen | Flagship "digital transformation" use case; data-quality dependent | 3, 5 |
| Event script | Code that runs in response to an action (button click, tag change) | Client-side or gateway-side — where it runs changes what's safe to put in it | 4 |
| Expression / calculated tag | A tag whose value is computed from other tags, not read directly from a device | Turns raw data into business-meaningful values | 4 |
| Named Query | Parameterized, reusable SQL query pattern (e.g., in Ignition) | Avoids SQL injection risk from raw string concatenation | 4 |
| CI/CD | Continuous Integration / Continuous Deployment | Standard DevOps automation; needs adaptation for OT blast-radius/rollback constraints | 5 |
| Infrastructure as Code (IaC) | Environment/server config defined in version-controlled files | Reproducible, auditable environments (Ansible, Terraform) | 5 |
| Management of Change (MOC) | Formal documented process for approving changes to systems affecting safety/quality/production | The real-world gate beyond "the tests passed" | 5 |
| Semantic versioning | MAJOR.MINOR.PATCH version convention | Communicates risk of updating at a glance | 6 |
| Safety-adjacent | Code/systems near, but not themselves, formal safety-instrumented systems | Ask, don't assume, when unsure if something qualifies | 6 |

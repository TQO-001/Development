# Section 3 — Industrial Data Analytics

## Why this section exists

Once Section 2's integration work gets you data out of historians/MES reliably, the next question is "so what do we actually do with it?" — this section covers turning raw process data into something a plant manager, an engineer, or an operator can actually use to make a decision. This is the "data analytics" and "digital transformation" pieces from the motivation letter, made concrete, and it's a genuinely high-growth area in industrial IT right now.

---

## 1. Time-series data is a different shape than typical business data

Business data (orders, customers, invoices) is usually **event-based** — a row per transaction, relatively low volume, read patterns are mostly "find specific records." Process/historian data is **time-series** — a value per tag per timestamp, extremely high volume (thousands of tags, sub-second to few-second intervals, running continuously for years), and read patterns are mostly "show me this tag (or set of tags) over this time range," often followed by aggregation (average, min, max) or resampling to a coarser interval for display. This shape difference is *why* historians are specialized databases rather than generic SQL tables (Section 2 already touched this) — and it's why the analytics tools/techniques that fit are somewhat different from typical business intelligence.

**Key concepts specific to time-series analysis:**
- **Resampling / downsampling.** A dashboard showing a year of data at 1-second resolution is both useless (you can't see anything at that zoom level) and slow to load — you resample to a coarser interval (e.g., hourly averages) appropriate to the time range being viewed.
- **Rolling/moving averages.** Smooth out noise in a signal to see the underlying trend — e.g., a 10-minute rolling average of a noisy temperature sensor makes a real trend visible that raw second-by-second data would hide in noise.
- **Anomaly detection basics.** Flagging values outside an expected range or statistical pattern — ranges from simple (a fixed high/low threshold, which is really just an alarm limit from the OT side) to statistical (values more than N standard deviations from a rolling mean) to full machine-learning approaches for more subtle pattern-based anomalies. Start with the simple end — a threshold-based flag is often 80% of the value for a fraction of the complexity of a full ML model, and it's far easier for an operator to trust and understand.
- **Correlation across tags.** Real analytical value often comes from looking at *multiple* tags together, not one in isolation — e.g., does a drop in output quality correlate with a particular temperature range, or with a particular shift, or with time since the last maintenance event? This is where genuine "digital transformation" value tends to live — connecting dots humans staring at one trend chart at a time would miss.

## 2. The Python data-analytics toolchain, applied to process data

Your existing Python skills map directly here:
- **pandas** — the core tool for loading, cleaning, and reshaping time-series data; a historian query result becomes a pandas DataFrame with a datetime index, and resampling/rolling-average operations become one-liners (`df.resample('1H').mean()`, `df.rolling('10min').mean()`).
- **matplotlib / plotly** — plotting trends; plotly specifically is worth knowing because it produces interactive charts (zoom, hover for exact values) that translate well into web dashboards, not just static images.
- **scikit-learn** — for anything beyond simple threshold-based anomaly detection (e.g., isolation forests for anomaly detection, simple regression models for predicting a quality outcome from process parameters) — you don't need to be a machine learning expert for this role, but recognizing when a problem is a good fit for a simple model, versus when a simple statistical rule is genuinely sufficient, is a valuable judgment call.

## 3. Dashboards and reporting — where analytics actually reaches people

Analysis that lives only in a Jupyter notebook on your laptop doesn't create business value — it needs to reach the people making decisions, which usually means one of:
- **BI tools** — Power BI and Grafana are the two most common in industrial contexts. **Power BI** fits well when the audience is business-side (plant managers, executives) and the data is already flowing into a business-friendly database. **Grafana** is extremely common specifically for *operational/real-time* dashboards sitting closer to OT (it has native time-series database connectors and is built around exactly the "trend over time" visualization pattern process data needs) — you'll see it a lot sitting at Level 3, giving a more modern/flexible alternative or complement to a SCADA system's built-in trending.
- **Custom web dashboards** — for something a BI tool can't do out of the box, a custom dashboard (e.g., a React frontend calling the kind of API you built in Section 2) gives full control — more dev effort, but no limits on what it can show or how it's interacted with.
- **Scheduled reports** — not everything needs a live dashboard; a lot of real value comes from a scheduled script (Python, run via a scheduled task/cron/Azure Function) that generates and emails a daily/weekly summary report — simple, reliable, and exactly what a lot of plant management actually wants (they don't need to stare at a live dashboard, they need Monday morning's summary in their inbox).

## 4. Hands-On Lab

**Lab 3.1 — Real time-series analysis with pandas**
1. Using your historian export from Section 2's Lab 2.1 (or generate synthetic data if needed — a Python script producing a fake noisy sensor reading every second for a simulated week works fine), load it into a pandas DataFrame with a proper datetime index.
2. Compute and plot: a raw trend, a resampled hourly-average trend, and a 10-minute rolling average — on the same chart, so you can see visually how each transformation changes what's visible.
3. Add a simple threshold-based anomaly flag (e.g., mark any point more than 2 standard deviations from a rolling mean) and plot those points highlighted on the chart.

**Lab 3.2 — Build a Grafana dashboard**
1. Install Grafana (free, runs locally in Docker or as a standalone install) and connect it to a database containing your time-series data (a simple PostgreSQL/TimescaleDB table works fine for this lab — load your Lab 3.1 data into it).
2. Build a dashboard panel showing the trend, with a time-range selector, matching the kind of operational dashboard you'd see in a real plant.
3. Add a threshold-based alert in Grafana itself (Grafana has built-in alerting) that would fire if the value crossed a limit — connecting this back to the alarm/alarm-rationalization concepts from the Industrial Deep Dive's Section 5.

**Lab 3.3 — Correlate two tags**
Using two related synthetic/real tags (e.g., a temperature and a downstream quality metric you simulate as loosely dependent on it), compute their correlation in pandas (`df.corr()`), plot them against each other, and write 2-3 sentences on what a real correlation like this would mean for a plant engineer trying to improve quality.

## 5. Autism For Evil — the real-world insider bit

The uncomfortable truth about industrial data analytics work: **the hard part is almost never the analysis technique — it's the data quality.** Real historian data is full of gaps (a sensor was offline), bad quality flags (Section 2's quality-flag concept matters enormously here — analyzing data without filtering out "Bad" quality readings first will quietly corrupt every downstream conclusion), unit inconsistencies (someone changed a sensor's calibration/units at some point and didn't document it clearly), and timezone/DST issues (a plant running across a DST change, or logging in local time instead of UTC, has genuinely caused real analytical errors — an hour of "duplicate" or "missing" timestamps twice a year is a classic gotcha). A junior who jumps straight to building a fancy model on data they haven't actually inspected for these problems will produce confidently wrong results — and confidently wrong is worse than obviously broken, because people act on it. The actual skill that gets valued here is unglamorous: **look at the raw data first, understand its quirks, before doing anything clever with it.**

The other insider thing: dashboards and reports that nobody asked for, showing data nobody's sure how to act on, are an extremely common and avoidable failure mode of "digital transformation" initiatives specifically. The projects that actually land well start from a real question someone with decision-making power actually has ("why does Line 2's scrap rate spike on nightshift?") and work backward to the data and visualization that answers it — not from "we have all this data, let's build a dashboard" and hope it's useful. If you ever get to propose an analytics project yourself, starting with the question, not the data, is the difference between something that gets used and something that gets built once, looked at twice, and forgotten.

---

## Done when

- [ ] You can explain the difference between resampling and a rolling average, and when you'd use each.
- [ ] You can explain why filtering by quality flag matters before doing any analysis on historian data.
- [ ] You've completed Lab 3.1 with a working anomaly flag on real or synthetic time-series data.
- [ ] You've built a working Grafana dashboard with at least one alert (Lab 3.2).
- [ ] You can explain, in your own words, why "start from the question, not the data" matters for a real analytics project.

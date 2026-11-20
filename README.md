# Linac QA Analytics & Reporting Hub

A Python/SQL tool that turns daily linac QA measurements into trend analysis, early drift warnings, and auto-generated monthly QA reports.

> **Research/portfolio tool. Not for clinical use.** Built on simulated data; tolerance levels are illustrative and must be replaced with AAPM TG-142 values and your clinic's policy before any real use.

## Why this exists
Medical physics assistants spend a lot of time collecting QA results, checking them against tolerances, and writing summaries. This project automates the repetitive part so the physicist can review instead of assemble. It sits on top of exported QA data (for example from QATrack+ style exports) rather than replacing those systems.

## Status
- [x] Week 1: simulator with injected drift/step/spike events, tests, demo plot
- [ ] Week 2: SQL schema and loader
- [ ] Week 3: tolerance engine
- [ ] Week 4: drift detection (EWMA / CUSUM)
- [ ] Week 5: AI-model monitoring module (simulated Dice-score drift)
- [ ] Week 6: validation across many seeds
- [ ] Week 7: dashboard, monthly PDF report, daily digest
- [ ] Week 8: write-up and demo

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Inspiration
The idea of monitoring AI tools the same way machines are monitored, and of short automated daily summaries, is inspired by publicly described work from Mayo Clinic's Radiation Oncology AI & Data Analytics group. This is an independent project on simulated data and is not affiliated with Mayo Clinic.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                               # should pass
PYTHONPATH=src python -m linac_qa.simulate --out data/simulated --seed 42
PYTHONPATH=src python scripts/plot_demo.py           # writes docs/img/demo_trend.png
```

## What the simulator produces
Two linacs (LA1, LA2), five parameters, about 260 weekdays of data, plus a ground-truth file listing four injected problems:

| Event | Machine / parameter | Purpose |
|-------|---------------------|---------|
| Slow drift | LA1 output | Should be caught well before the action level |
| Slow drift | LA2 kV imaging shift | Second drift, different scale |
| Step change | LA1 MLC picket fence | Sudden shift, like after a repair |
| One-day spike | LA2 laser | Transient; should NOT be reported as a trend |

Because the truth is known, detection quality can be measured (Week 5).

## Layout
```
config/tolerances.toml   illustrative tolerance/action levels
src/linac_qa/            package code (simulate.py now; db, engine, report later)
tests/                   pytest
scripts/                 plotting and helper scripts
docs/                    roadmap, design notes, images
data/                    generated data (simulated only)
```

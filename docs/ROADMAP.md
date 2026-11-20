# Roadmap: Linac QA Hub + AI-Model Monitoring (8 weeks)

**Plan:** about 6-8 hours per week. Each week ends with something you can commit and show.
If a week slips, keep the order and cut scope, never the tests.

**Inspiration (not a copy):** Mayo Clinic's Radiation Oncology AI & Data Analytics group (AIDA) publicly describes an
"AI Monitoring (AIM) Loop" that tracks metrics such as Dice score to catch model drift, and a "Daily Dose" LLM-written daily
summary. This project builds small, original, simulated-data versions of those two ideas on top of a linac QA analytics core.
Do not claim any connection to Mayo or AIDA.

## Big picture

```
simulated QA data ─┐
                   ├─> SQLite ─> tolerance engine ─> drift engine ─┬─> dashboard
simulated AI-model │                                               ├─> monthly PDF report
metrics (Dice) ────┘                                               └─> daily digest
```

One drift engine monitors two kinds of things: physical machines (linac QA) and AI tools (model performance).

---

## Week 1: Foundation (starter already built)
**Goal:** project runs on your computer and lives on GitHub.

| Day | Task | Done when |
|-----|------|-----------|
| 1 | Unzip, create venv, `pip install -r requirements.txt`, run `pytest` | 7 tests pass |
| 2 | Create GitHub repo `linac-qa-hub`, first commit and push | Repo is visible online |
| 3 | Read `simulate.py` line by line. Change a drift rate, rerun `plot_demo.py` | You can explain every function aloud |
| 4 | Replace placeholder tolerances in `config/tolerances.toml` with AAPM TG-142 values | Source cited in a comment |
| 5 | Add the plot to README, write 3 sentences on why you are building this | README reads clearly |

## Week 2: SQL data store
**Goal:** data lives in a database, not loose CSV files.
- SQLite schema: `machines`, `parameters` (with tolerance/action levels), `measurements`, `calibrations` (equipment, due dates), `ai_models`, `ai_metrics`
- `db.py`: create schema, load simulated CSVs
- Write and document 3 useful queries (for example: latest value per machine, out-of-tolerance days per month, calibrations due in 30 days)
- Tests: load, count rows, foreign keys hold

**Done when:** `python -m linac_qa.db --build` creates the database from simulated data and the 3 queries return sensible results.

## Week 3: Tolerance engine
**Goal:** every measurement is labeled pass, warning, or action.
- `engine/tolerance.py`: apply the limits from the config, handle one-sided parameters (like MLC error) and two-sided ones
- Monthly summary table per machine: days tested, warnings, actions
- Unit tests on edge cases (exactly at the limit, negative values, missing days)

**Done when:** a function returns a labeled table and tests cover the boundaries.

## Week 4: Drift detection engine (the core)
**Goal:** flag a problem before it reaches the action level, and do not flag one-day spikes as trends.
- Implement two detectors: **EWMA control chart** and **CUSUM**
- Baseline from the first N clean days; alert when the statistic crosses its limit
- Spike rule: a single outlier is reported as "transient", not "drift"
- Plot each detector with the alert date marked

**Done when:** both injected drifts and the step change are flagged, and the laser spike is not called a drift.

## Week 5: AI-model monitoring (the AIM-style module)
**Goal:** the same engine watches a simulated AI tool.
- Extend the simulator: weekly Dice score for an imaginary auto-contouring model, with a slow degradation injected (for example, after a software update or a change in scanner protocol), plus a seasonal wobble so it is not too easy
- Add a second metric, such as percent of contours needing major edits
- Reuse the Week 4 detectors with no new detection code; only configuration changes
- Alert text that makes sense to a clinician: "Dice fell from 0.88 to 0.84 over 6 weeks"

**Done when:** one command runs the engine over both linac QA and AI-model metrics and lists all alerts in one table.

## Week 6: Validation (your resume number)
**Goal:** prove it works with numbers.
- Run the full simulation over 100 random seeds
- Report: detection rate, **lead time** (days between first alert and first action-level breach), false-alarm rate on clean data, and spike handling
- Compare EWMA vs CUSUM vs a naive "wait for the action level" rule
- Save a results table and one summary figure in `docs/validation.md`

**Done when:** you can say, for example, "caught 98% of drifts a median of N days before the action level, with M false alarms per year." Use your real numbers.

## Week 7: Outputs people actually use
**Goal:** the tool produces things a physicist would read.
- **Dashboard** (Streamlit): pick machine and date range, see trends, alerts, calibrations due
- **Monthly PDF report:** summary table, trend plots, alerts, sign-off line for the physicist
- **Daily digest** (Daily Dose style): a short text summary generated from the numbers.
  - Step 1: template-based, fully deterministic
  - Step 2 (optional): pass the already-computed facts to an LLM to reword them. Numbers always come from code, never from the model. Simulated data only.

**Done when:** `streamlit run app/dashboard.py` works, and one command produces the PDF and the digest.

## Week 8: Polish and publish
- README: problem, approach, results table, screenshots, limitations
- `docs/limitations.md`: simulated data, illustrative tolerances, not for clinical use, what real deployment would need
- 2-minute demo video (screen recording)
- LinkedIn post and resume bullet using your measured numbers
- Pin the repo on your GitHub profile; add the link at the top of your resume

---

## Stretch goals (only after Week 8)
- Gamma analysis with PyMedPhys on public sample data
- Plan-parameter chart check from DICOM-RT (TCIA data)
- Docker + GitHub Actions running the tests
- Per-field dose prediction is a much larger project; leave for later

## Validation metrics (reference)
- **Lead time:** days between first detection and first action-level breach (bigger is better)
- **Detection rate:** share of injected drifts caught
- **False alarms:** flags on clean data and on the one-day spike
- Report mean and spread across many seeds, not one lucky run

## Honest limits (keep these in the README)
- Simulated data, not real clinic data
- Tolerance values must come from TG-142 and clinic policy before any real use
- Research and portfolio tool, not for clinical decisions
- Inspired by public descriptions of Mayo's AIDA work; not affiliated with Mayo Clinic

## Resume bullet (fill in the numbers after Week 6)
> Built a Python/SQL monitoring tool for linac QA and AI-model performance using EWMA/CUSUM control charts and TG-142 tolerances; flagged simulated drift a median of **N days** before action-level breach (**X%** detection, **Y** false alarms/year); auto-generated monthly QA reports and daily digests.

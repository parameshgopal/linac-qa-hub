# Project plan

The project is built in eight stages. Each stage ends with something that runs and has tests.

## How the pieces fit

```
simulated QA data ─┐
                   ├─> SQLite ─> tolerance labels ─> drift detection ─┬─> Power BI dashboard
simulated AI-model │                                                  ├─> monthly PDF report
metrics (Dice) ────┘                                                  └─> daily digest
```

One drift-detection engine monitors two kinds of things: physical machines (linac QA) and an AI tool (model performance). AI-model metrics skip the tolerance step and reuse the detector.

## Stages

| Stage | Build | Done when |
|-------|-------|-----------|
| 1 | Simulator with injected events, tests, demo plot, TG-142 tolerance values | `pytest` passes; tolerance source is cited |
| 2 | SQLite schema (machines, parameters, measurements, calibrations, ai_models, ai_metrics) and loader | Simulated CSVs load into the database; 3 documented queries return sensible results |
| 3 | Tolerance engine | Every measurement is labeled pass, warning or action; boundary cases are tested |
| 4 | Drift detection with EWMA and CUSUM control charts | Injected drifts and the step change are flagged; the one-day spike is reported as transient |
| 5 | AI-model monitoring module | The same detectors flag a simulated degradation in Dice score and contour-edit rate |
| 6 | Validation across 100 random seeds | Results table and figure in `docs/validation.md` |
| 7 | Power BI dashboard (fed by exported tables), monthly PDF report, daily digest | One command exports the tables and builds the report |
| 8 | Documentation and demo | README, limitations, and a short demo |

## Stretch goals
- Gamma analysis with PyMedPhys on public sample data
- Plan-parameter chart check from DICOM-RT (public TCIA data)
- Docker and GitHub Actions to run the tests
- A hosted web version of the dashboard

## Validation metrics (Stage 6)
- **Lead time:** days between the first alert and the first action-level breach (larger is better)
- **Detection rate:** share of injected drifts that are caught
- **False alarms:** alerts on clean data and on the one-day spike
- Reported as mean and spread across many seeds, not a single run

## Limitations
- Simulated data, not real clinic data
- Tolerance values must come from TG-142 and local policy before any real use
- Research and portfolio tool, not for clinical decisions

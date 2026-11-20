"""Simulate daily linac QA measurements with known, injected problems.

Why simulate? Real QA logs are protected clinic data and are not public.
Simulated data has one big advantage: we know exactly when each problem started,
so later we can measure how early the trend engine detects it (the project's
validation result).

Usage:
    python -m linac_qa.simulate --out data/simulated --seed 42
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "tolerances.toml"

# parameter -> (baseline mean, baseline standard deviation)
BASELINE: dict[str, tuple[float, float]] = {
    "output_dev_pct": (0.0, 0.35),
    "symmetry_dev_pct": (0.0, 0.25),
    "mlc_picket_max_mm": (0.35, 0.08),
    "laser_offset_mm": (0.0, 0.30),
    "kv_shift_mm": (0.0, 0.25),
}

MACHINES = ("LA1", "LA2")

# Injected problems. start_day counts weekdays from the first date.
#   drift: value rises linearly by `rate` per weekday after start_day
#   step:  value jumps by `size` at start_day and stays (e.g. after a repair)
#   spike: single-day outlier of `size` (a transient, NOT a real trend)
DEFAULT_EVENTS: list[dict] = [
    {"machine": "LA1", "parameter": "output_dev_pct", "kind": "drift", "start_day": 100, "rate": 0.025},
    {"machine": "LA2", "parameter": "kv_shift_mm", "kind": "drift", "start_day": 140, "rate": 0.014},
    {"machine": "LA1", "parameter": "mlc_picket_max_mm", "kind": "step", "start_day": 190, "size": 0.75},
    {"machine": "LA2", "parameter": "laser_offset_mm", "kind": "spike", "start_day": 80, "size": 2.6},
]


def load_limits(path: Path = DEFAULT_CONFIG) -> dict[str, dict]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _apply_events(values: np.ndarray, machine: str, parameter: str, events: list[dict]) -> np.ndarray:
    out = values.copy()
    n = len(out)
    for ev in events:
        if ev["machine"] != machine or ev["parameter"] != parameter:
            continue
        s = ev["start_day"]
        if ev["kind"] == "drift":
            out[s:] += ev["rate"] * np.arange(1, n - s + 1)
        elif ev["kind"] == "step":
            out[s:] += ev["size"]
        elif ev["kind"] == "spike":
            out[s] += ev["size"]
        else:
            raise ValueError(f"unknown event kind: {ev['kind']}")
    return out


def _first_breach(dates: pd.Series, values: np.ndarray, level: float, after: int = 0):
    idx = np.flatnonzero(np.abs(values[after:]) > level)
    return dates.iloc[after + idx[0]].date().isoformat() if idx.size else ""


def simulate(
    n_days: int = 260,
    start: str = "2025-01-06",
    seed: int = 42,
    events: list[dict] | None = None,
    limits: dict[str, dict] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (measurements, truth_events).

    measurements: long format with columns date, machine, parameter, value, unit_note
    truth_events: one row per injected event, with the first date the measured
                  value actually crossed the tolerance and action levels.
    """
    rng = np.random.default_rng(seed)
    events = DEFAULT_EVENTS if events is None else events
    limits = limits or load_limits()
    dates = pd.Series(pd.bdate_range(start=start, periods=n_days))

    for ev in events:
        if not 0 <= ev["start_day"] < n_days:
            raise ValueError(
                f"event {ev['kind']} on {ev['machine']}/{ev['parameter']} starts at day "
                f"{ev['start_day']}, outside the {n_days}-day simulation"
            )

    rows = []
    series: dict[tuple[str, str], np.ndarray] = {}
    for machine in MACHINES:
        for parameter, (mean, sd) in BASELINE.items():
            clean = rng.normal(mean, sd, n_days)
            vals = _apply_events(clean, machine, parameter, events)
            series[(machine, parameter)] = vals
            rows.append(
                pd.DataFrame(
                    {"date": dates, "machine": machine, "parameter": parameter, "value": vals.round(3)}
                )
            )
    measurements = pd.concat(rows, ignore_index=True)

    truth = []
    for ev in events:
        key = (ev["machine"], ev["parameter"])
        vals = series[key]
        lim = limits[ev["parameter"]]
        truth.append(
            {
                **ev,
                "start_date": dates.iloc[ev["start_day"]].date().isoformat(),
                "first_tolerance_breach": _first_breach(dates, vals, lim["tolerance"], ev["start_day"]),
                "first_action_breach": _first_breach(dates, vals, lim["action"], ev["start_day"]),
            }
        )
    return measurements, pd.DataFrame(truth)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--out", default="data/simulated", help="output folder")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--days", type=int, default=260, help="number of weekdays")
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meas, truth = simulate(n_days=args.days, seed=args.seed)
    meas.to_csv(out / "qa_daily.csv", index=False)
    truth.to_csv(out / "truth_events.csv", index=False)
    print(f"Wrote {len(meas)} measurements and {len(truth)} injected events to {out}/")


if __name__ == "__main__":
    main()

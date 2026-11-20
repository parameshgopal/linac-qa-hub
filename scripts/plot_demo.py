"""Plot the simulated QA data with tolerance/action lines (README screenshot).

Run from the project root:
    PYTHONPATH=src python scripts/plot_demo.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from linac_qa.simulate import load_limits, simulate

meas, truth = simulate()
limits = load_limits()
meas["date"] = pd.to_datetime(meas["date"])

panels = [
    ("LA1", "output_dev_pct"),
    ("LA2", "kv_shift_mm"),
    ("LA1", "mlc_picket_max_mm"),
    ("LA2", "laser_offset_mm"),
]
fig, axes = plt.subplots(len(panels), 1, figsize=(9, 10), sharex=True)
for ax, (machine, param) in zip(axes, panels):
    d = meas[(meas.machine == machine) & (meas.parameter == param)]
    ax.plot(d["date"], d["value"], lw=1, color="#1f5fa8")
    lim = limits[param]
    for sign in (1, -1) if "mlc" not in param else (1,):
        ax.axhline(sign * lim["tolerance"], color="#d99a00", ls="--", lw=1)
        ax.axhline(sign * lim["action"], color="#c0392b", ls="--", lw=1)
    ev = truth[(truth.machine == machine) & (truth.parameter == param)].iloc[0]
    ax.axvline(pd.to_datetime(ev["start_date"]), color="gray", ls=":", lw=1)
    ax.set_title(f"{machine} - {param} ({ev['kind']} injected at dotted line)", fontsize=10)
    ax.grid(alpha=0.2)
axes[-1].set_xlabel("Date")
fig.suptitle("Simulated daily linac QA (yellow = tolerance, red = action)", y=0.995)
fig.tight_layout()

out = Path("docs/img/demo_trend.png")
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=130)
print(f"saved {out}")

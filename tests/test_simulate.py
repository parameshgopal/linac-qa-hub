import numpy as np
import pandas as pd
import pytest

from linac_qa.simulate import BASELINE, MACHINES, simulate


def test_schema_and_size():
    meas, truth = simulate(n_days=260)
    assert list(meas.columns) == ["date", "machine", "parameter", "value"]
    assert len(meas) == 260 * len(MACHINES) * len(BASELINE)
    assert meas["value"].notna().all()
    assert len(truth) == 4


def test_event_outside_simulation_window_raises():
    with pytest.raises(ValueError, match="outside"):
        simulate(n_days=50)


def test_same_seed_is_reproducible():
    a, _ = simulate(seed=7)
    b, _ = simulate(seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_different_seed_differs():
    a, _ = simulate(seed=1)
    b, _ = simulate(seed=2)
    assert not np.allclose(a["value"], b["value"])


def test_clean_run_never_breaches_action_levels():
    meas, _ = simulate(events=[])
    from linac_qa.simulate import load_limits

    limits = load_limits()
    for parameter, grp in meas.groupby("parameter"):
        assert (grp["value"].abs() <= limits[parameter]["action"]).all(), parameter


def test_drift_events_breach_after_they_start():
    _, truth = simulate()
    drifts = truth[truth["kind"] == "drift"]
    assert len(drifts) == 2
    for _, row in drifts.iterrows():
        assert row["first_tolerance_breach"], "drift never reached tolerance"
        assert row["first_action_breach"], "drift never reached action level"
        assert row["start_date"] < row["first_tolerance_breach"] < row["first_action_breach"]


def test_spike_is_a_single_day():
    meas, _ = simulate()
    sub = meas[(meas["machine"] == "LA2") & (meas["parameter"] == "laser_offset_mm")]
    assert (sub["value"].abs() > 1.5).sum() == 1

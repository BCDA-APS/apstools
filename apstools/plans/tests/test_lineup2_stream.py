"""
Tests for lineup2() signal_stats stream (issue #1046).

Verifies that lineup2() writes peak statistics as a bluesky stream
before the run closes, using simulated devices only (no EPICS IOCs).
"""

import math
import re
import sys
from contextlib import nullcontext as does_not_raise

import databroker
import pytest
from bluesky import RunEngine
from ophyd import Signal
from ophyd import SoftPositioner
from ophyd.sim import SynGauss

from ...callbacks.scan_signal_statistics import SignalStatsCallback
from ..alignment import lineup2

MAIN = sys.modules["__main__"]


@pytest.fixture()
def RE():
    """Return a RunEngine with a temp catalog subscription."""
    cat = databroker.temp()
    _RE = RunEngine({})
    _RE.subscribe(cat.v1.insert)
    return _RE, cat


@pytest.fixture()
def motor():
    """Return a simulated positioner centred at 0."""
    return SoftPositioner(name="motor", init_pos=0)


@pytest.mark.parametrize(
    "parms, context",
    [
        # --- stream presence and key checks ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                stats_stream="signal_stats",
                expected_keys=["n", "centroid", "fwhm", "x_at_max_y", "success"],
            ),
            does_not_raise(),
            id="default stream name contains expected statistics",
        ),
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                stats_stream="my_custom_stream",
                expected_keys=["n", "centroid", "fwhm", "x_at_max_y", "success"],
            ),
            does_not_raise(),
            id="custom stream name is honoured",
        ),
        # --- success/failure values ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                expected_success=True,
                expected_centroid_tol=0.2,
                absent_keys=["reasons"],
            ),
            does_not_raise(),
            id="success=True for a clear Gaussian peak, no reasons",
        ),
        pytest.param(
            dict(
                center=100.0,
                Imax=100.0,
                expected_success=False,
                expected_reason_fragments=["No strong peak found."],
            ),
            does_not_raise(),
            id="success=False when peak is outside scan range",
        ),
        pytest.param(
            dict(
                center=0.0,
                Imax=0.0,
                expected_success=False,
                expected_reason_fragments=["No strong peak found."],
            ),
            does_not_raise(),
            id="constant-zero detector reports no strong peak",
        ),
        # --- nscans=2 covers rescan with adjusted range (lines 628-631) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                nscans=2,
                expected_success=True,
            ),
            does_not_raise(),
            id="nscans=2 rescans with adjusted range on success",
        ),
        # --- reporting=True covers final report (line 634) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                reporting=True,
                expected_success=True,
            ),
            does_not_raise(),
            id="reporting=True prints final report",
        ),
        # --- auto-created signal_stats from __main__ (lines 492-500) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                auto_signal_stats=True,
                expected_success=True,
            ),
            does_not_raise(),
            id="signal_stats auto-created in __main__ namespace",
        ),
        # --- mover without .position uses .get() fallback (lines 485-486) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                use_signal_mover=True,
                expected_keys=["n", "success"],
            ),
            does_not_raise(),
            id="mover without .position uses .get() fallback",
        ),
        # --- single detector not in a list (line 477) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                single_detector=True,
                expected_success=True,
            ),
            does_not_raise(),
            id="single detector (not a list) is auto-wrapped",
        ),
        # --- signal_stats pre-existing in __main__ (line 494) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                preexisting_signal_stats=True,
                expected_success=True,
            ),
            does_not_raise(),
            id="signal_stats found in __main__ namespace",
        ),
        # --- FWHM is zero reason (line 541) ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                points=1,
                expected_success=False,
                expected_reason_fragments=["FWHM is zero."],
            ),
            does_not_raise(),
            id="1-point scan produces FWHM=0 reason",
        ),
        # --- error cases ---
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                points=0,
            ),
            pytest.raises(
                AttributeError,
                match=re.escape("'NoneType' object has no attribute 'fwhm'"),
            ),
            id="points=0 raises AttributeError (no events, analysis is None)",
        ),
        pytest.param(
            dict(
                center=0.0,
                Imax=100.0,
                points=-5,
            ),
            pytest.raises(ValueError, match=re.escape("must be non-negative")),
            id="negative points raises ValueError from numpy",
        ),
    ],
)
def test_lineup2_stats_stream(parms, context, RE, motor):
    """lineup2() writes peak statistics as a stream before the run closes."""
    _RE, cat = RE
    stream_name = parms.get("stats_stream", "signal_stats")

    # Choose mover: Signal (no .position) or SoftPositioner.
    if parms.get("use_signal_mover"):
        mover = Signal(name="motor", value=0.0)
        det = SynGauss("det", motor, "motor", center=0.0, Imax=100.0, sigma=1.0, noise="none")
    else:
        mover = motor
        det = SynGauss(
            "det",
            motor,
            "motor",
            center=parms.get("center", 0.0),
            Imax=parms.get("Imax", 100.0),
            sigma=1.0,
            noise="none",
        )

    # Build lineup2 kwargs.
    kwargs = dict(
        nscans=parms.get("nscans", 1),
        stats_stream=stream_name,
    )

    if parms.get("auto_signal_stats"):
        # Remove any pre-existing signal_stats from __main__ so lineup2
        # creates a fresh one (covers lines 496-500).
        if hasattr(MAIN, "signal_stats"):
            delattr(MAIN, "signal_stats")
        kwargs["reporting"] = False
    elif parms.get("preexisting_signal_stats"):
        # Put a SignalStatsCallback in __main__ so lineup2 finds it (line 494).
        pre_stats = SignalStatsCallback()
        pre_stats.reporting = False
        setattr(MAIN, "signal_stats", pre_stats)
        kwargs["reporting"] = False
    else:
        stats = SignalStatsCallback()
        stats.reporting = parms.get("reporting", False)
        kwargs["signal_stats"] = stats
        if "reporting" in parms:
            kwargs["reporting"] = parms["reporting"]

    # Pass detector as single object or list (line 477).
    det_arg = det if parms.get("single_detector") else [det]

    with context:
        _RE(
            lineup2(
                det_arg,
                mover,
                -3,
                3,
                parms.get("points", 11),
                **kwargs,
            )
        )

        run = cat.v2[-1]
        assert stream_name in list(run)
        stream_data = getattr(run, stream_name).read()

        # Check expected keys are present.
        for key in parms.get("expected_keys", []):
            full_key = f"lineup2_signal_stats_{key}"
            assert full_key in stream_data, f"{full_key!r} not found in stream"

        # Check expected keys are absent.
        for key in parms.get("absent_keys", []):
            full_key = f"lineup2_signal_stats_{key}"
            assert full_key not in stream_data, f"{full_key!r} should not be in stream"

        # Check success flag.
        if "expected_success" in parms:
            success_val = bool(stream_data["lineup2_signal_stats_success"].values.item())
            assert success_val is parms["expected_success"]

        # Check centroid tolerance.
        if "expected_centroid_tol" in parms:
            centroid_val = float(stream_data["lineup2_signal_stats_centroid"].values.item())
            assert math.isclose(
                centroid_val,
                parms["center"],
                abs_tol=parms["expected_centroid_tol"],
            )

        # Check reasons fragments.
        if "expected_reason_fragments" in parms:
            reasons_key = "lineup2_signal_stats_reasons"
            assert reasons_key in stream_data
            reasons_val = str(stream_data[reasons_key].values.item())
            assert len(reasons_val) > 0
            for fragment in parms["expected_reason_fragments"]:
                assert fragment in reasons_val

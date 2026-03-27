"""
Tests for SignalStatsCallback.

Verifies that the callback correctly collects data from bluesky
documents and computes peak statistics without requiring a live
RunEngine or EPICS IOCs.  See issue #1072.
"""

import math
import re
from contextlib import nullcontext as does_not_raise

import pytest
from bluesky import RunEngine
from bluesky import plans as bp
from ophyd import SoftPositioner
from ophyd.sim import SynGauss

from ..scan_signal_statistics import SignalStatsCallback


@pytest.fixture()
def signal_stats():
    """Return a fresh SignalStatsCallback with reporting disabled."""
    ssc = SignalStatsCallback()
    ssc.reporting = False
    return ssc


@pytest.fixture()
def RE():
    """Return a fresh RunEngine."""
    return RunEngine({})


@pytest.fixture()
def motor():
    """Return a simulated positioner."""
    return SoftPositioner(name="motor", init_pos=0)


@pytest.fixture()
def noisy_det(motor):
    """Return a simulated Gaussian detector centred at x=0."""
    return SynGauss(
        "noisy_det",
        motor,
        "motor",
        center=0.0,
        Imax=100.0,
        sigma=1.0,
        noise="none",
    )


def test_clear(signal_stats):
    """clear() resets all internal state."""
    signal_stats.clear()
    assert signal_stats._scanning is False
    assert signal_stats.detectors == []
    assert signal_stats.positioners == []
    assert signal_stats._registers == {}
    assert signal_stats._descriptor_uid is None
    assert signal_stats._x_name is None
    assert signal_stats._y_names == []
    assert signal_stats._data == {}


def test_repr_before_use(signal_stats):
    """repr() works even before any documents are received."""
    r = repr(signal_stats)
    assert "SignalStatsCallback" in r
    assert "motors=" in r
    assert "detectors=" in r


def test_start_sets_state(signal_stats):
    """start() sets _scanning=True and records detectors/positioners."""
    start_doc = {
        "uid": "abc123",
        "time": 0,
        "detectors": ["det1"],
        "motors": ["m1"],
        "plan_name": "scan",
    }
    signal_stats.start(start_doc)
    assert signal_stats._scanning is True
    assert signal_stats.detectors == ["det1"]
    assert signal_stats.positioners == ["m1"]


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(npts=11),
            does_not_raise(),
            id="basic scan collects correct statistics",
        ),
        pytest.param(
            dict(npts=3),
            does_not_raise(),
            id="minimal 3-point scan",
        ),
    ],
)
def test_scan_statistics(parms, context, signal_stats, RE, motor, noisy_det):
    """SignalStatsCallback collects correct statistics from a scan."""
    npts = parms["npts"]

    RE.subscribe(signal_stats.receiver)

    with context:
        RE(bp.scan([noisy_det], motor, -3, 3, npts))

    assert signal_stats.analysis is not None
    assert signal_stats.analysis["n"] == npts
    assert math.isclose(signal_stats.analysis["centroid"], 0.0, abs_tol=0.2)
    assert math.isclose(signal_stats.analysis["x_at_max_y"], 0.0, abs_tol=0.7)
    assert signal_stats.analysis["max_y"] > 0
    assert signal_stats.analysis["min_x"] == -3.0
    assert signal_stats.analysis["max_x"] == 3.0


def test_scan_data_collected(signal_stats, RE, motor, noisy_det):
    """Data arrays are populated after a scan."""
    RE.subscribe(signal_stats.receiver)
    RE(bp.scan([noisy_det], motor, -2, 2, 5))

    assert "motor" in signal_stats._data
    assert "noisy_det" in signal_stats._data
    assert len(signal_stats._data["motor"]) == 5
    assert len(signal_stats._data["noisy_det"]) == 5


def test_scanning_flag_lifecycle(signal_stats, RE, motor, noisy_det):
    """_scanning is True during a scan and False after."""
    RE.subscribe(signal_stats.receiver)
    RE(bp.scan([noisy_det], motor, -1, 1, 3))

    assert signal_stats._scanning is False


def test_receiver_ignores_unknown_document_type(signal_stats):
    """receiver() ignores document types it doesn't handle."""
    signal_stats.receiver("datum", {"datum_id": "x"})
    # Should not raise; _scanning should remain unchanged.
    assert signal_stats._scanning is False


def test_descriptor_ignored_when_not_scanning(signal_stats):
    """descriptor() is a no-op when _scanning is False."""
    signal_stats.clear()
    signal_stats._scanning = False
    signal_stats.descriptor({"name": "primary", "uid": "x", "data_keys": {}})
    assert signal_stats._descriptor_uid is None


def test_event_ignored_when_not_scanning(signal_stats):
    """event() is a no-op when _scanning is False."""
    signal_stats._scanning = False
    signal_stats.event({"descriptor": "x", "data": {}})
    # Should not raise; no data collected.
    assert signal_stats._data == {}


def test_stop_ignored_when_not_scanning(signal_stats):
    """stop() is a no-op when _scanning is False."""
    signal_stats._scanning = False
    signal_stats.stop({"run_start": "x"})
    assert signal_stats._scanning is False
    assert signal_stats.analysis is None


def test_report_no_data(signal_stats, capsys):
    """report() prints nothing when no data has been collected."""
    signal_stats.clear()
    signal_stats.report()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_report_after_scan(signal_stats, RE, motor, noisy_det, capsys):
    """report() prints a table after a scan."""
    signal_stats.reporting = True
    RE.subscribe(signal_stats.receiver)
    RE(bp.scan([noisy_det], motor, -2, 2, 11))

    captured = capsys.readouterr()
    assert "Motor:" in captured.out
    assert "Detector:" in captured.out
    assert "centroid" in captured.out
    assert "fwhm" in captured.out


def test_clear_between_scans(signal_stats, RE, motor, noisy_det):
    """Running two scans resets state between them."""
    RE.subscribe(signal_stats.receiver)

    RE(bp.scan([noisy_det], motor, -2, 2, 5))
    first_n = signal_stats.analysis["n"]

    RE(bp.scan([noisy_det], motor, -1, 1, 7))
    assert signal_stats.analysis["n"] == 7
    assert signal_stats.analysis["n"] != first_n


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                stream_name="baseline",
                detectors=["det"],
                motors=["m1"],
                data_keys={"det": {}, "m1": {}},
            ),
            does_not_raise(),
            id="non-primary stream is ignored",
        ),
        pytest.param(
            dict(
                stream_name="primary",
                detectors=["missing_det"],
                motors=["m1"],
                data_keys={"m1": {}},
            ),
            does_not_raise(),
            id="no matching detector signals in descriptor",
        ),
        pytest.param(
            dict(
                stream_name="primary",
                detectors=["det"],
                motors=["missing_motor"],
                data_keys={"det": {}},
            ),
            does_not_raise(),
            id="no matching motor signals in descriptor",
        ),
    ],
)
def test_descriptor_no_usable_signals(parms, context, signal_stats):
    """descriptor() handles missing or non-matching signals gracefully."""
    with context:
        signal_stats.clear()
        signal_stats._scanning = True
        signal_stats.detectors = parms["detectors"]
        signal_stats.positioners = parms["motors"]
        signal_stats.descriptor(
            {
                "name": parms["stream_name"],
                "uid": "test_uid",
                "data_keys": parms["data_keys"],
            }
        )

        if parms["stream_name"] != "primary":
            assert signal_stats._descriptor_uid is None
        else:
            # Descriptor was processed but no x/y names were set.
            assert signal_stats._x_name is None
            assert signal_stats._y_names == []


def test_event_wrong_descriptor_ignored(signal_stats):
    """event() ignores events from a non-matching descriptor uid."""
    signal_stats._scanning = True
    signal_stats._descriptor_uid = "correct_uid"
    signal_stats._x_name = "motor"
    signal_stats._y_names = []
    signal_stats._data = {"motor": []}

    signal_stats.event({"descriptor": "wrong_uid", "data": {"motor": 1.0}})
    assert signal_stats._data["motor"] == []


def test_compute_before_data(signal_stats):
    """compute() is a no-op when no data has been accumulated."""
    signal_stats.clear()
    signal_stats.compute()
    assert signal_stats.analysis is None


def test_compute_with_data(signal_stats):
    """compute() populates analysis from manually accumulated data."""
    signal_stats.clear()
    signal_stats._x_name = "x"
    signal_stats._y_names = ["y"]
    signal_stats._data = {"x": [1.0, 2.0, 3.0], "y": [10.0, 20.0, 10.0]}

    signal_stats.compute()

    assert signal_stats.analysis is not None
    assert signal_stats.analysis["n"] == 3
    assert signal_stats.analysis["max_y"] == 20.0
    assert signal_stats.analysis["x_at_max_y"] == 2.0


def test_compute_called_by_stop(signal_stats, RE, motor, noisy_det):
    """stop() calls compute(), populating analysis correctly."""
    RE.subscribe(signal_stats.receiver)
    RE(bp.scan([noisy_det], motor, -2, 2, 11))

    assert signal_stats.analysis is not None
    assert signal_stats.analysis["n"] == 11
    assert math.isclose(signal_stats.analysis["centroid"], 0.0, abs_tol=0.2)


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(x_name=None, y_names=["y"], data={"y": [1.0, 2.0]}),
            does_not_raise(),
            id="compute is no-op when _x_name is None",
        ),
        pytest.param(
            dict(x_name="x", y_names=[], data={"x": [1.0, 2.0]}),
            does_not_raise(),
            id="compute is no-op when _y_names is empty",
        ),
        pytest.param(
            dict(x_name="x", y_names=["y"], data={"x": [], "y": []}),
            does_not_raise(),
            id="compute is no-op when _data arrays are empty",
        ),
        pytest.param(
            dict(x_name="x", y_names=["y"], data={"x": [1.0, 2.0]}),
            pytest.raises(KeyError, match=re.escape("y")),
            id="compute raises KeyError when y_name not in _data",
        ),
        pytest.param(
            dict(x_name="x", y_names=["y"], data={"x": [1.0, 2.0], "y": [1.0]}),
            pytest.raises(ValueError, match=re.escape("Unequal shapes:")),
            id="compute raises ValueError when x and y have different lengths",
        ),
    ],
)
def test_compute_incomplete_data(parms, context, signal_stats):
    """compute() handles missing or inconsistent data correctly."""
    with context:
        signal_stats.clear()
        signal_stats._x_name = parms["x_name"]
        signal_stats._y_names = parms["y_names"]
        signal_stats._data = parms["data"]

        signal_stats.compute()
        assert signal_stats.analysis is None

"""
Issue 606

> While using TuneAxis().tune(), received this message from
> a tuning scan where fwhm=None. In this case, the scan did
> not cross the peak.

    Error saving stream PeakStats:

Because fwhm is None.
"""

import dataclasses

import bluesky.preprocessors as bpp
import databroker
from bluesky import RunEngine
from bluesky.callbacks import best_effort

from .. import TuneResults
from ..doc_run import write_stream


@dataclasses.dataclass
class PeaksStatisticalData:
    """Statistical data from bec.peaks"""

    x: str = None
    y: str = None
    cen: float = None
    com: float = None
    fwhm: float = None
    min: list = None
    max: list = None
    crossings: list = None
    tune_ok: bool = False
    center: float = None
    initial_position: float = 0.0
    final_position: float = 0.0


@bpp.run_decorator()
def peak_stats_plan(peaks, stream="primary"):
    """Bluesky plan that saves PeakStats as a run."""
    stats = TuneResults("", name="stats")
    stats.set_stats(peaks)
    yield from write_stream(stats, stream)


def test_results_stream(capsys):
    bec = best_effort.BestEffortCallback()
    cat = databroker.temp()
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)
    RE.subscribe(bec)

    peaks = PeaksStatisticalData()
    peaks.x = "m1"
    peaks.y = "noisy"
    peaks.cen = -0.1550618680443165
    peaks.com = -0.05085308669291895
    peaks.fwhm = None
    peaks.min = [6.65000000e-01, 7.08289488e02]
    peaks.max = [-3.35000000e-01, 6.30815141e03]
    peaks.crossings = [-0.15506187]
    peaks.tune_ok = True
    peaks.center = -0.1550618680443165
    peaks.initial_position = 0.165
    peaks.final_position = -0.1550618680443165

    RE(peak_stats_plan(peaks, "PeakStats"))
    out, err = capsys.readouterr()
    assert err == ""
    assert out.find("PeakStats") >= 0

    run = cat.v2[-1]
    assert "PeakStats" in run
    assert run.metadata["start"]["scan_id"] == 1

    ds = run.PeakStats.read()
    prefix = "stats_"
    assert ds[f"{prefix}x"].data[0] == "m1"
    assert ds[f"{prefix}y"].data[0] == "noisy"
    assert ds[f"{prefix}fwhm"].data[0] == "null"
    assert ds[f"{prefix}cen"].data[0] == -0.1550618680443165
    assert ds[f"{prefix}com"].data[0] == -0.05085308669291895
    assert ds[f"{prefix}crossings"].data[0] == [-0.15506187]

    # these keys are not written by TuneResults.set_stats()
    for k in "center tune_ok initial_position final_position".split():
        assert ds[f"{prefix}{k}"].data[0] == 0

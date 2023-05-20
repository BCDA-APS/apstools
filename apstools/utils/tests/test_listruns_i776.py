"""
Test search for keys in hints from listruns().
"""

import random

import bluesky
import bluesky.plans as bp
import databroker
import pytest
from ophyd.scaler import ScalerCH

from ... import utils as utils
from ...tests import IOC_GP

PV = f"{IOC_GP}scaler1"


@pytest.mark.parametrize(
    # fmt: off
    "override, result",
    [
        (False, "scaler".split()),
        (True, "I0".split()),
    ],
    # fmt: on
)
def test_custom_hints(override, result):
    scaler = ScalerCH(PV, name="scaler")
    scaler.wait_for_connection()
    assert isinstance(scaler, ScalerCH)

    scaler.channels.chan01.chname.put("clock")
    scaler.channels.chan02.chname.put("I0")
    scaler.channels.chan03.chname.put("scint")
    scaler.channels.chan04.chname.put("diode")
    scaler.channels.chan05.chname.put("I000")
    scaler.channels.chan06.chname.put("I00")

    assert "" in list(scaler.read().keys())
    scaler.select_channels()
    assert "" not in list(scaler.read().keys())

    channel_names = list(scaler.read().keys())
    assert len(channel_names) > 2, f"{channel_names=}"
    chan = channel_names[1]
    assert chan != f"{scaler.name}_time", f"{chan=}  {scaler.name=}"

    cat = databroker.temp().v2
    RE = bluesky.RunEngine({})
    RE.subscribe(cat.v1.insert)

    scaler.preset_time.put(1)
    scaler.stage_sigs["preset_time"] = 0.2 + 0.1 * random.random()

    # make a run with the custom hint for "detectors"
    md = dict(hints=dict(detectors=[chan]))
    uids = RE(bp.count([scaler], md=md))
    assert len(uids) == 1

    # check the run for the custom hint
    run = cat[uids[0]]
    hints = run.metadata["start"].get("hints")
    assert hints is not None
    # assert hints == {}, f"{hints=}"

    dets = hints.get("detectors")
    assert dets is not None
    assert isinstance(dets, list)
    assert len(dets) == 1
    assert dets[0] == chan, f"{dets=}"

    # check listruns for the custom hint
    lr = utils.ListRuns()
    lr.cat = cat
    lr.hints_override = override
    dd = lr.parse_runs()
    assert isinstance(dd, dict)
    dets = dd.get("detectors")
    assert isinstance(dets, list)
    assert len(dets) == 1  # one run found
    assert isinstance(dets[0], list)
    assert len(dets[0]) == len(result)  # number of detectors
    assert dets[0][0] == result[0], f"{dets=}"

"""
test issue #1123: specwriter+baseline stream, extra data point written

# https://github.com/BCDA-APS/apstools/issues/1123
"""

import os
import pathlib
from contextlib import nullcontext as does_not_raise

import bluesky
import bluesky.plans
import pytest
import spec2nexus.spec
from bluesky import SupplementalData
from ophyd import Signal
from ophyd.sim import motor
from ophyd.sim import noisy_det

from .. import SpecWriterCallback2

signal1 = Signal(name="signal1", value=1.111)
signal2 = Signal(name="signal2", value=2.222)


@pytest.mark.parametrize(
    "baseline, context, expected",
    [
        [[], does_not_raise(), None],
        [[signal1, signal2], does_not_raise(), None],
    ],
)
def test_issue1123(baseline, context, expected, tempdir):
    with context as reason:
        os.chdir(tempdir)

        RE = bluesky.RunEngine()
        sd = SupplementalData()
        specwriter = SpecWriterCallback2()
        RE.subscribe(specwriter.receiver)

        if len(baseline) > 0:
            sd.baseline.extend(baseline)
        RE.preprocessors.append(sd)

        start, finish, npts = -1, 1, 3
        (uid,) = RE(bluesky.plans.scan([noisy_det], motor, start, finish, npts))

        path = pathlib.Path(specwriter.spec_filename)
        assert path.exists(), f"{specwriter.spec_filename=}"

        sdf = spec2nexus.spec.SpecDataFile(str(path))
        assert sdf is not None, f"{path=}"
        assert len(sdf.scans) == 1

        for scan in sdf.scans.values():
            assert "motor" in scan.data

            arr = scan.data.get("motor")
            assert arr is not None
            assert len(arr) == npts, f"{scan=}"
            assert arr[0] == start
            assert arr[-1] == finish

    if expected is not None:
        assert str(expected) in str(reason)

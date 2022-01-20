import pytest
import time

from ..calcout import CalcoutRecord
from ..sub import SubRecord
from ..sub import UserAverage
from ..sub import UserAverageDevice
from ...tests import IOC
from ...tests import SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING


@pytest.fixture(scope="function")
def ave():
    ave = UserAverage(f"{IOC}userAve9", name="ave")
    ave.wait_for_connection()
    ave.enable.put("E")
    yield ave
    ave.reset()


@pytest.fixture(scope="function")
def calc():
    calc = CalcoutRecord(f"{IOC}userCalcOut9", name="calc")
    calc.wait_for_connection()
    calc.enable.put("E")
    yield calc
    calc.reset()


# @pytest.fixture(scope="function")
# def sub():
#     # Is there some _other_ sub record to use for testing?
#     sub = SubRecord(f"{IOC}userAve9", name="sub")
#     sub.wait_for_connection()
#     sub.enable.put("E")
#     yield sub
#     sub.reset()


@pytest.mark.parametrize(
    "device, pv, nra, nca, nsl, nr",
    [
        [SubRecord, f"{IOC}userAve10", 12, 53, 137, 13],
        [UserAverage, f"{IOC}userAve10", 7, 33, 101, 7],
        [UserAverageDevice, IOC, 80, 340, 835, 70],
    ]
)
def test_connect(device, pv, nra, nca, nsl, nr):
    obj = device(pv, name="obj")
    assert obj is not None
    obj.wait_for_connection()

    assert len(obj.read_attrs) == nra
    assert len(obj.configuration_attrs) == nca
    assert len(obj._summary().splitlines()) == nsl
    assert len(obj.read()) == nr


# def test_sub_reset(sub):
#     assert isinstance(sub, SubRecord)
#     # TODO: need a sub record that can be reset, no general purpose available


def test_useraverage_reset(ave):
    pvname = ave.prefix.split(".")[0]

    assert ave.initroutine.get() == "initSubAve"
    assert ave.subroutine.get() == "SubAve"

    ave.number_samples.put(10)
    ave.channel.put(f"{pvname}.VAL")
    ave.precision.put(3)
    ave.mode.put("ONE-SHOT")
    ave.algorithm.put("FIT-LINE")

    ave.reset()
    time.sleep(SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)
    assert ave.initroutine.get() == "initSubAve"
    assert ave.subroutine.get() == "SubAve"

    assert ave.description.get() == pvname
    assert ave.enable.get() == "E"
    assert ave.channel.get() == ""
    # TODO: comes back as 1 : Why is that?
    # assert ave.number_samples.get() == 0
    assert ave.precision.get() == 0
    for attr in "mode algorithm scanning_rate".split():
        obj = getattr(ave, attr)
        assert obj.get() in (0, obj.enum_strs[0]), attr

# FIXME: 2022-01-20: skipped per #627
# def test_useraveragedevice_random(ave, calc):
#     # setup a random number generator
#     calc.calculation.put("RNDM")

#     # average the RNG
#     nsamples = 100
#     ave.channel.put(calc.prefix)
#     ave.number_samples.put(nsamples)
#     ave.precision.put(3)
#     ave.mode.put("ONE-SHOT")
#     ave.acquire.put(1)
#     for i in range(nsamples):
#         calc.process_record.put(1)
#         ave.process_record.put(1)
#         time.sleep(SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)
#         if ave.current_sample.get() == ave.number_samples.get():
#             break
#         assert ave.busy.get(as_string=False) == 1, i
#     assert ave.busy.get(as_string=False) == 0
#     # test that average = 0.5 as n -> inf
#     assert abs(ave.averaged_value.get() - 0.5) <= 0.1

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

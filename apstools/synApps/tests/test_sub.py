import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..calcout import CalcoutRecord
from ..sub import SubRecord
from ..sub import UserAverageDevice
from ..sub import UserAverageN


@pytest.fixture(scope="function")
def ave():
    ave = UserAverageN(f"{IOC_GP}userAve9", name="ave")
    ave.wait_for_connection()
    ave.enable.put("E")
    yield ave
    ave.reset()


@pytest.fixture(scope="function")
def calc():
    calc = CalcoutRecord(f"{IOC_GP}userCalcOut9", name="calc")
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
    "device, pv, connect, attr, expected",
    [
        [SubRecord, f"{IOC_GP}userAve10", False, "read_attrs", 12],
        [SubRecord, f"{IOC_GP}userAve10", False, "configuration_attrs", 65],
        [SubRecord, f"{IOC_GP}userAve10", True, "read()", 1],
        [SubRecord, f"{IOC_GP}userAve10", True, "summary()", 148],
        [UserAverageN, f"{IOC_GP}userAve10", False, "read_attrs", 7],
        [UserAverageN, f"{IOC_GP}userAve10", False, "configuration_attrs", 33],
        [UserAverageN, f"{IOC_GP}userAve10", True, "read()", 7],
        [UserAverageN, f"{IOC_GP}userAve10", True, "summary()", 101],
        [UserAverageDevice, IOC_GP, False, "read_attrs", 80],
        [UserAverageDevice, IOC_GP, False, "configuration_attrs", 340],
        [UserAverageDevice, IOC_GP, True, "read()", 70],
        [UserAverageDevice, IOC_GP, True, "summary()", 835],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


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
    timed_pause()
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
#         short_delay_for_EPICS_IOC_database_processing()
#         if ave.current_sample.get() == ave.number_samples.get():
#             break
#         assert ave.busy.get(as_string=False) == 1, i
#     assert ave.busy.get(as_string=False) == 0
#     # test that average = 0.5 as n -> inf
#     assert abs(ave.averaged_value.get() - 0.5) <= 0.1

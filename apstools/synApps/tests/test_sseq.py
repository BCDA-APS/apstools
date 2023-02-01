import pytest
from ophyd import EpicsSignal

from ...tests import IOC
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..sseq import SseqRecord
from ..sseq import UserStringSequenceDevice
from ..sseq import sseqRecordStep


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [SseqRecord, f"{IOC}userStringSeq10", False, "read_attrs", 31],
        [SseqRecord, f"{IOC}userStringSeq10", False, "configuration_attrs", 108],
        [SseqRecord, f"{IOC}userStringSeq10", True, "read()", 20],
        [SseqRecord, f"{IOC}userStringSeq10", True, "summary()", 274],

        [UserStringSequenceDevice, IOC, False, "read_attrs", 320],
        [UserStringSequenceDevice, IOC, False, "configuration_attrs", 1101],
        [UserStringSequenceDevice, IOC, True, "read()", 200],
        [UserStringSequenceDevice, IOC, True, "summary()", 2616],
    ]
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_sseq_reset():
    user = UserStringSequenceDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")
    assert len(user.read()) == 200

    sseq = user.sseq10
    assert isinstance(sseq, SseqRecord)
    sseq.enable.put("E")  # Note: only "E"

    step = sseq.steps.step1
    assert isinstance(step, sseqRecordStep)

    step.reset()
    timed_pause()

    assert step.input_pv.get() == ""

    uptime = EpicsSignal(f"{IOC}UPTIME", name="uptime")
    uptime.wait_for_connection()

    step.input_pv.put(uptime.pvname)
    assert step.string_value.get() == f"{0:.5f}"
    sseq.process_record.put(1)
    assert step.string_value.get() <= uptime.get()

    user.reset()
    timed_pause()
    assert step.input_pv.get() == ""
    assert step.string_value.get() == f"{0:.5f}"

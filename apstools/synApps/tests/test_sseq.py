from ophyd import EpicsSignal

from ..sseq import SseqRecord
from ..sseq import sseqRecordStep
from ..sseq import UserStringSequenceDevice


IOC = "gp:"
TEST_SSEQ_PV = f"{IOC}userStringSeq10"


def test_sseq_read():
    sseq = SseqRecord(TEST_SSEQ_PV, name="sseq")
    assert sseq is not None
    sseq.wait_for_connection()

    r = sseq.read()
    assert len(r) == 20


def test_sseq_reset():
    user = UserStringSequenceDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    sseq = user.sseq10
    assert isinstance(sseq, SseqRecord)
    sseq.enable.put("E")  # Note: only "E"

    step = sseq.steps.step1
    assert isinstance(step, sseqRecordStep)

    step.reset()
    assert step.input_pv.get() == ""

    uptime = EpicsSignal(f"{IOC}UPTIME", name="uptime")
    uptime.wait_for_connection()

    step.input_pv.put(uptime.pvname)
    assert step.string_value.get() == f"{0:.5f}"
    sseq.process_record.put(1)
    assert step.string_value.get() <= uptime.get()

    user.reset()
    assert step.input_pv.get() == ""
    assert step.string_value.get() == f"{0:.5f}"

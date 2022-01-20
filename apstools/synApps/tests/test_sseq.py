from ophyd import EpicsSignal
import time

from ..sseq import SseqRecord
from ..sseq import sseqRecordStep
from ..sseq import UserStringSequenceDevice
from ...__init__ import SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING


IOC = "gp:"


def test_read():
    sseq = SseqRecord(f"{IOC}userStringSeq10", name="sseq")
    assert sseq is not None
    sseq.wait_for_connection()

    assert len(sseq.read_attrs) == 31
    assert len(sseq.configuration_attrs) == 109
    assert len(sseq._summary().splitlines()) == 276


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
    time.sleep(SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)

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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

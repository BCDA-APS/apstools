"""
Ophyd support for the EPICS sseq (string sequence) record


Public Structures

.. autosummary::

    ~EditStringSequence
    ~SseqRecord
    ~UserStringSequenceDevice
    ~UserStringSequenceN
"""

from collections import OrderedDict
from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FC

from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsSynAppsRecordEnableMixin


STEP_LIST = [f"step{i+1}" for i in range(10)]  # step1, step2, step10


class sseqRecordStep(Device):
    """
    EPICS synApps sseq single step of an sseq record.

    Step of a synApps sseq record: 1..10  (note: for 10, the PVs use "A")

    .. index:: Ophyd Device; synApps sseqRecordStep

    .. autosummary::

        ~reset
    """

    input_pv = FC(EpicsSignal, "{self.prefix}.DOL{self._step}", kind="config")
    input_pv_valid = FC(EpicsSignalRO, "{self.prefix}.DOL{self._step}V", kind="config")
    delay = FC(EpicsSignal, "{self.prefix}.DLY{self._step}", kind="config")
    string_value = FC(
        EpicsSignal, "{self.prefix}.STR{self._step}", string=True, kind="hinted"
    )
    numeric_value = FC(EpicsSignal, "{self.prefix}.DO{self._step}", kind="hinted")
    output_pv = FC(EpicsSignal, "{self.prefix}.LNK{self._step}", kind="config")
    output_pv_valid = FC(EpicsSignalRO, "{self.prefix}.LNK{self._step}V", kind="config")

    waiting_completion = FC(
        EpicsSignalRO, "{self.prefix}.WTG{self._step}", kind="config"
    )
    wait_completion = FC(EpicsSignal, "{self.prefix}.WAIT{self._step}", kind="config")
    wait_error = FC(EpicsSignalRO, "{self.prefix}.WERR{self._step}", kind="config")

    def __init__(self, prefix, step, **kwargs):
        names = "_123456789A"  # step #10 (1-based) is called "A"
        self._step = names[step]
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.delay.put(0)
        self.numeric_value.put(0)  # EPICS will set string_value from this
        self.output_pv.put("")
        self.wait_completion.put("NoWait")


def _steps(step_list):
    defn = OrderedDict()
    for step in step_list:
        step_number = int(step[4:])
        defn[step] = (sseqRecordStep, "", {"step": step_number})
    return defn


class SseqRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS synApps sseq record support in ophyd

    .. index:: Ophyd Device; synApps SseqRecord

    .. autosummary::

        ~abort
        ~reset

    :see: https://htmlpreview.github.io/?https://raw.githubusercontent.com/epics-modules/calc/R3-6-1/documentation/sseqRecord.html
    """

    precision = Cpt(EpicsSignal, ".PREC", kind="config")
    busy = Cpt(EpicsSignalRO, ".PREC", kind="config")
    _abort = Cpt(EpicsSignal, ".ABORT", kind="omitted")

    selection_link = Cpt(EpicsSignal, ".SELL", kind="config")
    selection_mask = Cpt(EpicsSignal, ".SELM", kind="config")
    selection_number = Cpt(EpicsSignal, ".SELN", kind="config")

    steps = DDC(_steps(STEP_LIST))

    def abort(self):
        """
        .ABORT is a push button.  Send a 1 to the PV to "push" it.

        Push this button without a timeout from the .put() method.
        """
        self._abort.put(1, use_complete=False, force=True)

    def reset(self):
        """set all fields to default values"""
        self.scanning_rate.put("Passive")
        self.description.put(self.description.pvname.split(".")[0])
        self.forward_link.put("")
        self.precision.put(5)
        self.selection_link.put("")
        self.selection_mask.put("All")
        self.selection_number.put(1)
        for ch in self.steps.component_names:
            step = getattr(self.steps, ch)
            if isinstance(step, sseqRecordStep):
                step.reset()
        self.hints["fields"] = ["steps_%s" % c for c in self.steps.component_names]
        self.read_attrs = ["steps.%s" % c for c in STEP_LIST]


class UserStringSequenceN(EpicsSynAppsRecordEnableMixin, SseqRecord):
    """Single instance of the userStringSeqN database."""


class UserStringSequenceDevice(Device):
    """
    EPICS synApps XXX IOC setup of userStringSeqs: ``$(P):userStringSeq$(N)``

    Note: This will connect more than 1,000 EpicsSignal objects!

    .. index:: Ophyd Device; synApps UserStringSequenceDevice

    .. autosummary::

        ~reset
    """

    enable = Cpt(EpicsSignal, "userStringSeqEnable", kind="config")
    sseq1 = Cpt(UserStringSequenceN, "userStringSeq1")
    sseq2 = Cpt(UserStringSequenceN, "userStringSeq2")
    sseq3 = Cpt(UserStringSequenceN, "userStringSeq3")
    sseq4 = Cpt(UserStringSequenceN, "userStringSeq4")
    sseq5 = Cpt(UserStringSequenceN, "userStringSeq5")
    sseq6 = Cpt(UserStringSequenceN, "userStringSeq6")
    sseq7 = Cpt(UserStringSequenceN, "userStringSeq7")
    sseq8 = Cpt(UserStringSequenceN, "userStringSeq8")
    sseq9 = Cpt(UserStringSequenceN, "userStringSeq9")
    sseq10 = Cpt(UserStringSequenceN, "userStringSeq10")

    def reset(self):  # lgtm [py/similar-function]
        """set all fields to default values"""
        for c in self.component_names:
            if not c.startswith("sseq"):
                continue
            getattr(self, c).reset()
        self.read_attrs = self.component_names


class EditStringSequence(Device):
    """
    EPICS synApps sseq support to quickly re-arrange steps.

    See the ``editSseq_more`` GUI screen for assistance.
    """
    record_name = Cpt(EpicsSignal, "ES:recordName", kind="config")
    command = Cpt(EpicsSignal, "ES:command", kind="config")
    message_acknowledge = Cpt(EpicsSignal, "ES:OperAck", kind="config")
    message = Cpt(EpicsSignalRO, "ES:message", kind="normal")
    alert = Cpt(EpicsSignalRO, "ES:Alert", kind="normal")
    debug = Cpt(EpicsSignal, "ES:Debug", kind="config")

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

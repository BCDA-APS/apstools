"""
Ophyd support for the EPICS synApps sscan record

see:  https://epics.anl.gov/bcda/synApps/sscan/SscanRecord.html

EXAMPLE::

    import apstools.synApps
    scans = apstools.synApps.SscanDevice("xxx:", name="scans")
    scans.select_channels()     # only the channels configured in EPICS


Public Structures

.. autosummary::

    ~SscanRecord
    ~SscanDevice

Private Structures

.. autosummary::

    ~sscanPositioner
    ~sscanDetector
    ~sscanTrigger

"""

from collections import OrderedDict

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FC
from ophyd.status import DeviceStatus

from .. import utils as APS_utils
from typing import Any, Type, Union


class sscanPositioner(Device):
    """
    positioner of an EPICS sscan record

    .. index:: Ophyd Device; synApps sscanPositioner

    .. autosummary::

        ~defined_in_EPICS
        ~reset

    """

    readback_pv: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.R{self._ch_num}PV", kind="config")
    readback_value: FC[EpicsSignalRO] = FC(EpicsSignalRO, "{self.prefix}.R{self._ch_num}CV", kind="hinted")
    array: FC[EpicsSignalRO] = FC(
        EpicsSignalRO,
        "{self.prefix}.P{self._ch_num}CA",
        kind="normal",  # TODO: which kind here?
    )
    setpoint_pv: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}PV", kind="config")
    setpoint_value: FC[EpicsSignalRO] = FC(EpicsSignalRO, "{self.prefix}.P{self._ch_num}DV", kind="normal")
    start: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}SP", kind="config")
    center: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}CP", kind="config")
    end: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}EP", kind="config")
    step_size: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}SI", kind="config")
    width: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}WD", kind="config")
    abs_rel: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}AR", kind="config")
    mode: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.P{self._ch_num}SM", kind="config")
    units: FC[EpicsSignalRO] = FC(EpicsSignalRO, "{self.prefix}.P{self._ch_num}EU", kind="config")

    def __init__(self, prefix: str, num: Union[int, str], **kwargs: Any) -> None:
        self._ch_num = num
        super().__init__(prefix, **kwargs)

    def reset(self) -> None:
        """set all fields to default values"""
        self.readback_pv.put("")
        self.setpoint_pv.put("")
        self.start.put(0)
        self.center.put(0)
        self.end.put(0)
        self.step_size.put(0)
        self.width.put(0)
        self.abs_rel.put("ABSOLUTE")
        self.mode.put("LINEAR")

    @property
    def defined_in_EPICS(self) -> bool:
        """True if defined in EPICS"""
        return len(self.setpoint_pv.get().strip()) > 0


class sscanDetector(Device):
    """
    detector of an EPICS sscan record

    .. index:: Ophyd Device; synApps sscanDetector

    .. autosummary::

        ~defined_in_EPICS
        ~reset

    """

    input_pv: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.D{self._ch_num}PV", kind="config")
    current_value: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.D{self._ch_num}CV", kind="hinted")
    array: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.D{self._ch_num}CA", kind="omitted")

    def __init__(self, prefix: str, num: Union[int, str], **kwargs: Any) -> None:
        self._ch_num = num
        super().__init__(prefix, **kwargs)

    def reset(self) -> None:
        """set all fields to default values"""
        self.input_pv.put("")

    @property
    def defined_in_EPICS(self) -> bool:
        """True if defined in EPICS"""
        return len(self.input_pv.get().strip()) > 0


class sscanTrigger(Device):
    """
    detector trigger of an EPICS sscan record

    .. index:: Ophyd Device; synApps sscanTrigger

    .. autosummary::

        ~reset
    """

    trigger_pv: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.T{self._ch_num}PV", kind="config")
    trigger_value: FC[EpicsSignal] = FC(EpicsSignal, "{self.prefix}.T{self._ch_num}CD", kind="config")

    def __init__(self, prefix: str, num: Union[int, str], **kwargs: Any) -> None:
        self._ch_num = num
        super().__init__(prefix, **kwargs)

    def reset(self) -> None:
        """set all fields to default values"""
        self.trigger_pv.put("")
        self.trigger_value.put(1)

    @property
    def defined_in_EPICS(self) -> bool:
        """True if defined in EPICS"""
        return len(self.trigger_pv.get().strip()) > 0


def _sscan_positioners(channel_list: list[str]) -> OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]]:
    defn: OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]] = OrderedDict()
    for chan in channel_list:
        attr = "p{}".format(chan)
        defn[attr] = (sscanPositioner, "", {"num": chan})
    return defn


def _sscan_detectors(channel_list: list[str]) -> OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]]:
    defn: OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]] = OrderedDict()
    for chan in channel_list:
        attr = "d{}".format(chan)
        defn[attr] = (sscanDetector, "", {"num": chan})
    return defn


def _sscan_triggers(channel_list: list[str]) -> OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]]:
    defn: OrderedDict[str, tuple[Type[Device], str, dict[str, Any]]] = OrderedDict()
    for chan in channel_list:
        attr = "t{}".format(chan)
        defn[attr] = (sscanTrigger, "", {"num": chan})
    return defn


class SscanRecord(Device):
    """
    EPICS synApps sscan record: used as ``$(P):scan(N)``

    .. index:: Ophyd Device; synApps SscanRecord

    .. autosummary::

        ~defined_in_EPICS
        ~reset
        ~select_channels

    """

    desc: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".DESC", kind="config")
    scan_phase: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".FAZE", kind="config")
    data_state: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".DSTATE", kind="config")
    data_ready: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".DATA", kind="config")
    scan_busy: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".BUSY", kind="config")
    alert_flag: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".ALRT", kind="config")
    alert_message: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".SMSG", kind="config")
    number_points: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".NPTS", kind="config")
    maximum_number_points: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".MPTS", kind="config")
    current_point: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".CPT", kind="normal")
    pasm: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".PASM", kind="config")
    execute_scan: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".EXSC", kind="omitted")
    bspv: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".BSPV", kind="config")
    bscd: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".BSCD", kind="omitted")
    bswait: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".BSWAIT", kind="omitted")
    cmnd: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".CMND", kind="omitted")
    detector_delay: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".DDLY", kind="config")
    positioner_delay: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".PDLY", kind="config")
    reference_detector: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".REFD", kind="config")
    wait: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".WAIT", kind="config")
    wcnt: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, ".WCNT", kind="config")
    awct: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".AWCT", kind="config")
    acqt: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".ACQT", kind="config")
    acqm: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".ACQM", kind="config")
    atime: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".ATIME", kind="config")
    copyto: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".COPYTO", kind="config")
    a1pv: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".A1PV", kind="config")
    a1nv: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".A1NV", kind="config")
    a1cd: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".A1CD", kind="config")
    aspv: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".ASPV", kind="config")
    ascd: Cpt[EpicsSignal] = Cpt(EpicsSignal, ".ASCD", kind="config")

    positioners: DDC = DDC(_sscan_positioners("1 2 3 4".split()))
    detectors: DDC = DDC(_sscan_detectors(APS_utils.itemizer("%02d", range(1, 71))))
    triggers: DDC = DDC(_sscan_triggers("1 2 3 4".split()))

    def set(self, value: int, **kwargs: Any) -> Union[DeviceStatus, None]:
        """interface to use bps.mv()"""
        if value != 1:
            return

        working_status: DeviceStatus = DeviceStatus(self)
        started: bool = False

        def execute_scan_cb(value: Any, timestamp: Any, **kwargs: Any) -> None:
            conv_value = int(value)
            if started and conv_value == 0:
                working_status._finished()

        self.execute_scan.subscribe(execute_scan_cb)
        self.execute_scan.set(1)
        started = True
        return working_status

    def reset(self) -> None:
        """set all fields to default values"""
        self.desc.put(self.desc.pvname.split(".")[0])
        self.number_points.put(1000)
        for part in (self.positioners, self.detectors, self.triggers):
            for ch_name in part.component_names:
                channel = getattr(part, ch_name)
                channel.reset()
        self.a1pv.put("")
        self.acqm.put("NORMAL")
        if self.name.find("scanH") > 0:
            self.acqt.put("1D ARRAY")
        else:
            self.acqt.put("SCALAR")
        self.aspv.put("")
        self.bspv.put("")
        self.pasm.put("STAY")
        self.bswait.put("Wait")
        self.a1cd.put(1)
        self.ascd.put(1)
        self.bscd.put(1)
        self.reference_detector.put(1)
        self.atime.put(0)
        self.awct.put(0)
        self.copyto.put(0)
        self.detector_delay.put(0)
        self.positioner_delay.put(0)
        while self.wcnt.get() > 0:
            self.wait.put(0)

    def select_channels(self) -> None:
        """
        Select channels that are configured in EPICS
        """
        for part in (self.positioners, self.detectors, self.triggers):
            channel_names: list[str] = []  # part.get_configured_channels()
            # fmt: off
            channel_names = [
                ch
                for ch in part.component_names
                if getattr(part, ch).defined_in_EPICS
            ]
            # fmt: on

            part.configuration_attrs = channel_names
            part.read_attrs = channel_names
            part.kind = "normal"

    @property
    def defined_in_EPICS(self) -> bool:
        """True if will be used in EPICS"""
        self.select_channels()
        channels: int = len(self.positioners.read_attrs)
        channels += len(self.detectors.read_attrs)
        # channels += len(self.triggers.read_attrs)
        return channels > 0


class SscanDevice(Device):
    """
    EPICS synApps XXX IOC setup of sscan records: ``$(P):scan$(N)``

    .. index:: Ophyd Device; synApps SscanDevice

    .. autosummary::

        ~reset
        ~select_channels

    """

    scan_dimension: Cpt[EpicsSignalRO] = Cpt(EpicsSignalRO, "ScanDim", kind="config")
    scan_pause: Cpt[EpicsSignal] = Cpt(EpicsSignal, "scanPause", kind="omitted")
    abort_scans: Cpt[EpicsSignal] = Cpt(EpicsSignal, "AbortScans", kind="omitted")
    scan1: Cpt[SscanRecord] = Cpt(SscanRecord, "scan1")
    scan2: Cpt[SscanRecord] = Cpt(SscanRecord, "scan2")
    scan3: Cpt[SscanRecord] = Cpt(SscanRecord, "scan3")
    scan4: Cpt[SscanRecord] = Cpt(SscanRecord, "scan4")
    scanH: Cpt[SscanRecord] = Cpt(SscanRecord, "scanH")
    resume_delay: Cpt[EpicsSignal] = Cpt(EpicsSignal, "scanResumeSEQ.DLY1", kind="config")

    def reset(self) -> None:
        """set all fields to default values"""
        for chnum in "1 2 3 4 H".split():
            getattr(self, "scan" + chnum).reset()

    def select_channels(self) -> None:
        """
        Select only the scans that are configured in EPICS
        """
        scans: list[str] = ["scan" + ch for ch in "1 2 3 4 H".split()]
        attrs: list[str] = []
        for nm in self.component_names:
            if nm in scans and not getattr(self, nm).defined_in_EPICS:
                continue
            attrs.append(nm)
        self.read_attrs = attrs


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

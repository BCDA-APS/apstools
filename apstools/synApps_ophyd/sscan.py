
"""
Ophyd support for the EPICS synApps sscan record

EXAMPLE

    import apstools.synApps_ophyd
    scans = apstools.synApps_ophyd.sscanDevice("xxx:", name="scans")


Public Structures

.. autosummary::
   
    ~sscanRecord  
    ~sscanDevice

Private Structures

.. autosummary::
   
    ~sscanPositioner  
    ~sscanDetector  
    ~sscanTrigger

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd.status import DeviceStatus
from ophyd.ophydobj import Kind
from builtins import getattr


__all__ = """
    sscanRecord  
    sscanDevice
    """.split()


class sscanPositioner(Device):
    """positioner of an EPICS sscan record"""
    
    readback_pv = FC(EpicsSignal, '{self.prefix}.R{self._ch_num}PV')
    readback_value = FC(EpicsSignalRO, '{self.prefix}.R{self._ch_num}CV')
    array = FC(EpicsSignalRO, '{self.prefix}.P{self._ch_num}CA', kind=Kind.omitted)
    setpoint_pv = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}PV')
    setpoint_value = FC(EpicsSignalRO, '{self.prefix}.P{self._ch_num}DV')
    start = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SP')
    center = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}CP')
    end = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}EP')
    step_size = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SI')
    width = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}WD')
    abs_rel = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}AR')
    mode = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SM')
    units = FC(EpicsSignalRO, '{self.prefix}.P{self._ch_num}EU')

    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
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
    
    def get_configured_channels(self):
        """return list of all channels configured in EPICS"""
        channel_names = []
        for ch in self.component_names:
            if len(self.setpoint_pv.value.strip()) > 0:
                if ch not in channel_names:
                    channel_names.append(ch)
        return channel_names


class sscanDetector(Device):
    """detector of an EPICS sscan record"""
    
    input_pv = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}PV')
    current_value = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}CV')
    array = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}CA', kind=Kind.omitted)
    
    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
    
    def get_configured_channels(self):
        """return list of all channels configured in EPICS"""
        channel_names = []
        for ch in self.component_names:
            if len(self.input_pv.value.strip()) > 0:
                if ch not in channel_names:
                    channel_names.append(ch)
        return channel_names


class sscanTrigger(Device):
    """detector trigger of an EPICS sscan record"""
    
    trigger_pv = FC(EpicsSignal, '{self.prefix}.T{self._ch_num}PV')
    trigger_value = FC(EpicsSignal, '{self.prefix}.T{self._ch_num}CD')

    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
        """set all fields to default values"""
        self.trigger_pv.put("")
        self.trigger_value.put(1)
    
    def get_configured_channels(self):
        """return list of all channels configured in EPICS"""
        channel_names = []
        for ch in self.component_names:
            if len(self.trigger_pv.value.strip()) > 0:
                if ch not in channel_names:
                    channel_names.append(ch)
        return channel_names


def _sscan_positioners(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        attr = 'p{}'.format(chan)
        defn[attr] = (sscanPositioner, '', {'num': chan})
    return defn


def _sscan_detectors(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        attr = 'd{}'.format(chan)
        defn[attr] = (sscanDetector, '', {'num': chan})
    return defn


def _sscan_triggers(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        attr = 't{}'.format(chan)
        defn[attr] = (sscanTrigger, '', {'num': chan})
    return defn


class sscanRecord(Device):
    """EPICS synApps sscan record: used as $(P):scan(N)"""
    
    desc = Cpt(EpicsSignal, '.DESC')
    faze = Cpt(EpicsSignalRO, '.FAZE')
    data_state = Cpt(EpicsSignalRO, '.DSTATE')
    npts = Cpt(EpicsSignal, '.NPTS')
    cpt = Cpt(EpicsSignalRO, '.CPT')
    pasm = Cpt(EpicsSignal, '.PASM')
    exsc = Cpt(EpicsSignal, '.EXSC')
    bspv = Cpt(EpicsSignal, '.BSPV')
    bscd = Cpt(EpicsSignal, '.BSCD')
    bswait = Cpt(EpicsSignal, '.BSWAIT')
    cmnd = Cpt(EpicsSignal, '.CMND')
    ddly = Cpt(EpicsSignal, '.DDLY')
    pdly = Cpt(EpicsSignal, '.PDLY')
    refd = Cpt(EpicsSignal, '.REFD')
    wait = Cpt(EpicsSignal, '.WAIT')
    wcnt = Cpt(EpicsSignalRO, '.WCNT')
    awct = Cpt(EpicsSignal, '.AWCT')
    acqt = Cpt(EpicsSignal, '.ACQT')
    acqm = Cpt(EpicsSignal, '.ACQM')
    atime = Cpt(EpicsSignal, '.ATIME')
    copyto = Cpt(EpicsSignal, '.COPYTO')
    a1pv = Cpt(EpicsSignal, '.A1PV')
    a1cd = Cpt(EpicsSignal, '.A1CD')
    aspv = Cpt(EpicsSignal, '.ASPV')
    ascd = Cpt(EpicsSignal, '.ASCD')

    positioners = DDC(
        _sscan_positioners(
            "1 2 3 4".split()
        )
    )
    detectors = DDC(
        _sscan_detectors(
            ["%02d" % k for k in range(1,71)]
        )
    )
    triggers = DDC(
        _sscan_triggers(
            "1 2 3 4".split()
        )
    )

    def set(self, value, **kwargs):
        """interface to use bps.mv()"""
        if value != 1:
            return

        working_status = DeviceStatus(self)
        started = False

        def exsc_cb(value, timestamp, **kwargs):
            value = int(value)
            if started and value == 0:
                working_status._finished()
        
        self.exsc.subscribe(exsc_cb)
        self.exsc.set(1)
        started = True
        return working_status
    
    def reset(self):
        """set all fields to default values"""
        self.desc.put(self.desc.pvname.split(".")[0])
        self.npts.put(1000)
        for part in (self.positioners, self.detectors, self.triggers):
            for ch_name in part.read_attrs:
                channel = part.__getattr__(ch_name)
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
        self.refd.put(1)
        self.atime.put(0)
        self.awct.put(0)
        self.copyto.put(0)
        self.ddly.put(0)
        self.pdly.put(0)
        while self.wcnt.get() > 0:
            self.wait.put(0)
    
    def select_channels(self):
        """
        Select channels that are configured in EPICS
        """
        for part in (self.positioners, self.detectors, self.triggers):
            channel_names = part.get_configured_channels()

            attrs = []
            for ch in channel_names:
                attrs.append(ch)
                for attr in part.component_names:
                    attrs.append(ch + "." + attr)
    
            part.configuration_attrs = channel_names
            part.read_attrs = attrs
            part.kind = Kind.normal
            # TODO: (pattern from ScalerCH)
            # for ch in channel_names:
            #     getattr(part, ch).s.kind = Kind.hinted


class sscanDevice(Device):
    """synApps XXX IOC setup of sscan records: $(P):scan$(N)"""

    scan_dimension = Cpt(EpicsSignalRO, 'ScanDim')
    scan_pause = Cpt(EpicsSignal, 'scanPause')
    abort_scans = Cpt(EpicsSignal, 'AbortScans')
    scan1 = Cpt(sscanRecord, 'scan1')
    scan2 = Cpt(sscanRecord, 'scan2')
    scan3 = Cpt(sscanRecord, 'scan3')
    scan4 = Cpt(sscanRecord, 'scan4')
    scanH = Cpt(sscanRecord, 'scanH')
    resume_delay = Cpt(EpicsSignal, 'scanResumeSEQ.DLY1')

    def reset(self):
        """set all fields to default values"""
        for chnum in "1 2 3 4 H".split():
            getattr(self, "scan" + chnum).reset()
    
    def select_channels(self):
        """
        Select channels of each scan that are configured in EPICS
        """
        for chnum in "1 2 3 4 H".split():
            getattr(self, "scan" + chnum).select_channels()

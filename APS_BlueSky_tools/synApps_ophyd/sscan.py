
"""
Ophyd support for the EPICS synApps sscan record

EXAMPLE

    import APS_BlueSky_tools.synApps_ophyd
    scans = APS_BlueSky_tools.synApps_ophyd.sscanDevice("xxx:", name="scans")


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


from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, EpicsSignalRO


__all__ = """
    sscanRecord  
    sscanDevice
    """.split()


class sscanPositioner(Device):
    """positioner of an EPICS sscan record"""
    
    readback_pv = FC(EpicsSignal, '{self.prefix}.R{self._ch_num}PV')
    readback_value = FC(EpicsSignalRO, '{self.prefix}.R{self._ch_num}CV')
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


class sscanDetector(Device):
    """detector of an EPICS sscan record"""
    
    input_pv = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}PV')
    current_value = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}CV')
    
    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")


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
        attr = 'd{}'.format(chan)
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
        self.scan1.reset()
        self.scan2.reset()
        self.scan3.reset()
        self.scan4.reset()
        self.scanH.reset()

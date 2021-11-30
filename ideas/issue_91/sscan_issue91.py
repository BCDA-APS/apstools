
"""
this is a worksheet, not a fully functioning program

https://github.com/BCDA-APS/apstools/issues/91

It probably has errors and stuff that just does not work
If puzzled, look elsewhere for help

I started here:
http://nsls-ii.github.io/bluesky/async.html#flying
"""

import asyncio
from collections import deque, OrderedDict
import numpy as np
import time

P = "gp:"

from apstools.synApps import UserCalcsDevice
from apstools.synApps import SscanDevice
from apstools.synApps import SaveData
from apstools.synApps import setup_lorentzian_swait
from bluesky import RunEngine, plans as bp, preprocessors as bpre
from ophyd import EpicsMotor
from ophyd.scaler import ScalerCH
from ophyd.status import DeviceStatus

RE = RunEngine({})
scaler = ScalerCH(f"{P}scaler1", name="scaler")
scaler.select_channels(None)
m1 = EpicsMotor(f"{P}m1", name="m1")
calcs = UserCalcsDevice(P, name="calcs")
scans = SscanDevice(P, name="scans")
scans.select_channels()
save_data = SaveData(f"{P}saveData_", name="save_data")


# configure saveData for data collection into MDA files:
save_data.file_system.put("/tmp")
save_data.subdirectory.put("saveData")
save_data.base_name.put("sscan1_")
save_data.next_scan_number.put(1)
save_data.comment1.put("testing")
save_data.comment2.put("configured and run from ophyd")

# configure the sscan record for data collection:
scans.reset()       # clear out the weeds

scan = scans.scan1
scan.number_points.put(6)
scan.positioners.p1.setpoint_pv.put(m1.user_setpoint.pvname)
scan.positioners.p1.readback_pv.put(m1.user_readback.pvname)
scan.positioners.p1.start.put(-1)
scan.positioners.p1.end.put(0)
scan.positioner_delay.put(0.0)
scan.detector_delay.put(0.1)
scan.detectors.d01.input_pv.put(scaler.channels.chan03.s.pvname)
scan.detectors.d02.input_pv.put(scaler.channels.chan02.s.pvname)
scan.triggers.t1.trigger_pv.put(scaler.count.pvname)

scans.select_channels()     # finally, reconfigure

setup_lorentzian_swait(calcs.calc2, m1, 2)
noisy_det = calcs.calc2.val


RE(bp.scan([noisy_det], m1, -5, 5, 11))


# ophyd's MockFlyer example
# https://github.com/NSLS-II/ophyd/blob/master/ophyd/sim.py#L546

class MockFlyer:
    """
    Class for mocking a flyscan API implemented with stepper motors.
    """

    def __init__(self, name, detector, motor, start, stop, num, loop=None):
        self.name = name
        self.parent = None
        self._mot = motor
        self._detector = detector
        self._steps = np.linspace(start, stop, num)
        self._data = deque()
        self._completion_status = None
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

    def __setstate__(self, val):
        name, detector, motor, steps = val
        self.name = name
        self.parent = None
        self._mot = motor
        self._detector = detector
        self._steps = steps
        self._completion_status = None
        self.loop = asyncio.get_event_loop()

    def __getstate__(self):
        return (self.name, self._detector, self._mot, self._steps)

    def read_configuration(self):
        return OrderedDict()

    def describe_configuration(self):
        return OrderedDict()

    def describe_collect(self):
        dd = dict()
        dd.update(self._mot.describe())
        dd.update(self._detector.describe())
        return {'stream_name': dd}

    def complete(self):
        if self._completion_status is None:
            raise RuntimeError("No collection in progress")
        return self._completion_status

    def kickoff(self):
        if self._completion_status is not None:
            raise RuntimeError("Already kicked off.")
        self._data = deque()

        self._future = self.loop.run_in_executor(None, self._scan)
        st = DeviceStatus(device=self)
        self._completion_status = st
        self._future.add_done_callback(lambda x: st._finished())
        return st

    def collect(self):
        if self._completion_status is None or not self._completion_status.done:
            raise RuntimeError("No reading until done!")
        self._completion_status = None

        yield from self._data

    def _scan(self):
        "This will be run on a separate thread, started in self.kickoff()"
        time.sleep(.1)
        for p in self._steps:
            stat = self._mot.set(p)
            while True:
                if stat.done:
                    break
                time.sleep(0.01)
            stat = self._detector.trigger()
            while True:
                if stat.done:
                    break
                time.sleep(0.01)

            event = dict()
            event['time'] = time.time()
            event['data'] = dict()
            event['timestamps'] = dict()
            for r in [self._mot, self._detector]:
                d = r.read()
                for k, v in d.items():
                    event['data'][k] = v['value']
                    event['timestamps'][k] = v['timestamp']
            self._data.append(event)

    def stop(self, *, success=False):
        pass


mflyer = MockFlyer('mflyer', noisy_det, m1, -3, 6, 21)

# FIXME: fails, see: https://github.com/NSLS-II/bluesky/issues/1157
RE(bpre.fly_during_wrapper(bp.count([noisy_det], num=5), [mflyer]))      

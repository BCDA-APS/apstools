"""
file: /tmp/kohzu.py
"""

import time

from .. import KohzuSeqCtl_Monochromator
from ...tests import MASTER_TIMEOUT
from bluesky import plan_stubs as bps
from bluesky import RunEngine
from ophyd import Component
from ophyd import EpicsMotor
from ophyd.signal import EpicsSignalBase


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=MASTER_TIMEOUT,
        write_timeout=MASTER_TIMEOUT,
        connection_timeout=MASTER_TIMEOUT,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


class MyKohzu(KohzuSeqCtl_Monochromator):
    """
    Kohzu DCM with controls to enable wavelength controls.

    Wavelength controls are disabled when the physical motors are out of range
    for the choice of wavelength (such as mathematical singularity for energy
    when ``m_theta == 0` on start of the IOC.)
    """

    m_theta = Component(EpicsMotor, "m45")
    m_y = Component(EpicsMotor, "m46")
    m_z = Component(EpicsMotor, "m47")

    def into_control_range(self, p_theta=11, p_y=-18, p_z=90):
        """
        Move the Kohzu motors into range so the wavelength controls will work.

        Written as a bluesky plan so that all motors can be moved
        simultaneously. Return early if the motors are already in range.
        """
        args = []
        if self.m_theta.position < p_theta:
            args += [self.m_theta, p_theta]
            yield from bps.mv(self.m_theta.velocity, 5)
        if self.m_y.position > p_y:
            args += [self.m_y, p_y]
            yield from bps.mv(self.m_y.velocity, 5)
        if self.m_z.position < p_z:
            args += [self.m_z, p_z]
            yield from bps.mv(self.m_z.velocity, 5)
        if (len(args) == 0):
            # all motors in range, no work to do, MUST yield something
            yield from bps.null()
            return
        yield from bps.mv(*args)
        yield from bps.sleep(1)  # allow IOC to react
        yield from bps.mv(self.operator_acknowledge, 1)

    def stop(self):
        self.m_theta.stop()
        self.m_y.stop()
        self.m_z.stop()


def test_dcm():
    dcm = MyKohzu("gp:", name="dcm")
    assert dcm is not None
    assert dcm.energy.name == "dcm_energy"
    dcm.wait_for_connection()

    RE = RunEngine({})
    RE(dcm.into_control_range())
    assert dcm.energy.position > 0
    assert round(dcm.m_theta.position, 2) >= 2
    assert round(dcm.m_y.position, 2) <= -15
    assert round(dcm.m_z.position, 2) >= 90

    delay = 0.1
    time.sleep(delay)

    dcm.mode.put("Auto")
    time.sleep(delay)
    assert dcm.mode.get() == "Auto"

    dcm.energy.move(10.2)
    assert round(dcm.energy.setpoint.get(), 7) == 10.2
    assert round(dcm.energy.position, 1) == 10.2

    dcm.energy.move(10.2)  # send it to the same place
    assert round(dcm.energy.position, 1) == 10.2

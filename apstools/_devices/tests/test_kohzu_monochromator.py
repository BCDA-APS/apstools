"""
file: /tmp/kohzu.py
"""

import logging
import time

from .. import KohzuSeqCtl_Monochromator
from bluesky import plan_stubs as bps
from bluesky import RunEngine
from ophyd import Component
from ophyd import EpicsMotor
from ophyd import EpicsSignal


class MyKohzu(KohzuSeqCtl_Monochromator):
    m_theta = Component(EpicsMotor, "m45")
    m_y = Component(EpicsMotor, "m46")
    m_z = Component(EpicsMotor, "m47")

    def into_control_range(self, p_theta=2, p_y=-15, p_z=90):
        """
        Move the Kohzu motors into range so the energy controls will work.
        """
        yield from bps.mv(
            self.m_theta, p_theta,
            self.m_y, p_y,
            self.m_z, p_z,
        )
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
    assert round(dcm.m_theta.position, 2) == 2
    assert round(dcm.m_y.position, 2) == -15
    assert round(dcm.m_z.position, 2) == 90

    delay = 0.1
    time.sleep(delay)

    dcm.mode.put("Auto")
    assert dcm.mode.get() == "Auto"
    time.sleep(delay)

    dcm.energy.move(10.2)
    assert round(dcm.energy.setpoint.get(), 7) == 10.2
    assert round(dcm.energy.position, 1) == 10.2

    dcm.energy.move(10.2)  # send it to the same place
    assert round(dcm.energy.position, 1) == 10.2

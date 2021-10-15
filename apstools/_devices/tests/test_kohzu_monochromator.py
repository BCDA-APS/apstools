"""
file: /tmp/kohzu.py
"""

import time

from .. import KohzuSeqCtl_Monochromator
from bluesky import plan_stubs as bps
from bluesky import RunEngine
from ophyd import Component
from ophyd import EpicsMotor
from ophyd.signal import EpicsSignalBase


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True, timeout=60, write_timeout=60, connection_timeout=60,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


class MyKohzu(KohzuSeqCtl_Monochromator):
    m_theta = Component(EpicsMotor, "m45")
    m_y = Component(EpicsMotor, "m46")
    m_z = Component(EpicsMotor, "m47")

    def into_control_range(self, p_theta=2, p_y=-15, p_z=90):
        """
        Move the Kohzu motors into range so the energy controls will work.

        Written as a bluesky plan so that all motors can be moved simultaneously.
        Return early if the motors are already in range.
        """
        if (
            self.m_theta.position >= p_theta
            and self.m_y.position <= p_y
            and self.m_z.position >= p_z
        ):
            # all motors in range, no work to do, MUST yield something
            yield from bps.null()
            return
        # fmt: off
        yield from bps.mv(
            self.m_theta, p_theta,
            self.m_y, p_y,
            self.m_z, p_z,
        )
        # fmt: on
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

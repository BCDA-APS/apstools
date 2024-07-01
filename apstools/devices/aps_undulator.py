"""
APS undulators
++++++++++++++

.. autosummary::

   ~PlanarUndulator
"""

import logging
from enum import IntEnum

from ophyd import Component
from ophyd import DerivedSignal
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import PVPositioner


logger = logging.getLogger(__name__)


class DoneStatus(IntEnum):
    MOVING = 0
    DONE = 1


class BusyStatus(IntEnum):
    DONE = 0
    BUSY = 1


class MotorDriveStatus(IntEnum):
    NOT_READY = 0
    READY_TO_MOVE = 1


class UndulatorPositioner(PVPositioner):
    """A positioner for any of the gap control parameters.

    Communicates with the parent (presumably the undulator device) to
    start and stop the device.

    """

    setpoint = Component(EpicsSignal, "SetC.VAL")
    readback = Component(EpicsSignalRO, "M.VAL")

    actuate = Component(DerivedSignal, derived_from="parent.start_button", kind="omitted")
    stop_signal = Component(DerivedSignal, derived_from="parent.stop_button", kind="omitted")
    done = Component(DerivedSignal, derived_from="parent.done", kind="omitted")
    done_value = DoneStatus.DONE


class PlanarUndulator(Device):
    """APS Planar Undulator.

    .. index:: Ophyd Device; PlanarUndulator

    The signals *busy* and *done* convey complementary
    information. *busy* comes from the IOC, while *done* comes
    directly from the controller.

    EXAMPLE::

        undulator = PlanarUndulator("S25ID:USID:", name="undulator")

    """

    # X-ray spectrum parameters
    energy = Component(UndulatorPositioner, "Energy")
    energy_taper = Component(UndulatorPositioner, "TaperEnergy")
    gap = Component(UndulatorPositioner, "Gap")
    gap_taper = Component(UndulatorPositioner, "TaperGap")
    harmonic_value = Component(EpicsSignal, "HarmonicValueC", kind="config")
    total_power = Component(EpicsSignalRO, "TotalPowerM.VAL", kind="config")
    # Signals for moving the undulator
    start_button = Component(EpicsSignal, "StartC.VAL", put_complete=True, kind="omitted")
    stop_button = Component(EpicsSignal, "StopC.VAL", kind="omitted")
    busy = Component(EpicsSignalRO, "BusyM.VAL", kind="omitted")
    done = Component(EpicsSignalRO, "BusyDeviceM.VAL", kind="omitted")
    motor_drive_status = Component(EpicsSignalRO, "MotorDriveStatusM.VAL", kind="omitted")
    # Miscellaneous control signals
    gap_deadband = Component(EpicsSignal, "DeadbandGapC", kind="config")
    device_limit = Component(EpicsSignal, "DeviceLimitM.VAL", kind="config")
    access_mode = Component(EpicsSignalRO, "AccessSecurityC", kind="omitted")
    message1 = Component(EpicsSignalRO, "Message1M.VAL", kind="omitted")
    message2 = Component(EpicsSignalRO, "Message2M.VAL", kind="omitted")
    device = Component(EpicsSignalRO, "DeviceM", kind="config")
    magnet = Component(EpicsSignalRO, "DeviceMagnetM", kind="config")
    location = Component(EpicsSignalRO, "LocationM", kind="config")
    version_plc = Component(EpicsSignalRO, "PLCVersionM.VAL", kind="config")
    version_hpmu = Component(EpicsSignalRO, "HPMUVersionM.VAL", kind="config")


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
APS undulator
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsUndulator
   ~ApsUndulatorDual
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import Signal

from .tracking_signal import TrackingSignal

import logging
from enum import IntEnum

from ophyd import Component as Cpt
from ophyd import DerivedSignal, Device, EpicsSignal, EpicsSignalRO, PVPositioner

log = logging.getLogger(__name__)


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
    setpoint = Cpt(EpicsSignal, "SetC.VAL")
    readback = Cpt(EpicsSignalRO, "M.VAL")

    actuate = Cpt(DerivedSignal, derived_from="parent.start_button", kind="omitted")
    stop_signal = Cpt(DerivedSignal, derived_from="parent.stop_button", kind="omitted")
    done = Cpt(DerivedSignal, derived_from="parent.done", kind="omitted")
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
    energy = Cpt(UndulatorPositioner, "Energy")
    energy_taper = Cpt(UndulatorPositioner, "TaperEnergy")
    gap = Cpt(UndulatorPositioner, "Gap")
    gap_taper = Cpt(UndulatorPositioner, "TaperGap")
    harmonic_value = Cpt(EpicsSignal, "HarmonicValueC", kind="config")
    total_power = Cpt(EpicsSignalRO, "TotalPowerM.VAL", kind="config")
    # Signals for moving the undulator
    start_button = Cpt(EpicsSignal, "StartC.VAL", put_complete=True, kind="omitted")
    stop_button = Cpt(EpicsSignal, "StopC.VAL", kind="omitted")
    busy = Cpt(EpicsSignalRO, "BusyM.VAL", kind="omitted")
    done = Cpt(EpicsSignalRO, "BusyDeviceM.VAL", kind="omitted")
    motor_drive_status = Cpt(EpicsSignalRO, "MotorDriveStatusM.VAL", kind="omitted")
    # Miscellaneous control signals
    gap_deadband = Cpt(EpicsSignal, "DeadbandGapC", kind="config")
    device_limit = Cpt(EpicsSignal, "DeviceLimitM.VAL", kind="config")
    access_mode = Cpt(EpicsSignalRO, "AccessSecurityC", kind="omitted")
    message1 = Cpt(EpicsSignalRO, "Message1M.VAL", kind="omitted")
    message2 = Cpt(EpicsSignalRO, "Message2M.VAL", kind="omitted")
    device = Cpt(EpicsSignalRO, "DeviceM", kind="config")
    magnet = Cpt(EpicsSignalRO, "DeviceMagnetM", kind="config")
    location = Cpt(EpicsSignalRO, "LocationM", kind="config")
    version_plc = Cpt(EpicsSignalRO, "PLCVersionM.VAL", kind="config")
    version_hpmu = Cpt(EpicsSignalRO, "HPMUVersionM.VAL", kind="config")


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

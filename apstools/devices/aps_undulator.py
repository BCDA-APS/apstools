"""
APS undulators (Insertion Devices)
++++++++++++++++++++++++++++++++++

.. autosummary::

   ~PlanarUndulator
   ~Revolver_Undulator
   ~STI_Undulator
   ~Undulator2M
   ~Undulator4M

.. note:: The ``ApsUndulator`` and ``ApsUndulatorDual`` device support
    classes have been removed.  These devices are not used in the APS-U era.
"""

import logging

from ophyd import Component
from ophyd import DerivedSignal
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import PVPositioner


logger = logging.getLogger(__name__)

POSITIONER_DONE = 1


class UndulatorPositioner(PVPositioner):
    """A positioner for any of the gap control parameters.

    Communicates with the parent (presumably the undulator device) to
    start and stop the device.

    .. autosummary::

        ~setpoint
        ~readback
        ~actuate
        ~stop_signal
        ~done
        ~done_value
    """

    setpoint = Component(EpicsSignal, "SetC.VAL")
    readback = Component(EpicsSignalRO, "M.VAL")

    actuate = Component(DerivedSignal, derived_from="parent.start_button", kind="omitted")
    stop_signal = Component(DerivedSignal, derived_from="parent.stop_button", kind="omitted")
    done = Component(DerivedSignal, derived_from="parent.done", kind="omitted")
    done_value = POSITIONER_DONE


class ID_Controls_Mixin(Device):
    """Common controls components for insertion devices.

    Works for: Planar & Revolver

    The signals *busy* and *done* convey complementary
    information. *busy* comes from the IOC, while *done* comes
    directly from the controller.

    .. autosummary::

        ~start_button
        ~stop_button
        ~busy
        ~done
        ~motor_drive_status
    """

    # Signals for moving the undulator
    start_button = Component(EpicsSignal, "StartC.VAL", put_complete=True, kind="omitted")
    stop_button = Component(EpicsSignal, "StopC.VAL", kind="omitted")
    busy = Component(EpicsSignalRO, "BusyM.VAL", kind="omitted")
    done = Component(EpicsSignalRO, "BusyDeviceM.VAL", kind="omitted")
    motor_drive_status = Component(EpicsSignalRO, "MotorDriveStatusM.VAL", kind="omitted")


class ID_Misc_Mixin(Device):
    """Common miscellaneous components for insertion devices.

    Works for: Planar & Revolver

    .. autosummary::

        ~gap_deadband
        ~device_limit
        ~access_mode
        ~message1
        ~message2
        ~device
        ~magnet
        ~location
        ~version_plc
        ~version_hpmu
    """

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


class ID_Spectrum_Mixin(Device):
    """Common spectrum components for insertion devices.

    Works for: Planar & Revolver

    .. autosummary::

        ~energy
        ~energy_taper
        ~gap
        ~gap_taper
        ~harmonic_value
        ~total_power
    """

    # X-ray spectrum parameters
    energy = Component(UndulatorPositioner, "Energy")
    energy_taper = Component(UndulatorPositioner, "TaperEnergy")
    gap = Component(UndulatorPositioner, "Gap")
    gap_taper = Component(UndulatorPositioner, "TaperGap")
    harmonic_value = Component(EpicsSignal, "HarmonicValueC", kind="config")
    total_power = Component(EpicsSignalRO, "TotalPowerM.VAL", kind="config")


class PlanarUndulator(ID_Spectrum_Mixin, ID_Controls_Mixin, ID_Misc_Mixin, Device):
    """APS Planar Undulator.

    .. index:: Ophyd Device; PlanarUndulator

    APS Use: 34 devices, including 20ID.

    EXAMPLE::

        undulator = PlanarUndulator("S25ID:USID:", name="undulator")
    """


class Revolver_Undulator(ID_Spectrum_Mixin, ID_Controls_Mixin, ID_Misc_Mixin, Device):
    """APS Revolver Insertion Device.

    .. index:: Ophyd Device; PlanarUndulator

    APS Use: Only 08US, 08DS, 34DS.

    EXAMPLE::

        undulator = Revolver_Undulator("S08ID:USID:", name="undulator")
    """

    # Revolver control signals
    revolver_select = Component(EpicsSignal, "RevolverSelectC.VAL", kind="config")
    status_position1 = Component(EpicsSignalRO, "Position1M.VAL", kind="config")
    status_position2 = Component(EpicsSignalRO, "Position2M.VAL", kind="config")
    status_safe_gap = Component(EpicsSignalRO, "AtSafeGapM.VAL", kind="config")


class STI_Undulator(PlanarUndulator):
    """APS Planar Undulator built by STI Optronics.

    .. index::
        Ophyd Device; PlanarUndulator
        Ophyd Device; STI_Undulator

    APS Use: 13 devices, including 4ID.

    EXAMPLE::

        undulator = STI_Undulator("S04ID:USID:", name="undulator")
    """


class Undulator2M(ID_Spectrum_Mixin, ID_Controls_Mixin, ID_Misc_Mixin, Device):
    """APS 2M Undulator.

    .. index::
        Ophyd Device; PlanarUndulator
        Ophyd Device; Undulator2M

    APS Use: 1ID, downstream.

    EXAMPLE::

        undulator = Undulator2M("S01ID:DSID:", name="undulator")
    """

    # PVs not found
    busy = None
    magnet = None
    version_plc = None
    version_hpmu = None

    done = Component(EpicsSignalRO, "BusyM.VAL", kind="omitted")
    done_value = 0


class Undulator4M(Undulator2M):
    """APS 4M Undulator.

    .. index::
        Ophyd Device; PlanarUndulator
        Ophyd Device; Undulator4M

    APS Use: 11ID, downstream & upstream.

    EXAMPLE::

        undulator = Undulator4M("S11ID:DSID:", name="undulator")
    """

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

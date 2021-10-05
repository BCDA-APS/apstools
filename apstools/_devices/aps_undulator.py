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


class ApsUndulator(Device):
    """
    APS Undulator

    .. index:: Ophyd Device; ApsUndulator

    EXAMPLE::

        undulator = ApsUndulator("ID09ds:", name="undulator")
    """

    energy = Component(
        EpicsSignal, "Energy", write_pv="EnergySet", put_complete=True, kind="hinted",
    )
    energy_taper = Component(
        EpicsSignal, "TaperEnergy", write_pv="TaperEnergySet", kind="config",
    )
    gap = Component(EpicsSignal, "Gap", write_pv="GapSet")
    gap_taper = Component(
        EpicsSignal, "TaperGap", write_pv="TaperGapSet", kind="config"
    )
    start_button = Component(EpicsSignal, "Start", put_complete=True, kind="omitted")
    stop_button = Component(EpicsSignal, "Stop", kind="omitted")
    harmonic_value = Component(EpicsSignal, "HarmonicValue", kind="config")
    gap_deadband = Component(EpicsSignal, "DeadbandGap", kind="config")
    device_limit = Component(EpicsSignal, "DeviceLimit", kind="config")

    access_mode = Component(EpicsSignalRO, "AccessSecurity", kind="omitted")
    device_status = Component(EpicsSignalRO, "Busy", kind="omitted")
    total_power = Component(EpicsSignalRO, "TotalPower", kind="config")
    message1 = Component(EpicsSignalRO, "Message1", kind="omitted")
    message2 = Component(EpicsSignalRO, "Message2", kind="omitted")
    message3 = Component(EpicsSignalRO, "Message3", kind="omitted")
    time_left = Component(EpicsSignalRO, "ShClosedTime", kind="omitted")

    device = Component(EpicsSignalRO, "Device", kind="config")
    location = Component(EpicsSignalRO, "Location", kind="config")
    version = Component(EpicsSignalRO, "Version", kind="config")

    # Useful undulator parameters that are not EPICS PVs.
    energy_deadband = Component(Signal, value=0.0, kind="config")
    energy_backlash = Component(Signal, value=0.0, kind="config")
    energy_offset = Component(Signal, value=0, kind="config")
    tracking = Component(TrackingSignal, value=False, kind="config")


class ApsUndulatorDual(Device):
    """
    APS Undulator with upstream *and* downstream controls

    .. index:: Ophyd Device; ApsUndulatorDual

    EXAMPLE::

        undulator = ApsUndulatorDual("ID09", name="undulator")

    note:: the trailing ``:`` in the PV prefix should be omitted
    """

    upstream = Component(ApsUndulator, "us:")
    downstream = Component(ApsUndulator, "ds:")

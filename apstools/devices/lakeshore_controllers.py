"""
Lakeshore temperature controllers
+++++++++++++++++++++++++++++++++

.. autosummary::

   ~LakeShore336Device
   ~LakeShore340Device

.. not yet implemented
   ~LakeShore330Device
   ~LakeShore331Device
   ~LakeShore335Device
   ~LakeShoreDR93CADevice
"""

# TODO: refactor
#    temperature = Component(PVPositionerSoftDoneWithStop, ...)

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import FormattedComponent
from ophyd import Signal

from ..synApps import AsynRecord
from ..utils import HOUR
from . import PVPositionerSoftDoneWithStop


class LakeShore336_LoopControl(PVPositionerSoftDoneWithStop):
    """
    LakeShore 336 temperature controller -- with heater control.

    The LakeShore 336 accepts up to two heaters.
    """

    # position
    # readback is provided by PVPositionerSoftDoneWithStop

    setpoint = FormattedComponent(EpicsSignalWithRBV, "{prefix}OUT{loop_number}:SP", put_complete=True)

    # configuration
    units = FormattedComponent(EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="config")

    heater = FormattedComponent(EpicsSignalRO, "{prefix}HTR{loop_number}", auto_monitor=True, kind="normal")
    heater_range = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}HTR{loop_number}:Range",
        kind="config",
        auto_monitor=True,
        string=True,
    )

    pid_P = FormattedComponent(EpicsSignalWithRBV, "{prefix}P{loop_number}", kind="config")
    pid_I = FormattedComponent(EpicsSignalWithRBV, "{prefix}I{loop_number}", kind="config")
    pid_D = FormattedComponent(EpicsSignalWithRBV, "{prefix}D{loop_number}", kind="config")

    ramp_rate = FormattedComponent(EpicsSignalWithRBV, "{prefix}RampR{loop_number}", kind="config")
    ramp_on = FormattedComponent(EpicsSignalWithRBV, "{prefix}OnRamp{loop_number}", kind="config")

    loop_name = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="config")
    control = FormattedComponent(EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Cntrl", kind="config")
    manual = FormattedComponent(EpicsSignalWithRBV, "{prefix}OUT{loop_number}:MOUT", kind="config")
    mode = FormattedComponent(EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Mode", kind="config")

    def __init__(self, *args, loop_number=None, timeout=10 * HOUR, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, timeout=timeout, tolerance=0.1, use_target=True, readback_pv=f"IN{loop_number}", **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        else:
            self._settle_time = value

    def pause(self):
        """Change setpoint to current position."""
        self.setpoint.put(self._position)


class LakeShore336_LoopRO(Device):
    """
    LakeShore 336 temperature controller -- Read-only loop (no heaters).
    """

    # Set this to normal because we don't use it.
    readback = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}", kind="normal")
    units = FormattedComponent(EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="omitted")
    loop_name = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="omitted")

    def __init__(self, *args, loop_number=None, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)


class LakeShore336Device(Device):
    """
    LakeShore 336 temperature controller.

    - loop 1: temperature positioner AND heater, PID, & ramp controls
    - loop 2: temperature positioner AND heater, PID, & ramp controls
    - loop 3: temperature positioner
    - loop 4: temperature positioner
    """

    loop1 = FormattedComponent(LakeShore336_LoopControl, "{self.prefix}", loop_number=1)
    loop2 = FormattedComponent(LakeShore336_LoopControl, "{self.prefix}", loop_number=2)
    loop3 = FormattedComponent(LakeShore336_LoopRO, "{self.prefix}", loop_number=3)
    loop4 = FormattedComponent(LakeShore336_LoopRO, "{self.prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    read_all = Component(EpicsSignal, "readAll.PROC", kind="omitted")
    serial = Component(AsynRecord, "serial", kind="omitted")


class LS340_LoopBase(PVPositionerSoftDoneWithStop):
    """Base settings for both sample and control loops."""

    # position
    # readback is provided by PVPositionerSoftDoneWithStop
    # TODO: Polar reports: sometimes the setpoint PV is not updated
    setpoint = FormattedComponent(
        EpicsSignal,
        "{prefix}SP{loop_number}",
        write_pv="{prefix}wr_SP{loop_number}",
        kind="normal",
        put_complete=True,
    )

    # configuration
    units = Component(Signal, value="K", kind="config")

    pid_P = FormattedComponent(
        EpicsSignal,
        "{prefix}P{loop_number}",
        write_pv="{prefix}setPID{loop_number}.AA",
        kind="config",
    )
    pid_I = FormattedComponent(
        EpicsSignal,
        "{prefix}I{loop_number}",
        write_pv="{prefix}setPID{loop_number}.BB",
        kind="config",
    )
    pid_D = FormattedComponent(
        EpicsSignal,
        "{prefix}D{loop_number}",
        write_pv="{prefix}setPID{loop_number}.CC",
        kind="config",
    )

    ramp_rate = FormattedComponent(
        EpicsSignal,
        "{prefix}Ramp{loop_number}",
        write_pv="{prefix}setRamp{loop_number}.BB",
        kind="config",
    )
    ramp_on = FormattedComponent(EpicsSignal, "{prefix}Ramp{loop_number}_on", kind="config")

    def __init__(self, *args, loop_number=None, timeout=10 * HOUR, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, readback_pv="ignore", timeout=timeout, use_target=True, tolerance=0.1, **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        else:
            self._settle_time = value

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def pause(self):
        """Change setpoint to current position."""
        self.setpoint.put(self._position, wait=True)


class LS340_LoopControl(LS340_LoopBase):
    """Control specific"""

    readback = Component(EpicsSignalRO, "Control", kind="normal")
    sensor = Component(EpicsSignal, "Ctl_sel", kind="config")


class LS340_LoopSample(LS340_LoopBase):
    """Sample specific"""

    readback = Component(EpicsSignalRO, "Sample", kind="hinted")
    sensor = Component(EpicsSignal, "Spl_sel", kind="config")


class LakeShore340Device(Device):
    """
    LakeShore 340 temperature controller
    """

    control = FormattedComponent(LS340_LoopControl, "{prefix}", loop_number=1)
    sample = FormattedComponent(LS340_LoopSample, "{prefix}", loop_number=2)

    heater = Component(EpicsSignalRO, "Heater")
    heater_range = Component(EpicsSignal, "Rg_rdbk", write_pv="HeatRg", kind="normal", put_complete=True)

    read_pid = Component(EpicsSignal, "readPID.PROC", kind="omitted")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    serial = Component(AsynRecord, "serial", kind="omitted")


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

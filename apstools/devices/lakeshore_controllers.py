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

from typing import Any, Optional, Union

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

    setpoint: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:SP", put_complete=True
    )

    # configuration
    units: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="config"
    )

    heater: EpicsSignalRO = FormattedComponent(
        EpicsSignalRO, "{prefix}HTR{loop_number}", auto_monitor=True, kind="normal"
    )
    heater_range: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}HTR{loop_number}:Range",
        kind="config",
        auto_monitor=True,
        string=True,
    )

    pid_P: EpicsSignalWithRBV = FormattedComponent(EpicsSignalWithRBV, "{prefix}P{loop_number}", kind="config")
    pid_I: EpicsSignalWithRBV = FormattedComponent(EpicsSignalWithRBV, "{prefix}I{loop_number}", kind="config")
    pid_D: EpicsSignalWithRBV = FormattedComponent(EpicsSignalWithRBV, "{prefix}D{loop_number}", kind="config")

    ramp_rate: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}RampR{loop_number}", kind="config"
    )
    ramp_on: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OnRamp{loop_number}", kind="config"
    )

    loop_name: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="config")
    control: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Cntrl", kind="config"
    )
    manual: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:MOUT", kind="config"
    )
    mode: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Mode", kind="config"
    )

    def __init__(
        self, *args: Any, loop_number: Optional[int] = None, timeout: float = 10 * HOUR, **kwargs: Any
    ) -> None:
        """Initialize LakeShore336_LoopControl."""
        self.loop_number = loop_number
        super().__init__(
            *args, timeout=timeout, tolerance=0.1, use_target=True, readback_pv=f"IN{loop_number}", **kwargs
        )
        self._settle_time = 0

    @property
    def settle_time(self) -> float:
        """Get settle time."""
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value: float) -> None:
        """Set settle time."""
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        else:
            self._settle_time = value

    def pause(self) -> None:
        """Change setpoint to current position."""
        self.setpoint.put(self._position)


class LakeShore336_LoopRO(Device):
    """
    LakeShore 336 temperature controller -- Read-only loop (no heaters).
    """

    # Set this to normal because we don't use it.
    readback: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}", kind="normal")
    units: EpicsSignalWithRBV = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="omitted"
    )
    loop_name: EpicsSignalRO = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="omitted"
    )

    def __init__(self, *args: Any, loop_number: Optional[int] = None, **kwargs: Any) -> None:
        """Initialize LakeShore336_LoopRO."""
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

    loop1: LakeShore336_LoopControl = FormattedComponent(LakeShore336_LoopControl, "{self.prefix}", loop_number=1)
    loop2: LakeShore336_LoopControl = FormattedComponent(LakeShore336_LoopControl, "{self.prefix}", loop_number=2)
    loop3: LakeShore336_LoopRO = FormattedComponent(LakeShore336_LoopRO, "{self.prefix}", loop_number=3)
    loop4: LakeShore336_LoopRO = FormattedComponent(LakeShore336_LoopRO, "{self.prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate: EpicsSignal = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record: EpicsSignal = Component(EpicsSignal, "read.PROC", kind="omitted")

    read_all: EpicsSignal = Component(EpicsSignal, "readAll.PROC", kind="omitted")
    serial: AsynRecord = Component(AsynRecord, "serial", kind="omitted")


class LS340_LoopBase(PVPositionerSoftDoneWithStop):
    """Base settings for both sample and control loops."""

    # position
    # readback is provided by PVPositionerSoftDoneWithStop
    # TODO: Polar reports: sometimes the setpoint PV is not updated
    setpoint: EpicsSignal = FormattedComponent(
        EpicsSignal,
        "{prefix}SP{loop_number}",
        write_pv="{prefix}wr_SP{loop_number}",
        kind="normal",
        put_complete=True,
    )

    # configuration
    units: Signal = Component(Signal, value="K", kind="config")

    pid_P: EpicsSignal = FormattedComponent(
        EpicsSignal,
        "{prefix}P{loop_number}",
        write_pv="{prefix}setPID{loop_number}.AA",
        kind="config",
    )
    pid_I: EpicsSignal = FormattedComponent(
        EpicsSignal,
        "{prefix}I{loop_number}",
        write_pv="{prefix}setPID{loop_number}.BB",
        kind="config",
    )
    pid_D: EpicsSignal = FormattedComponent(
        EpicsSignal,
        "{prefix}D{loop_number}",
        write_pv="{prefix}setPID{loop_number}.CC",
        kind="config",
    )

    ramp_rate: EpicsSignal = FormattedComponent(
        EpicsSignal,
        "{prefix}Ramp{loop_number}",
        write_pv="{prefix}setRamp{loop_number}.BB",
        kind="config",
    )
    ramp_on: EpicsSignal = FormattedComponent(EpicsSignal, "{prefix}Ramp{loop_number}_on", kind="config")

    def __init__(
        self, *args: Any, loop_number: Optional[int] = None, timeout: float = 10 * HOUR, **kwargs: Any
    ) -> None:
        """Initialize LS340_LoopBase."""
        self.loop_number = loop_number
        super().__init__(*args, readback_pv="ignore", timeout=timeout, use_target=True, tolerance=0.1, **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self) -> float:
        """Get settle time."""
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value: float) -> None:
        """Set settle time."""
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        else:
            self._settle_time = value

    @property
    def egu(self) -> str:
        """Get engineering units."""
        return self.units.get(as_string=True)

    def pause(self) -> None:
        """Change setpoint to current position."""
        self.setpoint.put(self._position, wait=True)


class LS340_LoopControl(LS340_LoopBase):
    """Control specific"""

    readback: EpicsSignalRO = Component(EpicsSignalRO, "Control", kind="normal")
    sensor: EpicsSignal = Component(EpicsSignal, "Ctl_sel", kind="config")


class LS340_LoopSample(LS340_LoopBase):
    """Sample specific"""

    readback: EpicsSignalRO = Component(EpicsSignalRO, "Sample", kind="hinted")
    sensor: EpicsSignal = Component(EpicsSignal, "Spl_sel", kind="config")


class LakeShore340Device(Device):
    """
    LakeShore 340 temperature controller
    """

    control: LS340_LoopControl = FormattedComponent(LS340_LoopControl, "{prefix}", loop_number=1)
    sample: LS340_LoopSample = FormattedComponent(LS340_LoopSample, "{prefix}", loop_number=2)

    heater: EpicsSignalRO = Component(EpicsSignalRO, "Heater")
    heater_range: EpicsSignal = Component(
        EpicsSignal, "Rg_rdbk", write_pv="HeatRg", kind="normal", put_complete=True
    )

    read_pid: EpicsSignal = Component(EpicsSignal, "readPID.PROC", kind="omitted")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate: EpicsSignal = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record: EpicsSignal = Component(EpicsSignal, "read.PROC", kind="omitted")

    serial: AsynRecord = Component(AsynRecord, "serial", kind="omitted")


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

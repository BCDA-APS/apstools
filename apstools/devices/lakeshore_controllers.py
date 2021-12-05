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

from . import PVPositionerSoftDoneWithStop
from ..synApps import AsynRecord

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE


class BooleanSignal(Signal):
    """Signal that forces value to be a boolean."""

    def check_value(self, value):
        """
        Check if the value is a boolean.

        raises ``ValueError``
        """
        if not isinstance(value, bool):
            raise ValueError("value can only be True or False.")


class LakeShore336_LoopControl(PVPositionerSoftDoneWithStop):
    """
    LakeShore 336 temperature controller -- with heater control.

    The LakeShore 336 accepts up to two heaters.
    """

    # position
    # FIXME: Resolve this code:
    #    setpoint is the temperature to be reached
    #    readback is the current temperature
    #    XXXXX is the interim setpoint for the PID loop
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}", auto_monitor=True, kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}OUT{loop_number}:SP",
        put_complete=True,
        kind="normal",
    )

    # FIXME:  refactor (per above)
    # Due to ramping the setpoint will change slowly and the readback may catch
    # up even if the motion is not done.
    target = Component(Signal, value=0, kind="omitted")

    # configuration
    units = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="config"
    )

    heater = FormattedComponent(
        EpicsSignalRO, "{prefix}HTR{loop_number}", auto_monitor=True, kind="normal"
    )
    heater_range = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}HTR{loop_number}:Range",
        kind="config",
        auto_monitor=True,
        string=True,
    )

    pid_P = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}P{loop_number}", kind="config"
    )
    pid_I = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}I{loop_number}", kind="config"
    )
    pid_D = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}D{loop_number}", kind="config"
    )

    ramp_rate = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}RampR{loop_number}", kind="config"
    )
    ramp_on = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OnRamp{loop_number}", kind="config"
    )

    loop_name = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="config"
    )
    control = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Cntrl", kind="config"
    )
    manual = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:MOUT", kind="config"
    )
    mode = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OUT{loop_number}:Mode", kind="config"
    )

    auto_heater = Component(BooleanSignal, value=False, kind="config")

    # This must be modified either here, or before using auto_heater.
    _auto_ranges = None

    def __init__(self, *args, loop_number=None, timeout=10 * HOUR, **kwargs):
        self.loop_number = loop_number
        super().__init__(
            *args, timeout=timeout, tolerance=0.1, target_attr="target", **kwargs
        )
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

    def stop(self, *, success=False):
        if success is False:
            self.setpoint.put(self._position)
        super().stop(success=success)

    def pause(self):
        self.setpoint.put(self._position)

    @auto_heater.sub_value
    def _subscribe_auto_heater(self, value=None, **kwargs):
        if value:
            self.setpointRO.subscribe(self._switch_heater, event_type="value")
        else:
            self.setpointRO.clear_subs(self._switch_heater)

    def _switch_heater(self, value=None, **kwargs):
        # TODO: Find a better way to do this, perhaps with an array?
        for _heater_range, _temp_range in self._auto_ranges.items():
            if _temp_range:
                if _temp_range[0] < value <= _temp_range[1]:
                    self.heater_range.put(_heater_range)

    @property
    def auto_ranges(self):
        return self._auto_ranges

    @auto_ranges.setter
    def auto_ranges(self, value):
        if not isinstance(value, dict):
            raise TypeError("auto_ranges must be a dictionary.")

        for _heater_range, _temp_range in value.items():
            if _heater_range not in self.heater_range.enum_strs:
                raise ValueError(
                    "The input dictionary keys must be one of "
                    f"these: {self.heater_range.enum_strs}, but "
                    f"{_heater_range} was entered."
                )

            if _temp_range is not None and len(_temp_range) != 2:
                raise ValueError(
                    f"The value {_temp_range} is invalid! It "
                    "must be either None or an iterable with two "
                    "items."
                )

            self._auto_ranges = value


class LakeShore336_LoopRO(Device):
    """
    LakeShore 336 temperature controller -- Read-only loop (no heaters).
    """

    # Set this to normal because we don't use it.
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}", kind="normal"
    )
    units = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}IN{loop_number}:Units", kind="omitted"
    )
    loop_name = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}:Name_RBV", kind="omitted"
    )

    def __init__(self, *args, loop_number=None, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)


class LakeShore336_LoopBase(PVPositionerSoftDoneWithStop):
    """
    One control loop of the LakeShore 336 temperature controller.

    Each control loop is a separate process controller.

    DEFAULTS:

    - timeout: 10 hours
    - tolerance: 0.1
    """

    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}IN{loop_number}", auto_monitor=True, kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}OUT{loop_number}:SP",
        put_complete=True,
        kind="normal",
    )

    def __init__(self, *args, loop_number=None, timeout=10 * HOUR, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, timeout=timeout, tolerance=0.1, **kwargs)


class LakeShore336_LoopMore(LakeShore336_LoopBase):
    """
    Additional controls for LakeShore 336 loop1 and loop2: heater, pid, & ramp.

    Only used on loops 1 & 2.
    """

    heater = FormattedComponent(
        EpicsSignalRO, "{prefix}HTR{loop_number}", auto_monitor=True, kind="normal"
    )
    heater_range = FormattedComponent(
        EpicsSignalWithRBV,
        "{prefix}HTR{loop_number}:Range",
        kind="config",
        auto_monitor=True,
        string=True,
    )

    pid_P = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}P{loop_number}", kind="config"
    )
    pid_I = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}I{loop_number}", kind="config"
    )
    pid_D = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}D{loop_number}", kind="config"
    )

    ramp_rate = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}RampR{loop_number}", kind="config"
    )
    ramp_on = FormattedComponent(
        EpicsSignalWithRBV, "{prefix}OnRamp{loop_number}", kind="config"
    )


class LakeShore336Device(Device):
    """
    LakeShore 336 temperature controller.

    - loop 1: temperature positioner AND heater, PID, & ramp controls
    - loop 2: temperature positioner AND heater, PID, & ramp controls
    - loop 3: temperature positioner
    - loop 4: temperature positioner
    """

    loop1 = FormattedComponent(LakeShore336_LoopMore, "{self.prefix}", loop_number=1)
    loop2 = FormattedComponent(LakeShore336_LoopMore, "{self.prefix}", loop_number=2)
    loop3 = FormattedComponent(LakeShore336_LoopBase, "{self.prefix}", loop_number=3)
    loop4 = FormattedComponent(LakeShore336_LoopBase, "{self.prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    read_all = Component(EpicsSignal, "readAll.PROC", kind="omitted")
    serial = Component(AsynRecord, "serial", kind="omitted")


class LS340_LoopBase(PVPositionerSoftDoneWithStop):  # TODO: check, check, check
    """ Base settings for both sample and control loops. """

    # position
    readback = Component(Signal, value=0)
    # TODO: Polar reports: sometimes the setpoint PV is not updated
    setpoint = FormattedComponent(
        EpicsSignal,
        "{prefix}SP{loop_number}",
        write_pv="{prefix}wr_SP{loop_number}",
        kind="normal",
        put_complete=True,
    )

    # This is here only because of ramping, because then setpoint will change
    # slowly.
    target = Component(Signal, value=0, kind="omitted")

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
    ramp_on = FormattedComponent(
        EpicsSignal, "{prefix}Ramp{loop_number}_on", kind="config"
    )

    def __init__(self, *args, loop_number=None, timeout=10 * HOUR, **kwargs):
        self.loop_number = loop_number
        super().__init__(
            *args, timeout=timeout, tolerance=0.1, target_attr="target", **kwargs
        )
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

    def stop(self, *, success=False):
        if success is False:
            self.setpoint.put(self._position)
        super().stop(success=success)

    def pause(self):
        self.setpoint.put(self._position, wait=True)


class LS340_LoopControl(LS340_LoopBase):
    """ Control specific """

    readback = Component(EpicsSignalRO, "Control", kind="normal")
    sensor = Component(EpicsSignal, "Ctl_sel", kind="config")


class LS340_LoopSample(LS340_LoopBase):
    """ Sample specific """

    readback = Component(EpicsSignalRO, "Sample", kind="hinted")
    sensor = Component(EpicsSignal, "Spl_sel", kind="config")


class LakeShore340Device(Device):
    """
    LakeShore 340 temperature controller
    """

    control = FormattedComponent(LS340_LoopControl, "{prefix}", loop_number=1)
    sample = FormattedComponent(LS340_LoopSample, "{prefix}", loop_number=2)

    heater = Component(EpicsSignalRO, "Heater")
    heater_range = Component(
        EpicsSignal, "Rg_rdbk", write_pv="HeatRg", kind="normal", put_complete=True
    )

    auto_heater = Component(BooleanSignal, value=False, kind="config")

    read_pid = Component(EpicsSignal, "readPID.PROC", kind="omitted")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    serial = Component(AsynRecord, "serial", kind="omitted")

    # This must be modified either here, or before using auto_heater.
    _auto_ranges = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: I don't know why this has to be done, otherwise it gets hinted.
        self.control.readback.kind = "normal"

    @auto_heater.sub_value
    def _subscribe_auto_heater(self, value=None, **kwargs):
        if value:
            self.control.setpoint.subscribe(self._switch_heater, event_type="value")
        else:
            self.control.setpoint.clear_subs(self._switch_heater)

    def _switch_heater(self, value=None, **kwargs):
        # TODO: Find a better way to do this, perhaps with an array?
        for _heater_range, _temp_range in self._auto_ranges.items():
            if _temp_range:
                if _temp_range[0] < value <= _temp_range[1]:
                    self.heater_range.put(_heater_range)

    @property
    def auto_ranges(self):
        return self._auto_ranges

    @auto_ranges.setter
    def auto_ranges(self, value):
        if not isinstance(value, dict):
            raise TypeError("auto_ranges must be a dictionary.")

        for _heater_range, _temp_range in value.items():
            if _heater_range not in self.heater_range.enum_strs:
                raise ValueError(
                    "The input dictionary keys must be one of "
                    f"these: {self.heater_range.enum_strs}, but "
                    f"{_heater_range} was entered."
                )

            if _temp_range is not None and len(_temp_range) != 2:
                raise ValueError(
                    f"The value {_temp_range} is invalid! It "
                    "must be either None or an iterable with two "
                    "items."
                )

            self._auto_ranges = value

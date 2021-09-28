"""
Mixin classes for Motor Devices
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EpicsMotorDialMixin
   ~EpicsMotorEnableMixin
   ~EpicsMotorLimitsMixin
   ~EpicsMotorRawMixin
   ~EpicsMotorResolutionMixin
   ~EpicsMotorServoMixin
"""

from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import EpicsSignal
from .mixin_base import DeviceMixinBase


class EpicsMotorDialMixin(DeviceMixinBase):
    """
    add motor record's dial coordinate fields to Device

    .. index:: Ophyd Device Mixin; EpicsMotorDialMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorDialMixin

        class myEpicsMotor(EpicsMotorDialMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.dial.read())

    """

    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")


class EpicsMotorEnableMixin(DeviceMixinBase):
    """
    mixin providing access to motor enable/disable

    .. index:: Ophyd Device Mixin; EpicsMotorEnableMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorEnableMixin

        class MyEpicsMotor(EpicsMotorEnableMixin, EpicsMotor): ...

        m1 = MyEpicsMotor('xxx:m1', name='m1')
        print(m1.enabled)

    In a bluesky plan::

        yield from bps.mv(m1.enable_disable, m1.MOTOR_DISABLE)
        # ... other activities
        yield from bps.mv(m1.enable_disable, m1.MOTOR_ENABLE)

    """

    enable_disable = Component(EpicsSignal, "_able", kind="omitted")

    # constants for internal use
    MOTOR_ENABLE = 0
    MOTOR_DISABLE = 1

    @property
    def enabled(self):
        return self.enable_disable.get() in (self.MOTOR_ENABLE, "Enabled")

    def enable_motor(self):
        """BLOCKING call to enable motor axis"""
        self.enable_disable.put(self.MOTOR_ENABLE)

    def disable_motor(self):
        """BLOCKING call to disable motor axis"""
        self.enable_disable.put(self.MOTOR_DISABLE)


class EpicsMotorLimitsMixin(DeviceMixinBase):
    """
    add motor record HLM & LLM fields & compatibility get_lim() and set_lim()

    .. index:: Ophyd Device Mixin; EpicsMotorLimitsMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorLimitsMixin

        class myEpicsMotor(EpicsMotorLimitsMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        lo = m1.get_lim(-1)
        hi = m1.get_lim(1)
        m1.set_lim(-25, -5)
        print(m1.get_lim(-1), m1.get_lim(1))
        m1.set_lim(lo, hi)
    """

    soft_limit_lo = Component(EpicsSignal, ".LLM", kind="omitted")
    soft_limit_hi = Component(EpicsSignal, ".HLM", kind="omitted")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def cb_limit_changed(value, old_value, **kwargs):
            """
            update EpicsSignal object when a limit CA monitor received
            """
            if self.connected and old_value is not None and value != old_value:
                self.user_setpoint._metadata_changed(
                    self.user_setpoint.pvname,
                    self.user_setpoint._read_pv.get_ctrlvars(),
                    from_monitor=True,
                    update=True,
                )

        self.soft_limit_lo.subscribe(cb_limit_changed)
        self.soft_limit_hi.subscribe(cb_limit_changed)

    def get_lim(self, flag):
        """
        Returns the user limit of motor

        * flag > 0: returns high limit
        * flag < 0: returns low limit
        * flag == 0: returns None

        Similar with SPEC command
        """
        if flag > 0:
            return self.soft_limit_hi.get()
        elif flag < 0:
            return self.soft_limit_lo.get()

    def set_lim(self, low, high):
        """
        Sets the low and high limits of motor

        * No action taken if motor is moving.
        * Low limit is set to lesser of (low, high)
        * High limit is set to greater of (low, high)

        Similar with SPEC command
        """
        if not self.moving:
            # update EPICS
            # fmt: off
            yield from bps.mv(
                self.soft_limit_lo, min(low, high),
                self.soft_limit_hi, max(low, high),
            )
            # fmt: on
            # ophyd metadata dictionary will update via CA monitor


class EpicsMotorServoMixin(DeviceMixinBase):
    """
    add motor record's servo loop controls to Device

    .. index:: Ophyd Device Mixin; EpicsMotorServoMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorServoMixin

        class myEpicsMotor(EpicsMotorServoMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.servo.read())
    """

    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)


class EpicsMotorRawMixin(DeviceMixinBase):
    """
    add motor record's raw coordinate fields to Device

    .. index:: Ophyd Device Mixin; EpicsMotorRawMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorRawMixin

        class myEpicsMotor(EpicsMotorRawMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.raw.read())
    """

    raw = Component(EpicsSignal, ".RRBV", write_pv=".RVAL")


class EpicsMotorResolutionMixin(DeviceMixinBase):
    """
    Add motor record's resolution fields to motor.

    .. index:: Ophyd Device Mixin; EpicsMotorResolutionMixin

    Usually, a facility will not provide such high-level
    access to calibration parameters since these are
    associated with fixed parameters of hardware.
    For simulators, it is convenient to provide access
    so that default settings (typically low-resolution)
    from the IOC can be changed as part of the device
    setup in bluesky.

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorResolutionMixin

        class myEpicsMotor(EpicsMotorResolutionMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(f"resolution={m1.resolution.read()}")
        print(f"steps_per_rev={m1.steps_per_rev.read()}")
        print(f"units_per_rev={m1.units_per_rev.read()}")
    """

    resolution = Component(EpicsSignal, ".MRES", kind="omitted")
    steps_per_rev = Component(EpicsSignal, ".SREV", kind="omitted")
    units_per_rev = Component(EpicsSignal, ".UREV", kind="omitted")

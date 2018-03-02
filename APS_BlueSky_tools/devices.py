
"""
(ophyd) Devices that might be useful at the APS using BlueSky

.. autosummary::
   
    ~ApsPssShutter
    ~AxisTunerException
    ~AxisTunerMixin
    ~EpicsMotorDialMixin
    ~EpicsMotorServoMixin
    ~EpicsMotorRawMixin
    ~EpicsMotorDescriptionMixin
    ~EpicsMotorShutter
    ~sscanRecord  
    ~sscanDevice
    ~swaitRecord
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer
    ~userCalcsDevice

Legacy routines

.. autosummary::
   
    ~EpicsMotorWithDial
    ~EpicsMotorWithServo

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
from datetime import datetime
import threading
import time
from .synApps_ophyd import *
from ophyd import Component, Device, DeviceStatus
from ophyd import Signal, EpicsMotor, EpicsSignal
from bluesky.plan_stubs import mv, mvr, abs_set, wait


class ApsPssShutter(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
    
    USAGE:
    
        shutter_a = ApsPssShutter("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        shutter_a.set("open")
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(shutter_a))
        
    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.
    
    Example, add "o" & "x" as aliases for "open" & "close":
    
        shutter_a.valid_open_values.append("o")
        shutter_a.valid_close_values.append("x")
        shutter_a.set("o")
        shutter_a.set("x")
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    delay_s = 1.2
    valid_open_values = ["open",]   # lower-case strings ONLY
    valid_close_values = ["close",]
    busy = Signal(value=False, name="busy")
    
    def open(self):
        """request shutter to open, interactive use"""
        self.open_bit.put(1)
    
    def close(self):
        """request shutter to close, interactive use"""
        self.close_bit.put(1)
    
    def set(self, value, **kwargs):
        """request the shutter to open or close, BlueSky plan use"""
        # ensure numerical additions to lists are now strings
        def input_filter(v):
            return str(v).lower()
        self.valid_open_values = list(map(input_filter, self.valid_open_values))
        self.valid_close_values = list(map(input_filter, self.valid_close_values))
        
        if self.busy.value:
            raise RuntimeError("shutter is operating")

        acceptables = self.valid_open_values + self.valid_close_values
        if input_filter(value) not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)
        
        status = DeviceStatus(self)
        
        def move_shutter():
            if input_filter(value) in self.valid_open_values:
                self.open()     # no need to yield inside a thread
            elif input_filter(value) in self.valid_close_values:
                self.close()
        
        def run_and_delay():
            self.busy.put(True)
            move_shutter()
            # sleep, since we don't *know* when the shutter has moved
            time.sleep(self.delay_s)
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_delay, daemon=True).start()
        return status


class AxisTunerException(ValueError): 
    """Exception during execution of `AxisTunerBase` subclass"""
    pass


class AxisTunerMixin(object):
    """
    Mixin class to provide tuning capabilities for an axis
    
    USAGE::
    
        class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
            pass
        
        def a2r_pretune_hook():
            # set the counting time for *this* tune
            yield from bps.abs_set(scaler.preset_time, 0.2)
            
        a2r = TunableEpicsMotor("xxx:m1", name="a2r")
        a2r.tuner = TuneAxis([scaler], a2r, signal_name=scaler.channels.chan2.name)
        a2r.tuner.width = 0.02
        a2r.tuner.num = 21
        a2r.pre_tune_method = a2r_pretune_hook
        RE(a2r.tune())
        
        # tune four of the USAXS axes (using preconfigured parameters for each)
        RE(tune_axes([mr, m2r, ar, a2r])

    HOOK METHODS
    
    There are two hook methods (`pre_tune_method()`, and `post_tune_method()`)
    for callers to add additional plan parts, such as opening or closing shutters, 
    setting detector parameters, or other actions.
    
    Each hook method must accept one argument: 
    axis object such as `EpicsMotor` or `SynAxis`,
    such as::
    
        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")
        
        class TunableSynAxis(SynAxis, AxisTunerMixin):
            pass

        myaxis = TunableSynAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        myaxis.tuner = TuneAxis([mydet], myaxis)
        myaxis.pre_tune_method = my_pre_tune_hook
        myaxis.post_tune_method = my_post_tune_hook
        
        RE(myaxis.tune())

    """
    
    def __init__(self):
        # self.tuner = PeakAxisTuner()
        self.tuner = None   # such as: APS_BlueSky_tools.plans.TuneAxis
        
        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method
    
    def _default_pre_tune_method(self):
        """called before `tune()`"""
        print("{} position before tuning: {}".format(self.name, self.position))

    def _default_post_tune_method(self):
        """called after `tune()`"""
        print("{} position after tuning: {}".format(self.name, self.position))

    def tune(self, md=None, **kwargs):
        if self.tuner is None:
            msg = "Must define an axis tuner, none specified."
            msg += "  Consider using APS_BlueSky_tools.plans.TuneAxis()"
            raise AxisTunerException(msg)
        
        if self.tuner.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)

        if md is None:
            md = OrderedDict()
        md["purpose"] = "tuner"
        md["datetime"] = str(datetime.now())

        if self.pre_tune_method is not None:
            self.pre_tune_method()

        if self.tuner is not None:
            yield from self.tuner.tune(md=md, **kwargs)

        if self.post_tune_method is not None:
            self.post_tune_method()


class EpicsMotorDialMixin(object):
    """
    add motor record's dial coordinate fields
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorDialMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")


class EpicsMotorWithDial(EpicsMotor, EpicsMotorDialMixin):
    """
    add motor record's dial coordinates to EpicsMotor
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    This is legacy support.  For new work, use `EpicsMotorDialMixin`.
    """
    pass


class EpicsMotorServoMixin(object):
    """
    add motor record's servo loop controls
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorServoMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)


class EpicsMotorWithServo(EpicsMotor, EpicsMotorServoMixin):
    """
    extend basic motor support to enable/disable the servo loop controls
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    This is legacy support.  For new work, use `EpicsMotorServoMixin`.
    """
    pass


class EpicsMotorRawMixin(object):
    """
    add motor record's raw coordinate fields
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorRawMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    raw = Component(EpicsSignal, ".RRBV", write_pv=".RVAL")


class EpicsMotorDescriptionMixin(object):
    """
    add motor record's description field
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorDescriptionMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    desc = Component(EpicsSignal, ".DESC")


class EpicsMotorShutter(Device):
    """
    a shutter, implemented with an EPICS motor moved between two positions
    
    USAGE::

        tomo_shutter = EpicsMotorShutter("2bma:m23", name="tomo_shutter")
        tomo_shutter.closed_position = 1.0      # default
        tomo_shutter.open_position = 0.0        # default
        tomo_shutter.open()
        tomo_shutter.close()
        
        # or, when used in a plan
        def planA():
            yield from abs_set(tomo_shutter, "open", group="O")
            yield from wait("O")
            yield from abs_set(tomo_shutter, "close", group="X")
            yield from wait("X")
        def planA():
            yield from abs_set(tomo_shutter, "open", wait=True)
            yield from abs_set(tomo_shutter, "close", wait=True)
        def planA():
            yield from mv(tomo_shutter, "open")
            yield from mv(tomo_shutter, "close")

    """
    motor = Component(EpicsMotor, "")
    closed_position = 1.0
    open_position = 0.0
    _tolerance = 0.01
    
    def isopen(self):
        return abs(self.motor.position - self.open_position) <= self._tolerance
    
    def isclosed(self):
        return abs(self.motor.position - self.closed_position) <= self._tolerance
    
    def open(self):
        """move motor to BEAM NOT BLOCKED position, interactive use"""
        self.motor.move(self.open_position)
    
    def close(self):
        """move motor to BEAM BLOCKED position, interactive use"""
        self.motor.move(self.closed_position)

    def set(self, value, *, timeout=None, settle_time=None):
        """
        `set()` is like `put()`, but used in BlueSky plans

        PARAMETERS
        
        value : "open" or "close"

        timeout : float, optional
            Maximum time to wait. Note that set_and_wait does not support
            an infinite timeout.

        settle_time: float, optional
            Delay after the set() has completed to indicate completion
            to the caller

        RETURNS
        
        status : DeviceStatus
        """

        # using put completion:
        # timeout and settle time is handled by the status object.
        status = DeviceStatus(
            self, timeout=timeout, settle_time=settle_time)

        def put_callback(**kwargs):
            status._finished(success=True)

        if value.lower() == "open":
            pos = self.open_position
        elif value.lower() == "close":
            pos = self.closed_position
        else:
            msg = "value should be either open or close"
            msg + " : received " + str(value)
            raise ValueError(msg)
        self.motor.user_setpoint.put(
            pos, use_complete=True, callback=put_callback)

        return status


"""
(ophyd) Devices that might be useful at the APS using BlueSky

.. autosummary::
   
    ~AD_setup_FrameType
    ~AD_warmed_up
    ~ApsHDF5Plugin
    ~ApsMachineParametersDevice
    ~ApsPssShutter
    ~ApsPssShutterWithStatus
    ~AxisTunerException
    ~AxisTunerMixin
    ~DualPf4FilterBox
    ~EpicsMotorDialMixin
    ~EpicsMotorLimitsMixin
    ~EpicsMotorServoMixin
    ~EpicsMotorRawMixin
    ~EpicsMotorDescriptionMixin
    ~EpicsMotorShutter
    ~ProcedureRegistry
    ~sscanRecord  
    ~sscanDevice
    ~swaitRecord
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer
    ~TunableEpicsMotor
    ~use_EPICS_scaler_channels
    ~userCalcsDevice

Internal routines

.. autosummary::

    ~ApsOperatorMessagesDevice
    ~ApsFileStoreHDF5
    ~ApsFileStoreHDF5IterativeWrite

Legacy routines

.. autosummary::
   
    ~EpicsMotorWithDial
    ~EpicsMotorWithServo

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
from datetime import datetime
import epics
import itertools
import threading
import time

from .synApps_ophyd import *
from . import plans as APS_plans

import ophyd
from ophyd import Component, Device, DeviceStatus, FormattedComponent
from ophyd import Signal, EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd.scaler import EpicsScaler, ScalerCH
from bluesky.plan_stubs import mv, mvr, abs_set, wait

from ophyd.areadetector.filestore_mixins import FileStoreHDF5
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd import HDF5Plugin
from ophyd.utils import set_and_wait


def use_EPICS_scaler_channels(scaler):
    """
    configure scaler for only the channels with names assigned in EPICS 
    """
    if isinstance(scaler, EpicsScaler):
        import epics
        read_attrs = []
        for ch in scaler.channels.component_names:
            _nam = epics.caget("{}.NM{}".format(scaler.prefix, int(ch[4:])))
            if len(_nam.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs
    elif isinstance(scaler, ScalerCH):
        read_attrs = []
        for ch in scaler.channels.component_names:
            nm_pv = scaler.channels.__getattribute__(ch)
            if nm_pv is not None and len(nm_pv.chname.value.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs


class ApsOperatorMessagesDevice(Device):
    """general messages from the APS main control room"""
    operators = Component(EpicsSignalRO, "OPS:message1", string=True)
    floor_coordinator = Component(EpicsSignalRO, "OPS:message2", string=True)
    fill_pattern = Component(EpicsSignalRO, "OPS:message3", string=True)
    last_problem_message = Component(EpicsSignalRO, "OPS:message4", string=True)
    last_trip_message = Component(EpicsSignalRO, "OPS:message5", string=True)
    # messages 6-8: meaning?
    message6 = Component(EpicsSignalRO, "OPS:message6", string=True)
    message7 = Component(EpicsSignalRO, "OPS:message7", string=True)
    message8 = Component(EpicsSignalRO, "OPS:message8", string=True)


class ApsMachineParametersDevice(Device):
    """
    common operational parameters of the APS of general interest
    
    USAGE::

        import APS_BlueSky_tools.devices as APS_devices
        APS = APS_devices.ApsMachineParametersDevice(name="APS")
        aps_current = APS.current

        # make sure these values are logged at start and stop of every scan
        sd.baseline.append(APS)
        # record storage ring current as secondary stream during scans
        # name: aps_current_monitor
        # db[-1].table("aps_current_monitor")
        sd.monitors.append(aps_current)

    The `sd.baseline` and `sd.monitors` usage relies on this global setup:

        from bluesky import SupplementalData
        sd = SupplementalData()
        RE.preprocessors.append(sd)

    .. autosummary::
    
        ~inUserOperations
   

    """
    current = Component(EpicsSignalRO, "S:SRcurrentAI")
    lifetime = Component(EpicsSignalRO, "S:SRlifeTimeHrsCC")
    machine_status = Component(EpicsSignalRO, "S:DesiredMode", string=True)
    # In [3]: APS.machine_status.enum_strs
    # Out[3]: 
    # ('State Unknown',
    #  'USER OPERATIONS',
    #  'Bm Ln Studies',
    #  'INJ Studies',
    #  'ASD Studies',
    #  'NO BEAM',
    #  'MAINTENANCE')
    operating_mode = Component(EpicsSignalRO, "S:ActualMode", string=True)
    # In [4]: APS.operating_mode.enum_strs
    # Out[4]: 
    # ('State Unknown',
    # 'NO BEAM',
    # 'Injecting',
    # 'Stored Beam',
    # 'Delivered Beam',
    # 'MAINTENANCE')
    shutter_permit = Component(EpicsSignalRO, "ACIS:ShutterPermit", string=True)
    fill_number = Component(EpicsSignalRO, "S:FillNumber")
    orbit_correction = Component(EpicsSignalRO, "S:OrbitCorrection:CC")
    global_feedback = Component(EpicsSignalRO, "SRFB:GBL:LoopStatusBI", string=True)
    global_feedback_h = Component(EpicsSignalRO, "SRFB:GBL:HLoopStatusBI", string=True)
    global_feedback_v = Component(EpicsSignalRO, "SRFB:GBL:VLoopStatusBI", string=True)
    operator_messages = Component(ApsOperatorMessagesDevice)
    
    @property
    def inUserOperations(self):
        """
        determine if APS is in User Operations mode (boolean)
        
        Use this property to configure ophyd Devices for direct or simulated hardware.
        See issue #49 (https://github.com/BCDA-APS/APS_BlueSky_tools/issues/49) for details.
        
        EXAMPLE::
        
            APS = APS_BlueSky_tools.devices.ApsMachineParametersDevice(name="APS")
            
            if APS.inUserOperations:
                suspend_APS_current = bluesky.suspenders.SuspendFloor(APS.current, 2, resume_thresh=10)
                RE.install_suspender(suspend_APS_current)
            else:
                # use pseudo shutter controls and no current suspenders
                pass

        """
        verdict = self.machine_status.value in (1, "USER OPERATIONS")
        # verdict = verdict and self.operating_mode.value not in (5, "MAINTENANCE")
        return verdict


class ApsPssShutter(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
      (see :func:`ApsPssShutterWithStatus()` for alternative)
    
    USAGE::
    
        shutter_a = ApsPssShutter("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        shutter_a.set("open")
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use ``yield from``.
    
    ::

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


class ApsPssShutterWithStatus(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
      (see :func:`ApsPssShutter()` for alternative)
    
    USAGE::
    
        A_shutter = ApsPssShutterWithStatus(
            "2bma:A_shutter", 
            "PA:02BM:STA_A_FES_OPEN_PL", 
            name="A_shutter")
        B_shutter = ApsPssShutterWithStatus(
            "2bma:B_shutter", 
            "PA:02BM:STA_B_SBS_OPEN_PL", 
            name="B_shutter")
        
        A_shutter.open()
        A_shutter.close()
        
        or
        
        %mov A_shutter "open"
        %mov A_shutter "close"
        
        or
        
        A_shutter.set("open")       # MUST be "open", not "Open"
        A_shutter.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(A_shutter))
        
    The strings accepted by `set()` are defined in attributes
    (`open_str` and `close_str`).
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    pss_state = FormattedComponent(EpicsSignalRO, "{self.state_pv}")

    # strings the user will use
    open_str = 'open'
    close_str = 'close'

    # pss_state PV values from EPICS
    open_val = 1
    close_val = 0

    def __init__(self, prefix, state_pv, *args, **kwargs):
        self.state_pv = state_pv
        super().__init__(prefix, *args, **kwargs)

    def open(self, timeout=10):
        " "
        ophyd.status.wait(self.set(self.open_str), timeout=timeout)

    def close(self, timeout=10):
        " "
        ophyd.status.wait(self.set(self.close_str), timeout=timeout)

    def set(self, value, **kwargs):
        # first, validate the input value
        acceptables = (self.close_str, self.open_str)
        if value not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)

        command_signal = {
            self.open_str: self.open_bit, 
            self.close_str: self.close_bit
        }[value]
        expected_value = {
            self.open_str: self.open_val, 
            self.close_str: self.close_val
        }[value]

        working_status = DeviceStatus(self)
        
        def shutter_cb(value, timestamp, **kwargs):
            # APS shutter state PVs do not define strings, use numbers
            #value = enums[int(value)]
            value = int(value)
            if value == expected_value:
                self.pss_state.clear_sub(shutter_cb)
                working_status._finished()
        
        self.pss_state.subscribe(shutter_cb)
        command_signal.set(1)
        return working_status

    @property
    def isOpen(self):
        " "
        return self.pss_state.value == self.open_val
    
    @property
    def isClosed(self):
        " "
        return self.pss_state.value == self.close_val


class ApsUndulator(Device):
    """
    APS Undulator
    
    USAGE:  ``undulator = ApsUndulator("ID09ds:", name="undulator")``
    """
    energy = Component(EpicsSignal, "Energy", write_pv="EnergySet")
    energy_taper = Component(EpicsSignal, "TaperEnergy", write_pv="TaperEnergySet")
    gap = Component(EpicsSignal, "Gap", write_pv="GapSet")
    gap_taper = Component(EpicsSignal, "TaperGap", write_pv="TaperGapSet")
    start_button = Component(EpicsSignal, "Start")
    stop_button = Component(EpicsSignal, "Stop")
    harmonic_value = Component(EpicsSignal, "HarmonicValue")
    gap_deadband = Component(EpicsSignal, "DeadbandGap")
    device_limit = Component(EpicsSignal, "DeviceLimit")

    access_mode = Component(EpicsSignalRO, "AccessSecurity")
    device_status = Component(EpicsSignalRO, "Busy")
    total_power = Component(EpicsSignalRO, "TotalPower")
    message1 = Component(EpicsSignalRO, "Message1")
    message2 = Component(EpicsSignalRO, "Message2")
    message3 = Component(EpicsSignalRO, "Message3")
    time_left = Component(EpicsSignalRO, "ShClosedTime")

    device = Component(EpicsSignalRO, "Device")
    location = Component(EpicsSignalRO, "Location")
    version = Component(EpicsSignalRO, "Version")


class ApsUndulatorDual(Device):
    """
    APS Undulator with upstream *and* downstream controls
    
    USAGE:  ``undulator = ApsUndulatorDual("ID09", name="undulator")``
    
    note:: the trailing ``:`` in the PV prefix should be omitted
    """
    upstream = Component(ApsUndulator, "us:")
    downstream = Component(ApsUndulator, "ds:")


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

        if self.tuner is not None:
            if self.pre_tune_method is not None:
                self.pre_tune_method()

            yield from self.tuner.tune(md=md, **kwargs)
    
            if self.post_tune_method is not None:
                self.post_tune_method()


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    """
    EPICS motor with signal for tuning
    
    USAGE::

        def a2r_pretune_hook():
            # set the counting time for *this* tune
            yield from bps.abs_set(scaler.preset_time, 0.2)
    
        a2r = TunableEpicsMotor("xxx:m1", name="a2r")
        a2r.tuner = TuneAxis([scaler], a2r, signal_name=scaler.channels.chan2.name)
        a2r.tuner.width = 0.02
        a2r.tuner.num = 21
        a2r.pre_tune_method = a2r_pretune_hook
        RE(a2r.tune())
    
    """
    pass


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


class EpicsMotorLimitsMixin(Device):
    """
    add motor record HLM & LLM fields & compatibility get_lim() and set_lim()
    """
    
    soft_limit_lo = Component(EpicsSignal, ".LLM")
    soft_limit_hi = Component(EpicsSignal, ".HLM")
    
    def get_lim(self, flag):
        """
        Returns the user limit of motor
        
        flag > 0: returns high limit
        flag < 0: returns low limit
        flag == 0: returns None
        """
        if flag > 0:
            return self.high_limit
        else:
            return self.low_limit
    
    def set_lim(self, low, high):
        """
        Sets the low and high limits of motor
        
        * Low limit is set to lesser of (low, high)
        * High limit is set to greater of (low, high)
        * No action taken if motor is moving. 
        """
        if not self.moving:
            self.soft_limit_lo.put(min(low, high))
            self.soft_limit_hi.put(max(low, high))


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
    
    @property
    def isOpen(self):
        " "
        return abs(self.motor.position - self.open_position) <= self._tolerance
    
    @property
    def isClosed(self):
        " "
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


class DualPf4FilterBox(Device):
    """
    Dual Xia PF4 filter boxes using support from synApps (using Al, Ti foils)
    
    Example::
    
        pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")
        pf4_AlTi = DualPf4FilterBox("9idcRIO:pf4:", name="pf4_AlTi")
    
    """
    fPosA = Component(EpicsSignal, "fPosA")
    fPosB = Component(EpicsSignal, "fPosB")
    bankA = Component(EpicsSignalRO, "bankA")
    bankB = Component(EpicsSignalRO, "bankB")
    bitFlagA = Component(EpicsSignalRO, "bitFlagA")
    bitFlagB = Component(EpicsSignalRO, "bitFlagB")
    transmission = Component(EpicsSignalRO, "trans")
    transmission_a = Component(EpicsSignalRO, "transA")
    transmission_b = Component(EpicsSignalRO, "transB")
    inverse_transmission = Component(EpicsSignalRO, "invTrans")
    thickness_Al_mm = Component(EpicsSignalRO, "filterAl")
    thickness_Ti_mm = Component(EpicsSignalRO, "filterTi")
    thickness_glass_mm = Component(EpicsSignalRO, "filterGlass")
    energy_keV_local = Component(EpicsSignal, "E:local")
    energy_keV_mono = Component(EpicsSignal, "displayEnergy")
    mode = Component(EpicsSignal, "useMono", string=True)    


class ProcedureRegistry(Device):
    """
    Procedure Registry:  run a blocking function in a thread
    
    With many instruments, such as USAXS, there are several operating 
    modes to be used, each with its own setup code.  This ophyd Device
    should coordinate those modes so that the setup procedures can be called
    either as part of a Bluesky plan or from the command line directly.
    Assumes that users will write functions to setup a particular 
    operation or operating mode.  The user-written functions may not
    be appropriate to use in a plan directly since they might
    make blocking calls.  The ProcedureRegistry will call the function
    in a thread (which is allowed to make blocking calls) and wait
    for the thread to complete.
    
    It is assumed that each user-written function will not return until
    it is complete.
    .. autosummary::
       
        ~dir
        ~add
        ~remove
        ~set
        ~put

    EXAMPLE:
    
    Given these function definitions::

        def clearScalerNames():
            for ch in scaler.channels.configuration_attrs:
                if ch.find(".") < 0:
                    chan = scaler.channels.__getattribute__(ch)
                    chan.chname.put("")

        def setMyScalerNames():
            scaler.channels.chan01.chname.put("clock")
            scaler.channels.chan02.chname.put("I0")
            scaler.channels.chan03.chname.put("detector")
    
    create a registry and add the two functions (default name
    is the function name):
    
        use_mode = ProcedureRegistry(name="ProcedureRegistry")
        use_mode.add(clearScalerNames)
        use_mode.add(setMyScalerNames)
    
    and then use this registry in a plan, such as this::
    
        def myPlan():
            yield from bps.mv(use_mode, "setMyScalerNames")
            yield from bps.sleep(5)
            yield from bps.mv(use_mode, "clearScalerNames")

    """
    
    busy = Component(Signal, value=False)
    registry = {}
    delay_s = 0
    timeout_s = None
    state = "__created__"
    
    @property
    def dir(self):
        """tuple of procedure names"""
        return tuple(sorted(self.registry.keys()))
    
    def add(self, procedure, proc_name=None):
        """
        add procedure to registry
        """
        #if procedure.__class__ == "function":
        nm = proc_name or procedure.__name__
        self.registry[nm] = procedure
    
    def remove(self, procedure):
        """
        remove procedure from registry
        """
        if isinstance(procedure, str):
            nm = procedure
        else:
            nm = procedure.__name__
        if nm in self.registry:
            del self.registry[nm]
    
    def set(self, proc_name):
        """
        run procedure in a thread, return once it is complete
        
        proc_name (str) : name of registered procedure to be run
        """
        if not isinstance(proc_name, str):
            raise ValueError("expected a procedure name, not {}".format(proc_name))
        if proc_name not in self.registry:
            raise KeyError("unknown procedure name: "+proc_name)
        if self.busy.value:
            raise RuntimeError("busy now")
 
        self.state = "__busy__"
        status = DeviceStatus(self)
        
        @APS_plans.run_in_thread
        def run_and_delay():
            self.busy.put(True)
            self.registry[proc_name]()
            # optional delay
            if self.delay_s > 0:
                time.sleep(self.delay_s)
            self.busy.put(False)
            status._finished(success=True)
        
        run_and_delay()
        ophyd.status.wait(status, timeout=self.timeout_s)
        self.state = proc_name
        return status
    
    def put(self, value):   # TODO: risky?
        """replaces ophyd Device default put() behavior"""
        self.set(value)


# AreaDetector support

AD_FrameType_schemes = {
    "reset" : dict(             # default names from Area Detector code
        ZRST = "Normal",
        ONST = "Background",
        TWST = "FlatField",
        ),
    "NeXus" : dict(             # NeXus (typical locations)
        ZRST = "/entry/data/data",
        ONST = "/entry/data/dark",
        TWST = "/entry/data/white",
        ),
    "DataExchange" : dict(      # APS Data Exchange
        ZRST = "/exchange/data",
        ONST = "/exchange/data_dark",
        TWST = "/exchange/data_white",
        ),
}


def AD_setup_FrameType(prefix, scheme="NeXus"):
    """
    configure so frames are identified & handled by type (dark, white, or image)
    
    PARAMETERS

        prefix (str) : EPICS PV prefix of area detector, such as "13SIM1:"
        scheme (str) : any key in the `AD_FrameType_schemes` dictionary
    
    This routine prepares the EPICS Area Detector to identify frames
    by image type for handling by clients, such as the HDF5 file writing plugin.
    With the HDF5 plugin, the `FrameType` PV is added to the NDattributes
    and then used in the layout file to direct the acquired frame to
    the chosen dataset.  The `FrameType` PV value provides the HDF5 address
    to be used.
    
    To use a different scheme than the defaults, add a new key to
    the `AD_FrameType_schemes` dictionary, defining storage values for the
    fields of the EPICS `mbbo` record that you will be using.
    
    see: https://github.com/BCDA-APS/use_bluesky/blob/master/notebooks/images_darks_flats.ipynb
    
    EXAMPLE::
    
        AD_setup_FrameType("2bmbPG3:", scheme="DataExchange")
    
    * Call this function *before* creating the ophyd area detector object
    * use lower-level PyEpics interface
    """
    db = AD_FrameType_schemes.get(scheme)
    if db is None:
        msg = "unknown AD_FrameType_schemes scheme: {}".format(scheme)
        msg += "\n Should be one of: " + ", ".join(AD_FrameType_schemes.keys())
        raise ValueError(msg)

    template = "{}cam1:FrameType{}.{}"
    for field, value in db.items():
        epics.caput(template.format(prefix, "", field), value)
        epics.caput(template.format(prefix, "_RBV", field), value)

         
def AD_warmed_up(detector):
    """
    Has area detector pushed an NDarray to the HDF5 plugin?  True or False

    Works around an observed issue: #598
    https://github.com/NSLS-II/ophyd/issues/598#issuecomment-414311372

    If detector IOC has just been started and has not yet taken an image
    with the HDF5 plugin, then a TimeoutError will occur as the
    HDF5 plugin "Capture" is set to 1 (Start).  In such case,
    first acquire at least one image with the HDF5 plugin enabled.
    """
    old_capture = detector.hdf1.capture.value
    old_file_write_mode = detector.hdf1.file_write_mode.value
    if old_capture == 1:
        return True
    
    detector.hdf1.file_write_mode.put(1)
    detector.hdf1.capture.put(1)
    verdict = detector.hdf1.capture.get() == 1
    detector.hdf1.capture.put(old_capture)
    detector.hdf1.file_write_mode.put(old_file_write_mode)
    return verdict


class ApsFileStoreHDF5(FileStorePluginBase):
    """
    custom class to define image file name from EPICS

    To allow users to control the file name,
    we override the ``make_filename()`` method here
    and we need to override some intervening classes.

    To allow users to control the file number,
    we override the ``stage()`` method here
    and triple-comment out that line, and bring in
    sections from the methods we are replacing here.

    The image file name is set in `FileStoreBase.make_filename()` 
    from `ophyd.areadetector.filestore_mixins`.  This is called 
    (during device staging) from `FileStoreBase.stage()`

    To use this custom class, we need to connect it to some
    intervening structure:

    ====================================  ============================
    custom class                          superclass(es)
    ====================================  ============================
    ``ApsFileStoreHDF5``                  ``FileStorePluginBase``
    ``ApsFileStoreHDF5IterativeWrite``    ``ApsFileStoreHDF5``, `FileStoreIterativeWrite``
    ``ApsHDF5Plugin``                     ``HDF5Plugin``, `ApsFileStoreHDF5IterativeWrite``
    ====================================  ============================
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5'  # spec name stored in resource doc
        self.stage_sigs.update([
            ('file_template', '%s%s_%4.4d.h5'),
            ('file_write_mode', 'Stream'),
            ('capture', 1)
        ])

    def make_filename(self):
        """
        overrides default behavior: Get info from EPICS HDF5 plugin.
        """
        # start of the file name, file number will be appended per template
        filename = self.file_name.value
        
        # this is where the HDF5 plugin will write the image, 
        # relative to the IOC's filesystem
        write_path = self.file_path.value
        
        # this is where the DataBroker will find the image, 
        # on a filesystem accessible to BlueSky
        read_path = write_path

        return filename, read_path, write_path

    def generate_datum(self, key, timestamp, datum_kwargs):
        """Generate a uid and cache it with its key for later insertion."""
        template = self.file_template.get()
        filename, read_path, write_path = self.make_filename()
        file_number = self.file_number.get()
        hdf5_file_name = template % (read_path, filename, file_number)

        # inject the actual name of the HDF5 file here into datum_kwargs
        datum_kwargs["HDF5_file_name"] = hdf5_file_name
        
        # print("make_filename:", hdf5_file_name)
        return super().generate_datum(key, timestamp, datum_kwargs)

    def get_frames_per_point(self):
        """ """
        return self.num_capture.get()

    def stage(self):
        """ """
        # Make a filename.
        filename, read_path, write_path = self.make_filename()

        # Ensure we do not have an old file open.
        set_and_wait(self.capture, 0)
        # These must be set before parent is staged (specifically
        # before capture mode is turned on. They will not be reset
        # on 'unstage' anyway.
        set_and_wait(self.file_path, write_path)
        set_and_wait(self.file_name, filename)
        ### set_and_wait(self.file_number, 0)
        
        # get file number now since it is incremented during stage()
        file_number = self.file_number.get()
        # Must avoid parent's stage() since it sets file_number to 0
        # Want to call grandparent's stage()
        #super().stage()     # avoid this - sets `file_number` to zero
        # call grandparent.stage()
        FileStoreBase.stage(self)

        # AD does the file name templating in C
        # We can't access that result until after acquisition
        # so we apply the same template here in Python.
        template = self.file_template.get()
        self._fn = template % (read_path, filename, file_number)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError("Path {} does not exist on IOC.".format(
                          self.file_path.get()))

        # from FileStoreIterativeWrite.stage()
        self._point_counter = itertools.count()
        
        # from FileStoreHDF5.stage()
        res_kwargs = {'frame_per_point': self.get_frames_per_point()}
        self._generate_resource(res_kwargs)


class ApsFileStoreHDF5IterativeWrite(ApsFileStoreHDF5, FileStoreIterativeWrite):
    """custom class to enable users to control image file name"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FileStoreIterativeWrite.__init__(self, *args, **kwargs)


class ApsHDF5Plugin(HDF5Plugin, ApsFileStoreHDF5IterativeWrite):
    """
    custom class to take image file names from EPICS
    
    NOTE: replaces standard Bluesky algorithm where file names
          are defined as UUID strings, virtually guaranteeing that 
          no existing images files will ever be overwritten.
          *Caveat emptor* applies here.  You assume some expertise!
    
    USAGE::

        class MySimDetector(SingleTrigger, SimDetector):
            '''SimDetector with HDF5 file names specified by EPICS'''
            
            cam = ADComponent(MyAltaCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            
            hdf1 = ADComponent(
                ApsHDF5Plugin, 
                suffix = "HDF1:", 
                root = "/",
                write_path_template = "/local/data",
                )

        simdet = MySimDetector("13SIM1:", name="simdet")
        # remove this so array counter is not set to zero each staging
        del simdet.hdf1.stage_sigs["array_counter"]
        simdet.hdf1.stage_sigs["file_template"] = '%s%s_%3.3d.h5'
        simdet.hdf1.file_path.put("/local/data/demo/")
        simdet.hdf1.file_name.put("test")
        simdet.hdf1.array_counter.put(0)
        RE(bp.count([simdet]))

    """


"""
(ophyd) Devices that might be useful at the APS using BlueSky

APS GENERAL SUPPORT

.. autosummary::
   
    ~ApsMachineParametersDevice
    ~ApsPssShutter
    ~ApsPssShutterWithStatus
    ~SimulatedApsPssShutterWithStatus

AREA DETECTOR SUPPORT

.. autosummary::
   
    ~AD_setup_FrameType
    ~AD_warmed_up
    ~AD_EpicsHdf5FileName

DETECTOR / SCALER SUPPORT

.. autosummary::
   
    ~use_EPICS_scaler_channels

MOTORS, POSITIONERS, AXES, ...

.. autosummary::
   
    ~AxisTunerException
    ~AxisTunerMixin
    ~EpicsDescriptionMixin
    ~EpicsMotorDialMixin
    ~EpicsMotorLimitsMixin
    ~EpicsMotorRawMixin
    ~EpicsMotorServoMixin
    ~EpicsMotorShutter
    ~EpicsOnOffShutter

SHUTTERS

.. autosummary::
   
    ~ApsPssShutter
    ~ApsPssShutterWithStatus
    ~EpicsMotorShutter
    ~EpicsOnOffShutter
    ~OneSignalShutter
    ~ShutterBase
    ~SimulatedApsPssShutterWithStatus

synApps records

.. autosummary::
   
    ~busyRecord
    ~sscanRecord
    ~sscanDevice
    ~swaitRecord
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer
    ~userCalcsDevice

OTHER SUPPORT

.. autosummary::
   
    ~DualPf4FilterBox
    ~EpicsDescriptionMixin
    ~ProcedureRegistry

Internal routines

.. autosummary::

    ~ApsOperatorMessagesDevice
    ~DeviceMixinBase

"""

# Copyright (c) 2017-2019, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
from datetime import datetime
import epics
import itertools
import logging
import numpy as np
import threading
import time

from .synApps_ophyd import *
from . import plans as APS_plans

import ophyd
from ophyd import Component, Device, DeviceStatus, FormattedComponent
from ophyd import Signal, EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd.scaler import EpicsScaler, ScalerCH
from ophyd.positioner import PositionerBase

from ophyd.areadetector.filestore_mixins import FileStoreHDF5
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd import HDF5Plugin
from ophyd.utils import set_and_wait

from bluesky import plan_stubs as bps


logger = logging.getLogger(__name__)

"""for convenience"""		# TODO: contribute to ophyd?
SCALER_AUTOCOUNT_MODE = 1


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
    
    EXAMPLE::

        import apstools.devices as APS_devices
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
        See issue #49 (https://github.com/BCDA-APS/apstools/issues/49) for details.
        
        EXAMPLE::
        
            APS = apstools.devices.ApsMachineParametersDevice(name="APS")
            
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


class ShutterBase(Device):
    """
    base class for all shutter Devices
    
    PARAMETERS
    
    value : str
        any from ``self.choices`` (typically "open" or "close")

    valid_open_values : [str]
        A list of lower-case text values that are acceptable 
        for use with the ``set()`` command to open the shutter.

    valid_close_values : [str]
        A list of lower-case text values that are acceptable
        for use with the ``set()`` command to close the shutter.

    open_value : number
        The actual value to send to open ``signal`` to open the shutter.
        (default = 1)

    close_value : number
        The actual value to send to close ``signal`` to close the shutter.
        (default = 0)

    delay_s : float
        time to wait (s) after move is complete, 
        does not wait if shutter already in position
        (default = 0)

    busy : Signal
        (internal) tells if a move is in progress

    unknown_state : str
        (constant) Text reported by ``state`` when not open or closed.
        cannot move to this position
        (default = "unknown")
    """

    valid_open_values = ["open", "opened",]   # lower-case strings ONLY
    valid_close_values = ["close", "closed",]
    open_value = 1      # value of "open"
    close_value = 0     # value of "close"
    delay_s = 0.0       # time to wait (s) after move is complete
    busy = Component(Signal, value=False)
    unknown_state = "unknown"       # cannot move to this position

    # - - - - likely to override these methods in subclass - - - -

    def open(self):
        """BLOCKING: request shutter to open, called by set()"""
        raise NotImplementedError("must implement in subclass")
        """ example code
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here
        """

    def close(self):
        """BLOCKING: request shutter to close, called by set()"""
        raise NotImplementedError("must implement in subclass")
        """ example code
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here
        """

    @property
    def state(self):
        """returns 'open', 'close', or 'unknown'"""
        raise NotImplementedError("must implement in subclass")
        """ example code
        if self.signal.value == self.open_value:
            result = self.valid_open_values[0]
        elif self.signal.value == self.close_value:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result
        """
    
    # - - - - - - possible to override in subclass - - - - - -
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valid_open_values = list(map(self.lowerCaseString, self.valid_open_values))
        self.valid_close_values = list(map(self.lowerCaseString, self.valid_close_values))
    
    @property
    def isOpen(self):
        """is the shutter open?"""
        return str(self.state) == self.valid_open_values[0]
    
    @property
    def isClosed(self):
        """is the shutter closed?"""
        return str(self.state) == self.valid_close_values[0]

    def inPosition(self, target):
        """is the shutter at the target position?"""
        self.validTarget(target)
        __value__ = self.lowerCaseString(target)
        if __value__ in self.valid_open_values and self.isOpen:
            return True
        elif __value__ in self.valid_close_values and self.isClosed:
            return True
        return False

    def set(self, value, **kwargs):
        """
        plan: request the shutter to open or close

        PARAMETERS
        
        value : str
            any from ``self.choices`` (typically "open" or "close")
        
        kwargs : dict
            ignored at this time

        """
        if self.busy.value:
            raise RuntimeError("shutter is operating")
        
        __value__ = self.lowerCaseString(value)
        self.validTarget(__value__)

        status = DeviceStatus(self)
        
        if self.inPosition(__value__):
            # no need to move, cut straight to the end
            status._finished(success=True)
        else:
            def move_it():
                # runs in a thread, no need to "yield from"
                self.busy.put(True)
                if __value__ in self.valid_open_values:
                    self.open()
                elif __value__ in self.valid_close_values:
                    self.close()
                self.busy.put(False)
                status._finished(success=True)
            # get it moving
            threading.Thread(target=move_it, daemon=True).start()
        return status
    
    # - - - - - - not likely to override in subclass - - - - - -

    def addCloseValue(self, text):
        """a synonym to close the shutter, use with set()"""
        self.valid_close_values.append(self.lowerCaseString(text))
        return self.choices     # return the list of acceptable values
    
    def addOpenValue(self, text):
        """a synonym to open the shutter, use with set()"""
        self.valid_open_values.append(self.lowerCaseString(text))
        return self.choices     # return the list of acceptable values

    @property
    def choices(self):
        """return list of acceptable choices for set()"""
        return self.valid_open_values + self.valid_close_values
    
    def lowerCaseString(self, value):
        """ensure any given value is a lower-case string"""
        return str(value).lower()

    def validTarget(self, target, should_raise=True):
        """
        return whether (or not) target value is acceptable for self.set()
        
        raise ValueError if not acceptable (default)
        """
        acceptable_values = self.choices
        ok = self.lowerCaseString(target) in acceptable_values
        if not ok and should_raise:
            msg = "received " + str(target)
            msg += " : should be only one of "
            msg += " | ".join(acceptable_values)
            raise ValueError(msg)
        return ok


class OneSignalShutter(ShutterBase):
    """
    shutter Device using one Signal for open and close
    
    PARAMETERS

    signal : EpicsSignal or Signal
        (override in subclass)
        The ``signal`` is the comunication to the hardware.
        In a subclass, the hardware may have more than
        one communication channel to use.  See the
        ``ApsPssShutter`` as an example.
    
    See ``ShutterBase`` for more parameters.

    EXAMPLE

    Create a simulated shutter:

        shutter = OneSignalShutter(name="shutter")

    open the shutter (interactively):

        shutter.open()

    Check the shutter is open:

        In [144]: shutter.isOpen
        Out[144]: True

    Use the shutter in a Bluesky plan.
    Set a post-move delay time of 1.0 seconds.
    Be sure to use ``yield from``, such as::

        def in_a_plan(shutter):
            shutter.delay_s = 1.0
            t0 = time.time()
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.abs_set(shutter, "open", wait=True)    # wait for completion is optional
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.mv(shutter, "open")    # do it again
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.mv(shutter, "close")    # ALWAYS waits for completion
            print("Shutter state: " + shutter.state, time.time()-t0)
        
        RE(in_a_plan(shutter))
    
    which gives this output:

        Shutter state: close 1.7642974853515625e-05
        Shutter state: open 1.0032124519348145
        Shutter state: open 1.0057861804962158
        Shutter state: close 2.009695529937744
        
    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.
    
    Example, add "o" & "x" as aliases for "open" & "close":
    
        shutter.addOpenValue("o")
        shutter.addCloseValue("x")
        shutter.set("o")
        shutter.set("x")
    """

    signal = Component(Signal, value=0)
    
    # - - - - likely to override these methods in subclass - - - -

    def open(self):
        """BLOCKING: request shutter to open, called by set()"""
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    def close(self):
        """BLOCKING: request shutter to close, called by set()"""
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    @property
    def state(self):
        """is shutter "open", "close", or "unknown"?"""
        if self.signal.value == self.open_value:
            result = self.valid_open_values[0]
        elif self.signal.value == self.close_value:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result


class ApsPssShutter(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
      (see :func:`ApsPssShutterWithStatus()` for alternative)
    
    EXAMPLE::
    
        shutter_a = ApsPssShutter("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        shutter_a.set("open")
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use ``yield from``, such as::

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


class SimulatedApsPssShutterWithStatus(ShutterBase):
    """
    Simulated APS PSS shutter
    
    EXAMPLE::
    
        sim = SimulatedApsPssShutterWithStatus(name="sim")
    
    """
    open_signal = Component(Signal, value=0)
    close_signal = Component(Signal, value=0)
    pss_state = FormattedComponent(Signal, value='close')
    open_value = 1
    close_value = 0
    open_text = "open"
    close_text = "close"

    @property
    def state(self):
        """is shutter "open", "close", or "unknown"?"""
        if self.pss_state.value == self.open_text:
            result = self.open_text
        elif self.pss_state.value == self.close_text:
            result = self.close_text
        else:
            result = self.unknown_state
        return result

    def open(self, timeout=10):
        """request the shutter to open (ignore timeout)"""
        if not self.isOpen:
            self.open_signal.put(self.open_value)
            self.delay_s = self.simulate_response_time()
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here
            self.pss_state.put(self.open_text)

    def close(self, timeout=10):
        """request the shutter to close (ignore timeout)"""
        if not self.isClosed:
            self.close_signal.put(self.close_value)
            self.delay_s = self.simulate_response_time()
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here
            self.pss_state.put(self.close_text)

    def simulate_response_time(self):
        """simulated response time for PSS status"""
        return np.random.uniform(0.1, 0.9)

    def set(self, value, **kwargs):
        """
        plan: request the shutter to open or close

        PARAMETERS
        
        value : str
            any from ``self.choices`` (typically "open" or "close")
        
        kwargs : dict
            ignored at this time

        """
        if self.busy.value:
            raise RuntimeError("shutter is operating")
        
        __value__ = self.lowerCaseString(value)
        self.validTarget(__value__)

        status = DeviceStatus(self)
        
        if self.inPosition(__value__):
            # no need to move, cut straight to the end
            status._finished(success=True)
        else:
            def move_it():
                # runs in a thread, no need to "yield from"
                self.busy.put(True)
                if __value__ in self.valid_open_values:
                    self.open()
                    expected_value = self.open_text
                elif __value__ in self.valid_close_values:
                    self.close()
                    expected_value = self.close_text
                self.pss_state.set(expected_value)
                self.busy.put(False)
                status._finished(success=True)
            # get it moving
            threading.Thread(target=move_it, daemon=True).start()

        # finally, make sure both signals are reset
        self.open_signal.put(0)
        self.close_signal.put(0)
        return status


class ApsPssShutterWithStatus(SimulatedApsPssShutterWithStatus):
    """
    APS PSS shutter with separate status PV
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
      (see :func:`ApsPssShutter()` for alternative)
    
    EXAMPLE::
    
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
        
        A_shutter.set("open")
        A_shutter.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(A_shutter))
        
    The strings accepted by `set()` are defined in attributes
    (`open_text` and `close_text`).
    """
    # bo records that reset after a short time, set to 1 to move
    open_signal = Component(EpicsSignal, "open")    # :open
    close_signal = Component(EpicsSignal, "close")  # :close
    
    # bi record ZNAM=OFF, ONAM=ON
    pss_state = FormattedComponent(EpicsSignalRO, "{self.state_pv}")
    pss_state_open_values = []
    pss_state_closed_values = []

    def __init__(self, prefix, state_pv, *args, **kwargs):
        self.state_pv = state_pv
        super().__init__(prefix, *args, **kwargs)
        self.pss_state_open_values = [
            1,
            self.pss_state.enum_strs[1]]
        self.pss_state_closed_values = [
            0,
            self.pss_state.enum_strs[0]]

    @property
    def state(self):
        """is shutter "open", "close", or "unknown"?"""
        if self.pss_state.value in self.pss_state_open_values:
            result = self.open_text
        elif self.pss_state.value in self.pss_state_closed_values:
            result = self.close_text
        else:
            result = self.unknown_state
        return result

    def wait_for_pss_state(self, target, timeout=10, poll_s=0.01):
        if timeout is not None:
            expiration = time.time() + timeout
        else:
            expiration = None
        
        while self.pss_state.value not in target:
            time.sleep(poll_s)
            if poll_s < 0.1:
                poll_s *= 1.5   # progressively longer
            if expiration is not None and time.time() > expiration:
                msg = f"Timeout ({timeout} s) waiting for PSS shutter state"
                msg += f" to reach a value in {target}"
                raise TimeoutError(msg)

    def open(self, timeout=10):
        """request the shutter to open"""
        if not self.isOpen:
            self.open_signal.put(1)
            self.wait_for_pss_state(
                self.pss_state_open_values, 
                timeout=timeout)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    def close(self, timeout=10):
        """request the shutter to close"""
        if not self.isClosed:
            self.close_signal.put(1)
            self.wait_for_pss_state(
                self.pss_state_closed_values, 
                timeout=timeout)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    def set(self, value, **kwargs):
        """
        plan: request the shutter to open or close

        PARAMETERS
        
        value : str
            any from ``self.choices`` (typically "open" or "close")
        
        kwargs : dict
            ignored at this time

        """
        if self.busy.value:
            raise RuntimeError("shutter is operating")
        
        __value__ = self.lowerCaseString(value)
        self.validTarget(__value__)

        status = DeviceStatus(self)
        
        if self.inPosition(__value__):
            # no need to move, cut straight to the end
            status._finished(success=True)
        else:
            def move_it():
                # runs in a thread, no need to "yield from"
                self.busy.put(True)
                if __value__ in self.valid_open_values:
                    self.open()
                elif __value__ in self.valid_close_values:
                    self.close()
                self.busy.put(False)
                status._finished(success=True)

            # get it moving
            threading.Thread(target=move_it, daemon=True).start()

        return status


class ApsUndulator(Device):
    """
    APS Undulator
    
    EXAMPLE::
    
        undulator = ApsUndulator("ID09ds:", name="undulator")
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
    
    EXAMPLE::
    
        undulator = ApsUndulatorDual("ID09", name="undulator")
    
    note:: the trailing ``:`` in the PV prefix should be omitted
    """
    upstream = Component(ApsUndulator, "us:")
    downstream = Component(ApsUndulator, "ds:")


class ApsBssUserInfoDevice(Device):
    """
    provide current experiment info from the APS BSS
    
    BSS: Beamtime Scheduling System

    EXAMPLE::

        bss_user_info = ApsBssUserInfoDevice(
                            "9id_bss:",
                            name="bss_user_info")
        sd.baseline.append(bss_user_info)

    """
    proposal_number =   Component(EpicsSignal, "proposal_number")
    activity =          Component(EpicsSignal, "activity",      string=True)
    badge =             Component(EpicsSignal, "badge",         string=True)
    bss_name =          Component(EpicsSignal, "bss_name",      string=True)
    contact =           Component(EpicsSignal, "contact",       string=True)
    email =             Component(EpicsSignal, "email",         string=True)
    institution =       Component(EpicsSignal, "institution",   string=True)
    station =           Component(EpicsSignal, "station",       string=True)
    team_others =       Component(EpicsSignal, "team_others",   string=True)
    time_begin =        Component(EpicsSignal, "time_begin",    string=True)
    time_end =          Component(EpicsSignal, "time_end",      string=True)
    timestamp =         Component(EpicsSignal, "timestamp",     string=True)
    title =             Component(EpicsSignal, "title",         string=True)
    # not yet updated, see: https://git.aps.anl.gov/jemian/aps_bss_user_info/issues/10
    esaf =              Component(EpicsSignal, "esaf",          string=True)
    esaf_contact =      Component(EpicsSignal, "esaf_contact",  string=True)
    esaf_team =         Component(EpicsSignal, "esaf_team",     string=True)


class DeviceMixinBase(Device):
    """Base class for apstools Device mixin classes"""


class AxisTunerException(ValueError): 
    """Exception during execution of `AxisTunerBase` subclass"""


class AxisTunerMixin(EpicsMotor):   # from apstools.devices
    """
    Mixin class to provide tuning capabilities for an axis
    
    See the `TuneAxis()` example in this jupyter notebook: 
    https://github.com/BCDA-APS/apstools/blob/master/docs/source/resources/demo_tuneaxis.ipynb
    
    HOOK METHODS
    
    There are two hook methods (`pre_tune_method()`, and `post_tune_method()`)
    for callers to add additional plan parts, such as opening or closing shutters, 
    setting detector parameters, or other actions.
    
    Each hook method must accept a single argument: 
    an axis object such as `EpicsMotor` or `SynAxis`,
    such as::
    
        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")
        
        class TunableSynAxis(AxisTunerMixin, SynAxis): pass
        myaxis = TunableSynAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        myaxis.tuner = TuneAxis([mydet], myaxis)
        myaxis.pre_tune_method = my_pre_tune_hook
        myaxis.post_tune_method = my_post_tune_hook
        
        RE(myaxis.tune())
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuner = None   # such as: apstools.plans.TuneAxis

        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method

    def _default_pre_tune_method(self):
        """called before `tune()`"""
        logger.info("{} position before tuning: {}".format(self.name, self.position))
        yield from bps.null()

    def _default_post_tune_method(self):
        """called after `tune()`"""
        logger.info("{} position after tuning: {}".format(self.name, self.position))
        yield from bps.null()

    def tune(self, md=None, **kwargs):
        if self.tuner is None:
            msg = "Must define an axis tuner, none specified."
            msg += "  Consider using apstools.plans.TuneAxis()"
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
                yield from self.pre_tune_method()

            yield from self.tuner.tune(md=md, **kwargs)

            if self.post_tune_method is not None:
                yield from self.post_tune_method()


# TODO: issue #76
# class TunableSynAxis(AxisTunerMixin, SynAxis): """synthetic axis that can be tuned"""
# class TunableEpicsMotor(AxisTunerMixin, EpicsMotor): """EpicsMotor that can be tuned"""


class EpicsDescriptionMixin(DeviceMixinBase):
    """
    add a record's description field to a Device, such as EpicsMotor
    
    EXAMPLE::
    
        from ophyd import EpicsMotor
        from apstools.devices import EpicsDescriptionMixin
    
        class myEpicsMotor(EpicsDescriptionMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.desc.value)
    
    """
    
    desc = Component(EpicsSignal, ".DESC")


class EpicsMotorDialMixin(DeviceMixinBase):
    """
    add motor record's dial coordinate fields to Device
    
    EXAMPLE::
    
        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorDialMixin

        class myEpicsMotor(EpicsMotorDialMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.dial.read())
    
    """
    
    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")


class EpicsMotorLimitsMixin(DeviceMixinBase):
    """
    add motor record HLM & LLM fields & compatibility get_lim() and set_lim()
    
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
    
    soft_limit_lo = Component(EpicsSignal, ".LLM")
    soft_limit_hi = Component(EpicsSignal, ".HLM")
    
    def get_lim(self, flag):
        """
        Returns the user limit of motor
        
        * flag > 0: returns high limit
        * flag < 0: returns low limit
        * flag == 0: returns None
        
        Similar with SPEC command
        """
        if flag > 0:
            return self.soft_limit_hi.value
        else:
            return self.soft_limit_lo.value
    
    def set_lim(self, low, high):
        """
        Sets the low and high limits of motor
        
        * No action taken if motor is moving.
        * Low limit is set to lesser of (low, high)
        * High limit is set to greater of (low, high)
        
        Similar with SPEC command
        """
        if not self.moving:
            self.soft_limit_lo.put(min(low, high))
            self.soft_limit_hi.put(max(low, high))


class EpicsMotorServoMixin(DeviceMixinBase):
    """
    add motor record's servo loop controls to Device
    
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
    
    EXAMPLE::
    
        from ophyd import EpicsMotor
        from apstools.devices import EpicsMotorRawMixin
    
        class myEpicsMotor(EpicsMotorRawMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.raw.read())
    """
    
    raw = Component(EpicsSignal, ".RRBV", write_pv=".RVAL")


# TODO: issue #76
# class EpicsMotorWithDescription(EpicsDescriptionMixin, EpicsMotor):
#     """EpicsMotor with description field"""
#
# class EpicsMotorWithMore(
#     EpicsDescriptionMixin, 
#     EpicsMotorLimitsMixin, 
#     EpicsMotorDialMixin,
#     EpicsMotorRawMixin, 
#     EpicsMotor): 
#     """
#     EpicsMotor with more fields
#     
#     * description (``desc``)
#     * soft motor limits (``soft_limit_hi``, ``soft_limit_lo``)
#     * dial coordinates (``dial``)
#     * raw coordinates (``raw``)
#     """


class EpicsMotorShutter(OneSignalShutter):
    """
    a shutter, implemented with an EPICS motor moved between two positions
    
    EXAMPLE::

        tomo_shutter = EpicsMotorShutter("2bma:m23", name="tomo_shutter")
        tomo_shutter.close_value = 1.0      # default
        tomo_shutter.open_value = 0.0       # default
        tomo_shutter.tolerance = 0.01       # default
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
    signal = Component(EpicsMotor, "")
    tolerance = 0.01        # how close is considered in-position?

    @property
    def state(self):
        """is shutter "open", "close", or "unknown"?"""
        if abs(self.signal.position - self.open_value) <= self.tolerance:
            result = self.valid_open_values[0]
        elif abs(self.signal.position - self.close_value) <= self.tolerance:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result
    
    def open(self):
        """move motor to BEAM NOT BLOCKED position, interactive use"""
        if not self.isOpen:
            self.signal.move(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here
    
    def close(self):
        """move motor to BEAM BLOCKED position, interactive use"""
        self.signal.move(self.close_value)
        if not self.isClosed:
            self.signal.move(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here


class EpicsOnOffShutter(OneSignalShutter):
    """
    a shutter using a single EPICS PV moved between two positions
    
    Use for a shutter controlled by a single PV which takes a 
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.
    
    EXAMPLE::

        bit_shutter = EpicsOnOffShutter("2bma:bit1", name="bit_shutter")
        bit_shutter.close_value = 0      # default
        bit_shutter.open_value = 1       # default
        bit_shutter.open()
        bit_shutter.close()
        
        # or, when used in a plan
        def planA():
            yield from mv(bit_shutter, "open")
            yield from mv(bit_shutter, "close")

    """
    signal = Component(EpicsSignal, "")


class DualPf4FilterBox(Device):
    """
    Dual Xia PF4 filter boxes using support from synApps (using Al, Ti foils)
    
    EXAMPLE::
    
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


class AD_EpicsHdf5FileName(FileStorePluginBase):
    """
    custom class to define image file name from EPICS
    
    .. caution:: *Caveat emptor* applies here.  You assume expertise!
    
    Replace standard Bluesky algorithm where file names
    are defined as UUID strings, virtually guaranteeing that 
    no existing images files will ever be overwritten.
    
    Also, this method decouples the data files from the databroker,
    which needs the files to be named by UUID.
    
    .. autosummary::
       
        ~make_filename
        ~generate_datum
        ~get_frames_per_point
        ~stage

    To allow users to control the file **name**,
    we override the ``make_filename()`` method here
    and we need to override some intervening classes.

    To allow users to control the file **number**,
    we override the ``stage()`` method here
    and triple-comment out that line, and bring in
    sections from the methods we are replacing here.

    The image file name is set in `FileStoreBase.make_filename()` 
    from `ophyd.areadetector.filestore_mixins`.  This is called 
    (during device staging) from `FileStoreBase.stage()`
    
    EXAMPLE:

    To use this custom class, we need to connect it to some
    intervening structure.  Here are the steps:
    
    #. override default file naming
    #. use to make your custom iterative writer
    #. use to make your custom HDF5 plugin
    #. use to make your custom AD support
    
    imports::

        from bluesky import RunEngine, plans as bp
        from ophyd.areadetector import SimDetector, SingleTrigger
        from ophyd.areadetector import ADComponent, ImagePlugin, SimDetectorCam
        from ophyd.areadetector import HDF5Plugin
        from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
    
    override default file naming::
        
        from apstools.devices import AD_EpicsHdf5FileName
    
    make a custom iterative writer::
        
        class myHdf5EpicsIterativeWriter(AD_EpicsHdf5FileName, FileStoreIterativeWrite): pass
    
    make a custom HDF5 plugin::
        
        class myHDF5FileNames(HDF5Plugin, myHdf5EpicsIterativeWriter): pass
    
    define support for the detector (simulated detector here)::
        
        class MySimDetector(SingleTrigger, SimDetector):
            '''SimDetector with HDF5 file names specified by EPICS'''
            
            cam = ADComponent(SimDetectorCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            
            hdf1 = ADComponent(
                myHDF5FileNames, 
                suffix = "HDF1:", 
                root = "/",
                write_path_template = "/",
                )
    
    create an instance of the detector::
        
        simdet = MySimDetector("13SIM1:", name="simdet")
        if hasattr(simdet.hdf1.stage_sigs, "array_counter"):
            # remove this so array counter is not set to zero each staging
            del simdet.hdf1.stage_sigs["array_counter"]
        simdet.hdf1.stage_sigs["file_template"] = '%s%s_%3.3d.h5'
    
    setup the file names using the EPICS HDF5 plugin::
        
        simdet.hdf1.file_path.put("/tmp/simdet_demo/")    # ! ALWAYS end with a "/" !
        simdet.hdf1.file_name.put("test")
        simdet.hdf1.array_counter.put(0)
    
    If you have not already, create a bluesky RunEngine::
        
        RE = RunEngine({})
    
    take an image::

        RE(bp.count([simdet]))
    
    INTERNAL METHODS
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
        
        logger.debug("make_filename:", hdf5_file_name)
        return super().generate_datum(key, timestamp, datum_kwargs)

    def get_frames_per_point(self):
        """overrides default behavior"""
        return self.num_capture.get()

    def stage(self):
        """
        overrides default behavior
        
        Set EPICS items before device is staged, then copy EPICS 
        naming template (and other items) to ophyd after staging.
        """
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

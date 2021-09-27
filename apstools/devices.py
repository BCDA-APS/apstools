"""
(ophyd) Devices that might be useful at the APS using Bluesky

APS GENERAL SUPPORT

.. autosummary::

    ~apstools._devices.aps_cycle.ApsCycleComputedRO
    ~apstools._devices.aps_cycle.ApsCycleDM
    ~apstools._devices.aps_machine.ApsMachineParametersDevice
    ~apstools._devices.shutters.ApsPssShutter
    ~apstools._devices.shutters.ApsPssShutterWithStatus
    ~apstools._devices.shutters.SimulatedApsPssShutterWithStatus

AREA DETECTOR SUPPORT

.. autosummary::

    ~AD_EpicsHdf5FileName
    ~AD_EpicsJpegFileName
    ~AD_plugin_primed
    ~AD_prime_plugin
    ~AD_setup_FrameType

DETECTOR / SCALER SUPPORT

.. autosummary::

    ~Struck3820
    ~use_EPICS_scaler_channels

MOTORS, POSITIONERS, AXES, ...

.. autosummary::

    ~AxisTunerException
    ~AxisTunerMixin
    ~EpicsDescriptionMixin
    ~EpicsMotorDialMixin
    ~EpicsMotorEnableMixin
    ~EpicsMotorLimitsMixin
    ~EpicsMotorRawMixin
    ~EpicsMotorResolutionMixin
    ~EpicsMotorServoMixin
    ~apstools._devices.shutters.EpicsMotorShutter
    ~apstools._devices.shutters.EpicsOnOffShutter

SHUTTERS

.. autosummary::

    ~apstools._devices.shutters.ApsPssShutter
    ~apstools._devices.shutters.ApsPssShutterWithStatus
    ~apstools._devices.shutters.EpicsMotorShutter
    ~apstools._devices.shutters.EpicsOnOffShutter
    ~apstools._devices.shutters.OneSignalShutter
    ~apstools._devices.shutters.ShutterBase
    ~apstools._devices.shutters.SimulatedApsPssShutterWithStatus

synApps Support

    See separate :ref:`synApps` section.

OTHER SUPPORT

.. autosummary::

    ~apstools._devices.aps_bss_user.ApsBssUserInfoDevice
    ~DualPf4FilterBox
    ~EpicsDescriptionMixin
    ~KohzuSeqCtl_Monochromator
    ~ProcessController
    ~Struck3820

Internal routines

.. autosummary::

    ~apstools._devices.aps_machine.ApsOperatorMessagesDevice
    ~apstools._devices.tracking_signal.TrackingSignal
    ~DeviceMixinBase

"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------


from collections import OrderedDict
from datetime import datetime
import epics
import itertools
import logging
import numpy as np
import time
import warnings

from ophyd import Component, Device, DeviceStatus
from ophyd import Signal, EpicsSignal, EpicsSignalRO
from ophyd.mca import EpicsMCARecord
from ophyd.scaler import EpicsScaler, ScalerCH

from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase
from ophyd.utils import set_and_wait

from bluesky import plan_stubs as bps

# pull up submodule features for: from apstools.devices import XYZ
from ._devices.aps_cycle import ApsCycleComputedRO
from ._devices.aps_cycle import ApsCycleDM
from ._devices.aps_machine import ApsMachineParametersDevice
from ._devices.aps_machine import ApsOperatorMessagesDevice
from ._devices.shutters import ApsPssShutter
from ._devices.shutters import ApsPssShutterWithStatus
from ._devices.shutters import EpicsMotorShutter
from ._devices.shutters import EpicsOnOffShutter
from ._devices.shutters import OneSignalShutter
from ._devices.shutters import ShutterBase
from ._devices.shutters import SimulatedApsPssShutterWithStatus
from ._devices.tracking_signal import TrackingSignal
from ._devices.aps_bss_user import ApsBssUserInfoDevice
from .synApps import *


logger = logging.getLogger(__name__)


# for convenience
SCALER_AUTOCOUNT_MODE = 1  # TODO: contribute to ophyd?


def use_EPICS_scaler_channels(scaler):
    """
    configure scaler for only the channels with names assigned in EPICS

    Note: For `ScalerCH`, use `scaler.select_channels(None)` instead of this code.
    (Applies only to `ophyd.scaler.ScalerCH` in releases after 2019-02-27.)
    """
    if isinstance(scaler, EpicsScaler):
        read_attrs = []
        for ch in scaler.channels.component_names:
            _nam = epics.caget(f"{scaler.prefix}.NM{int(ch[4:])}")
            if len(_nam.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs
    elif isinstance(scaler, ScalerCH):
        # superceded by: https://github.com/NSLS-II/ophyd/commit/543e7ef81f3cb760192a0de719e51f9359642ae8
        scaler.match_names()
        read_attrs = []
        configuration_attrs = []
        for ch in scaler.channels.component_names:
            nm_pv = scaler.channels.__getattribute__(ch)
            if nm_pv is not None and len(nm_pv.chname.get().strip()) > 0:
                read_attrs.append(ch)
                configuration_attrs.append(ch)
                configuration_attrs.append(ch + ".chname")
                configuration_attrs.append(ch + ".preset")
                configuration_attrs.append(ch + ".gate")
        scaler.channels.read_attrs = read_attrs
        scaler.channels.configuration_attrs = configuration_attrs


class DeviceMixinBase(Device):
    """
    Base class for apstools Device mixin classes

    .. index:: Ophyd Device Mixin; DeviceMixinBase
    """


class AxisTunerException(ValueError):
    """
    Exception during execution of `AxisTunerBase` subclass

    .. index:: Ophyd Exception; AxisTunerException
    """


class AxisTunerMixin(DeviceMixinBase):
    """
    Mixin class to provide tuning capabilities for an axis

    .. index:: Ophyd Device Mixin; AxisTunerMixin

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

        def tune_myaxis():
            yield from myaxis.tune(md={"plan_name": "tune_myaxis"})

        RE(tune_myaxis())
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuner = None  # such as: apstools.plans.TuneAxis

        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method

    def _default_pre_tune_method(self):
        """called before `tune()`"""
        logger.info(
            "{} position before tuning: {}".format(
                self.name, self.position
            )
        )
        yield from bps.null()

    def _default_post_tune_method(self):
        """called after `tune()`"""
        logger.info(
            "{} position after tuning: {}".format(self.name, self.position)
        )
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


class EpicsDescriptionMixin(DeviceMixinBase):
    """
    add a record's description field to a Device, such as EpicsMotor

    .. index:: Ophyd Device Mixin; EpicsDescriptionMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsDescriptionMixin

        class myEpicsMotor(EpicsDescriptionMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
        print(m1.desc.get())

    more ideas::

        class TunableSynAxis(AxisTunerMixin, SynAxis):
            '''synthetic axis that can be tuned'''
        class TunableEpicsMotor(AxisTunerMixin, EpicsMotor):
            '''EpicsMotor that can be tuned'''
        class EpicsMotorWithDescription(EpicsDescriptionMixin, EpicsMotor):
            '''EpicsMotor with description field'''

        class EpicsMotorWithMore(
            EpicsDescriptionMixin,
            EpicsMotorLimitsMixin,
            EpicsMotorDialMixin,
            EpicsMotorRawMixin,
            EpicsMotor):
            '''
            EpicsMotor with more fields

            * description (``desc``)
            * soft motor limits (``soft_limit_hi``, ``soft_limit_lo``)
            * dial coordinates (``dial``)
            * raw coordinates (``raw``)
            '''
    """

    desc = Component(EpicsSignal, ".DESC")


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
            if (
                self.connected
                and old_value is not None
                and value != old_value
            ):
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


class DualPf4FilterBox(Device):
    """
    Dual Xia PF4 filter boxes using support from synApps (using Al, Ti foils)

    .. index:: Ophyd Device; DualPf4FilterBox

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


class KohzuSeqCtl_Monochromator(Device):
    """
    synApps Kohzu double-crystal monochromator sequence control program

    .. index:: Ophyd Device; KohzuSeqCtl_Monochromator
    """

    # lambda is reserved word in Python, can't use it
    wavelength = Component(
        EpicsSignal, "BraggLambdaRdbkAO", write_pv="BraggLambdaAO"
    )
    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO")
    theta = Component(
        EpicsSignal, "BraggThetaRdbkAO", write_pv="BraggThetaAO"
    )
    y1 = Component(EpicsSignalRO, "KohzuYRdbkAI")
    z2 = Component(EpicsSignalRO, "KohzuZRdbkAI")
    message2 = Component(EpicsSignalRO, "KohzuSeqMsg2SI")
    operator_acknowledge = Component(EpicsSignal, "KohzuOperAckBO")
    use_set = Component(EpicsSignal, "KohzuUseSetBO")
    mode = Component(EpicsSignal, "KohzuModeBO")
    move_button = Component(EpicsSignal, "KohzuPutBO")
    moving = Component(EpicsSignal, "KohzuMoving")
    y_offset = Component(EpicsSignal, "Kohzu_yOffsetAO")

    crystal_mode = Component(EpicsSignal, "KohzuMode2MO")
    crystal_h = Component(EpicsSignal, "BraggHAO")
    crystal_k = Component(EpicsSignal, "BraggKAO")
    crystal_l = Component(EpicsSignal, "BraggLAO")
    crystal_lattice_constant = Component(EpicsSignal, "BraggAAO")
    crystal_2d_spacing = Component(EpicsSignal, "Bragg2dSpacingAO")
    crystal_type = Component(EpicsSignal, "BraggTypeMO")

    def move_energy(self, energy):
        """for command-line use:  ``kohzu_mono.energy_move(8.2)``"""
        self.energy.put(energy)
        self.move_button.put(1)

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        PARAMETERS

        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put("Set")
        self.energy.put(value)
        self.use_set.put("Use")


class ProcessController(Device):
    """
    DEPRECATED (1.5.1): Use ``ophyd.PVPositioner`` instead.

    For the controlled signal (such as temperature), use ``ophyd.PVPositioner``.
    Include this within an ``ophyd.Device`` as appropriate.

    Common parts of a process controller support.

    .. index:: Ophyd Device; ProcessController

    A process controller keeps a signal (a readback value such as
    temperature, vacuum, himdity, etc.) as close as possible
    to a target (set point) value.  It has additional fields
    that describe parameters specific to the controller such
    as PID loop, on/off, applied controller power, and other
    details.

    This is a base class to standardize the few common terms
    used to command and record the target and readback values
    of a process controller.

    Subclasses should redefine (override) `controller_name`,
    ``signal``, ``target``, and ``units`` such as the example below.
    Also set values for ``tolerance``, ``report_interval_s``, and
    ``poll_s`` suitable for the specific controller used.

    *Floats*: ``signal``, ``target``, and ``tolerance`` will be
    considered as floating point numbers in the code.

    It is assumed in :meth:`settled()` that: ``|signal - target| <= tolerance``.
    Override this *property* method if a different decision is needed.

    EXAMPLE::

        class MyLinkam(ProcessController):
            controller_name = "MyLinkam Controller"
            signal = Component(EpicsSignalRO, "temp")
            target = Component(EpicsSignal, "setLimit", kind="omitted")
            units = Component(Signal, kind="omitted", value="C")

        controller = MyLinkam("my:linkam:", name="controller")
        RE(controller.wait_until_settled(timeout=10))

        controller.record_signal()
        print(f"{controller.controller_name} settled? {controller.settled}")

        def rampUp_rampDown():
            '''ramp temperature up, then back down'''
            yield from controller.set_target(25, timeout=180)
            controller.report_interval_s = 10    # change report interval to 10s
            for i in range(10, 0, -1):
                print(f"hold at {self.get():.2f}{self.units.get()}, time remaining: {i}s")
                yield from bps.sleep(1)
            yield from controller.set_target(0, timeout=180)

        RE(test_plan())

    """

    controller_name = "ProcessController"
    signal = Component(Signal)  # override in subclass
    target = Component(Signal, kind="omitted")  # override in subclass
    tolerance = Component(
        Signal, kind="omitted", value=1
    )  # override in subclass
    units = Component(
        Signal, kind="omitted", value=""
    )  # override in subclass

    report_interval_s = 5  # time between reports during loop, s
    poll_s = 0.02  # time to wait during polling loop, s

    def record_signal(self):
        """write signal to the console"""
        msg = f"{self.controller_name} signal: {self.get():.2f}{self.units.get()}"
        print(msg)
        return msg

    def set_target(
        self, target, wait=True, timeout=None, timeout_fail=False
    ):
        """plan: change controller to new signal set point"""
        yield from bps.mv(self.target, target)

        msg = f"Set {self.controller_name} target to {target:.2f}{self.units.get()}"
        print(msg)

        if wait:
            yield from self.wait_until_settled(
                timeout=timeout, timeout_fail=timeout_fail
            )

    @property
    def value(self):
        """shortcut to self.signal.get()"""
        return self.signal.get()

    @property
    def settled(self):
        """Is signal close enough to target?"""
        diff = abs(self.signal.get() - self.target.get())
        return diff <= self.tolerance.get()

    def wait_until_settled(self, timeout=None, timeout_fail=False):
        """
        plan: wait for controller signal to reach target within tolerance
        """
        # see: https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
        t0 = time.time()
        _st = DeviceStatus(self.signal)

        if self.settled:
            # just in case signal already at target
            _st._finished(success=True)
        else:
            started = False

            def changing_cb(*args, **kwargs):
                if started and self.settled:
                    _st._finished(success=True)

            token = self.signal.subscribe(changing_cb)
            started = True
            report = 0
            while not _st.done and not self.settled:
                elapsed = time.time() - t0
                if timeout is not None and elapsed > timeout:
                    _st._finished(success=self.settled)
                    msg = (
                        f"{self.controller_name} Timeout after {elapsed:.2f}s"
                        f", target {self.target.get():.2f}{self.units.get()}"
                        f", now {self.signal.get():.2f}{self.units.get()}"
                    )
                    print(msg)
                    if timeout_fail:
                        raise TimeoutError(msg)
                    continue
                if elapsed >= report:
                    report += self.report_interval_s
                    msg = (
                        f"Waiting {elapsed:.1f}s"
                        f" to reach {self.target.get():.2f}{self.units.get()}"
                        f", now {self.signal.get():.2f}{self.units.get()}"
                    )
                    print(msg)
                yield from bps.sleep(self.poll_s)

            self.signal.unsubscribe(token)

        self.record_signal()
        elapsed = time.time() - t0
        print(f"Total time: {elapsed:.3f}s, settled:{_st.success}")


class Struck3820(Device):
    """
    Struck/SIS 3820 Multi-Channel Scaler (as used by USAXS)

    .. index:: Ophyd Device; Struck3820
    """

    start_all = Component(EpicsSignal, "StartAll")
    stop_all = Component(EpicsSignal, "StopAll")
    erase_start = Component(EpicsSignal, "EraseStart")
    erase_all = Component(EpicsSignal, "EraseAll")
    mca1 = Component(EpicsMCARecord, "mca1")
    mca2 = Component(EpicsMCARecord, "mca2")
    mca3 = Component(EpicsMCARecord, "mca3")
    mca4 = Component(EpicsMCARecord, "mca4")
    clock_frequency = Component(EpicsSignalRO, "clock_frequency")
    current_channel = Component(EpicsSignalRO, "CurrentChannel")
    channel_max = Component(EpicsSignalRO, "MaxChannels")
    channels_used = Component(EpicsSignal, "NuseAll")
    elapsed_real_time = Component(EpicsSignalRO, "ElapsedReal")
    preset_real_time = Component(EpicsSignal, "PresetReal")
    dwell_time = Component(EpicsSignal, "Dwell")
    prescale = Component(EpicsSignal, "Prescale")
    acquiring = Component(EpicsSignalRO, "Acquiring", string=True)
    acquire_mode = Component(EpicsSignalRO, "AcquireMode", string=True)
    model = Component(EpicsSignalRO, "Model", string=True)
    firmware = Component(EpicsSignalRO, "Firmware")
    channel_advance = Component(EpicsSignal, "ChannelAdvance")
    count_on_start = Component(EpicsSignal, "CountOnStart")
    software_channel_advance = Component(
        EpicsSignal, "SoftwareChannelAdvance"
    )
    channel1_source = Component(EpicsSignal, "Channel1Source")
    user_led = Component(EpicsSignal, "UserLED")
    mux_output = Component(EpicsSignal, "MUXOutput")
    input_mode = Component(EpicsSignal, "InputMode")
    output_mode = Component(EpicsSignal, "OutputMode")
    output_polarity = Component(EpicsSignal, "OutputPolarity")
    read_rate = Component(EpicsSignal, "ReadAll.SCAN")
    do_readl_all = Component(EpicsSignal, "DoReadAll")


# AreaDetector support

AD_FrameType_schemes = {
    "reset": dict(  # default names from Area Detector code
        ZRST="Normal", ONST="Background", TWST="FlatField",
    ),
    "NeXus": dict(  # NeXus (typical locations)
        ZRST="/entry/data/data",
        ONST="/entry/data/dark",
        TWST="/entry/data/white",
    ),
    "DataExchange": dict(  # APS Data Exchange
        ZRST="/exchange/data",
        ONST="/exchange/data_dark",
        TWST="/exchange/data_white",
    ),
}


def AD_setup_FrameType(prefix, scheme="NeXus"):
    """
    configure so frames are identified & handled by type (dark, white, or image)

    PARAMETERS

        prefix
            *str* :
            EPICS PV prefix of area detector, such as ``13SIM1:``
        scheme
            *str* :
            any key in the ``AD_FrameType_schemes`` dictionary

    This routine prepares the EPICS Area Detector to identify frames
    by image type for handling by clients, such as the HDF5 file writing plugin.
    With the HDF5 plugin, the ``FrameType`` PV is added to the NDattributes
    and then used in the layout file to direct the acquired frame to
    the chosen dataset.  The ``FrameType`` PV value provides the HDF5 address
    to be used.

    To use a different scheme than the defaults, add a new key to
    the ``AD_FrameType_schemes`` dictionary, defining storage values for the
    fields of the EPICS ``mbbo`` record that you will be using.

    see: https://nbviewer.jupyter.org/github/BCDA-APS/use_bluesky/blob/main/lessons/sandbox/images_darks_flats.ipynb

    EXAMPLE::

        AD_setup_FrameType("2bmbPG3:", scheme="DataExchange")

    * Call this function *before* creating the ophyd area detector object
    * use lower-level PyEpics interface
    """
    db = AD_FrameType_schemes.get(scheme)
    if db is None:
        raise ValueError(
            f"unknown AD_FrameType_schemes scheme: {scheme}"
            "\n Should be one of: " + ", ".join(
                AD_FrameType_schemes.keys()
            )
        )

    template = "{}cam1:FrameType{}.{}"
    for field, value in db.items():
        epics.caput(template.format(prefix, "", field), value)
        epics.caput(template.format(prefix, "_RBV", field), value)


def AD_plugin_primed(plugin):
    """
    Has area detector pushed an NDarray to the file writer plugin?  True or False

    PARAMETERS

    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_plugin_primed(detector.hdf1)

    Works around an observed issue: #598
    https://github.com/NSLS-II/ophyd/issues/598#issuecomment-414311372

    If detector IOC has just been started and has not yet taken an image
    with the file writer plugin, then a TimeoutError will occur as the
    file writer plugin "Capture" is set to 1 (Start).  In such case,
    first acquire at least one image with the file writer plugin enabled.

    Also issue in apstools (needs a robust method to detect if primed):
    https://github.com/BCDA-APS/apstools/issues/464

    Since Area Detector release 2.1 (2014-10-14).

    The *prime* process is not needed if you select the
    *LazyOpen* feature with *Stream* mode for the file plugin.
    *LazyOpen* defers file creation until the first frame arrives
    in the plugin. This removes the need to initialize the plugin
    with a dummy frame before starting capture.
    """
    cam = plugin.parent.cam
    tests = []

    for obj in (cam, plugin):
        test = np.array(obj.array_size.get()).sum() != 0
        tests.append(test)
        if not test:
            logger.debug("'%s' image size is zero", obj.name)

    checks = dict(array_size=False, color_mode=True, data_type=True,)
    for key, as_string in checks.items():
        c = getattr(cam, key).get(as_string=as_string)
        p = getattr(plugin, key).get(as_string=as_string)
        test = c == p
        tests.append(test)
        if not test:
            logger.debug("%s does not match", key)

    return False not in tests


def AD_prime_plugin(detector, plugin):
    """
    Prime this area detector's file writer plugin.

    PARAMETERS

    detector
        *obj* :
        area detector (such as ``detector``)
    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_prime_plugin(detector, detector.hdf1)
    """
    nm = f"{plugin.parent.name}.{plugin.attr_name}"
    warnings.warn(f"Use AD_prime_plugin2({nm}) instead.")
    AD_prime_plugin2(plugin)


def AD_prime_plugin2(plugin):
    """
    Prime this area detector's file writer plugin.

    Collect and push an NDarray to the file writer plugin.
    Works with all file writer plugins.

    Based on ``ophyd.areadetector.plugins.HDF5Plugin.warmup()``.

    PARAMETERS

    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_prime_plugin2(detector.hdf1)

    """
    if AD_plugin_primed(plugin):
        logger.debug("'%s' plugin is already primed", plugin.name)
        return

    sigs = OrderedDict(
        [
            (plugin.enable, 1),
            (plugin.parent.cam.array_callbacks, 1),  # set by number
            (plugin.parent.cam.image_mode, 0),  # Single, set by number
            # Trigger mode names are not identical for every camera.
            # Assume here that the first item in the list is
            # the best default choice to prime the plugin.
            (plugin.parent.cam.trigger_mode, 0),  # set by number
            # just in case the acquisition time is set very long...
            (plugin.parent.cam.acquire_time, 1),
            (plugin.parent.cam.acquire_period, 1),
            (plugin.parent.cam.acquire, 1),  # set by number
        ]
    )

    original_vals = {sig: sig.get() for sig in sigs}

    for sig, val in sigs.items():
        time.sleep(0.1)  # abundance of caution
        set_and_wait(sig, val)

    time.sleep(2)  # wait for acquisition

    for sig, val in reversed(list(original_vals.items())):
        time.sleep(0.1)
        set_and_wait(sig, val)


class AD_EpicsHdf5FileName(
    FileStorePluginBase
):  # lgtm [py/missing-call-to-init]
    """
    custom class to define image file name from EPICS

    .. index:: Ophyd Device Support; AD_EpicsHdf5FileName

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
        FileStorePluginBase.__init__(self, *args, **kwargs)
        self.filestore_spec = "AD_HDF5"  # spec name stored in resource doc
        self.stage_sigs.update(
            [
                ("file_template", "%s%s_%4.4d.h5"),
                ("file_write_mode", "Stream"),
                ("capture", 1),
            ]
        )

    def make_filename(self):
        """
        overrides default behavior: Get info from EPICS HDF5 plugin.
        """
        # start of the file name, file number will be appended per template
        filename = self.file_name.get()

        # this is where the HDF5 plugin will write the image,
        # relative to the IOC's filesystem
        write_path = self.file_path.get()

        # this is where the DataBroker will find the image,
        # on a filesystem accessible to Bluesky
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

        logger.debug("make_filename: %s", hdf5_file_name)
        logger.debug("write_path: %s", write_path)
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
        # set_and_wait(self.file_number, 0)

        # get file number now since it is incremented during stage()
        file_number = self.file_number.get()
        # Must avoid parent's stage() since it sets file_number to 0
        # Want to call grandparent's stage()
        # super().stage()     # avoid this - sets `file_number` to zero
        # call grandparent.stage()
        FileStoreBase.stage(self)

        # AD does the file name templating in C
        # We can't access that result until after acquisition
        # so we apply the same template here in Python.
        template = self.file_template.get()
        self._fn = template % (read_path, filename, file_number)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError(
                f"Path {self.file_path.get()} does not exist on IOC."
            )

        self._point_counter = itertools.count()

        # from FileStoreHDF5.stage()
        res_kwargs = {"frame_per_point": self.get_frames_per_point()}
        self._generate_resource(res_kwargs)


class AD_EpicsJpegFileName(
    FileStorePluginBase
):  # lgtm [py/missing-call-to-init]

    """
    custom class to define image file name from EPICS

    .. index:: Ophyd Device Support; AD_EpicsJpegFileName

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

    Patterned on ``apstools.devices.AD_EpicsHdf5FileName()``.
    (Follow that documentation from this point.)
    """

    def __init__(self, *args, **kwargs):
        FileStorePluginBase.__init__(self, *args, **kwargs)
        # TODO: taking a guess here, it's needed if databroker is to *read* the image file
        # If we get this wrong, we have to update any existing runs before
        # databroker can read them into memory.  If there is not such symbol
        # defined, it's up to somone who wants to read these images with databroker.
        self.filestore_spec = "AD_JPEG"  # spec name stored in resource doc
        self.stage_sigs.update(
            [
                ("file_template", "%s%s_%4.4d.jpg"),
                ("file_write_mode", "Stream"),
                ("capture", 1),
            ]
        )

    def make_filename(self):
        """
        overrides default behavior: Get info from EPICS JPEG plugin.
        """
        # start of the file name, file number will be appended per template
        filename = self.file_name.get()

        # this is where the JPEG plugin will write the image,
        # relative to the IOC's filesystem
        write_path = self.file_path.get()

        # this is where the DataBroker will find the image,
        # on a filesystem accessible to Bluesky
        read_path = write_path

        return filename, read_path, write_path

    def generate_datum(self, key, timestamp, datum_kwargs):
        """Generate a uid and cache it with its key for later insertion."""
        template = self.file_template.get()
        filename, read_path, write_path = self.make_filename()
        file_number = self.file_number.get()
        jpeg_file_name = template % (read_path, filename, file_number)

        # inject the actual name of the JPEG file here into datum_kwargs
        datum_kwargs["JPEG_file_name"] = jpeg_file_name

        logger.debug("make_filename: %s", jpeg_file_name)
        logger.debug("write_path: %s", write_path)
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
        # set_and_wait(self.file_number, 0)

        # get file number now since it is incremented during stage()
        file_number = self.file_number.get()
        # Must avoid parent's stage() since it sets file_number to 0
        # Want to call grandparent's stage()
        # super().stage()     # avoid this - sets `file_number` to zero
        # call grandparent.stage()
        FileStoreBase.stage(self)

        # AD does the file name templating in C
        # We can't access that result until after acquisition
        # so we apply the same template here in Python.
        template = self.file_template.get()
        self._fn = template % (read_path, filename, file_number)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError(
                "Path {} does not exist on IOC.".format(
                    self.file_path.get()
                )
            )

        self._point_counter = itertools.count()

        # from FileStoreHDF5.stage()
        res_kwargs = {"frame_per_point": self.get_frames_per_point()}
        self._generate_resource(res_kwargs)

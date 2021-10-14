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

    ~apstools._devices.area_detector_support.AD_EpicsHdf5FileName
    ~apstools._devices.area_detector_support.AD_EpicsJpegFileName
    ~apstools._devices.area_detector_support.AD_plugin_primed
    ~apstools._devices.area_detector_support.AD_prime_plugin
    ~apstools._devices.area_detector_support.AD_setup_FrameType

DETECTOR / SCALER SUPPORT

.. autosummary::

    ~apstools._devices.struck3820.Struck3820
    ~apstools._devices.scaler_support.use_EPICS_scaler_channels

MOTORS, POSITIONERS, AXES, ...

.. autosummary::

    ~apstools._devices.axis_tuner.AxisTunerException
    ~apstools._devices.axis_tuner.AxisTunerMixin
    ~apstools._devices.description_mixin.EpicsDescriptionMixin
    ~apstools._devices.motor_mixins.EpicsMotorDialMixin
    ~apstools._devices.motor_mixins.EpicsMotorEnableMixin
    ~apstools._devices.motor_mixins.EpicsMotorLimitsMixin
    ~apstools._devices.motor_mixins.EpicsMotorRawMixin
    ~apstools._devices.motor_mixins.EpicsMotorResolutionMixin
    ~apstools._devices.motor_mixins.EpicsMotorServoMixin
    ~apstools._devices.positioner_soft_done.PVPositionerSoftDone
    ~apstools._devices.positioner_soft_done.PVPositionerSoftDoneWithStop
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

TEMPERATURE CONTROLLERS

.. autosummary::

    ~apstools._devices.linkam_controllers.Linkam_CI94_Device
    ~apstools._devices.linkam_controllers.Linkam_T96_Device
    ~apstools._devices.ptc10_controller.PTC10AioChannel
    ~apstools._devices.ptc10_controller.PTC10RtdChannel
    ~apstools._devices.ptc10_controller.PTC10TcChannel
    ~apstools._devices.ptc10_controller.PTC10PositionerMixin

OTHER SUPPORT

.. autosummary::

    ~apstools._devices.aps_bss_user.ApsBssUserInfoDevice
    ~apstools._devices.xia_pf4.Pf4FilterSingle
    ~apstools._devices.xia_pf4.Pf4FilterDual
    ~apstools._devices.xia_pf4.Pf4FilterTriple
    ~apstools._devices.xia_pf4.Pf4FilterBank
    ~apstools._devices.xia_pf4.Pf4FilterCommon
    ~apstools._devices.xia_pf4.DualPf4FilterBox
    ~apstools._devices.description_mixin.EpicsDescriptionMixin
    ~apstools._devices.kohzu_monochromator.KohzuSeqCtl_Monochromator
    ~apstools._devices.srs570_preamplifier.SRS570_PreAmplifier
    ~apstools._devices.struck3820.Struck3820
    ~ProcessController

Internal routines

.. autosummary::

    ~apstools._devices.aps_machine.ApsOperatorMessagesDevice
    ~apstools._devices.tracking_signal.TrackingSignal
    ~apstools._devices.mixin_base.DeviceMixinBase

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

import time

from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import Signal

from bluesky import plan_stubs as bps

# pull up submodule features for: from apstools.devices import XYZ
from ._devices import *
from .synApps import *


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

"""
(ophyd) Devices that might be useful at the APS using Bluesky

.. _devices.aps_support:

APS GENERAL SUPPORT

.. autosummary::

    ~apstools._devices.aps_cycle.ApsCycleDM
    ~apstools._devices.aps_machine.ApsMachineParametersDevice
    ~apstools._devices.shutters.ApsPssShutter
    ~apstools._devices.shutters.ApsPssShutterWithStatus
    ~apstools._devices.shutters.SimulatedApsPssShutterWithStatus

.. _devices.area_detector:

AREA DETECTOR SUPPORT

.. autosummary::

    ~apstools._devices.area_detector_support.AD_EpicsHdf5FileName
    ~apstools._devices.area_detector_support.AD_EpicsJpegFileName
    ~apstools._devices.area_detector_support.AD_plugin_primed
    ~apstools._devices.area_detector_support.AD_prime_plugin
    ~apstools._devices.area_detector_support.AD_setup_FrameType

.. _devices.scalers:

DETECTOR / SCALER SUPPORT

.. autosummary::

    ~apstools._devices.struck3820.Struck3820
    ~apstools._devices.scaler_support.use_EPICS_scaler_channels

.. _devices.motors:

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

.. _devices.shutters:


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

.. _devices.temperature_controllers:

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

Internal routines

.. autosummary::

    ~apstools._devices.aps_machine.ApsOperatorMessagesDevice
    ~apstools._devices.tracking_signal.TrackingSignal
    ~apstools._devices.mixin_base.DeviceMixinBase

"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
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

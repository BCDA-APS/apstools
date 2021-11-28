.. _devices:

=======
Devices
=======

(ophyd) Devices that might be useful at the APS using Bluesky

Also consult the :ref:`Index <genindex>` under the *Ophyd* heading for
links to the Devices, Exceptions, Mixins, Signals, and other support
items described here.

Categories
----------

.. _devices.aps_support:

APS GENERAL SUPPORT
+++++++++++++++++++

.. autosummary::

    ~apstools.devices.aps_cycle.ApsCycleDM
    ~apstools.devices.aps_machine.ApsMachineParametersDevice
    ~apstools.devices.shutters.ApsPssShutter
    ~apstools.devices.shutters.ApsPssShutterWithStatus
    ~apstools.devices.shutters.SimulatedApsPssShutterWithStatus

.. _devices.area_detector:

AREA DETECTOR SUPPORT
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.area_detector_support.AD_EpicsHdf5FileName
    ~apstools.devices.area_detector_support.AD_EpicsJpegFileName
    ~apstools.devices.area_detector_support.AD_plugin_primed
    ~apstools.devices.area_detector_support.AD_prime_plugin
    ~apstools.devices.area_detector_support.AD_setup_FrameType

.. _devices.scalers:

DETECTOR / SCALER SUPPORT
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.struck3820.Struck3820
    ~apstools.devices.scaler_support.use_EPICS_scaler_channels

.. _devices.motors:

MOTORS, POSITIONERS, AXES, ...
+++++++++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.axis_tuner.AxisTunerException
    ~apstools.devices.axis_tuner.AxisTunerMixin
    ~apstools.devices.description_mixin.EpicsDescriptionMixin
    ~apstools.devices.motor_mixins.EpicsMotorDialMixin
    ~apstools.devices.motor_mixins.EpicsMotorEnableMixin
    ~apstools.devices.motor_mixins.EpicsMotorLimitsMixin
    ~apstools.devices.motor_mixins.EpicsMotorRawMixin
    ~apstools.devices.motor_mixins.EpicsMotorResolutionMixin
    ~apstools.devices.motor_mixins.EpicsMotorServoMixin
    ~apstools.devices.positioner_soft_done.PVPositionerSoftDone
    ~apstools.devices.positioner_soft_done.PVPositionerSoftDoneWithStop
    ~apstools.devices.shutters.EpicsMotorShutter
    ~apstools.devices.shutters.EpicsOnOffShutter

.. _devices.shutters:

SHUTTERS
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.shutters.ApsPssShutter
    ~apstools.devices.shutters.ApsPssShutterWithStatus
    ~apstools.devices.shutters.EpicsMotorShutter
    ~apstools.devices.shutters.EpicsOnOffShutter
    ~apstools.devices.shutters.OneSignalShutter
    ~apstools.devices.shutters.ShutterBase
    ~apstools.devices.shutters.SimulatedApsPssShutterWithStatus

synApps Support
++++++++++++++++++++

    See separate :ref:`synApps` section.

.. _devices.temperature_controllers:

TEMPERATURE CONTROLLERS
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.linkam_controllers.Linkam_CI94_Device
    ~apstools.devices.linkam_controllers.Linkam_T96_Device
    ~apstools.devices.ptc10_controller.PTC10AioChannel
    ~apstools.devices.ptc10_controller.PTC10RtdChannel
    ~apstools.devices.ptc10_controller.PTC10TcChannel
    ~apstools.devices.ptc10_controller.PTC10PositionerMixin

OTHER SUPPORT
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.aps_bss_user.ApsBssUserInfoDevice
    ~apstools.devices.xia_pf4.Pf4FilterSingle
    ~apstools.devices.xia_pf4.Pf4FilterDual
    ~apstools.devices.xia_pf4.Pf4FilterTriple
    ~apstools.devices.xia_pf4.Pf4FilterBank
    ~apstools.devices.xia_pf4.Pf4FilterCommon
    ~apstools.devices.xia_pf4.DualPf4FilterBox
    ~apstools.devices.description_mixin.EpicsDescriptionMixin
    ~apstools.devices.kohzu_monochromator.KohzuSeqCtl_Monochromator
    ~apstools.devices.srs570_preamplifier.SRS570_PreAmplifier
    ~apstools.devices.struck3820.Struck3820

Internal routines
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.aps_machine.ApsOperatorMessagesDevice
    ~apstools.devices.tracking_signal.TrackingSignal
    ~apstools.devices.mixin_base.DeviceMixinBase

All Submodules
--------------

.. automodule:: apstools.devices.aps_bss_user
    :members:

.. automodule:: apstools.devices.area_detector_support
    :members:

.. automodule:: apstools.devices.aps_cycle
    :members:

.. automodule:: apstools.devices.aps_machine
    :members:

.. automodule:: apstools.devices.aps_undulator
    :members:

.. automodule:: apstools.devices.axis_tuner
    :members:

.. automodule:: apstools.devices.description_mixin
    :members:

.. automodule:: apstools.devices.kohzu_monochromator
    :members:

.. automodule:: apstools.devices.linkam_controllers
    :members:

.. automodule:: apstools.devices.mixin_base
    :members:

.. automodule:: apstools.devices.motor_mixins
    :members:

.. automodule:: apstools.devices.positioner_soft_done
    :members:

.. automodule:: apstools.devices.preamp_base
    :members:

.. automodule:: apstools.devices.ptc10_controller
    :members:

.. automodule:: apstools.devices.scaler_support
    :members:

.. automodule:: apstools.devices.shutters
    :members:

.. automodule:: apstools.devices.srs570_preamplifier
    :members:

.. automodule:: apstools.devices.struck3820
    :members:

.. automodule:: apstools.devices.tracking_signal
    :members:

.. automodule:: apstools.devices.xia_pf4
    :members:

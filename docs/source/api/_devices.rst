.. _devices:

=======
Devices
=======

Devices (subclasses of ophyd's `Device`) that might be useful at the APS using
Bluesky.

Also consult the :ref:`Index <genindex>` under the *Ophyd* heading for
links to the Devices, Exceptions, Mixins, Signals, and other support
items described here.

Categories
----------

See these categories:

* :ref:`devices.aps_support`
* :ref:`devices.area_detector`
* :ref:`devices.motors`
* :ref:`devices.scalers`
* :ref:`devices.shutters`
* :ref:`devices.slits`
* :ref:`devices.temperature_controllers`
* :ref:`devices.other_support`

.. _devices.aps_support:

APS General Support
+++++++++++++++++++

.. autosummary::

    ~apstools.devices.aps_cycle.ApsCycleDM
    ~apstools.devices.aps_machine.ApsMachineParametersDevice
    ~apstools.devices.shutters.ApsPssShutter
    ~apstools.devices.shutters.ApsPssShutterWithStatus
    ~apstools.devices.shutters.SimulatedApsPssShutterWithStatus

.. _devices.area_detector:

Area Detector Support
+++++++++++++++++++++

.. autosummary::

    ~apstools.devices.area_detector_support.AD_EpicsFileNameHDF5Plugin
    ~apstools.devices.area_detector_support.AD_EpicsFileNameJPEGPlugin
    ~apstools.devices.area_detector_support.AD_EpicsFileNameTIFFPlugin
    ~apstools.devices.area_detector_support.AD_EpicsHdf5FileName
    ~apstools.devices.area_detector_support.AD_EpicsHDF5IterativeWriter
    ~apstools.devices.area_detector_support.AD_EpicsJPEGFileName
    ~apstools.devices.area_detector_support.AD_EpicsJPEGIterativeWriter
    ~apstools.devices.area_detector_support.AD_EpicsTIFFFileName
    ~apstools.devices.area_detector_support.AD_EpicsTIFFIterativeWriter
    ~apstools.devices.area_detector_support.AD_full_file_name_local
    ~apstools.devices.area_detector_support.AD_plugin_primed
    ~apstools.devices.area_detector_support.AD_prime_plugin2
    ~apstools.devices.area_detector_support.AD_setup_FrameType
    ~apstools.devices.area_detector_support.CamMixin_V34
    ~apstools.devices.area_detector_support.CamMixin_V3_1_1
    ~apstools.devices.area_detector_support.SingleTrigger_V34

.. _devices.scalers:

Detector & Scaler Support
+++++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.struck3820.Struck3820
    ~apstools.devices.scaler_support.use_EPICS_scaler_channels
    ~apstools.devices.synth_pseudo_voigt.SynPseudoVoigt

.. _devices.motors:

Motors, Positioners, Axes, ...
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

Shutters
++++++++

.. autosummary::

    ~apstools.devices.shutters.ApsPssShutter
    ~apstools.devices.shutters.ApsPssShutterWithStatus
    ~apstools.devices.shutters.EpicsMotorShutter
    ~apstools.devices.shutters.EpicsOnOffShutter
    ~apstools.devices.shutters.OneSignalShutter
    ~apstools.devices.shutters.ShutterBase
    ~apstools.devices.shutters.SimulatedApsPssShutterWithStatus

.. _devices.slits:

Slits
++++++++

.. autosummary::

    ~apstools.devices.xia_slit.XiaSlit2D
    ~apstools.synApps.db_2slit.Optics2Slit1D
    ~apstools.synApps.db_2slit.Optics2Slit2D_HV
    ~apstools.synApps.db_2slit.Optics2Slit2D_InbOutBotTop
    ~apstools.utils.slit_core.SlitGeometry

synApps Support
++++++++++++++++++++

    See separate :ref:`synApps` section.

.. _devices.temperature_controllers:

Temperature Controllers
+++++++++++++++++++++++

.. autosummary::

    ~apstools.devices.eurotherm_2216e.Eurotherm2216e
    ~apstools.devices.lakeshore_controllers.LakeShore336Device
    ~apstools.devices.lakeshore_controllers.LakeShore340Device
    ~apstools.devices.linkam_controllers.Linkam_CI94_Device
    ~apstools.devices.linkam_controllers.Linkam_T96_Device
    ~apstools.devices.ptc10_controller.PTC10AioChannel
    ~apstools.devices.ptc10_controller.PTC10RtdChannel
    ~apstools.devices.ptc10_controller.PTC10TcChannel
    ~apstools.devices.ptc10_controller.PTC10PositionerMixin

.. _devices.other_support:

Other Support
+++++++++++++

.. autosummary::

    ~apstools.devices.aps_bss_user.ApsBssUserInfoDevice
    ~apstools.devices.xia_pf4.Pf4FilterSingle
    ~apstools.devices.xia_pf4.Pf4FilterDual
    ~apstools.devices.xia_pf4.Pf4FilterTriple
    ~apstools.devices.xia_pf4.Pf4FilterBank
    ~apstools.devices.xia_pf4.Pf4FilterCommon
    ~apstools.devices.xia_pf4.DualPf4FilterBox
    ~apstools.devices.description_mixin.EpicsDescriptionMixin
    ~apstools.devices.dict_device_support.make_dict_device
    ~apstools.devices.epics_scan_id_signal.EpicsScanIdSignal
    ~apstools.devices.kohzu_monochromator.KohzuSeqCtl_Monochromator
    ~apstools.devices.srs570_preamplifier.SRS570_PreAmplifier
    ~apstools.devices.struck3820.Struck3820

Internal Routines
+++++++++++++++++

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

.. automodule:: apstools.devices.dict_device_support
    :members:

.. automodule:: apstools.devices.epics_scan_id_signal
    :members:

.. automodule:: apstools.devices.eurotherm_2216e
    :members:

.. automodule:: apstools.devices.kohzu_monochromator
    :members:

.. automodule:: apstools.devices.lakeshore_controllers
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

.. automodule:: apstools.devices.synth_pseudo_voigt
    :members:

.. automodule:: apstools.devices.tracking_signal
    :members:

.. automodule:: apstools.devices.xia_pf4
    :members:

.. automodule:: apstools.devices.xia_slit
    :members:

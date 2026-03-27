.. _devices:

=======
Devices
=======

Ophyd-style Devices for the APS.

For complete API details see the :doc:`Full API Reference <autoapi/apstools/index>`.

Also consult the :ref:`Index <genindex>` under the *Ophyd* heading for
links to the Devices, Exceptions, Mixins, Signals, and other support
items described here.

Categories
----------

See these categories:

* :ref:`devices.aps_support`
* :ref:`devices.area_detector`
* :ref:`devices.factories`
* :ref:`devices.flyers`
* :ref:`devices.insertion_devices`
* :ref:`devices.motors`
* :ref:`devices.scalers`
* :ref:`devices.shutters`
* :ref:`devices.slits`
* :ref:`devices.temperature_controllers`
* :ref:`devices.other_support`

.. _devices.aps_support:

APS General Support
+++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.aps_cycle.ApsCycleDM`
     - get the APS cycle name from a local file (source: official APS schedule)
   * - :class:`~apstools.devices.aps_machine.ApsMachineParametersDevice`
     - common operational parameters of the APS of general interest
   * - :class:`~apstools.devices.shutters.ApsPssShutter`
     - APS PSS shutter
   * - :class:`~apstools.devices.shutters.ApsPssShutterWithStatus`
     - APS PSS shutter with separate status PV
   * - :class:`~apstools.devices.shutters.SimulatedApsPssShutterWithStatus`
     - simulated APS PSS shutter


.. _devices.area_detector:

Area Detector Support
+++++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.devices.area_detector_factory.ad_class_factory`
     - build an area detector class with specified plugins
   * - :func:`~apstools.devices.area_detector_factory.ad_creator`
     - create an area detector object from a custom class


.. rubric:: Plugins

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.area_detector_support.AD_EpicsFileNameHDF5Plugin`
     - HDF5 plugin: EPICS area detector PV sets file name
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsFileNameJPEGPlugin`
     - JPEG plugin: EPICS area detector PV sets file name
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsFileNameTIFFPlugin`
     - TIFF plugin: EPICS area detector PV sets file name


.. rubric:: Mix-in classes

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.area_detector_support.AD_EpicsFileNameMixin`
     - custom class to define image file name from EPICS
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsHdf5FileName`
     - custom class to define HDF5 image file name from EPICS PVs
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsHDF5IterativeWriter`
     - intermediate class between AD_EpicsHdf5FileName and AD_EpicsFileNameHDF5Plugin
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsJPEGFileName`
     - custom class to define JPEG image file name from EPICS PVs
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsJPEGIterativeWriter`
     - intermediate class between AD_EpicsJPEGFileName and AD_EpicsFileNameJPEGPlugin
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsTIFFFileName`
     - custom class to define TIFF image file name from EPICS PVs
   * - :class:`~apstools.devices.area_detector_support.AD_EpicsTIFFIterativeWriter`
     - intermediate class between AD_EpicsTIFFFileName and AD_EpicsFileNameTIFFPlugin
   * - :class:`~apstools.devices.area_detector_support.BadPixelPlugin`
     - ADCore NDBadPixel plugin, new in AD 3.13
   * - :class:`~apstools.devices.area_detector_support.CamMixin_V34`
     - update cam support to AD release 3.4
   * - :class:`~apstools.devices.area_detector_support.CamMixin_V3_1_1`
     - update cam support to AD release 3.1.1
   * - :class:`~apstools.devices.area_detector_support.SingleTrigger_V34`
     - variation of ophyd's SingleTrigger mixin supporting AcquireBusy


.. rubric:: Other support

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.devices.area_detector_support.AD_full_file_name_local`
     - return AD plugin's last filename using local filesystem path
   * - :func:`~apstools.devices.area_detector_support.AD_plugin_primed`
     - check whether an NDArray has been pushed to the file writer plugin
   * - :func:`~apstools.devices.area_detector_support.AD_prime_plugin2`
     - prime this area detector's file writer plugin
   * - :func:`~apstools.devices.area_detector_support.AD_setup_FrameType`
     - configure frames to be identified and handled by type
   * - :func:`~apstools.devices.area_detector_support.ensure_AD_plugin_primed`
     - ensure the AD file writing plugin is primed, if allowed


.. _devices.scalers:

Detector & Scaler Support
+++++++++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.measComp_usb_ctr_support.MeasCompCtr`
     - Measurement Computing USB CTR08 high-speed counter/timer
   * - :class:`~apstools.devices.measComp_usb_ctr_support.MeasCompCtrMcs`
     - Measurement Computing USB CTR08 multi-channel scaler controls
   * - :class:`~apstools.devices.struck3820.Struck3820`
     - Struck/SIS 3820 multi-channel scaler (as used by USAXS)
   * - :class:`~apstools.devices.synth_pseudo_voigt.SynPseudoVoigt`
     - evaluate a point on a pseudo-Voigt based on the value of a motor
   * - :func:`~apstools.devices.scaler_support.use_EPICS_scaler_channels`
     - configure scaler for only the channels with names assigned in EPICS


.. tip:: The Measurement Computing USB-CTR08 EPICS support
    provides a compatible EPICS scaler record.

.. _devices.factories:

Factory Functions
+++++++++++++++++

.. rubric:: Object Factories

Object factories create ophyd objects.

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.devices.area_detector_factory.ad_creator`
     - create an area detector object from a custom class
   * - :func:`~apstools.devices.dict_device_support.make_dict_device`
     - make a recordable DictionaryDevice instance from a dictionary
   * - :func:`~apstools.devices.motor_factory.mb_creator`
     - create a MotorBundle with any number of motors


.. rubric:: Class Factories

Class factories create ophyd Device classes.

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.devices.area_detector_factory.ad_class_factory`
     - build an area detector class with specified plugins
   * - :func:`~apstools.devices.dict_device_support.dict_device_factory`
     - create a DictionaryDevice class using the supplied dictionary
   * - :func:`~apstools.devices.motor_factory.mb_class_factory`
     - create a custom MotorBundle (or specified base) class


.. _devices.flyers:

Fly Scan Support
++++++++++++++++

``ScalerMotorFlyer()`` support withdrawn pending issue #763.

.. _devices.insertion_devices:

Insertion Devices
+++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.aps_undulator.PlanarUndulator`
     - APS planar undulator
   * - :class:`~apstools.devices.aps_undulator.Revolver_Undulator`
     - APS revolver insertion device
   * - :class:`~apstools.devices.aps_undulator.STI_Undulator`
     - APS planar undulator built by STI Optronics
   * - :class:`~apstools.devices.aps_undulator.Undulator2M`
     - APS 2M undulator
   * - :class:`~apstools.devices.aps_undulator.Undulator4M`
     - APS 4M undulator


.. note:: The ``ApsUndulator`` and ``ApsUndulatorDual`` device support
    classes have been removed.  These devices are not used in the APS-U era.

.. _devices.motors:

Motors, Positioners, Axes, ...
+++++++++++++++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.acs_motors.AcsMotor`
     - AcsMotionControl motor support
   * - :class:`~apstools.devices.axis_tuner.AxisTunerException`
     - exception during execution of AxisTunerBase subclass
   * - :class:`~apstools.devices.axis_tuner.AxisTunerMixin`
     - mixin class to provide tuning capabilities for an axis
   * - :class:`~apstools.devices.description_mixin.EpicsDescriptionMixin`
     - add a record's description field to a Device, such as EpicsMotor
   * - :class:`~apstools.devices.motor_mixins.EpicsMotorDialMixin`
     - add motor record's dial coordinate fields to Device
   * - :class:`~apstools.devices.motor_mixins.EpicsMotorEnableMixin`
     - mixin providing access to motor enable/disable
   * - :class:`~apstools.devices.motor_mixins.EpicsMotorRawMixin`
     - add motor record's raw coordinate fields to Device
   * - :class:`~apstools.devices.motor_mixins.EpicsMotorResolutionMixin`
     - add motor record's resolution fields to motor
   * - :class:`~apstools.devices.motor_mixins.EpicsMotorServoMixin`
     - add motor record's servo loop controls to Device
   * - :class:`~apstools.devices.shutters.EpicsMotorShutter`
     - shutter implemented with an EPICS motor moved between two positions
   * - :class:`~apstools.devices.shutters.EpicsOnOffShutter`
     - shutter using a single EPICS PV moved between two positions
   * - :func:`~apstools.devices.motor_factory.mb_class_factory`
     - create a custom MotorBundle (or specified base) class
   * - :func:`~apstools.devices.motor_factory.mb_creator`
     - create a MotorBundle with any number of motors
   * - :class:`~apstools.devices.positioner_soft_done.PVPositionerSoftDone`
     - PVPositioner that computes ``done`` as a soft signal
   * - :class:`~apstools.devices.positioner_soft_done.PVPositionerSoftDoneWithStop`
     - PVPositionerSoftDone with stop() and inposition
   * - :class:`~apstools.devices.simulated_controllers.SimulatedSwaitControllerPositioner`
     - simulated process controller as positioner with EPICS swait record
   * - :class:`~apstools.devices.simulated_controllers.SimulatedTransformControllerPositioner`
     - simulated process controller as positioner with EPICS transform record


.. _devices.shutters:

Shutters
++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.shutters.ApsPssShutter`
     - APS PSS shutter
   * - :class:`~apstools.devices.shutters.ApsPssShutterWithStatus`
     - APS PSS shutter with separate status PV
   * - :class:`~apstools.devices.shutters.EpicsMotorShutter`
     - shutter implemented with an EPICS motor moved between two positions
   * - :class:`~apstools.devices.shutters.EpicsOnOffShutter`
     - shutter using a single EPICS PV moved between two positions
   * - :class:`~apstools.devices.shutters.OneSignalShutter`
     - shutter Device using one Signal for open and close
   * - :class:`~apstools.devices.shutters.ShutterBase`
     - base class for all shutter Devices
   * - :class:`~apstools.devices.shutters.SimulatedApsPssShutterWithStatus`
     - simulated APS PSS shutter


.. _devices.slits:

Slits
+++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.hhl_slits.HHLSlits`
     - high heat load slit
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit1D`
     - EPICS synApps optics 2slit.db 1D support: xn, xp, size, center, sync
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit2D_HV`
     - EPICS synApps optics 2slit.db 2D support: h.xn, h.xp, v.xn, v.xp
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit2D_InbOutBotTop`
     - EPICS synApps optics 2slit.db 2D support: inb, out, bot, top
   * - :class:`~apstools.utils.slit_core.SlitGeometry`
     - slit size and center as a named tuple
   * - :class:`~apstools.devices.xia_slit.XiaSlit2D`
     - EPICS synApps optics xia_slit.db 2D support


synApps Support
+++++++++++++++

See separate :ref:`synApps` section.

.. _devices.temperature_controllers:

Temperature Support
+++++++++++++++++++

Controllers
~~~~~~~~~~~

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.eurotherm_2216e.Eurotherm2216e`
     - Eurotherm 2216e temperature controller
   * - :class:`~apstools.devices.lakeshore_controllers.LakeShore336Device`
     - LakeShore 336 temperature controller
   * - :class:`~apstools.devices.lakeshore_controllers.LakeShore340Device`
     - LakeShore 340 temperature controller
   * - :class:`~apstools.devices.linkam_controllers.Linkam_CI94_Device`
     - Linkam model CI94 temperature controller
   * - :class:`~apstools.devices.linkam_controllers.Linkam_T96_Device`
     - Linkam model T96 temperature controller
   * - :class:`~apstools.devices.ptc10_controller.PTC10AioChannel`
     - SRS PTC10 AIO module
   * - :class:`~apstools.devices.ptc10_controller.PTC10PositionerMixin`
     - mixin so SRS PTC10 can be used as a temperature positioner
   * - :class:`~apstools.devices.ptc10_controller.PTC10RtdChannel`
     - SRS PTC10 RTD module channel
   * - :class:`~apstools.devices.ptc10_controller.PTC10TcChannel`
     - SRS PTC10 thermocouple module channel
   * - :class:`~apstools.devices.simulated_controllers.SimulatedSwaitControllerPositioner`
     - simulated process controller as positioner with EPICS swait record
   * - :class:`~apstools.devices.simulated_controllers.SimulatedTransformControllerPositioner`
     - simulated process controller as positioner with EPICS transform record


Readers
~~~~~~~

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.measComp_tc32_support.MeasCompTc32`
     - Measurement Computing TC-32 32-channel thermocouple reader


.. _devices.other_support:

Other Support
+++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.aps_bss_user.ApsBssUserInfoDevice`
     - provide current experiment info from the APS BSS
   * - :class:`~apstools.devices.delay.DG645Delay`
     - SRS DG-645 digital delay/pulse generator
   * - :func:`~apstools.devices.dict_device_support.dict_device_factory`
     - create a DictionaryDevice class using the supplied dictionary
   * - :class:`~apstools.devices.aps_data_management.DM_WorkflowConnector`
     - support for APS Data Management tools
   * - :class:`~apstools.devices.xia_pf4.DualPf4FilterBox`
     - (*legacy*, use :class:`~apstools.devices.xia_pf4.Pf4FilterDual`) dual XIA PF4 filter boxes
   * - :class:`~apstools.devices.description_mixin.EpicsDescriptionMixin`
     - add a record's description field to a Device, such as EpicsMotor
   * - :class:`~apstools.devices.epics_scan_id_signal.EpicsScanIdSignal`
     - use an EPICS PV as the source of the RunEngine's ``scan_id``
   * - :class:`~apstools.devices.kohzu_monochromator.KohzuSeqCtl_Monochromator`
     - synApps Kohzu double-crystal monochromator sequence control
   * - :class:`~apstools.devices.labjack.LabJackBase`
     - LabJack T-series data acquisition unit (DAQ)
   * - :class:`~apstools.devices.labjack.LabJackT4`
     - LabJack T4 DAQ
   * - :class:`~apstools.devices.labjack.LabJackT7`
     - LabJack T7 DAQ
   * - :class:`~apstools.devices.labjack.LabJackT7Pro`
     - LabJack T7 Pro DAQ
   * - :class:`~apstools.devices.labjack.LabJackT8`
     - LabJack T8 DAQ
   * - :func:`~apstools.devices.dict_device_support.make_dict_device`
     - make a recordable DictionaryDevice instance from a dictionary
   * - :class:`~apstools.devices.measComp_usb_ctr_support.MeasCompCtr`
     - Measurement Computing USB CTR08 high-speed counter/timer
   * - :class:`~apstools.devices.xia_pf4.Pf4FilterBank`
     - single module of XIA PF4 filters (4 blades)
   * - :class:`~apstools.devices.xia_pf4.Pf4FilterCommon`
     - XIA PF4 filters — common support
   * - :class:`~apstools.devices.xia_pf4.Pf4FilterDual`
     - XIA PF4 filter: two sets of 4 filters (A, B)
   * - :class:`~apstools.devices.xia_pf4.Pf4FilterSingle`
     - XIA PF4 filter: one set of 4 filters (A)
   * - :class:`~apstools.devices.xia_pf4.Pf4FilterTriple`
     - XIA PF4 filter: three sets of 4 filters (A, B, C)
   * - :class:`~apstools.devices.simulated_controllers.SimulatedSwaitControllerPositioner`
     - simulated process controller as positioner with EPICS swait record
   * - :class:`~apstools.devices.simulated_controllers.SimulatedTransformControllerPositioner`
     - simulated process controller as positioner with EPICS transform record
   * - :class:`~apstools.devices.srs570_preamplifier.SRS570_PreAmplifier`
     - Stanford Research Systems 570 preamplifier from synApps
   * - :class:`~apstools.devices.struck3820.Struck3820`
     - Struck/SIS 3820 multi-channel scaler (as used by USAXS)


Internal Routines
+++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.devices.aps_machine.ApsOperatorMessagesDevice`
     - general messages from the APS main control room
   * - :class:`~apstools.devices.mixin_base.DeviceMixinBase`
     - base class for apstools Device mixin classes
   * - :class:`~apstools.devices.tracking_signal.TrackingSignal`
     - non-EPICS signal for use when coordinating Device actions

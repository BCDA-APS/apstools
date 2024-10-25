..
  This file describes user-visible changes between the versions.

  subsections could include these headings (in this order), omit if no content

    Notice
    Breaking Changes
    New Features
    Enhancements
    Fixes
    Maintenance
    Deprecations
    Known Problems
    New Contributors

Change History
##############

History of changes in the *apstools* project.
Project `milestones <https://github.com/BCDA-APS/apstools/milestones>`_
describe future plans.

..
   1.7.2
   ******

   Release expected by 2024-12-31.

1.7.1
******

Bugfix release expected by 2024-10-25.

Fixes
-----

- Allow imports to succeed when developing or testing with databroker v2.0+.
- In SpecWriterCallback2, set spec_filename in constructor.

Maintenance
-----------

- Use 'NeXus_release' file attribute in 'nxwriter' callback.

Deprecations
------------

- 'EpicsMotorLimitsMixin' features are now part of 'ophyd.EpicsMotor'.

1.7.0
******

released 2024-09-21

New Features
------------

* Add ad_creator() and ad_class_factory() -- Easy to create area detector objects.
* Add SpecWriterCallback2 (writes point-by-point to file).
* Support for most APS-U undulators.  (All but for 29-ID.)

Fixes
-----

* Area detector image shape of (0, 0, 0) caused listdevice() to fail.
* PVPositionerSoftDone should set done=False at start of move.
* RuntimeError from listdevice() with area detector object.
* PV name typo in synApps SaveData() class.  And capitalization.
* CI workflow artifact cache errors.

Maintenance
-----------

* Add ramp temperature and output enable to PTC-10.
* Remove Anaconda defaults channel from environment per TOS.
* Replace unit tests marked by 'local' decorator.
* Unit tests now support Python version 3.9, 3.10, & 3.11.
* Update common PVs for APS-U era.

1.6.20
******

released 2024-07-10

New Features
------------

* Add new APS PlanarUndulator device.
* Add new APS Revolver_Undulator device.
* Add new APS STI_Undulator device.
* Add new APS Undulator2M device.
* Add new APS Undulator4M device.

Maintenance
-----------

* Describe ``.component_names`` in *What are the objects to control?*
* Pin numpy<2 because upstream dask package needs a fix.
* Removed ApsUndulator and ApsUndulatorDual devices.
* Removed top-level requirements files.  They were not used.
* Update APS cycle begin & end dates.
* Update device support for APS machine parameters (current, lifetime, ...).

1.6.19
******

released 2024-04-23

New Features
------------

* Add new plan for edge alignment called edge_align.
* Added a mesh grid scan plan that will collect until number of collection points is met.

Fixes
-----

* lineup2() should work with low intensity peaks.
* lineup2() would raise ZeroDivideError in some cases.
* Increase minimum aps-dm-api version to 8.
* PVPositionerSoftDone should set 'done' to False at start of a move.
* Race condition with SR570 pre-amp.

Maintenance
-----------

* Code format conforms to 'ruff'.
* Add additional support for APS Data Management API.
* Make the home page more concise.
* Refactor packaging from setup.py to pyproject.toml.

1.6.18
******

released 2024-01-23

New Features
------------

* Add (ophyd) device support for:
  * DG-645 digital delay/pulse generator.
  * Measurement Computing USB CTR08 High-Speed Counter/Timer
  * Simulated process controller as positioner using EPICS swait record.
  * Simulated process controller as positioner using EPICS transform record.
  * synApps userArrayCalcs and EPICS acalcout record.
* Add subnet check for APSU beamlines.
* Add template support for writing NeXus/HDF5 files.
* New lineup2() plan can be used in console, notebooks, and queueserver.

Fixes
-----------

* Fix ``AD_full_file_name_local()`` for case when the read & write paths are identical.

Maintenance
-----------

* Avoid voltage spikes when changing gain of SRS570 preamplifier.
* In ``listdevice(show_pv=True)``, set ``cname=True, dname=False`` if not provided by caller.
* Move ``.OVAL`` field from ``EpicsRecordOutputFields to new ``EpicsRecordAnalogOutputFields``
* Write tables of plot statistics in most compact form.

Known Problems
--------------

* Remove ``ScalerMotorFlyer``, pending issue #763.

1.6.17
******

released 2023-07-19

New Features
------------

* Add ophyd device support for APS Data Management workflows.

1.6.16
******

released 2023-05-23

Enhancements
------------

* Add ``fb_epid`` database support from the optics module.
* Add guide *How to interrupt/stop/abort a running plan & recover to safe settings*.
* Add ``close_pv`` & ``open_pv`` kwargs to ``ApsPssShutter``
* Add ``ensure_AD_plugin_primed()`` convenience function.
* Made ``listdevice()`` more tolerant of unconnectable signals.

Fixes
-----

* APS cycle set to ``APSU`` during this *dark* year.
* Resolve AD ERROR reports "capture not supported in Single mode".

Maintenance
------------

* Add unit tests for shutters.
* Apply consistent code style (black) throughout.
* Set ``kind`` attribute to add plugin to ad.read_attrs list.
* Clear ``PVPositionerSoftDone``'s setpoint & readback subscriptions at exit.

1.6.15
******

released 2023-03-27

Maintenance
------------

* add ``log_path=None`` kwarg to ``apstools.utils.stream_log_handler()``

Fixes
------------

- resolved ``AttributeError`` for certain logging configurations


1.6.14
******

released 2023-03-12

Breaking Changes
------------------------

* listobjects() ``printing`` keyword argument is deprecated.
* ListRuns.to_dataframe()' method is deprecated.
* ListRuns.to_table() method is deprecated.
* listruns() ``printing`` keyword argument is deprecated.
* listruns() ``tablefmt`` keyword argument is deprecated.  Use ``table_style`` instead.
* listruns() now returns pyRestTable.Table or pandas.DataFrame

New Features
------------

* MeasCompTc32: Measurement Computing TC-32 Thermocouple reader

Enhancements
------------

* Add guide *What are the objects to control?*

Fixes
------------

- labels_to_streams(): do not plot items in the labeled stream
- labels_to_streams(): failed when no motor label assigned

Maintenance
------------

* add more unit tests for ``apstools.plans``
* addDeviceDataAsStream() renamed to write_stream()
* FileWriterCallbackBase.file_name now a property, uses pathlib
* listobjects() now returns pyRestTable (by default)
* listdevice() now returns pyRestTable (by default)
* listplans() now returns pyRestTable (by default)
* listruns() now returns pyRestTable (by default)
* NXWriter: unit tests added for proper NXdata@axes structure.

1.6.13
******

released 2023-02-16

Maintenance
------------

* Release process updated on the wiki.

1.6.12
******

released 2023-02-16

Maintenance
------------

* NXWriter: add wait_writer_plan_stub() method for use in a plan.
* Release process documented on the wiki.

1.6.11
******

released 2023-02-15

New Features
------------

* Support to record all motor (or other ophyd-labeled devices) positions at start (or end) of run.
* SpecWriterCallback: write ``#O`` and ``#P`` lines from motor positions recorded at start of run.

Fixes
------------

* NXWriter: scans with area detectors did not have image data.  Fixed.  Clients must wait for writer to finish.
* PVPositionerSoftDone: computation of 'done' signal and 'inposition' deconvoluted.
* Struck3820: changed (typo) ``do_readl_all`` to ``do_read_all``
* Tests involving PVPositionerSoftDone call '.cb_readback()' method to upate 'done' signal.

Maintenance
------------

* Added github/super-linter workflow, adds mypy, isort, and other tests.
* Apply isort code style.

Known Problems
--------------

* Observing random occurrence of unit test failures involving PVPositionerSoftDone.

1.6.10
******

released 2023-01-11

New Features
------------

* Add ``apstools.utils.plotxy()`` utility function.
* Add tag-based documentation selection via PyData switcher.

Enhancements
------------

* In listruns(), also search the hints for keys.

Fixes
------------

* CI failed to build documentation when creating pip installation.
* ScalerMotorFlyer default fly_time_pad increased to 10 s.
* ScalerMotorFlyer now sets scaler to "OneShot" mode.
* ScalerMotorFlyer in-position comparison now based on motor's precision.
* Version number was not reported correctly in certain situations (issue #771).

Maintenance
------------

* "Custom HDF5 File Name" example updated to latest advice.
* Pin Sphinx to `<6` due to problems with PyData and Sphinx v6.
* Conda channel "nsls2forge" no longer needed.
* Remove ``nsls2forge`` channel from conda environment.

New Contributors
-----------------------

* @jwkim-anl (Jong Woo Kim, ANL) for the ``plotxy()`` idea.

1.6.9
******

released 2022-11-30

New Features
------------

* Add ``ScalerMotorFlyer()`` device.
* Add functions to support reporting of logging messages.
* Add :meth:`restorable_stage_sigs` decorator.
* Add support for Python 3.11.
* Add ``utils.analysis_1D()`` & ``utils.analysis_2D()`` functions for peaks statistics.

Enhancements
------------

* Add example notebook *Fly Scans with EPICS motor and scaler*.
* Add guide *How to Search in Databroker*.
* Add guide *How to setup logging*.

Maintenance
------------

* Add convenience import:``from apstools.devices import AD_EpicsFileNameMixin``.
* Enable: ``from apstools.devices import AD_EpicsFileNameMixin``.
* Resolve intermittent, random CI failures.
* Resolve problems reporting unit test coverage statistics.
* Unit tests now support Python version 3.8, 3.9, 3.10, & 3.11.

1.6.8
******

released 2022-10-16

Fixes
------------

* [again] Make sure that YML (and other) files are packaged for pip and conda.

1.6.7
******

skipped

1.6.6
******

released 2022-10-13

New Features
------------

* Add ``request_input()`` plan stub, per user request.
* Add fly scan for scaler v. continuous motor.

Maintenance
-----------

* Rename: ``devices.make_dict_device()`` is now ``devices.dict_device_factory()``.

Fixes
------------

* Make sure that YML (and other) files are packaged for pip and conda.
* PVPositioner got stuck if target position was the same as current position.

Deprecations
------------

* Removed all snapshot support.

1.6.5
******

released 2022-10-04

Maintenance
---------------

* Pip requirements updated.

1.6.4
******

released 2022-10-03

New Features and/or Enhancements
---------------------------------------------

* Example of imaging with AreaDetector in Single mode writing HDF5 files.
* ``lineup()``: user can choose which feature (max, min, cen, com), additional API changes.
* ``devices.make_dict_device()`` to make a recordable Device from a dictionary.
* Only publish documentation on demand by executing GitHub workflow.
* Switch HTML documentation to use *PyData* theme.

Maintenance
---------------

* Re-arranged the documentation.  Some examples renamed.  Content unchanged.
* Update the APS cycle dates file through 2023-04-30.

1.6.3
******

released 2022-08-15

New Features and/or Enhancements
---------------------------------------------

* Add devices.CamMixin_V3_1_1
* Add devices.CamMixin_V34
* Add devices.SingleTrigger_V34
* Add EpicsScanIdSignal (scan_id from EPICS PV).
* Add run_blocking_function() plan to run blocking functions in the RunEngine.
* Published on conda-forge ``conda install -c conda-forge apstools``.
* replay() can now take a run, [run], header, or [header]
* Switch HTML documentation to use *furo* theme.

Maintenance
---------------

* Combine install steps, workflows in CI
* Describe how to use the NXWriter callback.
* Refactor AD test with EPICS-controlled image file names.
* Refactor test_move_to_zero().
* Unit tests now support Python version 3.8, 3.9, & 3.10.

Deprecations
---------------

* ``bluesky_snapshot_viewer`` and underlying GUI code will be dropped by 2022-12-31.
* Drop support for Python 3.7 per NEP29.
* Stop publishing on channel ``-c aps-anl-tag`` (use ``-c conda-forge`` instead).

1.6.2
******

released 2022-07-06

Notice
---------------

* Confirmed: databroker finds HDF5 image files with custom names.
* Still not ready for databroker 2.0+.

New Features
---------------

* Documentation website: https://bcda-aps.github.io/apstools/
* New example: user-controlled HDF5 image file names.
* Using Jupyter notebooks directly (via ``nbsphinx`` extension).
* User-controlled HDF5, JPEG, TIFF image file names.

Fixes
---------------

* Fix timeout problem in utils.connect_pvlist().
* Fix unexpected key in datum kwargs.
* Fix ``utils.listdevice()`` mixing dot and underline name separators.

Maintenance
---------------

* Applied custom project badge for APS software License.
* Use micromamba in testing workflows.

Deprecations
---------------

* Drop LGTM.com static code analysis service.
* Drop RTD (readthedocs) documentation publishing service.

Contributors
---------------

* Harry Zhou

1.6.1
******

released 2022-01-26

Fixes
---------------

* Move ``enable`` Component out from synApps Record devices.
* Renew the unit tests for PVPositionerSoftDoneWithStop.

1.6.0
******

released 2022-01-20

Breaking Changes
-----------------

* Moved ``apsbss`` support to new ``apsbss`` package (install with either ``pip`` or ``conda``).  See https://bcda-aps.github.io/apsbss/ for details.
* Can use Python 3.7 - 3.9.  Cannot use Python 3.10 yet due to upstream limitation from databroker and intake packages.
* Moved ``command_list_as_table()`` from `utils` into ``plans/command_list``.
* Removed ``BusyStatus`` from `apstools.synApps.busy`
* ``callbacks/``: ``DocumentCollectorCallback``, ``document_contents_callback``, and ``SnapshotReport`` moved into ``callbacks/``.
* ``devices/``: Reorganized all devices, including ``synApps/``, into ``devices/`` subpackage.
* ``devices/``: ``SynPseudoVoigt()`` moved from ``signals/`` to ``devices/``.
* ``plans/``: Reorganized ``plans.py`` and ``_plans/`` into ``plans/`` subpackage.
* ``snapshot/``: Moved ``snapshot`` application and related files to a subdirectory.
* ``utils/``: Reorganized ``utils.py`` and ``_utils/`` into ``utils/`` subpackage.

New Features and/or Enhancements
---------------------------------------------

* Add support for Eurotherm 2216e temperature controller
* Add support for Lakeshore 336 temperature controller
* Add support for Lakeshore 340 temperature controller
* Add support for synApps calc ``scalcout`` record.
* Add support for synApps calc ``sseq`` record.
* Add support for EPICS base ``sub`` record.
* Add support for synApps calc ``userAve`` database.
* Add support for synApps calc ``userStringSeq`` database.
* Add support for synApps calc ``userStringCalc`` database.
* Add support for synApps optics ``2slit`` database.

Fixes
-----------

* Convert ``None`` to ``"null"`` when saving ``PeakStats`` to stream.

Maintenance
---------------

Now testing with Python versions 3.7 - 3.9.  (Can't use with Py3.10 yet due to upstream requirements.)

Update notebooks:

* ``demo_specfile_example``
* ``demo_tuneaxis``

Remove notebooks:

* ``demo_specfile_databroker``

Deprecations
---------------

* Applications

  * `apstools_plan_catalog` application and related support.

* Devices

  * ``ApsCycleComputedRO``
  * ``move_energy()`` method in ``KohzuSeqCtl_Monochromator`` class
  * ``ProcessController``

* Utilities

  * ``device_read2table``
  * ``json_export``
  * ``json_import``
  * ``listdevice_1_5_2``
  * ``listruns_v1_4``
  * ``object_explorer``

Contributors
---------------

* Gilberto Fabbris
* Jan Ilavsky
* Qingteng Zhang

1.5.4
******

released 2021-11-25

NOTE: The ``apsbss`` component will be moved out of ``apstools`` into its
own package with the next release (1.6.0, ~Feb 2022) of ``apstools``.

Notice
-----------------

The Python version is limited to 3.7 due to *aps-dm-api* package.  Expect this
limitation to be relaxed, allowing any Python 3.7 and higher with the 1.6.0
release.

Fixes
---------------

* Added table of APS run cycle dates.  Use that if *aps-dm-api* not available.
* Restricted python version to 3.7 due to upstream *aps_dm_api* package.
* Rename name `uid` to `token` to avoid LGTM security false alert.

Deprecations
---------------

This support was marked as deprecated in release 1.5.4:

* ``apstools.devices.ApsCycleComputedRO``

1.5.3
******

released 2021-10-15

.. Format of the Change History changes with this release to make
   the layout become more relevant to the __reader__.  The
   `release notes <https://github.com/BCDA-APS/apstools/wiki/Release-Notes>`_
   on the wiki provide links to these specifics.

Notice
-----------------

The ``apstools.beamtime`` module and related content (includes ``apsbss``)
will be moved to a new repository for release 1.6.0. This will
remove the requirement that the APS data management tools (package *aps-dm*,
which only works on the APS computing network) be included.  With this
change, users will be able to ``conda install apstools -c aps-anl-tag`` on
computers outside of the APS computing network.

Breaking Changes
-----------------

* ``apstools.utils.listdevice`` has a new API (old version renamed to ``listdevice_1_5_2``)

New Features and/or Enhancements
---------------------------------------------

* Kohzu monochromator ``energy``, ``wavelength``, and ``theta`` each are now a ``PVPositioner`` (subclass).
* Linkam temperature controller CI94
* Linkam temperature controller T96
* Stanford Research Systems 570 current preamplifier
* Stanford Research Systems PTC10 temperature controller
* XIA PF4 filter now supports multiple PF4 units.
* Generalize that amplifiers will have a ``gain`` Component attribute.
* Generalize that temperature controllers will have a  ``temperature`` Component attribute that is a positioner (subclass of ``ophyd.PVPositioner``).
* Enhanced positioners for EPICS Devices:
  * ``apstools.devices.PVPositionerSoftDone``
  * ``apstools.devices.PVPositionerSoftDoneWithStop``

Fixes
---------------

* Fixed bug in ``devices.ApsCycleComputedRO`` and ``devices.ApsCycleDM`` involving ``datetime``.

Maintenance
---------------

* Moved all device support into individual modules under `apstools._devices` because `apstools.devices` module was getting too big.  Will refactor all with release 1.6.0.
* Add unit tests for ``devices.ApsCycle*`` Devices.
* Add EPICS IOCs (ADSimDetector and synApps xxx) to continuous integration for use in unit testing.
* Unit tests now use *pytest* package.
* Suppress certain warnings during unit testing.

Deprecations
---------------

This support will be removed in release 1.6.0:

* ``apstools.beamtime`` module and related content (includes ``apsbss``) will be moved to a new repository
* ``apstools.devices.ProcessController``
* ``apstools.utils.device_read2table``
* ``apstools.utils.listdevice_1_5_2``
* ``apstools.utils.object_explorer``

Contributors
---------------

* Fanny Rodolakis
* Gilberto Fabbris
* Jan Ilavsky
* Qingteng Zhang
* 4-ID-C Polar
* 8-ID-I XPCS
* 9-ID-C USAXS

1.5.2 (and previous)
************************

See this table for release change histories, highlighted by version control
reference (pull request or issue):

:1.5.2:  released 2021-09-29

   * Drop Codacy (https://app.codacy.com/gh/BCDA-APS/apstools) as no longer needed.

   * `#540 <https://github.com/BCDA-APS/apstools/pull/540>`_
      Add ``apstools.utils.listplans()`` function.

   * `#534 <https://github.com/BCDA-APS/apstools/pull/534>`_
      Add ``apstools.utils.OverrideParameters`` class.
      Hoisted from APS USAXS instrument.

   * `#537 <https://github.com/BCDA-APS/apstools/pull/537>`_
      Enhancements to ``apstools.utils.listruns()``:

      * Add search by list of ``scan_id`` or ``uid`` values.
      * Optimize search speed.

   * `#534 <https://github.com/BCDA-APS/apstools/pull/534>`_
      Add ``apstools.plans.documentation_run()`` plan.
      Hoisted from APS USAXS instrument.

   * `#528 <https://github.com/BCDA-APS/apstools/pull/528>`_
      Add ``kind=`` kwarg to synApps Devices.

   * `#539 <https://github.com/BCDA-APS/apstools/pull/539>`_
      Break ``devices`` into submodule ``_devices``.

:1.5.1:  released 2021-07-22

   * `#522 <https://github.com/BCDA-APS/apstools/issues/522>`_
      Deprecate `apstools.devices.ProcessController`.
      Suggest `ophyd.PVPositioner` instead.

   * `#521 <https://github.com/BCDA-APS/apstools/issues/521>`_
      Enhancement: new functions: getRunData(), getRunDataValue(),
      getStreamValues() & listRunKeys()

   * `#518 <https://github.com/BCDA-APS/apstools/issues/518>`_
      Bug fixed: TypeError from summary() of CalcoutRecord

   * `#517 <https://github.com/BCDA-APS/apstools/pull/517>`_
      Added support for python 3.9.

   * `#514 <https://github.com/BCDA-APS/apstools/pull/514>`_
      Refactor 'SIGNAL.value' to 'SIGNAL.get()'

:1.5.0:  released 2021-04-02

   * `#504 comment <https://github.com/BCDA-APS/apstools/pull/504#issuecomment-804377418>`_
      Dropped support for python 3.6.

   * `#495 <https://github.com/BCDA-APS/apstools/pull/495>`_
      Dropped diffractometer support code.

   * `#511 <https://github.com/BCDA-APS/apstools/pull/511>`_
      & `#497 <https://github.com/BCDA-APS/apstools/pull/497>`_
      Add ``utils.findbyname()`` and ``utils.findbypv()`` functions.

   * `#506 <https://github.com/BCDA-APS/apstools/pull/506>`_
      ``spec2ophyd`` can now read SPEC config files from APS 17BM

   * `#504 <https://github.com/BCDA-APS/apstools/pull/504>`_
      Overhaul of listruns() using pandas.  Previous code
      renamed to listruns_v1_4().

   * `#503 <https://github.com/BCDA-APS/apstools/pull/503>`_
      Unit tests with data now used msgpack-backed databroker.

   * `#495 <https://github.com/BCDA-APS/apstools/pull/495>`_
      remove *hklpy* requirement since all diffractometer
      support code will be moved to
      [*hklpy*](https://github.com/bluesky/hklpy) package.

:1.4.1:  released: 2021-01-23

    * add Area Detector configuration examples:
      Pilatus & Perkin-Elmer, both writing image to HDF5 file

    * `#488 <https://github.com/BCDA-APS/apstools/pull/488>`_
       use first trigger_mode when priming AD plugin

    * `#487 <https://github.com/BCDA-APS/apstools/pull/487>`_
       ensure spec2ophyd code is packaged

:1.4.0:  released: 2021-01-15

    * `#483 <https://github.com/BCDA-APS/apstools/pull/483>`_
       Python code style must pass ``flake8`` test.

    * `#482 <https://github.com/BCDA-APS/apstools/pull/482>`_
       specwriter: Fix bug when plan_args structure includes a numpy
       ndarray.

    * `#474 <https://github.com/BCDA-APS/apstools/pull/474>`_
       :func:`apstools.utils.listruns()` now defaults to the
       current catalog in use.

       New functions:

       * :func:`apstools.utils.getDatabase`
       * :func:`apstools.utils.getDefaultDatabase`

    * `#472 <https://github.com/BCDA-APS/apstools/pull/472>`_
       Respond to changes in upstream packages.

       * package requirements
       * auto-detection of command list format (Excel or text)
       * use *openpyxl* [#]_ instead of *xlrd* [#]_ and
         *pandas* [#]_ to read Microsoft Excel `.xlsx` spreadsheet
         files

       .. [#] https://openpyxl.readthedocs.io
       .. [#] https://xlrd.readthedocs.io
       .. [#] https://pandas.pydata.org

    * `#470 <https://github.com/BCDA-APS/apstools/pull/470>`_
       Area Detector plugin preparation & detection.

       * :func:`apstools.devices.AD_plugin_primed()`
          re-written completely
       * :func:`apstools.devices.AD_prime_plugin()`
          replaced by :func:`apstools.devices.AD_prime_plugin2()`

    * `#463 <https://github.com/BCDA-APS/apstools/pull/463>`_
       Remove deprecated features.

       * ``apstools.suspenders.SuspendWhenChanged()``
       * ``apstools.utils.plot_prune_fifo()``
       * ``apstools.utils.show_ophyd_symbols()``
       * ``apstools.synapps.asyn.AsynRecord.binary_output_maxlength()``
       * ``apstools.devices.AD_warmed_up()``

    * `#451 <https://github.com/BCDA-APS/apstools/pull/451>`_
       Undulator and Kohzu monochromator functionalities

       * :class:`apstools.devices.ApsUndulator()`

         Adds some ``Signal`` components (such as setting `kind` kwarg)
         that are helpful in moving the undulator

:1.3.9:  released 2020-11-30

    * `#459 <https://github.com/BCDA-APS/apstools/pull/459>`_
       ``apsbss``: list ESAFs & proposals from other cycles
    * `#457 <https://github.com/BCDA-APS/apstools/pull/457>`_
       :func:`apstools.utils.rss_mem()`: show memory used by this process

:1.3.8:  released: 2020-10-23

    * `#449 <https://github.com/BCDA-APS/apstools/pull/449>`_
       diffractometer wh() shows extra positioners
    * `#446 <https://github.com/BCDA-APS/apstools/pull/446>`_
       utils: device_read2table() renamed to listdevice()
    * `#445 <https://github.com/BCDA-APS/apstools/pull/445>`_
       synApps: add Device for iocStats
    * `#437 <https://github.com/BCDA-APS/apstools/pull/437>`_
       diffractometer add pa() report
    * `#426 <https://github.com/BCDA-APS/apstools/pull/426>`_
       diffractometer add simulated diffractometers
    * `#425 <https://github.com/BCDA-APS/apstools/pull/425>`_
       BUG fixed: listruns() when no stop document
    * `#423 <https://github.com/BCDA-APS/apstools/pull/423>`_
       BUG fixed: apsbss IOC starter script

:1.3.7:  released: 2020-09-18

    * `#422 <https://github.com/BCDA-APS/apstools/pull/422>`_
       additional AD support from APS USAXS
    * `#421 <https://github.com/BCDA-APS/apstools/pull/421>`_
       wait for undulator when start_button pushed
    * `#418 <https://github.com/BCDA-APS/apstools/pull/418>`_
       apsbss: only update APS run cycle name after current cycle ends

:1.3.6:  released 2020-09-04

    * `#416 <https://github.com/BCDA-APS/apstools/pull/416>`_
       apsbss: allow iso8601 time strings to have *option* for fractional seconds
    * `#415 <https://github.com/BCDA-APS/apstools/pull/415>`_
       Get APS cycle name from official source

:1.3.5:  released 2020-08-25

    * `#406 <https://github.com/BCDA-APS/apstools/pull/406>`_
       replace ``plot_prune_fifo()`` with ``trim_plot()``
       and ``trim_plot_by_name()``
    * `#405 <https://github.com/BCDA-APS/apstools/pull/405>`_
       add Y1 & Z2 read-only signal to Kohzu Monochromator device
    * `#403 <https://github.com/BCDA-APS/apstools/pull/403>`_
       deprecate ``SuspendWhenChanged()``

:1.3.4:  released 2020-08-14

    * `#400 <https://github.com/BCDA-APS/apstools/pull/400>`_
       resolve warnings and example documentation inconsistency
    * `#399 <https://github.com/BCDA-APS/apstools/pull/399>`_
       parse iso8601 date for py36
    * `#398 <https://github.com/BCDA-APS/apstools/pull/398>`_
       DiffractometerMixin: add wh() method
    * `#396 <https://github.com/BCDA-APS/apstools/pull/396>`_
       provide spec2ophyd application
    * `#394 <https://github.com/BCDA-APS/apstools/pull/394>`_
       add utils.copy_filtered_catalog()
    * `#392 <https://github.com/BCDA-APS/apstools/pull/392>`_
       RTD make parameter lists clearer
    * `#390 <https://github.com/BCDA-APS/apstools/pull/390>`_
       improve formatting of parameter list in RTD
    * `#388 <https://github.com/BCDA-APS/apstools/pull/388>`_
       add utils.quantify_md_key_use()
    * `#385 <https://github.com/BCDA-APS/apstools/issues/385>`_
       spec2ophyd: make entry point

:1.3.3:  released 2020-07-22

    * `#384 <https://github.com/BCDA-APS/apstools/pull/384>`_
       apsbss: print, not log from commands
    * `#382 <https://github.com/BCDA-APS/apstools/pull/382>`_
       spec2ophyd analyses

:1.3.2:  released 2020-07-20

    * `#380 <https://github.com/BCDA-APS/apstools/pull/380>`_
       apsbss: fix object references

:1.3.1:  released 2020-07-18

    * `#378 <https://github.com/BCDA-APS/apstools/pull/378>`_
       apsbss_ioc.sh: add checkup (keep-alive feature for the IOC)
    * `#376 <https://github.com/BCDA-APS/apstools/pull/376>`_
       apsbss: example beam line-specific shell scripts
    * `#375 <https://github.com/BCDA-APS/apstools/pull/375>`_
       apsbss: add PVs for numbers of users
    * `#374 <https://github.com/BCDA-APS/apstools/pull/374>`_
       apsbss_ophyd: addDeviceDataAsStream() from USAXS
    * `#373 <https://github.com/BCDA-APS/apstools/pull/373>`_
       account for time zone when testing datetime-based file name
    * `#371 <https://github.com/BCDA-APS/apstools/pull/371>`_
       update & simplify the travis-ci setup
    * `#369 <https://github.com/BCDA-APS/apstools/pull/369>`_
       spec2ophyd: handle NONE in SPEC counters
    * `#368 <https://github.com/BCDA-APS/apstools/pull/368>`_
       spec2ophyd: config file as command-line argument
    * `#367 <https://github.com/BCDA-APS/apstools/pull/367>`_
       apsbss: move ophyd import from main
    * `#364 <https://github.com/BCDA-APS/apstools/pull/364>`_
       apsbss: add PVs for ioc_host and ioc_user
    * `#363 <https://github.com/BCDA-APS/apstools/pull/363>`_
       Handle when mailInFlag not provided
    * `#360 <https://github.com/BCDA-APS/apstools/pull/360>`_
       prefer logging to print

:1.3.0:  release expected by 2020-07-15

    * add NeXus writer callback
    * add ``apsbss`` : APS experiment metadata support
    * `#351 <https://github.com/BCDA-APS/apstools/issues/351>`_
       apsbss: put raw info into PV
    * `#350 <https://github.com/BCDA-APS/apstools/issues/350>`_
       apsbss: clarify meaning of reported dates
    * `#349 <https://github.com/BCDA-APS/apstools/issues/349>`_
       apsbss: add "next" subcommand
    * `#347 <https://github.com/BCDA-APS/apstools/issues/347>`_
       some apbss files not published
    * `#346 <https://github.com/BCDA-APS/apstools/pull/346>`_
       publish fails to push conda packages
    * `#344 <https://github.com/BCDA-APS/apstools/pull/344>`_
       listruns() uses databroker v2 API
    * `#343 <https://github.com/BCDA-APS/apstools/issues/343>`_
       review and update requirements
    * `#342 <https://github.com/BCDA-APS/apstools/pull/342>`_
       summarize runs in databroker by plan_name and frequency
    * `#341 <https://github.com/BCDA-APS/apstools/issues/341>`_
       tools to summarize activity
    * `#340 <https://github.com/BCDA-APS/apstools/issues/340>`_
       update copyright year
    * `#339 <https://github.com/BCDA-APS/apstools/issues/339>`_
       resolve Codacy code review issues
    * `#338 <https://github.com/BCDA-APS/apstools/issues/338>`_
       unit tests are leaving directories undeleted
    * `#337 <https://github.com/BCDA-APS/apstools/issues/337>`_
       Document new filewriter callbacks
    * `#336 <https://github.com/BCDA-APS/apstools/pull/336>`_
       add NeXus file writer from USAXS
    * `#335 <https://github.com/BCDA-APS/apstools/issues/335>`_
       update requirements
    * `#334 <https://github.com/BCDA-APS/apstools/pull/334>`_
       support APS proposal & ESAF systems to provide useful metadata
    * `#333 <https://github.com/BCDA-APS/apstools/issues/333>`_
       access APS proposal and ESAF information
    * `#332 <https://github.com/BCDA-APS/apstools/issues/332>`_
       listruns(): use databroker v2 API
    * `#329 <https://github.com/BCDA-APS/apstools/issues/329>`_
       add NeXus writer base class from USAXS

:1.2.6:  released *2020-06-26*

    * `#331 <https://github.com/BCDA-APS/apstools/pull/331>`_
       listruns succeeds even when number of existing runs is less than requested
    * `#330 <https://github.com/BCDA-APS/apstools/issues/330>`_
       BUG: listruns: less than 20 runs in catalog
    * `#328 <https://github.com/BCDA-APS/apstools/pull/328>`_
       epid: add final_value (.VAL field)
    * `#327 <https://github.com/BCDA-APS/apstools/pull/327>`_
       epid: remove clock_ticks (.CT field)
    * `#326 <https://github.com/BCDA-APS/apstools/issues/326>`_
       BUG: epid failed to connect to .CT field
    * `#325 <https://github.com/BCDA-APS/apstools/issues/325>`_
       BUG: epid final_value signal not found
    * `#324 <https://github.com/BCDA-APS/apstools/issues/324>`_
       BUG: epid controlled_value signal name

:1.2.5:  released *2020-06-05*

    * `#322 <https://github.com/BCDA-APS/apstools/issues/322>`_
       add py38 to travis config
    * `#320 <https://github.com/BCDA-APS/apstools/issues/320>`_
       multi-pass tune should use FWHM for next scan
    * `#318 <https://github.com/BCDA-APS/apstools/issues/318>`_
       AxisTunerMixin is now subclass of DeviceMixinBase
    * `#317 <https://github.com/BCDA-APS/apstools/issues/317>`_
       BUG: USAXS can't tune motors
    * `#316 <https://github.com/BCDA-APS/apstools/issues/316>`_
       BUG: Error in asyn object definition
    * `#315 <https://github.com/BCDA-APS/apstools/issues/315>`_
       BUG: AttributeError from db.hs

:1.2.3:  released *2020-05-07*

    * `#314 <https://github.com/BCDA-APS/apstools/issues/314>`_
       fix ImportError about SignalRO
    * `#313 <https://github.com/BCDA-APS/apstools/issues/313>`_
       update packaging requirements

:1.2.2:  released *2020-05-06*

    * DEPRECATION `#306 <https://github.com/BCDA-APS/apstools/issues/306>`_
	   `apstools.plans.show_ophyd_symbols()` will be removed by 2020-07-01.
	   Use `apstools.plans.listobjects()` instead.

    * `#311 <https://github.com/BCDA-APS/apstools/issues/311>`_
       adapt to databroker v1
    * `#310 <https://github.com/BCDA-APS/apstools/issues/310>`_
       enhance listruns() search capabilities
    * `#308 <https://github.com/BCDA-APS/apstools/issues/308>`_
       manage diffractometer constraints
    * `#307 <https://github.com/BCDA-APS/apstools/issues/307>`_
       add diffractometer emhancements
    * `#306 <https://github.com/BCDA-APS/apstools/issues/306>`_
       rename show_ophyd_objects() as listobjects()
    * `#305 <https://github.com/BCDA-APS/apstools/issues/305>`_
       add utils.safe_ophyd_name()
    * `#299 <https://github.com/BCDA-APS/apstools/issues/299>`_
       set_lim() does not set low limit

:1.2.1: released *2020-02-18* - bug fix

    * `#297 <https://github.com/BCDA-APS/apstools/issues/297>`_
       fix import error

:1.2.0: released *2020-02-18* - remove deprecated functions

    * `#293 <https://github.com/BCDA-APS/apstools/issues/293>`_
       remove run_blocker_in_plan()
    * `#292 <https://github.com/BCDA-APS/apstools/issues/292>`_
       remove list_recent_scans()
    * `#291 <https://github.com/BCDA-APS/apstools/issues/291>`_
       remove unix_cmd()
    * `#288 <https://github.com/BCDA-APS/apstools/issues/288>`_
       add object_explorer() (from APS 8-ID-I)

:1.1.19:  released *2020-02-15*

    * `#285 <https://github.com/BCDA-APS/apstools/issues/285>`_
       add EpicsMotorResolutionMixin
    * `#284 <https://github.com/BCDA-APS/apstools/issues/284>`_
       adjust ophyd.EpicsMotor when motor limits changed from other EPICS client
    * `#283 <https://github.com/BCDA-APS/apstools/issues/283>`_
       print_RE_md() now returns a pyRestTable.Table object

:1.1.18:  released *2020-02-09*

    * PyPI would not accept the 1.1.17 version: `filename has already been used`
    * see release notes for 1.1.17

:1.1.17:  released *2020-02-09* - hot fixes

    * `#277 <https://github.com/BCDA-APS/apstools/issues/277>`_
       replace .value with .get()
    * `#276 <https://github.com/BCDA-APS/apstools/issues/276>`_
       update ophyd metadata after motor set_lim()
    * `#274 <https://github.com/BCDA-APS/apstools/issues/274>`_
       APS user operations could be in mode 1 OR 2

:1.1.16:  released *2019-12-05*

    * `#269 <https://github.com/BCDA-APS/apstools/issues/269>`_
       bug: shutter does not move when expected
    * `#268 <https://github.com/BCDA-APS/apstools/issues/268>`_
       add `redefine_motor_position()` plan
    * `#267 <https://github.com/BCDA-APS/apstools/issues/267>`_
       remove `lineup()` plan for now
    * `#266 <https://github.com/BCDA-APS/apstools/issues/266>`_
       bug fix for #265
    * `#265 <https://github.com/BCDA-APS/apstools/issues/265>`_
       refactor of #264
    * `#264 <https://github.com/BCDA-APS/apstools/issues/264>`_
       Limit number of traces shown on a plot - use a FIFO
    * `#263 <https://github.com/BCDA-APS/apstools/issues/263>`_
       `device_read2table()` should print unless optioned False
    * `#262 <https://github.com/BCDA-APS/apstools/issues/262>`_
       add `lineup()` plan (from APS 8-ID-I XPCS)

:1.1.15:  released *2019-11-21* : bug fixes, adds asyn record support

    * `#259 <https://github.com/BCDA-APS/apstools/issues/259>`_
       resolve AssertionError from setup_lorentzian_swait
    * `#258 <https://github.com/BCDA-APS/apstools/issues/258>`_
       swait record does not units, some other fields
    * `#255 <https://github.com/BCDA-APS/apstools/issues/255>`_
       plans: resolve indentation error
    * `#254 <https://github.com/BCDA-APS/apstools/issues/254>`_
       add computed APS cycle as signal
    * `#252 <https://github.com/BCDA-APS/apstools/issues/252>`_
       synApps: add asyn record support

:1.1.14:  released *2019-09-03* : bug fixes, more synApps support

    * `#246 <https://github.com/BCDA-APS/apstools/issues/246>`_
       synApps: shorten name from synApps_ophyd
    * `#245 <https://github.com/BCDA-APS/apstools/issues/245>`_
       swait & calcout: change from *EpicsMotor* to any *EpicsSignal*
    * `#240 <https://github.com/BCDA-APS/apstools/issues/240>`_
       swait: refactor swait record & userCalc support
    * `#239 <https://github.com/BCDA-APS/apstools/issues/239>`_
       transform: add support for transform record
    * `#238 <https://github.com/BCDA-APS/apstools/issues/238>`_
       calcout: add support for calcout record & userCalcOuts
    * `#237 <https://github.com/BCDA-APS/apstools/issues/237>`_
       epid: add support for epid record
    * `#234 <https://github.com/BCDA-APS/apstools/issues/234>`_
       utils: replicate the `unix()` command
    * `#230 <https://github.com/BCDA-APS/apstools/issues/230>`_
       signals: resolve TypeError

:1.1.13:  released *2019-08-15* : enhancements, bug fix, rename

    * `#226 <https://github.com/BCDA-APS/apstools/issues/226>`_
       writer: unit tests for empty #O0 & P0 control lines
    * `#224 <https://github.com/BCDA-APS/apstools/issues/224>`_
       rename: list_recent_scans --> listscans
    * `#222 <https://github.com/BCDA-APS/apstools/issues/222>`_
       writer: add empty #O0 and #P0 lines
    * `#220 <https://github.com/BCDA-APS/apstools/issues/220>`_
       ProcessController: bug fix - raised TypeError

:1.1.12:  released *2019-08-05* : bug fixes & updates

    * `#219 <https://github.com/BCDA-APS/apstools/issues/219>`_
       ``ProcessController``: bug fixes
    * `#218 <https://github.com/BCDA-APS/apstools/issues/218>`_
       ``replay()``: sort chronological by default
    * `#216 <https://github.com/BCDA-APS/apstools/issues/216>`_
       ``replay()``: fails when not list

:1.1.11:  released *2019-07-31* : updates & new utility

    * `#214 <https://github.com/BCDA-APS/apstools/issues/214>`_
       new: ``apstools.utils.APS_utils.replay()``
    * `#213 <https://github.com/BCDA-APS/apstools/issues/213>`_
       ``list_recent_scans`` show ``exit_status``
    * `#212 <https://github.com/BCDA-APS/apstools/issues/212>`_
       ``list_recent_scans`` show reconstructed scan command

:1.1.10:  released *2019-07-30* : updates & bug fix

    * `#211 <https://github.com/BCDA-APS/apstools/issues/211>`_
       ``devices`` calls to superclass ``__init__()``
    * `#209 <https://github.com/BCDA-APS/apstools/issues/209>`_
       ``devices`` call to superclass ``__init__()``
    * `#207 <https://github.com/BCDA-APS/apstools/issues/207>`_
       ``show_ophyd_symbols`` also shows labels
    * `#206 <https://github.com/BCDA-APS/apstools/issues/206>`_
       new: ``apstools.utils.APS_utils.list_recent_scans()``
    * `#205 <https://github.com/BCDA-APS/apstools/issues/205>`_
       ``show_ophyd_symbols`` uses ipython shell's namespace
    * `#202 <https://github.com/BCDA-APS/apstools/issues/202>`_
       add ``labels`` attribute to enable ``wa`` and ``ct`` magic commands

:1.1.9:  released *2019-07-28* : updates & bug fix

    * `#203 <https://github.com/BCDA-APS/apstools/issues/203>`_
       `SpecWriterCallback`: `#N` is number of data columns
    * `#199 <https://github.com/BCDA-APS/apstools/issues/199>`_
       `spec2ophyd` handle CNTPAR:read_misc_1

:1.1.8:  released *2019-07-25* : updates

    * `#196 <https://github.com/BCDA-APS/apstools/issues/196>`_
       `spec2ophyd` handle MOTPAR:read_misc_1
    * `#194 <https://github.com/BCDA-APS/apstools/issues/194>`_
       new ``show_ophyd_symbols`` shows table of global ophyd ``Signal`` and ``Device`` instances
    * `#193 <https://github.com/BCDA-APS/apstools/issues/193>`_
       `spec2ophyd` ignore None items in SPEC config file
    * `#192 <https://github.com/BCDA-APS/apstools/issues/192>`_
       `spec2ophyd` handles VM_EPICS_PV in SPEC config file
    * `#191 <https://github.com/BCDA-APS/apstools/issues/191>`_
       `spec2ophyd` handles PSE_MAC_MOT in SPEC config file
    * `#190 <https://github.com/BCDA-APS/apstools/issues/190>`_
       `spec2ophyd` handles MOTPAR in SPEC config file

:1.1.7:  released 2019-07-04

    * `DEPRECATION <https://github.com/BCDA-APS/apstools/issues/90#issuecomment-483405890>`_
	   `apstools.plans.run_blocker_in_plan()` will be removed by 2019-12-31.
	   Do not write blocking code in bluesky plans.
    * Dropped python 3.5 from supported versions
    * `#175 <https://github.com/BCDA-APS/apstools/issues/175>`_
       move `plans.run_in_thread()` to `utils.run_in_thread()`
    * `#168 <https://github.com/BCDA-APS/apstools/issues/168>`_
       new `spec2ophyd`  migrates SPEC config file to ophyd setup
    * `#166 <https://github.com/BCDA-APS/apstools/issues/166>`_
       `device_read2table()`: format `device.read()` results in a pyRestTable.Table
    * `#161 <https://github.com/BCDA-APS/apstools/issues/161>`_
       `addDeviceDataAsStream()`: add Device as named document stream event
    * `#159 <https://github.com/BCDA-APS/apstools/issues/159>`_
       convert xlrd.XLRDError into apstools.utils.ExcelReadError
    * `#158 <https://github.com/BCDA-APS/apstools/issues/158>`_
       new ``run_command_file()`` runs a command list from text file or Excel spreadsheet

:1.1.6:  released *2019-05-26*

    * `#156 <https://github.com/BCDA-APS/apstools/issues/156>`_
       add ProcessController Device
    * `#153 <https://github.com/BCDA-APS/apstools/issues/153>`_
       print dictionary contents as table
    * `#151 <https://github.com/BCDA-APS/apstools/issues/151>`_
       EpicsMotor support for enable/disable
    * `#148 <https://github.com/BCDA-APS/apstools/issues/148>`_
       more LGTM recommendations
    * `#146 <https://github.com/BCDA-APS/apstools/issues/146>`_
       LGTM code review recommendations
    * `#143 <https://github.com/BCDA-APS/apstools/issues/143>`_
       filewriter fails to raise IOError
    * `#141 <https://github.com/BCDA-APS/apstools/issues/141>`_
       ValueError during tune()

:1.1.5:  released *2019-05-14*

    * `#135 <https://github.com/BCDA-APS/apstools/issues/135>`_
       add refresh button to snapshot GUI

:1.1.4:  released *2019-05-14*

    * `#140 <https://github.com/BCDA-APS/apstools/issues/140>`_
       `event-model` needs at least v1.8.0
    * `#139 <https://github.com/BCDA-APS/apstools/issues/139>`_
       ``ValueError`` in :func:`~apstools.plans.TuneAxis.tune._scan`

:1.1.3:  released *2019-05-10*

    * adds packaging dependence on event-model
    * `#137 <https://github.com/BCDA-APS/apstools/issues/137>`_
       adds `utils.json_export()` and `utils.json_import()`

:1.1.1:  released *2019-05-09*

    * adds packaging dependence on spec2nexus
    * `#136 <https://github.com/BCDA-APS/apstools/issues/136>`_
       get json document stream(s)
    * `#134 <https://github.com/BCDA-APS/apstools/issues/134>`_
       add build on travis-ci with py3.7
    * `#130 <https://github.com/BCDA-APS/apstools/issues/130>`_
       fix conda recipe and pip dependencies (thanks to Maksim Rakitin!)
    * `#128 <https://github.com/BCDA-APS/apstools/issues/128>`_
       SpecWriterCallback.newfile() problem with scan_id = 0
    * `#127 <https://github.com/BCDA-APS/apstools/issues/127>`_
       fixed: KeyError from SPEC filewriter
    * `#126 <https://github.com/BCDA-APS/apstools/issues/126>`_
       add uid to metadata
    * `#125 <https://github.com/BCDA-APS/apstools/issues/125>`_
       SPEC filewriter scan numbering when "new" data file exists
    * `#124 <https://github.com/BCDA-APS/apstools/issues/124>`_
       fixed: utils.trim_string_for_EPICS() trimmed string too long
    * `#100 <https://github.com/BCDA-APS/apstools/issues/100>`_
       fixed: SPEC file data columns in wrong places

:1.1.0:  released *2019.04.16*

    * change release numbering to Semantic Versioning (remove all previous tags and releases)
    * batch scans using Excel spreadsheets
    * bluesky_snapshot_viewer and bluesky_snapshot
    * conda package available

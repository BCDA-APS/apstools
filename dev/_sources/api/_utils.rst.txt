.. _utilities:

==========
Utilities
==========

Assists measurement, data exploration, and the user experience.

For complete API details see the :doc:`Full API Reference <autoapi/apstools/index>`.

Also consult the :ref:`Index <genindex>` under the *apstools* heading
for links to the Exceptions, and Utilities described here.

Utilities by Activity
----------------------

.. _utils.aps_dm:

APS Data Management
+++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.aps_data_management.dm_api_cat`
     - return the APS DM Catalog API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_daq`
     - return the APS DM Data Acquisition API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_dataset_cat`
     - return the APS DM Dataset Metadata Catalog API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_ds`
     - return the APS DM Data Storage API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_file`
     - return the APS DM File API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_filecat`
     - return the APS DM Metadata Catalog Service API object
   * - :func:`~apstools.utils.aps_data_management.dm_api_proc`
     - return the APS DM Processing API object
   * - :func:`~apstools.utils.aps_data_management.dm_setup`
     - set up this session for APS Data Management
   * - :class:`~apstools.utils.aps_data_management.DM_WorkflowCache`
     - track one or more APS DM workflows for bluesky plans


.. _utils.finding:

Finding
+++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.pvregistry.findbyname`
     - find the ophyd object associated with the given ophyd name
   * - :func:`~apstools.utils.pvregistry.findbypv`
     - find all ophyd objects associated with the given EPICS PV
   * - :func:`~apstools.utils.catalog.findCatalogsInNamespace`
     - return a dictionary of databroker catalogs in the default namespace


.. _utils.listing:

Listing
+++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.device_info.listdevice`
     - describe signal information from a device in a pandas DataFrame
   * - :func:`~apstools.utils.misc.listobjects`
     - show all ophyd Signal and Device objects defined as globals
   * - :func:`~apstools.utils.list_plans.listplans`
     - list all plans
   * - :func:`~apstools.utils.list_runs.listRunKeys`
     - list all keys (column names) in a scan's stream
   * - :class:`~apstools.utils.list_runs.ListRuns`
     - list runs from a catalog according to some options
   * - :func:`~apstools.utils.list_runs.listruns`
     - list runs from catalog


.. _utils.reporting:

Reporting
+++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.log_utils.file_log_handler`
     - record logging output to a file
   * - :func:`~apstools.utils.log_utils.get_log_path`
     - return a path to ``./.logs``
   * - :func:`~apstools.utils.misc.print_RE_md`
     - print the RunEngine metadata in a table
   * - :func:`~apstools.utils.log_utils.setup_IPython_console_logging`
     - record all input and output from the IPython console
   * - :class:`~apstools.utils.slit_core.SlitGeometry`
     - slit size and center as a named tuple
   * - :func:`~apstools.utils.log_utils.stream_log_handler`
     - record logging output to a stream such as the console


.. _utils.other:

Other Utilities
+++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.statistics.array_index`
     - return the index of the first occurrence of value in an array
   * - :func:`~apstools.utils.misc.cleanupText`
     - convert text so it can be used as a dictionary key
   * - :func:`~apstools.utils.misc.connect_pvlist`
     - given a list of EPICS PV names, return a dict of EpicsSignal objects
   * - :func:`~apstools.utils.misc.dynamic_import`
     - import the object given its import path as text
   * - :class:`~apstools.utils.email.EmailNotifications`
     - send email notifications when requested
   * - :data:`~apstools.utils.statistics.factor_fwhm`
     - conversion factor between FWHM and standard deviation
   * - :func:`~apstools.utils.statistics.peak_full_width`
     - assess apparent FWHM by inspecting the data
   * - :func:`~apstools.utils.plot.plotxy`
     - plot y vs x from a bluesky run
   * - :func:`~apstools.utils.plot.select_live_plot`
     - get the first live plot matching a signal
   * - :func:`~apstools.utils.plot.select_mpl_figure`
     - get the matplotlib Figure window for y vs x
   * - :func:`~apstools.utils.plot.trim_plot_by_name`
     - replot with at most the last *n* lines, by figure name
   * - :func:`~apstools.utils.plot.trim_plot_lines`
     - replot with at most the last *n* lines for given x and y axes
   * - :func:`~apstools.utils.misc.trim_string_for_EPICS`
     - ensure a string does not exceed EPICS PV length
   * - :func:`~apstools.utils.time_constants.ts2iso`
     - convert Python timestamp (float) to ISO 8601 time in current time zone
   * - :func:`~apstools.utils.misc.unix`
     - run a UNIX command, return (stdout, stderr)
   * - :func:`~apstools.utils.apsu_controls_subnet.warn_if_not_aps_controls_subnet`
     - warn if not on APS-U controls subnet
   * - :func:`~apstools.utils.statistics.xy_statistics`
     - compute statistical measures of a 1-D array using numpy


.. _utils.general:

General
+++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.utils.misc.call_signature_decorator`
     - get the names of all function parameters supplied by the caller
   * - :func:`~apstools.utils.misc.cleanupText`
     - convert text so it can be used as a dictionary key
   * - :func:`~apstools.plans.command_list.command_list_as_table`
     - format a command list as a pyRestTable table object
   * - :func:`~apstools.utils.misc.connect_pvlist`
     - given a list of EPICS PV names, return a dict of EpicsSignal objects
   * - :func:`~apstools.utils.catalog.copy_filtered_catalog`
     - copy filtered runs from source catalog to target catalog
   * - :func:`~apstools.utils.query.db_query`
     - search the databroker v2 database
   * - :func:`~apstools.utils.misc.dictionary_table`
     - return a text table from a dictionary
   * - :func:`~apstools.utils.misc.dynamic_import`
     - import the object given its import path as text
   * - :class:`~apstools.utils.email.EmailNotifications`
     - send email notifications when requested
   * - :class:`~apstools.utils.spreadsheet.ExcelDatabaseFileBase`
     - base class: read-only support for Excel files as databases
   * - :class:`~apstools.utils.spreadsheet.ExcelDatabaseFileGeneric`
     - generic read-only handling of Excel spreadsheet-as-database
   * - :class:`~apstools.utils.spreadsheet.ExcelReadError`
     - exception when reading Excel spreadsheet
   * - :func:`~apstools.utils.pvregistry.findbyname`
     - find the ophyd object associated with the given ophyd name
   * - :func:`~apstools.utils.pvregistry.findbypv`
     - find all ophyd objects associated with the given EPICS PV
   * - :func:`~apstools.utils.catalog.findCatalogsInNamespace`
     - return a dictionary of databroker catalogs in the default namespace
   * - :func:`~apstools.utils.misc.full_dotted_name`
     - return the full dotted name of an ophyd object
   * - :func:`~apstools.utils.descriptor_support.get_stream_data_map`
     - return the names of run's detector and motor signals
   * - :func:`~apstools.utils.catalog.getCatalog`
     - return a catalog object
   * - :func:`~apstools.utils.catalog.getDatabase`
     - return a bluesky database using keyword guides or default choice
   * - :func:`~apstools.utils.catalog.getDefaultCatalog`
     - return the default databroker catalog
   * - :func:`~apstools.utils.catalog.getDefaultDatabase`
     - find the default database (has the most recent run)
   * - :func:`~apstools.utils.profile_support.getDefaultNamespace`
     - get the IPython shell's namespace dictionary
   * - :func:`~apstools.utils.list_runs.getRunData`
     - get the run's data
   * - :func:`~apstools.utils.list_runs.getRunDataValue`
     - get value of key in run stream
   * - :func:`~apstools.utils.catalog.getStreamValues`
     - get values from a previous scan stream in a databroker catalog
   * - :func:`~apstools.utils.profile_support.ipython_profile_name`
     - return the name of the current IPython profile
   * - :func:`~apstools.utils.misc.itemizer`
     - format a list of items
   * - :func:`~apstools.utils.device_info.listdevice`
     - describe signal information from a device in a pandas DataFrame
   * - :func:`~apstools.utils.misc.listobjects`
     - show all ophyd Signal and Device objects defined as globals
   * - :func:`~apstools.utils.list_plans.listplans`
     - list all plans
   * - :func:`~apstools.utils.list_runs.listRunKeys`
     - list all keys (column names) in a scan's stream
   * - :class:`~apstools.utils.list_runs.ListRuns`
     - list runs from a catalog according to some options
   * - :func:`~apstools.utils.list_runs.listruns`
     - list runs from catalog
   * - :class:`~apstools.utils.mmap_dict.MMap`
     - dictionary with keys accessible as attributes (read-only)
   * - :class:`~apstools.utils.override_parameters.OverrideParameters`
     - define parameters that can be overridden from a user configuration file
   * - :func:`~apstools.utils.misc.pairwise`
     - break a list into pairs
   * - :func:`~apstools.utils.plot.plotxy`
     - plot y vs x from a bluesky run
   * - :func:`~apstools.utils.misc.print_RE_md`
     - print the RunEngine metadata in a table
   * - :func:`~apstools.utils.catalog.quantify_md_key_use`
     - print table of different key values and how many times each appears
   * - :func:`~apstools.utils.misc.redefine_motor_position`
     - set EPICS motor record's user coordinate to a new position
   * - :func:`~apstools.utils.misc.render`
     - round floating-point numbers to significant figures
   * - :func:`~apstools.utils.misc.replay`
     - replay the document stream from one or more scans
   * - :func:`~apstools.utils.memory.rss_mem`
     - return memory used by this process
   * - :func:`~apstools.utils.misc.run_in_thread`
     - decorator: run a function in a thread
   * - :func:`~apstools.utils.misc.safe_ophyd_name`
     - make text safe to be used as an ophyd object name
   * - :func:`~apstools.utils.plot.select_live_plot`
     - get the first live plot matching a signal
   * - :func:`~apstools.utils.plot.select_mpl_figure`
     - get the matplotlib Figure window for y vs x
   * - :func:`~apstools.utils.misc.split_quoted_line`
     - split a line into words, some of which may be quoted
   * - :class:`~apstools.utils.stored_dict.StoredDict`
     - a MutableMapping which syncs its contents to storage
   * - :func:`~apstools.utils.list_runs.summarize_runs`
     - report bluesky run metrics from the databroker
   * - :func:`~apstools.utils.misc.text_encode`
     - encode source using the default codepoint
   * - :func:`~apstools.utils.misc.to_unicode_or_bust`
     - convert bytes to unicode
   * - :func:`~apstools.utils.plot.trim_plot_by_name`
     - replot with at most the last *n* lines, by figure name
   * - :func:`~apstools.utils.plot.trim_plot_lines`
     - replot with at most the last *n* lines for given x and y axes
   * - :func:`~apstools.utils.misc.trim_string_for_EPICS`
     - ensure a string does not exceed EPICS PV length
   * - :func:`~apstools.utils.misc.unix`
     - run a UNIX command, return (stdout, stderr)

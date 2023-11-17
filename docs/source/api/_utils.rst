==========
Utilities
==========

Various utilities to help APS use the Bluesky framework.

Also consult the :ref:`Index <genindex>` under the *apstools* heading
for links to the Exceptions, and Utilities described
here.

Utilities by Activity
----------------------

.. _utils.finding:

Finding
+++++++++++

.. autosummary::

   ~apstools.utils.pvregistry.findbyname
   ~apstools.utils.pvregistry.findbypv
   ~apstools.utils.catalog.findCatalogsInNamespace

.. _utils.listing:

Listing
+++++++++++

.. autosummary::

   ~apstools.utils.device_info.listdevice
   ~apstools.utils.misc.listobjects
   ~apstools.utils.list_plans.listplans
   ~apstools.utils.list_runs.listRunKeys
   ~apstools.utils.list_runs.ListRuns
   ~apstools.utils.list_runs.listruns

.. _utils.reporting:

Reporting
+++++++++++

.. autosummary::

   ~apstools.utils.misc.print_RE_md
   ~apstools.utils.log_utils.file_log_handler
   ~apstools.utils.log_utils.get_log_path
   ~apstools.utils.log_utils.setup_IPython_console_logging
   ~apstools.utils.log_utils.stream_log_handler
   ~apstools.utils.slit_core.SlitGeometry

.. _utils.other:

Other Utilities
++++++++++++++++

.. autosummary::

   ~apstools.utils.aps_data_management.dm_setup
   ~apstools.utils.apsu_controls_subnet.warn_if_not_aps_controls_subnet
   ~apstools.utils.misc.cleanupText
   ~apstools.utils.misc.connect_pvlist
   ~apstools.utils.email.EmailNotifications
   ~apstools.utils.plot.select_live_plot
   ~apstools.utils.plot.select_mpl_figure
   ~apstools.utils.plot.trim_plot_by_name
   ~apstools.utils.plot.trim_plot_lines
   ~apstools.utils.misc.trim_string_for_EPICS
   ~apstools.utils.misc.unix

.. _utils.general:

General
+++++++++++

.. autosummary::

   ~apstools.utils.misc.cleanupText
   ~apstools.plans.command_list.command_list_as_table
   ~apstools.utils.misc.connect_pvlist
   ~apstools.utils.catalog.copy_filtered_catalog
   ~apstools.utils.query.db_query
   ~apstools.utils.misc.dictionary_table
   ~apstools.utils.email.EmailNotifications
   ~apstools.utils.spreadsheet.ExcelDatabaseFileBase
   ~apstools.utils.spreadsheet.ExcelDatabaseFileGeneric
   ~apstools.utils.spreadsheet.ExcelReadError
   ~apstools.utils.pvregistry.findbyname
   ~apstools.utils.pvregistry.findbypv
   ~apstools.utils.catalog.findCatalogsInNamespace
   ~apstools.utils.misc.full_dotted_name
   ~apstools.utils.catalog.getCatalog
   ~apstools.utils.catalog.getDatabase
   ~apstools.utils.catalog.getDefaultCatalog
   ~apstools.utils.catalog.getDefaultDatabase
   ~apstools.utils.profile_support.getDefaultNamespace
   ~apstools.utils.list_runs.getRunData
   ~apstools.utils.list_runs.getRunDataValue
   ~apstools.utils.catalog.getStreamValues
   ~apstools.utils.profile_support.ipython_profile_name
   ~apstools.utils.misc.itemizer
   ~apstools.utils.device_info.listdevice
   ~apstools.utils.misc.listobjects
   ~apstools.utils.list_plans.listplans
   ~apstools.utils.list_runs.listRunKeys
   ~apstools.utils.list_runs.ListRuns
   ~apstools.utils.list_runs.listruns
   ~apstools.utils.override_parameters.OverrideParameters
   ~apstools.utils.misc.pairwise
   ~apstools.utils.plot.plotxy
   ~apstools.utils.misc.print_RE_md
   ~apstools.utils.catalog.quantify_md_key_use
   ~apstools.utils.misc.redefine_motor_position
   ~apstools.utils.misc.replay
   ~apstools.utils.memory.rss_mem
   ~apstools.utils.misc.run_in_thread
   ~apstools.utils.misc.safe_ophyd_name
   ~apstools.utils.plot.select_live_plot
   ~apstools.utils.plot.select_mpl_figure
   ~apstools.utils.misc.split_quoted_line
   ~apstools.utils.list_runs.summarize_runs
   ~apstools.utils.misc.text_encode
   ~apstools.utils.misc.to_unicode_or_bust
   ~apstools.utils.plot.trim_plot_by_name
   ~apstools.utils.plot.trim_plot_lines
   ~apstools.utils.misc.trim_string_for_EPICS
   ~apstools.utils.misc.unix

Submodules
---------------

.. automodule:: apstools.utils.aps_data_management
    :members:

.. automodule:: apstools.utils.apsu_controls_subnet
    :members:

.. automodule:: apstools.utils.catalog
    :members:

.. automodule:: apstools.utils.device_info
    :members:

.. automodule:: apstools.utils.email
    :members:

.. automodule:: apstools.utils.image_analysis
    :members:

.. automodule:: apstools.utils.list_plans
    :members:

.. automodule:: apstools.utils.list_runs
    :members:

.. automodule:: apstools.utils.log_utils
    :members:

.. automodule:: apstools.utils.memory
    :members:

.. automodule:: apstools.utils.misc
    :members:

.. automodule:: apstools.utils.override_parameters
    :members:

.. automodule:: apstools.utils.plot
    :members:

.. automodule:: apstools.utils.profile_support
    :members:

.. automodule:: apstools.utils.pvregistry
    :members:

.. automodule:: apstools.utils.query
    :members:

.. automodule:: apstools.utils.slit_core
    :members:

.. automodule:: apstools.utils.spreadsheet
    :members:

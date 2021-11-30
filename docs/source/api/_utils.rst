==========
Utilities
==========

Various utilities to help APS use the Bluesky framework.

Also consult the :ref:`Index <genindex>` under the *apstools* heading
for links to the Exceptions, and Utilities described
here.

Categories
----------

.. _utils.finding:

FINDING
+++++++++++

.. autosummary::

   ~findbyname
   ~findbypv
   ~findCatalogsInNamespace

.. _utils.listing:

LISTING
+++++++++++

.. autosummary::

   ~apstools._utils.device_info.listdevice
   ~listobjects
   ~apstools._utils.list_plans.listplans
   ~listRunKeys
   ~ListRuns
   ~listruns

.. _utils.reporting:

REPORTING
+++++++++++

.. autosummary::

   ~print_RE_md
   ~print_snapshot_list

.. _utils.other:

OTHER UTILITIES
++++++++++++++++

.. autosummary::

   ~cleanupText
   ~connect_pvlist
   ~EmailNotifications
   ~select_live_plot
   ~select_mpl_figure
   ~trim_plot_by_name
   ~trim_plot_lines
   ~trim_string_for_EPICS
   ~unix

.. _utils.general:

GENERAL
+++++++++++

.. autosummary::

   ~cleanupText
   ~command_list_as_table
   ~connect_pvlist
   ~copy_filtered_catalog
   ~db_query
   ~dictionary_table
   ~EmailNotifications
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ExcelReadError
   ~findbyname
   ~findbypv
   ~findCatalogsInNamespace
   ~full_dotted_name
   ~getCatalog
   ~getDatabase
   ~getDefaultCatalog
   ~getDefaultDatabase
   ~apstools._utils.profile_support.getDefaultNamespace
   ~getRunData
   ~getRunDataValue
   ~getStreamValues
   ~apstools._utils.profile_support.ipython_profile_name
   ~itemizer
   ~apstools._utils.device_info.listdevice
   ~listobjects
   ~apstools._utils.list_plans.listplans
   ~listRunKeys
   ~ListRuns
   ~listruns
   ~apstools._utils.override_parameters.OverrideParameters
   ~pairwise
   ~print_RE_md
   ~print_snapshot_list
   ~quantify_md_key_use
   ~redefine_motor_position
   ~replay
   ~rss_mem
   ~run_in_thread
   ~safe_ophyd_name
   ~select_live_plot
   ~select_mpl_figure
   ~split_quoted_line
   ~summarize_runs
   ~text_encode
   ~to_unicode_or_bust
   ~trim_plot_by_name
   ~trim_plot_lines
   ~trim_string_for_EPICS
   ~unix

Submodules
---------------

.. automodule:: apstools._utils.catalog
    :members:

.. automodule:: apstools._utils.device_info
    :members:

.. automodule:: apstools._utils.list_plans
    :members:

.. automodule:: apstools._utils.list_runs
    :members:

.. automodule:: apstools._utils.override_parameters
    :members:

.. automodule:: apstools._utils.profile_support
    :members:

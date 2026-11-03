.. _plans:

===========
Plans
===========

Customize your measurement procedures.

For complete API details see the :doc:`Full API Reference <autoapi/apstools/index>`.

Plans and Support by Activity
------------------------------

.. _plans.batch:

Batch Scanning
+++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.plans.command_list.execute_command_list`
     - execute the command list as a plan
   * - :func:`~apstools.plans.command_list.get_command_list`
     - return command list from either text or Excel file
   * - :func:`~apstools.plans.command_list.parse_Excel_command_file`
     - parse an Excel spreadsheet with commands, return as command list
   * - :func:`~apstools.plans.command_list.parse_text_command_file`
     - parse a text file with commands, return as command list
   * - :func:`~apstools.plans.command_list.register_command_handler`
     - define the function called to execute the command list
   * - :func:`~apstools.plans.command_list.run_command_file`
     - execute a list of commands from a text or Excel file as a plan
   * - :func:`~apstools.plans.command_list.summarize_command_file`
     - print the command list from a text or Excel file


.. _plans.custom:

Custom Scans
+++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.plans.doc_run.documentation_run`
     - save text as a bluesky run
   * - :func:`~apstools.plans.alignment.edge_align`
     - align to the edge given mover and detector data, relative to absolute position
   * - :func:`~apstools.plans.labels_to_streams.label_stream_decorator`
     - decorator: write labeled device(s) to bluesky stream(s)
   * - :func:`~apstools.plans.alignment.lineup`
     - (*deprecated*) lineup and center a given axis, relative to current position
   * - :func:`~apstools.plans.alignment.lineup2`
     - lineup and center a given mover, relative to the current position
   * - :func:`~apstools.plans.xpcs_mesh.mesh_list_grid_scan`
     - scan over a multi-dimensional mesh with *n* total points per motor trajectory
   * - :func:`~apstools.plans.nscan_support.nscan`
     - scan over *n* variables moved together, each in equally spaced steps
   * - :func:`~apstools.plans.sscan_support.sscan_1D`
     - simple 1-D scan using EPICS synApps sscan record
   * - :class:`~apstools.plans.alignment.TuneAxis`
     - tune a single axis with a signal


.. _plans.overall:

Overall
+++++++++++++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.plans.doc_run.addDeviceDataAsStream`
     - (*deprecated*) renamed to :func:`~apstools.plans.doc_run.write_stream`
   * - :func:`~apstools.plans.command_list.command_list_as_table`
     - format a command list as a pyRestTable table object
   * - :func:`~apstools.plans.doc_run.documentation_run`
     - save text as a bluesky run
   * - :func:`~apstools.plans.command_list.execute_command_list`
     - execute the command list as a plan
   * - :func:`~apstools.plans.command_list.get_command_list`
     - return command list from either text or Excel file
   * - :func:`~apstools.plans.labels_to_streams.label_stream_decorator`
     - decorator: write labeled device(s) to bluesky stream(s)
   * - :func:`~apstools.plans.labels_to_streams.label_stream_stub`
     - write ophyd-labeled objects to open bluesky run streams
   * - :func:`~apstools.plans.labels_to_streams.label_stream_wrapper`
     - decorator support: write labeled device(s) to stream(s)
   * - :func:`~apstools.plans.alignment.lineup`
     - (*deprecated*) lineup and center a given axis, relative to current position
   * - :func:`~apstools.plans.alignment.lineup2`
     - lineup and center a given mover, relative to the current position
   * - :func:`~apstools.plans.xpcs_mesh.mesh_list_grid_scan`
     - scan over a multi-dimensional mesh with *n* total points per motor trajectory
   * - :func:`~apstools.plans.nscan_support.nscan`
     - scan over *n* variables moved together, each in equally spaced steps
   * - :func:`~apstools.plans.command_list.parse_Excel_command_file`
     - parse an Excel spreadsheet with commands, return as command list
   * - :func:`~apstools.plans.command_list.parse_text_command_file`
     - parse a text file with commands, return as command list
   * - :func:`~apstools.plans.command_list.register_command_handler`
     - define the function called to execute the command list
   * - :func:`~apstools.plans.input_plan.request_input`
     - request input from the user during a plan
   * - :func:`~apstools.plans.stage_sigs_support.restorable_stage_sigs`
     - decorator: save and restore a device's stage_sigs around a plan
   * - :func:`~apstools.plans.run_blocking_function_plan.run_blocking_function`
     - run a blocking function as a bluesky plan in a thread
   * - :func:`~apstools.plans.command_list.run_command_file`
     - execute a list of commands from a text or Excel file as a plan
   * - :func:`~apstools.plans.sscan_support.sscan_1D`
     - simple 1-D scan using EPICS synApps sscan record
   * - :func:`~apstools.plans.command_list.summarize_command_file`
     - print the command list from a text or Excel file
   * - :class:`~apstools.plans.alignment.TuneAxis`
     - tune a single axis with a signal
   * - :func:`~apstools.plans.doc_run.write_stream`
     - add an ophyd Device as an additional document stream


Also consult the :ref:`Index <genindex>` under the *Bluesky* heading
for links to the Callbacks, Devices, Exceptions, and Plans described
here.

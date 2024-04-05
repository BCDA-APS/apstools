.. _plans:

===========
Plans
===========

Plans that might be useful at the APS when using Bluesky.

Plans and Support by Activity
------------------------------

.. _plans.batch:

Batch Scanning
+++++++++++++++++++

.. autosummary::

   ~apstools.plans.command_list.execute_command_list
   ~apstools.plans.command_list.get_command_list
   ~apstools.plans.command_list.parse_Excel_command_file
   ~apstools.plans.command_list.parse_text_command_file
   ~apstools.plans.command_list.register_command_handler
   ~apstools.plans.command_list.run_command_file
   ~apstools.plans.command_list.summarize_command_file

.. _plans.custom:

Custom Scans
+++++++++++++++++++

.. autosummary::

   ~apstools.plans.doc_run.documentation_run
   ~apstools.plans.labels_to_streams.label_stream_decorator
   ~apstools.plans.alignment.lineup
   ~apstools.plans.alignment.lineup2
   ~apstools.plans.nscan_support.nscan
   ~apstools.plans.sscan_support.sscan_1D
   ~apstools.plans.alignment.TuneAxis
   ~apstools.plans.alignment.tune_axes

.. _plans.overall:

Overall
+++++++++++++++++++

.. autosummary::

   ~apstools.plans.doc_run.addDeviceDataAsStream
   ~apstools.plans.command_list.command_list_as_table
   ~apstools.plans.doc_run.documentation_run
   ~apstools.plans.command_list.execute_command_list
   ~apstools.plans.command_list.get_command_list
   ~apstools.plans.alignment.lineup
   ~apstools.plans.alignment.lineup2
   ~apstools.plans.nscan_support.nscan
   ~apstools.plans.command_list.parse_Excel_command_file
   ~apstools.plans.command_list.parse_text_command_file
   ~apstools.plans.labels_to_streams.label_stream_decorator
   ~apstools.plans.labels_to_streams.label_stream_stub
   ~apstools.plans.labels_to_streams.label_stream_wrapper
   ~apstools.plans.command_list.register_command_handler
   ~apstools.plans.command_list.run_command_file
   ~apstools.plans.input_plan.request_input
   ~apstools.plans.stage_sigs_support.restorable_stage_sigs
   ~apstools.plans.run_blocking_function_plan.run_blocking_function
   ~apstools.plans.sscan_support.sscan_1D
   ~apstools.plans.command_list.summarize_command_file
   ~apstools.plans.alignment.TuneAxis
   ~apstools.plans.alignment.tune_axes
   ~apstools.plans.doc_run.write_stream

Also consult the :ref:`Index <genindex>` under the *Bluesky* heading
for links to the Callbacks, Devices, Exceptions, and Plans described
here.

Submodules
---------------

.. automodule:: apstools.plans.alignment
    :members:

.. automodule:: apstools.plans.command_list
    :members:

.. automodule:: apstools.plans.doc_run
    :members:

.. automodule:: apstools.plans.input_plan
    :members:

.. automodule:: apstools.plans.labels_to_streams
    :members:

.. automodule:: apstools.plans.nscan_support
    :members:

.. automodule:: apstools.plans.run_blocking_function_plan
    :members:

.. automodule:: apstools.plans.sscan_support
    :members:

.. automodule:: apstools.plans.stage_sigs_support
    :members:

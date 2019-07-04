.. index:: Excel scan, scan; Excel, command list

.. _example_run_command_file:

Example: the :func:`~apstools.plans.run_command_file` plan
================================================================

You can use a text file or an Excel spreadsheet as a multi-sample 
batch scan tool using the :func:`~apstools.plans.run_command_file` plan.
This section is divided into these parts.

* :ref:`command_file`

	* :ref:`command_file_text`
	* :ref:`command_file_spreadsheet`

* :ref:`command_file_actions`
* :ref:`command_file_register`
* :ref:`command_file_testing`
* :ref:`command_file_running`
* :ref:`command_file_appendix`

.. _command_file:

The Command File
++++++++++++++++

A command file can be written as either a plain text file or a 
spreadsheet (such as from Microsoft Excel or Libre Office).

.. _command_file_text:

Text Command File
-----------------

For example, given a text command file (named ``sample_example.txt``) 
with content as shown ...

.. literalinclude:: ../resources/sample_example.txt
   :tab-width: 4
   :linenos:
   :language: guess

... can be summarized in a bluesky ipython session:

.. code-block:: guess

	In [1]: import apstools.plans
	In [2]: apstools.plans.summarize_command_file("sample_example.txt")
	Command file: sample_example.xlsx
	====== ========== ===========================================================
	line # action     parameters                                                 
	====== ========== ===========================================================
	3      step_scan  5.07, 8.3, 0.0, Water Blank, deionized                     
	4      other_scan 5.07, 8.3, 0.0, Water Blank, deionized                     
	8      this       line, will, not, be, recognized, by, execute_command_list()
	====== ========== ===========================================================

Observe which lines (3, 4, and 8) in the text file are part of
the summary.  The other lines are either comments or blank.
The action on line 8 will be passed to ``execute_command_list()`` which will
then report the ``this`` action it is not handled.  
(Looks like another type of a comment.)
See :func:`~apstools.plans.parse_text_command_file()` for more details.

.. _command_file_spreadsheet:

Spreadsheet Command File
------------------------

Follow the example spreadsheet (in the :ref:`examples_downloads` section)
and accompanying Jupyter notebook [#]_ to write your own ``Excel_plan()``.

.. [#] https://github.com/BCDA-APS/apstools/blob/master/docs/source/resources/excel_scan.ipynb

For example, given a spreadsheet (named ``sample_example.xlsx``) 
with content as shown in the next figure:

.. figure:: ../resources/sample_example.jpg
   :width: 95%
   
   Image of ``sample_example.xlsx`` spreadsheet file.

.. tip:: Place the column labels on the fourth row of the spreadsheet, 
   starting in the first column.
   The actions start on the next row.  The first blank row indicates
   the end of the command table within the spreadsheet.
   Use as many columns as you need, one column per argument.

This spreadsheet can be summarized in a bluesky ipython session:

.. code-block:: guess

	In [1]: import apstools.plans
	In [2]: apstools.plans.summarize_command_file("sample_example.xlsx")
	Command file: sample_example.xlsx
	====== ================================================================== ======================================
	line # action                                                             parameters                            
	====== ================================================================== ======================================
	1      step_scan                                                          5.07, 8.3, 0.0, Water Blank, deionized
	2      other_scan                                                         5.07, 8.3, 0.0, Water Blank, deionized
	3      this will be ignored (and also the next blank row will be ignored)                                       
	====== ================================================================== ======================================

Note that lines 9 and 10 in the spreadsheet file are not part of
the summary.  The spreadsheet handler will stop reading the list of actions
at the first blank line.  The action described on line 3 will not be handled
(since we will not define an action named 
``this will be ignored (and also the next blank row will be ignored)``).
See :func:`~apstools.plans.parse_Excel_command_file()` for more details.

.. _command_file_actions:

The *Actions*
++++++++++++++++

To use this example with the :func:`~apstools.plans.run_command_file()` plan, it is 
necessary to redefine the :func:`~apstools.plans.execute_command_list()` plan, 
we must write a plan to handle every different type of action described 
in the spreadsheet.  For ``sample_example.xlsx``, we need to 
handle the ``step_scan`` and ``other_scan`` actions.  

.. tip:: Always write these *actions* as bluesky plans.  
  To test your *actions*, use either 
  ``bluesky.simulators.summarize_plan(step_scan())``
  or ``bluesky.simulators.summarize_plan(other_scan())``.

Here are examples of those two actions (and a stub for an additional 
instrument procedure to make the example more realistic):

.. code-block:: python
	:linenos:
   
	def step_scan(sx, sy, thickness, title, md={}):
		md["sample_title"] = title			# log this metadata
		md["sample_thickness"] = thickness	# log this metadata
		yield from bluesky.plan_stubs.mv(
			sample_stage.x, sx,
			sample_stage.y, sy,
		)
		yield from prepare_detector("scintillator")
		yield from bluesky.plans.scan([scaler], motor, 0, 180, 360, md=md)
	
	def other_scan(sx, sy, thickness, title, md={}):
		md["sample_title"] = title			# log this metadata
		md["sample_thickness"] = thickness	# log this metadata
		yield from bluesky.plan_stubs.mv(
			sample_stage.x, sx,
			sample_stage.y, sy,
		)
		yield from prepare_detector("areadetector")
		yield from bluesky.plans.count([areadetector], md=md)
	
	def prepare_detector(detector_name):
		# for this example, we do nothing
		# we should move the proper detector into position here
		yield from bluesky.plan_stubs.null()

Now, we replace :func:`~apstools.plans.execute_command_list()` 
with our own definition to include those two actions:

.. code-block:: python
	:linenos:
	
	def execute_command_list(filename, commands, md={}):
	    """our custom execute_command_list"""
	    full_filename = os.path.abspath(filename)
	
	    if len(commands) == 0:
	        yield from bps.null()
	        return
	
	    text = f"Command file: {filename}\n"
	    text += str(apstools.utils.command_list_as_table(commands))
	    print(text)
	
	    for command in commands:
	        action, args, i, raw_command = command
	        logger.info(f"file line {i}: {raw_command}")
	
	        _md = {}
	        _md["full_filename"] = full_filename
	        _md["filename"] = filename
	        _md["line_number"] = i
	        _md["action"] = action
	        _md["parameters"] = args    # args is shorter than parameters, means the same thing here
	
	        _md.update(md or {})      # overlay with user-supplied metadata
	
	        action = action.lower()
	        if action == "step_scan":
	            yield from step_scan(*args, md=_md)
	        elif action == "other_scan":
	            yield from other_scan(*args, md=_md)
	
	        else:
	            logger.info(f"no handling for line {i}: {raw_command}")

.. _command_file_register:

Register our own ``execute_command_list``
+++++++++++++++++++++++++++++++++++++++++

Finally, we register our new version of ``execute_command_list``
(which replaces the default :func:`~apstools.plans.execute_command_list()`)::

    APS_plans.register_command_handler(execute_command_list)

If you wish to verify that your own code has been installed, use this command::

    print(APS_plans._COMMAND_HANDLER_)

If its output contains ``apstools.plans.execute_command_list``, you have not 
registered your own function.  However, if the output looks something such as 
either of these::

	<function __main__.execute_command_list(filename, commands, md={})>
	# or
	<function execute_command_list at 0x7f4cf0d616a8>

then you have installed your own code.

.. tip:  You do not have to use the exact name ``execute_command_list``.
   By using :func:`~apstools.plans.register_command_handler()`, your handler
   function can be named as you wish.  However, the parameters must match
   the signature of :func:`~apstools.plans.execute_command_list()`.

.. _command_file_testing:

Testing the command file
++++++++++++++++++++++++

As you were developing plans for each of your actions, we showed you
how to test that each plan was free of basic syntax and bluesky procedural
errors.  The :func:`bluesky.simulators.summarize_plan()` function
will run through your plan and show you the basic data acquisition steps
that will be executed during your plan.  Becuase you did not write
any blocking code, no hardware should ever be changed by running
this plan summary.

To test our command file, run it through the 
:func:`bluesky.simulators.summarize_plan()` function::

    bluesky.simulators.summarize_plan(run_command_file("sample_example.txt"))

The output will be rather lengthy, if there are no errors.
Here are the first few lines:

.. literalinclude:: ../resources/sample_example_summary.txt
   :tab-width: 4
   :language: guess
   :lines: 1-20

and the last few lines:

.. literalinclude:: ../resources/sample_example_summary.txt
   :tab-width: 4
   :language: guess
   :lines: 728-

.. _command_file_running:

Running the command file
++++++++++++++++++++++++

Prepare the RE
-------------------

These steps were used to prepare our bluesky ipython session to run the plan:

.. code-block:: python
	:linenos:
   
	from bluesky import RunEngine
	from bluesky.utils import get_history
	RE = RunEngine(get_history())

	# Import matplotlib and put it in interactive mode.
	import matplotlib.pyplot as plt
	plt.ion()

	# load config from ~/.config/databroker/mongodb_config.yml
	from databroker import Broker
	db = Broker.named("mongodb_config")

	# Subscribe metadatastore to documents.
	# If this is removed, data is not saved to metadatastore.
	RE.subscribe(db.insert)

	# Set up SupplementalData.
	from bluesky import SupplementalData
	sd = SupplementalData()
	RE.preprocessors.append(sd)
	
	# Add a progress bar.
	from bluesky.utils import ProgressBarManager
	pbar_manager = ProgressBarManager()
	RE.waiting_hook = pbar_manager
	
	# Register bluesky IPython magics.
	from bluesky.magics import BlueskyMagics
	get_ipython().register_magics(BlueskyMagics)
	
	# Set up the BestEffortCallback.
	from bluesky.callbacks.best_effort import BestEffortCallback
	bec = BestEffortCallback()
	RE.subscribe(bec)

Also, since we are using an EPICS area detector (ADSimDetector) and have just
started its IOC, we must process at least one image from the CAM to each of the
file writing plugins we'll use (just the HDF1 for us).  A procedure has been added
to the ``ophyd.areadetector`` code for this.  Here is the command we used
for this procedure:

    areadetector.hdf1.warmup() 

Run the command file
---------------------------

To run the command file, you need to pass this to an instance of the
:class:`bluesky.RunEngine`, defined as ``RE`` above:: 

	RE(apstools.plans.run_command_file("sample_example.txt"))

The output will be rather lengthy.
Here are the first few lines of the output on my system (your hardware
may be different so the exact data columns and values will vary):

.. literalinclude:: ../resources/sample_example_run.txt
   :tab-width: 4
   :language: guess
   :lines: 1-25

and the last few lines:

.. literalinclude:: ../resources/sample_example_run.txt
   :tab-width: 4
   :language: guess
   :lines: 390-


.. _command_file_appendix:

Appendix: Other spreadsheet examples
++++++++++++++++++++++++++++++++++++

You can use an Excel spreadsheet as a multi-sample batch scan tool.  

**SIMPLE**:  Your Excel spreadsheet could be rather simple...

.. figure:: ../resources/excel_simple.jpg
   :width: 95%
   
   Unformatted Excel spreadsheet for batch scans.

See :class:`~apstools.utils.ExcelDatabaseFileGeneric` for an example bluesky plan
that reads from this spreadsheet.

**FANCY**:  ... or contain much more information, including formatting.

.. _excel_plan_spreadsheet_screen:

.. figure:: ../resources/excel_plan_spreadsheet.jpg
   :width: 95%
   
   Example Excel spreadsheet for multi-sample batch scans.

The idea is that your table will start with column labels 
in **row 4** of the Excel spreadsheet.  One of the columns will be the name
of the action (in the example, it is ``Scan Type``).  The other columns will
be parameters or other information.  Each of the rows under the labels will
describe one type of action such as a scan.  Basically, whatever you  
handle in your ``Excel_plan()``.  
Any rows that you do not handle will be reported to the console during execution
but will not result in any action.
Grow (or shrink) the table as needed.

.. note::  For now, make sure there is no content in any of the spreadsheet
   cells outside (either below or to the right) of your table.  
   Such content will trigger a cryptic error
   about a numpy float that cannot be converted.  Instead, put that content 
   in a second spreadsheet page.
   
   .. see: https://github.com/BCDA-APS/apstools/issues/116

You'll need to have an action plan for every different action your spreadsheet
will specify.  Call these plans from your ``Excel_plan()`` within an ``elif`` block,
as shown in this example.  The example ``Excel_plan()`` converts the ``Scan Type`` 
into  lower case for simpler comparisons.  Your plan can be different if you choose.

.. code-block:: python

    if scan_command == "step_scan":
        yield from step_scan(...)
    elif scan_command == "energy_scan":
        yield from scan_energy(...)
    elif scan_command == "radiograph":
        yield from AcquireImage(...)
    else:
        print(f"no handling for table row {i+1}: {row}")

The example plan saves all row parameters as metadata to the row's action.
This may be useful for diagnostic purposes.

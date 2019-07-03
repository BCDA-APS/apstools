.. index:: Excel scan, scan; Excel, command list

.. _example_run_command_file:

Example: the ``run_command_file`` plan
======================================

You can use a text file or an Excel spreadsheet as a multi-sample 
batch scan tool using the :func:`run_command_file` plan.

The Command File
++++++++++++++++

A command file can be written as either a plain text file or a 
spreadsheet (such as from Microsoft Excel or Libre Office).

Text Command File
-----------------

For example, given a text command file (named ``sample_example.txt``) 
with content as shown ...

.. literalinclude:: ../resources/sample_example.txt
   :tab-width: 4
   :linenos:
   :language: guess

... can be summarized in a bluesky ipython session:

.. code-block:: ipython

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

.. code-block:: ipython

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
	            yield from step_scan(*args. md=_md)
	        elif action == "other_scan":
	            yield from other_scan(*args. md=_md)
	
	        else:
	            logger.info(f"no handling for line {i}: {raw_command}")

Testing
++++++++++++++++

``bluesky.simulators.summarize_plan(run_command_file("sample_example.txt"))``

-tba-

Running
++++++++++++++++

``RE(run_command_file("sample_example.txt"))``

-tba-

.. TODO: re-write below per issue 178

------------

You can use an Excel spreadsheet as a multi-sample batch scan tool.  

**SIMPLE**:  Your Excel spreadsheet could be rather simple...

.. figure:: ../resources/excel_simple.jpg
   :width: 95%
   
   Unformatted Excel spreadsheet for batch scans.

See :class:`ExcelDatabaseFileGeneric` for an example bluesky plan
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

::

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
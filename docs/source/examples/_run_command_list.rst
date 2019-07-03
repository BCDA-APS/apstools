.. index:: Excel scan, scan; Excel, command list

.. _example_run_command_file:

Example: the ``run_command_file`` plan
======================================

You can use a text file or an Excel spreadsheet as a multi-sample 
batch scan tool using the :func:`run_command_file` plan.

.. TODO: re-write below per issue 178

------------

You can use an Excel spreadsheet as a multi-sample batch scan tool.  Follow
the example spreadsheet (in the 
:ref:`examples_downloads` section)
and accompanying Jupyter notebook 
(https://github.com/BCDA-APS/apstools/blob/master/docs/source/resources/excel_scan.ipynb)
to write your own ``Excel_plan()``.

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
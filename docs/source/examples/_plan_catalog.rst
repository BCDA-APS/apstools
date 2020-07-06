.. _example_plan_catalog:

Example: the ``plan_catalog`` application
==================================================

The *apstools* package provides an executable that can be
used to display a summary of all the scans in the database.
The executable wraps the demo function: :func:`~apstools.examples.plan_catalog()`.
It is for demonstration purposes only (since it does not filter
the output to any specific subset of scans).

The output is a table, formatted as restructured text, with these columns:

:date/time:

   The date and time the scan was started.

:short_uid:

   The first characters of the scan's UUID (unique identifier).

:id:

   The scan number.
   (User has control of this and could reset the counter for the next scan.)

:plan:

   Name of the plan that initiated this scan.

:args:

   Arguments to the plan that initiated this scan.


This is run as a linux console command::

   apstools_plan_catalog | tee out.txt

The :download:`full output <../resources/plan_catalog.txt>`
is almost a thousand lines.  Here are the first few lines:

.. literalinclude:: ../resources/plan_catalog.txt
   :language: console
   :linenos:
   :lines: 1-10

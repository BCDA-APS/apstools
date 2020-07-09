

.. index:: apsbss

.. _apsbss_application:

apsbss
------

Information from the APS Proposal and ESAF (experiment safety approval form) databases.

Example - command line
++++++++++++++++++++++

Before using the command-line interface, find out what
the *apsbss* application expects::

	$ apsbss  -h
	usage: apsbss.py [-h]
					{beamlines,current,cycles,esaf,proposal,clear,setup,update}
					...

	Retrieve specific records from the APS Proposal and ESAF databases

	optional arguments:
	-h, --help            show this help message and exit

	subcommand:
	{beamlines,current,cycles,esaf,proposal,clear,setup,update}
		beamlines           print list of beamlines
		current             print current ESAF(s) and proposal(s)
		cycles              print APS cycle names
		esaf                print specific ESAF
		proposal            print specific proposal
		clear               EPICS PVs: clear
		setup               EPICS PVs: setup
		update              EPICS PVs: update from BSS


Source code documentation
+++++++++++++++++++++++++

See :ref:`beamtime_source_docs` for the source code documentation.

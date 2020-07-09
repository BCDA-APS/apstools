

.. index:: apsbss

.. _apsbss_application:

apsbss
------

Provide information from APS Proposal and ESAF (experiment safety approval
form) databases as PVs at each beam line so that this information
(metadata) may be added to new data files.  The ``aps-dm-api``
(``dm`` for short) package [#]_
is used to access the APS databases as read-only.

*No information is written back to the APS databases.*

.. [#] ``dm``: https://anaconda.org/search?q=aps-dm-api

.. sidebar:: Info written to local PVs

	This information retreived from the APS databases is stored in PVs
	on the beam line subnet.  These PVs are available to *any* EPICS
	client as metadata (SPEC, area detector, Bluesky, GUI screens, logging, other).
	This design allows the local instrument team to override
	any values read from the APS databases, if that is needed.

Given a beam line name (such as ``9-ID-B,C``),
APS run cycle name (such as ``2020-2``),
proposal ID number (such as ``66083``), and
ESAF ID number (such as ``226319``),
the typical information obtained includes:

* ESAF & proposal titles
* user names
* user institutional affiliations
* user emails
* applicable dates, reported in ISO8601 time format
* is proposal propietary?
* is experiment mail-in?

These PVs are loaded on demand by the local instrument team at the beam line.

.. TODO: describe how this is done

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

.. TODO: describe each of these subcommands

.. _apsbss_ioc_management:

IOC Management
++++++++++++++

The EPICS PVs are provided by running an instance of ``apsbss.db``
either in an existing EPICS IOC or using the ``softIoc`` application
from EPICS base.  A shell script (``manage_ioc.sh``) is included
for management of the IOC::

	$ ./manage_ioc.sh
	Usage: manage_ioc.sh {start|stop|restart|status|console|run} [NAME [PREFIX]]

		COMMANDS
			console   attach to IOC console if IOC is running in screen
			restart   restart IOC
			run       run IOC in console (not screen)
			start     start IOC
			status    report if IOC is running
			stop      stop IOC

		OPTIONAL TERMS
			NAME      name of IOC session (default: apsbss)
			PREFIX    IOC prefix (default: ioc:bss:)

.. TODO: download for ``apsbss.db``


.. _apsbss_epics_gui_screens:

Displays for MEDM & caQtDM
++++++++++++++++++++++++++

Display screen files are provided for viewing the EPICS PVs
using either MEDM (``apsbss.adl``) or caQtDM (``apsbss.ui``).

.. TODO: downloads for each screen file
.. TODO: screen images here

Source code documentation
+++++++++++++++++++++++++

See :ref:`beamtime_source_docs` for the source code documentation.

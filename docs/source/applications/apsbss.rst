

.. index:: apsbss

.. _apsbss_application:

apsbss
------

Provide information from APS Proposal and ESAF (experiment safety approval
form) databases as PVs at each beam line so that this information
(metadata) may be added to new data files.  The ``aps-dm-api``
(``dm`` for short) package [#]_
is used to access the APS databases as read-only.

*No information is written back to the APS
databases from this software.*

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
See the :ref:`apsbss_startup` section for details about
managing the EPICS PVs.

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

See :ref:`beamtime_source_docs` for the source code documentation
of each of these subcommands.

IOC Management
++++++++++++++

The EPICS PVs are provided by running an instance of ``apsbss.db``
either in an existing EPICS IOC or using the ``softIoc`` application
from EPICS base.  A shell script (``apsbss_ioc.sh``) is included
for loading Proposal and ESAF information from the
APS databases into the IOC.

* :download:`apsbss.db <../../../apstools/beamtime/apsbss.db>`

See the section titled ":ref:`apsbss_startup`"
for the management of the EPICS IOC.

.. _apsbss_epics_gui_screens:

Displays for MEDM & caQtDM
++++++++++++++++++++++++++

Display screen files are provided for viewing the EPICS PVs
using either MEDM (``apsbss.adl``) or caQtDM (``apsbss.ui``).

* MEDM screen: :download:`apsbss.adl <../../../apstools/beamtime/apsbss.adl>`
* caQtDM screen: :download:`apsbss.ui <../../../apstools/beamtime/apsbss.ui>`

.. TODO: screen images here

Downloads
+++++++++

* EPICS database: :download:`apsbss.db <../../../apstools/beamtime/apsbss.db>`
* EPICS IOC shell script :download:`apsbss_ioc.sh <../../../apstools/beamtime/apsbss_ioc.sh>`
* MEDM screen: :download:`apsbss.adl <../../../apstools/beamtime/apsbss.adl>`
* caQtDM screen: :download:`apsbss.ui <../../../apstools/beamtime/apsbss.ui>`

Source code documentation
+++++++++++++++++++++++++

See :ref:`beamtime_source_docs` for the source code documentation.

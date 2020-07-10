.. _apsbss_startup:

apsbss: IOC Startup and Management
==================================

The :ref:`apsbss_application` software
provides information from the APS Proposal
and ESAF (experiment safety approval
form) databases as PVs to the local controls network.
The ``aps-dm-api`` (``dm`` for short) package [#]_
is used to access the APS databases as read-only.
The information in the PVs can be used as metadata
for inclusion in data files produced

*No information is written back to the APS
databases from this software.*

.. [#] ``dm``: https://anaconda.org/search?q=aps-dm-api


Overview
--------

#. Create the PVs in an EPICS IOC
#. Initialize PVs with beam line name and APS run cycle number
#. Set PV with the Proposal ID number
#. Set PV with the ESAF ID number
#. Retrieve information from APS databases


.. _apsbss_ioc_management:

Start EPICS IOC
---------------

The EPICS Process Variables (PVs) that support this software
are provided by an EPICS PV server (IOC).  The PVs are defined
by including the ``apsbss.db`` database file in the startup
of the IOC.  The database can be add to an existing IOC
or run as a stand-alone IOC using the ``softIoc`` application
from EPICS base.

To ensure that we create PVs with unique names, decide what
prefix to use with the EPICS database.  Such as, for APS beam
line 9-ID, you might pick: ``9id:bss:`` (making sure to end
the prefix with the customary ``:``).

Add EPICS database to existing IOC
++++++++++++++++++++++++++++++++++

To include ``apsbss.db`` in an existing IOC, copy the file
(see Downloads below) into the IOC's startup directory
(typically the directory with ``st.cmd``).  Edit the ``st.cmd``
file and a line like this just before the call to ``iocInit``::

    dbLoadRecords("apsbss.db", "P=9id:bss:")

Once the IOC is started, these PVs should be available to any
EPICS client on the local network.

Run EPICS database in softIoc from EPICS Base
+++++++++++++++++++++++++++++++++++++++++++++

For this example, we pick a unique name for this process,
(``ioc9idbss``) based on the PV prefix (``9id:bss:``).

.. sidebar:: TIP

    If you customize your copy of ``apsbss_ioc.sh``
    and pre-define the two lines::

        # change the program defaults here
        DEFAULT_SESSION_NAME=apsbss
        DEFAULT_IOC_PREFIX=ioc:bss:

    then you do not need to supply these terms as
    command-line arguments.  The usage command
    will show these the default names you provided.

**Start** the IOC using the ``apsbss_ioc.sh`` tool
(as described below), with this command::

    $ apsbss_ioc.sh start ioc9idbss 9id:bss:
    Starting ioc9idbss with IOC prefix 9id:bss:

**Stop** the IOC with this command::

    $ apsbss_ioc.sh stop ioc9idbss 9id:bss:
    ioc9idbss is not running

The IOC **restart** command, will first stop the IOC (if
it is running), then start it.

Report whether or not the IOC is running with this command::

    $ apsbss_ioc.sh status ioc9idbss 9id:bss:
    ioc9idbss is not running

To interact with the **console** of an IOC running in
a ``screen`` session::

    $ apsbss_ioc.sh console ioc9idbss 9id:bss:

To end this interaction, type ``^A`` then ``D`` which will
leave the IOC running.  Type ``exit`` to stop the IOC from
the console.

For diagnostic (or other) purposes, you can also run the IOC
without using a screen session.  This is the command::

    $ apsbss_ioc.sh run ioc9idbss 9id:bss:
    dbLoadDatabase("/home/beams1/JEMIAN/.conda/envs/bluesky_2020_5/epics/bin/linux-x86_64/../../dbd/softIoc.dbd")
    softIoc_registerRecordDeviceDriver(pdbbase)
    dbLoadRecords("apsbss.db", "P=9id:bss:")
    iocInit()
    Starting iocInit
    ############################################################################
    ## EPICS R7.0.4
    ## Rev. 2020-05-29T13:39+0000
    ############################################################################
    cas warning: Configured TCP port was unavailable.
    cas warning: Using dynamically assigned TCP port 39809,
    cas warning: but now two or more servers share the same UDP port.
    cas warning: Depending on your IP kernel this server may not be
    cas warning: reachable with UDP unicast (a host's IP in EPICS_CA_ADDR_LIST)
    iocRun: All initialization complete
    epics>

You should see the IOC shell prompt (``epics> ``).  If you type ``exit``
or otherwise close the session, the IOC will exit.


Shell Script to manage softIoc
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run a stand-alone IOC using the ``softIoc`` application
from EPICS base, use the supplied IOC management shell script
``apsbss_ioc.sh``::

	$ apsbss_ioc.sh
	Usage: apsbss_ioc.sh {start|stop|restart|status|console|run} [NAME [PREFIX]]

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

* :download:`apsbss.db <../../../apstools/beamtime/apsbss.db>`
* :download:`apsbss_ioc.sh <../../../apstools/beamtime/apsbss_ioc.sh>`

.. note:: The shell script assumes that a working ``softIoc`` application
    (from EPICS base) is in your executable ``$PATH``.  You should confirm
    this first before trying to start the IOC.

.. note:: The ``softIoc`` application is run within a ``screen``
    session so that it remains running even if you close the
    console session.  Confirm that you have the ``screen`` application
    first before trying to start the IOC.


Initialize PVs for beam line and APC run cycle
----------------------------------------------

After creating the PVs in an IOC, the next step is to
initialize them with the beam line name and the APS
run cycle name.  Both of these must match exactly
with values known in the data management (``dm``) system.

For any of these commands, you must know the EPICS
PV prefix to be used.  The examples above are for
beam line 9-ID.  The PV prefix in these examples
is ``9id:bss:``.

What beam line name to use?
+++++++++++++++++++++++++++

To learn the beam line names accepted by the system, use this command::

    $ apsbss beamlines
    1-BM-B,C       8-ID-I         15-ID-B,C,D    23-BM-B
    1-ID-B,C,E     9-BM-B,C       16-BM-B        23-ID-B
    2-BM-A,B       9-ID-B,C       16-BM-D        23-ID-D
    2-ID-D         10-BM-A,B      16-ID-B        24-ID-C
    2-ID-E         10-ID-B        16-ID-D        24-ID-E
    3-ID-B,C,D     11-BM-B        17-BM-B        26-ID-C
    4-ID-C         11-ID-B        17-ID-B        27-ID-B
    4-ID-D         11-ID-C        18-ID-D        29-ID-C,D
    5-BM-C         11-ID-D        19-BM-D        30-ID-B,C
    5-BM-D         12-BM-B        19-ID-D        31-ID-D
    5-ID-B,C,D     12-ID-B        20-BM-B        32-ID-B,C
    6-BM-A,B       12-ID-C,D      20-ID-B,C      33-BM-C
    6-ID-B,C       13-BM-C        21-ID-D        33-ID-D,E
    6-ID-D         13-BM-D        21-ID-E        34-ID-C
    7-BM-B         13-ID-C,D      21-ID-F        34-ID-E
    7-ID-B,C,D     13-ID-E        21-ID-G        35-ID-B,C,D,E
    8-BM-B         14-BM-C        22-BM-D
    8-ID-E         14-ID-B        22-ID-D

For either station at 9-ID, use ``9-ID-B,C``.


What APS run cycle to use?
+++++++++++++++++++++++++++

To learn the APS run cycle names accepted by the system, use this command::

    $ apsbss cycles
    2008-3    2011-2    2014-1    2016-3    2019-2
    2009-1    2011-3    2014-2    2017-1    2019-3
    2009-2    2012-1    2014-3    2017-2    2020-1
    2009-3    2012-2    2015-1    2017-3    2020-2
    2010-1    2012-3    2015-2    2018-1
    2010-2    2013-1    2015-3    2018-2
    2010-3    2013-2    2016-1    2018-3
    2011-1    2013-3    2016-2    2019-1

Pick the cycle of interest.  Here, we pick ``2020-2``.

Write the beam line name and cycle to the PVs
+++++++++++++++++++++++++++++++++++++++++++++

To configure ``9id:bss:`` PVs for beam line
``9-ID-B,C`` and cycle ``2020-2``,
use this command::

    $ apsbss setup 9id:bss: 9-ID-B,C 2020-2
    connected in 0.143s
    setup EPICS 9id:bss: 9-ID-B,C cycle=2020-2 sector=9

Or you could enter them into the appropriate boxes on the GUI.

.. figure:: ../resources/ui_initialized.png
   :width: 95%

   Image of ``apsbss.ui`` screen GUI in caQtDM showing PV prefix
   (``9id:bss:``), APS run cycle ``2020-2`` and beam line ``9-ID-B,C``.

What Proposal and ESAF ID numbers to use?
-----------------------------------------

Proposals are usually valid for two years.  To learn what
proposals are valid for your beam line, use this command
with your own beam line's name.  The report will provide
two tables, one for ESAFs for the current cycle and the
other for proposals
within the last two years (6 APS cycles)::

    $ apsbss current 9id:bss: 9-ID-B,C
    Current Proposal(s) on 9-ID-B,C

    ===== ====== =================== ==================== ========================================
    id    cycle  date                user(s)              title
    ===== ====== =================== ==================== ========================================
    57504 2019-3 2017-10-27 15:31:46 Zhang,Levine,Long... Towards USAXS/SAXS/WAXS Characterizat...
    55236 2019-2 2017-07-07 12:32:39 Du,Vacek,Syed,Hon... Developing 3D cryo ptychography at th...
    64629 2019-2 2019-03-01 18:35:02 Ilavsky,Okasinski    2019 National School on Neutron & X-r...
    62490 2019-1 2018-10-25 11:10:49 Ilavsky,Frith,Sun    Dissolution of nano-precipitates in m...
    ===== ====== =================== ==================== ========================================

    Current ESAF(s) on sector 9

    ====== ======== ========== ========== ==================== ========================================
    id     status   start      end        user(s)              title
    ====== ======== ========== ========== ==================== ========================================
    221805 Approved 2020-02-18 2020-12-25 Chen,Deng,Yao,Jia... Bionanoprobe commissioning
    226319 Approved 2020-05-26 2020-09-28 Ilavsky,Maxey,Kuz... Commission 9ID and USAXS
    226572 Approved 2020-06-10 2020-09-28 Sterbinsky,Heald,... 9BM Beamline Commissioning 2020-2
    226612 Approved 2020-06-10 2020-09-28 Chen,Deng,Yao,Jia... Bionanoprobe commissioning
    ====== ======== ========== ========== ==================== ========================================

Note that some of the information in the tables above has been removed for brevity.

View Proposal Information
-------------------------

To view information about a specific proposal, you
must be able to provide the proposal's ID number and
the APS run cycle name.

::

    $ apsbss proposal 64629 2019-2 9-ID-B,C
    duration: 36000
    endTime: '2019-06-25 17:00:00'
    experimenters:
    - badge: 'text_number_here'
      email: uuuuuuuuuu@email.fqdn
      firstName: Jan
      id: number_here
      instId: 3927
      institution: Argonne National Laboratory
      lastName: Ilavsky
    - badge: 'text_number_here'
      email: uuuuuuuuuu@email.fqdn
      firstName: John
      id: number_here
      instId: 3927
      institution: Argonne National Laboratory
      lastName: Okasinski
      piFlag: Y
    id: 64629
    mailInFlag: N
    proprietaryFlag: N
    startTime: '2019-06-25 07:00:00'
    submittedDate: '2019-03-01 18:35:02'
    title: 2019 National School on Neutron & X-ray Scattering Beamline Practicals - CMS
    totalShiftsRequested: 12


Get ESAF Information
--------------------

To view information about a specific ESAF, you
must be able to provide the ESAF ID number.

::

    $ apsbss esaf 226319
    description: We will commission beamline and  USAXS instrument. We will perform experiments
      with safe beamline standards and test samples (all located at beamline and used
      for this purpose routinely) to evaluate performance of beamline and instrument.
      We will perform hardware and software development as needed.
    esafId: 226319
    esafStatus: Approved
    esafTitle: Commission 9ID and USAXS
    experimentEndDate: '2020-09-28 08:00:00'
    experimentStartDate: '2020-05-26 08:00:00'
    experimentUsers:
    - badge: 'text_number_here'
      badgeNumber: 'text_number_here'
      email: uuuuuuuuuu@email.fqdn
      firstName: Jan
      lastName: Ilavsky
    - badge: 'text_number_here'
      badgeNumber: 'text_number_here'
      email: uuuuuuuuuu@email.fqdn
      firstName: Evan
      lastName: Maxey
    - badge: 'text_number_here'
      badgeNumber: 'text_number_here'
      email: uuuuuuuuuu@email.fqdn
      firstName: Ivan
      lastName: Kuzmenko
    sector: 09


Update EPICS PVs with Proposal and ESAF
---------------------------------------

To update the PVs with Proposal and Information from the APS
database, first enter the proposal and ESAF ID numbers into
the GUI (or set the ``9id:bss:proposal:id``, and respectively).
Note that for this ESAF ID, we had to change the cycle to `2019-2`.


.. figure:: ../resources/ui_id_entered.png
   :width: 95%

   Image of ``apsbss.ui`` screen GUI in caQtDM with Proposal
   and ESAF ID numbers added.

Then, use this command to retrieve the information and update
the PVs::

    $ apsbss update 9id:bss:
    update EPICS 9id:bss:
    connected in 0.105s

Here's a view of the GUI after running the update.  The
information shown in the GUI is only part of the PVs,
presented in a compact format.

.. figure:: ../resources/ui_updated.png
   :width: 95%

   Image of ``apsbss.ui`` screen GUI in caQtDM showing Proposal
   and ESAF information.

Clear the EPICS PVs
-------------------

To clear the information from the PVs, use this command::

    $ apsbss clear 9id:bss:
    clear EPICS 9id:bss:
    connected in 0.104s
    cleared in 0.011s

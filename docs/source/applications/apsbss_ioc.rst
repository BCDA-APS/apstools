.. _apsbss_ioc:

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
#. Retrieve (& update PVs) information from APS databases


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

You should see the IOC shell prompt::

    ``epics> ``

If you type ``exit`` or otherwise close the session, the IOC will exit.


Shell Script to manage softIoc
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run a stand-alone IOC using the ``softIoc`` application
from EPICS base, use the supplied IOC management shell script
``apsbss_ioc.sh``::

	$ apsbss_ioc.sh
	Usage: apsbss_ioc.sh {start|stop|restart|status|checkup|console|run} [NAME [PREFIX]]

		COMMANDS
			console   attach to IOC console if IOC is running in screen
			checkup   check that IOC is running, restart if not
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


Here's an example starter script for the IOC from APS 9-ID-C (USAXS).  
This shell script is stored as file `~/bin/ioc9idcbss.sh` with
executable permissions:

.. code-block:: bash

    #!/bin/bash

    PROCESS_NAME=ioc9idcbss
    IOC_PREFIX=9idc:bss:

    # activate the bluesky environment
    BLUESKY=/APSshare/anaconda3/Bluesky
    source ${BLUESKY}/bin/activate base

    # need shell script and EPICS database file
    APSTOOLS=$(dirname $(python -c "import apstools; print(apstools.__file__)"))

    # need EPICS base/bin/softIoc from this path
    export PATH=${PATH}:/APSshare/epics/base-7.0.3/bin/${EPICS_HOST_ARCH}

    cd "${APSTOOLS}"/beamtime
    ./apsbss_ioc.sh  "${@}"  "${PROCESS_NAME}" "${IOC_PREFIX}"



Here's an example cron task for the IOC from APS 9-ID-C (USAXS)
to keep the softIoc running (and start the IOC after system reboot):

.. code-block:: text

     */2 * * * * /home/beams/USAXS/bin/ioc9idcbss.sh checkup 2>&1 > /dev/null

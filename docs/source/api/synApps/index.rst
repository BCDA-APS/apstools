.. _synApps:

synApps Support
===============

Ophyd support for EPICS synApps modules (records and databases).

Support the default structures as provided by the
synApps template XXX IOC.

EXAMPLES::

    import apstools.synApps
    calcs = apstools.synApps.userCalcsDevice("xxx:", name="calcs")
    scans = apstools.synApps.SscanDevice("xxx:", name="scans")
    xxxstats = apstools.synApps.IocStatsDevice("xxx:", name="xxxstats")

    calc1 = calcs.calc1
    apstools.synApps.swait_setup_random_number(calc1)

    apstools.synApps.swait_setup_incrementer(calcs.calc2)

    calc1.reset()

..
   Compare this effort with a similar project:
   https://github.com/klauer/recordwhat

.. toctree::
   :maxdepth: 2
   :glob:

   _*

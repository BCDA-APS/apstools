.. _synApps:

=============================================
synApps Support: Records, Databases, ...
=============================================

Ophyd-style support for EPICS synApps structures (records and databases).

EXAMPLES::

    import apstools.synApps
    calcs = apstools.synApps.userCalcsDevice("xxx:", name="calcs")
    scans = apstools.synApps.SscanDevice("xxx:", name="scans")
    scripts = apstools.synApps.userScriptsDevice("xxx:set1:", name="scripts")
    xxxstats = apstools.synApps.IocStatsDevice("xxx:", name="xxxstats")

    calc1 = calcs.calc1
    apstools.synApps.swait_setup_random_number(calc1)

    apstools.synApps.swait_setup_incrementer(calcs.calc2)

    calc1.reset()

.. [#] synApps XXX: https://github.com/epics-modules/xxx
..
   Compare this effort with a similar project:
   https://github.com/klauer/recordwhat

Categories
----------

Support the default structures as provided by the synApps template XXX [#]_ IOC.
Also support, as needed, for structures from EPICS base.

Records
+++++++++++++++++++

.. autosummary::

    ~apstools.synApps.asyn.AsynRecord
    ~apstools.synApps.busy.BusyRecord
    ~apstools.synApps.calcout.CalcoutRecord
    ~apstools.synApps.epid.EpidRecord
    ~apstools.synApps.luascript.LuascriptRecord
    ~apstools.synApps.scalcout.ScalcoutRecord
    ~apstools.synApps.sscan.SscanRecord
    ~apstools.synApps.sseq.SseqRecord
    ~apstools.synApps.swait.SwaitRecord
    ~apstools.synApps.transform.TransformRecord

The ophyd-style Devices for these records rely on common structures:

.. autosummary::

   ~apstools.synApps._common.EpicsRecordDeviceCommonAll
   ~apstools.synApps._common.EpicsRecordInputFields
   ~apstools.synApps._common.EpicsRecordOutputFields
   ~apstools.synApps._common.EpicsRecordFloatFields

Databases
+++++++++++++++++++

.. autosummary::

   ~apstools.synApps.sseq.EditStringSequence
   ~apstools.synApps.db_2slit.Optics2Slit1D
   ~apstools.synApps.db_2slit.Optics2Slit2D_HV
   ~apstools.synApps.db_2slit.Optics2Slit2D_InbOutBotTop
   ~apstools.synApps.save_data.SaveData
   ~apstools.synApps.sscan.SscanDevice
   ~apstools.synApps.swait.UserCalcsDevice
   ~apstools.synApps.calcout.UserCalcoutDevice
   ~apstools.synApps.scalcout.UserScalcoutDevice
   ~apstools.synApps.luascript.UserScriptsDevice
   ~apstools.synApps.sseq.UserStringSequenceDevice
   ~apstools.synApps.transform.UserTransformsDevice

.. autosummary::

   ~apstools.synApps.calcout.CalcoutRecordChannel
   ~apstools.synApps.iocstats.IocStatsDevice
   ~apstools.synApps.luascript.LuascriptRecordNumberInput
   ~apstools.synApps.luascript.LuascriptRecordStringInput
   ~apstools.synApps.scalcout.ScalcoutRecordNumberChannel
   ~apstools.synApps.scalcout.ScalcoutRecordStringChannel
   ~apstools.synApps.swait.SwaitRecordChannel

Other Support
+++++++++++++++++++

.. autosummary::

   ~apstools.synApps.calcout.setup_gaussian_calcout
   ~apstools.synApps.calcout.setup_incrementer_calcout
   ~apstools.synApps.calcout.setup_lorentzian_calcout
   ~apstools.synApps.swait.setup_gaussian_swait
   ~apstools.synApps.swait.setup_incrementer_swait
   ~apstools.synApps.swait.setup_lorentzian_swait
   ~apstools.synApps.swait.setup_random_number_swait


All Submodules
--------------

.. toctree::
   :maxdepth: 2
   :glob:

   _*

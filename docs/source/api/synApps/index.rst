.. _synApps:

=======
synApps
=======

Ophyd-style support for EPICS synApps structures (records and databases).

For complete API details see the :doc:`Full API Reference <../autoapi/apstools/index>`.

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
+++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.synApps.asyn.AsynRecord`
     - EPICS asyn record support
   * - :class:`~apstools.synApps.busy.BusyRecord`
     - EPICS synApps busy record
   * - :class:`~apstools.synApps.calcout.CalcoutRecord`
     - EPICS base calcout record support
   * - :class:`~apstools.synApps.epid.EpidRecord`
     - EPICS synApps epid record support
   * - :class:`~apstools.synApps.luascript.LuascriptRecord`
     - EPICS synApps luascript record
   * - :class:`~apstools.synApps.scalcout.ScalcoutRecord`
     - EPICS synApps scalcout record support
   * - :class:`~apstools.synApps.sscan.SscanRecord`
     - EPICS synApps sscan record
   * - :class:`~apstools.synApps.sseq.SseqRecord`
     - EPICS synApps sseq record support
   * - :class:`~apstools.synApps.sub.SubRecord`
     - EPICS base sub record support
   * - :class:`~apstools.synApps.swait.SwaitRecord`
     - EPICS synApps swait record
   * - :class:`~apstools.synApps.transform.TransformRecord`
     - EPICS transform record support


The ophyd-style Devices for these records rely on common structures:

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.synApps._common.EpicsRecordDeviceCommonAll`
     - fields common to all EPICS records
   * - :class:`~apstools.synApps._common.EpicsRecordFloatFields`
     - fields common to EPICS records supporting floating point values
   * - :class:`~apstools.synApps._common.EpicsRecordInputFields`
     - fields common to EPICS input records
   * - :class:`~apstools.synApps._common.EpicsRecordOutputFields`
     - fields common to EPICS output records


Databases
+++++++++

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.synApps.sseq.EditStringSequence`
     - quickly re-arrange steps in an sseq record
   * - :class:`~apstools.synApps.iocstats.IocStatsDevice`
     - synApps IOC stats
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit1D`
     - synApps optics 2slit.db 1D support: xn, xp, size, center, sync
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit2D_HV`
     - synApps optics 2slit.db 2D support: h.xn, h.xp, v.xn, v.xp
   * - :class:`~apstools.synApps.db_2slit.Optics2Slit2D_InbOutBotTop`
     - synApps optics 2slit.db 2D support: inb, out, bot, top
   * - :class:`~apstools.synApps.save_data.SaveData`
     - synApps saveData support
   * - :class:`~apstools.synApps.sscan.SscanDevice`
     - synApps XXX IOC setup of sscan records
   * - :class:`~apstools.synApps.sub.UserAverageDevice`
     - synApps XXX IOC setup of user averaging sub records
   * - :class:`~apstools.synApps.sub.UserAverageN`
     - single instance of the user average sub record
   * - :class:`~apstools.synApps.swait.UserCalcN`
     - single instance of the userCalcN database
   * - :class:`~apstools.synApps.calcout.UserCalcoutDevice`
     - synApps XXX IOC setup of user calcouts
   * - :class:`~apstools.synApps.calcout.UserCalcoutN`
     - single instance of the userCalcoutN database
   * - :class:`~apstools.synApps.swait.UserCalcsDevice`
     - synApps XXX IOC setup of userCalcs
   * - :class:`~apstools.synApps.scalcout.UserScalcoutDevice`
     - synApps XXX IOC setup of user scalcouts
   * - :class:`~apstools.synApps.scalcout.UserScalcoutN`
     - single instance of the userStringCalcN database
   * - :class:`~apstools.synApps.luascript.UserScriptsDevice`
     - synApps XXX IOC setup of user lua scripts
   * - :class:`~apstools.synApps.sseq.UserStringSequenceDevice`
     - synApps XXX IOC setup of userStringSeqs
   * - :class:`~apstools.synApps.sseq.UserStringSequenceN`
     - single instance of the userStringSeqN database
   * - :class:`~apstools.synApps.transform.UserTransformN`
     - single instance of the userTranN database
   * - :class:`~apstools.synApps.transform.UserTransformsDevice`
     - synApps XXX IOC setup of userTransforms


Common support structures:

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.synApps.calcout.CalcoutRecordChannel`
     - channel of a calcout record: A–L
   * - :class:`~apstools.synApps._common.EpicsSynAppsRecordEnableMixin`
     - supports ``{PV}Enable`` feature from user databases
   * - :class:`~apstools.synApps.luascript.LuascriptRecordNumberInput`
     - number input of a luascript record: A–J
   * - :class:`~apstools.synApps.luascript.LuascriptRecordStringInput`
     - string input of a luascript record: AA–JJ
   * - :class:`~apstools.synApps.scalcout.ScalcoutRecordNumberChannel`
     - number channel of a scalcout record: A–L
   * - :class:`~apstools.synApps.scalcout.ScalcoutRecordStringChannel`
     - string channel of a scalcout record: AA–LL
   * - :class:`~apstools.synApps.sub.SubRecordChannel`
     - number channel of a sub record: A–L
   * - :class:`~apstools.synApps.swait.SwaitRecordChannel`
     - single channel of a swait record: A–L


Other Support
+++++++++++++

These functions configure calcout or swait records for certain algorithms.

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.synApps.calcout.setup_gaussian_calcout`
     - set up calcout record for a noisy Gaussian
   * - :func:`~apstools.synApps.swait.setup_gaussian_swait`
     - set up swait record for a noisy Gaussian
   * - :func:`~apstools.synApps.calcout.setup_incrementer_calcout`
     - set up calcout record as an incrementer
   * - :func:`~apstools.synApps.swait.setup_incrementer_swait`
     - set up swait record as an incrementer
   * - :func:`~apstools.synApps.calcout.setup_lorentzian_calcout`
     - set up calcout record for a noisy Lorentzian
   * - :func:`~apstools.synApps.swait.setup_lorentzian_swait`
     - set up swait record for a noisy Lorentzian
   * - :func:`~apstools.synApps.swait.setup_random_number_swait`
     - set up swait record to generate random numbers


All Submodules
--------------

.. toctree::
   :maxdepth: 2
   :glob:

   _*

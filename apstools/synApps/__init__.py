"""
Ophyd support for synApps configuration of EPICS records

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

Compare this effort with a similar project:
https://github.com/klauer/recordwhat
"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------


# structures
from .asyn import *
from .busy import *
from .calcout import *
from .epid import *
from .iocstats import *
from .save_data import *
from .sscan import *
from .swait import *
from .transform import *

__all__ = """
    AsynRecord
    BusyRecord
    BusyStatus
    CalcoutRecord
    CalcoutRecordChannel
    EpidRecord
    SaveData
    SscanRecord
    SscanDevice
    SwaitRecord
    SwaitRecordChannel
    TransformRecord
    UserCalcoutDevice
    UserCalcsDevice
    UserTransformsDevice
    setup_gaussian_calcout
    setup_gaussian_swait
    setup_incrementer_calcout
    setup_incrementer_swait
    setup_lorentzian_calcout
    setup_lorentzian_swait
    setup_random_number_swait
    """.split()

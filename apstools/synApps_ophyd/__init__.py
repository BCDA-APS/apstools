
"""
Ophyd support for synApps configuration of EPICS records

Support the default structures as provided by the 
synApps template XXX IOC.

EXAMPLES:;

    import apstools.synApps_ophyd
    scans = apstools.synApps_ophyd.sscanDevice("xxx:", name="scans")
    calcs = apstools.synApps_ophyd.userCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    apstools.synApps_ophyd.swait_setup_random_number(calc1)

    apstools.synApps_ophyd.swait_setup_incrementer(calcs.calc2)
    
    calc1.reset()

Compare this effort with a similar project:
https://github.com/klauer/recordwhat
"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


from .busy import *
from .save_data import *
from .sscan import *
from .swait import *

__all__ = """
    busyRecord
    BusyStatus
    SaveData
    sscanRecord  
    sscanDevice
    swaitRecord 
    userCalcsDevice
    swait_setup_random_number 
    swait_setup_gaussian
    swait_setup_lorentzian 
    swait_setup_incrementer
    """.split()

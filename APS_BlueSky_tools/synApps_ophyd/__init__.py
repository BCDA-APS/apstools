
"""
Ophyd support for synApps configuration of EPICS records

Support the default structures as provided by the 
synApps template XXX IOC.

EXAMPLES:;

    import APS_BlueSky_tools.synApps_ophyd
    scans = APS_BlueSky_tools.synApps_ophyd.sscanDevice("xxx:", name="scans")
    calcs = APS_BlueSky_tools.synApps_ophyd.userCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    APS_BlueSky_tools.synApps_ophyd.swait_setup_random_number(calc1)

    APS_BlueSky_tools.synApps_ophyd.swait_setup_incrementer(calcs.calc2)
    
    calc1.reset()

Compare this effort with a similar project:
https://github.com/klauer/recordwhat
"""


from .busy import *
from .sscan import *
from .swait import *

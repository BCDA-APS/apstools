
"""
support for EPICS

.. autosummary::
   
   ~connect_pvlist
   ~trim_string_for_EPICS
"""

__all__ = """
    connect_pvlist
    trim_string_for_EPICS
    MAX_EPICS_STRINGOUT_LENGTH
""".split()

import logging
logger = logging.getLogger(__name__)


MAX_EPICS_STRINGOUT_LENGTH = 40


def connect_pvlist(pvlist, wait=True, timeout=2, poll_interval=0.1):
    """
    given a list of EPICS PV names, return a dictionary of EpicsSignal objects

    PARAMETERS

    pvlist : list(str)
        list of EPICS PV names
    wait : bool
        should wait for EpicsSignal objects to connect, default: True
    timeout : float
        maximum time to wait for PV connections, seconds, default: 2.0
    poll_interval : float
        time to sleep between checks for PV connections, seconds, default: 0.1
    """
    obj_dict = OrderedDict()
    for item in pvlist:
        if len(item.strip()) == 0:
            continue
        pvname = item.strip()
        oname = "signal_{}".format(len(obj_dict))
        obj = ophyd.EpicsSignal(pvname, name=oname)
        obj_dict[oname] = obj

    if wait:
        times_up = time.time() + min(0, timeout)
        poll_interval = min(0.01, poll_interval)
        waiting = True
        while waiting and time.time() < times_up:
            time.sleep(poll_interval)
            waiting = False in [o.connected for o in obj_dict.values()]
        if waiting:
            n = OrderedDict()
            for k, v in obj_dict.items():
                if v.connected:
                    n[k] = v
                else:
                    print(f"Could not connect {v.pvname}")
            if len(n) == 0:
                raise RuntimeError("Could not connect any PVs in the list")
            obj_dict = n

    return obj_dict


def trim_string_for_EPICS(msg):
    """string must not be too long for EPICS PV"""
    if len(msg) > MAX_EPICS_STRINGOUT_LENGTH:
        msg = msg[:MAX_EPICS_STRINGOUT_LENGTH-1]
    return msg

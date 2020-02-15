
"""
reports and tables

.. autosummary::
   
   ~command_list_as_table
   ~device_read2table
   ~dictionary_table
   ~listruns
   ~print_RE_md
   ~print_snapshot_list
   ~show_ophyd_symbols
"""

__all__ = """
    command_list_as_table
    device_read2table
    dictionary_table
    listruns
    print_RE_md
    print_snapshot_list
    show_ophyd_symbols
""".split()

import logging
logger = logging.getLogger(__name__)

import datetime
import pyRestTable
from ..filewriters import _rebuild_scan_command
from .shell import ipython_shell_namespace


def command_list_as_table(commands, show_raw=False):
    """
    format a command list as a pyRestTable.Table object
    """
    tbl = pyRestTable.Table()
    tbl.addLabel("line #")
    tbl.addLabel("action")
    tbl.addLabel("parameters")
    if show_raw:        # only the developer might use this
        tbl.addLabel("raw input")
    for command in commands:
        action, args, line_number, raw_command = command
        row = [line_number, action, ", ".join(map(str, args))]
        if show_raw:
            row.append(str(raw_command))
        tbl.addRow(row)
    return tbl


def device_read2table(device, show_ancient=True, use_datetime=True, printing=True):
    """
    read an ophyd device and return a pyRestTable Table
    
    Include an option to suppress ancient values identified
    by timestamp from 1989.  These are values only defined in 
    the original .db file.
    """
    table = pyRestTable.Table()
    table.labels = "name value timestamp".split()
    ANCIENT_YEAR = 1989
    for k, rec in device.read().items():
        value = rec["value"]
        ts = rec["timestamp"]
        dt = datetime.datetime.fromtimestamp(ts)
        if dt.year > ANCIENT_YEAR or show_ancient:
            if use_datetime:
                ts = dt
            table.addRow((k, value, ts))

    if printing:
        print(table)

    return table


def dictionary_table(dictionary, **kwargs):
    """
    return a text table from ``dictionary``
    
    PARAMETERS
    
    dictionary : dict
        Python dictionary

    Note:  Keyword arguments parameters 
    are kept for compatibility with previous
    versions of apstools.  They are ignored now.
    
    RETURNS

    table : object or `None`
        ``pyRestTable.Table()`` object (multiline text table) 
        or ``None`` if dictionary has no contents
    
    EXAMPLE::

        In [8]: RE.md                                                                                                               
        Out[8]: {'login_id': 'jemian:wow.aps.anl.gov', 'beamline_id': 'developer', 'proposal_id': None, 'pid': 19072, 'scan_id': 10, 'version': {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}}

        In [9]: print(dictionary_table(RE.md))                                                                                      
        =========== =============================================================================
        key         value                                                                        
        =========== =============================================================================
        beamline_id developer                                                                    
        login_id    jemian:wow.aps.anl.gov                                                       
        pid         19072                                                                        
        proposal_id None                                                                         
        scan_id     10                                                                           
        version     {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}
        =========== =============================================================================

    """
    if len(dictionary) == 0:
        return
    t = pyRestTable.Table()
    t.addLabel("key")
    t.addLabel("value")
    for k, v in sorted(dictionary.items()):
        t.addRow((k, str(v)))
    return t


def listruns(
        num=20, keys=[], printing=True, 
        show_command=True, db=None):
    """
    make a table of the most recent runs (scans)

    PARAMETERS
    
    num : int
        Make the table include the ``num`` most recent runs.
        (default: ``20``)
    keys : [str]
        Include these additional keys from the start document.
        (default: ``[]``)
    printing : bool
        If True, print the table to stdout
        (default: ``True``)
    show_command : bool
        If True, show the (reconstructed) full command,
        but truncate it to no more than 40 characters)
        (note: This command is reconstructed from keys in the start
        document so it will not be exactly as the user typed.)
        (default: ``True``)
    db : object
        Instance of ``databroker.Broker()``
        (default: ``db`` from the IPython shell)

    RETURNS
    
    object:
        Instance of ``pyRestTable.Table()``
    
    EXAMPLE::

        In [2]: from apstools import utils as APS_utils
        
        In [3]: APS_utils.listruns(num=5, keys=["proposal_id","pid"])
        ========= ======================= ======= ======= ======================================== =========== ===
        short_uid date/time               exit    scan_id command                                  proposal_id pid
        ========= ======================= ======= ======= ======================================== =========== ===
        5f2bc62   2019-03-10 22:27:57.803 success 3       fly()
        ef7777d   2019-03-10 22:27:12.449 success 2       fly()
        8048ea1   2019-03-10 22:25:01.663 success 1       scan(detectors=['calcs_calc2_val'],  ...
        83ad06d   2019-03-10 22:19:14.352 success 4       fly()
        b713d46   2019-03-10 22:13:26.481 success 3       fly()
        ========= ======================= ======= ======= ======================================== =========== ===

    *new in apstools release 1.1.10*
    """
    db = db or ipython_shell_namespace()["db"]
    
    if show_command:
        labels = "scan_id  command".split() + keys
    else:
        labels = "scan_id  plan_name".split() + keys
    
    table = pyRestTable.Table()
    table.labels = "short_uid  date/time  exit".split() + labels
    
    for h in db[-abs(num):]:
        dt = datetime.datetime.fromtimestamp(h.start['time'])
        row = [
            h.start["uid"][:7],
            dt.isoformat(sep=" ", timespec="milliseconds"),
            h.stop.get("exit_status", "")
            ]
        for k in labels:
            if k == "command":
                command = _rebuild_scan_command(h.start)
                command = command[command.find(" "):].strip()
                maxlen = 40
                if len(command) > maxlen:
                    suffix = " ..."
                    command = command[:maxlen-len(suffix)] + suffix
                row.append(command)
            else:
                row.append(h.start.get(k, ""))
        table.addRow(row)
    
    if printing:
        print(table)
    return table


def print_RE_md(dictionary=None, fmt="simple", printing=True):
    """
    custom print the RunEngine metadata in a table
    
    PARAMETERS
    
    dictionary : dict
        Python dictionary

    EXAMPLE::

        In [4]: print_RE_md()                                                                                                       
        RunEngine metadata dictionary:
        ======================== ===================================
        key                      value                              
        ======================== ===================================
        EPICS_CA_MAX_ARRAY_BYTES 1280000                            
        EPICS_HOST_ARCH          linux-x86_64                       
        beamline_id              APS USAXS 9-ID-C                   
        login_id                 usaxs:usaxscontrol.xray.aps.anl.gov
        pid                      67933                              
        proposal_id              testing Bluesky installation       
        scan_id                  0                                  
        versions                 ======== =====                     
                                 key      value                     
                                 ======== =====                     
                                 apstools 1.1.3                     
                                 bluesky  1.5.2                     
                                 epics    3.3.1                     
                                 ophyd    1.3.3                     
                                 ======== =====                     
        ======================== ===================================
    
    """
    # override noting that fmt="markdown" will not display correctly
    fmt="simple"

    dictionary = dictionary or ipython_shell_namespace()["RE"].md
    md = dict(dictionary)   # copy of input for editing
    v = dictionary_table(md["versions"])   # sub-table
    md["versions"] = v.reST(fmt=fmt).rstrip()
    table = dictionary_table(md)
    if printing:
        print("RunEngine metadata dictionary:")
        print(table.reST(fmt=fmt))
    return table


def print_snapshot_list(db, printing=True, **search_criteria):
    """
    print (stdout) a list of all snapshots in the databroker
    
    USAGE::
    
        print_snapshot_list(db, )
        print_snapshot_list(db, purpose="this is an example")
        print_snapshot_list(db, since="2018-12-21", until="2019")
    
    EXAMPLE::
    
        In [16]: from apstools.utils import print_snapshot_list
            ...: from apstools.callbacks import SnapshotReport 
            ...: print_snapshot_list(db, since="2018-12-21", until="2019") 
            ...:                                                                                                                            
        = ======== ========================== ==================
        # uid      date/time                  purpose           
        = ======== ========================== ==================
        0 d7831dae 2018-12-21 11:39:52.956904 this is an example
        1 5049029d 2018-12-21 11:39:30.062463 this is an example
        2 588e0149 2018-12-21 11:38:43.153055 this is an example
        = ======== ========================== ==================
        
        In [17]: SnapshotReport().print_report(db["5049029d"])
        
        ========================================
        snapshot: 2018-12-21 11:39:30.062463
        ========================================
        
        example: example 2
        hints: {}
        iso8601: 2018-12-21 11:39:30.062463
        look: can snapshot text and arrays too
        note: no commas in metadata
        plan_description: archive snapshot of ophyd Signals (usually EPICS PVs)
        plan_name: snapshot
        plan_type: generator
        purpose: this is an example
        scan_id: 1
        software_versions: {
            'python': 
                '''3.6.2 |Continuum Analytics, Inc.| (default, Jul 20 2017, 13:51:32)
                [GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]''', 
            'PyEpics': '3.3.1', 
            'bluesky': '1.4.1', 
            'ophyd': '1.3.0', 
            'databroker': '0.11.3', 
            'apstools': '0.0.38'
            }
        time: 1545413970.063167
        uid: 5049029d-075c-453c-96d2-55431273852b
        
        ========================== ====== ================ ===================
        timestamp                  source name             value              
        ========================== ====== ================ ===================
        2018-12-20 18:24:34.220028 PV     compress         [0.1, 0.2, 0.3]    
        2018-12-13 14:49:53.121188 PV     gov:HOSTNAME     otz.aps.anl.gov    
        2018-12-21 11:39:24.268148 PV     gov:IOC_CPU_LOAD 0.22522317161410768
        2018-12-21 11:39:24.268151 PV     gov:SYS_CPU_LOAD 9.109026666525944  
        2018-12-21 11:39:30.017643 PV     gov:iso8601      2018-12-21T11:39:30
        2018-12-13 14:49:53.135016 PV     otz:HOSTNAME     otz.aps.anl.gov    
        2018-12-21 11:39:27.705304 PV     otz:IOC_CPU_LOAD 0.1251210270549924 
        2018-12-21 11:39:27.705301 PV     otz:SYS_CPU_LOAD 11.611234438304471 
        2018-12-21 11:39:30.030321 PV     otz:iso8601      2018-12-21T11:39:30
        ========================== ====== ================ ===================
        
        exit_status: success
        num_events: {'primary': 1}
        run_start: 5049029d-075c-453c-96d2-55431273852b
        time: 1545413970.102147
        uid: 6c1b2100-1ef6-404d-943e-405da9ada882
       
    """
    t = pyRestTable.Table()
    t.addLabel("#")
    t.addLabel("uid")
    t.addLabel("date/time")
    t.addLabel("#items")
    t.addLabel("purpose")
    search_criteria["plan_name"] = "snapshot"
    for i, h in enumerate(db(**search_criteria)):
        uid = h.start["uid"].split("-")[0]
        n = len(list(h.start.keys()))
        t.addRow((i, uid, h.start["iso8601"], n, h.start["purpose"]))
    if printing:
        print(t)
    return t


def show_ophyd_symbols(show_pv=True, printing=True, verbose=False, symbols=None):
    """
    show all the ophyd Signal and Device objects defined as globals
    
    PARAMETERS
    
    show_pv: bool
        If True, also show relevant EPICS PV, if available.
        (default: True)
    printing: bool
        If True, print table to stdout.
        (default: True)
    verbose: bool
        If True, also show ``str(obj``.
        (default: False)
    symbols: dict
        If None, use global symbol table.
        If not None, use provided dictionary. 
        (default: `globals()`)
    
    RETURNS
    
    object:
        Instance of `pyRestTable.Table()``

    EXAMPLE::
    
        In [1]: show_ophyd_symbols()                                                                                                                                                                           
        ======== ================================ =============
        name     ophyd structure                  EPICS PV     
        ======== ================================ =============
        adsimdet MySingleTriggerSimDetector       vm7SIM1:     
        m1       EpicsMotor                       vm7:m1       
        m2       EpicsMotor                       vm7:m2       
        m3       EpicsMotor                       vm7:m3       
        m4       EpicsMotor                       vm7:m4       
        m5       EpicsMotor                       vm7:m5       
        m6       EpicsMotor                       vm7:m6       
        m7       EpicsMotor                       vm7:m7       
        m8       EpicsMotor                       vm7:m8       
        noisy    EpicsSignalRO                    vm7:userCalc1
        scaler   ScalerCH                         vm7:scaler1  
        shutter  SimulatedApsPssShutterWithStatus              
        ======== ================================ =============
        
        Out[1]: <pyRestTable.rest_table.Table at 0x7fa4398c7cf8>
        
        In [2]:    

    *new in apstools release 1.1.8*
    """
    table = pyRestTable.Table()
    table.labels = ["name", "ophyd structure"]
    if show_pv:
        table.addLabel("EPICS PV")
    if verbose:
        table.addLabel("object representation")
    table.addLabel("label(s)")
    if symbols is None:
        # the default choice
        g = ipython_shell_namespace()
        if len(g) == 0:
            # ultimate fallback
            g = globals()
    else:
        g = symbols
    for k, v in sorted(g.items()):
        if isinstance(v, (ophyd.Signal, ophyd.Device)):
            row = [k, v.__class__.__name__]
            if show_pv:
                if hasattr(v, "pvname"):
                    row.append(v.pvname)
                elif hasattr(v, "prefix"):
                    row.append(v.prefix)
                else:
                    row.append("")
            if verbose:
                row.append(str(v))
            row.append(' '.join(v._ophyd_labels_))
            table.addRow(row)
    if printing:
        print(table)
    return table

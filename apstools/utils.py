"""
Various utilities

.. autosummary::
   
   ~cleanupText
   ~command_list_as_table
   ~connect_pvlist
   ~device_read2table
   ~dictionary_table
   ~EmailNotifications
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ExcelReadError
   ~full_dotted_name
   ~ipython_profile_name
   ~itemizer
   ~json_export
   ~json_import
   ~listobjects
   ~listruns
   ~object_explorer
   ~pairwise
   ~plot_prune_fifo
   ~print_snapshot_list
   ~print_RE_md
   ~redefine_motor_position
   ~replay
   ~run_in_thread
   ~safe_ophyd_name
   ~show_ophyd_symbols
   ~split_quoted_line
   ~text_encode
   ~to_unicode_or_bust
   ~trim_string_for_EPICS
   ~unix

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2020, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky import plan_stubs as bps
from collections import OrderedDict
import databroker
import datetime
from email.mime.text import MIMEText
from event_model import NumpyEncoder
import json
import logging
import math
import ophyd
import os
import pandas
import pyRestTable
import re
import smtplib
import subprocess
import sys
import threading
import time
import warnings
import xlrd
import zipfile

from .filewriters import _rebuild_scan_command


logger = logging.getLogger(__name__)

MAX_EPICS_STRINGOUT_LENGTH = 40


class ExcelReadError(xlrd.XLRDError): ...


def cleanupText(text):
    """
    convert text so it can be used as a dictionary key

    Given some input text string, return a clean version
    remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    """
    pattern = "[a-zA-Z0-9_]"

    def mapper(c):
        if re.match(pattern, c) is not None:
            return c
        return "_"

    return "".join([mapper(c) for c in text])


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


def full_dotted_name(obj):
    """
    Return the full dotted name

    The ``.dotted_name`` property does not include the 
    name of the root object.  This routine adds that.

    see: https://github.com/bluesky/ophyd/pull/797
    """
    names = []
    while obj.parent is not None:
        names.append(obj.attr_name)
        obj = obj.parent
    names.append(obj.name)
    return '.'.join(names[::-1])


def _get_named_child(obj, nm):
    """
    return named child of ``obj`` or None
    """
    try:
        child = getattr(obj, nm)
        return child
    except TimeoutError:
        logger.debug(f"timeout: {obj.name}_{nm}")
        return "TIMEOUT"


def _get_pv(obj):
    """
    returns PV name, prefix of None from ophyd object
    """
    if hasattr(obj, "pvname"):
        return obj.pvname
    elif hasattr(obj, "prefix"):
        return obj.prefix


def itemizer(fmt, items):
    """format a list of items"""
    return [fmt % k for k in items]


def listruns(
        num=20, keys=[], printing=True,
        show_command=True, db=None,
        exit_status=None,
        **db_search_terms):
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
    db_search_terms : dict
        Any additional keyword arguments will be passed to
        the databroker to refine the search for matching runs.

    RETURNS

    object:
        Instance of ``pyRestTable.Table()``

    EXAMPLE::

        In [2]: from apstools import utils as APS_utils

        In [3]: APS_utils.listruns(num=5, keys=["proposal_id","pid"])
        ========= ========================== ======= ======= ======================================== =========== ===
        short_uid date/time                  exit    scan_id command                                  proposal_id pid
        ========= ========================== ======= ======= ======================================== =========== ===
        5f2bc62   2019-03-10 22:27:57.803193 success 3       fly()
        ef7777d   2019-03-10 22:27:12.449852 success 2       fly()
        8048ea1   2019-03-10 22:25:01.663526 success 1       scan(detectors=['calcs_calc2_val'],  ...
        83ad06d   2019-03-10 22:19:14.352157 success 4       fly()
        b713d46   2019-03-10 22:13:26.481118 success 3       fly()
        ========= ========================== ======= ======= ======================================== =========== ===

        In [100]: listruns(keys=["file_name",], since="2020-02-06", until="2020-02-07", num=10, plan_name="lambda_test", exit_status="success")
            ...:
        ========= ========================== ======= ======= ======================================== ==============================
        short_uid date/time                  exit    scan_id command                                  file_name
        ========= ========================== ======= ======= ======================================== ==============================
        efab384   2020-02-06 11:21:36.129510 success 5081    lambda_test(detector_name=lambdadet, ... C042_Latex_Lq0_001
        394a20a   2020-02-06 10:32:07.525558 success 5072    lambda_test(detector_name=lambdadet, ... B041_Aerogel_Translate_Lq0_001
        aeea69b   2020-02-06 10:31:27.522871 success 5071    lambda_test(detector_name=lambdadet, ... B040_Aerogel_Translate_Lq0_001
        b39813a   2020-02-06 10:27:16.267097 success 5069    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_005
        0651cb6   2020-02-06 10:27:02.070575 success 5068    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_004
        63897f8   2020-02-06 10:26:47.770677 success 5067    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_003
        188d31a   2020-02-06 10:26:33.230039 success 5066    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_002
        9907451   2020-02-06 10:26:19.048433 success 5065    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_001
        ========= ========================== ======= ======= ======================================== ==============================

        Out[100]: <pyRestTable.rest_table.Table at 0x7f004e4d4898>

    *new in apstools release 1.1.10*
    """
    db = db or ipython_shell_namespace()["db"]

    if show_command:
        labels = "scan_id  command".split() + keys
    else:
        labels = "scan_id  plan_name".split() + keys

    table = pyRestTable.Table()
    table.labels = "short_uid   date/time  exit".split() + labels

    if len(db_search_terms) > 0:
        # TODO: Can this be more efficient to extract `num` runs?
        runs = list(db(**db_search_terms))[-abs(num):]
    else:
        runs = db[-abs(num):]
    for h in runs:
        if (
                exit_status is not None 
                and 
                h.stop.get("exit_status") != exit_status):
            continue
        row = [
            h.start["uid"][:7],
            datetime.datetime.fromtimestamp(h.start['time']),
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


def _ophyd_structure_walker(obj):
    """
    walk the structure of the ophyd obj

    RETURNS

    list of ophyd objects that are children of ``obj``
    """
    # import pdb; pdb.set_trace()
    if isinstance(obj, ophyd.signal.EpicsSignalBase):
        return [obj]
    elif isinstance(obj, ophyd.Device):
        items = []
        for nm in obj.component_names:
            child = _get_named_child(obj, nm)
            if child in (None, "TIMEOUT"):
                continue
            result = _ophyd_structure_walker(child)
            if result is not None:
                items.extend(result)
        return items


def object_explorer(obj, sortby=None, fmt='simple', printing=True):
    """
    print the contents of obj
    """
    t = pyRestTable.Table()
    t.addLabel("name")
    t.addLabel("PV reference")
    t.addLabel("value")
    items = _ophyd_structure_walker(obj)
    logger.debug(f"number of items: {len(items)}")

    def sorter(obj):
        if sortby is None:
            key = obj.dotted_name
        elif str(sortby).lower() == "pv":
            key = _get_pv(obj) or "--"
        else:
            raise ValueError(
                "sortby should be None or 'PV'"
                f" found sortby='{sortby}'"
                )
        return key

    for item in sorted(items, key=sorter):
        t.addRow((item.dotted_name, _get_pv(item), item.get()))
    if printing:
        print(t.reST(fmt=fmt))
    return t


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


def pairwise(iterable):
    """
    break a list (or other iterable) into pairs
    
    ::
    
		s -> (s0, s1), (s2, s3), (s4, s5), ...
		
		In [71]: for item in pairwise("a b c d e fg".split()): 
			...:     print(item) 
			...:                                                                                                                         
		('a', 'b')
		('c', 'd')
		('e', 'fg')
  
    """
    a = iter(iterable)
    return zip(a, a)


def replay(headers, callback=None, sort=True):
    """
    replay the document stream from one (or more) scans (headers)
    
    PARAMETERS
    
    headers: scan or [scan]
        Scan(s) to be replayed through callback.
        A *scan* is an instance of a Bluesky `databroker.Header`.
        see: https://nsls-ii.github.io/databroker/api.html?highlight=header#header-api
    
    callback: scan or [scan]
        The Bluesky callback to handle the stream of documents from a scan.
        If `None`, then use the `bec` (BestEffortCallback) from the IPython shell.
        (default:``None``)
    
    sort: bool
        Sort the headers chronologically if True.
        (default:``True``)

    *new in apstools release 1.1.11*
    """
    callback = callback or ipython_shell_namespace().get(
        "bec",                  # get from IPython shell
        BestEffortCallback(),   # make one, if we must
        )
    _headers = headers   # do not mutate the input arg
    if isinstance(_headers, databroker.Header):
        _headers = [_headers]

    def increasing_time_sorter(run):
        return run.start["time"]

    def decreasing_time_sorter(run):
        "default for databroker v0 results"
        return -run.start["time"]

    sorter = {
        True: increasing_time_sorter, 
        False: decreasing_time_sorter
        }[sort]

    for h in sorted(_headers, key=sorter):
        if not isinstance(h, databroker.Header):
            raise TypeError(
                f"Must be a databroker Header: received: {type(h)}: |{h}|"
            )
        cmd = _rebuild_scan_command(h.start)
        logger.debug(f"{cmd}")
        
        # at last, this is where the real action happens
        for k, doc in h.documents():    # get the stream
            callback(k, doc)            # play it through the callback


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def safe_ophyd_name(text):
    """
    make text safe to be used as an ophyd object name

    Given some input text string, return a clean version.
    Remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    
    The "sanitized" name fits this regular expression::
    
        [A-Za-z_][\w_]*

    Also can be used for safe HDF5 and NeXus names.
    """
    replacement = '_'
    noncompliance = '[^\w_]'
    
    # replace ALL non-compliances with '_'
    safer = replacement.join(re.split(noncompliance, text))

    # can't start with a digit
    if safer[0].isdigit():
        safer = replacement + safer
    return safer


def listobjects(show_pv=True, printing=True, verbose=False, symbols=None):
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
    
        In [1]: listobjects()                                                                                                                                                                           
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


def show_ophyd_symbols(show_pv=True, 
                       printing=True, 
                       verbose=False, 
                       symbols=None):
    warnings.warn(
        "DEPRECATED: show_ophyd_symbols() will be removed" 
        " in a future release.  Use listobjects() instead."
        )
    listobjects(
        show_pv=show_pv, 
        printing=printing, 
        verbose=verbose, 
        symbols=symbols)


def split_quoted_line(line):
    """
    splits a line into words some of which might be quoted

    TESTS::

        FlyScan 0   0   0   blank
        FlyScan 5   2   0   "empty container"
        FlyScan 5   12   0   "even longer name"
        SAXS 0 0 0 blank
        SAXS 0 0 0 "blank"

    RESULTS::

        ['FlyScan', '0', '0', '0', 'blank']
        ['FlyScan', '5', '2', '0', 'empty container']
        ['FlyScan', '5', '12', '0', 'even longer name']
        ['SAXS', '0', '0', '0', 'blank']
        ['SAXS', '0', '0', '0', 'blank']

    """
    parts = []

    # look for open and close quoted parts and combine them
    quoted = False
    multi = None
    for p in line.split():
        if not quoted and p.startswith('"'):   # begin quoted text
            quoted = True
            multi = ""

        if quoted:
            if len(multi) > 0:
                multi += " "
            multi += p
            if p.endswith('"'):     # end quoted text
                quoted = False

        if not quoted:
            if multi is not None:
                parts.append(multi[1:-1])   # remove enclosing quotes
                multi = None
            else:
                parts.append(p)

    return parts


def text_encode(source):
    """encode ``source`` using the default codepoint"""
    return source.encode(errors='ignore')


def to_unicode_or_bust(obj, encoding='utf-8'):
    """from: http://farmdev.com/talks/unicode/"""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


def trim_string_for_EPICS(msg):
    """string must not be too long for EPICS PV"""
    if len(msg) > MAX_EPICS_STRINGOUT_LENGTH:
        msg = msg[:MAX_EPICS_STRINGOUT_LENGTH-1]
    return msg


def unix(command, raises=True):
    """
    run a UNIX command, returns (stdout, stderr)

    PARAMETERS
    
    command: str
        UNIX command to be executed
    raises: bool
        If `True`, will raise exceptions as needed,
        default: `True`
    """
    if sys.platform not in ("linux", "linux2"):
        emsg = f"Cannot call unix() when OS={sys.platform}"
        raise RuntimeError(emsg)

    process = subprocess.Popen(
        command, 
        shell=True,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        )

    stdout, stderr = process.communicate()

    if len(stderr) > 0:
        emsg = f"unix({command}) returned error:\n{stderr}"
        logger.error(emsg)
        if raises:
            raise RuntimeError(emsg)

    return stdout, stderr


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


class EmailNotifications(object):
    """
    send email notifications when requested
    
    use default OS mail utility (so no credentials needed)
    """
    
    def __init__(self, sender=None):
        self.addresses = []
        self.notify_on_feedback = True
        self.sender = sender or "nobody@localhost"
        self.smtp_host = "localhost"
    
    def add_addresses(self, *args):
        for address in args:
            self.addresses.append(address)

    @run_in_thread
    def send(self, subject, message):
        """send ``message`` to all addresses"""
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ",".join(self.addresses)
        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(self.sender, self.addresses, msg.as_string())
        s.quit()


class ExcelDatabaseFileBase(object):
    """
    base class: read-only support for Excel files, treat them like databases
    
    Use this class when creating new, specific spreadsheet support.
    
    EXAMPLE
    
    Show how to read an Excel file where one of the columns
    contains a unique key.  This allows for random access to
    each row of data by use of the *key*.
    
    ::

        class ExhibitorsDB(ExcelDatabaseFileBase):
            '''
            content for Exhibitors, vendors, and Sponsors from the Excel file
            '''
            EXCEL_FILE = os.path.join("resources", "exhibitors.xlsx")
            LABELS_ROW = 2
        
            def handle_single_entry(self, entry):
                '''any special handling for a row from the Excel file'''
                pass
        
            def handleExcelRowEntry(self, entry):
                '''identify the unique key for this entry (row of the Excel file)'''
                key = entry["Name"]
                self.db[key] = entry

    """
    
    EXCEL_FILE = None       # subclass MUST define
    # EXCEL_FILE = os.path.join("abstracts", "index of abstracts.xlsx")
    LABELS_ROW = 3          # labels are on line LABELS_ROW+1 in the Excel file

    def __init__(self, ignore_extra=True):
        self.db = OrderedDict()
        self.data_labels = None
        if self.EXCEL_FILE is None:
            raise ValueError("subclass must define EXCEL_FILE")
        self.fname = os.path.join(os.getcwd(), self.EXCEL_FILE)
        
        self.sheet_name = 0

        self.parse(ignore_extra=ignore_extra)
        
    def handle_single_entry(self, entry):       # subclass MUST override
        raise NotImplementedError("subclass must override handle_single_entry() method")

    def handleExcelRowEntry(self, entry):       # subclass MUST override
        raise NotImplementedError("subclass must override handleExcelRowEntry() method")

    def parse(self, labels_row_num=None, data_start_row_num=None, ignore_extra=True):
        labels_row_num = labels_row_num or self.LABELS_ROW
        try:
            if ignore_extra:
                # ignore data outside of table in spreadsheet file
                nrows, ncols = self.getTableBoundaries(labels_row_num)
                xl = pandas.read_excel(
                    self.fname, 
                    sheet_name=self.sheet_name, 
                    skiprows=labels_row_num,
                    usecols=range(ncols),
                    nrows=nrows,
                    )
            else:
                xl = pandas.read_excel(
                    self.fname, 
                    sheet_name=self.sheet_name, 
                    header=None,
                    )
        except xlrd.XLRDError as exc:
            raise ExcelReadError(exc)
        self.data_labels = list(map(str, xl.columns.values))
        # unused: data_start_row_num = data_start_row_num or labels_row_num+1
        for row_data in xl.values:
            entry = OrderedDict()
            for _col, label in enumerate(self.data_labels):
                entry[label] = self._getExcelColumnValue(row_data, _col)
                self.handle_single_entry(entry)
            self.handleExcelRowEntry(entry)

    def _getExcelColumnValue(self, row_data, col):
        v = row_data[col]
        if self._isExcel_nan(v):
            v = None
        else:
            v = to_unicode_or_bust(v)
            if isinstance(v, str):
                v = v.strip()
        return v
    
    def _isExcel_nan(self, value):
        if not isinstance(value, float):
            return False
        return math.isnan(value)

    def getTableBoundaries(self, labels_row_num=None):
        """
        identify how many rows and columns are in the Excel spreadsheet table
        """
        labels_row_num = labels_row_num or self.LABELS_ROW
        xl = pandas.read_excel(self.fname, sheet_name=self.sheet_name, skiprows=labels_row_num)
    
        ncols = len(xl.columns)
        for i, k in enumerate(xl.columns):
            if k.startswith(f"Unnamed: {i}"):
                # TODO: verify all values under this label are NaN
                ncols = i
                break
    
        nrows = len(xl.values)
        for j, r in enumerate(xl.values):
            r = r[:ncols]
            if False not in [self._isExcel_nan(value) for value in r]:
                nrows = j
                break
        
        return nrows, ncols


class ExcelDatabaseFileGeneric(ExcelDatabaseFileBase):
    """
    Generic (read-only) handling of Excel spreadsheet-as-database
    
    .. index:: Excel scan, scan; Excel
    
    .. note:: This is the class to use when reading Excel spreadsheets.

    In the spreadsheet, the first sheet should contain the table to be used.
    By default (see keyword parameter `labels_row`), the table should start
    in cell A4.  The column labels are given in row 4.  A blank column 
    should appear to the right of the table (see keyword parameter `ignore_extra`).
    The column labels will describe the action and its parameters.  Additional
    columns may be added for metadata or other purposes.
    The rows below the column labels should contain actions and parameters
    for those actions, one action per row.
    To make a comment, place a `#` in the action column.  A comment
    should be ignored by the bluesky plan that reads this table.
    The table will end with a row of empty cells.
    
    While it's a good idea to put the `action` column first, that is not necessary.
    It is not even necessary to name the column `action`.
    You can re-arrange the order of the columns and change their names 
    **as long as** the column names match
    what text strings your Python code expects to find.
    
    A future upgrade [#]_ will allow the table boundaries to be named by Excel when
    using Excel's `Format as Table` [#]_ feature.
    For now, leave a blank row and column at the bottom and right edges of the table.
    
    .. [#] https://github.com/BCDA-APS/apstools/issues/122
    .. [#] Excel's `Format as Table`: https://support.office.com/en-us/article/Format-an-Excel-table-6789619F-C889-495C-99C2-2F971C0E2370

    PARAMETERS

    filename : str
        name (absolute or relative) of Excel spreadsheet file
    labels_row : int
        Row (zero-based numbering) of Excel file with column labels,
        default: `3` (Excel row 4)
    ignore_extra : bool
        When True, ignore any cells outside of the table,
        default: `True`
        
        Note that when True, a row of cells *within* the table will
        be recognized as the end of the table, even if there are
        actions in following rows.  To force an empty row, use
        a comment symbol `#` (actually, any non-empty content will work).
        
        When False, cells with other information (in Sheet 1) will be made available,
        sometimes with unpredictable results.
    
    EXAMPLE
    
    See section :ref:`example_run_command_file` for more examples.

    (See also :ref:`example screen shot <excel_plan_spreadsheet_screen>`.)
    Table (on Sheet 1) begins on row 4 in first column::
    
        1  |  some text here, maybe a title
        2  |  (could have content here)
        3  |  (or even more content here)
        4  |  action  | sx   | sy   | sample     | comments          |  | <-- leave empty column
        5  |  close   |      |                   | close the shutter |  |
        6  |  image   | 0    | 0    | dark       | dark image        |  |
        7  |  open    |      |      |            | open the shutter  |  |
        8  |  image   | 0    | 0    | flat       | flat field image  |  |
        9  |  image   | 5.1  | -3.2 | 4140 steel | heat 9172634      |  |
        10 |  scan    | 5.1  | -3.2 | 4140 steel | heat 9172634      |  |
        11 |  scan    | 0    | 0    | blank      |                   |  |
        12 |  
        13 |  ^^^ leave empty row ^^^
        14 | (could have content here)


    
    Example python code to read this spreadsheet::
    
        from apstools.utils import ExcelDatabaseFileGeneric, cleanupText
        
        def myExcelPlan(xl_file, md={}):
            excel_file = os.path.abspath(xl_file)
            xl = ExcelDatabaseFileGeneric(excel_file)
            for i, row in xl.db.values():
                # prepare the metadata
                _md = {cleanupText(k): v for k, v in row.items()}
                _md["xl_file"] = xl_file
                _md["excel_row_number"] = i+1
                _md.update(md) # overlay with user-supplied metadata

                # determine what action to take
                action = row["action"].lower()
                if action == "open":
                    yield from bps.mv(shutter, "open")
                elif action == "close":
                    yield from bps.mv(shutter, "close")
                elif action == "image":
                    # your code to take an image, given **row as parameters
                    yield from my_image(**row, md=_md)
                elif action == "scan":
                    # your code to make a scan, given **row as parameters
                    yield from my_scan(**row, md=_md)
                else:
                    print(f"no handling for row {i+1}: action={action}")
    
        # execute this plan through the RunEngine
        RE(myExcelPlan("spreadsheet.xlsx", md=dict(purpose="apstools demo"))
        
    """
    
    def __init__(self, filename, labels_row=3, ignore_extra=True):
        self._index_ = 0
        self.EXCEL_FILE = self.EXCEL_FILE or filename
        self.LABELS_ROW = labels_row
        ExcelDatabaseFileBase.__init__(self, ignore_extra=ignore_extra)

    def handle_single_entry(self, entry):
        pass

    def handleExcelRowEntry(self, entry):
        """use row number as the unique key"""
        key = str(self._index_)
        self.db[key] = entry
        self._index_ += 1


def ipython_profile_name():
    """
    return the name of the current ipython profile or `None`
    
    Example (add to default RunEngine metadata)::

        RE.md['ipython_profile'] = str(ipython_profile_name())
        print("using profile: " + RE.md['ipython_profile'])

    """
    from IPython import get_ipython
    return get_ipython().profile


def ipython_shell_namespace():
    """
    get the IPython shell's namespace dictionary (or empty if not found)
    """
    try:
        from IPython import get_ipython
        ns = get_ipython().user_ns
    except AttributeError as _exc:
        ns = {}
    return ns


def plot_prune_fifo(bec, n, y, x):
    """
    find the plot with axes x and y and replot with only the last *n* lines

    Note: this is not a bluesky plan.  Call it as normal Python function.

    EXAMPLE::

        plot_prune_fifo(bec, 1, noisy, m1)

    PARAMETERS
    
    bec : object
        instance of BestEffortCallback
    
    n : int
        number of plots to keep
    
    y : object
        instance of ophyd.Signal (or subclass), 
        dependent (y) axis
    
    x : object
        instance of ophyd.Signal (or subclass), 
        independent (x) axis
    """
    assert n >= 0, "n must be 0 or greater"
    for liveplot in bec._live_plots.values():
        lp = liveplot.get(y.name)
        if lp is None:
            logger.debug(f"no LivePlot with name {y.name}")
            continue
        if lp.x != x.name or lp.y != y.name:
            logger.debug(f"no LivePlot with axes ('{x.name}', '{y.name}')")
            continue

        # pick out only the traces that contain plot data
        # skipping the lines that show peak centers
        lines = [
            tr
            for tr in lp.ax.lines
            if len(tr._x) != 2 
                or len(tr._y) != 2 
                or (len(tr._x) == 2 and tr._x[0] != tr._x[1])
        ]
        if len(lines) > n:
            logger.debug(f"limiting LivePlot({y.name}) to {n} traces")
            lp.ax.lines = lines[-n:]
            lp.ax.legend()
            if n > 0:
                lp.update_plot()
        return lp


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


def json_export(headers, filename, zipfilename=None):
    """
    write a list of headers (from databroker) to a file

    PARAMETERS

    headers : list(headers) or `databroker._core.Results` object
        list of databroker headers as returned from `db(...search criteria...)`
    filename : str
        name of file into which to write JSON
    zipfilename : str or None
        name of ZIP file container of `filename` 
        (if None, do not ZIP `filename`)
        
        .. note::  If writing to a ZIP file, the data file is
           *only* written into the ZIP file.
    
    EXAMPLE::

        from databroker import Broker
        db = Broker.named("mongodb_config")
        headers = db(plan_name="count", since="2019-04-01")

        json_export(
            headers, 
            "data.json", 
            zipfilename="bluesky_data.zip")
    
    EXAMPLE: READ THE ZIP FILE:
    
     using :meth:`~json_import`::

        datasets = json_import("data.json", zipfilename="bluesky_data.zip")
    
    EXAMPLE: READ THE JSON TEXT FILE
    
    using :meth:`~json_import`::

        datasets = json_import("data.json)

    """
    datasets = [list(h.documents()) for h in headers]
    buf = json.dumps(datasets, cls=NumpyEncoder, indent=2)

    if zipfilename is None:
        with open(filename, "w") as fp:
            fp.write(buf)
    else:
        with zipfile.ZipFile(zipfilename, "w", allowZip64=True) as fp:
            fp.writestr(filename, buf, compress_type=zipfile.ZIP_LZMA)
                

def json_import(filename, zipfilename=None):
    """
    read the file exported by :meth:`~json_export()`
    
    RETURNS

    datasets : list of documents
        list of 
        `documents <https://blueskyproject.io/bluesky/documents.html/>`_,
        such as returned by
        `[list(h.documents()) for h in db]`
        
        See:
        https://blueskyproject.io/databroker/generated/databroker.Header.documents.html
    
    EXAMPLE
    
    Insert the datasets into the databroker ``db``::
    
        def insert_docs(db, datasets):
            for i, h in enumerate(datasets):
                print(f"{i+1}/{len(datasets)} : {len(h)} documents")
                for k, doc in h:
                    db.insert(k, doc)
    
    """
    if zipfilename is None:
        with open(filename, "r") as fp:
            buf = fp.read()
            datasets = json.loads(buf)
    else:
        with zipfile.ZipFile(zipfilename, "r") as fp:
            buf = fp.read(filename).decode("utf-8")
            datasets = json.loads(buf)
    
    return datasets


def redefine_motor_position(motor, new_position):
    """set EPICS motor record's user coordinate to `new_position`"""
    yield from bps.mv(motor.set_use_switch, 1)
    yield from bps.mv(motor.user_setpoint, new_position)
    yield from bps.mv(motor.set_use_switch, 0)

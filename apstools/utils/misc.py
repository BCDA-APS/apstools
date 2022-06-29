"""
Miscellaneous Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~cleanupText
   ~connect_pvlist
   ~dictionary_table
   ~full_dotted_name
   ~itemizer
   ~listobjects
   ~pairwise
   ~print_RE_md
   ~print_snapshot_list
   ~redefine_motor_position
   ~replay
   ~run_in_thread
   ~safe_ophyd_name
   ~split_quoted_line
   ~text_encode
   ~to_unicode_or_bust
   ~trim_string_for_EPICS
   ~unix
"""

import databroker
import logging
import ophyd
import pyRestTable
import re
import subprocess
import sys
import threading
import time

from bluesky import plan_stubs as bps
from bluesky.callbacks.best_effort import BestEffortCallback
from collections import OrderedDict

from ._core import MAX_EPICS_STRINGOUT_LENGTH
from .profile_support import ipython_shell_namespace
from ..callbacks import spec_file_writer


logger = logging.getLogger(__name__)


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


def dictionary_table(dictionary, **kwargs):
    """
    return a text table from ``dictionary``

    PARAMETERS

    dictionary
        *dict* :
        Python dictionary

    Note:  Keyword arguments parameters
    are kept for compatibility with previous
    versions of apstools.  They are ignored now.

    RETURNS

    table
        *object* or ``None`` :
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
    return ".".join(names[::-1])


def itemizer(fmt, items):
    """Format a list of items."""
    return [fmt % k for k in items]


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


def print_RE_md(dictionary=None, fmt="simple", printing=True):
    """
    custom print the RunEngine metadata in a table

    PARAMETERS

    dictionary
        *dict* :
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
    fmt = "simple"

    dictionary = dictionary or ipython_shell_namespace()["RE"].md
    md = dict(dictionary)  # copy of input for editing
    v = dictionary_table(md["versions"])  # sub-table
    md["versions"] = v.reST(fmt=fmt).rstrip()
    table = dictionary_table(md)
    if printing:
        print("RunEngine metadata dictionary:")
        print(table.reST(fmt=fmt))
    return table


def replay(headers, callback=None, sort=True):
    """
    Replay the document stream from one (or more) scans (headers).

    PARAMETERS

    headers
        *scan* or *[scan]* :
        Scan(s) to be replayed through callback.
        A *scan* is an instance of a Bluesky ``databroker.Header``.
        see: https://nsls-ii.github.io/databroker/api.html?highlight=header#header-api

    callback
        *scan* or *[scan]* :
        The Bluesky callback to handle the stream of documents from a
        scan. If ``None``, then use the `bec` (BestEffortCallback) from
        the IPython shell.
        (default:``None``)

    sort
        *bool* :
        Sort the headers chronologically if True.
        (default:``True``)

    (new in apstools release 1.1.11)
    """
    # fmt: off
    callback = callback or ipython_shell_namespace().get(
        "bec",  # get from IPython shell
        BestEffortCallback(),  # make one, if we must
    )
    # fmt: on
    _headers = headers  # do not mutate the input arg
    if isinstance(_headers, databroker.Header):
        _headers = [_headers]

    def increasing_time_sorter(run):
        return run.start["time"]

    def decreasing_time_sorter(run):
        """Default for databroker v0 results."""
        return -run.start["time"]

    # fmt: off
    sorter = {
        True: increasing_time_sorter,
        False: decreasing_time_sorter,
    }[sort]
    # fmt: on

    for h in sorted(_headers, key=sorter):
        if not isinstance(h, databroker.Header):
            # fmt: off
            raise TypeError(
                f"Must be a databroker Header: received: {type(h)}: |{h}|"
            )
            # fmt: on
        cmd = spec_file_writer._rebuild_scan_command(h.start)
        logger.debug("%s", cmd)

        # at last, this is where the real action happens
        for k, doc in h.documents():  # get the stream
            callback(k, doc)  # play it through the callback


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
    r"""
    make text safe to be used as an ophyd object name

    Given some input text string, return a clean version.
    Remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.

    The "sanitized" name fits this regular expression::

        [A-Za-z_][\w_]*

    Also can be used for safe HDF5 and NeXus names.
    """
    replacement = "_"
    noncompliance = r"[^\w_]"

    # replace ALL non-compliances with '_'
    safer = replacement.join(re.split(noncompliance, text))

    # can't start with a digit
    if safer[0].isdigit():
        safer = replacement + safer
    return safer


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
        if not quoted and p.startswith('"'):  # begin quoted text
            quoted = True
            multi = ""

        if quoted:
            if len(multi) > 0:
                multi += " "
            multi += p
            if p.endswith('"'):  # end quoted text
                quoted = False

        if not quoted:
            if multi is not None:
                parts.append(multi[1:-1])  # remove enclosing quotes
                multi = None
            else:
                parts.append(p)

    return parts


def text_encode(source):
    """Encode ``source`` using the default codepoint."""
    return source.encode(errors="ignore")


def to_unicode_or_bust(obj, encoding="utf-8"):
    """from: http://farmdev.com/talks/unicode/  ."""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


def trim_string_for_EPICS(msg):
    """String must not exceed EPICS PV length."""
    if len(msg) > MAX_EPICS_STRINGOUT_LENGTH:
        msg = msg[: MAX_EPICS_STRINGOUT_LENGTH - 1]
    return msg


def unix(command, raises=True):
    """
    Run a UNIX command, returns (stdout, stderr).

    PARAMETERS

    command
        *str* :
        UNIX command to be executed
    raises
        *bool* :
        If ``True``, will raise exceptions as needed,
        default: ``True``
    """
    if sys.platform not in ("linux", "linux2"):
        emsg = f"Cannot call unix() when OS={sys.platform}"
        raise RuntimeError(emsg)

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()

    if len(stderr) > 0:
        emsg = f"unix({command}) returned error:\n{stderr}"
        logger.error(emsg)
        if raises:
            raise RuntimeError(emsg)

    return stdout, stderr


def listobjects(show_pv=True, printing=True, verbose=False, symbols=None):
    """
    Show all the ophyd Signal and Device objects defined as globals.

    PARAMETERS

    show_pv
        *bool* :
        If True, also show relevant EPICS PV, if available.
        (default: True)
    printing
        *bool* :
        If True, print table to stdout.
        (default: True)
    verbose
        *bool* :
        If True, also show ``str(obj``.
        (default: False)
    symbols
        *dict* :
        If None, use global symbol table.
        If not None, use provided dictionary.
        (default: ``globals()``)

    RETURNS

    object:
        Instance of ``pyRestTable.Table()``

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

    (new in apstools release 1.1.8)
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
            row.append(" ".join(v._ophyd_labels_))
            table.addRow(row)
    if printing:
        print(table)
    return table


def connect_pvlist(pvlist, wait=True, timeout=2, poll_interval=0.1):
    """
    Given list of EPICS PV names, return dict of EpicsSignal objects.

    PARAMETERS

    pvlist
        *[str]* :
        list of EPICS PV names
    wait
        *bool* :
        should wait for EpicsSignal objects to connect
        (default: ``True``)
    timeout
        *float* :
        maximum time to wait for PV connections, seconds
        (default: 2.0)
    poll_interval
        *float* :
        time to sleep between checks for PV connections, seconds
        (default: 0.1)
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
        times_up = time.time() + max(0, timeout)
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


def redefine_motor_position(motor, new_position):
    """Set EPICS motor record's user coordinate to ``new_position``."""
    yield from bps.mv(motor.set_use_switch, 1)
    yield from bps.mv(motor.user_setpoint, new_position)
    yield from bps.mv(motor.set_use_switch, 0)

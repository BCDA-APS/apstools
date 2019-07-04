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
   ~itemizer
   ~json_export
   ~json_import
   ~ipython_profile_name
   ~pairwise
   ~print_snapshot_list
   ~print_RE_md
   ~run_in_thread
   ~split_quoted_line
   ~text_encode
   ~to_unicode_or_bust
   ~trim_string_for_EPICS
   ~unix_cmd

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

from collections import OrderedDict
import datetime
from email.mime.text import MIMEText
from event_model import NumpyEncoder
import json
import logging
import math
import os
import pandas
import pyRestTable
import re
import smtplib
import subprocess
import threading
import time
import xlrd
import zipfile


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


def device_read2table(device, show_ancient=True, use_datetime=True):
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
    return table


def dictionary_table(dictionary, fmt="simple"):
    """
    return a text table from ``dictionary``
    
    PARAMETERS
    
    dictionary : dict
        Python dictionary
    fmt : str
        Any of the format names provided by *pyRestTable*. [#]_
        One of these: ``simple | plain | grid | complex | markdown | list-table | html``
        
        default: ``simple``
	
	.. [#] *pyRestTable* : https://pyresttable.readthedocs.io/en/latest/examples/index.html#examples
    
    RETURNS

    table : str or `None`
        multiline text table with dictionary contents in chosen format
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
    _t = pyRestTable.Table()
    _t.addLabel("key")
    _t.addLabel("value")
    for k, v in sorted(dictionary.items()):
        _t.addRow((k, str(v)))
    return _t.reST(fmt=fmt)


def itemizer(fmt, items):
    """format a list of items"""
    return [fmt % k for k in items]


def print_RE_md(dictionary=None, fmt="simple"):
    """
    custom print the RunEngine metadata in a table
    
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
    global RE
    dictionary = dictionary or RE.md
    md = dict(dictionary)   # copy of input for editing
    v = dictionary_table(md["versions"], fmt=fmt)   # sub-table
    md["versions"] = str(v).rstrip()
    print("RunEngine metadata dictionary:")
    print(dictionary_table(md, fmt=fmt))


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


def unix_cmd(command_list):
    """run a UNIX command, returns (stdout, stderr)"""
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
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
    from ophyd import EpicsSignal

    obj_dict = OrderedDict()
    for item in pvlist:
        if len(item.strip()) == 0:
            continue
        pvname = item.strip()
        oname = "signal_{}".format(len(obj_dict))
        obj = EpicsSignal(pvname, name=oname)
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


def print_snapshot_list(db, **search_criteria):
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
    print(t) 


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

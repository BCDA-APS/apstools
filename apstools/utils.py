"""
Various utilities

.. autosummary::
   
   ~connect_pvlist
   ~EmailNotifications
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ipython_profile_name
   ~pairwise
   ~print_snapshot_list
   ~text_encode
   ~to_unicode_or_bust
   ~unix_cmd

"""

from collections import OrderedDict
from email.mime.text import MIMEText
import logging
import math
import os
import pandas
import pyRestTable
import smtplib
import subprocess
import time

from .plans import run_in_thread


logger = logging.getLogger(__name__)


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


def text_encode(source):
    """encode ``source`` using the default codepoint"""
    return source.encode(errors='ignore')


def to_unicode_or_bust(obj, encoding='utf-8'):
    """from: http://farmdev.com/talks/unicode/"""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


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

    def __init__(self):
        self.db = OrderedDict()
        self.data_labels = None
        if self.EXCEL_FILE is None:
            raise ValueError("subclass must define EXCEL_FILE")
        self.fname = os.path.join(os.getcwd(), self.EXCEL_FILE)

        self.parse()
        
    def handle_single_entry(self, entry):       # subclass MUST override
        raise NotImplementedError("subclass must override handle_single_entry() method")

    def handleExcelRowEntry(self, entry):       # subclass MUST override
        raise NotImplementedError("subclass must override handleExcelRowEntry() method")

    def parse(self, labels_row_num=None, data_start_row_num=None):
        labels_row_num = labels_row_num or self.LABELS_ROW
        xl = pandas.read_excel(self.fname, sheet_name=0, header=None)
        self.data_labels = list(xl.iloc[labels_row_num,:])
        data_start_row_num = data_start_row_num or labels_row_num+1
        grid = xl.iloc[data_start_row_num:,:]
        # grid is a pandas DataFrame
        # logger.info(type(grid))
        # logger.info(grid.iloc[:,1])
        for row_number, _ignored in enumerate(grid.iloc[:,0]):
            row_data = grid.iloc[row_number,:]
            entry = {}
            for _col, label in enumerate(self.data_labels):
                entry[label] = self._getExcelColumnValue(row_data, _col)
                self.handle_single_entry(entry)
            self.handleExcelRowEntry(entry)

    def _getExcelColumnValue(self, row_data, col):
        v = row_data.values[col]
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


class ExcelDatabaseFileGeneric(ExcelDatabaseFileBase):
    """
    Generic (read-only) handling of Excel spreadsheet-as-database
    
    Table labels are given on Excel row ``N``, ``self.labels_row = N-1``
    """
    
    def __init__(self, filename, labels_row=3):
        self._index_ = 0
        self.EXCEL_FILE = self.EXCEL_FILE or filename
        self.LABELS_ROW = labels_row
        ExcelDatabaseFileBase.__init__(self)

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
    t.addLabel("purpose")
    search_criteria["plan_name"] = "snapshot"
    for i, h in enumerate(db(**search_criteria)):
        uid = h.start["uid"].split("-")[0]
        t.addRow((i, uid, h.start["iso8601"], h.start["purpose"]))
    print(t) 

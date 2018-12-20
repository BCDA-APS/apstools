"""
Various utilities

.. autosummary::
   
   ~connect_pvlist
   ~EmailNotifications
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ipython_profile_name
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
import smtplib
import subprocess
import time


HOME_PATH = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def text_encode(source):
    """encode ``source`` using the default codepoint"""
    return source.encode(errors='ignore')


def unix_cmd(command_list):
    """run a UNIX command, returns (stdout, stderr)"""
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr


def to_unicode_or_bust(obj, encoding='utf-8'):
    """from: http://farmdev.com/talks/unicode/"""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


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
        self.fname = os.path.join(HOME_PATH, self.EXCEL_FILE)

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

"""
Various utilities

.. autosummary::
   
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ipython_profile_name
   ~text_encode
   ~to_unicode_or_bust

"""

from collections import OrderedDict
import logging
import math
import os
import pandas


HOME_PATH = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def text_encode(source):
    """encode ``source`` using the default codepoint"""
    return source.encode(errors='ignore')


def to_unicode_or_bust(obj, encoding='utf-8'):
    """from: http://farmdev.com/talks/unicode/"""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


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
    import IPython.paths
    import IPython.core.profileapp
    import IPython.core.profiledir
    
    path = IPython.paths.get_ipython_dir()
    ipd = IPython.core.profiledir.ProfileDir()
    for p in IPython.core.profileapp.list_profiles_in(path):
        pd = ipd.find_profile_dir_by_name(path, p)
        if os.path.dirname(__file__) == pd.startup_dir:
            return p

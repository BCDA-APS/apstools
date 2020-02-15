
"""
Support for Microsoft Excel spreadsheets

.. autosummary::
   
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ExcelReadError
"""

__all__ = """
    ExcelDatabaseFileBase
    ExcelDatabaseFileGeneric
    ExcelReadError
""".split()

import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict
import math
import os
import pandas
import xlrd


def to_unicode_or_bust(obj, encoding='utf-8'):
    """from: http://farmdev.com/talks/unicode/"""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


class ExcelReadError(xlrd.XLRDError): ...


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
        xl = pandas.read_excel(
            self.fname, 
            sheet_name=self.sheet_name, 
            skiprows=labels_row_num)
    
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

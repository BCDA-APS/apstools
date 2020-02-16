"""
Various utilities

.. autosummary::
   
   ~sundry.cleanupText
   ~reports.command_list_as_table
   ~epics_support.connect_pvlist
   ~reports.device_read2table
   ~reports.dictionary_table
   ~emails.EmailNotifications
   ~excel.ExcelDatabaseFileBase
   ~excel.ExcelDatabaseFileGeneric
   ~excel.ExcelReadError
   ~explorer.full_dotted_name
   ~shell.ipython_profile_name
   ~sundry.itemizer
   ~doc_streams.json_export
   ~doc_streams.json_import
   ~reports.listruns
   ~explorer.object_explorer
   ~sundry.pairwise
   ~reports.print_RE_md
   ~reports.print_snapshot_list
   ~plotting.plot_prune_fifo
   ~doc_streams.replay
   ~decorators.run_in_thread
   ~reports.show_ophyd_symbols
   ~sundry.split_quoted_line
   ~sundry.text_encode
   ~epics_support.trim_string_for_EPICS
   ~shell.unix
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

# import logging
# logger = logging.getLogger(__name__)

from .decorators import *
from .doc_streams import *
from .emails import *
from .epics_support import *
from .excel import *
from .explorer import *
from .plotting import *
from .reports import *
from .shell import *
from .sundry import *

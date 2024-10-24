from enum import Enum

import pandas
import pyRestTable

FIRST_DATA = "1995-01-01"
LAST_DATA = "2100-12-31"

MAX_EPICS_STRINGOUT_LENGTH = 40


class PRT_Table(pyRestTable.Table):
    """Change the default from pyRestTable."""

    def __repr__(self):
        return str(self)


class TableStyle(Enum):
    """Describes what table style to use."""

    pandas = pandas.DataFrame
    pyRestTable = PRT_Table  # pyRestTable.Table


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

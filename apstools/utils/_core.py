"""
Core utilities and constants for apstools.
"""

from enum import Enum
from typing import Any, Type

import pandas
import pyRestTable

FIRST_DATA: str = "1995-01-01"
LAST_DATA: str = "2100-12-31"

MAX_EPICS_STRINGOUT_LENGTH: int = 40


class PRT_Table(pyRestTable.Table):
    """Change the default from pyRestTable."""

    def __repr__(self) -> str:
        return str(self)


class TableStyle(Enum):
    """Describes what table style to use."""

    pandas: Type[pandas.DataFrame] = pandas.DataFrame
    pyRestTable: Type[PRT_Table] = PRT_Table  # pyRestTable.Table


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

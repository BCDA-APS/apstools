"""
Directory of the known plans
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~listplans
"""

import inspect
import logging
from typing import Any, Optional, Union

import pandas as pd
from ophyd.ophydobj import OphydObject

from ._core import TableStyle
from .profile_support import getDefaultNamespace

logger = logging.getLogger(__name__)


def listplans(
    base: Optional[Any] = None,
    trunc: int = 50,
    table_style: TableStyle = TableStyle.pyRestTable,
) -> Union[pd.DataFrame, Any]:
    """
    List all plans.  (Actually, lists all generator functions).

    NOTE: Can only detect generator functions.
    Bluesky plans are generator functions that generate
    ``bluesky.Msg`` objects.  There is a PR to define
    a decorator that identifies a generator function
    as a bluesky plan.

    Parameters
    ----------
    base : Optional[Any], optional
        Object that contains plan methods (if None, use global namespace).
        Default: None
    trunc : int, optional
        Truncate long docstrings to no more than trunc characters.
        Default: 50
    table_style : TableStyle, optional
        Either TableStyle.pyRestTable (default) or TableStyle.pandas,
        using values from :class:`apstools.utils.TableStyle`.

        Note: pandas.DataFrame will truncate long text to at most 50 characters.
        Default: TableStyle.pyRestTable

    Returns
    -------
    Union[pd.DataFrame, Any]
        A table containing the list of plans and their docstrings.
        The type depends on the table_style parameter.
    """
    if base is None:
        base = getDefaultNamespace(attr="user_global_ns")
        _gg = {k: v for k, v in base.items() if not k.startswith("_")}
    else:
        # fmt: off
        _gg = {
            k: getattr(base, k)
            for k in dir(base)
            if not k.startswith("_")  # not interested in these
            if k not in ("signal_names", )  # names to avoid
        }
        # fmt: on

    if inspect.ismodule(base):
        prefix = base.__name__ + "."
    elif isinstance(base, OphydObject):
        prefix = base.name + "."
    else:
        prefix = ""

    dd: dict[str, list[str]] = dict(plan=[], doc=[])

    for key, obj in _gg.items():
        if inspect.isgeneratorfunction(obj):  # TODO: bluesky.isplan(obj)
            doc = (obj.__doc__ or "").lstrip().split("\n")[0]
            if len(doc.strip()) == 0:
                doc = "---"
            more = " ..."
            if len(doc) > trunc and trunc > len(more):
                doc = doc[: trunc - len(more)] + more
            dd["plan"].append(f"{prefix}{key}")
            dd["doc"].append(doc)

    return table_style.value(dd)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

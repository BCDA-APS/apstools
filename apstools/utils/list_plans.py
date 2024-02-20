"""
Directory of the known plans
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~listplans
"""

import inspect
import logging

from ophyd.ophydobj import OphydObject

from ._core import TableStyle
from .profile_support import getDefaultNamespace

logger = logging.getLogger(__name__)


def listplans(base=None, trunc=50, table_style=TableStyle.pyRestTable):
    """
    List all plans.  (Actually, lists all generator functions).

    NOTE: Can only detect generator functions.
    Bluesky plans are generator functions that generate
    ``bluesky.Msg`` objects.  There is a PR to define
    a decorator that identifies a generator function
    as a bluesky plan.

    PARAMETERS

    base *object* or *None* :
        Object that contains plan methods (if ``None``, use global namespace.)
        (default: ``None``)
    trunc *int* :
        Truncate long docstrings to no more than ``trunc`` characters.
        (default: 50)
    table_style *object* :
        Either ``TableStyle.pyRestTable`` (default) or ``TableStyle.pandas``,
        using values from :class:`apstools.utils.TableStyle`.

        .. note:: ``pandas.DataFrame`` wll truncate long text to at most 50 characters.
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

    dd = dict(plan=[], doc=[])

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
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

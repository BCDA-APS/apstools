"""
Documentation of batch runs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~listplans
"""

import inspect
from ophyd.ophydobj import OphydObject
import pandas as pd


def listplans(base=None, trunc=40):
    """
    List all plans.  (Actually, lists all generator functions).

    NOTE: Can only detect generator functions.
    Bluesky plans are generator functions that generate
    ``bluesky.Msg`` objects.  There is a PR to define
    a decorator that identifies a generator function
    as a bluesky plan.

    PARAMETERS

    base
        *object* or *None* :
        Object that contains plan methods (if ``None``, use global namespace.)
        (default: ``None``)
    trunc
        *int* :
        Truncate long docstrings to no more than ``trunc`` characters.
        (default: 40)
    """
    prefix = ""
    if base is None:
        _gg = {k: v for k, v in globals().items() if not k.startswith("_")}
    else:
        _gg = {k: getattr(base, k) for k in dir(base) if not k.startswith("_")}
        if inspect.ismodule(base):
            prefix = base.__name__ + "."
        if isinstance(base, OphydObject):
            prefix = base.name + "."

    dd = dict(plan=[], doc=[])

    for key, obj in _gg.items():
        if inspect.isgeneratorfunction(obj):  # TODO: bluesky.isplan(obj)
            doc = (obj.__doc__ or "").split("\n")[0]
            if len(doc.strip()) == 0:
                doc = "---"
            if len(doc) > trunc and trunc > 4:
                doc = doc[: trunc - 4] + " ..."
            dd["plan"].append(f"{prefix}{key}")
            dd["doc"].append(doc)
    return pd.DataFrame(dd)

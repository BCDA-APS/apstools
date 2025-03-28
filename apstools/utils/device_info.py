"""
Device information
++++++++++++++++++

.. autosummary::

   ~listdevice
"""

import datetime
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from ophyd import Device
from ophyd import Signal
from ophyd.signal import ConnectionTimeoutError
from ophyd.signal import EpicsSignalBase

from ._core import TableStyle
from .misc import call_signature_decorator

logger = logging.getLogger(__name__)
pd.set_option("display.max_rows", None)


DEFAULT_COLUMN_WIDTH = 50
TRUNCATION_TEXT = " ..."
# Use NOT_CONNECTED_VALUE in tables for signals that are not connected.
NOT_CONNECTED_VALUE = "-n/c-"


def _all_signals(base: Union[Signal, Device]) -> List[Signal]:
    """
    Get all signals from a device.

    Args:
        base: Signal or Device instance

    Returns:
        List of signals
    """
    if isinstance(base, Signal):
        return [base]
    items = []
    if hasattr(base, "component_names"):
        for k in base.component_names:
            # Check for lazy components that may not be connected
            try:
                obj = getattr(base, k)
            except (ConnectionTimeoutError, TimeoutError):
                logger.warning(f"Could not list component: {base.name}.{k}")
                continue
            if isinstance(obj, (Device, Signal)):
                items += _all_signals(obj)
    return items


def _get_named_child(obj: Device, nm: str) -> Union[Any, str]:
    """
    Return named child of obj or None.

    Args:
        obj: Device instance
        nm: Child name

    Returns:
        Child object or "TIMEOUT" string
    """
    try:
        child = getattr(obj, nm)
        return child
    except TimeoutError:
        logger.debug(f"timeout: {obj.name}_{nm}")
        return "TIMEOUT"


def _get_pv(obj: Any) -> Optional[str]:
    """
    Return PV name, prefix, or None from ophyd object.

    Args:
        obj: Ophyd object

    Returns:
        PV name or prefix if available, None otherwise
    """
    if hasattr(obj, "pvname"):
        return obj.pvname
    elif hasattr(obj, "prefix"):
        return obj.prefix
    return None


def _list_epics_signals(obj: Union[EpicsSignalBase, Device]) -> Optional[List[EpicsSignalBase]]:
    """
    Return a list of the EPICS signals in obj.

    Args:
        obj: EpicsSignalBase or Device instance

    Returns:
        List of EPICS signals or None
    """
    if isinstance(obj, EpicsSignalBase):
        return [obj]
    elif isinstance(obj, Device):
        items = []
        for nm in obj.component_names:
            child = _get_named_child(obj, nm)
            if child in (None, "TIMEOUT"):
                continue
            result = _list_epics_signals(child)
            if result is not None:
                items.extend(result)
        return items
    return None


@call_signature_decorator
def listdevice(
    obj: Union[Signal, Device],
    scope: Optional[str] = None,
    cname: bool = False,
    dname: bool = True,
    show_pv: bool = False,
    use_datetime: bool = True,
    show_ancient: bool = True,
    max_column_width: Optional[int] = None,
    table_style: Any = TableStyle.pyRestTable,
    _call_args: Optional[Dict[str, Any]] = None,
) -> Union[pd.DataFrame, Any]:
    """
    Describe the signal information from device obj in a pandas DataFrame.

    Args:
        obj: Instance of ophyd Signal or Device
        scope: Scope of content to show ("full", "epics", "read")
        cname: Show control name in column "name"
        dname: Show data name in column "data name"
        show_pv: Show EPICS PV name in column "PV"
        use_datetime: Show EPICS timestamp
        show_ancient: Show uninitialized EPICS PVs
        max_column_width: Truncate long columns
        table_style: Table formatting style
        _call_args: Internal call arguments

    Returns:
        DataFrame with device information
    """
    if max_column_width is not None:
        if table_style != TableStyle.pyRestTable:
            logger.warning("Changing table style to pyRestTable.")
        table_style = TableStyle.pyRestTable
    limit_width = max_column_width is not None or table_style == TableStyle.pyRestTable
    max_column_width = max_column_width or DEFAULT_COLUMN_WIDTH

    scope = (scope or "full").lower()
    signals = _all_signals(obj)
    if scope in ("full", "epics"):
        if scope == "epics":
            signals = [s for s in signals if isinstance(s, EpicsSignalBase)]
    elif scope == "read":
        reading = obj.read()
        signals = [s for s in signals if s.name in reading]
    else:
        raise KeyError(f"Unknown scope='{scope}'." " Must be one of None, 'full', 'epics', 'read'")

    # in EPICS, an uninitialized PV has a timestamp of 1990-01-01 UTC
    UNINITIALIZED = datetime.datetime.timestamp(datetime.datetime.fromisoformat("1990-06-01"))

    if show_pv:
        cname = cname if "cname" in _call_args else True
        dname = dname if "dname" in _call_args else False
    if not cname and not dname:
        cname = True

    dd = defaultdict(list)
    for signal in signals:
        if scope != "epics" or isinstance(signal, EpicsSignalBase):
            ts = getattr(signal, "timestamp", 0)
            if show_ancient or (ts >= UNINITIALIZED):
                if cname:
                    head = obj
                    while head.dotted_name != "":
                        # walk back to the head
                        head = head.parent
                    dd["name"].append(f"{head.name}.{signal.dotted_name}")
                if dname:
                    dd["data name"].append(signal.name)
                if show_pv:
                    dd["PV"].append(_get_pv(signal) or NOT_CONNECTED_VALUE)
                if signal.connected:
                    try:
                        v = signal.get()
                    except Exception as reason:
                        v = str(reason)
                else:
                    v = NOT_CONNECTED_VALUE
                dd["value"].append(v)
                if use_datetime:
                    dd["timestamp"].append(datetime.datetime.fromtimestamp(ts) if ts > 0 else NOT_CONNECTED_VALUE)
                dd["value"].append(getattr(signal, "value", NOT_CONNECTED_VALUE))

    df = pd.DataFrame(dd)
    if limit_width:
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(lambda x: truncate(str(x), max_column_width, TRUNCATION_TEXT))

    if table_style == TableStyle.pyRestTable:
        return df.to_string()
    return df


def truncate(value: str, width: int, pad: str) -> str:
    """
    Truncate string to specified width.

    Args:
        value: String to truncate
        width: Maximum width
        pad: Padding text

    Returns:
        Truncated string
    """
    if len(value) <= width:
        return value
    return value[: width - len(pad)] + pad


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

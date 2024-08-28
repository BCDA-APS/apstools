"""
Device information
++++++++++++++++++

.. autosummary::

   ~listdevice
"""


import datetime
import logging
from collections import defaultdict

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


def _all_signals(base):
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


def _get_named_child(obj, nm):
    """
    return named child of ``obj`` or None
    """
    try:
        child = getattr(obj, nm)
        return child
    except TimeoutError:
        logger.debug(f"timeout: {obj.name}_{nm}")
        return "TIMEOUT"


def _get_pv(obj):
    """
    Return PV name, prefix, or None from ophyd object.
    """
    if hasattr(obj, "pvname"):
        return obj.pvname
    elif hasattr(obj, "prefix"):
        return obj.prefix


def _list_epics_signals(obj):
    """
    Return a list of the EPICS signals in obj.

    RETURNS

    list of ophyd objects that are children of ``obj``
    """
    # import pdb; pdb.set_trace()
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


@call_signature_decorator
def listdevice(
    obj,
    scope=None,
    cname=False,
    dname=True,
    show_pv=False,
    use_datetime=True,
    show_ancient=True,
    max_column_width=None,
    table_style=TableStyle.pyRestTable,
    _call_args=None,
):
    """Describe the signal information from device ``obj`` in a pandas DataFrame.

    Look through all subcomponents to find all the signals to be
    shown. Components that are disconnected will be skipped and a
    warning logged.

    EXAMPLE::

        >>> listdevice(m1)
        ======================= ======= ==========================
        data name               value   timestamp                 
        ======================= ======= ==========================
        m1                      0.0     2024-08-28 09:41:08.364137
        m1_user_setpoint        0.0     2024-08-28 09:41:08.364137
        m1_user_offset          0.0     2024-08-28 11:46:56.116048
        m1_user_offset_dir      0       2024-08-28 09:41:08.364137
        m1_offset_freeze_switch 0       2024-08-28 09:41:08.364137
        m1_set_use_switch       0       2024-08-28 09:41:08.364137
        m1_velocity             1.0     2024-08-28 09:41:08.364137
        m1_acceleration         0.2     2024-08-28 09:41:08.364137
        m1_motor_egu            degrees 2024-08-28 09:41:08.364137
        m1_motor_is_moving      0       2024-08-28 09:41:08.364137
        m1_motor_done_move      1       2024-08-28 11:46:56.116057
        m1_high_limit_switch    0       2024-08-28 09:41:08.364137
        m1_low_limit_switch     0       2024-08-28 09:41:08.364137
        m1_high_limit_travel    1000.0  2024-08-28 11:46:56.116048
        m1_low_limit_travel     -1000.0 2024-08-28 11:46:56.116048
        m1_direction_of_travel  0       2024-08-28 09:41:08.364137
        m1_motor_stop           0       2024-08-28 09:41:08.364137
        m1_home_forward         0       2024-08-28 09:41:08.364137
        m1_home_reverse         0       2024-08-28 09:41:08.364137
        m1_steps_per_revolution 2000    2024-08-28 09:41:08.364137
        ======================= ======= ==========================

    PARAMETERS

    obj
        *object* : Instance of ophyd Signal or Device.
    scope
        *str* or None : Scope of content to be shown.

        - ``"full"`` (or ``None``) shows all Signal components
        - ``"epics"`` shows only EPICS-based Signals
        - ``"read"`` shows only the signals returned by ``obj.read()``

        default: ``None``
    cname
        *bool* : Show the _control_ (Python, dotted) name in column ``name``.

        default: ``False``
    dname
        *bool* : Show the _data_ (databroker, with underlines) name in
        column ``data name``.

        default: ``True``
    show_pv
        *bool* : Show the EPICS process variable (PV) name in
        column ``PV``.

        default: ``False``

        .. note:: Special case when ``show_pv=True``:
           If ``cname`` is not provided, it will be set ``True``.
           If ``dname`` is not provided, it will be set ``False``.

    use_datetime *bool* :
        Show the EPICS timestamp (time of last update) in
        column ``timestamp``.

        default: ``True``
    show_ancient *bool* :
        Show uninitialized EPICS process variables.

        In EPICS, an uninitialized PV has a timestamp of 1990-01-01 UTC.
        This option enables or suppresses ancient values identified
        by timestamp from 1989.  These are values only defined in
        the original ``.db`` file.

        default: ``True``
    max_column_width *int* or *None* :
        Truncate long columns to no more than this length.  If not default,
        then table will be formatted using pyRestTable.

        default: ``None`` (will use ``50``)
    table_style *object* :
        Either ``apstools.utils.TableStyle.pandas`` (default) or
        using values from :class:`apstools.utils.TableStyle`.

        .. note:: ``pandas.DataFrame`` wll truncate long text
           to at most 50 characters.

    .. seealso:: ``listdevice()`` in :doc:`/examples/ho_list_control_objects`
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
        # fmt: off
        raise KeyError(
            f"Unknown scope='{scope}'."
            " Must be one of None, 'full', 'epics', 'read'"
        )
        # fmt: on

    # in EPICS, an uninitialized PV has a timestamp of 1990-01-01 UTC
    # fmt: off
    UNINITIALIZED = datetime.datetime.timestamp(
        datetime.datetime.fromisoformat("1990-06-01")
    )
    # fmt: on

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
                    dd["PV"].append(_get_pv(signal) or "")
                # At this point, either the Signal has connected or it may never
                # connect.  It's much too slow to wait for a connection timeout
                # on each signal, in series.  The default connection timeout has
                # already been set.
                # If the signal is not connected now, provide informative text
                # and move along.
                if signal.connected:
                    try:
                        v = signal.get()
                    except Exception as reason:
                        v = str(reason)
                else:
                    v = NOT_CONNECTED_VALUE
                dd["value"].append(v)
                if use_datetime:
                    dd["timestamp"].append(datetime.datetime.fromtimestamp(ts))

    def truncate(value, width, pad):
        """Ensure that str(value) fits into column of 'width'."""
        value = str(value)
        if len(value) > width:
            value = value[: width - len(pad)] + pad
        return value

    if limit_width:  # check if column widths need to be truncated
        for k in dd:
            vv = []
            for v in dd[k]:
                vv.append(truncate(v, max_column_width, TRUNCATION_TEXT))
            dd[k] = vv  # replace the row with (maybe) truncated content

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

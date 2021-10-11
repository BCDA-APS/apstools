"""
Device information
++++++++++++++++++

.. autosummary::

   ~device_read2table
   ~listdevice
   ~listdevice_1_5_2
   ~object_explorer
"""

__all__ = """
    device_read2table
    listdevice
    listdevice_1_5_2
    object_explorer
""".split()


from ophyd import Device
from ophyd.signal import EpicsSignalBase

import datetime
import logging
import pandas as pd
import pyRestTable
import warnings


logger = logging.getLogger(__name__)


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


def _ophyd_structure_walker(obj):
    """
    walk the structure of the ophyd obj

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
            result = _ophyd_structure_walker(child)
            if result is not None:
                items.extend(result)
        return items


def device_read2table(
    # fmt:off
    device, show_ancient=True, use_datetime=True, printing=True
    # fmt:on
):
    """
    DEPRECATED (release 1.3.8): Use listdevice() instead.  (Remove in 1.6.0.)
    """
    # fmt: off
    warnings.warn(
        "DEPRECATED: device_read2table() will be removed"
        " in release 1.6.0.  Use listdevice() instead.",
        DeprecationWarning,
    )
    listdevice(
        device,
        show_ancient=show_ancient,
        use_datetime=use_datetime,
        printing=printing,
    )
    # fmt: on


def listdevice_1_5_2(
    # fmt:off
    device, show_ancient=True, use_datetime=True, printing=True
    # fmt:on
):
    """
    DEPRECATED (release 1.5.3): Use listdevice() instead.  (Remove in 1.6.0.)

    Read an ophyd device and return a pyRestTable Table.

    Include an option to suppress ancient values identified
    by timestamp from 1989.  These are values only defined in
    the original ``.db`` file.
    """
    table = pyRestTable.Table()
    table.labels = "name value timestamp".split()
    ANCIENT_YEAR = 1989
    for k, rec in device.read().items():
        value = rec["value"]
        ts = rec["timestamp"]
        dt = datetime.datetime.fromtimestamp(ts)
        if dt.year > ANCIENT_YEAR or show_ancient:
            if use_datetime:
                ts = dt
            table.addRow((k, value, ts))

    if printing:
        print(table)

    return table


def listdevice(*args, **kwargs):
    return listdevice_1_5_2(*args, **kwargs)


def object_explorer(obj, sortby=None, fmt="simple", printing=True):
    """
    DEPRECATED (release 1.5.3): Use listdevice() instead.  (Remove in 1.6.0.)

    print the contents of obj
    """
    t = pyRestTable.Table()
    t.addLabel("name")
    t.addLabel("PV reference")
    t.addLabel("value")
    items = _ophyd_structure_walker(obj)
    logger.debug(f"number of items: {len(items)}")

    def sorter(obj):
        if sortby is None:
            key = obj.dotted_name
        elif str(sortby).lower() == "pv":
            key = _get_pv(obj) or "--"
        else:
            # fmt: off
            raise ValueError(
                f"sortby should be None or 'PV', found sortby='{sortby}'"
            )
            # fmt: on
        return key

    for item in sorted(items, key=sorter):
        t.addRow((item.dotted_name, _get_pv(item), item.get()))
    if printing:
        print(t.reST(fmt=fmt))
    return t

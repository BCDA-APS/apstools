
"""
print table of signal values of an ophyd Device

.. autosummary::
   
   ~full_dotted_name
   ~object_explorer

"""


__all__ = [
    'full_dotted_name',
    'object_explorer',
]


import logging
logger = logging.getLogger(__name__)

from ophyd import Device
from ophyd.signal import EpicsSignalBase
import pyRestTable


def full_dotted_name(obj):
    """
    Return the full dotted name

    The ``.dotted_name`` property does not include the 
    name of the root object.  This routine adds that.

    see: https://github.com/bluesky/ophyd/pull/797
    """
    names = []
    while obj.parent is not None:
        names.append(obj.attr_name)
        obj = obj.parent
    names.append(obj.name)
    return '.'.join(names[::-1])


def get_child(obj, nm):
    """
    return named child of ``obj`` or None
    """
    try:
        child = getattr(obj, nm)
        return child
    except TimeoutError:
        logger.debug(f"timeout: {obj.name}_{nm}")
        return "TIMEOUT"
    logger.debug(f"None: {obj.name}_{nm}")


def walker(obj):
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
            child = get_child(obj, nm)
            if child in (None, "TIMEOUT"):
                continue
            result = walker(child)
            if result is not None:
                items.extend(result)
        return items


def object_explorer(obj, sortby=None, fmt='simple', printing=True):
    """
    print the contents of obj
    """
    t = pyRestTable.Table()
    t.addLabel("name")
    t.addLabel("PV reference")
    t.addLabel("value")
    items = walker(obj)
    logger.debug(f"number of items: {len(items)}")

    def sorter(obj):
        if sortby is None:
            key = obj.dotted_name
        elif str(sortby).lower() == "pv":
            key = get_pv(obj) or "--"
        else:
            raise ValueError(
                "sortby should be None or 'PV'"
                f" found sortby='{sortby}'"
                )
        return key

    for item in sorted(items, key=sorter):
        t.addRow((item.dotted_name, get_pv(item), item.get()))
    if printing:
        print(t.reST(fmt=fmt))
    return t


def get_pv(obj):
    if hasattr(obj, "pvname"):
        return obj.pvname
    elif hasattr(obj, "prefix"):
        return obj.prefix

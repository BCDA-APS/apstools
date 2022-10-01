"""
DictionaryDevice

Create an ophyd Device defined by a dictionary so
that a simple dictionary can be recorded in a bluesky data stream.
"""

from ophyd import Component
from ophyd import Device
from ophyd import Signal
import time


def _make_dict_device_class(data={}):
    """
    Create a DictionaryDevice class using the supplied dictionary.
    """
    component_dict = {k: Component(Signal, value=v) for k, v in data.items()}
    fc = type("DictionaryDevice", (Device,), component_dict)
    return fc


def make_dict_device(obj, name="ddev"):
    """Make recordable DictionaryDevice instance from dictionary."""
    # Is obj dictionary-like?
    fix_it = False
    for v in obj.values():
        # Same structure as from Signal.read()?
        if not isinstance(v, dict):
            fix_it = True
            break
        if sorted(list(v.keys())) != sorted("value timestamp".split()):
            fix_it = True
            break
    if fix_it:
        # Make it look like .read()
        ts = time.time()
        obj = {k: dict(value=v, timestamp=ts) for k, v in obj.items()}

    kv = {k: v["value"] for k, v in obj.items()}
    ddev = _make_dict_device_class(kv)("", name=name)
    # set the timestamps to what was read
    for k, v in obj.items():
        getattr(ddev, k)._metadata["timestamp"] = v["timestamp"]
    return ddev


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

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
    """
    Make recordable DictionaryDevice instance from dictionary.

    New in release 1.6.4.
    """
    def standardize(obj):
        """Make obj look like .read()"""
        d_new = {}
        ts = time.time()  # new timestamps will be the same
        for k, v in obj.items():
            # fmt: off
            # Same structure as from Signal.read()?
            if (
                isinstance(v, dict) and
                sorted(list(v.keys())) == sorted("value timestamp".split())
            ):
                # looks like v is from .read(), accept it
                d_new[k] = v
            else:
                # Make it look like .read()
                d_new[k] = dict(value=v, timestamp=ts)
            # fmt: on
        return d_new

    obj = standardize(obj)
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

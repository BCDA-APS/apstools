"""
DictionaryDevice
+++++++++++++++++++++++++++++++++++++++

Create an ophyd Device defined by a dictionary so
that a simple dictionary can be recorded in a bluesky data stream.

.. autosummary::

    ~dict_device_factory
    ~make_dict_device
"""

import time
from typing import Any, Dict, Type, Union

from ophyd import Component
from ophyd import Device
from ophyd import Signal


def dict_device_factory(data: Dict[str, Any] = {}) -> Type[Device]:
    """
    Create a DictionaryDevice class using the supplied dictionary.

    Args:
        data: Dictionary of key-value pairs to create as Signal components.
            Each value will be used as the initial value of a Signal.

    Returns:
        Type[Device]: A new Device class with Signal components for each key-value pair.
    """
    component_dict = {k: Component(Signal, value=v) for k, v in data.items()}
    fc = type("DictionaryDevice", (Device,), component_dict)
    return fc


def make_dict_device(obj: Dict[str, Any], name: str = "ddev") -> Device:
    """
    Make recordable DictionaryDevice instance from dictionary.

    New in release 1.6.4.

    Args:
        obj: Dictionary of key-value pairs to create as Signal components.
            Values can be either direct values or dictionaries with 'value' and 'timestamp' keys.
        name: Name for the created device. Defaults to "ddev".

    Returns:
        Device: A new Device instance with Signal components for each key-value pair.
    """

    def standardize(obj: Dict[str, Any]) -> Dict[str, Dict[str, Union[Any, float]]]:
        """
        Make obj look like .read() by standardizing the format of values.

        Args:
            obj: Dictionary of key-value pairs to standardize.

        Returns:
            Dict[str, Dict[str, Union[Any, float]]]: Dictionary with standardized format
                where each value is a dict with 'value' and 'timestamp' keys.
        """
        d_new: Dict[str, Dict[str, Union[Any, float]]] = {}
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
    ddev = dict_device_factory(kv)("", name=name)
    # set the timestamps to what was read
    for k, v in obj.items():
        getattr(ddev, k)._metadata["timestamp"] = v["timestamp"]
    return ddev


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

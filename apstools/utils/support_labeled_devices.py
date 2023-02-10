import bluesky.magics

from .profile_support import getDefaultNamespace


def read_labeled_devices(labels=None):
    """
    Return a dict with the value & timestamp reading of the labeled objects.

    Args:
        labels (str or [str], optional):
            Label of configured ophyd Signala or Device object.
            Defaults to ``None`` (meaning all).

    Returns:
        dict[label, dict[signal_name, dict[]]]: Object reading (value & timestamp) of all labeled objects.

    *new in apstools release 1.6.11*
    """
    ns = getDefaultNamespace()
    devices = bluesky.magics.get_labeled_devices(ns)
    labels = labels or list(devices.keys())
    if not isinstance(labels, (list, tuple)):
        labels = [labels]

    # fmt: off
    out = {
        label: {  # hierarchy by label
            k: v
            for _, obj in devices[label]
            for k, v in obj.read().items()
            if len(v) > 0
        }
        for label in labels
    }
    # fmt: on

    return out


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2023, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

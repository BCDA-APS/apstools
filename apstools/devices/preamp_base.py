"""
Generalized ophyd Device base class for preamplifiers.

.. autosummary::

   ~PreamplifierBaseDevice
"""

from typing import Any, Dict, Optional, Union

from ophyd import Component
from ophyd import Device
from ophyd import Signal


class PreamplifierBaseDevice(Device):
    """
    Generalized interface (base class) for preamplifiers.

    All subclasses of ``PreamplifierBaseDevice`` must define how to update the
    gain with the correct value from the amplifier. An example is
    :class:`~apstools._devices.srs570_preamplifier.SRS570_PreAmplifier`.

    :see: https://github.com/BCDA-APS/apstools/issues/544

    Attributes:
        gain: A Signal component representing the preamplifier gain value.
            Default value is 1.
    """

    gain: Signal = Component(Signal, kind="normal", value=1)

    def __init__(
        self,
        name: str,
        *,
        parent: Optional[Device] = None,
        kind: str = "normal",
        labels: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the preamplifier base device.

        Args:
            name: The name of the device
            parent: The parent device, if any
            kind: The kind of device
            labels: List of labels associated with the device
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(name=name, parent=parent, kind=kind, labels=labels, **kwargs)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

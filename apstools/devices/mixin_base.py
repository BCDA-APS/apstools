"""
Base class for Device Mixins
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~DeviceMixinBase
"""

from typing import Any, Dict, Optional, Union

from ophyd import Device


class DeviceMixinBase(Device):
    """
    Base class for apstools Device mixin classes.

    .. index:: Ophyd Device Mixin; DeviceMixinBase

    This class serves as a base for all device mixins in the apstools package.
    It inherits from ophyd.Device and provides a common foundation for mixin
    functionality.

    Attributes:
        name: The name of the device
        parent: The parent device, if any
        kind: The kind of device
        labels: List of labels associated with the device
    """

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
        Initialize the device mixin.

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

"""
Mixin to add EPICS .DESC field
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EpicsDescriptionMixin
"""

from typing import Any, Dict, Optional, Union

from ophyd import Component
from ophyd import EpicsSignal

from .mixin_base import DeviceMixinBase


class EpicsDescriptionMixin(DeviceMixinBase):
    """
    Add a record's description field to a Device, such as EpicsMotor.

    .. index:: Ophyd Device Mixin; EpicsDescriptionMixin

    This mixin adds a description field to EPICS devices by connecting to the
    .DESC field of the EPICS record.

    Attributes:
        desc: An EpicsSignal component that connects to the .DESC field of the
            EPICS record.

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsDescriptionMixin

        class MyEpicsMotor(EpicsDescriptionMixin, EpicsMotor): pass

        m1 = MyEpicsMotor('xxx:m1', name='m1')
        print(m1.desc.get())

    more ideas::

        class TunableSynAxis(AxisTunerMixin, SynAxis):
            '''synthetic axis that can be tuned'''

        class TunableEpicsMotor(AxisTunerMixin, EpicsMotor):
            '''EpicsMotor that can be tuned'''

        class EpicsMotorWithDescription(EpicsDescriptionMixin, EpicsMotor):
            '''EpicsMotor with description field'''

        class EpicsMotorWithMore(
            EpicsDescriptionMixin,
            EpicsMotorDialMixin,
            EpicsMotorRawMixin,
            EpicsMotor
        ):
            '''
            EpicsMotor with more fields

            * description (``desc``)
            * soft motor limits (``soft_limit_hi``, ``soft_limit_lo``)
            * dial coordinates (``dial``)
            * raw coordinates (``raw``)
            '''
    """

    desc: EpicsSignal = Component(EpicsSignal, ".DESC")

    def __init__(
        self,
        name: str,
        *,
        parent: Optional[DeviceMixinBase] = None,
        kind: str = "normal",
        labels: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the EPICS description mixin.

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

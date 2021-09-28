"""
Mixin to add EPICS .DESC field
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EpicsDescriptionMixin
"""

from ophyd import Component
from ophyd import EpicsSignal
from .mixin_base import DeviceMixinBase


class EpicsDescriptionMixin(DeviceMixinBase):
    """
    add a record's description field to a Device, such as EpicsMotor

    .. index:: Ophyd Device Mixin; EpicsDescriptionMixin

    EXAMPLE::

        from ophyd import EpicsMotor
        from apstools.devices import EpicsDescriptionMixin

        class myEpicsMotor(EpicsDescriptionMixin, EpicsMotor): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
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
            EpicsMotorLimitsMixin,
            EpicsMotorDialMixin,
            EpicsMotorRawMixin,
            EpicsMotor):
            '''
            EpicsMotor with more fields

            * description (``desc``)
            * soft motor limits (``soft_limit_hi``, ``soft_limit_lo``)
            * dial coordinates (``dial``)
            * raw coordinates (``raw``)
            '''
    """

    desc = Component(EpicsSignal, ".DESC")

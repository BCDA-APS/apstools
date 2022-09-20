"""
Axis Tuner
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~AxisTunerException
   ~AxisTunerMixin
"""

import datetime
import logging
from bluesky import plan_stubs as bps
from collections import OrderedDict
from .mixin_base import DeviceMixinBase

logger = logging.getLogger(__name__)


class AxisTunerException(ValueError):
    """
    Exception during execution of `AxisTunerBase` subclass

    .. index:: Ophyd Exception; AxisTunerException
    """


class AxisTunerMixin(DeviceMixinBase):
    """
    Mixin class to provide tuning capabilities for an axis

    .. index:: Ophyd Device Mixin; AxisTunerMixin

    See the `TuneAxis()` example in this jupyter notebook:
    https://github.com/BCDA-APS/apstools/blob/master/docs/source/resources/demo_tuneaxis.ipynb

    HOOK METHODS

    There are two hook methods (`pre_tune_method()`, and `post_tune_method()`)
    for callers to add additional plan parts, such as opening or closing shutters,
    setting detector parameters, or other actions.

    Each hook method must accept a single argument:
    an axis object such as `EpicsMotor` or `SynAxis`,
    such as::

        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")

        class TunableSynAxis(AxisTunerMixin, SynAxis): pass

        myaxis = TunableSynAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        myaxis.tuner = TuneAxis([mydet], myaxis)
        myaxis.pre_tune_method = my_pre_tune_hook
        myaxis.post_tune_method = my_post_tune_hook

        def tune_myaxis():
            yield from myaxis.tune(md={"plan_name": "tune_myaxis"})

        RE(tune_myaxis())
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuner = None  # such as: apstools.plans.TuneAxis

        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method

    def _default_pre_tune_method(self):
        """called before `tune()`"""
        logger.info(
            "{} position before tuning: {}".format(
                self.name, self.position
            )
        )
        yield from bps.null()

    def _default_post_tune_method(self):
        """called after `tune()`"""
        logger.info(
            "{} position after tuning: {}".format(self.name, self.position)
        )
        yield from bps.null()

    def tune(self, md=None, **kwargs):
        if self.tuner is None:
            msg = "Must define an axis tuner, none specified."
            msg += "  Consider using apstools.plans.TuneAxis()"
            raise AxisTunerException(msg)

        if self.tuner.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)

        if md is None:
            md = OrderedDict()
        md["purpose"] = "tuner"
        md["datetime"] = datetime.datetime.now().isoformat(sep=" ")

        if self.tuner is not None:
            if self.pre_tune_method is not None:
                yield from self.pre_tune_method()

            yield from self.tuner.tune(md=md, **kwargs)

            if self.post_tune_method is not None:
                yield from self.post_tune_method()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

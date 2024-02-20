"""
Support for ``stage_sigs``
+++++++++++++++++++++++++++++++++++++++

Often when writing a plan, it is desired to change the staging of one or more
``ophyd.Devices`` by modifying the ``device.stage_sigs`` dictionary(ies), then
reset them to original values after the plan.

.. autosummary::

   ~restorable_stage_sigs
   ~stage_sigs_wrapper

EXAMPLE:

For example, move the motor at 2 units/second and count the scaler for 0.5
seconds during a custom plan.  After the plan, both scaler and motor will have
their original ``.stage_sigs`` dictionaries.

.. code-block:: python
    :linenos:

    @restorable_stage_sigs([scaler, motor])
    def my_plan(start, finish, npts, ct=1, v=1):
        scaler.stage_sigs = dict(preset_time=ct)
        motor.stage_sigs = dict(velocity=v)
        yield from bp.rel_scan([scaler], motor, start, finish, npts)

    RE(my_plan(-1, 1, 11, ct=0.5, v=2))

(new in apstools release 1.6.9)
"""

import logging

from bluesky.utils import make_decorator

logger = logging.getLogger(__name__)


def stage_sigs_wrapper(user_plan, devices):
    """
    Save stage_sigs from each device and restore after the user_plan.

    The user_plan is free to modify the stage_sigs of each device
    without further need to preserve original values.
    """

    def display(preface):
        for device in devices:
            logger.debug("%s: %s.stage_sigs: %s", preface, device.name, device.stage_sigs)

    def _restore():
        for device in reversed(devices):
            device.stage_sigs = original[device].copy()
        display("AFTER restore")

    original = {}
    display("ORIGINAL")
    for device in devices:
        original[device] = device.stage_sigs.copy()

    try:
        display("BEFORE plan")
        yield from user_plan
        display("AFTER plan")
    finally:
        _restore()


restorable_stage_sigs = make_decorator(stage_sigs_wrapper)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

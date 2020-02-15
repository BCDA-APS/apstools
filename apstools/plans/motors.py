
"""
motor support plans

.. autosummary::
   
   ~EmailNotifications
"""

__all__ = ["redefine_motor_position",]

import logging
logger = logging.getLogger(__name__)

from bluesky import plan_stubs as bps


def redefine_motor_position(motor, new_position):
    """set EPICS motor record's user coordinate to `new_position`"""
    yield from bps.mv(motor.set_use_switch, 1)
    yield from bps.mv(motor.user_setpoint, new_position)
    yield from bps.mv(motor.set_use_switch, 0)

"""
High Heat Load Slits
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~HHLSlits
"""

from typing import Any, Dict, Optional, Union

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor


class HHLSlits(Device):
    """
    High Heat Load Slit.

    There are no independent parts to move, so each axis only has center and size.

    Based on the 25-ID-A whitebeam slits.

    The motor parameters listed below specify which motor records
    control which axis. The last piece of the PV prefix will be
    removed, and the motor number added on. For example, if the prefix
    is "255ida:slits:US:", and the pitch motor is "255ida:slits:m3",
    then *pitch_motor* should be "m3".

    Attributes:
        h: Horizontal slit axis with size and center controls
        v: Vertical slit axis with size and center controls
        pitch: Real motor controlling pitch
        yaw: Real motor controlling yaw
        horizontal: Real motor controlling horizontal position
        diagonal: Real motor controlling diagonal position

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with HHL Slit IOC, ex: "25ida:slits:US:"
    pitch_motor:
      The motor record suffix controlling the real pitch motor, ex "m3"
    yaw_motor:
      The motor record suffix controlling the real yaw motor, ex "m4"
    horizontal_motor:
      The motor record suffix controlling the real horizontal motor, ex: "m1"
    diagonal_motor:
      The motor record suffix controlling the real diagonal motor, ex: "m2"
    """

    def __init__(
        self,
        prefix: str,
        pitch_motor: str,
        yaw_motor: str,
        horizontal_motor: str,
        diagonal_motor: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the HHL Slits device.

        Args:
            prefix: EPICS prefix required to communicate with HHL Slit IOC
            pitch_motor: The motor record suffix controlling the real pitch motor
            yaw_motor: The motor record suffix controlling the real yaw motor
            horizontal_motor: The motor record suffix controlling the real horizontal motor
            diagonal_motor: The motor record suffix controlling the real diagonal motor
            *args: Additional positional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._pitch_motor = pitch_motor
        self._yaw_motor = yaw_motor
        self._horizontal_motor = horizontal_motor
        self._diagonal_motor = diagonal_motor

        super().__init__(prefix, *args, **kwargs)

    class SlitAxis(Device):
        """
        Inner class representing a single slit axis with size and center controls.

        Attributes:
            size: Motor controlling the size of the slit
            center: Motor controlling the center position of the slit
        """

        size: EpicsMotor = Cpt(EpicsMotor, "Size", labels={"motors"})
        center: EpicsMotor = Cpt(EpicsMotor, "Center", labels={"motors"})

    # Individual slit directions
    h: SlitAxis = Cpt(SlitAxis, "h")
    v: SlitAxis = Cpt(SlitAxis, "v")

    # Real motors that directly control the slits
    pitch: EpicsMotor = FCpt(EpicsMotor, "{motor_prefix}:{_pitch_motor}", labels={"motors"})
    yaw: EpicsMotor = FCpt(EpicsMotor, "{motor_prefix}:{_yaw_motor}", labels={"motors"})
    horizontal: EpicsMotor = FCpt(EpicsMotor, "{motor_prefix}:{_horizontal_motor}", labels={"motors"})
    diagonal: EpicsMotor = FCpt(EpicsMotor, "{motor_prefix}:{_diagonal_motor}", labels={"motors"})


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

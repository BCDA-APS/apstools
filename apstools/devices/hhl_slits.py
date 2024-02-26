from ophyd import Component as Cpt
from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor


class HHLSlits(Device):
    """A rotating aperture that functions like a set of slits.

    Unlike the blades slits, there are no independent parts to move,
    so each axis only has center and size.

    Based on the 25-ID-A whitebeam slits.

    The motor parameters listed below specify which motor records
    control which axis. The last piece of the PV prefix will be
    removed, and the motor number added on. For example, if the prefix
    is "255ida:slits:US:", and the pitch motor is "255ida:slits:m3",
    then *pitch_motor* should be "m3".

    Parameters
    ==========
    pitch_motor
      The motor record suffix controlling the real pitch motor. Don't
      include a field. E.g. "m3"
    yaw_motor
      The motor record suffix controlling the real yaw motor. Don't
      include a field. E.g. "m3"
    horizontal_motor
      The motor record suffix controlling the real horizontal
      motor. This is different from the horizontal slits
      position. Don't include a field. E.g. "m3"
    diagonal_motor
      The motor record suffix controlling the real diagonal
      motor. Don't include a field. E.g. "m3"

    """

    def __init__(
        self,
        # prefix: str,
        *args,
        **kwargs,
    ):

        # Determine the prefix for the motors
        # pieces = prefix.strip(":").split(":")
        # self.motor_prefix = ":".join(pieces[:-1])

        self.motor_prefix = ""  # To do
        self._pitch_motor = "pitch_motor"  # Find name from mark of HHL Slit
        self._yaw_motor = "yaw_motor"  # Find name from mark of HHL Slit
        self._horizontal_motor = "horizontal_motor"  # Find name from mark of HHL Slit
        self._diagonal_motor = "diagonal_motor"  # Find name from mark of HHL Slit

        # super().__init__(prefix, *args, **kwargs)
        super().__init__(*args, **kwargs)  # To do

    class SlitAxis(Device):
        size = Cpt(EpicsMotor, "Size", labels={"motors"})
        center = Cpt(EpicsMotor, "Center", labels={"motors"})

    # Individual slit directions
    h = Cpt(SlitAxis, "h")
    v = Cpt(SlitAxis, "v")

    # Real motors that directly control the slits
    pitch = FCpt(EpicsMotor, "{motor_prefix}:{pitch_motor}", labels={"motors"})
    yaw = FCpt(EpicsMotor, "{motor_prefix}:{yaw_motor}", labels={"motors"})
    horizontal = FCpt(EpicsMotor, "{motor_prefix}:{horizontal_motor}", labels={"motors"})
    diagonal = FCpt(EpicsMotor, "{motor_prefix}:{diagonal_motor}", labels={"motors"})

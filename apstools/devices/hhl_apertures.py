from ophyd import Component as Cpt
from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor


class HHLAperture(Device):
    """
    High Heat Load Aperture.

    There are no independent parts to move, so each axis only has center and size.

    Based on the Variable Mass Aperture Slits support in OPTICS module.

        Similar to HHL_slits but for beamlines that dont follow 25ID nomenclature.

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with HHL Slit IOC, ex: "9ida:SL1:"
    pitch_motor:
      The motor record PV controlling the real pitch motor, ex "9ida:CR9A1:m3"
    yaw_motor:
      The motor record PV controlling the real yaw motor, ex "9ida:CR9A1:m4"
    horizontal_motor:
      The motor record PV controlling the real horizontal motor, ex: "9ida:CR9A1:m1"
    diagonal_motor:
      The motor record PV controlling the real diagonal motor, ex: "9ida:CR9A1:m2"
    """

    def __init__(
        self,
        prefix: str,
        pitch_motor: str,
        yaw_motor: str,
        horizontal_motor: str,
        diagonal_motor: str,
        *args,
        **kwargs,
    ):
        #        # Determine the prefix for the motors
        #        pieces = prefix.strip(":").split(":")
        #        self.motor_prefix = ":".join(pieces[:-1])

        self._pitch_motor = pitch_motor
        self._yaw_motor = yaw_motor
        self._horizontal_motor = horizontal_motor
        self._diagonal_motor = diagonal_motor

        super().__init__(prefix, *args, **kwargs)

    class SlitAxis(Device):
        size = Cpt(EpicsMotor, "Size", labels={"motors"})
        center = Cpt(EpicsMotor, "Center", labels={"motors"})

    # Individual slit directions
    h = Cpt(SlitAxis, "h")
    v = Cpt(SlitAxis, "v")

    # Real motors that directly control the slits
    pitch = FCpt(EpicsMotor, "{_pitch_motor}", labels={"motors"})
    yaw = FCpt(EpicsMotor, "{_yaw_motor}", labels={"motors"})
    horizontal = FCpt(EpicsMotor, "{_horizontal_motor}", labels={"motors"})
    diagonal = FCpt(EpicsMotor, "{_diagonal_motor}", labels={"motors"})

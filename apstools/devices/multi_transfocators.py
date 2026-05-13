"""
Multi-system Transfocators (a.k.a, CRLs, compact refracting lenses)

Beamline optics involving 1 or more transfocators.

EPICS support uses PyDevice for focal size calculation and lens configuration control

Available classes:
    TransfocatorSystem
        Base class for all transfocator setups
    Transfocator1x
        Single CRL, no z-motion of system
    Transfocator1xZ
        Single CRL with z-motion of system
    Transfocator2x
        Base class for double CRL system, no z-motion on either system
    Transfocator2xZ_
        Double CRL, z-motion on upstream transfocator
    Transfocator2x_Z
        Double CRL, z-motion on downstream transfocator
    Transfocator2xZZ
        Double CRL, z-motion on on both transfocators

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with transfocator IOC, ex: "100idPyCRL:CRL:"
    crls:
        list of crl labels (strings)
    samples:
        list of sample station labels (strings)
    pitch1_motor:
      The motor record PV controlling the real pitch motor on CRL1, ex "100id:m4"
    yaw1_motor:
      The motor record PV controlling the real yaw motor on CRL1, ex "100id:m5"
    x1_motor:
      The motor record PV controlling the real lateral motor on CRL1, ex: "100id:m1"
    y1_motor:
      The motor record PV controlling the real vertical motor on CRL1, ex: "100id:m2"


    Optional
    ========
    For CRL with translation (transfocator1xZ) there's one more motor:

    z1_motor:
      The motor record PV controlling the real translation motor on CRL1, ex: "100id:m3"

    For two CRL system  (transfocator2x) there's 4 more motors:

    pitch2_motor:
      The motor record PV controlling the real pitch motor on CRL1, ex "100id:m29"
    yaw2_motor:
      The motor record PV controlling the real yaw motor on CRL1, ex "100id:m30"
    x2_motor:
      The motor record PV controlling the real lateral motor on CRL1, ex: "100id:m26"
    y2_motor:
      The motor record PV controlling the real vertical motor on CRL1, ex: "100id:m27"

    For two CRL system with Translation (transfocator2xZZ), there's yet another motor:

    z2_motor:
      The motor record PV controlling the real translation motor on CRL2, ex: "100id:m28"

"""

from deprecated.sphinx import versionadded
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import EpicsMotor
from ophyd import PVPositioner


@versionadded(version="1.7.11")
class FPowerIndex(PVPositioner):
    """
    focal power index "positioner"; increasing index, increasing focal power
    """

    readback = Cpt(EpicsSignalRO, "fpower;sortedIndex_RBV")
    setpoint = Cpt(EpicsSignal, "fpower:sortedIndex")
    done = Cpt(EpicsSignalRO, "sysBusy")


@versionadded(version="1.7.11")
class FocalSize(PVPositioner):
    """
    focal size positioner
    """

    readback = Cpt(EpicsSignalRO, "fSize_actual")
    setpoint = Cpt(EpicsSignal, "focalSize")
    done = Cpt(EpicsSignalRO, "sysBusy")


@versionadded(version="1.7.11")
class TransfocatorSystem(Device):
    """
    Base class for CRL system
    """

    def __init__(
        self,
        prefix: str,
        crls: list[str],
        #        samples: list[str],
        pitch1_motor: str,
        yaw1_motor: str,
        x1_motor: str,
        y1_motor: str,
        z1_motor: str = None,
        pitch2_motor: str = None,
        yaw2_motor: str = None,
        x2_motor: str = None,
        y2_motor: str = None,
        z2_motor: str = None,
        *args,
        **kwargs,
    ):

        #        self.crls = crls
        #        self.samples = samples
        #
        #        self._pitch1_motor = pitch1_motor
        #        self._yaw1_motor = yaw1_motor
        #        self._x1_motor = x1_motor
        #        self._y1_motor = y1_motor
        #        self._z1_motor = z1_motor
        #
        #        self._pitch2_motor = pitch2_motor
        #        self._yaw2_motor = yaw2_motor
        #        self._x2_motor = x2_motor
        #        self._y2_motor = y2_motor
        #        self._z2_motor = z2_motor

        super().__init__(prefix, *args, **kwargs)

    focalPower = FCpt(FPowerIndex, "{prefix}")
    focalSize = FCpt(FocalSize, "{prefix}")

    q = Cpt(EpicsSignalRO, "q", kind="hinted")
    dq = Cpt(EpicsSignalRO, "dq", kind="hinted")

    sam_position_readback = Cpt(EpicsSignalRO, "SamPosCalc.F", kind="hinted")
    sam_position_offset_readback = Cpt(EpicsSignalRO, "SamPosCalc.G", kind="hinted")

    energy_keV_local = Cpt(EpicsSignal, "EnergyLocal", kind="config")
    energy_keV_mono = Cpt(EpicsSignalRO, "EnergyBeamline", kind="config")
    energy_keV_lookup = Cpt(EpicsSignalRO, "energy_rbv", kind="hinted")

    beamMode = Cpt(EpicsSignal, "beamMode", string=True, kind="config")
    energyMode = Cpt(EpicsSignal, "energySelect", string=True, kind="config")

    systemType = Cpt(EpicsSignal, "sysType_RBV", write_pv="sysType", string=True, kind="config")

    system1 = Cpt(EpicsSignal, "system1_RBV", write_pv="system1", string=True, kind="config")
    system2 = Cpt(EpicsSignal, "system2_RBV", write_pv="system2", string=True, kind="config")

    sample = Cpt(EpicsSignal, "sample_RBV", write_pv="sample", string=True, kind="config")


@versionadded(version="1.7.11")
class Transfocator1x(TransfocatorSystem):
    """
    Base class for single CRL system
    """

    def __init__(
        self,
        prefix: str,
        crls: list[str],
        pitch1_motor: str,
        yaw1_motor: str,
        x1_motor: str,
        y1_motor: str,
        *args,
        **kwargs,
    ):

        self.crls = crls

        self._pitch1_motor = pitch1_motor
        self._yaw1_motor = yaw1_motor
        self._x1_motor = x1_motor
        self._y1_motor = y1_motor

        super().__init__(prefix, crls, pitch1_motor, yaw1_motor, x1_motor, y1_motor, *args, **kwargs)

    binary_crl1_config = FCpt(EpicsSignalRO, "{prefix}{crls[0]}:lenses", kind="hinted")
    bw_crl1_config = FCpt(EpicsSignalRO, "{prefix}{crls[0]}:lensConfig_BW")
    rbv_crl1_config = FCpt(EpicsSignalRO, "{prefix}{crls[0]}:lensConfig_RBV", kind="hinted")
    crl1_z_pos = FCpt(EpicsSignalRO, "{prefix}{crls[0]}:oePositionOffset_RBV")
    interLensDelay1 = FCpt(EpicsSignal, "{prefix}{crls[0]}:interLensDelay", kind="config")

    binary_crl1_set = FCpt(EpicsSignal, "{prefix}{crls[0]}:lens_decode.A", kind="hinted")

    pitch1 = FCpt(EpicsMotor, "{_pitch1_motor}", labels={"motors"})
    yaw1 = FCpt(EpicsMotor, "{_yaw1_motor}", labels={"motors"})
    x1 = FCpt(EpicsMotor, "{_x1_motor}", labels={"motors"})
    y1 = FCpt(EpicsMotor, "{_y1_motor}", labels={"motors"})


@versionadded(version="1.7.11")
class Transfocator1xZ(Transfocator1x):
    """
    Single CRL system with z-motion
    """

    def __init__(
        self,
        prefix: str,
        z1_motor: str,
        *args,
        **kwargs,
    ):

        self._z1_motor = z1_motor

        super().__init__(prefix, *args, **kwargs)

    z1 = FCpt(EpicsMotor, "{_z1_motor}", labels={"motors"})


@versionadded(version="1.7.11")
class Transfocator2x(Transfocator1x):
    """
    Base class for 2 CRL system
    """

    def __init__(
        self,
        prefix: str,
        crls: list[str],
        pitch2_motor: str,
        yaw2_motor: str,
        x2_motor: str,
        y2_motor: str,
        *args,
        **kwargs,
    ):

        self.crls = crls

        self._pitch2_motor = pitch2_motor
        self._yaw2_motor = yaw2_motor
        self._x2_motor = x2_motor
        self._y2_motor = y2_motor

        super().__init__(prefix, crls, *args, **kwargs)

    binary_crl2_config = FCpt(EpicsSignalRO, "{prefix}{crls[1]}:lenses", kind="hinted")
    bw_crl2_config = FCpt(EpicsSignalRO, "{prefix}{crls[1]}:lensConfig_BW")
    rbv_crl2_config = FCpt(EpicsSignalRO, "{prefix}{crls[1]}:lensConfig_RBV", kind="hinted")
    crl2_z_pos = FCpt(EpicsSignalRO, "{prefix}{crls[1]}:oePositionOffset_RBV")
    interLensDelay2 = FCpt(EpicsSignal, "{prefix}{crls[1]}:interLensDelay", kind="config")

    binary_crl2_set = FCpt(EpicsSignal, "{prefix}{crls[1]}:lens_decode.A", kind="hinted")

    pitch2 = FCpt(EpicsMotor, "{_pitch2_motor}", labels={"motors"})
    yaw2 = FCpt(EpicsMotor, "{_yaw2_motor}", labels={"motors"})
    x2 = FCpt(EpicsMotor, "{_x2_motor}", labels={"motors"})
    y2 = FCpt(EpicsMotor, "{_y2_motor}", labels={"motors"})


@versionadded(version="1.7.11")
class Transfocator2xZ_(Transfocator2x):
    """
    2 CRL system, upstream CRL has z-motion
    """

    def __init__(
        self,
        prefix: str,
        z1_motor: str,
        *args,
        **kwargs,
    ):

        self._z1_motor = z1_motor
        super().__init__(prefix, *args, **kwargs)

    z1 = FCpt(EpicsMotor, "{_z1_motor}", labels={"motors"})


@versionadded(version="1.7.11")
class Transfocator2x_Z(Transfocator2x):
    """
    2 CRL system, only downstream CRL has z-motion
    """

    def __init__(
        self,
        prefix: str,
        z2_motor: str,
        *args,
        **kwargs,
    ):

        self._z2_motor = z2_motor
        super().__init__(prefix, *args, **kwargs)

    z2 = FCpt(EpicsMotor, "{_z2_motor}", labels={"motors"})


@versionadded(version="1.7.11")
class Transfocator2xZZ(Transfocator2xZ_):
    """
    2 CRL system, each CRL has z-motion
    """

    def __init__(
        self,
        prefix: str,
        z2_motor: str,
        *args,
        **kwargs,
    ):

        self._z2_motor = z2_motor

        super().__init__(prefix, *args, **kwargs)

    z2 = FCpt(EpicsMotor, "{_z2_motor}", labels={"motors"})

"""
Simulate process controllers as positioners using EPICS records.

.. autosummary::

    ~SimulatedSwaitControllerPositioner
    ~SimulatedTransformControllerPositioner
"""

import time
from typing import Any, Dict, Optional, Union

from ophyd import FormattedComponent as FC

from ..synApps import SwaitRecord
from ..synApps import TransformRecord
from . import PVPositionerSoftDoneWithStop


class SimulatedSwaitControllerPositioner(PVPositionerSoftDoneWithStop):
    """
    Simulated process controller as positioner with EPICS swait record.

    The swait record completes the feedback loop, computing
    the next simulated controller reading.

    Example with ``swait`` record::

        controller = SimulatedSwaitControllerPositioner(
            "",
            name="controller",
            loop_pv="gp:userCalc1",
        )
        controller.wait_for_connection()
        controller.setup(25)

    .. autosummary::

        ~setup
    """

    loop: SwaitRecord = FC(SwaitRecord, "{loop_pv}", kind="config")

    def __init__(
        self,
        *args: Any,
        loop_pv: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the simulated swait controller positioner.

        Args:
            *args: Variable length argument list
            loop_pv: The EPICS PV prefix for the swait record
            **kwargs: Additional keyword arguments to pass to the parent class

        Raises:
            ValueError: If loop_pv is empty
        """
        if len(loop_pv.strip()) == 0:
            raise ValueError("Must supply a value for 'loop_pv'.")

        self.loop_pv = loop_pv

        kwargs["readback_pv"] = f"{loop_pv}.VAL"
        kwargs["setpoint_pv"] = f"{loop_pv}.B"

        super().__init__(*args, **kwargs)

    def setup(
        self,
        setpoint: float,
        label: str = "controller",
        noise: float = 1,
        period: str = "1 second",
        max_change: float = 1,
        tolerance: float = 1,
    ) -> None:
        """
        Configure the swait record as a process controller.

        Args:
            setpoint: The target value for the controller
            label: A descriptive label for the controller
            noise: The amount of random noise to add
            period: The update period for the controller
            max_change: The maximum allowed change per update
            tolerance: The tolerance for considering the controller "in position"
        """
        self.tolerance.put(tolerance)

        swait = self.loop
        swait.reset()  # remove any prior configuration
        time.sleep(2.0 / 60)  # short pause for IOC processing

        swait.description.put(label)
        swait.channels.A.input_value.put(setpoint)  # readback
        swait.channels.A.input_pv.put(swait.calculated_value.pvname)
        swait.channels.B.input_value.put(setpoint)  # setpoint
        swait.channels.C.input_value.put(noise)
        swait.channels.D.input_value.put(max_change)
        swait.scanning_rate.put(period)
        swait.precision.put(3)
        swait.calculated_value.put(setpoint)  # preset initial value
        swait.calculation.put("A+max(-D,min(D,(B-A)))+C*(RNDM-0.5)")


class SimulatedTransformControllerPositioner(PVPositionerSoftDoneWithStop):
    """
    Simulated process controller as positioner with EPICS transform record.

    The transform record completes the feedback loop, computing the next
    simulated controller reading and reporting if the readback is "in position".

    Example with ``transform`` record::

        controller = SimulatedTransformControllerPositioner(
            "", name="controller", loop_pv="gp:userTran1",
        )
        controller.wait_for_connection()
        controller.setup(25)

    .. autosummary::

        ~setup
    """

    loop: TransformRecord = FC(TransformRecord, "{loop_pv}", kind="config")

    def __init__(
        self,
        *args: Any,
        loop_pv: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the simulated transform controller positioner.

        Args:
            *args: Variable length argument list
            loop_pv: The EPICS PV prefix for the transform record
            **kwargs: Additional keyword arguments to pass to the parent class

        Raises:
            ValueError: If loop_pv is empty
        """
        if len(loop_pv.strip()) == 0:
            raise ValueError("Must supply a value for 'loop_pv'.")

        self.loop_pv = loop_pv

        kwargs["readback_pv"] = f"{loop_pv}.H"
        kwargs["setpoint_pv"] = f"{loop_pv}.B"

        super().__init__(*args, **kwargs)

        self.following_error = self.loop.channels.E.current_value

    def setup(
        self,
        setpoint: float,
        label: str = "controller",
        noise: float = 2,
        period: str = "1 second",
        max_change: float = 2,
        tolerance: float = 1,
    ) -> None:
        """
        Configure the transform record as a process controller.

        Args:
            setpoint: The target value for the controller
            label: A descriptive label for the controller
            noise: The amount of random noise to add
            period: The update period for the controller
            max_change: The maximum allowed change per update
            tolerance: The tolerance for considering the controller "in position"
        """
        self.wait_for_connection()
        self.tolerance.put(tolerance)

        transform = self.loop
        transform.reset()  # remove any prior configuration
        time.sleep(2.0 / 60)  # short pause for IOC processing

        transform.description.put(label)

        transform.channels.A.comment.put("last readback")
        transform.channels.A.current_value.put(setpoint)  # readback
        transform.channels.A.input_pv.put(transform.channels.H.current_value.pvname)

        transform.channels.B.comment.put("setpoint")
        transform.channels.B.current_value.put(setpoint)  # setpoint

        transform.channels.C.comment.put("noise level")
        transform.channels.C.current_value.put(noise)

        transform.channels.D.comment.put("max_change")
        transform.channels.D.current_value.put(max_change)

        transform.channels.E.comment.put("following error")
        transform.channels.E.expression.put("B-A")

        transform.channels.F.comment.put("step")
        transform.channels.F.expression.put("max(-D,min(D,E))")

        transform.channels.G.comment.put("noise")
        transform.channels.G.expression.put("C*(RNDM-0.5)")

        transform.channels.H.comment.put("readback")
        transform.channels.H.current_value.put(setpoint)  # preset initial value
        transform.channels.H.expression.put("A+F+G")

        transform.channels.I.comment.put("tolerance")
        transform.channels.I.current_value.put(tolerance)

        transform.channels.J.comment.put("in position")
        transform.channels.J.expression.put("abs(H-B)<=I")

        transform.precision.put(3)

        transform.scanning_rate.put(period)

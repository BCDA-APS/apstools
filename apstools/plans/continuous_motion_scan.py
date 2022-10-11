"""
Continuous motion scan using scaler v. motor
++++++++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ContinuousScalerMotorFlyer
   ~fly_scaler_motor

New in release 1.6.6
"""

from bluesky import plans as bp
from ophyd import Device
from ophyd import DeviceStatus
import time


def fly_scaler_motor(scaler, motor, start_position, end_position, velocity=None, num_points=10, md={}):
    """
    Run the ContinuousScalerMotorFlyer in a plan.

    ::

        RE(
            fly_scaler_motor(
                scaler, motor, start_position, end_position,
                velocity=None, num_points=10,
                md={},
            )
        )

    New in release 1.6.6
    """
    flyer = ContinuousScalerMotorFlyer(
        scaler,
        motor,
        start_position,
        end_position,
        velocity=velocity,
        num_points=num_points,
        name="fly_scaler_motor_object",
    )
    if md is None:
        md = {}
    yield from bp.fly([flyer], md=md)


class ContinuousScalerMotorFlyer(Device):
    """
    Documentation

    New in release 1.6.6
    """

    # TODO: move to devices

    def __init__(
        self,
        scaler,
        motor,
        start_position,
        end_position,
        *args,
        velocity=None,
        num_points=10,
        stream_name="primary",
        # md={},
        **kwargs,
    ):
        if not hasattr(scaler, "count"):
            raise TypeError(f"Not prepared to handle object as scaler: {scaler=}")
        if not hasattr(motor, "motor_done_move"):
            raise TypeError(f"Not prepared to handle object as motor: {motor=}")

        self._scaler = scaler
        self._motor = motor
        self._start_position = start_position
        self._end_position = end_position
        self._velocity = velocity
        self._num_points = num_points

        # self._original = {}
        # self._events = []

        self.stream_name = stream_name

        super().__init__(*args, **kwargs)

    def kickoff(self):
        """Start the flyer."""
        status = DeviceStatus(self)
        status.set_finished()  # ALWAYS in kickoff()
        return status

    def complete(self):
        """Wait for the flyer to complete."""
        status = DeviceStatus(self)
        status.set_finished()  # once the flyer is truly complete
        return status

    def describe_collect(self):
        """Describe the data from collect()."""
        schema = {}
        return {self.stream_name: schema}

    def collect(self):
        """Report data collected by this flyer."""
        event = dict(time=time.time(), data={}, timestamps={})
        yield event

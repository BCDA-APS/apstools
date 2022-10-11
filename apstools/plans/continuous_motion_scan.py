"""
Continuous motion scan using scaler v. motor
++++++++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ContinuousScalerMotorFlyer
   ~fly_scaler_motor
   ~FlyerError

New in release 1.6.6
"""

from apstools.utils import run_in_thread
from bluesky import plans as bp
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import Signal
import logging
import time

logger = logging.getLogger(__name__)
MOTOR_BASE_VELOCITY = 0.1  # Provided in motor's .VBAS field


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


class FlyerError(RuntimeError):
    """Raised by ContinuousScalerMotorFlyer."""


# TODO: move to devices
class ContinuousScalerMotorFlyer(Device):
    """
    Documentation

    New in release 1.6.6
    """

    mode = Component(Signal, value="idle")

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

        self._restore_db = []
        self._readings = []  # cache of new device readings
        self._old_scaler_reading = None
        self._action_modes = "idle kickoff taxi fly return".split()

        self.stream_name = stream_name
        self.flyscan_complete_status = DeviceStatus(self)

        super().__init__(*args, **kwargs)

    def add_reading(self):
        """Record a reading to the cache."""
        if self._old_scaler_reading is None:
            raise FlyerError("No previous scaler reading.")

        s_read = self._scaler.read()
        delta = s_read.copy()
        for k in delta.keys():
            delta[k]["value"] -= self._old_scaler_reading[k]["value"]  # difference
        self._old_scaler_reading = s_read

        reading = {}
        reading.update(self._motor.read())
        reading.update(delta)
        self._readings.append(reading)

    @run_in_thread
    def fly_scan_activity(self):
        """
        Prep and run the fly scan.

        Runs in background thread so it does not block RunEngine.
        Not a plan (generator function), so blocking code is allowed.
        """
        # ---------------------------------------
        # self.mode.put("kickoff")  # already
        self._readings = []  # clear the cache

        # ---------------------------------------
        self.mode.put("taxi")
        self._restore_db.append((self._motor.user_setpoint, self._motor.position))
        st = self._motor.move(self._start_position)  # FIXME: Why does this timeout?
        if not st.done:
            raise FlyerError(f"Did not move to start position: {self._start_position}")
        del st
        self._set_velocity(self._velocity)

        # TODO: start scaler counting

        self._old_scaler_reading = self._scaler.read()
        self.add_reading()  # provisional

        # TODO: start accumulator (collects only when mode="fly")
        # TODO: start motion
        self._motor.user_setpoint.put(self._end_position)

        # ---------------------------------------
        self.mode.put("fly")
        self.add_reading()  # provisional
        while not self._motor.motor_done_move.get():
            time.sleep(0.05)

        # ---------------------------------------
        self.mode.put("return")
        self._restore_settings()

        # ---------------------------------------
        # once all is complete...
        self.mode.put("idle")
        self.flyscan_complete_status.set_finished()  # once the flyer is truly complete

    def _set_velocity(self, velocity):
        if velocity is None:
            velocity = self._motor.velocity.get()

        target_velocity = max(MOTOR_BASE_VELOCITY, velocity)
        if self._motor.velocity.get() != target_velocity:
            self._restore_db.append((self._motor.velocity, self._motor.velocity.get()))
            self._motor.velocity.put(target_velocity)
            velocity = self._motor.velocity.get()  # value as reported by the motor
        logger.info(
            "scanned motor '%s' velocity: %.3f %s/s",
            self._motor.name, velocity, self._motor.egu
        )
        return velocity

    def _restore_settings(self):
        for pair in reversed(self._restore_db):
            pair[0].put(pair[-1])
        self._restore_db = []

    def kickoff(self):
        """Start the flyer."""
        self.mode.put("kickoff")
        self.fly_scan_activity()
        status = DeviceStatus(self)
        status.set_finished()  # ALWAYS in kickoff()
        return status

    def complete(self):
        """Wait for the flyer to complete."""
        return self.flyscan_complete_status

    def describe_collect(self):
        """Describe the data from collect()."""
        schema = {}
        schema.update(self._motor.describe())
        schema.update(self._scaler.describe())
        return {self.stream_name: schema}

    def collect(self):
        """Report data collected by this flyer."""
        new_readings = self._readings.copy()
        self._readings = []  # clear the cache

        # TODO: What if there are no readings in the cache?
        for reading in new_readings:
            event = dict(data={}, timestamps={})
            tslist = []
            for k, r in reading.items():
                tslist.append(r["timestamp"])
                event["timestamps"].update({k: r["timestamp"]})
                event["data"].update({k: r["value"]})
            event["time"] = max(tslist)  # most recent timestamp
            yield event

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

    def add_reading(self):  # FIXME: timestamps & previous reading
        """Record a reading to the cache."""
        def get_read_timestamp(d):
            for v in d.values():
                return v["timestamp"]

        if self._old_scaler_reading is None:
            raise FlyerError("No previous scaler reading.")
        print(f"{time.time()=}")
        print(f"{get_read_timestamp(self._old_scaler_reading)=}")

        # read both as synchronous as possible
        m_read = self._motor.read()
        s_read = self._scaler.read()
        print(f"{get_read_timestamp(s_read)=}")

        delta = s_read.copy()
        for k, old in self._old_scaler_reading.items():
            delta[k]["value"] = delta[k]["value"] - old["value"]  # difference
        self._old_scaler_reading = s_read.copy()
        print(f"{get_read_timestamp(self._old_scaler_reading)=}")
        print("~"*40)

        reading = {}
        reading.update(m_read)
        # reading.update(s_read)
        reading.update(delta)
        self._readings.append(reading)

    def _fly_scan_kickoff(self):
        # self.mode.put("kickoff")  # already
        logger.debug("mode: %s", self.mode.get())
        self._readings = []  # clear the cache
        self._restore_db = []
        taxi_status = DeviceStatus(None)
        return taxi_status

    def _fly_scan_taxi(self, taxi_status):
        self.mode.put("taxi")
        logger.debug("mode: %s", self.mode.get())

        # begin move to start position
        self._restore_db.append((self._motor.user_setpoint, self._motor.position))
        self._motor.user_setpoint.put(self._start_position)

        velocity = self._set_velocity(self._velocity)

        scan_time_expected = abs(self._start_position - self._end_position)/velocity
        acquire_period = scan_time_expected / self._num_points
        logger.info("expected scan time: %.1f seconds", scan_time_expected)
        logger.info("take a reading every %.3f seconds", acquire_period)

        self._restore_db.append((self._scaler.preset_time, self._scaler.preset_time.get()))
        self._restore_db.append((self._scaler.count, self._scaler.count.get()))
        extra_scaler_time = 9  # so scaler does not stop before motor
        self._scaler.preset_time.put(scan_time_expected + extra_scaler_time)

        # wait for move to start position
        time_remaining = abs(self._motor.position - self._start_position) / velocity
        extra_motion_time = 2
        expire = time.time() + time_remaining + extra_motion_time
        while not self._motor.motor_done_move.get(): # != 1:
            time.sleep(0.000_1)
            if time.time() >= expire:
                raise FlyerError(
                    "Did not move to start position: {self._start_position}"
                )

        self._scaler.count.put("Count")  # start scaler counting
        t_start = time.time()
        while True:
            s_read = self._scaler.read()
            for v in s_read.values():
                t_read = v["timestamp"]
                break
            if t_read > t_start:
                break
            time.sleep(0.000_1)  # wait for EPICS
        self._old_scaler_reading = s_read
        self.add_reading()

        moving_status = DeviceStatus(self._motor.motor_done_move)
        self._watch_motor(taxi_status, moving_status)
        self._fly_scan_sampler(acquire_period, taxi_status, moving_status)
        self._motor.user_setpoint.put(self._end_position)  # start motion

        taxi_status.set_finished()
        return moving_status

    def _fly_scan_fly(self, moving_status):
        self.mode.put("fly")
        logger.debug("mode: %s", self.mode.get())
        moving_status.wait()

    def _fly_scan_return(self):
        self.mode.put("return")
        logger.debug("mode: %s", self.mode.get())
        self._restore_settings()

    @run_in_thread
    def fly_scan_activity(self):
        """
        Prep and run the fly scan.

        Runs in background thread so it does not block RunEngine.
        Not a plan (generator function), so blocking code is allowed.
        """
        logger.debug("enter fly_scan_activity()")
        try:
            taxi_status = self._fly_scan_kickoff()
            moving_status = self._fly_scan_taxi(taxi_status)
            self._fly_scan_fly(moving_status)
        except FlyerError as exc:
            logger.error("FlyerError: %s", exc)
            print(f"FlyerError: {exc=}")
        finally:
            self._fly_scan_return()

        self.mode.put("idle") # once all is complete...
        logger.debug("mode: %s", self.mode.get())
        self.flyscan_complete_status.set_finished()  # once the flyer is truly complete
        logger.debug("leave fly_scan_activity()")

    def _set_velocity(self, velocity):
        if velocity is None:
            velocity = self._motor.velocity.get()

        target_velocity = max(MOTOR_BASE_VELOCITY, velocity)
        if self._motor.velocity.get() != target_velocity:
            self._restore_db.append((self._motor.velocity, self._motor.velocity.get()))
            self._motor.velocity.put(target_velocity)
            velocity = self._motor.velocity.get(use_monitor=False)  # value as reported by the motor
        logger.info(
            "scanned motor '%s' velocity: %.3f %s/s",
            self._motor.name, velocity, self._motor.egu
        )
        return velocity

    @run_in_thread
    def _fly_scan_sampler(self, acquire_period, taxi_status, fly_status):
        """Acquire readings at periodic intervals while flying."""
        logger.debug("enter _sampler()")
        while not taxi_status.done:
            # wait for mode="fly" to start
            time.sleep(0.000_1)

        logger.debug("_sampler() active=%s fly_status=%s", acquire_period, fly_status)
        report_time = time.time() + acquire_period
        i = 0
        while not fly_status.done:
            if time.time() >= report_time and self.mode.get() == "fly":
                self.add_reading()
                i += 1
                logger.debug(
                    "add_reading(): i=%s time=%s report_time=%s",
                    i, time.time(), report_time
                )
                report_time += acquire_period
            time.sleep(acquire_period/25)
        logger.debug("leave _sampler()")

    @run_in_thread
    def _watch_motor(self, taxi_status, moving_status):
        logger.debug("enter _watch_motor()")
        while not taxi_status.done:
            # wait for mode="fly" to start
            time.sleep(0.001)

        logger.debug("_watch_motor() active")
        while not self._motor.motor_done_move.get():
            # wait for motor to stop
            time.sleep(0.05)
        moving_status.set_finished()
        logger.debug("leave _watch_motor()")

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

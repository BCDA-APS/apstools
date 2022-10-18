"""
Motor and scaler flyer, constant velocity
++++++++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~SignalValueStack
   ~FlyerError
   ~FlyerBase
   ~ActionsFlyer
   ~_MotorFlyer
   ~FlyerPlusModes
   ~FlyerPlusScaler
   ~FlyerPlusAcquisition

New in release 1.6.6
"""

from ..utils import run_in_thread
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import Signal
from ophyd.scaler import ScalerCH
from ophyd.status import Status
import logging
import time

logger = logging.getLogger(__name__)


class SignalValueStack:
    """Gather a list of (signal, value) pairs to be restored later."""

    def __init__(self) -> None:
        self.clear()

    def add(self, signal, value):
        """Push a (signal, value) pair on to the stack."""
        self._cache.append((signal, value))

    def clear(self):
        """Empty the stack."""
        self._cache = []

    def remember(self, signal):
        """Push the signal's value on to the stack."""
        self.add(signal, signal.get())

    def restore(self):
        """Write the signals in the stack, in reverse order."""
        for pair in reversed(self._cache):
            pair[0].put(pair[-1])
        self._cache = []


class FlyerError(RuntimeError):
    """Exceptions specific to these flyers."""


class FlyerBase(Device):
    """Canonical ophyd Flyer object."""

    STREAM_NAME = "primary"

    def kickoff(self):
        """Start the flyer."""
        status = DeviceStatus(self)
        status.set_finished()  # ALWAYS in kickoff()
        return status

    def complete(self):
        """Wait for the flyer to complete."""
        status = DeviceStatus(self)
        status.set_finished()  # once the flyer is done
        return status

    def describe_collect(self):
        """Describe the data from collect()."""
        logging.debug("describe_collect()")
        schema = {}
        return {self.STREAM_NAME: schema}

    def collect(self):
        """Data event(s)."""
        logging.debug("collect()")
        event = dict(time=time.time(), data={}, timestamps={})
        yield event


class ActionsFlyer(FlyerBase):
    """Call actions_thread() method from kickoff().  Extends FlyerBase()."""

    def __init__(self, *args, **kwargs):
        self.status_actions_thread = None
        self.status_complete = None
        self.status_kickoff = None
        super().__init__(*args, **kwargs)

    def kickoff(self):
        """Start the flyer."""
        logging.debug("kickoff()")

        self.status_actions_thread = Status()
        self.status_complete = Status()
        self.status_kickoff = Status()

        logging.debug("starting actions thread")
        self.actions_thread()

        self.status_kickoff.set_finished()  # ALWAYS in kickoff()
        return self.status_kickoff

    def complete(self):
        """Wait for the flyer to complete."""
        logging.debug("complete()")

        self.status_actions_thread.wait()
        self.status_complete.set_finished()
        logging.debug("completed actions thread")

        return self.status_complete

    @run_in_thread
    def actions_thread(self):
        """Run the flyer in a thread.  Not a bluesky plan."""
        logging.debug("in actions thread")
        time.sleep(1)  # as a demonstration of a slow action
        self.status_actions_thread.set_finished()
        logging.debug("actions thread marked 'finished'")


class _MotorFlyer(ActionsFlyer):
    """Move the motor through its trajectory.  Extends ActionsFlyer()."""

    def __init__(self, motor, start, finish, *args, fly_time=1, fly_time_pad=2, **kwargs):
        if not hasattr(motor, "velocity"):
            raise TypeError(f"Unprepared to handle object as motor: {motor=}")
        if not isinstance(fly_time, (float, int)):
            raise TypeError(f"Must be a number: {fly_time=}")
        if fly_time <= 0:
            raise ValueError(f"Must be a POSITIVE number: {fly_time=}")
        if not isinstance(fly_time_pad, (float, int)):
            raise TypeError(f"Must be a number: {fly_time_pad=}")
        if fly_time_pad <= 0:
            raise ValueError(f"Must be a POSITIVE number: {fly_time_pad=}")

        self._motor = motor
        self._pos_start = start
        self._pos_finish = finish
        self._fly_time = fly_time
        self._fly_time_pad = fly_time_pad

        self._original_values = SignalValueStack()

        self.status_fly = None
        self.status_taxi = None

        super().__init__(*args, **kwargs)

    @run_in_thread
    def actions_thread(self):
        """
        Prep and run the fly scan in a thread.

        Runs in background thread so it does not block RunEngine. This is not a
        generator function. It is not a bluesky plan, so blocking code is ok.
        """
        self.status_taxi = self._motor.move(self._pos_start, wait=False)
        self.status_taxi.wait()
        if self._motor.position != self._pos_start:  # TODO: within tolerance?
            raise FlyerError(
                "Not in requested taxi position:"
                f" requested={self._pos_start}"
                f" position={self._motor.position}"
            )

        velocity = abs(self._pos_finish - self._pos_start) / self._fly_time
        if velocity != self._motor.velocity.get():
            self._original_values.remember(self._motor.velocity)
            self._motor.velocity.put(velocity)

        self.status_fly = self._motor.move(self._pos_finish, wait=False)
        self.status_fly.wait(timeout=(self._fly_time + self._fly_time_pad))

        self._original_values.restore()
        self.status_actions_thread.set_finished()


class _ModeFlyer(_MotorFlyer):
    """Make it easier to recover from an exception.  Extends _MotorFlyer()."""

    mode = Component(Signal, value="idle")
    ACTION_MODES = "idle setup taxi fly return".split()

    @run_in_thread
    def actions_thread(self):
        """Run the flyer in a thread."""
        try:
            self._action_setup()
            self._action_taxi()
            self._action_fly()
        except Exception as exc:
            print(f"FlyerError: {exc=}")
        finally:
            self._action_return()
            self.mode.put("idle")

        self.status_actions_thread.set_finished()

    def _action_setup(self):
        """Prepare for the taxi & fly."""
        self.mode.put("setup")
        self.status_taxi = None  # re-created by the taxi move
        self.status_fly = None  # re-created by the fly move
        self._original_values.clear()

    def _action_taxi(self):
        """Move motor to start position."""
        self.mode.put("taxi")
        self.status_taxi = self._motor.move(self._pos_start, wait=False)
        self.status_taxi.wait()
        if self._motor.position != self._pos_start:  # TODO: within tolerance?
            raise FlyerError(
                "Not in requested taxi position:"
                f" requested={self._pos_start}"
                f" position={self._motor.position}"
            )

        velocity = abs(self._pos_finish - self._pos_start) / self._fly_time
        if velocity != self._motor.velocity.get():
            self._original_values.remember(self._motor.velocity)
            self._motor.velocity.put(velocity)

    def _action_fly(self):
        """Start the fly scan and wait for it to complete."""
        self.mode.put("fly")
        allowed_motion_time = self._fly_time + self._fly_time_pad

        # get the motor moving
        self.status_fly = self._motor.move(self._pos_finish, wait=False)

        # wait for motor to be done moving
        self.status_fly.wait(timeout=allowed_motion_time)

    def _action_return(self):
        self.mode.put("return")
        self._original_values.restore()


class _ScalerFlyer(_ModeFlyer):
    """Add the scaler and trigger it for the fly motion.  Extends _ModeFlyer()."""

    def __init__(self, scaler, *args, scaler_time_pad=9, **kwargs):
        if not (
            # fmt: off
            hasattr(scaler, "count")
            and hasattr(scaler, "preset_time")
            and hasattr(scaler, "update_rate")
            # fmt: on
        ):
            raise TypeError(f"Unprepared to handle as scaler: {scaler=}")
        self._scaler = scaler
        self._scaler_time_pad = scaler_time_pad

        super().__init__(*args, **kwargs)

    def _action_fly(self):
        """Start the fly scan and wait for it to complete."""
        self.mode.put("fly")

        motion_time_allowance = self._fly_time + self._fly_time_pad
        count_time_allowance = self._fly_time + self._scaler_time_pad
        self._original_values.remember(self._scaler.count)
        self._original_values.remember(self._scaler.preset_time)
        self._scaler.preset_time.put(count_time_allowance)

        self._scaler.count.put("Count")  # start scaler counting
        time.sleep(1 / self._scaler.update_rate.get())

        # get the motor moving
        self.status_fly = self._motor.move(self._pos_finish, wait=False)

        # wait for motor to be done moving
        self.status_fly.wait(timeout=motion_time_allowance)
        self._scaler.count.put("Done")  # stop scaler counting


class ScalerMotorFlyer(_ScalerFlyer):
    """Add periodic data acquisition.  Extends _ScalerFlyer()."""

    def __init__(self, *args, period=0.1, **kwargs):
        if not (isinstance(period, (float, int)) and period > 0):
            raise FlyerError("Sampling period must be a POSITIVE number: {period=}")

        self._period = period
        self._readings = []
        self.scaler_keys = None

        super().__init__(*args, **kwargs)

    def _action_acquire_event(self, **kwargs):
        """
        Record a single data acquisition event into the internal cache.

        Called by subscription to the scaler's elapsed counting time (CA monitor
        event).  Record the data as it exists when this is called.  Scaler
        timestamps are set from the current time. (Scaler timestamps update
        _only_ once counting has stopped.)
        """
        # read all the data at once
        ts = time.time()
        m_now = self._motor.read()
        s_now = self._scaler.read()

        for v in s_now.values():
            # Scaler timestamps update _only_ once counting has stopped.
            v["timestamp"] = ts  # substitute with current timestamp

        # Build the data acquisition event for collect() method.  Use _counting
        # and _done_moving keys to ID events for successive counter readings.
        event = dict(
            time=ts,
            _counting=self._scaler.count.get(),
            _done_moving=self._motor.motor_done_move.get(),
        )
        event.update(m_now)
        event.update(s_now)

        self._readings.append(event)  # add to internal cache

    def _action_setup(self):
        """Acquire new data at the scaler's update rate."""
        super()._action_setup()

        # try to set the sampling period
        update_rate = 1.0 / self._period
        self._original_values.remember(self._scaler.update_rate)
        self._scaler.update_rate.put(update_rate)
        if round(abs(self._scaler.update_rate.get() - update_rate), 4) > 0.001:
            # this math avoids precision mismatches
            raise FlyerError(
                "Could not get requested scaler sample period:"
                f" requested={self._period}"
                f" received={1/self._scaler.update_rate.get()}"
            )

    def _action_fly(self):
        """
        Start the fly scan and wait for it to complete.

        Data will be accumulated in response to CA monitor events from the
        scaler.
        """

        self.mode.put("fly")

        self._original_values.remember(self._scaler.count)
        self._original_values.remember(self._scaler.preset_time)

        motion_time_allowance = self._fly_time + self._fly_time_pad
        count_time_allowance = self._fly_time + self._scaler_time_pad
        self._scaler.preset_time.put(count_time_allowance)

        # scaler update rate was set in _action_setup()
        self._scaler.time.subscribe(self._action_acquire_event)  # CA monitor

        # start scaler counting, THEN motor moving
        self._scaler.count.put("Count")
        self.status_fly = self._motor.move(self._pos_finish, wait=False)

        # wait for motor to be done moving
        self.status_fly.wait(timeout=motion_time_allowance)
        self._action_acquire_event()  # last event

        self._scaler.count.put("Done")  # stop scaler counting
        self._scaler.time.unsubscribe_all()  # stop acquiring

    def _action_readings_to_collect_events(self):
        """Return the readings as collect() events."""
        motor_keys = list(self._motor.read().keys())
        scaler_keys = list(self._scaler.read().keys())
        all_keys = motor_keys + scaler_keys

        previous = None
        for reading in self._readings:
            if (
                # fmt: off
                previous is not None
                and reading["_counting"]
                and not reading["_done_moving"]
                # fmt: on
            ):
                # reportable event
                ts = reading["time"]
                # fmt: off
                event = dict(
                    time=ts,
                    data={k: None for k in all_keys},
                    timestamps={k: None for k in all_keys},
                )
                # fmt: on
                for k in motor_keys:
                    event["data"][k] = reading[k]["value"]
                    event["timestamps"][k] = reading[k]["timestamp"]
                for k in scaler_keys:
                    # TODO: divide by time increment?
                    delta = reading[k]["value"] - previous[k]["value"]
                    event["data"][k] = delta
                    event["timestamps"][k] = ts
                yield event
            previous = reading.copy()

    def describe_collect(self):
        """Describe the data from collect()."""
        schema = {}
        schema.update(self._motor.describe())
        schema.update(self._scaler.describe())
        return {self.STREAM_NAME: schema}

    def collect(self):
        """Report the collected data."""
        yield from self._action_readings_to_collect_events()

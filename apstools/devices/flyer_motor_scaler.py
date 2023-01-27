"""
Flyers for motor and scaler scans
++++++++++++++++++++++++++++++++++++++++++++

.. rubric:: Public

.. autosummary::
   :recursive:

   ~SignalValueStack
   ~FlyerBase
   ~ActionsFlyerBase
   ~ScalerMotorFlyer

.. rubric:: Private

.. autosummary::
   :recursive:

   ~_SMFlyer_Step_1
   ~_SMFlyer_Step_2
   ~_SMFlyer_Step_3

New in release 1.6.9
"""

import logging
import time

import pysumreg
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import EpicsMotor
from ophyd import Signal
from ophyd.scaler import ScalerCH
from ophyd.status import Status

from ..utils import run_in_thread

logger = logging.getLogger(__name__)


class SignalValueStack:
    """
    Gather a list of (signal, value) pairs to be restored later.

    Signals and values will restored in reverse order from how they were
    pushed to the stack.

    Not a bluesky plan. This is blocking code, intended for use in a separate
    thread from the RunEngine.

    Similar to the ``stage()`` / ``unstage()`` algorithm, an
    instance of ``SignalValueStack()`` records signals and their values
    to be reset once some operations have finished.

    Since any signal cannot be staged twice, or staged from within a running
    plan, we need some support that will save/restore values that are changed
    during a plan's execution.
    Use this for internal operations (such as in a multi-step fly plan)
    to allow original values to be recovered from Signals.

    .. rubric:: Usage

    ::

        from apstools.devices import SignalValueStack
        import ophyd
        signal = ophyd.Signal(name="signal", value=1)
        original = SignalValueStack()

        # ... in the threaded code
        original.remember(signal) # remember the original value
        signal.put(2)  # make some change(s)
        original.restore()  # put it back as we found it
    """

    def __init__(self) -> None:
        self.clear()

    # TODO: Use the 'list' interface?
    def push(self, signal, value):
        """Add a (signal, value) pair on the stack."""
        self._cache.append((signal, value))

    def clear(self):
        """Empty the stack."""
        self._cache = []

    def remember(self, signal):
        """Push the signal's value on the stack."""
        self.push(signal, signal.get())

    def restore(self):
        """Write the signals in the stack, in reverse order."""
        for pair in reversed(self._cache):
            pair[0].put(pair[-1])
        self._cache = []


class FlyerBase(Device):
    """
    Canonical ophyd Flyer object.  Acquires one empty data event.
    """

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
        """Describe the data from :meth:`~collect()`."""
        logging.debug("describe_collect()")
        schema = {}
        return {self.STREAM_NAME: schema}

    def collect(self):
        """Data event(s)."""
        logging.debug("collect()")
        event = dict(time=time.time(), data={}, timestamps={})
        yield event


class ActionsFlyerBase(FlyerBase):
    """
    Call :meth:`~actions_thread` method from :meth:`~kickoff`.

    Method :meth:`~actions_thread()` will describe all the fly scan steps.
    Method :meth:`~collect` is changed to wait for :meth:`~actions_thread`
    to complete before signalling that the flyer is complete and data is ready
    to :meth:`~collect`.

    In :meth:`~actions_thread()`, wait for all fly scan actions to complete,
    then mark the status object as finished before returning.
    """

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

    def actions_thread(self):
        """
        Run the flyer in a thread.  Not a bluesky plan.

        Any acquired data should be saved internally and yielded from
        :meth:`~collect`.  (Remember to modify :meth:`~describe_collect` for
        any changes in the structure of data yielded by :meth:`~collect`!)
        """

        @run_in_thread
        def example_action():
            logging.debug("in actions thread")
            time.sleep(1)  # as a demonstration of a slow action
            self.status_actions_thread.set_finished()
            logging.debug("actions thread marked 'finished'")

        example_action()


class _SMFlyer_Step_1(ActionsFlyerBase):
    """
    Add a motor to ActionsFlyerBase().

    .. rubric:: Parameters

    motor
        *object* :
        Instance of :class:`ophyd.EpicsMotor`.
    start
        *float* or *int* :
        Fly scan will begin at this motor position.
    finish
        *float* or *int* :
        Fly scan will end at this motor position.
    fly_time
        *float* or *int* :
        Time (seconds, approximate) for fly scan to traverse from 'start' to
        'finish'.  The motor velocity will be set to meet this parameter.
        (Default: 1 s)
    fly_time_pad
        *float* or *int* :
        Extra time (seconds) to allow the fly scan to finish before a fly
        scan timeout is declared.
        (Default: 10 s)

    .. note:: This class is used internally to build, in steps,
        :class:`~ScalerMotorFlyer` from :class:`~ActionsFlyerBase`.
    """

    def __init__(self, motor, start, finish, *args, fly_time=1, fly_time_pad=10, **kwargs):
        fly_time = fly_time or 1
        fly_time_pad = fly_time_pad or 2
        if not hasattr(motor, "velocity"):
            raise TypeError(f"Unprepared to handle as motor: {motor=}")
        if fly_time <= 0:
            raise ValueError(f"Must be a POSITIVE number: {fly_time=}")
        if fly_time_pad <= 0:
            raise ValueError(f"Must be a POSITIVE number: {fly_time_pad=}")

        self.motor = motor
        self.pos_start = start
        self.pos_finish = finish
        self.fly_time = fly_time
        self.fly_time_pad = fly_time_pad

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

        @run_in_thread
        def example_fly_scan():
            self.status_taxi = self.motor.move(self.pos_start, wait=False)
            self.status_taxi.wait()

            # arrived to within motor's precision?
            if round(
                self._motor.position - self._pos_start,
                self._motor.precision
            ) != 0:
                raise RuntimeError(
                    "Not in requested taxi position:"
                    f" requested={self.pos_start}"
                    f" position={self.motor.position}"
                )

            velocity = abs(self.pos_finish - self.pos_start) / self.fly_time
            if velocity != self.motor.velocity.get():
                self._original_values.remember(self.motor.velocity)
                self.motor.velocity.put(velocity)

            self.status_fly = self.motor.move(self.pos_finish, wait=False)
            self.status_fly.wait(timeout=(self.fly_time + self.fly_time_pad))

            self._original_values.restore()
            self.status_actions_thread.set_finished()

        example_fly_scan()

    @property
    def motor(self):
        return self._motor

    @motor.setter
    def motor(self, obj):
        if not isinstance(obj, EpicsMotor):
            raise TypeError(
                "Expected instance of 'ophyd.EpicsMotor'."
                f"  Received: {type(obj)}"
            )
        self._motor = obj

    @property
    def pos_start(self):
        return self._pos_start

    @pos_start.setter
    def pos_start(self, value):
        self._pos_start = value

    @property
    def pos_finish(self):
        return self._pos_finish

    @pos_finish.setter
    def pos_finish(self, value):
        self._pos_finish = value

    @property
    def fly_time(self):
        return self._fly_time

    @fly_time.setter
    def fly_time(self, value):
        if value <= 0:
            raise ValueError(f"Value must be greater than zero.  Received: {value}")
        self._fly_time = value

    @property
    def fly_time_pad(self):
        return self._fly_time_pad

    @fly_time_pad.setter
    def fly_time_pad(self, value):
        if value < 0:
            raise ValueError(f"Value must not be negative.  Received: {value}")
        self._fly_time_pad = value


class _SMFlyer_Step_2(_SMFlyer_Step_1):
    """
    Add modes (states) to _SMFlyer_Step_1() to recover from exceptions.

    Overrides :meth:`~actions_thread()` to recover from exceptions and restore
    previous values.  Since exceptions from threaded code are not reported
    through to the RunEgine (the thread simply stops for unhandled exceptions),
    the override handles such exceptions and then restores any signals to
    original values, as recorded via use of :class:`~SignalValueStack`. Here's
    the algorithm::

        try
            setup, taxi, then fly
        except Exception
            report the exception and save as attribute
        finally
            restore and return to idle

        mark status finished

    .. note:: This class is used internally to build, in steps,
        :class:`~ScalerMotorFlyer` from :class:`~ActionsFlyerBase`.
    """

    mode = Component(Signal, value="idle")
    ACTION_MODES = "idle setup taxi fly return".split()
    action_exception = None

    def actions_thread(self):
        """Run the flyer in a thread."""

        @run_in_thread
        def fly_scan_workflow():
            self.action_exception = None
            try:
                self._action_setup()
                self._action_taxi()
                self._action_fly()
            except Exception as exc:
                self.action_exception = exc
                logger.exception("Flyer Error")
                print(f"Flyer Error: {exc=}")
            finally:
                self._action_return()
                self.mode.put("idle")

            self.status_actions_thread.set_finished()

        fly_scan_workflow()

    def _action_setup(self):
        """Prepare for the taxi & fly."""
        self.mode.put("setup")
        self.status_taxi = None  # re-created by the taxi move
        self.status_fly = None  # re-created by the fly move
        self._original_values.clear()

    def _action_taxi(self):
        """Move motor to start position."""
        self.mode.put("taxi")
        self.status_taxi = self.motor.move(self.pos_start, wait=False)
        self.status_taxi.wait()

        # arrived to within motor's precision?
        if round(
            self._motor.position - self._pos_start,
            self._motor.precision
        ) != 0:
            raise RuntimeError(
                "Not in requested taxi position:"
                f" requested={self.pos_start}"
                f" position={self.motor.position}"
            )

    def _action_fly(self):
        """Start the fly scan and wait for it to complete."""
        self.mode.put("fly")

        # set the fly scan velocity
        velocity = abs(self.pos_finish - self.pos_start) / self.fly_time
        if velocity != self.motor.velocity.get():
            self._original_values.remember(self.motor.velocity)
            self.motor.velocity.put(velocity)

        # get the motor moving
        self.status_fly = self.motor.move(self.pos_finish, wait=False)

        # wait for motor to be done moving
        allowed_motion_time = self.fly_time + self.fly_time_pad
        self.status_fly.wait(timeout=allowed_motion_time)

    def _action_return(self):
        """Restore original values."""
        self.mode.put("return")
        self._original_values.restore()


class _SMFlyer_Step_3(_SMFlyer_Step_2):
    """
    Add a scaler to _SMFlyer_Step_2() and trigger it for the fly motion.

    .. rubric:: Parameters

    scaler
        *object* :
        Instance of :class:`ophyd.scaler.ScalerCH`.
    scaler_time_pad
        *float* or *int* :
        Extra time (seconds) to leave the scaler counting before a fly scan
        timeout is declared.
        (Default: 2 s)

    .. note:: This class is used internally to build, in steps,
        :class:`~ScalerMotorFlyer` from :class:`~ActionsFlyerBase`.
    """

    def __init__(self, scaler, *args, scaler_time_pad=2, **kwargs):
        if not (
            # fmt: off
            hasattr(scaler, "count")
            and hasattr(scaler, "preset_time")
            and hasattr(scaler, "update_rate")
            # fmt: on
        ):
            raise TypeError(f"Unprepared to handle as scaler: {scaler=}")
        self.scaler = scaler
        self.scaler_time_pad = scaler_time_pad

        super().__init__(*args, **kwargs)

    def _action_fly(self):
        """Start the fly scan and wait for it to complete."""
        self.mode.put("fly")

        motion_time_allowance = self.fly_time + self.fly_time_pad
        count_time_allowance = self.fly_time + self.scaler_time_pad
        self._original_values.remember(self.scaler.count)
        self._original_values.remember(self.scaler.preset_time)
        self._original_values.remember(self.scaler.count_mode)
        self.scaler.preset_time.put(count_time_allowance)
        self.scaler.count_mode.put("OneShot")
        self.scaler.count.put("Done")

        self.scaler.count.put("Count")  # start scaler counting
        time.sleep(1 / self.scaler.update_rate.get())

        # get the motor moving
        self.status_fly = self.motor.move(self.pos_finish, wait=False)

        # wait for motor to be done moving
        self.status_fly.wait(timeout=motion_time_allowance)
        self.scaler.count.put("Done")  # stop scaler counting

    @property
    def scaler(self):
        return self._scaler

    @scaler.setter
    def scaler(self, obj):
        if not isinstance(obj, ScalerCH):
            raise TypeError(
                "Expected instance of 'ophyd.scaler.ScalerCH'."
                f"  Received: {type(obj)}"
            )
        self._scaler = obj

    @property
    def scaler_time_pad(self):
        return self._scaler_time_pad

    @scaler_time_pad.setter
    def scaler_time_pad(self, value):
        if value < 0:
            raise ValueError(f"Value must not be negative.  Received: {value}")
        self._scaler_time_pad = value


class ScalerMotorFlyer(_SMFlyer_Step_3):
    """
    Motor and scaler flyer, moving at constant velocity.

    Built from the :class:`~ActionsFlyerBase`, the
    :class:`~ScalerMotorFlyer` runs a fly scan described
    in :meth:`~actions_thread`.

    .. rubric:: Parameters

    period
        *float* or *int* :
        Time (seconds) between successive (starts of) data collection events.
        (Default: 0.1 s)

    Extends :class:`SMFlyer__Step_3()`, adding periodic data acquisition.

    .. rubric:: How to change parameters?

    Start, finish, and other parameters may be changed after the flyer object
    has been created. These properties may be changed after the flyer object has
    been created (but before a fly scan has started):

    ====================  ======  ===========================
    property              type    description
    ====================  ======  ===========================
    ``motor``             object  Instance (not the name) of ``EpicsMotor``.
    ``scaler``            object  Instance (not the name) of ``ScalerCH``.
    ``fly_time``          float   Fly scan duration (seconds). Time to move ``motor`` from start to finish.
    ``pos_start``         float   Starting position of the fly scan.
    ``pos_finish``        float   Finishing position of the fly scan.
    ``period``            float   Sampling period (s); time between (starts of) scaler readings.
    ``fly_time_pad``      float   Extra time (s) allowed for motion to reach finish.
    ``scaler_time_pad``   float   Extra time (s) allowed for scaler to finish counting.
    ====================  ======  ===========================

    For a flyer object named ``flyer``, change the fly time to 120 s::

        flyer.fly_time = 120

    .. autosummary::

        ~_action_acquire_event
        ~_action_setup
        ~_action_fly
        ~_action_readings_to_collect_events
        ~describe_collect
        ~collect
    """

    def __init__(self, *args, period=None, **kwargs):
        period = period or 0.1
        if period <= 0:
            raise ValueError(
                f"Sampling period must be a POSITIVE number: {period=}"
            )

        self.period = period
        self._readings = []
        self.scaler_keys = None
        self.stats = None

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
        m_now = self.motor.read()
        s_now = self.scaler.read()

        for v in s_now.values():
            # Scaler timestamps update _only_ once counting has stopped.
            v["timestamp"] = ts  # substitute with current timestamp

        # Build the data acquisition event for collect() method.  Use _counting
        # and _done_moving keys to ID events for successive counter readings.
        event = dict(
            time=ts,
            _counting=self.scaler.count.get(),
            _done_moving=self.motor.motor_done_move.get(),
        )
        event.update(m_now)
        event.update(s_now)

        self._readings.append(event)  # add to internal cache

    def _action_setup(self):
        """Acquire new data at the scaler's update rate."""
        super()._action_setup()

        # try to set the sampling period
        expected_period = round(self.period, 5)
        self._original_values.remember(self.scaler.update_rate)
        self.scaler.update_rate.put(1 / self.period)
        received_period = round(
            1 / self.scaler.update_rate.get(use_monitor=False), 5
        )
        if received_period != expected_period:
            raise ValueError(
                "Could not get requested scaler sample period:"
                f" requested={self.period}"
                f" received={received_period}"
            )

        self.stats = None

    def _action_fly(self):
        """
        Start the fly scan and wait for it to complete.

        Data will be accumulated in response to CA monitor events from the
        scaler.
        """

        self.mode.put("fly")

        # set the fly scan velocity
        velocity = abs(self.pos_finish - self.pos_start) / self.fly_time
        if velocity != self.motor.velocity.get():
            self._original_values.remember(self.motor.velocity)
            self.motor.velocity.put(velocity)

        # set the scaler count time (allowance)
        self._original_values.remember(self.scaler.preset_time)
        count_time_allowance = self.fly_time + self.scaler_time_pad
        self.scaler.preset_time.put(count_time_allowance)

        # start acquiring, scaler update rate was set in _action_setup()
        self.scaler.time.subscribe(self._action_acquire_event)  # CA monitor

        # start scaler counting, THEN motor moving
        self._original_values.remember(self.scaler.count)
        self._original_values.remember(self.scaler.count_mode)
        self.scaler.count_mode.put("OneShot")
        self.scaler.count.put("Done")
        self.scaler.count.put("Count")
        self.status_fly = self.motor.move(self.pos_finish, wait=False)

        # wait for motor to be done moving
        motion_time_allowance = self.fly_time + self.fly_time_pad
        self.status_fly.wait(timeout=motion_time_allowance)
        self._action_acquire_event()  # last event

        self.scaler.count.put("Done")  # stop scaler counting
        self.scaler.time.unsubscribe_all()  # stop acquiring

    def _action_readings_to_collect_events(self):
        """Return the readings as collect() events."""
        motor_keys = list(self.motor.read().keys())
        scaler_keys = list(self.scaler.read().keys())
        all_keys = motor_keys + scaler_keys
        self.stats = {k: pysumreg.SummationRegisters() for k in scaler_keys}

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

                # use first motor reading is the one to use
                x_value = reading[motor_keys[0]]["value"]
                for k in scaler_keys:
                    # TODO: consider divide by time increment
                    delta = reading[k]["value"] - previous[k]["value"]
                    event["data"][k] = delta
                    event["timestamps"][k] = ts
                    self.stats[k].add(x_value, delta)

                yield event
            previous = reading.copy()

    def describe_collect(self):
        """Describe the data from collect()."""
        schema = {}
        schema.update(self.motor.describe())
        schema.update(self.scaler.describe())
        return {self.STREAM_NAME: schema}

    def collect(self):
        """Report the collected data."""
        from bluesky import plan_stubs as bps

        from . import make_dict_device

        yield from self._action_readings_to_collect_events()

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if value <= 0:
            raise ValueError(f"Value must be greater than zero.  Received: {value}")
        self._period = value

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2023, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

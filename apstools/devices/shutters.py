"""
Shutters
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsPssShutter
   ~ApsPssShutterWithStatus
   ~EpicsMotorShutter
   ~EpicsOnOffShutter
   ~OneSignalShutter
   ~ShutterBase
   ~SimulatedApsPssShutterWithStatus
"""

import threading
import time

import numpy as np
from deprecated.sphinx import versionchanged
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent
from ophyd import Signal


@versionchanged(version="1.7.6", reason="add kwargs to __init__()")
class ShutterBase(Device):
    """
    Base class for all shutter Devices.

    .. index:: Ophyd Device; ShutterBase

    PARAMETERS

    value *str* :
        any from ``self.choices`` (typically "open" or "close")

    valid_open_values *list[str]* :
        A list of lower-case text values that are acceptable
        for use with the ``set()`` command to open the shutter.

    valid_close_values *list[str]* :
        A list of lower-case text values that are acceptable
        for use with the ``set()`` command to close the shutter.

    open_value *number* :
        The actual value to send to open ``signal`` to open the shutter.
        (default = 1)

    close_value *number* :
        The actual value to send to close ``signal`` to close the shutter.
        (default = 0)

    delay_s *float* :
        time to wait (s) after move is complete,
        does not wait if shutter already in position
        (default = 0)

    busy *Signal* :
        (internal) tells if a move is in progress

    unknown_state *str* :
        (constant) Text reported by ``state`` when not open or closed.
        cannot move to this position
        (default = "unknown")

    name *str* :
        (kwarg, required) object's canonical name
    """

    busy = Component(Signal, value=False)
    """True if a move is in progress."""

    unknown_state: str = "unknown"  # cannot move to this position
    """
    Text reported by 'state' when not open or closed. Cannot move to this
    position. (default = "unknown")
    """

    # - - - - likely to override these methods in subclass - - - -

    def open(self) -> None:
        """
        BLOCKING: request shutter to open, called by ``set()``.

        Must implement in subclass of ShutterBase()

        EXAMPLE::

            if not self.isOpen:
                self.signal.put(self.open_value)
                if self.delay_s > 0:
                    time.sleep(self.delay_s)    # blocking call OK here

        """
        raise NotImplementedError("must implement in subclass")

    def close(self) -> None:
        """
        BLOCKING: request shutter to close, called by ``set()``.

        Must implement in subclass of ShutterBase()

        EXAMPLE::

            if not self.isClosed:
                self.signal.put(self.close_value)
                if self.delay_s > 0:
                    time.sleep(self.delay_s)    # blocking call OK here

        """
        raise NotImplementedError("must implement in subclass")

    @property
    def state(self) -> str:
        """
        returns ``open``, ``close``, or ``unknown``

        Must implement in subclass of ShutterBase()

        EXAMPLE::

            if self.signal.get() == self.open_value:
                result = self.valid_open_values[0]
            elif self.signal.get() == self.close_value:
                result = self.valid_close_values[0]
            else:
                result = self.unknown_state
            return result

        """
        raise NotImplementedError("must implement in subclass")

    # - - - - - - possible to override in subclass - - - - - -

    def __init__(
        self,
        *args,
        open_value: int = 1,
        close_value: int = 0,
        valid_open_values: list[str] = ["open", "opened"],  # lower-case strings ONLY
        valid_close_values: list[str] = ["close", "closed"],
        delay_s: float = 1.2,
        **kwargs,
    ):
        self.delay_s = delay_s  # allow time for shutter to move
        self.open_value = open_value
        self.close_value = close_value
        self.valid_open_values = [str(v).lower() for v in valid_open_values]
        self.valid_close_values = [str(v).lower() for v in valid_close_values]

        super().__init__(*args, **kwargs)

        # TODO: Remove this belt-and-suspenders code?
        # self.valid_open_values = list(map(self.lowerCaseString, self.valid_open_values))
        # self.valid_close_values = list(map(self.lowerCaseString, self.valid_close_values))

    @property
    def isOpen(self) -> bool:
        """is the shutter open?"""
        return str(self.state) == self.valid_open_values[0]

    @property
    def isClosed(self) -> bool:
        """is the shutter closed?"""
        return str(self.state) == self.valid_close_values[0]

    def inPosition(self, target) -> bool:
        """is the shutter at the target position?"""
        self.validTarget(target)
        __value__ = self.lowerCaseString(target)
        if __value__ in self.valid_open_values and self.isOpen:
            return True
        elif __value__ in self.valid_close_values and self.isClosed:
            return True
        return False

    def set(self, value, **kwargs):
        """
        plan: request the shutter to open or close

        PARAMETERS

        value
            *str* :
            any from ``self.choices`` (typically "open" or "close")

        kwargs
            *dict* :
            ignored at this time

        """
        if self.busy.get():
            raise RuntimeError("shutter is operating")

        __value__ = self.lowerCaseString(value)
        self.validTarget(__value__)

        status = DeviceStatus(self)

        if self.inPosition(__value__):
            # no need to move, cut straight to the end
            status._finished(success=True)
        else:

            def move_it():
                # runs in a thread, no need to "yield from"
                self.busy.put(True)
                if __value__ in self.valid_open_values:
                    self.open()
                elif __value__ in self.valid_close_values:
                    self.close()
                self.busy.put(False)
                status._finished(success=True)

            # get it moving
            threading.Thread(target=move_it, daemon=True).start()
        return status

    # - - - - - - not likely to override in subclass - - - - - -

    def addCloseValue(self, text) -> list[str]:
        """a synonym to close the shutter, use with set()"""
        self.valid_close_values.append(self.lowerCaseString(text))
        return self.choices  # return the list of acceptable values

    def addOpenValue(self, text) -> list[str]:
        """a synonym to open the shutter, use with set()"""
        self.valid_open_values.append(self.lowerCaseString(text))
        return self.choices  # return the list of acceptable values

    @property
    def choices(self):
        """return list of acceptable choices for set()"""
        return self.valid_open_values + self.valid_close_values

    def lowerCaseString(self, value) -> str:
        """ensure any given value is a lower-case string"""
        return str(value).lower()

    def validTarget(self, target: str, should_raise: bool =True):
        """
        return whether (or not) target value is acceptable for self.set()

        raise ValueError if not acceptable (default)
        """
        acceptable_values = self.choices
        ok = self.lowerCaseString(target) in acceptable_values
        if not ok and should_raise:
            raise ValueError(
                f"received {target!r}"
                # .
                f" : should be only one of {' | '.join(acceptable_values)}"
            )
        return ok


class OneSignalShutter(ShutterBase):
    """
    Shutter Device using one Signal for open and close.

    .. index:: Ophyd Device; OneSignalShutter

    PARAMETERS

    signal
        ``EpicsSignal`` or ``Signal`` :
        (override in subclass)
        The ``signal`` is the comunication to the hardware.
        In a subclass, the hardware may have more than
        one communication channel to use.  See the
        ``ApsPssShutter`` as an example.

    name
        *str* :
        (kwarg, required) object's canonical name

    See ``ShutterBase`` for more parameters.

    EXAMPLE

    Create a simulated shutter:

        shutter = OneSignalShutter(name="shutter")

    open the shutter (interactively):

        shutter.open()

    Check the shutter is open:

        In [144]: shutter.isOpen
        Out[144]: True

    Use the shutter in a Bluesky plan.
    Set a post-move delay time of 1.0 seconds.
    Be sure to use ``yield from``, such as::

        def in_a_plan(shutter):
            shutter.delay_s = 1.0
            t0 = time.time()
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.abs_set(shutter, "open", wait=True)    # wait for completion is optional
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.mv(shutter, "open")    # do it again
            print("Shutter state: " + shutter.state, time.time()-t0)
            yield from bps.mv(shutter, "close")    # ALWAYS waits for completion
            print("Shutter state: " + shutter.state, time.time()-t0)

        RE(in_a_plan(shutter))

    which gives this output:

        Shutter state: close 1.7642974853515625e-05
        Shutter state: open 1.0032124519348145
        Shutter state: open 1.0057861804962158
        Shutter state: close 2.009695529937744

    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.

    Example, add "o" & "x" as aliases for "open" & "close":

        shutter.addOpenValue("o")
        shutter.addCloseValue("x")
        shutter.set("o")
        shutter.set("x")
    """

    signal = Component(Signal, value=0)

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        if self.signal.get() == self.open_value:
            result = self.valid_open_values[0]
        elif self.signal.get() == self.close_value:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result

    def open(self):
        """BLOCKING: request shutter to open, called by set()"""
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

    def close(self):
        """BLOCKING: request shutter to close, called by set()"""
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here


@versionchanged(version="1.7.6", reason="add kwargs to __init__()")
class ApsPssShutter(ShutterBase):
    """
    APS PSS shutter

    .. index:: Ophyd Device; ApsPssShutter

    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
      (see :func:`ApsPssShutterWithStatus()` for alternative)

    Since there is no direct indication that a shutter has moved, the
    ``state`` property will always return *unknown* and the
    ``isOpen`` and ``isClosed`` properties will always return *False*.

    A consequence of the unknown state is that the shutter will always
    be commanded to move (and wait the ``delay_s`` time),
    even if it is already at that position.  This device could keep
    track of the last commanded position, but that is not guaranteed
    to be true since the shutter could be moved from other software.

    The default ``delay_s`` has been set at *1.2 s* to allow for
    shutter motion.  Change this as desired.  Advise if this
    default should be changed.

    PARAMETERS

    prefix *str* :
        EPICS PV prefix

    name *str* :
        (kwarg, required) object's canonical name

    close_pv *str* :
        (kwarg, optional) Name of EPICS PV to close the shutter.
        If ``None``, defaults to ``"{prefix}Close"``.

    open_pv *str* :
        (kwarg, optional) Name of EPICS PV to open the shutter.
        If ``None``, defaults to ``"{prefix}Open"``.

    open_reset_value: *int* :
        To open, set 'self.open_signal' to this value.  Default = 1.

    close_reset_value: *int* :
        To open, set 'self.close_signal' to this value.  Default = 1.

    open_reset_value: *int* :
        To reset 'self.open_signal', set to this value.  Default = 0.

    close_reset_value: *int* :
        To reset 'self.close_signal', set to this value.  Default = 0.

    EXAMPLE::

        shutter_a = ApsPssShutter("2bma:A_shutter:", name="shutter")
        shutter_a.wait_for_connection()

        shutter_a.open()
        shutter_a.close()

        shutter_a.set("open")
        shutter_a.set("close")

    When using the shutter in a plan, be sure to use ``yield from``, such as::

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)

        RE(in_a_plan(shutter_a))

    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.

    Example, add "o" & "x" as aliases for "open" & "close":

        shutter_a.addOpenValue("o")
        shutter_a.addCloseValue("x")
        shutter_a.set("o")
        shutter_a.set("x")
    """

    # bo records that reset after a short time, set to 1 to move
    # note: upper-case first characters here (unique to 9-ID)?
    open_signal = FormattedComponent(EpicsSignal, "{self.open_pv}")
    close_signal = FormattedComponent(EpicsSignal, "{self.close_pv}")

    def __init__(
        self,
        prefix: str,
        *args,
        close_pv: str = None,
        open_pv: str = None,
        open_value: int = 1,
        close_value: int = 1,
        open_reset_value: int = 0,
        close_reset_value: int = 0,
        **kwargs,
    ):
        """."""
        self.open_pv = open_pv or f"{prefix}Open"
        self.close_pv = close_pv or f"{prefix}Close"
        self.open_reset_value = open_reset_value
        self.close_reset_value = close_reset_value

        super().__init__(
            prefix,
            *args,
            open_value=open_value,
            close_value=close_value,
            **kwargs,
        )

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        return self.unknown_state  # no state info available

    def open(self, timeout=10) -> None:
        """request the shutter to open (timeout is ignored)"""
        if not self.isOpen:
            self.open_signal.put(self.open_value)

            # wait for the shutter to move
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

            # reset that signal (if not done by EPICS)
            if self.open_signal.get() == self.open_value:
                self.open_signal.put(self.open_reset_value)

    def close(self, timeout=10) -> None:
        """request the shutter to close (timeout is ignored)"""
        if not self.isClosed:
            self.close_signal.put(self.close_value)

            # wait for the shutter to move
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

            # reset that signal (if not done by EPICS)
            if self.close_signal.get() == self.close_value:
                self.close_signal.put(self.close_reset_value)


class ApsPssShutterWithStatus(ApsPssShutter):
    """
    APS PSS shutter with separate status PV

    .. index:: Ophyd Device; ApsPssShutterWithStatus

    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
      (see :func:`ApsPssShutter()` for alternative)

    PARAMETERS

    prefix *str* :
        EPICS PV prefix

    state_pv *str* :
        Name of EPICS PV that provides shutter's current state.

    name *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        A_shutter = ApsPssShutterWithStatus(
            "2bma:A_shutter:",
            "PA:02BM:STA_A_FES_OPEN_PL",
            name="A_shutter")
        B_shutter = ApsPssShutterWithStatus(
            "2bma:B_shutter:",
            "PA:02BM:STA_B_SBS_OPEN_PL",
            name="B_shutter")
        A_shutter.wait_for_connection()
        B_shutter.wait_for_connection()

        A_shutter.open()
        A_shutter.close()

        or

        A_shutter.set("open")
        A_shutter.set("close")

    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)

        RE(in_a_plan(A_shutter))

    """

    # bi record ZNAM=OFF, ONAM=ON
    pss_state = FormattedComponent(EpicsSignalRO, "{self.state_pv}")
    pss_state_open_values = [1]
    pss_state_closed_values = [0]

    _poll_factor_: float = 1.5
    _poll_s_min_: float = 0.002
    _poll_s_max_: float = 0.15

    def __init__(self, prefix, state_pv: str, *args, **kwargs):
        self.state_pv: str = state_pv
        super().__init__(prefix, *args, **kwargs)

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        # update the list of acceptable values - very inefficient but works
        for item in self.pss_state.enum_strs[1]:
            if item not in self.pss_state_open_values:
                self.pss_state_open_values.append(item)
        for item in self.pss_state.enum_strs[0]:
            if item not in self.pss_state_closed_values:
                self.pss_state_closed_values.append(item)

        if self.pss_state.get() in self.pss_state_open_values:
            result = self.valid_open_values[0]
        elif self.pss_state.get() in self.pss_state_closed_values:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result

    def wait_for_state(self, target, timeout=10, poll_s=0.01) -> None:
        """
        wait for the PSS state to reach a desired target

        PARAMETERS

        (kwarg, optional) Name of EPICS PV to close the shutter.
        If ``None``, defaults to ``"{prefix}Close"``.

        target
            *[str]* :
            list of strings containing acceptable values

        timeout
            *non-negative number* :
            (kwarg, optional) Maximum amount of time (seconds) to wait for PSS
            state to reach target. If ``None``, defaults to ``10``.

        poll_s
            *non-negative number* :
            (kwarg, optional) Time to wait (seconds) in first polling cycle.
            After first poll, this will be increased by ``_poll_factor_``
            up to a maximum time of ``_poll_s_max_``.
            If ``None``, defaults to ``0.01``.
        """
        if timeout is not None:
            expiration = time.time() + max(timeout, 0)  # ensure non-negative timeout
        else:
            expiration = None

        # ensure the poll delay is reasonable
        if poll_s > self._poll_s_max_:
            poll_s = self._poll_s_max_
        elif poll_s < self._poll_s_min_:
            poll_s = self._poll_s_min_

        while self.pss_state.get() not in target:
            time.sleep(poll_s)
            if poll_s < self._poll_s_max_:
                poll_s *= self._poll_factor_  # progressively longer
            if expiration is not None and time.time() > expiration:
                msg = f"Timeout ({timeout} s) waiting for shutter state"
                msg += f" to reach a value in {target}"
                raise TimeoutError(msg)

    def open(self, timeout=10) -> None:
        """request the shutter to open"""
        if not self.isOpen:
            self.open_signal.put(self.open_value)

            # wait for the shutter to move
            self.wait_for_state(self.pss_state_open_values, timeout=timeout)

            # wait as caller specified
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

            # reset that signal (if not done by EPICS)
            if self.open_signal.get() == self.open_value:
                self.open_signal.put(self.open_reset_value)

    def close(self, timeout=10) -> None:
        """request the shutter to close"""
        if not self.isClosed:
            self.close_signal.put(1)

            # wait for the shutter to move
            self.wait_for_state(self.pss_state_closed_values, timeout=timeout)

            # wait as caller specified
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

            # reset that signal (if not done by EPICS)
            if self.close_signal.get() == 1:
                self.close_signal.put(0)


class SimulatedApsPssShutterWithStatus(ApsPssShutterWithStatus):
    """
    Simulated APS PSS shutter

    .. index:: Ophyd Device; SimulatedApsPssShutterWithStatus

    PARAMETERS

    prefix *str* :
        EPICS PV prefix

    name *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        sim = SimulatedApsPssShutterWithStatus(name="sim")

    """

    open_signal = Component(Signal, value=0)
    close_signal = Component(Signal, value=0)
    pss_state = FormattedComponent(Signal, value="close")

    def __init__(self, *args, **kwargs):
        super(SimulatedApsPssShutterWithStatus, self).__init__("", "", *args, **kwargs)
        self.pss_state_open_values += self.valid_open_values
        self.pss_state_closed_values += self.valid_close_values

    def wait_for_state(self, target, timeout=10, poll_s=0.01) -> None:
        """
        wait for the PSS state to reach a desired target

        PARAMETERS

        target
            *[str]* :
            list of strings containing acceptable values

        timeout
            *non-negative number* :
            Ignored in the simulation.

        poll_s
            *non-negative number* :
            Ignored in the simulation.
        """
        simulated_response_time_s = np.random.uniform(0.1, 0.9)
        time.sleep(simulated_response_time_s)
        self.pss_state.put(target[0])

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        if self.pss_state.get() in self.pss_state_open_values:
            result = self.valid_open_values[0]
        elif self.pss_state.get() in self.pss_state_closed_values:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result


@versionchanged(version="1.7.6", reason="add tolerance kwarg to __init__()")
class EpicsMotorShutter(OneSignalShutter):
    """
    Shutter, implemented with an EPICS motor moved between two positions

    .. index:: Ophyd Device; EpicsMotorShutter

    PARAMETERS

    prefix *str* :
        EPICS PV prefix

    name *str* :
        (kwarg, required) object's canonical name

    tolerance *float* :
        Used to decide in-position: abs(readback-setpoint) <= tolerance.

    EXAMPLE::

        tomo_shutter = EpicsMotorShutter("2bma:m23", name="tomo_shutter")
        tomo_shutter.wait_for_connection()
        tomo_shutter.close_value = 1.0      # default
        tomo_shutter.open_value = 0.0       # default
        tomo_shutter.tolerance = 0.01       # default
        tomo_shutter.open()
        tomo_shutter.close()

        # or, when used in a plan
        def planA():
            yield from abs_set(tomo_shutter, "open", group="O")
            yield from wait("O")
            yield from abs_set(tomo_shutter, "close", group="X")
            yield from wait("X")
        def planA():
            yield from abs_set(tomo_shutter, "open", wait=True)
            yield from abs_set(tomo_shutter, "close", wait=True)
        def planA():
            yield from mv(tomo_shutter, "open")
            yield from mv(tomo_shutter, "close")

    """

    signal = Component(EpicsMotor, "")

    def __init__(
        self,
        *args,
        tolerance: float = 0.01,  # how close is considered in-position?
        **kwargs,
    ):
        self.tolerance = tolerance
        super().__init__(*args, **kwargs)

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        if abs(self.signal.user_readback.get() - self.open_value) <= self.tolerance:
            result = self.valid_open_values[0]
        elif abs(self.signal.user_readback.get() - self.close_value) <= self.tolerance:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result

    def open(self) -> None:
        """move motor to BEAM NOT BLOCKED position, interactive use"""
        if not self.isOpen:
            self.signal.move(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here

    def close(self) -> None:
        """move motor to BEAM BLOCKED position, interactive use"""
        self.signal.move(self.close_value)
        if not self.isClosed:
            self.signal.move(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)  # blocking call OK here


class EpicsOnOffShutter(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutter

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix *str* :
        EPICS PV prefix

    name *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutter("2bma:bit1", name="bit_shutter")
        bit_shutter.wait_for_connection()
        bit_shutter.close_value = 0      # default
        bit_shutter.open_value = 1       # default
        bit_shutter.open()
        bit_shutter.close()

        # or, when used in a plan
        def planA():
            yield from mv(bit_shutter, "open")
            yield from mv(bit_shutter, "close")

    """

    signal = Component(EpicsSignal, "")


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

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
from typing import Any, Dict, List, Optional, Union

import numpy as np
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent
from ophyd import Signal


class ShutterBase(Device):
    """
    Base class for all shutter Devices.

    .. index:: Ophyd Device; ShutterBase

    PARAMETERS

    value
        *str* :
        any from ``self.choices`` (typically "open" or "close")

    valid_open_values
        *[str]* :
        A list of lower-case text values that are acceptable
        for use with the ``set()`` command to open the shutter.

    valid_close_values
        *[str]* :
        A list of lower-case text values that are acceptable
        for use with the ``set()`` command to close the shutter.

    open_value
        *number* :
        The actual value to send to open ``signal`` to open the shutter.
        (default = 1)

    close_value
        *number* :
        The actual value to send to close ``signal`` to close the shutter.
        (default = 0)

    delay_s
        *float* :
        time to wait (s) after move is complete,
        does not wait if shutter already in position
        (default = 0)

    busy
        *Signal* :
        (internal) tells if a move is in progress

    unknown_state
        *str* :
        (constant) Text reported by ``state`` when not open or closed.
        cannot move to this position
        (default = "unknown")

    name
        *str* :
        (kwarg, required) object's canonical name
    """

    # fmt: off
    valid_open_values: List[str] = ["open", "opened"]  # lower-case strings ONLY
    valid_close_values: List[str] = ["close", "closed"]
    # fmt: on
    open_value: int = 1  # value of "open"
    close_value: int = 0  # value of "close"
    delay_s: float = 0.0  # time to wait (s) after move is complete
    busy: Signal = Component(Signal, value=False)
    unknown_state: str = "unknown"  # cannot move to this position

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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the shutter base device.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.valid_open_values = list(map(self.lowerCaseString, self.valid_open_values))
        self.valid_close_values = list(map(self.lowerCaseString, self.valid_close_values))

    @property
    def isOpen(self) -> bool:
        """is the shutter open?"""
        return str(self.state) == self.valid_open_values[0]

    @property
    def isClosed(self) -> bool:
        """is the shutter closed?"""
        return str(self.state) == self.valid_close_values[0]

    def inPosition(self, target: str) -> bool:
        """
        is the shutter at the target position?

        Args:
            target: The target position to check

        Returns:
            bool: True if the shutter is at the target position
        """
        self.validTarget(target)
        __value__ = self.lowerCaseString(target)
        if __value__ in self.valid_open_values and self.isOpen:
            return True
        elif __value__ in self.valid_close_values and self.isClosed:
            return True
        return False

    def set(self, value: str, **kwargs: Any) -> DeviceStatus:
        """
        plan: request the shutter to open or close

        Args:
            value: any from ``self.choices`` (typically "open" or "close")
            **kwargs: ignored at this time

        Returns:
            DeviceStatus: A status object that can be used to track the operation

        Raises:
            RuntimeError: If the shutter is currently operating
            ValueError: If the target value is not valid
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

            def move_it() -> None:
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

    def addCloseValue(self, text: str) -> List[str]:
        """
        Add a synonym to close the shutter, use with set().

        Args:
            text: The text to add as a close value

        Returns:
            List[str]: The list of acceptable values
        """
        self.valid_close_values.append(self.lowerCaseString(text))
        return self.choices  # return the list of acceptable values

    def addOpenValue(self, text: str) -> List[str]:
        """
        Add a synonym to open the shutter, use with set().

        Args:
            text: The text to add as an open value

        Returns:
            List[str]: The list of acceptable values
        """
        self.valid_open_values.append(self.lowerCaseString(text))
        return self.choices  # return the list of acceptable values

    @property
    def choices(self) -> List[str]:
        """return list of acceptable choices for set()"""
        return self.valid_open_values + self.valid_close_values

    def lowerCaseString(self, value: Any) -> str:
        """
        Ensure any given value is a lower-case string.

        Args:
            value: The value to convert

        Returns:
            str: The lower-case string representation of the value
        """
        return str(value).lower()

    def validTarget(self, target: str, should_raise: bool = True) -> bool:
        """
        Return whether (or not) target value is acceptable for self.set().

        Args:
            target: The target value to check
            should_raise: Whether to raise a ValueError if the target is not valid

        Returns:
            bool: True if the target is valid

        Raises:
            ValueError: If the target is not valid and should_raise is True
        """
        acceptable_values = self.choices
        ok = self.lowerCaseString(target) in acceptable_values
        if not ok and should_raise:
            msg = "received " + str(target)
            msg += " : should be only one of "
            msg += " | ".join(acceptable_values)
            raise ValueError(msg)
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

    signal: Signal = Component(Signal, value=0)

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        if self.signal.get() == self.open_value:
            return self.valid_open_values[0]
        elif self.signal.get() == self.close_value:
            return self.valid_close_values[0]
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


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

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    close_pv
        *str* :
        (kwarg, optional) Name of EPICS PV to close the shutter.
        If ``None``, defaults to ``"{prefix}Close"``.

    open_pv
        *str* :
        (kwarg, optional) Name of EPICS PV to open the shutter.
        If ``None``, defaults to ``"{prefix}Open"``.

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
    open_signal: EpicsSignal = FormattedComponent(EpicsSignal, "{self.open_pv}")
    close_signal: EpicsSignal = FormattedComponent(EpicsSignal, "{self.close_pv}")

    delay_s: float = 1.2  # allow time for shutter to move

    def __init__(
        self,
        prefix: str,
        *args: Any,
        close_pv: Optional[str] = None,
        open_pv: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the APS PSS shutter.

        Args:
            prefix: EPICS PV prefix
            *args: Additional positional arguments
            close_pv: Name of EPICS PV to close the shutter
            open_pv: Name of EPICS PV to open the shutter
            **kwargs: Additional keyword arguments
        """
        self.close_pv = close_pv or f"{prefix}Close"
        self.open_pv = open_pv or f"{prefix}Open"
        super().__init__(prefix, *args, **kwargs)

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        return self.unknown_state

    def open(self, timeout: float = 10) -> None:
        """
        Open the shutter.

        Args:
            timeout: Timeout in seconds for the operation
        """
        self.open_signal.put(1)
        if self.delay_s > 0:
            time.sleep(self.delay_s)

    def close(self, timeout: float = 10) -> None:
        """
        Close the shutter.

        Args:
            timeout: Timeout in seconds for the operation
        """
        self.close_signal.put(1)
        if self.delay_s > 0:
            time.sleep(self.delay_s)


class ApsPssShutterWithStatus(ApsPssShutter):
    """
    APS PSS shutter with separate status PV

    .. index:: Ophyd Device; ApsPssShutterWithStatus

    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
      (see :func:`ApsPssShutter()` for alternative)

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    state_pv
        *str* :
        Name of EPICS PV that provides shutter's current state.

    name
        *str* :
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
    pss_state: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{self.state_pv}")
    pss_state_open_values: List[int] = [1]
    pss_state_closed_values: List[int] = [0]

    delay_s: float = 0  # let caller add time after the move

    _poll_factor_: float = 1.5
    _poll_s_min_: float = 0.002
    _poll_s_max_: float = 0.15

    def __init__(
        self,
        prefix: str,
        state_pv: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the APS PSS shutter with status.

        Args:
            prefix: EPICS PV prefix
            state_pv: Name of EPICS PV that provides shutter's current state
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.state_pv = state_pv
        super().__init__(prefix, *args, **kwargs)

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.pss_state.get()
            if value in self.pss_state_open_values:
                return self.valid_open_values[0]
            elif value in self.pss_state_closed_values:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def wait_for_state(
        self,
        target: str,
        timeout: float = 10,
        poll_s: float = 0.01,
    ) -> None:
        """
        Wait for the shutter to reach the target state.

        Args:
            target: The target state to wait for
            timeout: Timeout in seconds
            poll_s: Polling interval in seconds

        Raises:
            TimeoutError: If the shutter does not reach the target state within the timeout
        """
        self.validTarget(target)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.inPosition(target):
                return
            time.sleep(min(poll_s * self._poll_factor_, self._poll_s_max_))
            poll_s = max(poll_s / self._poll_factor_, self._poll_s_min_)
        raise TimeoutError(f"shutter did not reach {target} in {timeout} seconds")

    def open(self, timeout: float = 10) -> None:
        """
        Open the shutter.

        Args:
            timeout: Timeout in seconds for the operation

        Raises:
            TimeoutError: If the shutter does not open within the timeout
        """
        self.open_signal.put(1)
        self.wait_for_state("open", timeout=timeout)

    def close(self, timeout: float = 10) -> None:
        """
        Close the shutter.

        Args:
            timeout: Timeout in seconds for the operation

        Raises:
            TimeoutError: If the shutter does not close within the timeout
        """
        self.close_signal.put(1)
        self.wait_for_state("close", timeout=timeout)


class SimulatedApsPssShutterWithStatus(ApsPssShutterWithStatus):
    """
    Simulated APS PSS shutter

    .. index:: Ophyd Device; SimulatedApsPssShutterWithStatus

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        sim = SimulatedApsPssShutterWithStatus(name="sim")

    """

    open_signal: Signal = Component(Signal, value=0)
    close_signal: Signal = Component(Signal, value=0)
    pss_state: Signal = FormattedComponent(Signal, value="close")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the simulated shutter."""
        super().__init__("sim:", "sim:state", *args, **kwargs)
        self.pss_state_open_values += self.valid_open_values
        self.pss_state_closed_values += self.valid_close_values

    def wait_for_state(
        self,
        target: str,
        timeout: float = 10,
        poll_s: float = 0.01,
    ) -> None:
        """
        Wait for the shutter to reach the target state.

        Args:
            target: The target state to wait for
            timeout: Timeout in seconds
            poll_s: Polling interval in seconds

        Raises:
            TimeoutError: If the shutter does not reach the target state within the timeout
        """
        self.validTarget(target)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.inPosition(target):
                return
            time.sleep(poll_s)
        raise TimeoutError(f"shutter did not reach {target} in {timeout} seconds")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.pss_state.get()
            if value in self.pss_state_open_values:
                return self.valid_open_values[0]
            elif value in self.pss_state_closed_values:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state


class EpicsMotorShutter(OneSignalShutter):
    """
    Shutter, implemented with an EPICS motor moved between two positions

    .. index:: Ophyd Device; EpicsMotorShutter

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

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

    signal: EpicsMotor = Component(EpicsMotor, "")
    tolerance: float = 0.01  # how close is considered in-position?

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.signal.position
            if abs(value - self.open_value) <= self.tolerance:
                return self.valid_open_values[0]
            elif abs(value - self.close_value) <= self.tolerance:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method moves the motor to the open position and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.move(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method moves the motor to the close position and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.move(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutter(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutter

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
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

    signal: EpicsSignal = Component(EpicsSignal, "")


class EpicsOnOffShutterWithStatus(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus17(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus17

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus17("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus18(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus18

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus18("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus19(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus19

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus19("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus20(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus20

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus20("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus21(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus21

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus21("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus22(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus22

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus22("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus23(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus23

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus23("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus24(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus24

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus24("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus25(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus25

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus25("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus26(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus26

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus26("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus27(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus27

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus27("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus28(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus28

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus28("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus29(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus29

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus29("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


class EpicsOnOffShutterWithStatus30(OneSignalShutter):
    """
    Shutter using a single EPICS PV moved between two positions

    .. index:: Ophyd Device; EpicsOnOffShutterWithStatus30

    Use for a shutter controlled by a single PV which takes a
    value for the close command and a different value for the open command.
    The current position is determined by comparing the value of the control
    with the expected open and close values.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix

    name
        *str* :
        (kwarg, required) object's canonical name

    EXAMPLE::

        bit_shutter = EpicsOnOffShutterWithStatus30("2bma:bit1", name="bit_shutter")
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

    signal: EpicsSignal = Component(EpicsSignal, "")
    status: EpicsSignalRO = Component(EpicsSignalRO, "")

    @property
    def state(self) -> str:
        """
        Returns the current state of the shutter.

        Returns:
            str: The current state of the shutter
        """
        try:
            value = self.status.get()
            if value == self.open_value:
                return self.valid_open_values[0]
            elif value == self.close_value:
                return self.valid_close_values[0]
        except Exception:
            pass
        return self.unknown_state

    def open(self) -> None:
        """
        Open the shutter.

        This method sets the signal to the open value and waits for the delay time.
        """
        if not self.isOpen:
            self.signal.put(self.open_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)

    def close(self) -> None:
        """
        Close the shutter.

        This method sets the signal to the close value and waits for the delay time.
        """
        if not self.isClosed:
            self.signal.put(self.close_value)
            if self.delay_s > 0:
                time.sleep(self.delay_s)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

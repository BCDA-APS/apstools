"""UR robotic arm control device.

Ophyd wrapper around the Universal Robots PVs served by the
``urRobot`` EPICS support module. Exposes the six joint readbacks and
command setpoints, the TCP pose (Cartesian + Euler) readbacks and command
setpoints, motion parameters, and the move/stop triggers needed to drive
the arm from Bluesky.
"""

import threading
import time

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd.status import Status
from ophyd.status import SubscriptionStatus


def _motion_complete_callback():
    """Build a SubscriptionStatus callback that requires a 0->1->0 cycle.

    ``Control:Moving`` reads 0 when idle. A fresh ``.set()`` must only
    resolve on the *new* move's 1->0 transition, not on the tail end of
    a prior move that was still completing when we subscribed. Tracking
    whether we have seen the 0->1 rising edge first closes that race.
    """
    saw_motion_start = [False]

    def _done(*, old_value, value, **kw):
        if old_value == 0 and value == 1:
            saw_motion_start[0] = True
            return False
        return saw_motion_start[0] and old_value == 1 and value == 0

    return _done


class _URJointGroup(Device):
    """Multi-axis joint positioner.

    ``set((j1, j2, j3, j4, j5, j6))`` writes all six J*Cmd setpoints,
    triggers ``Control:moveJ.PROC``, and returns a Status that completes
    when ``Control:Moving`` cycles 0->1->0 (motion started then
    finished). The 0->1 requirement ensures the Status does not resolve
    on the tail of a prior move that happened to still be in flight.
    """

    j1 = Component(EpicsSignal, "Control:J1Cmd", kind="omitted")
    j2 = Component(EpicsSignal, "Control:J2Cmd", kind="omitted")
    j3 = Component(EpicsSignal, "Control:J3Cmd", kind="omitted")
    j4 = Component(EpicsSignal, "Control:J4Cmd", kind="omitted")
    j5 = Component(EpicsSignal, "Control:J5Cmd", kind="omitted")
    j6 = Component(EpicsSignal, "Control:J6Cmd", kind="omitted")
    readback = Component(EpicsSignalRO, "Receive:ActualJointPositions")
    actuate = Component(EpicsSignal, "Control:moveJ.PROC", kind="omitted")
    moving = Component(EpicsSignalRO, "Control:Moving", kind="omitted")

    set_timeout = 60.0

    def set(self, target):
        t0 = time.monotonic()
        while self.moving.get() == 1:
            if time.monotonic() - t0 > self.set_timeout:
                raise TimeoutError(f"UR joint move did not complete within {self.set_timeout}s")
            time.sleep(0.05)

        targets = tuple(target)
        if len(targets) != 6:
            raise ValueError(f"UR joint group needs 6 targets (j1..j6), got {len(targets)}")
        for cpt, val in zip((self.j1, self.j2, self.j3, self.j4, self.j5, self.j6), targets):
            cpt.put(val)
        status = SubscriptionStatus(
            self.moving,
            _motion_complete_callback(),
            timeout=self.set_timeout,
        )
        self.actuate.put(1)
        return status


class _URPoseGroup(Device):
    """Cartesian TCP positioner.

    ``set((x, y, z, roll, pitch, yaw))`` writes all six Pose*Cmd setpoints,
    triggers ``Control:moveL.PROC``, and returns a Status that completes
    when ``Control:Moving`` cycles 0->1->0 (motion started then
    finished). The 0->1 requirement ensures the Status does not resolve
    on the tail of a prior move that happened to still be in flight.
    """

    readback = Component(EpicsSignalRO, "Receive:ActualTCPPose")
    x = Component(EpicsSignal, "Control:PoseXCmd", kind="omitted")
    y = Component(EpicsSignal, "Control:PoseYCmd", kind="omitted")
    z = Component(EpicsSignal, "Control:PoseZCmd", kind="omitted")
    roll = Component(EpicsSignal, "Control:PoseRollCmd", kind="omitted")
    pitch = Component(EpicsSignal, "Control:PosePitchCmd", kind="omitted")
    yaw = Component(EpicsSignal, "Control:PoseYawCmd", kind="omitted")
    actuate = Component(EpicsSignal, "Control:moveL.PROC", kind="omitted")
    moving = Component(EpicsSignalRO, "Control:Moving", kind="omitted")

    set_timeout = 60.0

    def set(self, target):
        t0 = time.monotonic()
        while self.moving.get() == 1:
            if time.monotonic() - t0 > self.set_timeout:
                raise TimeoutError(f"UR pose move did not complete within {self.set_timeout}s")
            time.sleep(0.05)

        targets = tuple(target)
        if len(targets) != 6:
            raise ValueError(f"UR pose group needs 6 targets (x,y,z,roll,pitch,yaw), got {len(targets)}")
        for cpt, val in zip((self.x, self.y, self.z, self.roll, self.pitch, self.yaw), targets):
            cpt.put(val)
        status = SubscriptionStatus(
            self.moving,
            _motion_complete_callback(),
            timeout=self.set_timeout,
        )
        self.actuate.put(1)
        return status


class _PipetteGroup(Device):
    """Tricontinent OEM pipette mounted on the UR.

    Wraps the ``Pipette:*`` records from the IOC's
    ``tricontinent_pipette.db``. ``home`` and ``aspirate`` are ``bo`` write
    triggers; the ``set_*`` signals are scalar setpoints in their record's
    engineering units; ``calc_plunger_position`` / ``actual_plunger_position``
    are the calculated and encoder-derived plunger positions in increments.
    """

    home = Component(EpicsSignal, "Pipette:Home")
    set_volume = Component(EpicsSignal, "Pipette:SetVolume")
    dispense = Component(EpicsSignal, "Pipette:Dispense")
    aspirate = Component(EpicsSignal, "Pipette:Aspirate")
    set_speed = Component(EpicsSignal, "Pipette:SetSpeed")
    set_dead_volume = Component(EpicsSignal, "Pipette:SetDeadVolume")
    calc_plunger_position = Component(EpicsSignalRO, "Pipette:CPPI")
    actual_plunger_position = Component(EpicsSignalRO, "Pipette:APPS")
    set_plunger = Component(EpicsSignal, "Pipette:SetPlunger")


class _RobotiqGripperGroup(Device):
    """Robotiq gripper mounted on the UR.

    Wraps the ``RobotiqGripper:*`` records from ``robotiq_gripper.db``.

    ``set("open")`` or ``set("close")`` triggers the gripper and returns
    a Status that completes when the move finishes. Close is considered
    done when not moving AND (is_closed OR is_stopped_inner). Open is
    done when not moving AND (is_open OR is_stopped_outer).
    """

    connected = Component(EpicsSignalRO, "RobotiqGripper:Connected")
    calibrated = Component(EpicsSignalRO, "RobotiqGripper:Calibrated")
    is_active = Component(EpicsSignalRO, "RobotiqGripper:IsActive")
    is_open = Component(EpicsSignalRO, "RobotiqGripper:IsOpen")
    is_closed = Component(EpicsSignalRO, "RobotiqGripper:IsClosed")
    is_stopped_inner = Component(EpicsSignalRO, "RobotiqGripper:IsStoppedInner")
    is_stopped_outer = Component(EpicsSignalRO, "RobotiqGripper:IsStoppedOuter")
    move_status = Component(EpicsSignalRO, "RobotiqGripper:MoveStatus", string=True)
    current_position = Component(EpicsSignalRO, "RobotiqGripper:CurrentPosition")
    open_position = Component(EpicsSignalRO, "RobotiqGripper:OpenPosition")
    closed_position = Component(EpicsSignalRO, "RobotiqGripper:ClosedPosition")

    connect = Component(EpicsSignal, "RobotiqGripper:Connect")
    activate = Component(EpicsSignal, "RobotiqGripper:Activate")
    auto_calibrate = Component(EpicsSignal, "RobotiqGripper:AutoCalibrate")
    open = Component(EpicsSignal, "RobotiqGripper:Open")
    close = Component(EpicsSignal, "RobotiqGripper:Close")
    set_position_range = Component(EpicsSignal, "RobotiqGripper:SetPositionRange")

    min_position = Component(EpicsSignal, "RobotiqGripper:MinPosition")
    max_position = Component(EpicsSignal, "RobotiqGripper:MaxPosition")
    position_unit = Component(EpicsSignal, "RobotiqGripper:PositionUnit", string=True)
    set_speed = Component(EpicsSignal, "RobotiqGripper:SetSpeed")
    set_force = Component(EpicsSignal, "RobotiqGripper:SetForce")

    set_timeout = 10.0

    def set(self, target):
        target = target.lower()
        if target not in ("open", "close"):
            raise ValueError(f"Gripper target must be 'open' or 'close', got {target!r}")

        def check():
            if target == "close":
                return self.is_closed.get() or self.is_stopped_inner.get()
            return self.is_open.get() or self.is_stopped_outer.get()

        status = Status(timeout=self.set_timeout)

        def _poll():
            try:
                if target == "close":
                    self.close.put(1)
                else:
                    self.open.put(1)
                t0 = time.monotonic()
                while True:
                    not_moving = self.move_status.get() != "Moving"
                    if not_moving and check():
                        status.set_finished()
                        return
                    if time.monotonic() - t0 > self.set_timeout:
                        status.set_exception(
                            TimeoutError(f"Gripper {target} did not complete within {self.set_timeout}s")
                        )
                        return
                    time.sleep(0.05)
            except Exception as exc:
                status.set_exception(exc)

        threading.Thread(target=_poll, daemon=True).start()
        return status


class UR(Device):
    """Universal Robots e-series arm exposed via the urRobot EPICS support module."""

    joints_readback = Component(EpicsSignalRO, "Receive:ActualJointPositions")
    pose_readback = Component(EpicsSignalRO, "Receive:ActualTCPPose")

    linear_speed = Component(EpicsSignal, "Control:LinearSpeed")
    joint_acceleration = Component(EpicsSignal, "Control:JointAcceleration")

    stop_robot = Component(EpicsSignal, "Control:Stop.PROC", kind="omitted")
    joints = Component(_URJointGroup, "")
    pose = Component(_URPoseGroup, "")
    pipette = Component(_PipetteGroup, "", lazy=True)
    gripper = Component(_RobotiqGripperGroup, "")

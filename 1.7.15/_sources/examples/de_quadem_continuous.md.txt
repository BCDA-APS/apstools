# quadEM electrometers (TetrAMM, FX4, ...) in continuous mode

**Objective**

Show the recommended pattern for using an
[EPICS quadEM](https://github.com/epics-modules/quadEM) electrometer
(such as the [TetrAMM](https://www.caenels.com/products/tetramm/) or the
[FX4](https://pyramid.tech/products/fx4)) with
[bluesky](https://blueskyproject.io/) when the device is operated as a
continuous beam-position monitor (BPM).

## Why no `apstools` device?

`apstools` does **not** provide its own quadEM device class.  Support already
exists upstream in `ophyd.quadem` (`QuadEM`, `TetrAMM`, `NSLS_EM`, `APS_EM`),
so the recommended pattern is to subclass the appropriate `ophyd` class
directly for beamline-specific behavior rather than to depend on an
`apstools` wrapper.

This is the same conclusion reached for the TetrAMM
([issue #878](https://github.com/BCDA-APS/apstools/issues/878)) and the FX4
([issue #1185](https://github.com/BCDA-APS/apstools/issues/1185)): if the
device can be represented cleanly by `ophyd.quadem.QuadEM`, keep the
customization in beamline code.

## The triggering problem

`ophyd.quadem.QuadEM.__init__()` sets these staging signals:

```py
self.stage_sigs.update(
    [("acquire", 0), ("acquire_mode", 2)]  # stop acquiring, single mode
)
```

For a detector that is triggered once per data point this is correct.  But
when the electrometer is used as a *continuous* BPM, these defaults cause a
scan such as

```py
RE(bp.rel_scan([tetramm], motor, -1, 1, 11))
```

to stall: the trigger presses ``Acquire`` in single mode and the trigger
status object never reports ``done``, so the scan hangs between points
([issue #1023](https://github.com/BCDA-APS/apstools/issues/1023)).

## Recommended beamline pattern

For continuous / BPM operation, subclass the `ophyd` device, clear the
staging signals so the acquisition mode is left untouched, and override
``trigger()`` to press ``Acquire`` and immediately mark the status as
finished so a subsequent ``.read()`` returns the current values:

```py
from ophyd import TetrAMM
from ophyd.status import Status


class ContinuousTetrAMM(TetrAMM):
    """TetrAMM as a continuous beam-position monitor.

    * Do not change the acquire mode when staging.
    * ``trigger()`` ensures acquisition is running, then reports done
      immediately so ``read()`` returns the current values.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Leave the device in whatever (continuous) mode it is already in.
        self.stage_sigs = {}

    def trigger(self):
        # Make sure the detector is acquiring, then report done.
        self.acquire.put(1)
        status = Status(self)
        status.set_finished()
        return status


tetramm = ContinuousTetrAMM("ioc_prefix:", name="tetramm")
tetramm.wait_for_connection()
```

The same pattern applies to any other quadEM-family device by subclassing the
appropriate `ophyd` class (for example a local `QuadEM` subclass with
``port_name="FX4"`` for the FX4; see
[issue #1185](https://github.com/BCDA-APS/apstools/issues/1185)).

## bluesky

Use the device in a plan like any other detector:

```py
RE(bp.rel_scan([tetramm], motor, -1, 1, 11))
```

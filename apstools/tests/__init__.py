import pathlib
import random
import time
import warnings

from ophyd.signal import EpicsSignalBase

# IOC prefixes
IOC_GP = "gp:"  # general purpose IOC: motors, scalers, slits, ...
IOC_AD = "ad:"  # ADSimDetector IOC

MASTER_TIMEOUT = 10
MAX_TESTING_RETRIES = 3
SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING = 2.0 / 60  # two 60Hz clock cycles

IMAGE_DIR = "adsimdet/%Y/%m/%d"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=MASTER_TIMEOUT,
        write_timeout=MASTER_TIMEOUT,
        connection_timeout=MASTER_TIMEOUT,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


def common_attribute_quantities_test(device, pv, connect, attr, expected):
    """
    Verify the quantities of an attribute.

    Count the number (or number of lines) of the named attribute. Special cases
    for certain methods.  Here are the known cases:

        * configuration_attrs
        * read_attrs
        * read()
        * summary()

    PARAMETERS

    device class:
        The class to be constructed for testing.
    pv str:
        The EPICS Process Variable name (or prefix) to be used.
    connect bool:
        Does testing require the object's Components to be connected with EPICS?
    attr str:
        The attribute (or method) to be tested.  Unhandled methods will raise an
        AttributeError.
    expected int:
        Expected quantity:  ``len(attr)`` (see code below)

    NOTE:  A retry handler was implemented to respond to some cases where random
    Components failed to connect with the default timeout. Testing with longer
    timeout intervals did not succeed while retrying the initial connection was
    successful.  A warning is reported when a timeout is encountered.
    """
    retry = 0
    while retry < MAX_TESTING_RETRIES:
        retry += 1
        obj = device(pv, name="obj")
        assert obj is not None, pv
        if not connect:
            break  # no need to wait
        try:
            obj.wait_for_connection()
            break
        except TimeoutError:
            # note: Increasing interval did not resolve the timeout.
            # Forcing retries was successful
            # This problem is intermittent.
            warnings.warn(f"Timeout connecting {attr} in {retry}/{MAX_TESTING_RETRIES}")

    if connect:
        assert obj.connected, f"{pv} {attr} {connect}"

    if attr == "read()":
        l = len(obj.read())
    elif attr == "summary()":
        l = len(obj._summary().splitlines())
    else:
        l = len(getattr(obj, attr))
    assert l == expected, f"{attr}: {l} != {expected}"


def rand(base, scale):
    return base + scale * random.random()


def setup_transform_as_soft_motor(
    t_rec, tol=5e-4, digits=5, smoothing=0.9, scan=".1 second", title="simulated motor"
):
    """Setup a synApps transform record as a positioner (motor) simulator."""
    t_rec.reset()
    for chan in t_rec.channels.component_names:
        getattr(t_rec.channels, chan).kind = "config"

    t_rec.channels.A.comment.put("setpoint")
    t_rec.channels.A.kind = "normal"

    # readback from previous process of record, computed
    t_rec.channels.B.comment.put("last readback")
    t_rec.channels.B.expression.put("O")  # channel O, the computed readback

    # fraction that new channels adds to readback
    t_rec.channels.C.comment.put("smoothing")
    t_rec.channels.C.current_value.put(smoothing)

    # done moving, computed
    t_rec.channels.D.comment.put("done")
    t_rec.channels.D.expression.put("G=B")
    # FIXME: goes to zero when setpoint is updated?

    # setpoint, rounded same as readback, computed
    t_rec.channels.G.comment.put("rounded setpoint")
    t_rec.channels.G.expression.put("FLOOR(A/P+0.5)*P")

    # stop, ignored for now
    t_rec.channels.H.comment.put("stop (ignored)")
    # TODO: how to respond to this, then reset it?

    # actuate, ignored for now
    t_rec.channels.I.comment.put("actuate (ignored)")
    # TODO: how to respond to this, then reset it?

    # readback, with roundoff, computed
    t_rec.channels.O.comment.put("readback")
    t_rec.channels.O.expression.put("FLOOR((B+(A-B)*C)/P+0.5)*P")
    t_rec.channels.O.kind = "normal"
    t_rec.channels.O.current_value.name = t_rec.name  # default name for read()

    # roundoff precision
    t_rec.channels.P.comment.put("roundoff")
    t_rec.channels.P.current_value.put(tol)
    t_rec.precision.put(digits)

    t_rec.scanning_rate.put(scan)
    t_rec.description.put(title)


def timed_pause(delay=None):
    time.sleep(delay or SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)


class MonitorCache:
    """Capture CA monitor values that match 'target'."""

    def __init__(self, target=None):
        self.target = target
        self.reset()

    def reset(self):
        self.messages = []

    def receiver(self, **kwargs):
        value = kwargs["value"]
        if value == self.target or self.target is None:
            self.messages.append(value)


class SignalSaveRestoreCache:
    """
    Save and restore previous signal values.

    Ensure area detector signals are restored to previous values.
    """

    def __init__(self) -> None:
        self.cache = {}

    def save(self, signal):
        if signal in self.cache:
            raise KeyError(f"'{signal.name}' already in the cache.")
        self.cache[signal] = signal.get()

    def restore(self):
        for signal in reversed(self.cache):
            signal.put(self.cache[signal])

    @property
    def review(self):
        return {signal.name: v for signal, v in self.cache.items()}

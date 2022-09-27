import time
import warnings

IOC = "gp:"
MASTER_TIMEOUT = 30
MAX_TESTING_RETRIES = 3
SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING = 2. / 60  # two 60Hz clock cycles


def short_delay_for_EPICS_IOC_database_processing(delay=None):
    time.sleep(delay or SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)


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
            warnings.warn(
                f"Timeout connecting {attr} in {retry}/{MAX_TESTING_RETRIES}"
            )

    if connect:
        assert obj.connected, f"{pv} {attr} {connect}"

    if attr == "read()":
        l = len(obj.read())
    elif attr == "summary()":
        l = len(obj._summary().splitlines())
    else:
        l = len(getattr(obj, attr))
    assert l == expected, f"{attr}: {l} != {expected}"

import logging
import threading
from typing import Any, Callable, Generator

import bluesky.plan_stubs as bps

from ..utils import run_in_thread

logger = logging.getLogger(__name__)
POLL_DELAY: float = 0.000_05


def run_blocking_function(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Generator[Any, None, None]:
    """
    Run a blocking function as a bluesky plan, in a thread.

    The ``run_blocking_function()`` is a bluesky plan which
    runs ``function(*args, **kwargs)`` in a thread so it does
    not block the RunEngine's background operations.

    .. note: Any result(s) returned from ``function``
       will be ignored.

    It is intended to call blocking code that should not be
    called directly from a bluesky plan.

    USAGE::

        yield from run_blocking_function(function, *args, **kwargs)

    EXAMPLE:

    This example creates a bluesky plan named ``start_incrementer()``
    which configures a synApps "userCalc" as an automated
    10Hz incrementer.
    Configuration is made by calling the *blocking* function
    :func:`~apstools.synApps.swait.setup_incrementer_swait`.
    The incrementer resets to zero at 100,000:

    .. code-block:: python

        from apstools.plans import run_blocking_function
        from apstools.synApps import SwaitRecord
        from apstools.synApps import setup_incrementer_swait
        import bluesky.plan_stubs as bps

        swait = SwaitRecord("ioc:userCalc1", name="swait")

        def start_incrementer():
            yield from run_blocking_function(
                setup_incrementer_swait,
                swait,
                scan="0.1 second",
                limit=100_000
            )

        # now, run my_plan
        RE(my_plan())

    .. note: This function is a convenience adapter to execute
       functions that are not bluesky generator functions, plans.
       It's best not to use this as a decorator.

    (new in release 1.6.3)
    """

    @run_in_thread
    def internal() -> threading.Thread:
        """
        Internal function to run the blocking function in a separate thread.

        Returns:
            threading.Thread: The thread running the blocking function.
        """
        result: Any = function(*args, **kwargs)
        logger.debug("%s() result=%s", result)

    thread: threading.Thread = internal()
    while thread.is_alive():
        yield from bps.sleep(POLL_DELAY)

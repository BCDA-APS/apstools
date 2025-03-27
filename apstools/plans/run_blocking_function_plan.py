import logging
from typing import Any, Callable, Generator, TypeVar

import bluesky.plan_stubs as bps

from ..utils import run_in_thread

logger = logging.getLogger(__name__)
POLL_DELAY = 0.000_05

T = TypeVar("T")


def run_blocking_function(
    function: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> Generator[None, None, None]:
    """
    Run a blocking function as a bluesky plan, in a thread.

    Args:
        function: Function to run in a thread
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Generator yielding None
    """

    @run_in_thread
    def internal() -> None:
        result = function(*args, **kwargs)
        logger.debug("%s() result=%s", result)

    thread = internal()
    while thread.is_alive():
        yield from bps.sleep(POLL_DELAY)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

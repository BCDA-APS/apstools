"""
nscan plan
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~nscan
"""

import datetime
from collections import OrderedDict
from typing import Any, Dict, Generator, List, Optional, Tuple, Union, Callable

import numpy as np
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from ophyd import Device, Signal


def nscan(
    detectors: List[Device],
    *motor_sets: Union[Signal, float],
    num: int = 11,
    per_step: Optional[
        Callable[[List[Device], Dict[Signal, float], Dict[Signal, float]], Generator[None, None, None]]
    ] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    Scan over n variables moved together, each in equally spaced steps.

    Args:
        detectors: list of 'readable' objects
        motor_sets: sequence of one or more groups of: motor, start, finish
        num: number of steps (default: 11)
        per_step: hook for customizing action of inner loop (messages per step)
        md: metadata dictionary

    Returns:
        Generator yielding None
    """

    def take_n_at_a_time(args: List[Any], n: int = 2) -> Generator[Tuple[Any, ...], None, None]:
        yield from zip(*[iter(args)] * n)

    if len(motor_sets) < 3:
        raise ValueError("must provide at least one movable")
    if len(motor_sets) % 3 > 0:
        raise ValueError("must provide sets of movable, start, finish")

    motors = OrderedDict()
    for m, s, f in take_n_at_a_time(motor_sets, n=3):
        if not isinstance(s, (int, float)):
            msg = "start={} ({}): is not a number".format(s, type(s))
            raise ValueError(msg)
        if not isinstance(f, (int, float)):
            msg = "finish={} ({}): is not a number".format(f, type(f))
            raise ValueError(msg)
        motors[m.name] = dict(
            motor=m,
            start=s,
            finish=f,
            steps=np.linspace(start=s, stop=f, num=num),
        )

    _md = {
        "detectors": [det.name for det in detectors],
        "motors": [m for m in motors.keys()],
        "num_points": num,
        "num_intervals": num - 1,
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "num": num,
            "motors": repr(motor_sets),
            "per_step": repr(per_step),
        },
        "plan_pattern": "linspace",
        "hints": {},
        "iso8601": str(datetime.datetime.now()),
    }
    _md.update(md or {})

    try:
        m = list(motors.keys())[0]
        dimensions = [(motors[m]["motor"].hints["fields"], "primary")]
    except (AttributeError, KeyError):
        pass
    else:
        _md["hints"].setdefault("dimensions", dimensions)

    if per_step is None:
        per_step = bps.one_nd_step

    @bpp.stage_decorator(list(detectors) + [m["motor"] for m in motors.values()])
    @bpp.run_decorator(md=_md)
    def inner_scan() -> Generator[None, None, None]:
        for step in range(num):
            step_cache: Dict[Signal, float] = {}
            pos_cache: Dict[Signal, float] = {}
            for m in motors.values():
                next_pos = m["steps"][step]
                m = m["motor"]
                pos_cache[m] = m.read()[m.name]["value"]
                step_cache[m] = next_pos
            yield from per_step(detectors, step_cache, pos_cache)

    return (yield from inner_scan())


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

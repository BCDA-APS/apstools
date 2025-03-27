from bluesky import plan_stubs as bps
from bluesky import utils
from bluesky import plan_patterns
from bluesky import preprocessors as bpp
from cycler import Cycler

import inspect
from itertools import zip_longest, cycle
from collections import defaultdict
import os
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

from toolz import partition
from ophyd import Device, Signal


def mesh_list_grid_scan(
    detectors: List[Device],
    *args: Union[Signal, List[float]],
    number_of_collection_points: int,
    snake_axes: Union[bool, List[Signal]] = False,
    per_step: Optional[Callable[[List[Device], Dict[Signal, float], Dict[Signal, float]], Generator[None, None, None]]] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    Scan over a multi-dimensional mesh, collecting a total of n points.

    Args:
        detectors: list of 'readable' objects
        *args: patterned like (motor1, position_list1, motor2, position_list2, ...)
        number_of_collection_points: total number of collection points
        snake_axes: which axes should be snaked (default: False)
        per_step: hook for customizing action of inner loop (default: None)
        md: metadata dictionary (default: None)

    Returns:
        Generator yielding None
    """
    full_cycler = plan_patterns.outer_list_product(args, snake_axes)

    md_args = []
    motor_names = []
    motors = []
    for motor, pos_list in partition(2, args):
        md_args.extend([repr(motor), pos_list])
        motor_names.append(motor.name)
        motors.append(motor)
    _md = {
        "shape": tuple(len(pos_list) for motor, pos_list in partition(2, args)),
        "extents": tuple([min(pos_list), max(pos_list)] for motor, pos_list in partition(2, args)),
        "snake_axes": snake_axes,
        "plan_args": {"detectors": list(map(repr, detectors)), "args": md_args, "per_step": repr(per_step)},
        "plan_name": "list_grid_scan",
        "plan_pattern": "outer_list_product",
        "plan_pattern_args": dict(args=md_args, snake_axes=snake_axes),
        "plan_pattern_module": plan_patterns.__name__,
        "motors": tuple(motor_names),
        "hints": {},
    }
    _md.update(md or {})
    try:
        _md["hints"].setdefault("dimensions", [(m.hints["fields"], "primary") for m in motors])
    except (AttributeError, KeyError):
        pass

    return (
        yield from mesh_scan_nd(detectors, full_cycler, number_of_collection_points, per_step=per_step, md=_md)
    )


def mesh_scan_nd(
    detectors: List[Device],
    cycler: Cycler,
    number_of_collection_points: int,
    *,
    per_step: Optional[Callable[[List[Device], Dict[Signal, float], Dict[Signal, float]], Generator[None, None, None]]] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    Scan over an arbitrary N-dimensional trajectory.

    Args:
        detectors: list of 'readable' objects
        cycler: Cycler object mapping movable interfaces to positions
        number_of_collection_points: total number of collection points
        per_step: hook for customizing action of inner loop (default: None)
        md: metadata dictionary (default: None)

    Returns:
        Generator yielding None
    """
    _md = {
        "detectors": [det.name for det in detectors],
        "motors": [motor.name for motor in cycler.keys],
        "num_points": len(cycler),
        "num_intervals": len(cycler) - 1,
        "plan_args": {"detectors": list(map(repr, detectors)), "cycler": repr(cycler), "per_step": repr(per_step)},
        "plan_name": "scan_nd",
        "hints": {},
    }
    _md.update(md or {})
    try:
        dimensions = [(motor.hints["fields"], "primary") for motor in cycler.keys]
    except (AttributeError, KeyError):
        pass
    else:
        _md["hints"].setdefault("dimensions", dimensions)

    predeclare = per_step is None and os.environ.get("BLUESKY_PREDECLARE", False)
    if per_step is None:
        per_step = bps.one_nd_step
    else:
        sig = inspect.signature(per_step)

        def _verify_step(sig: inspect.Signature, expected_list: List[str]) -> bool:
            if len(sig.parameters) < 3:
                return False
            for name, (p_name, p) in zip_longest(expected_list, sig.parameters.items()):
                if name is not None:
                    if name != p_name:
                        return False
                else:
                    if p.kind is p.VAR_KEYWORD or p.kind is p.VAR_POSITIONAL:
                        continue
                    if p.default is p.empty:
                        return False
            return True

        if sig == inspect.signature(bps.one_nd_step):
            pass
        elif _verify_step(sig, ["detectors", "step", "pos_cache"]):
            pass
        elif _verify_step(sig, ["detectors", "motor", "step"]):
            dims = len(list(cycler.keys))
            if dims != 1:
                raise TypeError(f"Signature of per_step assumes 1D trajectory but {dims} motors are specified.")
            (motor,) = cycler.keys
            user_per_step = per_step

            def adapter(detectors: List[Device], step: Dict[Signal, float], pos_cache: Dict[Signal, float]) -> Generator[None, None, None]:
                (step,) = step.values()
                return (yield from user_per_step(detectors, motor, step))

            per_step = adapter
        else:
            raise TypeError(
                "per_step must be a callable with the signature \n "
                "<Signature (detectors, step, pos_cache)> or "
                "<Signature (detectors, motor, step)>. \n"
                "per_step signature received: {}".format(sig)
            )
    pos_cache: Dict[Signal, float] = defaultdict(lambda: None)  # where last position is stashed
    cycler = utils.merge_cycler(cycler)
    motors = list(cycler.keys)

    @bpp.stage_decorator(list(detectors) + motors)
    @bpp.run_decorator(md=_md)
    def scan_until_completion() -> Generator[None, None, None]:
        """
        Scanning until the total number of required collection points is achieved
        """
        if predeclare:
            yield from bps.declare_stream(*motors, *detectors, name="primary")

        iterations = 0
        for step in cycle(cycler):
            yield from per_step(detectors, step, pos_cache)
            iterations += 1
            if iterations == number_of_collection_points:
                break

    return (yield from scan_until_completion())

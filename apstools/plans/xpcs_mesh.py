from bluesky import plan_stubs as bps
from bluesky import utils
from bluesky import plan_patterns
from bluesky import preprocessors as bpp

import inspect
from itertools import zip_longest, cycle
from collections import defaultdict
import os

from toolz import partition


def mesh_list_grid_scan(detectors, *args, number_of_collection_points, snake_axes=False, per_step=None, md=None):
    """
    Scan over a multi-dimensional mesh, collecting a total of *n* points; each motor is on an independent trajectory.

    Parameters
    ----------
    detectors: list
        list of 'readable' objects
    args: list
        patterned like (``motor1, position_list1,``
                        ``motor2, position_list2,``
                        ``motor3, position_list3,``
                        ``...,``
                        ``motorN, position_listN``)

        The first motor is the "slowest", the outer loop. ``position_list``'s
        are lists of positions, all lists must have the same length. Motors
        can be any 'settable' object (motor, temp controller, etc.).
    number_of_collection_points: int
        The total number of collection points that must be collected within the
        grid until the scan is ready to stop.
    snake_axes: boolean or iterable, optional
        which axes should be snaked, either ``False`` (do not snake any axes),
        ``True`` (snake all axes) or a list of axes to snake. "Snaking" an axis
        is defined as following snake-like, winding trajectory instead of a
        simple left-to-right trajectory.The elements of the list are motors
        that are listed in `args`. The list must not contain the slowest
        (first) motor, since it can't be snaked.
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md: dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.rel_list_grid_scan`
    :func:`bluesky.plans.list_scan`
    :func:`bluesky.plans.rel_list_scan`
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
        ...

    return (
        yield from mesh_scan_nd(detectors, full_cycler, number_of_collection_points, per_step=per_step, md=_md)
    )


def mesh_scan_nd(detectors, cycler, number_of_collection_points, *, per_step=None, md=None):
    """
    Scan over an arbitrary N-dimensional trajectory.

    Parameters
    ----------
    detectors : list
    cycler : Cycler
        cycler.Cycler object mapping movable interfaces to positions
    number_of_collection_points: int
        The total number of collection points that must be collected within the
        grid until the scan is ready to stop.
    per_step : callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md : dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.inner_product_scan`
    :func:`bluesky.plans.grid_scan`

    Examples
    --------
    >>> from cycler import cycler
    >>> cy = cycler(motor1, [1, 2, 3]) * cycler(motor2, [4, 5, 6])
    >>> scan_nd([sensor], cy)
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
        # Not all motors provide a 'fields' hint, so we have to skip it.
        pass
    else:
        # We know that hints exists. Either:
        #  - the user passed it in and we are extending it
        #  - the user did not pass it in and we got the default {}
        # If the user supplied hints includes a dimension entry, do not
        # change it, else set it to the one generated above
        _md["hints"].setdefault("dimensions", dimensions)

    predeclare = per_step is None and os.environ.get("BLUESKY_PREDECLARE", False)
    if per_step is None:
        per_step = bps.one_nd_step
    else:
        # Ensure that the user-defined per-step has the expected signature.
        sig = inspect.signature(per_step)

        def _verify_step(sig, expected_list):
            if len(sig.parameters) < 3:
                return False
            for name, (p_name, p) in zip_longest(expected_list, sig.parameters.items()):
                # this is one of the first 3 positional arguements, check that the name matches
                if name is not None:
                    if name != p_name:
                        return False
                # if there are any extra arguments, check that they have a default
                else:
                    if p.kind is p.VAR_KEYWORD or p.kind is p.VAR_POSITIONAL:
                        continue
                    if p.default is p.empty:
                        return False

            return True

        if sig == inspect.signature(bps.one_nd_step):
            pass
        elif _verify_step(sig, ["detectors", "step", "pos_cache"]):
            # check other signature for back-compatibility
            pass

        elif _verify_step(sig, ["detectors", "motor", "step"]):
            # Accept this signature for back-compat reasons (because
            # inner_product_scan was renamed scan).
            dims = len(list(cycler.keys))
            if dims != 1:
                raise TypeError(f"Signature of per_step assumes 1D trajectory but {dims} motors are specified.")
            (motor,) = cycler.keys
            user_per_step = per_step

            def adapter(detectors, step, pos_cache):
                # one_nd_step 'step' parameter is a dict; one_id_step 'step'
                # parameter is a value
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
    pos_cache = defaultdict(lambda: None)  # where last position is stashed
    cycler = utils.merge_cycler(cycler)
    motors = list(cycler.keys)

    @bpp.stage_decorator(list(detectors) + motors)
    @bpp.run_decorator(md=_md)
    def scan_until_completion():
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

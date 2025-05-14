"""
Motor Bundle Factory
====================

Factory for creating ophyd Devices with any number of real or simulated motors.

- Use `mb_creator()` to quickly group motors (axes) into a single device.
- Supports both real (EpicsMotor) and simulated (SoftPositioner) axes.
- Advanced axis configuration is possible via per-axis dictionaries.
- Custom base classes, class names, and labels are supported.

.. autosummary::

    ~axis_component
    ~mb_class_factory
    ~mb_creator

.. rubric:: Quick Example

.. code-block:: python

    from apstools.devices import mb_creator
    xy_stage = mb_creator(
        prefix="IOC:",
        motors={"x": "m21", "y": "m22"},
        name="xy_stage"
    )

.. seealso::
    - :doc:`Quickstart <examples/ho_motor_factory_quickstart>`
    - :doc:`Full usage <examples/ho_motor_factory>`
"""

from typing import Any, Callable, cast
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union
from typing import TypeVar

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import Kind
from ophyd import MotorBundle
from ophyd import SoftPositioner

from apstools.utils import dynamic_import

T = TypeVar("T")

DEFAULT_DEVICE_BASE_CLASSES: list[Union[str, type]] = [MotorBundle]
DEFAULT_DEVICE_CLASS_NAME: str = "MB_Device"
DEFAULT_MOTOR_LABELS: list[str] = ["motors"]
DEFAULT_KIND: Kind = Kind.hinted | Kind.normal

MOTORS_TYPE = Union[list[str], dict[str, Optional[Union[str, dict[str, Any]]]]]


def axis_component(parms: Union[str, dict[str, Any]]) -> Component:
    """Return a Component with 'parms' for this axis.

    Args:
        parms: Parameters for the axis, either as a string (prefix) or a dictionary.

    Returns:
        Component: An ophyd Component for the axis.
    """
    parms = parms or {}
    if isinstance(parms, str):
        parms = dict(prefix=parms)
    attrs: dict[str, Any] = dict(kind=DEFAULT_KIND, labels=DEFAULT_MOTOR_LABELS)
    has_prefix: bool = parms.get("prefix") is not None
    axis_class_name: Optional[str] = parms.pop("class", None)
    factory: Optional[dict[str, Any]] = parms.pop("factory", None)
    if axis_class_name is not None and factory is not None:
        raise ValueError(f"Unsupported configuration: {axis_class_name=!r} and {factory=!r}")
    if factory is not None:
        creator: Union[Callable[..., type], str] = factory.pop("function")
        if isinstance(creator, str):
            creator = dynamic_import(creator)
        base: type = creator(**factory)
        # Add 'prefix' if missing?
    elif axis_class_name is None:
        base: type = EpicsMotor if has_prefix else SoftPositioner
        if base == EpicsMotor and "prefix" not in parms:
            parms["prefix"] = ""
    else:
        # Allow for any positioner type.
        base = dynamic_import(axis_class_name)
    attrs.update(**parms)

    args: list[Any] = [base]
    prefix: Optional[str] = attrs.pop("prefix", None)
    if prefix is not None:
        args.append(prefix)
    return Component(*args, **attrs)


def mb_class_factory(
    motors: Optional[MOTORS_TYPE] = None,
    class_bases: list[Union[str, type]] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
) -> type:
    """Create a custom MotorBundle (or as specified in 'class_bases') class.

    Args:
        motors: List or dict of motors to include in the bundle.
        class_bases: List of base classes (as types or import strings).
        class_name: Name of the generated class.

    Returns:
        type: The dynamically created class.
    """
    motors = motors or {}
    if isinstance(motors, list):
        motors = {axis: {} for axis in motors}

    if not isinstance(class_bases, list):
        raise TypeError(f"Must be a list, received {class_bases=!r}")

    resolved_bases: list[type] = [
        dynamic_import(base) if isinstance(base, str) else base
        for base in class_bases
    ]

    axes: dict[str, Component] = {axis: axis_component(parms) for axis, parms in motors.items()}
    factory_class_attributes: dict[str, Any] = {}
    factory_class_attributes.update(**axes)

    def __init__(self: Any, prefix: str = "", **kwargs: Any) -> None:
        for base in resolved_bases:
            if hasattr(base, "__init__"):
                base.__init__(self, prefix=prefix, **kwargs)

    factory_class_attributes["__init__"] = __init__

    return type(class_name, tuple(resolved_bases), factory_class_attributes)


def mb_creator(
    *,
    prefix: str = "",
    name: Optional[str] = None,
    motors: MOTORS_TYPE = {},
    class_bases: list[type] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
    labels: list[str] = ["motor_device"],
) -> Any:
    """
    Create MotorBundle with any number of motors.

    Args:
        prefix: The prefix for the device.
        name: The name of the device (required).
        motors: List or dict of motors to include in the bundle.
        class_bases: List of base classes for the bundle.
        class_name: Name of the generated class.
        labels: List of labels for the device.

    Returns:
        Any: An instance of the generated MotorBundle class.
    """
    if not isinstance(name, str):
        raise TypeError(f"Must provide a 'name', received {name=!r}")

    if not isinstance(motors, (dict, list)):
        raise TypeError(f"Expected 'motors' as list or dict, received {motors=!r}")

    MB_Device: type = mb_class_factory(
        motors=motors,
        class_bases=class_bases,
        class_name=class_name,
    )
    return MB_Device(prefix, name=name, labels=labels)

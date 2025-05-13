"""
Motor Bundle Factory
====================

Factory for creating bundles with any number of positioners.

.. autosummary::

    ~axis_component
    ~mb_class_factory
    ~mb_creator

.. rubric:: Examples

.. code-block:: python
    :linenos:

    xy_stage = mb_creator(prefix="IOC:", motors={"x": "m21", "y": "m22"})

.. seealso:: :doc:`How to use 'mb_creator()' </examples/ho_motor_factory>`
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import Kind
from ophyd import MotorBundle
from ophyd import SoftPositioner

from apstools.utils import dynamic_import

DEFAULT_DEVICE_BASE_CLASSES: List[Union[str, Type]] = [MotorBundle]
DEFAULT_DEVICE_CLASS_NAME: str = "MB_Device"
DEFAULT_MOTOR_LABELS: List[str] = ["motors"]
DEFAULT_KIND: Kind = Kind.hinted | Kind.normal

MOTORS_TYPE = Union[List[str], Dict[str, Optional[Union[str, Dict]]]]


def axis_component(parms: dict[str, Any]) -> Component:
    """Return a Component with 'parms for this axis."""
    parms = parms or {}
    if isinstance(parms, str):
        parms = dict(prefix=parms)
    attrs = dict(kind=DEFAULT_KIND, labels=DEFAULT_MOTOR_LABELS)
    has_prefix: bool = parms.get("prefix") is not None
    axis_class_name = parms.pop("class", None)
    factory = parms.pop("factory", None)
    if axis_class_name is not None and factory is not None:
        raise ValueError(f"Unsupported configuration: {axis_class_name=!r} and {factory=!r}")
    if factory is not None:
        creator = factory.pop("function")
        if isinstance(creator, str):
            creator = dynamic_import(creator)
        base = creator(**factory)
        # Add 'prefix' if missing?
    elif axis_class_name is None:
        base = EpicsMotor if has_prefix else SoftPositioner
        if base == EpicsMotor and "prefix" not in parms:
            parms["prefix"] = ""
    else:
        # Allow for any positioner type.
        base = dynamic_import(axis_class_name)
    attrs.update(**parms)

    args = [base]
    prefix = attrs.pop("prefix", None)
    if prefix is not None:
        args.append(prefix)
    return Component(*args, **attrs)


def mb_class_factory(
    motors: MOTORS_TYPE = None,
    class_bases: List[Union[str, Type]] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
) -> Type:
    """Create a custom MotorBundle (or as specified in 'class_bases') class."""
    motors: MOTORS_TYPE = motors or {}
    if isinstance(motors, list):
        motors = {axis: {} for axis in motors}

    if not isinstance(class_bases, list):
        raise TypeError(f"Must be a list, received {class_bases=!r}")

    class_bases = [
        dynamic_import(base) if isinstance(base, str) else base
        # .
        for base in class_bases
    ]

    axes: Dict[str, Component] = {axis: axis_component(parms) for axis, parms in motors.items()}
    factory_class_attributes: Dict[str, Any] = {}
    factory_class_attributes.update(**axes)

    def __init__(self, prefix: str = "", **kwargs):
        for base in class_bases:
            if hasattr(base, "__init__"):
                base.__init__(self, prefix=prefix, **kwargs)

    factory_class_attributes["__init__"] = __init__

    return type(class_name, tuple(class_bases), factory_class_attributes)


def mb_creator(
    *,
    prefix: str = "",
    name: Optional[str] = None,
    motors: MOTORS_TYPE = {},
    class_bases: List[Type] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
    labels: List[str] = ["motor_device"],
):
    """
    Create MotorBundle with any number of motors.
    """

    if not isinstance(name, str):
        raise TypeError("Must provide a 'name', received {name=!r}")

    if not isinstance(motors, (dict, list)):
        raise TypeError("Expected 'motors' as list or dict, received {motors=!r}")

    MB_Device: Type = mb_class_factory(
        motors=motors,
        class_bases=class_bases,
        class_name=class_name,
    )
    return MB_Device(prefix, name=name, labels=labels)

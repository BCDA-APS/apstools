"""
Motor Bundle Factory
====================

Factory for creating bundles with any number of positioners.

* Use :func:`~apstools.devices.motor_factory.mb_creator()`
  to quickly group motors (axes) into a single ophyd device.
* Supports different axes types including EpicsMotor,
  simulated (SoftPositioner), and other positioners.
* Advanced axis configuration is possible via per-axis dictionaries.
* Custom base classes, class names, labels, and factories are supported.

.. autosummary::

    ~axis_component
    ~mb_class_factory
    ~mb_creator

.. rubric:: Quick Example

.. code-block:: python
    :linenos:

    xy_stage = mb_creator(
        prefix="IOC:",
        motors={"x": "m21", "y": "m22"},
        name="xy_stage",
    )

.. seealso::

   * :doc:`Quick Start </examples/ho_motor_factory_quickstart>`
   * :doc:`How to use 'mb_creator()' </examples/ho_motor_factory>`
"""

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union

from deprecated.sphinx import versionadded
from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import Kind
from ophyd import MotorBundle
from ophyd import SoftPositioner

from apstools.utils import dynamic_import

DEFAULT_DEVICE_BASE_CLASSES: Sequence[Union[str, Type]] = [MotorBundle]
DEFAULT_DEVICE_CLASS_NAME: str = "MB_Device"
DEFAULT_MOTOR_LABELS: Sequence[str] = ["motors"]
DEFAULT_KIND: Kind = Kind.hinted | Kind.normal

MOTORS_TYPE = Union[Sequence[str], Mapping[str, Optional[Union[str, Mapping]]]]


def axis_component(
    parms: Union[None, str, Mapping[str, Any]],
) -> Component:
    """
    Return a Component with 'parms for this axis.

    PARAMETERS

    parms:
        Parameters for the axis, either as a string (prefix) or a mapping.

    RETURNS

    Component:
        An ophyd Component for the axis.
    """
    if parms is None:
        _parms = {}
    elif isinstance(parms, str):
        _parms = dict(prefix=parms)
    else:
        _parms = {**parms}

    attrs: Dict[str, Any] = dict(kind=DEFAULT_KIND, labels=DEFAULT_MOTOR_LABELS)
    has_prefix: bool = _parms.get("prefix") is not None
    axis_class_name: Optional[str] = _parms.pop("class", None)
    factory: Optional[Mapping[str, Any]] = _parms.pop("factory", None)
    if axis_class_name is not None and factory is not None:
        raise ValueError(f"Cannot be used together: {axis_class_name=!r} and {factory=!r}")
    if factory is not None:
        creator: Union[Callable[..., type], str] = factory.pop("function")
        if isinstance(creator, str):
            creator = dynamic_import(creator)
        base = creator(**factory)
        # Add 'prefix' if missing?
    elif axis_class_name is None:
        base: Device = EpicsMotor if has_prefix else SoftPositioner
        if base == EpicsMotor and "prefix" not in _parms:
            _parms["prefix"] = ""
        elif base == SoftPositioner and "init_pos" not in _parms:
            _parms["init_pos"] = 0
    else:
        # Allow for any positioner type or factory function.
        base: Callable = dynamic_import(axis_class_name)
    attrs.update(**_parms)

    args: Sequence[Device] = [base]
    prefix: Optional[str] = attrs.pop("prefix", None)
    if prefix is not None:
        args.append(prefix)
    return Component(*args, **attrs)


@versionadded(version="1.7.4")
def mb_class_factory(
    motors: Union[MOTORS_TYPE, None] = None,
    class_bases: Sequence[Union[str, Type]] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
) -> Type[Device]:
    """
    Create a custom MotorBundle (or as specified in 'class_bases') class.

    PARAMETERS

        motors:
            Dictionary or list of motors to include in the bundle.
        class_bases:
            List of base classes (as Python objects or import strings).
        class_name:
            Name of the generated class.

    RETURNS:
        The dynamically-created class (a subclass of ophyd.Device).
    """
    _motors: MOTORS_TYPE = motors or {}
    if isinstance(_motors, (list, set, tuple)):
        _motors = {axis: {} for axis in _motors}

    if not isinstance(class_bases, (list, set, tuple)):
        raise TypeError(f"Must be a list, received {class_bases=!r}")

    bases = [
        dynamic_import(base) if isinstance(base, str) else base
        # .
        for base in class_bases
    ]

    axes: Mapping[str, Component] = {
        axis: axis_component(parms)
        # .
        for axis, parms in _motors.items()
    }
    factory_class_attributes: Mapping[str, Any] = {}
    factory_class_attributes.update(**axes)

    def __init__(self: Device, prefix: str = "", **kwargs: Mapping):
        for base in bases:
            if hasattr(base, "__init__"):
                base.__init__(self, prefix=prefix, **kwargs)

    factory_class_attributes["__init__"] = __init__

    return type(class_name, tuple(bases), factory_class_attributes)


@versionadded(version="1.7.4")
def mb_creator(
    *,
    prefix: str = "",
    name: Optional[str] = None,
    motors: MOTORS_TYPE = {},
    class_bases: Sequence[Type] = DEFAULT_DEVICE_BASE_CLASSES,
    class_name: str = DEFAULT_DEVICE_CLASS_NAME,
    labels: Sequence[str] = ["motor_device"],
) -> Device:
    """
    Create MotorBundle with any number of motors.

    PARAMETERS

    prefix str:
        The prefix for the device.

    name str:
        The name of the device (required).

    motors list | dict:
        List or dictionary of motor specifications to include in the bundle.

    class_bases:
        List of base classes for the bundle.

    class_name str:
        Name of the generated class.

    labels list:
        List of labels for the device.

    RETURNS

        An instance of the generated MotorBundle (or other, as directed) class.
    """

    if not isinstance(name, str):
        raise TypeError(f"Must provide a 'name', received {name=!r}")

    if not isinstance(motors, (list, Mapping, set, tuple)):
        raise TypeError(f"Expected 'motors' as list or dict, received {motors=!r}")

    MB_Device: Type[Device] = mb_class_factory(
        motors=motors,
        class_bases=class_bases,
        class_name=class_name,
    )
    return MB_Device(prefix, name=name, labels=labels)

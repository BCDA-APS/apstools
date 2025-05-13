"""Test the motor bundle factories."""

from contextlib import nullcontext as does_not_raise
from typing import Any, LiteralString
from typing import Dict, Callable
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import pytest
from ophyd import Component
from ophyd import Device
from ophyd import MotorBundle

from ..motor_factory import axis_component
from ..motor_factory import mb_class_factory
from ..motor_factory import mb_creator
from ..motor_factory import MOTORS_TYPE


class Mixin(Device):
    """Device class for testing."""

    _mixin = True


@pytest.mark.parametrize(
    "parms, class_str, raises, expected",
    [
        [None, "SoftPositioner", None, None],  # no PV, default to soft
        [dict(), "SoftPositioner", None, None],  # same
        ["m1", "EpicsMotor", None, None],  # PV str, use a motor
        [dict(prefix="m1"), "EpicsMotor", None, None],  # same
        [  # dict with a pv ('prefix', by name)
            dict(
                prefix="m1",
                labels=["dcm"],
            ),
            "EpicsMotor",
            None,
            None,
        ],
        [  # can't specify a class AND a factory
            {
                "class": "abcde",
                "factory": "factory",
            },
            None,
            ValueError,
            "Unsupported configuration",
        ],
        [  # specify a class
            {
                "class": "apstools.devices.PVPositionerSoftDoneWithStop",
                "readback_pv": "gp:float14",
                "setpoint_pv": "gp:float4",
            },
            "PVPositionerSoftDoneWithStop",
            None,
            None,
        ],
        [  # specify a class factory
            {
                "factory": {
                    "function": "apstools.devices.mb_class_factory",
                    "motors": ["x1", "x2", "y1", "y2", "y3", "z"],
                    "class_name": "TestDevice",
                },
            },
            "TestDevice",
            None,
            None,
        ],
    ],
)
def test_axis_component(
    parms: (
        List[None | str]
        | List[Dict | None | str]
        | List[Dict[str, str] | None | str]
        | List[Dict[str, str | List[str]] | None | str]
        | List[Dict[str, str] | None | type[ValueError] | str]
        | List[Dict[str, Dict[str, str | List[str]]] | None | str]
    ),
    class_str: str,
    raises: (
        List[None | str]
        | List[Dict | None | str]
        | List[Dict[str, str] | None | str]
        | List[Dict[str, str | List[str]] | None | str]
        | List[Dict[str, str] | None | type[ValueError] | str]
        | List[Dict[str, Dict[str, str | List[str]]] | None | str]
    ),
    expected: (
        List[None | str]
        | List[Dict | None | str]
        | List[Dict[str, str] | None | str]
        | List[Dict[str, str | List[str]] | None | str]
        | List[Dict[str, str] | None | type[ValueError] | str]
        | List[Dict[str, Dict[str, str | List[str]]] | None | str]
    ),
):
    context = does_not_raise() if raises is None else pytest.raises(raises)
    with context as reason:
        cpt = axis_component(parms)
        assert isinstance(cpt, Component)
        assert class_str in str(cpt.cls)

    if raises is not None and expected is not None:
        assert expected in str(reason)


@pytest.mark.parametrize(
    "structure, raises, expected",
    [
        [dict(motors="m1 m2".split()), None, None],
        [dict(motors=dict(m1=None, m2=None)), None, None],
        [dict(motors=dict(m1={}, m2={})), None, None],
        [dict(motors={"m1", "m2"}), AttributeError, "object has no attribute 'items'"],
        [dict(motors="m1"), AttributeError, "object has no attribute 'items'"],
        [
            dict(motors="m1 m2".split(), class_bases="Abcdefg"),
            TypeError,
            "Must be a list,",
        ],
        [
            dict(motors="m1 m2".split(), class_bases=["Abcdefg"]),
            ValueError,
            "Must use a dotted path,",
        ],
        [
            dict(motors="m1 m2".split(), class_bases=["xyz.Abcdefg"]),
            ModuleNotFoundError,
            "No module named 'xyz'",
        ],
        [dict(motors="m1 m2".split(), class_bases=[Mixin]), None, None],
        [dict(motors="m1 m2".split(), class_bases=[Mixin, MotorBundle]), None, None],
        [dict(motors="m1 m2".split(), class_name="Abcdefg"), None, None],
    ],
)
def test_motor_device_class_factory(
    structure: (
        List[Dict[str, List[LiteralString]] | None]
        | List[Dict[str, Dict[str, None]] | None]
        | List[Dict[str, Dict[str, Dict[Any, Any]]] | None]
        | List[Dict[str, set[str]] | type[AttributeError] | str]
        | List[Dict[str, str] | type[AttributeError] | str]
        | List[Dict[str, List[LiteralString] | str] | type[TypeError] | str]
        | List[Dict[str, List[LiteralString]] | type[ValueError] | str]
        | List[Dict[str, List[LiteralString]] | type[ModuleNotFoundError] | str]
        | List[Dict[str, List[LiteralString] | List[type[Mixin]]] | None]
        | List[Dict[str, List[LiteralString] | List[type[Mixin] | MotorBundle]] | None]
        | List[Dict[str, List[LiteralString] | str] | None]
    ),
    raises: (
        List[Dict[str, List[LiteralString]] | None]
        | List[Dict[str, Dict[str, None]] | None]
        | List[Dict[str, Dict[str, Dict[Any, Any]]] | None]
        | List[Dict[str, set[str]] | type[AttributeError] | str]
        | List[Dict[str, str] | type[AttributeError] | str]
        | List[Dict[str, List[LiteralString] | str] | type[TypeError] | str]
        | List[Dict[str, List[LiteralString]] | type[ValueError] | str]
        | List[Dict[str, List[LiteralString]] | type[ModuleNotFoundError] | str]
        | List[Dict[str, List[LiteralString] | List[type[Mixin]]] | None]
        | List[Dict[str, List[LiteralString] | List[type[Mixin] | MotorBundle]] | None]
        | List[Dict[str, List[LiteralString] | str] | None]
    ),
    expected: (
        List[Dict[str, List[LiteralString]] | None]
        | List[Dict[str, Dict[str, None]] | None]
        | List[Dict[str, Dict[str, Dict[Any, Any]]] | None]
        | List[Dict[str, set[str]] | type[AttributeError] | str]
        | List[Dict[str, str] | type[AttributeError] | str]
        | List[Dict[str, List[LiteralString] | str] | type[TypeError] | str]
        | List[Dict[str, List[LiteralString]] | type[ValueError] | str]
        | List[Dict[str, List[LiteralString]] | type[ModuleNotFoundError] | str]
        | List[Dict[str, List[LiteralString] | List[type[Mixin]]] | None]
        | List[Dict[str, List[LiteralString] | List[type[Mixin] | MotorBundle]] | None]
        | List[Dict[str, List[LiteralString] | str] | None]
    ),
):
    context = does_not_raise() if raises is None else pytest.raises(raises)
    with context as reason:
        Bundle = mb_class_factory(**structure)
        assert Bundle is not None

        for base in structure.get("class_bases", []):
            assert issubclass(Bundle, base)

        if issubclass(Bundle, Mixin):
            assert Bundle._mixin

        cname = structure.get("class_name")
        if cname is not None:
            assert cname in str(Bundle)

    if raises is not None and expected is not None:
        assert expected in str(reason)


@pytest.mark.parametrize(
    "structure, read, config, pvnames, raises, expected",
    [
        [{}, [], [], {}, TypeError, "Must provide a 'name'"],
        [dict(name="empty"), [], [], {}, None, None],
        [dict(name="s1", motors="m1 m2 m3".split()), [], [], {}, None, None],
        [
            dict(
                motors="not a dict or list",
                name="s2",
            ),
            [],
            [],
            {},
            TypeError,
            "Expected 'motors' as list or dict",
        ],
        [
            dict(
                name="s3",
                prefix="gp:",
                motors=dict(x="m1"),
            ),
            [],
            [],
            {"x.user_readback": "gp:m1.RBV"},
            None,
            None,
        ],
        [
            dict(
                name="s4",
                prefix="gp:",
                motors=["m1"],
            ),
            [],
            [],
            {"m1": "gp:m1"},
            None,
            None,
        ],
        [
            dict(
                name="s5",
                motors=dict(
                    theta=dict(prefix="gp:m3", labels=["dcm"]),
                    y1=dict(limits=[-50, 1], init_pos=-15, labels=["arm", "dcm"]),
                    z2=dict(limits=[-1, 300], init_pos=75, labels=["arm", "dcm"]),
                    ty1=dict(limits=[-10, 10], kind="config", labels=["table", "dcm"]),
                    ty2=dict(limits=[-10, 10], kind="config", labels=["table", "dcm"]),
                ),
            ),
            "theta y1 z2".split(),
            "ty1 ty2".split(),
            {
                "theta": "gp:m3",
            },
            None,
            None,
        ],
        [
            dict(
                name="s6",
                prefix="xyz:",
                motors=dict(
                    u="m11",
                    v="m12",
                    w="m13",
                    a=None,
                    b={
                        "class": "apstools.devices.PVPositionerSoftDoneWithStop",
                        "prefix": "",
                        "readback_pv": "gp:float14",
                        "setpoint_pv": "gp:float4",
                    },
                ),
            ),
            "u v w a b".split(),
            [],
            {
                "w": "xyz:m13",
                "b.readback": "xyz:gp:float14",
                "b.setpoint": "xyz:gp:float4",
            },
            None,
            None,
        ],
        [
            dict(
                name="s7",
                motors=dict(
                    psic=dict(
                        factory=dict(
                            function="hklpy2.diffract.diffractometer_class_factory",
                            reals="mu eta chi phi nu delta".split(),
                            geometry="APS POLAR",
                        ),
                    ),
                    table=dict(
                        factory=dict(
                            function=mb_class_factory,
                            motors="x1 x2 y1 y2 y3 z".split(),
                        ),
                    ),
                ),
            ),
            """
            psic.beam.wavelength 
            psic.h psic.k psic.l 
            psic.mu psic.eta psic.chi psic.phi psic.nu psic.delta
            table.x1 table.x2 table.y1 table.y2 table.y3 table.z
            """.split(),
            ["psic.beam.source_type", "psic.solver_signature"],
            {},
            None,
            None,
        ],
    ],
)
def test_motor_device_factory(
    structure: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
    read: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
    config: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
    pvnames: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
    raises: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
    expected: (
        List[type[TypeError] | str | Dict[Any, Any] | List[Any]]
        | List[Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[LiteralString]] | None | List[Any]]
        | List[Dict[str, str] | type[TypeError] | str | List[Any]]
        | List[Dict[str, str | Dict[str, str]] | Dict[str, str] | None | List[Any]]
        | List[Dict[str, str | List[str]] | Dict[str, str] | None | List[Any]]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, str | List[str]]
                    | Dict[str, List[int] | int | List[str]]
                    | Dict[str, List[int] | str | List[str]],
                ],
            ]
            | List[LiteralString]
            | Dict[str, str]
            | None
        ]
        | List[
            Dict[str, str | Dict[str, str | None | Dict[str, str]]] | List[LiteralString] | Dict[str, str] | None
        ]
        | List[
            Dict[
                str,
                str
                | Dict[
                    str,
                    Dict[str, Dict[str, str | List[LiteralString]]]
                    | Dict[str, Dict[str, Callable[..., Type] | List[LiteralString]]],
                ],
            ]
            | List[LiteralString]
            | List[str]
            | None
        ]
    ),
):
    context = does_not_raise() if raises is None else pytest.raises(raises)
    with context as reason:
        device = mb_creator(**structure)
        assert device is not None

        for attr in read:
            assert attr in device.read_attrs
        for attr in config:
            assert attr in device.configuration_attrs
        for attr, pv in pvnames.items():
            obj = getattr(device, attr)
            if hasattr(obj, "pvname"):
                assert obj.pvname == pv, f"{obj=}"
            elif hasattr(obj, "prefix"):
                assert obj.prefix == pv, f"{obj=}"

    if raises is not None and expected is not None:
        assert expected in str(reason)

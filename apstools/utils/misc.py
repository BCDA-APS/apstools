"""
Miscellaneous Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~call_signature_decorator
   ~cleanupText
   ~connect_pvlist
   ~count_child_devices_and_signals
   ~count_common_subdirs
   ~dictionary_table
   ~dynamic_import
   ~full_dotted_name
   ~itemizer
   ~listobjects
   ~pairwise
   ~print_RE_md
   ~redefine_motor_position
   ~render
   ~replay
   ~run_in_thread
   ~safe_ophyd_name
   ~split_quoted_line
   ~text_encode
   ~to_unicode_or_bust
   ~trim_string_for_EPICS
   ~unix
"""

import inspect
import logging
import pathlib
import re
import subprocess
import sys
import threading
import time
import warnings
from collections import OrderedDict, defaultdict
from functools import wraps
from typing import Any, Optional, Type, Union, cast

import ophyd
import pyRestTable
from bluesky import plan_stubs as bps
from bluesky.callbacks.best_effort import BestEffortCallback
from ophyd.ophydobj import OphydObject

from ..callbacks import spec_file_writer
from ._core import MAX_EPICS_STRINGOUT_LENGTH, TableStyle
from .profile_support import ipython_shell_namespace

logger = logging.getLogger(__name__)


def call_signature_decorator(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Get the names of all function parameters supplied by the caller.

    This is used to differentiate user-supplied parameters from as-defined
    parameters with the same value.

    Parameters
    ----------
    f : Callable[..., Any]
        The function to decorate.

    Returns
    -------
    Callable[..., Any]
        The decorated function.

    Notes
    -----
    HOW TO USE THIS DECORATOR:

    Decorate a function or method with this decorator *and* add an additional
    `_call_args=None` kwarg to the function. The function can test `_call_args`
    if a specific kwarg was supplied by the caller.

    Example::

        @call_signature_decorator
        def func1(a, b=1, c=True, _call_args=None):
            if 'c' in _call_args:  # Caller supplied this kwarg?
                pass

    With ``call_signature_decorator``, it is not possible to get the names
    of the positional arguments. Since positional parameters are not specified by
    name, such capability is not expected to become a requirement.

    See: https://stackoverflow.com/questions/14749328#58166804
        (how-to-check-whether-optional-function-parameter-is-set)
    """
    key = "_call_args"
    varnames = inspect.getfullargspec(f)[0]

    @wraps(f)
    def wrapper(*a: Any, **kw: Any) -> Any:
        kw[key] = set(list(varnames[: len(a)]) + list(kw.keys()))
        return f(*a, **kw)

    return wrapper


def cleanupText(text: str, replace: Optional[str] = "_") -> str:
    """
    Convert text so it can be used as a dictionary key.

    Given some input text string, return a clean version
    remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.

    Parameters
    ----------
    text : str
        The text to clean up.
    replace : Optional[str], optional
        Character to use for replacement. Default: "_"

    Returns
    -------
    str
        Cleaned up text string.
    """
    pattern = "[a-zA-Z0-9_]"
    if replace is None:
        replace = "_"

    def mapper(c: str) -> str:
        if re.match(pattern, c) is not None:
            return c
        return replace

    return "".join([mapper(c) for c in text])


def count_child_devices_and_signals(device: OphydObject) -> dict[str, int]:
    """
    Dict with number of children of this device. Keys: Device and Signal.

    Parameters
    ----------
    device : OphydObject
        The device to count children for.

    Returns
    -------
    dict[str, int]
        Dictionary with counts of devices and signals.
    """
    count = dict(Device=0, Signal=0)
    if hasattr(device, "walk_components"):  # Device has this attribute
        for item in device.walk_components():
            # assume if it is NOT a device, then it's a signal
            which = "Device" if item.item.is_device else "Signal"
            count[which] += 1
    else:
        count["Signal"] += 1
    return count


def count_common_subdirs(p1: Union[str, pathlib.Path], p2: Union[str, pathlib.Path]) -> int:
    """
    Count how many subdirectories are common to both file paths.

    Parameters
    ----------
    p1 : Union[str, pathlib.Path]
        First path to compare.
    p2 : Union[str, pathlib.Path]
        Second path to compare.

    Returns
    -------
    int
        Number of common subdirectories.
    """
    parts1 = pathlib.Path(p1).parts
    parts2 = pathlib.Path(p2).parts
    count = 0
    for x, y in zip(reversed(parts1), reversed(parts2)):
        if x != y:
            break
        count += 1
    if count == 0 and min(len(parts1), len(parts2)) > 0:
        # special case when first part of path is common
        if parts1[0] == parts2[0]:
            count = 1
    return count


def dictionary_table(dictionary: dict[str, Any], **kwargs: Any) -> Optional[pyRestTable.Table]:
    """
    Return a text table from dictionary.

    Dictionary keys in first column, values in second.

    Parameters
    ----------
    dictionary : dict[str, Any]
        Python dictionary to convert to table.
    **kwargs : Any
        Keyword arguments parameters are kept for compatibility with previous
        versions of apstools. They are ignored now.

    Returns
    -------
    Optional[pyRestTable.Table]
        pyRestTable.Table() object (multiline text table)
        or None if dictionary has no contents

    Example
    -------
    >>> RE.md
    {'login_id': 'jemian:wow.aps.anl.gov', 'beamline_id': 'developer', 
     'proposal_id': None, 'pid': 19072, 'scan_id': 10, 
     'version': {'bluesky': '1.5.2', 'ophyd': '1.3.3', 
                'apstools': '1.1.5', 'epics': '3.3.3'}}

    >>> print(dictionary_table(RE.md))
    =========== =============================================================================
    key         value
    =========== =============================================================================
    beamline_id developer
    login_id    jemian:wow.aps.anl.gov
    pid         19072
    proposal_id None
    scan_id     10
    version     {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}
    =========== =============================================================================
    """
    if len(dictionary) == 0:
        return None
    t = pyRestTable.Table()
    t.addLabel("key")
    t.addLabel("value")
    for k, v in sorted(dictionary.items()):
        t.addRow((k, str(v)))
    return t


def dynamic_import(full_path: str) -> Type[Any]:
    """
    Import the object given its import path as text.

    Parameters
    ----------
    full_path : str
        Full dotted path to the object to import.

    Returns
    -------
    Type[Any]
        The imported object.

    Raises
    ------
    ImportError
        If the import fails.
    """
    module_path, class_name = full_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def full_dotted_name(obj: Any) -> str:
    """
    Return the full dotted name of an object.

    Parameters
    ----------
    obj : Any
        The object to get the dotted name for.

    Returns
    -------
    str
        The full dotted name of the object.
    """
    return f"{obj.__module__}.{obj.__name__}"


def itemizer(fmt: str, items: list[Any]) -> str:
    """
    Format a list of items using the given format string.

    Parameters
    ----------
    fmt : str
        Format string to use for each item.
    items : list[Any]
        List of items to format.

    Returns
    -------
    str
        Formatted string.
    """
    return " ".join([fmt.format(item) for item in items])


def pairwise(iterable: list[Any]) -> list[tuple[Any, Any]]:
    """
    Return successive pairs of items from iterable.

    Parameters
    ----------
    iterable : list[Any]
        List of items to pair.

    Returns
    -------
    list[tuple[Any, Any]]
        List of pairs.

    Example
    -------
    >>> pairwise([1, 2, 3, 4])
    [(1, 2), (2, 3), (3, 4)]
    """
    a = iter(iterable)
    return list(zip(a, a))


def print_RE_md(
    dictionary: Optional[dict[str, Any]] = None,
    fmt: str = "simple",
    printing: bool = True,
) -> Optional[str]:
    """
    Print the metadata dictionary from a bluesky RunEngine.

    Parameters
    ----------
    dictionary : Optional[dict[str, Any]], optional
        Dictionary to print. If None, uses RE.md.
        Default: None
    fmt : str, optional
        Format to use for printing.
        Default: "simple"
    printing : bool, optional
        Whether to print the output.
        Default: True

    Returns
    -------
    Optional[str]
        Formatted string if printing is False, None otherwise.
    """
    if dictionary is None:
        dictionary = ipython_shell_namespace().get("RE", {}).md
    if dictionary is None:
        return None

    table = dictionary_table(dictionary)
    if table is None:
        return None

    if printing:
        print(table.reST(fmt=fmt))
        return None
    return table.reST(fmt=fmt)


def render(value: Any, sig_figs: int = 12) -> str:
    """
    Render a value as a string with specified precision.

    Parameters
    ----------
    value : Any
        Value to render.
    sig_figs : int, optional
        Number of significant figures to use.
        Default: 12

    Returns
    -------
    str
        Rendered string.
    """
    if isinstance(value, (int, float)):
        return f"{value:.{sig_figs}g}"
    return str(value)


def replay(
    headers: list[Any],
    callback: Optional[Callable[..., Any]] = None,
    sort: bool = True,
) -> None:
    """
    Replay a list of headers through a callback.

    Parameters
    ----------
    headers : list[Any]
        List of headers to replay.
    callback : Optional[Callable[..., Any]], optional
        Callback to use for replay.
        Default: None
    sort : bool, optional
        Whether to sort headers by time.
        Default: True
    """
    if callback is None:
        callback = BestEffortCallback()

    def as_header(run: Any) -> Any:
        """Convert run to header."""
        return run

    def increasing_time_sorter(run: Any) -> float:
        """Sort runs by increasing time."""
        return run.start["time"]

    def decreasing_time_sorter(run: Any) -> float:
        """Sort runs by decreasing time."""
        return -run.start["time"]

    if sort:
        if isinstance(sort, bool):
            sorter = increasing_time_sorter
        else:
            sorter = decreasing_time_sorter
        headers = sorted(headers, key=sorter)

    for header in headers:
        header = as_header(header)
        callback("start", header.start)
        for name, doc in header.documents():
            if name == "start":
                continue
            callback(name, doc)
        callback("stop", header.stop)


def run_in_thread(func: Callable[..., Any]) -> Callable[..., None]:
    """
    Decorator to run a function in a thread.

    Parameters
    ----------
    func : Callable[..., Any]
        Function to run in thread.

    Returns
    -------
    Callable[..., None]
        Decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()

    return wrapper


def safe_ophyd_name(text: str) -> str:
    """
    Convert text to a safe ophyd name.

    Parameters
    ----------
    text : str
        Text to convert.

    Returns
    -------
    str
        Safe ophyd name.
    """
    # Remove any characters that are not alphanumeric or underscore
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
    # Ensure the name starts with a letter
    if not text[0].isalpha():
        text = "x" + text
    return text


def split_quoted_line(line: str) -> list[str]:
    """
    Split a line into words, respecting quotes.

    Parameters
    ----------
    line : str
        Line to split.

    Returns
    -------
    list[str]
        List of words.
    """
    words = []
    current = []
    in_quotes = False
    quote_char = None

    for char in line:
        if char in '"\'':
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif quote_char == char:
                in_quotes = False
                quote_char = None
            else:
                current.append(char)
        elif char.isspace() and not in_quotes:
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        words.append("".join(current))

    return words


def text_encode(source: str) -> bytes:
    """
    Encode text to bytes.

    Parameters
    ----------
    source : str
        Text to encode.

    Returns
    -------
    bytes
        Encoded text.
    """
    return source.encode("utf-8")


def to_unicode_or_bust(obj: Any, encoding: str = "utf-8") -> str:
    """
    Convert object to unicode string.

    Parameters
    ----------
    obj : Any
        Object to convert.
    encoding : str, optional
        Encoding to use.
        Default: "utf-8"

    Returns
    -------
    str
        Unicode string.
    """
    if isinstance(obj, str):
        return obj
    if isinstance(obj, bytes):
        return obj.decode(encoding)
    return str(obj)


def trim_string_for_EPICS(msg: str) -> str:
    """
    Trim string to EPICS maximum length.

    Parameters
    ----------
    msg : str
        String to trim.

    Returns
    -------
    str
        Trimmed string.
    """
    return msg[:MAX_EPICS_STRINGOUT_LENGTH]


def unix(command: str, raises: bool = True) -> tuple[int, str, str]:
    """
    Run a unix command.

    Parameters
    ----------
    command : str
        Command to run.
    raises : bool, optional
        Whether to raise an exception on error.
        Default: True

    Returns
    -------
    tuple[int, str, str]
        Tuple of (return code, stdout, stderr).

    Raises
    ------
    subprocess.CalledProcessError
        If raises is True and command fails.
    """
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = process.communicate()
    if raises and process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    return process.returncode, stdout, stderr


def listobjects(
    show_pv=True,
    printing=None,  # DEPRECATED
    verbose=False,
    symbols=None,
    child_devices=False,
    child_signals=False,
    table_style=TableStyle.pyRestTable,
):
    """
    Show all the ophyd Signal and Device objects defined as globals.

    PARAMETERS

    show_pv
        *bool* :
        If True, also show relevant EPICS PV, if available.
        (default: True)
    printing *bool* :
        Deprecated.
    verbose
        *bool* :
        If True, also show ``str(obj``.
        (default: False)
    symbols
        *dict* :
        If None, use global symbol table.
        If not None, use provided dictionary.
        (default: ``globals()``)
    child_devices
        *bool* :
        If True, also show how many Devices are children of this device.
        (default: False)
    child_signals
        *bool* :
        If True, also show how many Signals are children of this device.
        (default: False)
    table_style *object* :
        Either ``apstools.utils.TableStyle.pandas`` (default) or
        using values from :class:`apstools.utils.TableStyle`.

        .. note:: ``pandas.DataFrame`` wll truncate long text
           to at most 50 characters.

    RETURNS

    object:
        Instance of ``pyRestTable.Table()``

    EXAMPLE::

        In [1]: listobjects()
        ======== ================================ =============
        name     ophyd structure                  EPICS PV
        ======== ================================ =============
        adsimdet MySingleTriggerSimDetector       vm7SIM1:
        m1       EpicsMotor                       vm7:m1
        m2       EpicsMotor                       vm7:m2
        m3       EpicsMotor                       vm7:m3
        m4       EpicsMotor                       vm7:m4
        m5       EpicsMotor                       vm7:m5
        m6       EpicsMotor                       vm7:m6
        m7       EpicsMotor                       vm7:m7
        m8       EpicsMotor                       vm7:m8
        noisy    EpicsSignalRO                    vm7:userCalc1
        scaler   ScalerCH                         vm7:scaler1
        shutter  SimulatedApsPssShutterWithStatus
        ======== ================================ =============

        Out[1]: <pyRestTable.rest_table.Table at 0x7fa4398c7cf8>

        In [2]:

    (new in apstools release 1.1.8)
    """
    if symbols is None:
        g = ipython_shell_namespace()  # the default choice
        if len(g) == 0:
            g = globals()  # ultimate fallback
    else:
        g = symbols
    g = {k: v for k, v in sorted(g.items()) if isinstance(v, OphydObject)}
    # Now, g is a dict of the objects to be listed.

    # Build the table as a dict keyed by column names.
    contents = defaultdict(list)
    for k, v in g.items():
        contents["name"].append(k)
        contents["class"].append(v.__class__.__name__)
        if show_pv:
            if hasattr(v, "pvname"):
                pv = v.pvname
            elif hasattr(v, "prefix"):
                pv = v.prefix
            else:
                pv = ""
            contents["PV (or prefix)"].append(pv)
        if verbose:
            contents["object"].append(v)
        if child_devices or child_signals:
            nchildren = count_child_devices_and_signals(v)
            if child_devices:
                contents["#devices"].append(nchildren["Device"])
            if child_signals:
                contents["#signals"].append(nchildren["Signal"])
        contents["label(s)"].append(" ".join(v._ophyd_labels_))

    # Render the dict as a table.
    table = table_style.value(contents)

    if printing is not None:
        warnings.warn(f"Keyword argument 'printing={printing}' is deprecated.")

    return table


def connect_pvlist(pvlist, wait=True, timeout=2, poll_interval=0.1):
    """
    Given list of EPICS PV names, return dict of EpicsSignal objects.

    PARAMETERS

    pvlist
        *[str]* :
        list of EPICS PV names
    wait
        *bool* :
        should wait for EpicsSignal objects to connect
        (default: ``True``)
    timeout
        *float* :
        maximum time to wait for PV connections, seconds
        (default: 2.0)
    poll_interval
        *float* :
        time to sleep between checks for PV connections, seconds
        (default: 0.1)
    """
    obj_dict = OrderedDict()
    for item in pvlist:
        if len(item.strip()) == 0:
            continue
        pvname = item.strip()
        oname = "signal_{}".format(len(obj_dict))
        obj = ophyd.EpicsSignal(pvname, name=oname)
        obj_dict[oname] = obj

    if wait:
        times_up = time.time() + max(0, timeout)
        poll_interval = max(0.01, poll_interval)
        waiting = True
        while waiting and time.time() < times_up:
            time.sleep(poll_interval)
            waiting = False in [sig.connected for sig in obj_dict.values()]

        if waiting:
            # If did not connect all, revise with only the connected PVs
            # and report the unconncetd PVs.
            revised_dict = OrderedDict()
            for label, sig in obj_dict.items():
                if sig.connected:
                    revised_dict[label] = sig
                else:
                    print(f"Could not connect {sig.pvname}")
            if len(revised_dict) == 0:
                raise RuntimeError("Could not connect any PVs in the list")
            obj_dict = revised_dict

    return obj_dict


def redefine_motor_position(motor, new_position):
    """Set EPICS motor record's user coordinate to ``new_position``."""
    yield from bps.mv(motor.set_use_switch, 1)
    yield from bps.mv(motor.user_setpoint, new_position)
    yield from bps.mv(motor.set_use_switch, 0)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

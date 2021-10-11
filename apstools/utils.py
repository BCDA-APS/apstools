"""
Various utilities

.. autosummary::

   ~cleanupText
   ~command_list_as_table
   ~connect_pvlist
   ~copy_filtered_catalog
   ~db_query
   ~apstools._utils.device_info.device_read2table
   ~dictionary_table
   ~EmailNotifications
   ~ExcelDatabaseFileBase
   ~ExcelDatabaseFileGeneric
   ~ExcelReadError
   ~findbyname
   ~findbypv
   ~findCatalogsInNamespace
   ~full_dotted_name
   ~getCatalog
   ~getDatabase
   ~getDefaultCatalog
   ~getDefaultDatabase
   ~getDefaultNamespace
   ~getRunData
   ~getRunDataValue
   ~getStreamValues
   ~ipython_profile_name
   ~itemizer
   ~json_export
   ~json_import
   ~apstools._utils.device_info.listdevice
   ~apstools._utils.device_info.listdevice_1_5_2
   ~listobjects
   ~apstools._utils.list_plans.listplans
   ~listRunKeys
   ~ListRuns
   ~listruns
   ~listruns_v1_4
   ~apstools._utils.device_info.object_explorer
   ~apstools._utils.override_parameters.OverrideParameters
   ~pairwise
   ~print_RE_md
   ~print_snapshot_list
   ~quantify_md_key_use
   ~redefine_motor_position
   ~replay
   ~rss_mem
   ~run_in_thread
   ~safe_ophyd_name
   ~select_live_plot
   ~select_mpl_figure
   ~split_quoted_line
   ~summarize_runs
   ~text_encode
   ~to_unicode_or_bust
   ~trim_plot_by_name
   ~trim_plot_lines
   ~trim_string_for_EPICS
   ~unix

"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

from bluesky import plan_stubs as bps
from bluesky.callbacks.best_effort import BestEffortCallback
from collections import defaultdict
from collections import OrderedDict
from databroker._drivers.mongo_normalized import BlueskyMongoCatalog
from dataclasses import dataclass
from email.mime.text import MIMEText
from event_model import NumpyEncoder

import databroker
import databroker.queries
import datetime
import json
import logging
import math
import openpyxl
import openpyxl.utils.exceptions
import ophyd
import os
import pandas as pd
import psutil
import pyRestTable
import re
import smtplib
import subprocess
import sys
import threading
import time
import typing
import warnings
import zipfile

from .filewriters import _rebuild_scan_command
from ._utils import *


logger = logging.getLogger(__name__)

MAX_EPICS_STRINGOUT_LENGTH = 40

FIRST_DATA = "1995-01-01"
LAST_DATA = "2100-12-31"


class ExcelReadError(openpyxl.utils.exceptions.InvalidFileException):
    """
    Exception when reading Excel spreadsheet.

    .. index:: apstools Exception; ExcelReadError
    """


def cleanupText(text):
    """
    convert text so it can be used as a dictionary key

    Given some input text string, return a clean version
    remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    """
    pattern = "[a-zA-Z0-9_]"

    def mapper(c):
        if re.match(pattern, c) is not None:
            return c
        return "_"

    return "".join([mapper(c) for c in text])


def command_list_as_table(commands, show_raw=False):
    """
    format a command list as a pyRestTable.Table object
    """
    tbl = pyRestTable.Table()
    tbl.addLabel("line #")
    tbl.addLabel("action")
    tbl.addLabel("parameters")
    if show_raw:  # only the developer might use this
        tbl.addLabel("raw input")
    for command in commands:
        action, args, line_number, raw_command = command
        row = [line_number, action, ", ".join(map(str, args))]
        if show_raw:
            row.append(str(raw_command))
        tbl.addRow(row)
    return tbl


def dictionary_table(dictionary, **kwargs):
    """
    return a text table from ``dictionary``

    PARAMETERS

    dictionary
        *dict* :
        Python dictionary

    Note:  Keyword arguments parameters
    are kept for compatibility with previous
    versions of apstools.  They are ignored now.

    RETURNS

    table
        *object* or ``None`` :
        ``pyRestTable.Table()`` object (multiline text table)
        or ``None`` if dictionary has no contents

    EXAMPLE::

        In [8]: RE.md
        Out[8]: {'login_id': 'jemian:wow.aps.anl.gov', 'beamline_id': 'developer', 'proposal_id': None, 'pid': 19072, 'scan_id': 10, 'version': {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}}

        In [9]: print(dictionary_table(RE.md))
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
        return
    t = pyRestTable.Table()
    t.addLabel("key")
    t.addLabel("value")
    for k, v in sorted(dictionary.items()):
        t.addRow((k, str(v)))
    return t


def full_dotted_name(obj):
    """
    Return the full dotted name

    The ``.dotted_name`` property does not include the
    name of the root object.  This routine adds that.

    see: https://github.com/bluesky/ophyd/pull/797
    """
    names = []
    while obj.parent is not None:
        names.append(obj.attr_name)
        obj = obj.parent
    names.append(obj.name)
    return ".".join(names[::-1])


def getDatabase(db=None, catalog_name=None):
    """
    Return Bluesky database using keyword guides or default choice.

    PARAMETERS

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``
        (default: see ``catalog_name`` keyword argument)

    catalog_name
        *str* :
        Name of databroker v2 catalog, used when supplied
        ``db`` is ``None``.
        (default: catalog with most recent run timestamp)

    RETURNS

    object or ``None``:
        Bluesky database, an instance of ``databroker.catalog``

    (new in release 1.4.0)
    """
    if not hasattr(db, "v2"):
        # fmt: off
        if (
            hasattr(catalog_name, "name")
            and catalog_name in databroker.catalog
        ):
            # in case a catalog was passed as catalog_name
            db = catalog_name
        elif catalog_name is None:
            db = getDefaultDatabase()
        else:
            db = databroker.catalog[catalog_name]
        # fmt: on
    return db.v2


def getDefaultDatabase():
    """
    Find the "default" database (has the most recent run).

    Note that here, *database* and *catalog* mean the same.

    This routine looks at all the database instances defined in the
    current session (console or notebook).  If there is only one or no
    database instances defined as objects in the current session, the
    choice is simple.  When there is more than one database instance in
    the current session, then the one with the most recent run timestamp
    is selected.  In the case (as happens when starting with a new
    database) that the current database has **no** runs *and* another
    database instance is defined in the session *and* that additional
    database has runs in it (such as the previous database), then the
    database with the newest run timestamp (and not the newer empty
    database) will be chosen.

    RETURNS

    object or ``None``:
        Bluesky database, an instance of ``databroker.catalog``

    (new in release 1.4.0)
    """
    # look through the console namespace
    g = ipython_shell_namespace()
    if len(g) == 0:
        # ultimate fallback
        g = globals()

    # note all database instances in memory
    db_list = []
    for k, v in g.items():
        if hasattr(v, "__class__") and not k.startswith("_"):
            end = v.__class__.__name__.split(".")[-1]
            if end in ("Broker", "BlueskyMongoCatalog"):
                db_list.append(v)

    # easy decisions first
    if len(db_list) == 0:
        return None
    if len(db_list) == 1:
        return db_list[0]

    # get the most recent run from each
    time_ref = {}
    for cat_name in list(databroker.catalog):
        cat = databroker.catalog[cat_name]
        if cat in db_list:
            print(cat_name, cat.name)
            if len(cat) > 0:
                run = cat.v2[-1]
                t = run.metadata["start"]["time"]
            else:
                t = 0
            time_ref[cat_name] = t, cat

    # pick the highest number for time
    highest = max([v[0] for v in time_ref.values()])
    choices = [v[1] for v in time_ref.values() if v[0] == highest]
    if len(choices) == 0:
        return None
    # return the catalog with the most recent timestamp
    return sorted(choices)[-1]


def db_query(db, query):
    """
    Searches the databroker v2 database.

    PARAMETERS

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``.

    query
        *dict* :
        Search parameters.

    RETURNS

    *object* :
        Bluesky database, an instance of ``databroker.catalog``
        satisfying the ``query`` parameters.

    .. seealso::

       :func:`databroker.catalog.search`
    """

    if query is None:
        return db

    since = query.pop("since", None)
    until = query.pop("until", None)

    if since or until:
        if not since:
            since = FIRST_DATA
        if not until:
            until = LAST_DATA

        # fmt: off
        _db = db.v2.search(
            databroker.queries.TimeRange(since=since, until=until)
        )
        # fmt: on
    else:
        _db = db

    if len(query) != 0:
        _db = _db.v2.search(query)

    return _db


def getRunData(scan_id, db=None, stream="primary", query=None, use_v1=True):
    """
    Convenience function to get the run's data.  Default is the ``primary`` stream.

    PARAMETERS

    scan_id
        *int* or *str* :
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.

    stream
        *str* :
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'

    query
        *dict* :
        mongo query dictionary, used to filter the results
        Default: ``{}``

        see: https://docs.mongodb.com/manual/reference/operator/query/

    use_v1
        *bool* :
        Chooses databroker API version between 'v1' or 'v2'.
        Default: ``True`` (meaning use the v1 API)

    (new in apstools 1.5.1)
    """
    cat = getCatalog(db)
    if query:
        cat = db_query(cat, query)

    stream = stream or "primary"

    if use_v1 is None or use_v1:
        run = cat.v1[scan_id]
        if stream in run.stream_names:
            return run.table(stream_name=stream)
    else:
        run = cat.v2[scan_id]
        if hasattr(run, stream):
            return run[stream].read().to_dataframe()

    raise AttributeError(f"No such stream '{stream}' in run '{scan_id}'.")


def getRunDataValue(
    scan_id, key, db=None, stream="primary", query=None, idx=-1, use_v1=True
):
    """
    Convenience function to get value of key in run stream.

    Defaults are last value of key in primary stream.

    PARAMETERS

    scan_id
        *int* or *str* :
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).

    key
        *str* :
        Name of the key (data column) in the table of the stream's data.
        Must match *identically*.

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.

    stream
        *str* :
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'

    query
        *dict* :
        mongo query dictionary, used to filter the results
        Default: ``{}``

        see: https://docs.mongodb.com/manual/reference/operator/query/

    idx
        *int* or *str* :
        List index of value to be returned from column of table.
        Can be ``0`` for first value, ``-1`` for last value, ``"mean"``
        for average value, or ``"all"`` for the full list of values.
        Default: ``-1``

    use_v1
        *bool* :
        Chooses databroker API version between 'v1' or 'v2'.
        Default: ``True`` (meaning use the v1 API)

    (new in apstools 1.5.1)
    """
    if idx is None:
        idx = -1
    try:
        _idx = int(idx)
    except ValueError:
        _idx = str(idx).lower()

    if isinstance(_idx, str) and _idx not in "all mean".split():
        raise KeyError(
            f"Did not understand 'idx={idx}', use integer, 'all', or 'mean'."
        )

    stream = stream or "primary"

    table = getRunData(scan_id, db=db, stream=stream, query=query)

    if key not in table:
        raise KeyError(f"'{key}' not found in scan {scan_id} stream '{stream}'.")
    data = table[key]

    if _idx == "all":
        return data.values
    elif _idx == "mean":
        return data.mean()
    elif (0 <= _idx < len(data)) or (_idx < 0):
        return data.values[_idx]
    raise KeyError(
        f"Cannot reference idx={idx} in scan {scan_id} stream'{stream}' key={key}."
    )


def getStreamValues(
    scan_id, key_fragment="", db=None, stream="baseline", query=None, use_v1=True
):
    """
    Get values from a previous scan stream in a databroker catalog.

    Optionally, select only those data with names including ``key_fragment``.

    .. tip::

        If the output is truncated, use
        ``pd.set_option('display.max_rows', 300)``
        to increase the number of rows displayed.

    PARAMETERS

    scan_id
        *int* or *str* :
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).

    key_fragment
        *str* :
        Part or all of key name to be found in selected stream.
        For instance, if you specify ``key_fragment="lakeshore"``,
        it will return all the keys that include ``lakeshore``.

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.

    stream
        *str* :
        Name of the bluesky data stream to obtain the data.
        Default: 'baseline'

    query
        *dict* :
        mongo query dictionary, used to filter the results
        Default: ``{}``

        see: https://docs.mongodb.com/manual/reference/operator/query/

    use_v1
        *bool* :
        Chooses databroker API version between 'v1' or 'v2'.
        Default: ``True`` (meaning use the v1 API)

    RETURNS

    *object* :
        pandas DataFrame with values from selected stream, search_string, and query

        see: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

    (new in apstools 1.5.1)
    """
    if key_fragment is None:
        key_fragment = ""
    if use_v1 is None:
        use_v1 = True

    data = getRunData(scan_id, db=db, stream=stream, query=query, use_v1=use_v1)

    indices = [1, 2] if len(data["time"]) == 2 else [1]
    dd = {}

    # date_format = "%m/%d/%y %H:%M:%S"  # common in US
    date_format = "%y-%m-%d %H:%M:%S"  # modified ISO8601

    # fmt: off
    key = "time"
    dd[key] = [
        data[key][i].strftime(date_format)
        for i in indices
    ]
    # fmt: on

    for key in sorted(data.keys()):
        if key_fragment in key:
            dd[key] = [data[key][i] for i in indices]

    return pd.DataFrame(dd).transpose()


def listRunKeys(
    scan_id,
    key_fragment="",
    db=None,
    stream="primary",
    query=None,
    strict=False,
    use_v1=True,
):
    """
    Convenience function to list all keys (column names) in the scan's stream (default: primary).

    PARAMETERS

    scan_id
        *int* or *str* :
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).

    key_fragment
        *str* :
        Part or all of key name to be found in selected stream.
        For instance, if you specify ``key_fragment="lakeshore"``,
        it will return all the keys that include ``lakeshore``.

    db
        *object* :
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.

    stream
        *str* :
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'

    query
        *dict* :
        mongo query dictionary, used to filter the results
        Default: ``{}``

        see: https://docs.mongodb.com/manual/reference/operator/query/

    strict
        *bool* :
        Should the ``key_fragment`` be matched identically (``strict=True``)
        or matched by lower case comparison (``strict=False``)?
        Default: ``False``

    use_v1
        *bool* :
        Chooses databroker API version between 'v1' or 'v2'.
        Default: ``True`` (meaning use the v1 API)

    (new in apstools 1.5.1)
    """
    table = getRunData(scan_id, db=db, stream=stream, query=query, use_v1=use_v1)

    # fmt: off
    if len(key_fragment):
        output = [
            col
            for col in table.columns
            if (
                (strict and key_fragment in col)
                or (not strict and key_fragment.lower() in col.lower())
            )
        ]
    else:
        output = list(table.columns)
    # fmt: on
    return output


def itemizer(fmt, items):
    """Format a list of items."""
    return [fmt % k for k in items]


def getCatalog(ref=None):
    if isinstance(ref, str):  # and ref in databroker.catalog:
        return databroker.catalog[ref]
    if ref is not None and hasattr(ref, "v2"):
        return ref.v2

    cat = getDefaultCatalog()
    if cat is None:
        raise ValueError("Cannot identify default databroker catalog.")
    return cat


def findCatalogsInNamespace():
    g = {}
    g.update(getDefaultNamespace())
    ns_cats = {}
    for k, v in g.items():
        if not k.startswith("_") and hasattr(v, "__class__"):
            try:
                if hasattr(v.v2, "container") and hasattr(v.v2, "metadata"):
                    ns_cats[k] = v
            except (AttributeError, TypeError):
                continue
    return ns_cats


def getDefaultCatalog():
    cats = findCatalogsInNamespace()
    if len(cats) == 1:
        return cats[list(cats.keys())[0]]
    if len(cats) > 1:
        # fmt: off
        choices = "   ".join([
            f"{k} ({v.name})"
            for k, v in cats.items()
        ])
        # fmt: on
        raise ValueError(
            "No catalog defined.  "
            "Multiple catalog objects available."
            "  Specify one of these:"
            f" {choices}"
        )

    cats = list(databroker.catalog)
    if len(cats) == 1:
        return databroker.catalog[cats[0]]
    if len(cats) > 1:
        choices = "   ".join([f'databroker.catalog["{k}"]' for k in cats])
        raise ValueError(
            "No catalog defined.  "
            "Multiple catalog configurations available."
            "  Create specific catalog object from one of these commands:"
            f" {choices}"
        )

    raise ValueError("No catalogs available.")


def getDefaultNamespace():
    """
    get the IPython shell's namespace dictionary (or globals() if not found)
    """
    try:
        from IPython import get_ipython

        ns = get_ipython().user_ns
    except (ModuleNotFoundError, AttributeError):
        ns = globals()
    return ns


@dataclass
class ListRuns:
    """
    List the runs from the given catalog according to some options.

    EXAMPLE::

        ListRuns(cat).to_dataframe()

    PUBLIC METHODS

    .. autosummary::

        ~to_dataframe
        ~to_table
        ~parse_runs

    INTERNAL METHODS

    .. autosummary::

        ~_get_by_key
        ~_check_cat
        ~_apply_search_filters
        ~_check_keys

    """

    cat: object = None
    query: dict = None
    keys: str = None
    missing: str = ""
    num: int = 20
    reverse: bool = True
    since: str = None
    sortby: str = "time"
    timefmt: str = "%Y-%m-%d %H:%M:%S"
    until: str = None
    ids: "typing.Any" = None

    _default_keys = "scan_id time plan_name detectors"

    def _get_by_key(self, md, key):
        """
        Get run's metadata value by key.

        Look in ``start`` document first.
        If not found, look in ``stop`` document.
        If not found, report using ``self.missing``.

        If ``key`` is found but value is None, report as ``self.missing``.

        The ``time`` key will be formatted by the ``self.timefmt`` value.
        See https://strftime.org/ for examples.  The special ``timefmt="raw"``
        is used to report time as the raw value (floating point time as used in
        python's ``time.time()``).

        A special syntax of ``key`` allows reporting of keys in other
        metadata subdictionaries.  The syntax is ``doc.key`` (such as
        specifying the ``time`` key  from the ``stop`` document:
        ``stop.time``) where a ``.`` is used to separate the
        subdictionary name (``doc``) from the ``key``.
        **Note**:
        It is not possible to ``sortby`` the dotted-key syntax
        at this time.
        """
        v = None
        if key == "time":
            v = md["start"][key]
            if self.timefmt != "raw":
                ts = datetime.datetime.fromtimestamp(v)
                v = ts.strftime(self.timefmt)
        elif key in md["start"]:
            v = md["start"].get(key, self.missing)
        elif md["stop"] and key in md["stop"]:
            v = md["stop"].get(key, self.missing)
        elif len(key.split(".")) == 2:
            # dotted-key syntax
            doc, key = key.split(".")
            if md[doc] is not None:
                v = md[doc].get(key, self.missing)
                if key == "time" and self.timefmt != "raw":
                    ts = datetime.datetime.fromtimestamp(v)
                    v = ts.strftime(self.timefmt)
        return v or self.missing

    def _check_cat(self):
        if self.cat is None:
            self.cat = getCatalog()

    def _apply_search_filters(self):
        """Search for runs from the catalog."""
        since = self.since or FIRST_DATA
        until = self.until or LAST_DATA
        self._check_cat()
        query = {}
        query.update(databroker.queries.TimeRange(since=since, until=until))
        query.update(self.query or {})
        cat = self.cat.v2.search(query)
        return cat

    def parse_runs(self):
        """Parse the runs for the given metadata keys.  Return a dict."""
        self._check_keys()
        cat = self._apply_search_filters()

        def _sort(uid):
            """Sort runs in desired order based on metadata key."""
            md = self.cat[uid].metadata
            for doc in "start stop".split():
                if md[doc] and self.sortby in md[doc]:
                    return md[doc][self.sortby] or self.missing
            return self.missing

        num_runs_requested = min(abs(self.num), len(cat))
        results = {k: [] for k in self.keys}
        sequence = ()  # iterable of run uids

        if self.ids is not None:
            sequence = []
            for k in self.ids:
                try:
                    cat[k]  # try to access the run using `k`
                    sequence.append(k)
                except Exception as exc:
                    logger.warning(
                        "Could not find run %s in search of catalog %s: %s",
                        k,
                        self.cat.name,
                        exc,
                    )
        else:
            if isinstance(cat, BlueskyMongoCatalog) and self.sortby == "time":
                if self.reverse:
                    # the default rendering: from MongoDB in reverse time order
                    sequence = iter(cat)
                else:
                    # by increasing time order
                    sequence = [uid for uid in cat][::-1]
            else:
                # full search in Python
                sequence = sorted(cat.keys(), key=_sort, reverse=self.reverse)

        count = 0
        for uid in sequence:
            run = cat[uid]
            for k in self.keys:
                results[k].append(self._get_by_key(run.metadata, k))
            count += 1
            if count >= num_runs_requested:
                break
        return results

    def _check_keys(self):
        """Check that self.keys is a list of strings."""
        self.keys = self.keys or self._default_keys
        if isinstance(self.keys, str) and self.keys.find(" ") >= 0:
            # convert a space-delimited string of names
            self.keys = self.keys.split()

    def to_dataframe(self):
        """Output as pandas DataFrame object"""
        dd = self.parse_runs()
        return pd.DataFrame(dd, columns=self.keys)

    def to_table(self, fmt=None):
        """Output as pyRestTable object."""
        dd = self.parse_runs()

        table = pyRestTable.Table()
        rows = []
        for label, values in dd.items():
            table.addLabel(label)
            rows.append(values)
        table.rows = list(zip(*rows))

        return table.reST(fmt=fmt or "simple")


def listruns(
    cat=None,
    keys=None,
    missing="",
    num=20,
    printing="smart",
    reverse=True,
    since=None,
    sortby="time",
    tablefmt="dataframe",
    timefmt="%Y-%m-%d %H:%M:%S",
    until=None,
    ids=None,
    **query,
):
    """
    List runs from catalog.

    This function provides a thin interface to the highly-reconfigurable
    ``ListRuns()`` class in this package.

    For the old version of this function, see
    ``listruns_v1_4()``.  That code was last
    updated in apstools version 1.4.1.  It
    will be removed some time in the future.

    PARAMETERS

    cat
        *object* :
        Instance of databroker v1 or v2 catalog.
    keys
        *str* or *[str]* or None:
        Include these additional keys from the start document.
        (default: ``None`` means ``"scan_id time plan_name detectors"``)
    missing
        *str*:
        Test to report when a value is not available.
        (default: ``""``)
    ids
        *[int]* or *[str]*:
        List of ``uid`` or ``scan_id`` value(s).
        Can mix different kinds in the same list.
        Also can specify offsets (e.g., ``-1``).
        According to the rules for ``databroker`` catalogs,
        a string is a ``uid`` (partial representations allowed),
        an int is ``scan_id`` if positive or an offset if negative.
        (default: ``None``)
    num
        *int* :
        Make the table include the ``num`` most recent runs.
        (default: ``20``)
    printing
        *bool* or ``"smart"``:
        If ``True``, print the table to stdout.
        If ``"smart"``, then act as shown below.
        (default: ``True``)

        ================  ===================
        session           action(s)
        ================  ===================
        python session    print and return ``None``
        Ipython console   return ``DataFrame`` object
        Jupyter notebook  return ``DataFrame`` object
        ================  ===================

    reverse
        *bool* :
        If ``True``, sort in descending order by ``sortby``.
        (default: ``True``)
    since
        *str* :
        include runs that started on or after this ISO8601 time
        (default: ``"1995-01-01"``)
    sortby
        *str* :
        Sort columns by this key, found by exact match in either
        the ``start`` or ``stop`` document.
        (default: ``"time"``)
    tablefmt
        *str* :
        When returning an object, specify which type
        of object to return.
        (default: ``"dataframe",``)

        ========== ==============
        value      object
        ========== ==============
        dataframe  ``pandas.DataFrame``
        table      ``str(pyRestTable.Table)``
        ========== ==============

    timefmt
        *str* :
        The ``time`` key (also includes keys ``"start.time"`` and  ``"stop.time"``)
        will be formatted by the ``self.timefmt`` value.
        See https://strftime.org/ for examples.  The special ``timefmt="raw"``
        is used to report time as the raw value (floating point time as used in
        python's ``time.time()``).
        (default: ``"%Y-%m-%d %H:%M:%S",``)
    until
        *str* :
        include runs that started before this ISO8601 time
        (default: ``2100-12-31``)
    ``**query``
        *dict* :
        Any additional keyword arguments will be passed to
        the databroker to refine the search for matching runs
        using the ``mongoquery`` package.

    RETURNS

    object:
        ``None`` or ``str`` or ``pd.DataFrame()`` object

    EXAMPLE::

        TODO

    (new in release 1.5.0)
    """

    lr = ListRuns(
        cat=cat,
        keys=keys,
        missing=missing,
        num=num,
        reverse=reverse,
        since=since,
        sortby=sortby,
        timefmt=timefmt,
        until=until,
        ids=ids,
    )

    tablefmt = tablefmt or "dataframe"
    if tablefmt == "dataframe":
        obj = lr.to_dataframe()
    else:
        obj = lr.to_table()

    if printing:
        if lr.cat is not None:
            print(f"catalog: {lr.cat.name}")
        print(obj)
        return
    return obj


def listruns_v1_4(
    num=20,
    keys=None,
    printing=True,
    show_command=True,
    db=None,
    catalog_name=None,
    exit_status=None,
    since=None,
    until=None,
    **db_search_terms,
):
    """
    DEPRECATED: Use newer ``listruns()`` instead.

    make a table of the most recent runs (scans)

    PARAMETERS

    num
        *int* :
        Make the table include the ``num`` most recent runs.
        (default: ``20``)
    keys
        *[str]* :
        Include these additional keys from the start document.
        (default: ``[]``)
    printing
        *bool* :
        If ``True``, print the table to stdout
        (default: ``True``)
    show_command
        *bool* :
        If ``True``, show the (reconstructed) full command,
        but truncate it to no more than 40 characters)
        (note: This command is reconstructed from keys in the start
        document so it will not be exactly as the user typed.)
        (default: ``True``)
    db
        *object* :
        Instance of databroker v1 ``Broker`` or
        v2 ``BlueskyMongoCatalog``.
        (default: see ``catalog_name`` keyword argument)
    catalog_name
        *str* :
        Name of databroker v2 catalog, used when the supplied
        ``db`` is ``None``.
        (default: catalog with most recent run timestamp)
        (new in release 1.3.0)
    since
        *str* :
        include runs that started on or after this ISO8601 time
        (default: ``1995-01-01``)
    until
        *str* :
        include runs that started before this ISO8601 time
        (default: ``2100-12-31``)
    db_search_terms
        *dict* :
        Any additional keyword arguments will be passed to
        the databroker to refine the search for matching runs.

    RETURNS

    object:
        Instance of ``pyRestTable.Table()``

    EXAMPLE::

        In [2]: from apstools import utils as APS_utils

        In [3]: APS_utils.listruns(num=5, keys=["proposal_id","pid"])
        ========= ========================== ======= ======= ======================================== =========== ===
        short_uid date/time                  exit    scan_id command                                  proposal_id pid
        ========= ========================== ======= ======= ======================================== =========== ===
        5f2bc62   2019-03-10 22:27:57.803193 success 3       fly()
        ef7777d   2019-03-10 22:27:12.449852 success 2       fly()
        8048ea1   2019-03-10 22:25:01.663526 success 1       scan(detectors=['calcs_calc2_val'],  ...
        83ad06d   2019-03-10 22:19:14.352157 success 4       fly()
        b713d46   2019-03-10 22:13:26.481118 success 3       fly()
        ========= ========================== ======= ======= ======================================== =========== ===

        In [100]: listruns(keys=["file_name",], since="2020-02-06", until="2020-02-07", num=10, plan_name="lambda_test", exit_status="success")
            ...:
        ========= ========================== ======= ======= ======================================== ==============================
        short_uid date/time                  exit    scan_id command                                  file_name
        ========= ========================== ======= ======= ======================================== ==============================
        efab384   2020-02-06 11:21:36.129510 success 5081    lambda_test(detector_name=lambdadet, ... C042_Latex_Lq0_001
        394a20a   2020-02-06 10:32:07.525558 success 5072    lambda_test(detector_name=lambdadet, ... B041_Aerogel_Translate_Lq0_001
        aeea69b   2020-02-06 10:31:27.522871 success 5071    lambda_test(detector_name=lambdadet, ... B040_Aerogel_Translate_Lq0_001
        b39813a   2020-02-06 10:27:16.267097 success 5069    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_005
        0651cb6   2020-02-06 10:27:02.070575 success 5068    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_004
        63897f8   2020-02-06 10:26:47.770677 success 5067    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_003
        188d31a   2020-02-06 10:26:33.230039 success 5066    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_002
        9907451   2020-02-06 10:26:19.048433 success 5065    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_001
        ========= ========================== ======= ======= ======================================== ==============================

        Out[100]: <pyRestTable.rest_table.Table at 0x7f004e4d4898>

    (new in apstools release 1.1.10)
    """
    warnings.warn(
        "DEPRECATED: listruns_v1_4() will be removed"
        " in a future release.  Instead, use newer ``listruns()``.",
        DeprecationWarning,
    )
    db = getDatabase(db=db, catalog_name=catalog_name)
    keys = keys or []
    num_runs_requested = min(abs(num), len(db))
    since = since or "1995-01-01"
    until = until or "2100-12-31"

    if show_command:
        labels = "scan_id  command".split() + keys
    else:
        labels = "scan_id  plan_name".split() + keys

    # fmt: off
    cat = db.search(
        databroker.queries.TimeRange(since=since, until=until)
    ).search(db_search_terms)
    # fmt: on

    sortKey = "time"

    def sorter(uid):
        return cat[uid].metadata["start"][sortKey]

    table = pyRestTable.Table()
    table.labels = "short_uid   date/time  exit".split() + labels
    for uid in sorted(cat, key=sorter, reverse=True):
        if len(table.rows) == num_runs_requested:
            break
        run = cat[uid]
        start = run.metadata["start"]
        stop = run.metadata["stop"]
        reported_exit_status = "unknown"
        if stop is not None:
            reported_exit_status = stop.get("exit_status", "")

        if exit_status is not None and reported_exit_status != exit_status:
            continue

        row = [
            start["uid"][:7],
            datetime.datetime.fromtimestamp(start["time"]),
            reported_exit_status,
        ]

        for k in labels:
            if k == "command":
                command = _rebuild_scan_command(start)
                # fmt: off
                command = command[command.find(" "):].strip()
                # fmt: on
                maxlen = 40
                if len(command) > maxlen:
                    suffix = " ..."
                    command = command[: maxlen - len(suffix)] + suffix
                row.append(command)
            else:
                row.append(start.get(k, ""))
        table.addRow(row)

    if printing:
        if db.name is not None:
            print(f"catalog name: {db.name}")
        print(table)
    return table


def print_RE_md(dictionary=None, fmt="simple", printing=True):
    """
    custom print the RunEngine metadata in a table

    PARAMETERS

    dictionary
        *dict* :
        Python dictionary

    EXAMPLE::

        In [4]: print_RE_md()
        RunEngine metadata dictionary:
        ======================== ===================================
        key                      value
        ======================== ===================================
        EPICS_CA_MAX_ARRAY_BYTES 1280000
        EPICS_HOST_ARCH          linux-x86_64
        beamline_id              APS USAXS 9-ID-C
        login_id                 usaxs:usaxscontrol.xray.aps.anl.gov
        pid                      67933
        proposal_id              testing Bluesky installation
        scan_id                  0
        versions                 ======== =====
                                 key      value
                                 ======== =====
                                 apstools 1.1.3
                                 bluesky  1.5.2
                                 epics    3.3.1
                                 ophyd    1.3.3
                                 ======== =====
        ======================== ===================================

    """
    # override noting that fmt="markdown" will not display correctly
    fmt = "simple"

    dictionary = dictionary or ipython_shell_namespace()["RE"].md
    md = dict(dictionary)  # copy of input for editing
    v = dictionary_table(md["versions"])  # sub-table
    md["versions"] = v.reST(fmt=fmt).rstrip()
    table = dictionary_table(md)
    if printing:
        print("RunEngine metadata dictionary:")
        print(table.reST(fmt=fmt))
    return table


def pairwise(iterable):
    """
    break a list (or other iterable) into pairs

    ::

        s -> (s0, s1), (s2, s3), (s4, s5), ...

        In [71]: for item in pairwise("a b c d e fg".split()):
            ...:     print(item)
            ...:
        ('a', 'b')
        ('c', 'd')
        ('e', 'fg')

    """
    a = iter(iterable)
    return zip(a, a)


def replay(headers, callback=None, sort=True):
    """
    replay the document stream from one (or more) scans (headers)

    PARAMETERS

    headers
        *scan* or *[scan]* :
        Scan(s) to be replayed through callback.
        A *scan* is an instance of a Bluesky ``databroker.Header``.
        see: https://nsls-ii.github.io/databroker/api.html?highlight=header#header-api

    callback
        *scan* or *[scan]* :
        The Bluesky callback to handle the stream of documents from a
        scan. If ``None``, then use the `bec` (BestEffortCallback) from
        the IPython shell.
        (default:``None``)

    sort
        *bool* :
        Sort the headers chronologically if True.
        (default:``True``)

    (new in apstools release 1.1.11)
    """
    # fmt: off
    callback = callback or ipython_shell_namespace().get(
        "bec",  # get from IPython shell
        BestEffortCallback(),  # make one, if we must
    )
    # fmt: on
    _headers = headers  # do not mutate the input arg
    if isinstance(_headers, databroker.Header):
        _headers = [_headers]

    def increasing_time_sorter(run):
        return run.start["time"]

    def decreasing_time_sorter(run):
        """Default for databroker v0 results."""
        return -run.start["time"]

    # fmt: off
    sorter = {
        True: increasing_time_sorter,
        False: decreasing_time_sorter,
    }[sort]
    # fmt: on

    for h in sorted(_headers, key=sorter):
        if not isinstance(h, databroker.Header):
            # fmt: off
            raise TypeError(
                f"Must be a databroker Header: received: {type(h)}: |{h}|"
            )
            # fmt: on
        cmd = _rebuild_scan_command(h.start)
        logger.debug("%s", cmd)

        # at last, this is where the real action happens
        for k, doc in h.documents():  # get the stream
            callback(k, doc)  # play it through the callback


def rss_mem():
    """return memory used by this process"""
    return psutil.Process(os.getpid()).memory_info()


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread

    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...

       #...
       progress_reporting()   # runs in separate thread
       #...

    """

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def safe_ophyd_name(text):
    r"""
    make text safe to be used as an ophyd object name

    Given some input text string, return a clean version.
    Remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.

    The "sanitized" name fits this regular expression::

        [A-Za-z_][\w_]*

    Also can be used for safe HDF5 and NeXus names.
    """
    replacement = "_"
    noncompliance = r"[^\w_]"

    # replace ALL non-compliances with '_'
    safer = replacement.join(re.split(noncompliance, text))

    # can't start with a digit
    if safer[0].isdigit():
        safer = replacement + safer
    return safer


def listobjects(show_pv=True, printing=True, verbose=False, symbols=None):
    """
    show all the ophyd Signal and Device objects defined as globals

    PARAMETERS

    show_pv
        *bool* :
        If True, also show relevant EPICS PV, if available.
        (default: True)
    printing
        *bool* :
        If True, print table to stdout.
        (default: True)
    verbose
        *bool* :
        If True, also show ``str(obj``.
        (default: False)
    symbols
        *dict* :
        If None, use global symbol table.
        If not None, use provided dictionary.
        (default: ``globals()``)

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
    table = pyRestTable.Table()
    table.labels = ["name", "ophyd structure"]
    if show_pv:
        table.addLabel("EPICS PV")
    if verbose:
        table.addLabel("object representation")
    table.addLabel("label(s)")
    if symbols is None:
        # the default choice
        g = ipython_shell_namespace()
        if len(g) == 0:
            # ultimate fallback
            g = globals()
    else:
        g = symbols
    for k, v in sorted(g.items()):
        if isinstance(v, (ophyd.Signal, ophyd.Device)):
            row = [k, v.__class__.__name__]
            if show_pv:
                if hasattr(v, "pvname"):
                    row.append(v.pvname)
                elif hasattr(v, "prefix"):
                    row.append(v.prefix)
                else:
                    row.append("")
            if verbose:
                row.append(str(v))
            row.append(" ".join(v._ophyd_labels_))
            table.addRow(row)
    if printing:
        print(table)
    return table


def split_quoted_line(line):
    """
    splits a line into words some of which might be quoted

    TESTS::

        FlyScan 0   0   0   blank
        FlyScan 5   2   0   "empty container"
        FlyScan 5   12   0   "even longer name"
        SAXS 0 0 0 blank
        SAXS 0 0 0 "blank"

    RESULTS::

        ['FlyScan', '0', '0', '0', 'blank']
        ['FlyScan', '5', '2', '0', 'empty container']
        ['FlyScan', '5', '12', '0', 'even longer name']
        ['SAXS', '0', '0', '0', 'blank']
        ['SAXS', '0', '0', '0', 'blank']

    """
    parts = []

    # look for open and close quoted parts and combine them
    quoted = False
    multi = None
    for p in line.split():
        if not quoted and p.startswith('"'):  # begin quoted text
            quoted = True
            multi = ""

        if quoted:
            if len(multi) > 0:
                multi += " "
            multi += p
            if p.endswith('"'):  # end quoted text
                quoted = False

        if not quoted:
            if multi is not None:
                parts.append(multi[1:-1])  # remove enclosing quotes
                multi = None
            else:
                parts.append(p)

    return parts


def summarize_runs(since=None, db=None):
    """
    Report bluesky run metrics from the databroker.

    * How many different plans?
    * How many runs?
    * How many times each run was used?
    * How frequently?  (TODO:)

    PARAMETERS

    since
        *str* :
        Report all runs since this ISO8601 date & time
        (default: ``1995``)
    db
        *object* :
        Instance of ``databroker.Broker()``
        (default: ``db`` from the IPython shell)
    """
    db = db or ipython_shell_namespace()["db"]
    # no APS X-ray experiment data before 1995!
    since = since or "1995"
    cat = db.v2.search(databroker.queries.TimeRange(since=since))
    plans = defaultdict(list)
    t0 = time.time()
    for n, uid in enumerate(cat):
        t1 = time.time()
        # next step is very slow (0.01 - 0.5 seconds each!)
        run = cat[uid]
        t2 = time.time()
        plan_name = run.metadata["start"].get("plan_name", "unknown")
        # fmt:off
        dt = datetime.datetime.fromtimestamp(
            run.metadata["start"]["time"]
        ).isoformat()
        # fmt:on
        scan_id = run.metadata["start"].get("scan_id", "unknown")
        # fmt: off
        plans[plan_name].append(
            dict(
                plan_name=plan_name,
                dt=dt,
                time_start=dt,
                uid=uid,
                scan_id=scan_id,
            )
        )
        # fmt: on
        logger.debug(
            "%s %s dt1=%4.01fus dt2=%5.01fms %s",
            scan_id,
            dt,
            (t1 - t0) * 1e6,
            (t2 - t1) * 1e3,
            plan_name,
        )
        t0 = time.time()

    def sorter(plan_name):
        return len(plans[plan_name])

    table = pyRestTable.Table()
    table.labels = "plan quantity".split()
    for k in sorted(plans.keys(), key=sorter, reverse=True):
        table.addRow((k, sorter(k)))
    table.addRow(("TOTAL", n + 1))
    print(table)


def text_encode(source):
    """Encode ``source`` using the default codepoint."""
    return source.encode(errors="ignore")


def to_unicode_or_bust(obj, encoding="utf-8"):
    """from: http://farmdev.com/talks/unicode/  ."""
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


def trim_string_for_EPICS(msg):
    """String must not exceed EPICS PV length."""
    if len(msg) > MAX_EPICS_STRINGOUT_LENGTH:
        msg = msg[: MAX_EPICS_STRINGOUT_LENGTH - 1]
    return msg


def unix(command, raises=True):
    """
    Run a UNIX command, returns (stdout, stderr).

    PARAMETERS

    command
        *str* :
        UNIX command to be executed
    raises
        *bool* :
        If ``True``, will raise exceptions as needed,
        default: ``True``
    """
    if sys.platform not in ("linux", "linux2"):
        emsg = f"Cannot call unix() when OS={sys.platform}"
        raise RuntimeError(emsg)

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()

    if len(stderr) > 0:
        emsg = f"unix({command}) returned error:\n{stderr}"
        logger.error(emsg)
        if raises:
            raise RuntimeError(emsg)

    return stdout, stderr


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
        times_up = time.time() + min(0, timeout)
        poll_interval = min(0.01, poll_interval)
        waiting = True
        while waiting and time.time() < times_up:
            time.sleep(poll_interval)
            waiting = False in [o.connected for o in obj_dict.values()]
        if waiting:
            n = OrderedDict()
            for k, v in obj_dict.items():
                if v.connected:
                    n[k] = v
                else:
                    print(f"Could not connect {v.pvname}")
            if len(n) == 0:
                raise RuntimeError("Could not connect any PVs in the list")
            obj_dict = n

    return obj_dict


class EmailNotifications(object):
    """
    send email notifications when requested

    .. index:: apstools Utility; EmailNotifications

    use default OS mail utility (so no credentials needed)

    EXAMPLE

    Send email(s) when `feedback_limits_approached`
    (a hypothetical boolean) is `True`::

        # setup
        from apstools.utils import EmailNotifications

        SENDER_EMAIL = "instrument_user@email.host.tld"

        email_notices = EmailNotifications(SENDER_EMAIL)
        email_notices.add_addresses(
            # This list receives email when send() is called.
            "joe.user@goodmail.com",
            "instrument_team@email.host.tld",
            # others?
        )

        # ... later

        if feedback_limits_approached:
            # send emails to list
            subject = "Feedback problem"
            message = "Feedback is very close to its limits."
            email_notices.send(subject, message)
    """

    def __init__(self, sender=None):
        self.addresses = []
        self.notify_on_feedback = True
        self.sender = sender or "nobody@localhost"
        self.smtp_host = "localhost"

    def add_addresses(self, *args):
        for address in args:
            self.addresses.append(address)

    @run_in_thread
    def send(self, subject, message):
        """send ``message`` to all addresses"""
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ",".join(self.addresses)
        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(self.sender, self.addresses, msg.as_string())
        s.quit()


class ExcelDatabaseFileBase(object):
    """
    base class: read-only support for Excel files, treat them like databases

    .. index:: apstools Utility; ExcelDatabaseFileBase

    Use this class when creating new, specific spreadsheet support.

    EXAMPLE

    Show how to read an Excel file where one of the columns
    contains a unique key.  This allows for random access to
    each row of data by use of the *key*.

    ::

        class ExhibitorsDB(ExcelDatabaseFileBase):
            '''
            content for exhibitors from the Excel file
            '''
            EXCEL_FILE = os.path.join("resources", "exhibitors.xlsx")
            LABELS_ROW = 2

            def handle_single_entry(self, entry):
                '''any special handling for a row from the Excel file'''
                pass

            def handleExcelRowEntry(self, entry):
                '''identify unique key (row of the Excel file)'''
                key = entry["Name"]
                self.db[key] = entry

    """

    EXCEL_FILE = None  # subclass MUST define
    # EXCEL_FILE = os.path.join("abstracts", "index of abstracts.xlsx")
    LABELS_ROW = 3  # labels are on line LABELS_ROW+1 in the Excel file

    def __init__(self, ignore_extra=True):
        self.db = OrderedDict()
        self.data_labels = None
        if self.EXCEL_FILE is None:
            raise ValueError("subclass must define EXCEL_FILE")
        self.fname = os.path.join(os.getcwd(), self.EXCEL_FILE)

        self.sheet_name = 0

        self.parse(ignore_extra=ignore_extra)

    def handle_single_entry(self, entry):  # subclass MUST override
        # fmt: off
        raise NotImplementedError(
            "subclass must override handle_single_entry() method"
        )
        # fmt: on

    def handleExcelRowEntry(self, entry):  # subclass MUST override
        # fmt: off
        raise NotImplementedError(
            "subclass must override handleExcelRowEntry() method"
        )
        # fmt: on

    def parse(
        self, labels_row_num=None, data_start_row_num=None, ignore_extra=True,
    ):
        labels_row_num = labels_row_num or self.LABELS_ROW
        try:
            wb = openpyxl.load_workbook(self.fname)
            ws = wb.worksheets[self.sheet_name]
            if ignore_extra:
                # ignore data outside of table in spreadsheet file
                data = list(ws.rows)[labels_row_num:]
                self.data_labels = []
                for c in data[0]:
                    if c.value is None:
                        break
                    self.data_labels.append(c.value)
                rows = []
                for r in data[1:]:
                    if r[0].value is None:
                        break
                    rows.append(r[: len(self.data_labels)])
            else:
                # use the whole sheet
                rows = list(ws.rows)
                # create the column titles
                # fmt: off
                self.data_labels = [
                    f"Column_{i+1}" for i in range(len(rows[0]))
                ]
                # fmt: on
        except openpyxl.utils.exceptions.InvalidFileException as exc:
            raise ExcelReadError(exc)
        for row in rows:
            entry = OrderedDict()
            for _col, label in enumerate(self.data_labels):
                entry[label] = row[_col].value
                self.handle_single_entry(entry)
            self.handleExcelRowEntry(entry)

    def _getExcelColumnValue(self, row_data, col):
        v = row_data[col]
        if self._isExcel_nan(v):
            v = None
        else:
            v = to_unicode_or_bust(v)
            if isinstance(v, str):
                v = v.strip()
        return v

    def _isExcel_nan(self, value):
        if not isinstance(value, float):
            return False
        return math.isnan(value)


class ExcelDatabaseFileGeneric(ExcelDatabaseFileBase):
    """
    Generic (read-only) handling of Excel spreadsheet-as-database

    .. index:: apstools Utility; ExcelDatabaseFileGeneric
    .. index:: Excel scan, scan; Excel

    .. note:: This is the class to use when reading Excel spreadsheets.

    In the spreadsheet, the first sheet should contain the table to be
    used. By default (see keyword parameter ``labels_row``), the table
    should start in cell A4.  The column labels are given in row 4.  A
    blank column should appear to the right of the table (see keyword
    parameter ``ignore_extra``). The column labels will describe the
    action and its parameters.  Additional columns may be added for
    metadata or other purposes.

    The rows below the column labels should contain actions and
    parameters for those actions, one action per row.

    To make a comment, place a ``#`` in the action column.  A comment
    should be ignored by the bluesky plan that reads this table. The
    table will end with a row of empty cells.

    While it's a good idea to put the ``action`` column first, that is
    not necessary. It is not even necessary to name the column
    ``action``. You can re-arrange the order of the columns and change
    their names **as long as** the column names match what text strings
    your Python code expects to find.

    A future upgrade [#]_ will allow the table boundaries to be named by
    Excel when using Excel's ``Format as Table`` [#]_ feature. For now,
    leave a blank row and column at the bottom and right edges of the
    table.

    .. [#] https://github.com/BCDA-APS/apstools/issues/122
    .. [#] Excel's ``Format as Table``:
        https://support.office.com/en-us/article/Format-an-Excel-table-6789619F-C889-495C-99C2-2F971C0E2370

    PARAMETERS

    filename
        *str* :
        name (absolute or relative) of Excel spreadsheet file
    labels_row
        *int* :
        Row (zero-based numbering) of Excel file with column labels,
        default: ``3`` (Excel row 4)
    ignore_extra
        *bool* :
        When ``True``, ignore any cells outside of the table, default:
        ``True``.

        Note that when ``True``, a row of cells *within* the table will
        be recognized as the end of the table, even if there are
        actions in following rows.  To force an empty row, use
        a comment symbol ``#`` (actually, any non-empty content will work).

        When ``False``, cells with other information (in Sheet 1) will
        be made available, sometimes with unpredictable results.

    EXAMPLE

    See section :ref:`example_run_command_file` for more examples.

    (See also :ref:`example screen shot
    <excel_plan_spreadsheet_screen>`.) Table (on Sheet 1) begins on row
    4 in first column::

        1  |  some text here, maybe a title
        2  |  (could have content here)
        3  |  (or even more content here)
        4  |  action  | sx   | sy   | sample     | comments          |  | <-- leave empty column
        5  |  close   |      |                   | close the shutter |  |
        6  |  image   | 0    | 0    | dark       | dark image        |  |
        7  |  open    |      |      |            | open the shutter  |  |
        8  |  image   | 0    | 0    | flat       | flat field image  |  |
        9  |  image   | 5.1  | -3.2 | 4140 steel | heat 9172634      |  |
        10 |  scan    | 5.1  | -3.2 | 4140 steel | heat 9172634      |  |
        11 |  scan    | 0    | 0    | blank      |                   |  |
        12 |
        13 |  ^^^ leave empty row ^^^
        14 | (could have content here)



    Example python code to read this spreadsheet::

        from apstools.utils import ExcelDatabaseFileGeneric, cleanupText

        def myExcelPlan(xl_file, md={}):
            excel_file = os.path.abspath(xl_file)
            xl = ExcelDatabaseFileGeneric(excel_file)
            for i, row in xl.db.values():
                # prepare the metadata
                _md = {cleanupText(k): v for k, v in row.items()}
                _md["xl_file"] = xl_file
                _md["excel_row_number"] = i+1
                _md.update(md) # overlay with user-supplied metadata

                # determine what action to take
                action = row["action"].lower()
                if action == "open":
                    yield from bps.mv(shutter, "open")
                elif action == "close":
                    yield from bps.mv(shutter, "close")
                elif action == "image":
                    # your code to take an image, given **row as parameters
                    yield from my_image(**row, md=_md)
                elif action == "scan":
                    # your code to make a scan, given **row as parameters
                    yield from my_scan(**row, md=_md)
                else:
                    print(f"no handling for row {i+1}: action={action}")

        # execute this plan through the RunEngine
        RE(myExcelPlan("spreadsheet.xlsx", md=dict(purpose="apstools demo"))

    """

    def __init__(self, filename, labels_row=3, ignore_extra=True):
        self._index_ = 0
        self.EXCEL_FILE = self.EXCEL_FILE or filename
        self.LABELS_ROW = labels_row
        ExcelDatabaseFileBase.__init__(self, ignore_extra=ignore_extra)

    def handle_single_entry(self, entry):
        pass

    def handleExcelRowEntry(self, entry):
        """use row number as the unique key"""
        key = str(self._index_)
        self.db[key] = entry
        self._index_ += 1


def ipython_profile_name():
    """
    return the name of the current ipython profile or ``None``

    Example (add to default RunEngine metadata)::

        RE.md['ipython_profile'] = str(ipython_profile_name())
        print("using profile: " + RE.md['ipython_profile'])

    """
    from IPython import get_ipython

    return get_ipython().profile


def ipython_shell_namespace():
    """
    get the IPython shell's namespace dictionary (or empty if not found)
    """
    try:
        from IPython import get_ipython

        ns = get_ipython().user_ns
    except AttributeError:
        ns = {}
    return ns


def select_mpl_figure(x, y):
    """
    get the MatPlotLib Figure window for y vs x

    PARAMETERS

    x
        *object*:
        X axis object (an ``ophyd.Signal``)
    y
        ophyd object:
        X axis object (an ``ophyd.Signal``)

    RETURNS

    object or ``None``:
        Instance of ``matplotlib.pyplot.Figure()``
    """
    import matplotlib.pyplot as plt

    figure_name = f"{y.name} vs {x.name}"
    if figure_name in plt.get_figlabels():
        return plt.figure(figure_name)


def select_live_plot(bec, signal):
    """
    get the *first* live plot that matches ``signal``

    PARAMETERS

    bec
        *object*:
        instance of ``bluesky.callbacks.best_effort.BestEffortCallback``
    signal
        *object*:
        The Y axis object (an ``ophyd.Signal``)

    RETURNS

    *object*:
        Instance of ``bluesky.callbacks.best_effort.LivePlotPlusPeaks()``
        or ``None``
    """
    for live_plot_dict in bec._live_plots.values():
        live_plot = live_plot_dict.get(signal.name)
        if live_plot is not None:
            return live_plot


def trim_plot_lines(bec, n, x, y):
    """
    find the plot with axes x and y and replot with at most the last *n* lines

    Note: :func:`trim_plot_lines` is not a bluesky plan.  Call it as
    normal Python function.

    EXAMPLE::

        trim_plot_lines(bec, 1, m1, noisy)

    PARAMETERS

    bec
        *object* :
        instance of BestEffortCallback

    n
        *int* :
        number of plots to keep

    x
        *object* :
        instance of ophyd.Signal (or subclass),
        independent (x) axis

    y
        *object* :
        instance of ophyd.Signal (or subclass),
        dependent (y) axis

    (new in release 1.3.5)
    """
    liveplot = select_live_plot(bec, y)
    if liveplot is None:
        logger.debug("no live plot found with signal '%s'", y.name)
        return

    fig = select_mpl_figure(x, y)
    if fig is None:
        logger.debug("no figure found with '%s vs %s'", y.name, x.name)
        return
    if len(fig.axes) == 0:
        logger.debug("no plots on figure: '%s vs %s'", y.name, x.name)
        return

    ax = fig.axes[0]
    while len(ax.lines) > n:
        try:
            ax.lines[0].remove()
        except ValueError as exc:
            if not str(exc).endswith("x not in list"):
                # fmt: off
                logger.warning(
                    "%s vs %s: mpl remove() error: %s",
                    y.name, x.name, str(exc),
                )
                # fmt: on
    ax.legend()
    liveplot.update_plot()
    logger.debug("trim complete")


def trim_plot_by_name(n=3, plots=None):
    """
    Find the plot(s) by name and replot with at most the last *n* lines.

    Note: this is not a bluesky plan.  Call it as normal Python function.

    It is recommended to call :func:`~trim_plot_by_name()` *before* the
    scan(s) that generate plots.  Plots are generated from a RunEngine
    callback, executed *after* the scan completes.

    PARAMETERS

    n
        *int* :
        number of plots to keep

    plots
        *str*, [*str*], or *None* :
        name(s) of plot windows to trim
        (default: all plot windows)

    EXAMPLES::

        trim_plot_by_name()   # default of n=3, apply to all plots
        trim_plot_by_name(5)  # change from default of n=3
        trim_plot_by_name(5, "noisy_det vs motor")  # just this plot
        trim_plot_by_name(
            5,
            ["noisy_det vs motor", "det noisy_det vs motor"]]
        )

    EXAMPLE::

        # use simulators from ophyd
        from bluesky import plans as bp
        from bluesky import plan_stubs as bps
        from ophyd.sim import *

        snooze = 0.25

        def scan_set():
            trim_plot_by_name()
            yield from bp.scan([noisy_det], motor, -1, 1, 5)
            yield from bp.scan([noisy_det, det], motor, -2, 1, motor2, 3, 1, 6)
            yield from bps.sleep(snooze)

        # repeat the_scans 15 times
        uids = RE(bps.repeat(scan_set, 15))

    (new in release 1.3.5)
    """
    import matplotlib.pyplot as plt

    if isinstance(plots, str):
        plots = [plots]

    for fig_name in plt.get_figlabels():
        if plots is None or fig_name in plots:
            fig = plt.figure(fig_name)
            for ax in fig.axes:
                while len(ax.lines) > n:
                    ax.lines[0].remove()
                # update the plot legend
                ax.legend()


def print_snapshot_list(db, printing=True, **search_criteria):
    """
    print (stdout) a list of all snapshots in the databroker

    USAGE::

        print_snapshot_list(db, )
        print_snapshot_list(db, purpose="this is an example")
        print_snapshot_list(db, since="2018-12-21", until="2019")

    EXAMPLE::

        In [16]: from apstools.utils import print_snapshot_list
            ...: from apstools.callbacks import SnapshotReport
            ...: print_snapshot_list(db, since="2018-12-21", until="2019")
            ...:
        = ======== ========================== ==================
        # uid      date/time                  purpose
        = ======== ========================== ==================
        0 d7831dae 2018-12-21 11:39:52.956904 this is an example
        1 5049029d 2018-12-21 11:39:30.062463 this is an example
        2 588e0149 2018-12-21 11:38:43.153055 this is an example
        = ======== ========================== ==================

        In [17]: SnapshotReport().print_report(db["5049029d"])

        ========================================
        snapshot: 2018-12-21 11:39:30.062463
        ========================================

        example: example 2
        hints: {}
        iso8601: 2018-12-21 11:39:30.062463
        look: can snapshot text and arrays too
        note: no commas in metadata
        plan_description: archive snapshot of ophyd Signals (usually EPICS PVs)
        plan_name: snapshot
        plan_type: generator
        purpose: this is an example
        scan_id: 1
        software_versions: {
            'python':
                '''3.6.2 |Continuum Analytics, Inc.| (default, Jul 20 2017, 13:51:32)
                [GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]''',
            'PyEpics': '3.3.1',
            'bluesky': '1.4.1',
            'ophyd': '1.3.0',
            'databroker': '0.11.3',
            'apstools': '0.0.38'
            }
        time: 1545413970.063167
        uid: 5049029d-075c-453c-96d2-55431273852b

        ========================== ====== ================ ===================
        timestamp                  source name             value
        ========================== ====== ================ ===================
        2018-12-20 18:24:34.220028 PV     compress         [0.1, 0.2, 0.3]
        2018-12-13 14:49:53.121188 PV     gov:HOSTNAME     otz.aps.anl.gov
        2018-12-21 11:39:24.268148 PV     gov:IOC_CPU_LOAD 0.22522317161410768
        2018-12-21 11:39:24.268151 PV     gov:SYS_CPU_LOAD 9.109026666525944
        2018-12-21 11:39:30.017643 PV     gov:iso8601      2018-12-21T11:39:30
        2018-12-13 14:49:53.135016 PV     otz:HOSTNAME     otz.aps.anl.gov
        2018-12-21 11:39:27.705304 PV     otz:IOC_CPU_LOAD 0.1251210270549924
        2018-12-21 11:39:27.705301 PV     otz:SYS_CPU_LOAD 11.611234438304471
        2018-12-21 11:39:30.030321 PV     otz:iso8601      2018-12-21T11:39:30
        ========================== ====== ================ ===================

        exit_status: success
        num_events: {'primary': 1}
        run_start: 5049029d-075c-453c-96d2-55431273852b
        time: 1545413970.102147
        uid: 6c1b2100-1ef6-404d-943e-405da9ada882

    """
    t = pyRestTable.Table()
    t.addLabel("#")
    t.addLabel("uid")
    t.addLabel("date/time")
    t.addLabel("#items")
    t.addLabel("purpose")
    search_criteria["plan_name"] = "snapshot"
    for i, h in enumerate(db(**search_criteria)):
        uid = h.start["uid"].split("-")[0]
        n = len(list(h.start.keys()))
        t.addRow((i, uid, h.start["iso8601"], n, h.start["purpose"]))
    if printing:
        print(t)
    return t


def json_export(headers, filename, zipfilename=None):
    """
    DEPRECATED: Use *databroker-pack* package instead.

    write a list of headers (from databroker) to a file

    PARAMETERS

    headers
        *[headers]* or ``databroker._core.Results`` object :
        list of databroker headers as returned from
        ``db(...search criteria...)``
    filename
        *str* :
        name of file into which to write JSON
    zipfilename
        *str* or ``None`` :
        name of ZIP file container of ``filename``
        (if ``None``, do not ZIP ``filename``)

        .. note::  If writing to a ZIP file, the data file is
           *only* written into the ZIP file.

    EXAMPLE::

        from databroker import Broker
        db = Broker.named("mongodb_config")
        headers = db(plan_name="count", since="2019-04-01")

        json_export(
            headers,
            "data.json",
            zipfilename="bluesky_data.zip")

    EXAMPLE: READ THE ZIP FILE:

     using :func:`~json_import`::

        datasets = json_import("data.json", zipfilename="bluesky_data.zip")

    EXAMPLE: READ THE JSON TEXT FILE

    using :func:`~json_import`::

        datasets = json_import("data.json)

    """
    warnings.warn(
        "DEPRECATED: json_import() will be removed"
        " in a future release.  Instead, use *databroker-pack* package.",
        DeprecationWarning,
    )
    datasets = [list(h.documents()) for h in headers]
    buf = json.dumps(datasets, cls=NumpyEncoder, indent=2)

    if zipfilename is None:
        with open(filename, "w") as fp:
            fp.write(buf)
    else:
        with zipfile.ZipFile(zipfilename, "w", allowZip64=True) as fp:
            fp.writestr(filename, buf, compress_type=zipfile.ZIP_LZMA)


def json_import(filename, zipfilename=None):
    """
    DEPRECATED: Use *databroker-pack* package instead.

    read the file exported by :func:`~json_export()`

    RETURNS

    datasets :
        *list of documents* :
        list of
        `documents <https://blueskyproject.io/bluesky/documents.html/>`_,
        such as returned by
        ``[list(h.documents()) for h in db]``

        See:
        https://blueskyproject.io/databroker/generated/databroker.Header.documents.html

    EXAMPLE

    Insert the datasets into the databroker ``db``::

        def insert_docs(db, datasets):
            for i, h in enumerate(datasets):
                print(f"{i+1}/{len(datasets)} : {len(h)} documents")
                for k, doc in h:
                    db.insert(k, doc)

    """
    warnings.warn(
        "DEPRECATED: json_import() will be removed"
        " in a future release.  Instead, use *databroker-pack* package.",
        DeprecationWarning,
    )
    if zipfilename is None:
        with open(filename, "r") as fp:
            buf = fp.read()
            datasets = json.loads(buf)
    else:
        with zipfile.ZipFile(zipfilename, "r") as fp:
            buf = fp.read(filename).decode("utf-8")
            datasets = json.loads(buf)

    return datasets


def redefine_motor_position(motor, new_position):
    """set EPICS motor record's user coordinate to ``new_position``"""
    yield from bps.mv(motor.set_use_switch, 1)
    yield from bps.mv(motor.user_setpoint, new_position)
    yield from bps.mv(motor.set_use_switch, 0)


def quantify_md_key_use(
    key=None, db=None, catalog_name=None, since=None, until=None, query=None,
):
    """
    print table of different ``key`` values and how many times each appears

    PARAMETERS

    key
        *str* :
        one of the metadata keys in a run's start document
        (default: ``plan_name``)
    db
        *object* :
        Instance of databroker v1 ``Broker`` or v2 ``catalog``
        (default: see ``catalog_name`` keyword argument)
    catalog_name
        *str* :
        Name of databroker v2 catalog, used when supplied ``db`` is ``None``.
        (default: ``mongodb_config``)
    since
        *str* :
        include runs that started on or after this ISO8601 time
        (default: ``1995-01-01``)
    until
        *str* :
        include runs that started before this ISO8601 time
        (default: ``2100-12-31``)
    query
        *dict* :
        mongo query dictionary, used to filter the results
        (default: ``{}``)

        see: https://docs.mongodb.com/manual/reference/operator/query/

    EXAMPLES::

        quantify_md_key_use(key="proposal_id")
        quantify_md_key_use(key="plan_name", catalog_name="9idc", since="2020-07")
        quantify_md_key_use(key="beamline_id", catalog_name="9idc")
        quantify_md_key_use(key="beamline_id",
                            catalog_name="9idc",
                            query={'plan_name': 'Flyscan'},
                            since="2020",
                            until="2020-06-21 21:51")
        quantify_md_key_use(catalog_name="8id", since="2020-01", until="2020-03")

    """
    key = key or "plan_name"
    catalog_name = catalog_name or "mongodb_config"
    query = query or {}
    since = since or "1995-01-01"
    until = until or "2100-12-31"

    cat = (
        (db or databroker.catalog[catalog_name])
        .v2.search(databroker.queries.TimeRange(since=since, until=until))
        .search(query)
    )

    items = []
    while True:
        runs = cat.search({key: {"$exists": True, "$nin": items}})
        if len(runs) == 0:
            break
        else:
            items.append(runs.v1[-1].start.get(key))

    def sorter(key):
        if key is None:
            key = " None"
        return str(key)

    table = pyRestTable.Table()
    table.labels = f"{key} #runs".split()
    for item in sorted(items, key=sorter):
        table.addRow((item, len(cat.search({key: item}))))
    print(table)


def copy_filtered_catalog(source_cat, target_cat, query=None):
    """
    copy filtered runs from source_cat to target_cat

    PARAMETERS

    source_cat
        *obj* :
        instance of `databroker.Broker` or `databroker.catalog[name]`
    target_cat
        *obj* :
        instance of `databroker.Broker` or `databroker.catalog[name]`
    query
        *dict* :
        mongo query dictionary, used to filter the results
        (default: ``{}``)

        see: https://docs.mongodb.com/manual/reference/operator/query/

    example::

        copy_filtered_catalog(
            databroker.Broker.named("mongodb_config"),
            databroker.catalog["test1"],
            {'plan_name': 'snapshot'})
    """
    query = query or {}
    for i, uid in enumerate(source_cat.v2.search(query)):
        run = source_cat.v1[uid]
        # fmt: off
        logger.debug(
            "%d  %s  #docs=%d", i + 1, uid, len(list(run.documents()))
        )
        # fmt: on
        for key, doc in run.documents():
            target_cat.v1.insert(key, doc)


_findpv_registry = None


class PVRegistry:
    """
    Cross-reference EPICS PVs with ophyd EpicsSignalBase objects.
    """

    def __init__(self, ns=None):
        """
        Search ophyd objects for PV or ophyd names.

        The rebuild starts with the IPython console namespace
        (and defaults to the global namespace if the former
        cannot be obtained).

        PARAMETERS

        ns *dict* or `None`: namespace dictionary
        """
        self._pvdb = defaultdict(lambda: defaultdict(list))
        self._odb = {}
        self._device_name = None
        self._known_device_names = []
        g = ns or ipython_shell_namespace() or globals()

        # kickoff the registration process
        # fmt: off
        logger.debug(
            "Cross-referencing EPICS PVs with Python objects & ophyd symbols"
        )
        # fmt: on
        self._ophyd_epicsobject_walker(g)

    def _ophyd_epicsobject_walker(self, parent):
        """
        Walk through the parent object for ophyd Devices & EpicsSignals.

        This function is used to rebuild the ``self._pvdb`` object.
        """
        if isinstance(parent, dict):
            keys = parent.keys()
        else:
            keys = parent.component_names
            _nm_base = self._device_name
        for k in keys:
            if isinstance(parent, dict):
                _nm_base = []
                v = self._ref_dict(parent, k)
            else:
                v = self._ref_object_attribute(parent, k)
            if v is None:
                continue
            # print(k, type(v))
            if isinstance(v, ophyd.signal.EpicsSignalBase):
                try:
                    self._signal_processor(v)
                    self._odb[v.name] = ".".join(self._device_name + [k])
                except (KeyError, RuntimeError) as exc:
                    # fmt: off
                    logger.error(
                        "Exception while examining key '%s': (%s)", k, exc
                    )
                    # fmt: on
            elif isinstance(v, ophyd.Device):
                # print("Device", v.name)
                self._device_name = _nm_base + [k]
                if v.name not in self._known_device_names:
                    self._odb[v.name] = ".".join(self._device_name)
                    self._known_device_names.append(v.name)
                    self._ophyd_epicsobject_walker(v)

    def _ref_dict(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        return parent[key]

    def _ref_object_attribute(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        try:
            obj = getattr(parent, key, None)
            return obj
        except (KeyError, RuntimeError, TimeoutError) as exc:
            # fmt: off
            logger.error(
                "Exception while getting object '%s.%s': (%s)",
                ".".join(self._device_name), key, exc,
            )
            # fmt: on

    def _register_signal(self, signal, pv, mode):
        """Register a signal with the given mode."""
        fdn = full_dotted_name(signal)
        if fdn not in self._pvdb[pv][mode]:
            self._pvdb[pv][mode].append(fdn)

    def _signal_processor(self, signal):
        """Register a signal's read & write PVs."""
        self._register_signal(signal, signal._read_pv.pvname, "R")
        if hasattr(signal, "_write_pv"):
            self._register_signal(signal, signal._write_pv.pvname, "W")

    def search_by_mode(self, pvname, mode="R"):
        """Search for PV in specified mode."""
        if mode not in ["R", "W"]:
            raise ValueError(
                f"Incorrect mode given ({mode}." "  Must be either `R` or `W`."
            )
        return self._pvdb[pvname][mode]

    def search(self, pvname):
        """Search for PV in both read & write modes."""
        return dict(
            read=self.search_by_mode(pvname, "R"),
            write=self.search_by_mode(pvname, "W"),
        )

    def ophyd_search(self, oname):
        """Search for ophyd object by ophyd name."""
        return self._odb.get(oname)


def _get_pv_registry(force_rebuild, ns):
    """
    Check if need to build/rebuild the PV registry.

    PARAMETERS

    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        EPICS PV names to ophyd objects.
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    """
    global _findpv_registry
    if _findpv_registry is None or force_rebuild:
        _findpv_registry = PVRegistry(ns=ns)
    return _findpv_registry


def findbyname(oname, force_rebuild=False, ns=None):
    """
    Find the ophyd (dotted name) object associated with the given ophyd name.

    PARAMETERS

    oname
        *str* :
        ophyd name to search
    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        ophyd names to ophyd objects.
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    RETURNS

    str or ``None``:
        Name of the ophyd object.

    EXAMPLE::

        In [45]: findbyname("adsimdet_cam_acquire")
        Out[45]: 'adsimdet.cam.acquire'

    (new in apstools 1.5.0)
    """
    return _get_pv_registry(force_rebuild, ns).ophyd_search(oname)


def findbypv(pvname, force_rebuild=False, ns=None):
    """
    Find all ophyd objects associated with the given EPICS PV.

    PARAMETERS

    pvname
        *str* :
        EPICS PV name to search
    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        EPICS PV names to ophyd objects.
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    RETURNS

    dict or ``None``:
        Dictionary of matching ophyd objects, keyed by how the
        PV is used by the ophyd signal.  The keys are
        ``read`` and ``write``.

    EXAMPLE::

        In [45]: findbypv("ad:cam1:Acquire")
        Out[45]: {'read': [], 'write': ['adsimdet.cam.acquire']}

        In [46]: findbypv("ad:cam1:Acquire_RBV")
        Out[46]: {'read': ['adsimdet.cam.acquire'], 'write': []}

    """
    return _get_pv_registry(force_rebuild, ns).search(pvname)

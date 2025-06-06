"""
Directory of bluesky runs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~getRunData
   ~getRunDataValue
   ~listRunKeys
   ~ListRuns
   ~listruns
   ~summarize_runs
"""

import dataclasses
import datetime
import logging
import time
import typing
import warnings
from collections import defaultdict

from deprecated.sphinx import deprecated
from deprecated.sphinx import versionadded
from deprecated.sphinx import versionchanged

from ._core import FIRST_DATA
from ._core import LAST_DATA
from ._core import TableStyle
from .query import db_query

logger = logging.getLogger(__name__)


@versionadded(version="1.5.1")
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
    """
    from . import getCatalog

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


@versionadded(version="1.5.1")
def getRunDataValue(scan_id, key, db=None, stream="primary", query=None, idx=-1, use_v1=True):
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
    """
    if idx is None:
        idx = -1
    try:
        _idx = int(idx)
    except ValueError:
        _idx = str(idx).lower()

    if isinstance(_idx, str) and _idx not in "all mean".split():
        raise KeyError(f"Did not understand 'idx={idx}', use integer, 'all', or 'mean'.")

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
    raise KeyError(f"Cannot reference idx={idx} in scan {scan_id} stream'{stream}' key={key}.")


@versionadded(version="1.5.1")
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


@dataclasses.dataclass
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
    query: object = None
    keys: object = None
    missing: str = ""
    num: int = 20
    reverse: bool = True
    since: object = None
    sortby: str = "time"
    timefmt: str = "%Y-%m-%d %H:%M:%S"
    until: object = None
    ids: "typing.Any" = None
    hints_override: bool = False

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
        v = self.missing
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
        hints = md["start"].get("hints", {})
        if (v == self.missing or self.hints_override) and key in hints:
            v = hints[key]
        return v

    def _check_cat(self):
        from . import getCatalog

        if self.cat is None:
            self.cat = getCatalog()

    def _apply_search_filters(self):
        """Search for runs from the catalog."""
        from databroker.queries import TimeRange

        since = self.since or FIRST_DATA
        until = self.until or LAST_DATA
        self._check_cat()
        query = {}
        query.update(TimeRange(since=since, until=until))
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
            from databroker import Broker
            from databroker._drivers.mongo_normalized import BlueskyMongoCatalog

            MONGO_CATALOG_CLASSES = (Broker, BlueskyMongoCatalog)
            if isinstance(cat, MONGO_CATALOG_CLASSES) and self.sortby == "time":
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
        if isinstance(self.keys, str):
            self.keys = self.keys.split()

    @deprecated(version="1.6.14")
    def to_dataframe(self):
        """**Deprecated**: Output as pandas DataFrame object"""
        warnings.warn("'ListRuns.to_dataframe()' method is deprecated.")
        dd = self.parse_runs()
        return TableStyle.pandas.value(dd, columns=self.keys)

    @deprecated(version="1.6.14")
    def to_table(self, fmt=None):
        """**Deprecated**: Output as pyRestTable object."""
        warnings.warn("'ListRuns.to_table()' method is deprecated.")
        dd = self.parse_runs()
        return TableStyle.pyRestTable.value(dd=dd).reST(fmt=fmt or "simple")


@versionadded(version="1.5.0")
def listruns(
    cat=None,
    keys=None,
    missing="",
    num=20,
    printing=None,  # DEPRECATED
    reverse=True,
    since=None,
    sortby="time",
    tablefmt=None,  # DEPRECATED
    table_style=TableStyle.pyRestTable,
    timefmt="%Y-%m-%d %H:%M:%S",
    until=None,
    ids=None,
    hints_override=False,
    **query,
):
    """
    List runs from catalog.

    This function provides a thin interface to the highly-reconfigurable
    ``ListRuns()`` class in this package.

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
    hints_override *bool*:
        For a key that appears in both the metadata and the hints,
        override the metadata value if the same key is found in the hints.
        (default: ``False``)
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
    printing *bool* or *str* :
        Deprecated.
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
    tablefmt *str* :
        Deprecated.  Use ``table_style`` instead.
    table_style *object* :
        Either ``TableStyle.pyRestTable`` (default) or ``TableStyle.pandas``,
        using values from :class:`apstools.utils.TableStyle`.

        .. note:: ``pandas.DataFrame`` wll truncate long text to at most 50 characters.
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

    .. EXAMPLE

        TODO
    """

    lr = ListRuns(
        cat=cat,
        keys=keys,
        missing=missing,
        num=num,
        query=query,
        reverse=reverse,
        since=since,
        sortby=sortby,
        timefmt=timefmt,
        until=until,
        ids=ids,
        hints_override=hints_override,
    )

    table_style = table_style or TableStyle.pyRestTable
    if tablefmt is not None:
        if tablefmt == "dataframe":
            choice = "TableStyle.pandas"
            table_style = TableStyle.pandas
        else:
            choice = "TableStyle.pyRestTable"
            table_style = TableStyle.pyRestTable

        # fmt: off
        warnings.warn(
            f"Use 'table_style={choice}' instead of"
            f" deprecated option 'tablefmt=\"{tablefmt}\"'."
        )
        # fmt: on

    if printing is not None:
        warnings.warn(f"Keyword argument 'printing={printing}' is deprecated.")

    return table_style.value(lr.parse_runs())


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
    from databroker.queries import TimeRange

    from . import ipython_shell_namespace

    db = db or ipython_shell_namespace()["db"]
    # no APS X-ray experiment data before 1995!
    since = since or "1995"
    cat = db.v2.search(TimeRange(since=since))
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

    table = TableStyle.pyRestTable.value()
    table.labels = "plan quantity".split()
    for k in sorted(plans.keys(), key=sorter, reverse=True):
        table.addRow((k, sorter(k)))
    table.addRow(("TOTAL", n + 1))
    print(table)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

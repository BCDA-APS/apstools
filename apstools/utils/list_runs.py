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
import warnings
from collections import defaultdict
from typing import Any, Optional, Union

import pandas as pd
from databroker import catalog

from ._core import FIRST_DATA
from ._core import LAST_DATA
from ._core import TableStyle
from .query import db_query

logger = logging.getLogger(__name__)


def getRunData(
    scan_id: Union[int, str],
    db: Optional[catalog] = None,
    stream: str = "primary",
    query: Optional[dict[str, Any]] = None,
    use_v1: bool = True,
) -> pd.DataFrame:
    """
    Convenience function to get the run's data. Default is the ``primary`` stream.

    Parameters
    ----------
    scan_id : Union[int, str]
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).
    db : Optional[catalog], optional
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.
    stream : str, optional
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'
    query : Optional[dict[str, Any]], optional
        mongo query dictionary, used to filter the results.
        Default: None
        see: https://docs.mongodb.com/manual/reference/operator/query/
    use_v1 : bool, optional
        Chooses databroker API version between 'v1' or 'v2'.
        Default: True (meaning use the v1 API)

    Returns
    -------
    pd.DataFrame
        The run's data as a pandas DataFrame.

    Raises
    ------
    AttributeError
        If the specified stream does not exist in the run.
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


def getRunDataValue(
    scan_id: Union[int, str],
    key: str,
    db: Optional[catalog] = None,
    stream: str = "primary",
    query: Optional[dict[str, Any]] = None,
    idx: Union[int, str] = -1,
    use_v1: bool = True,
) -> Any:
    """
    Convenience function to get value of key in run stream.

    Defaults are last value of key in primary stream.

    Parameters
    ----------
    scan_id : Union[int, str]
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).
    key : str
        Name of the key (data column) in the table of the stream's data.
        Must match *identically*.
    db : Optional[catalog], optional
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.
    stream : str, optional
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'
    query : Optional[dict[str, Any]], optional
        mongo query dictionary, used to filter the results.
        Default: None
        see: https://docs.mongodb.com/manual/reference/operator/query/
    idx : Union[int, str], optional
        List index of value to be returned from column of table.
        Can be ``0`` for first value, ``-1`` for last value, ``"mean"``
        for average value, or ``"all"`` for the full list of values.
        Default: -1
    use_v1 : bool, optional
        Chooses databroker API version between 'v1' or 'v2'.
        Default: True (meaning use the v1 API)

    Returns
    -------
    Any
        The requested value from the run data.

    Raises
    ------
    KeyError
        If the key is not found in the stream or if idx is invalid.
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


def listRunKeys(
    scan_id: Union[int, str],
    key_fragment: str = "",
    db: Optional[catalog] = None,
    stream: str = "primary",
    query: Optional[dict[str, Any]] = None,
    strict: bool = False,
    use_v1: bool = True,
) -> list[str]:
    """
    Convenience function to list all keys (column names) in the scan's stream (default: primary).

    Parameters
    ----------
    scan_id : Union[int, str]
        Scan (run) identifier.
        Positive integer value is ``scan_id`` from run's metadata.
        Negative integer value is since most recent run in databroker.
        String is run's ``uid`` unique identifier (can abbreviate to
        the first characters needed to assure it is unique).
    key_fragment : str, optional
        Part or all of key name to be found in selected stream.
        For instance, if you specify ``key_fragment="lakeshore"``,
        it will return all the keys that include ``lakeshore``.
        Default: ""
    db : Optional[catalog], optional
        Bluesky database, an instance of ``databroker.catalog``.
        Default: will search existing session for instance.
    stream : str, optional
        Name of the bluesky data stream to obtain the data.
        Default: 'primary'
    query : Optional[dict[str, Any]], optional
        mongo query dictionary, used to filter the results.
        Default: None
        see: https://docs.mongodb.com/manual/reference/operator/query/
    strict : bool, optional
        If True, only return keys that exactly match key_fragment.
        Default: False
    use_v1 : bool, optional
        Chooses databroker API version between 'v1' or 'v2'.
        Default: True (meaning use the v1 API)

    Returns
    -------
    list[str]
        List of keys that match the criteria.
    """
    table = getRunData(scan_id, db=db, stream=stream, query=query)
    if strict:
        return [k for k in table.keys() if k == key_fragment]
    return [k for k in table.keys() if key_fragment in k]


@dataclasses.dataclass
class ListRuns:
    """
    List the runs from the given catalog according to some options.

    Example::

        ListRuns(cat).to_dataframe()

    Public Methods
    -------------
    to_dataframe : Convert runs to pandas DataFrame
    to_table : Convert runs to table format
    parse_runs : Parse and return run data

    Internal Methods
    ---------------
    _get_by_key : Get value by key from metadata
    _check_cat : Check catalog validity
    _apply_search_filters : Apply search filters to catalog
    """

    cat: Optional[catalog] = None
    query: Optional[dict[str, Any]] = None
    keys: Optional[list[str]] = None
    missing: str = ""
    num: int = 20
    reverse: bool = True
    since: Optional[Union[str, datetime.datetime]] = None
    sortby: str = "time"
    timefmt: str = "%Y-%m-%d %H:%M:%S"
    until: Optional[Union[str, datetime.datetime]] = None
    ids: Optional[Union[int, str, list[Union[int, str]]]] = None
    hints_override: bool = False

    _default_keys: list[str] = dataclasses.field(
        default_factory=lambda: [
            "scan_id",
            "time",
            "uid",
            "plan_name",
            "num_events",
            "num_interruptions",
            "scan_id",
            "time",
            "uid",
            "plan_name",
            "num_events",
            "num_interruptions",
        ]
    )

    def _get_by_key(self, md: dict[str, Any], key: str) -> Any:
        """
        Get value by key from metadata.

        Parameters
        ----------
        md : dict[str, Any]
            Metadata dictionary
        key : str
            Key to look up

        Returns
        -------
        Any
            Value associated with key, or missing value if not found
        """
        if key in md:
            return md[key]
        return self.missing

    def _check_cat(self) -> None:
        """
        Check catalog validity.

        Raises
        ------
        ValueError
            If catalog is None
        """
        if self.cat is None:
            raise ValueError("No catalog specified")

    def _apply_search_filters(self) -> None:
        """
        Apply search filters to catalog.

        Raises
        ------
        ValueError
            If catalog is None
        """
        self._check_cat()
        if self.query:
            self.cat = db_query(self.cat, self.query)

    def parse_runs(self) -> list[dict[str, Any]]:
        """
        Parse and return run data.

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing run data
        """
        self._apply_search_filters()

        def _sort(uid: str) -> Any:
            """
            Sort function for runs.

            Parameters
            ----------
            uid : str
                Run UID

            Returns
            -------
            Any
                Sort key
            """
            if self.sortby == "time":
                return self._get_by_key(self.cat.v1[uid].metadata, "time")
            elif self.sortby == "scan_id":
                return self._get_by_key(self.cat.v1[uid].metadata, "scan_id")
            else:
                return uid

        runs = []
        for uid in sorted(self.cat.v1, key=_sort, reverse=self.reverse)[: self.num]:
            md = self.cat.v1[uid].metadata
            run = {}
            for key in self.keys:
                run[key] = self._get_by_key(md, key)
            runs.append(run)
        return runs

    def _check_keys(self) -> None:
        """
        Check keys validity.

        Raises
        ------
        ValueError
            If keys is None
        """
        if self.keys is None:
            self.keys = self._default_keys

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert runs to pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame containing run data
        """
        self._check_keys()
        runs = self.parse_runs()
        return pd.DataFrame(runs)

    def to_table(
        self, fmt: Optional[TableStyle] = None
    ) -> Union[pd.DataFrame, Any]:
        """
        Convert runs to table format.

        Parameters
        ----------
        fmt : Optional[TableStyle], optional
            Table format style. Default: None

        Returns
        -------
        Union[pd.DataFrame, Any]
            Table containing run data
        """
        if fmt is None:
            fmt = TableStyle.pyRestTable
        df = self.to_dataframe()
        return fmt.value(df)


def listruns(
    cat: Optional[catalog] = None,
    keys: Optional[list[str]] = None,
    missing: str = "",
    num: int = 20,
    printing: Optional[bool] = None,  # DEPRECATED
    reverse: bool = True,
    since: Optional[Union[str, datetime.datetime]] = None,
    sortby: str = "time",
    tablefmt: Optional[str] = None,  # DEPRECATED
    table_style: TableStyle = TableStyle.pyRestTable,
    timefmt: str = "%Y-%m-%d %H:%M:%S",
    until: Optional[Union[str, datetime.datetime]] = None,
    ids: Optional[Union[int, str, list[Union[int, str]]]] = None,
    hints_override: bool = False,
    **query: Any,
) -> Union[pd.DataFrame, Any]:
    """
    List the runs from the given catalog according to some options.

    Parameters
    ----------
    cat : Optional[catalog], optional
        Bluesky database, an instance of ``databroker.catalog``.
        Default: None
    keys : Optional[list[str]], optional
        List of keys to include in output.
        Default: None
    missing : str, optional
        Value to use for missing keys.
        Default: ""
    num : int, optional
        Number of runs to return.
        Default: 20
    printing : Optional[bool], optional
        DEPRECATED: Use table_style instead.
        Default: None
    reverse : bool, optional
        If True, sort in reverse order.
        Default: True
    since : Optional[Union[str, datetime.datetime]], optional
        Only show runs since this time.
        Default: None
    sortby : str, optional
        Field to sort by.
        Default: "time"
    tablefmt : Optional[str], optional
        DEPRECATED: Use table_style instead.
        Default: None
    table_style : TableStyle, optional
        Table format style.
        Default: TableStyle.pyRestTable
    timefmt : str, optional
        Time format string.
        Default: "%Y-%m-%d %H:%M:%S"
    until : Optional[Union[str, datetime.datetime]], optional
        Only show runs until this time.
        Default: None
    ids : Optional[Union[int, str, list[Union[int, str]]]], optional
        Run IDs to include.
        Default: None
    hints_override : bool, optional
        Override hints.
        Default: False
    **query : Any
        Additional query parameters.

    Returns
    -------
    Union[pd.DataFrame, Any]
        Table containing run data
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
        hints_override=hints_override,
    )
    if query:
        lr.query = query
    return lr.to_table(table_style)


def summarize_runs(
    since: Optional[Union[str, datetime.datetime]] = None,
    db: Optional[catalog] = None,
) -> pd.DataFrame:
    """
    Summarize runs since a given time.

    Parameters
    ----------
    since : Optional[Union[str, datetime.datetime]], optional
        Only show runs since this time.
        Default: None
    db : Optional[catalog], optional
        Bluesky database, an instance of ``databroker.catalog``.
        Default: None

    Returns
    -------
    pd.DataFrame
        DataFrame containing run summary
    """
    from . import getCatalog

    cat = getCatalog(db)
    if since:
        cat = db_query(cat, {"time": {"$gte": since}})

    def sorter(plan_name: str) -> str:
        """
        Sort function for plan names.

        Parameters
        ----------
        plan_name : str
            Plan name

        Returns
        -------
        str
            Sort key
        """
        if plan_name.startswith("scan"):
            return "scan"
        return plan_name

    runs = []
    for uid in sorted(cat.v1, key=lambda x: sorter(cat.v1[x].metadata["plan_name"])):
        md = cat.v1[uid].metadata
        runs.append(
            {
                "scan_id": md.get("scan_id", ""),
                "time": md.get("time", ""),
                "uid": uid,
                "plan_name": md.get("plan_name", ""),
                "num_events": md.get("num_events", 0),
                "num_interruptions": md.get("num_interruptions", 0),
            }
        )
    return pd.DataFrame(runs)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

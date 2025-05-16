"""
Working with databroker catalogs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~copy_filtered_catalog
   ~findCatalogsInNamespace
   ~getCatalog
   ~getDatabase
   ~getDefaultCatalog
   ~getDefaultDatabase
   ~getStreamValues
   ~quantify_md_key_use
"""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import pyRestTable
from databroker import Broker, catalog as db_catalog
from databroker._drivers.mongo_normalized import BlueskyMongoCatalog
from databroker._drivers.msgpack import BlueskyMsgpackCatalog
from intake import Catalog

from .list_runs import getRunData
from .profile_support import getDefaultNamespace, ipython_shell_namespace

logger = logging.getLogger(__name__)


def copy_filtered_catalog(
    source_cat: Union[Broker, Any],
    target_cat: Union[Broker, Any],
    query: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Copy filtered runs from source_cat to target_cat.

    Args:
        source_cat: instance of `databroker.Broker` or `databroker.catalog[name]`
        target_cat: instance of `databroker.Broker` or `databroker.catalog[name]`
        query: mongo query dictionary to filter results (default: None)
    """
    query = query or {}
    for i, uid in enumerate(source_cat.v2.search(query)):
        run = source_cat.v1[uid]
        logger.debug("%d  %s  #docs=%d", i + 1, uid, len(list(run.documents())))
        for key, doc in run.documents():
            target_cat.v1.insert(key, doc)


def findCatalogsInNamespace() -> Dict[str, Any]:
    """
    Return a dictionary of databroker catalogs in the default namespace.

    Returns:
        Dictionary mapping catalog names to catalog objects
    """
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


def getCatalog(ref: Optional[Union[str, Any]] = None) -> Any:
    """
    Return a catalog object.

    Args:
        ref: Catalog reference (default: None)

    Returns:
        Catalog object
    """
    if isinstance(ref, str):
        return db_catalog[ref]
    if ref is not None and hasattr(ref, "v2"):
        return ref.v2

    cat = getDefaultCatalog()
    if cat is None:
        raise ValueError("Cannot identify default databroker catalog.")
    return cat


def getDatabase(
    db: Optional[Any] = None,
    catalog_name: Optional[Union[str, Any]] = None,
) -> Any:
    """
    Return Bluesky database using keyword guides or default choice.

    Args:
        db: Bluesky database instance (default: None)
        catalog_name: Name of databroker v2 catalog (default: None)

    Returns:
        Bluesky database instance
    """
    if not hasattr(db, "v2"):
        if hasattr(catalog_name, "name") and catalog_name in db_catalog:
            db = catalog_name
        elif catalog_name is None:
            db = getDefaultDatabase()
        else:
            db = db_catalog[catalog_name]
    return db.v2


def getDefaultCatalog() -> Any:
    """
    Return the default databroker catalog.

    Returns:
        Default catalog object
    """
    cats = findCatalogsInNamespace()
    if len(cats) == 1:
        return cats[list(cats.keys())[0]]
    if len(cats) > 1:
        choices = "   ".join([f"{k} ({v.name})" for k, v in cats.items()])
        raise ValueError(
            "No catalog defined.  Multiple catalog objects available.  Specify one of these: {choices}"
        )

    cats = list(db_catalog)
    if len(cats) == 1:
        return db_catalog[cats[0]]
    if len(cats) > 1:
        choices = "   ".join([f'catalog["{k}"]' for k in cats])
        raise ValueError(
            "No catalog defined.  "
            "Multiple catalog configurations available."
            "  Create specific catalog object from one of these commands:"
            f" {choices}"
        )

    raise ValueError("No catalogs available.")


def getDefaultDatabase() -> Optional[Any]:
    """
    Find the "default" database (has the most recent run).

    Returns:
        Bluesky database instance or None
    """
    CATALOG_CLASSES = (Broker, BlueskyMongoCatalog, BlueskyMsgpackCatalog, Catalog)
    g = ipython_shell_namespace()
    if len(g) == 0:
        g = globals()

    db_list = []
    for v in g.values():
        if isinstance(v, CATALOG_CLASSES):
            db_list.append(v)

    if len(db_list) == 0:
        return None
    if len(db_list) == 1:
        return db_list[0]

    time_ref = {}
    for cat_name in list(db_catalog):
        cat = db_catalog[cat_name]
        if cat in db_list:
            if len(cat) > 0:
                run = cat.v2[-1]
                t = run.metadata["start"]["time"]
            else:
                t = 0
            time_ref[cat_name] = t, cat

    highest = max([v[0] for v in time_ref.values()])
    choices = [v[1] for v in time_ref.values() if v[0] == highest]
    if len(choices) == 0:
        return None
    return sorted(choices)[-1]


def getStreamValues(
    scan_id: Union[str, int],
    key_fragment: str = "",
    db: Optional[Any] = None,
    stream: str = "baseline",
    query: Optional[Dict[str, Any]] = None,
    use_v1: bool = True,
) -> pd.DataFrame:
    """
    Get values from a previous scan stream in a databroker catalog.

    Args:
        scan_id: Scan identifier
        key_fragment: Filter data by key fragment (default: "")
        db: Database instance (default: None)
        stream: Stream name (default: "baseline")
        query: Additional query parameters (default: None)
        use_v1: Use v1 API (default: True)

    Returns:
        DataFrame containing stream values
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


def quantify_md_key_use(
    key: Optional[str] = None,
    db: Optional[Any] = None,
    catalog_name: Optional[str] = None,
    since: Optional[float] = None,
    until: Optional[float] = None,
    query: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Quantify metadata key usage in a database.

    Args:
        key: Metadata key to analyze (default: None)
        db: Database instance (default: None)
        catalog_name: Catalog name (default: None)
        since: Start time (default: None)
        until: End time (default: None)
        query: Additional query parameters (default: None)

    Returns:
        DataFrame with key usage statistics
    """
    from databroker.queries import TimeRange

    key = key or "plan_name"
    catalog_name = catalog_name or "mongodb_config"
    query = query or {}
    since = since or "1995-01-01"
    until = until or "2100-12-31"

    cat = (db or db_catalog[catalog_name]).v2.search(TimeRange(since=since, until=until)).search(query)

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


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

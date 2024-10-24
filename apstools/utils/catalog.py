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

import pandas as pd
import pyRestTable

from .list_runs import getRunData
from .profile_support import getDefaultNamespace
from .profile_support import ipython_shell_namespace

logger = logging.getLogger(__name__)


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


def findCatalogsInNamespace():
    """Return a dictionary of databroker catalogs in the default namespace."""
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


def getCatalog(ref=None):
    """Return a catalog object."""
    from databroker import catalog

    if isinstance(ref, str):  # and ref in databroker.catalog:
        return catalog[ref]
    if ref is not None and hasattr(ref, "v2"):
        return ref.v2

    cat = getDefaultCatalog()
    if cat is None:
        raise ValueError("Cannot identify default databroker catalog.")
    return cat


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
    from databroker import catalog

    if not hasattr(db, "v2"):
        # fmt: off
        if (
            hasattr(catalog_name, "name")
            and catalog_name in catalog
        ):
            # in case a catalog was passed as catalog_name
            db = catalog_name
        elif catalog_name is None:
            db = getDefaultDatabase()
        else:
            db = catalog[catalog_name]
        # fmt: on
    return db.v2


def getDefaultCatalog():
    """Return the default databroker catalog."""
    from databroker import catalog

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
            "No catalog defined.  Multiple catalog objects available.  Specify one of these: {choices}"
        )

    cats = list(catalog)
    if len(cats) == 1:
        return catalog[cats[0]]
    if len(cats) > 1:
        choices = "   ".join([f'catalog["{k}"]' for k in cats])
        raise ValueError(
            "No catalog defined.  "
            "Multiple catalog configurations available."
            "  Create specific catalog object from one of these commands:"
            f" {choices}"
        )

    raise ValueError("No catalogs available.")


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
    from databroker import Broker
    from databroker import catalog as db_catalog
    from databroker._drivers.mongo_normalized import BlueskyMongoCatalog
    from databroker._drivers.msgpack import BlueskyMsgpackCatalog
    from intake import Catalog

    CATALOG_CLASSES = (Broker, BlueskyMongoCatalog, BlueskyMsgpackCatalog, Catalog)
    # look through the console namespace
    g = ipython_shell_namespace()
    if len(g) == 0:
        # ultimate fallback
        g = globals()

    # note all database instances in memory
    db_list = []
    for v in g.values():
        if isinstance(v, CATALOG_CLASSES):
            db_list.append(v)

    # easy decisions first
    if len(db_list) == 0:
        return None
    if len(db_list) == 1:
        return db_list[0]

    # get the most recent run from each
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

    # pick the highest number for time
    highest = max([v[0] for v in time_ref.values()])
    choices = [v[1] for v in time_ref.values() if v[0] == highest]
    if len(choices) == 0:
        return None
    # return the catalog with the most recent timestamp
    return sorted(choices)[-1]


def getStreamValues(scan_id, key_fragment="", db=None, stream="baseline", query=None, use_v1=True):
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


def quantify_md_key_use(
    key=None,
    db=None,
    catalog_name=None,
    since=None,
    until=None,
    query=None,
):
    """
    Print table of different ``key`` values and how many times each appears.

    PARAMETERS

    key *str* :
        one of the metadata keys in a run's start document
        (default: ``plan_name``)
    db *object* :
        Instance of databroker v1 ``Broker`` or v2 ``catalog``
        (default: see ``catalog_name`` keyword argument)
    catalog_name *str* :
        Name of databroker v2 catalog, used when supplied ``db`` is ``None``.
        (default: ``mongodb_config``)
    since *str* :
        include runs that started on or after this ISO8601 time
        (default: ``1995-01-01``)
    until *str* :
        include runs that started before this ISO8601 time
        (default: ``2100-12-31``)
    query *dict* :
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

        In [8]: quantify_md_key_use(catalog_name="apstools_test")
        ========= =====
        plan_name #runs
        ========= =====
        count     26
        scan      27
        ========= =====

        In [9]: quantify_md_key_use(catalog_name="usaxs_test")
        ========================== =====
        plan_name                  #runs
        ========================== =====
        Flyscan                    1
        TuneAxis.tune              1
        count                      1
        measure_USAXS_Transmission 1
        run_Excel_file             1
        snapshot                   1
        tune_a2rp                  1
        tune_ar                    1
        tune_m2rp                  1
        tune_mr                    1
        ========================== =====
    """
    from databroker import catalog
    from databroker.queries import TimeRange

    key = key or "plan_name"
    catalog_name = catalog_name or "mongodb_config"
    query = query or {}
    since = since or "1995-01-01"
    until = until or "2100-12-31"

    cat = (
        (db or catalog[catalog_name])
        .v2.search(TimeRange(since=since, until=until))
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


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

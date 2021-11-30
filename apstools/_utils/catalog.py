"""
Working with databroker catalogs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~findCatalogsInNamespace
   ~getCatalog
   ~getDefaultCatalog
   ~getDatabase
   ~getDefaultDatabase
   ~db_query
"""

import databroker
import databroker.queries
import databroker._drivers.mongo_normalized
import databroker._drivers.msgpack

from ..callbacks.spec_file_writer import _rebuild_scan_command
from . import getDefaultNamespace
from . import ipython_shell_namespace
from ._core import CATALOG_CLASSES
from ._core import FIRST_DATA
from ._core import LAST_DATA


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


def getCatalog(ref=None):
    if isinstance(ref, str):  # and ref in databroker.catalog:
        return databroker.catalog[ref]
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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

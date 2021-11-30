"""
Searching databroker catalogs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~db_query
"""

import databroker
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

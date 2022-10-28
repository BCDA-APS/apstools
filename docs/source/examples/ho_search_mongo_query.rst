How to Search in Databroker
===========================

Show how to `search <https://github.com/BCDA-APS/apstools/issues/674>`__
a catalog with `MongoDB
Query <https://www.mongodb.com/docs/manual/reference/operator/query/>`__.

First, examine the databroker `search and
lookup <https://blueskyproject.io/databroker/tutorials/search-and-lookup.html>`__
tutorial.

Custom queries can be done with the `MongoDB query
language <https://www.mongodb.com/docs/manual/reference/operator/query/>`__.

Additional help with the MongoDB query language, operators, and syntax
may be found online, such as
`w3schools <https://www.w3schools.com/python/python_mongodb_query.asp>`__.

listruns
--------

Show with additional keys:

-  plan
-  dets
-  md
-  start position
-  end position
-  number of points

MongoDB Query with ``listruns()``
---------------------------------

MongoDB Query with a databroker catalog
---------------------------------------

Goals
-----

-  using ``apstools.utils.listruns()``

   -  plan
   -  dets
   -  md
   -  start position
   -  end position
   -  number of points

-  using start or stop document metadata
-  user
-  sample
-  Proposal or ESAF ID
-  fuzzy or misspelled terms
-  combination searches

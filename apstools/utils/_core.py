import databroker._drivers.mongo_normalized
import databroker._drivers.msgpack
import intake


FIRST_DATA = "1995-01-01"
LAST_DATA = "2100-12-31"

CATALOG_CLASSES = (
    databroker.Broker,
    databroker._drivers.mongo_normalized.BlueskyMongoCatalog,
    databroker._drivers.msgpack.BlueskyMsgpackCatalog,
    intake.Catalog,
)
MONGO_CATALOG_CLASSES = (
    databroker.Broker,
    databroker._drivers.mongo_normalized.BlueskyMongoCatalog,
    # intake.Catalog,
)
MAX_EPICS_STRINGOUT_LENGTH = 40

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

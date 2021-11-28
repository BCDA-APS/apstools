.. apstools documentation master file, created by
   sphinx-quickstart on Wed Nov 15 14:58:09 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
apstools
========

Various Python tools for use with Bluesky at the APS

Summary Contents
----------------

* :ref:`applications`
* :ref:`examples`
* :ref:`api_documentation`
  * Devices

    * :ref:`APS general support <devices.aps_support>`
    * :ref:`area detector support <devices.area_detector>`
    * :ref:`motors, positioners, ... <devices.motors>`
    * :ref:`scalers <devices.scalers>`
    * :ref:`shutters <devices.shutters>`
    * :ref:`synApps support <devices.synApps_support>`
    * :ref:`temperature controllers <devices.temperature_controllers>`

  * Plans
     * :ref:`batch scanning support <plans.batch>`
     * :ref:`custom scans <plans.custom>`
       * :func:`~apstools.plans.lineup()`

  * Utilities
     * :ref:`Finding ... <utils.finding>`
     * :ref:`Listing ... <utils.listing>`
     * :ref:`Reporting ... <utils.reporting>`
     * :ref:`Other ... <utils.other>`

* :ref:`license`

Package Information
-------------------

============= ========================================
version       |version|
published     |today|
copyright     2017-2022, UChicago Argonne, LLC
license       ANL OPEN SOURCE LICENSE (see LICENSE.txt file)
author        Pete R. Jemian <jemian@anl.gov>
============= ========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   install
   applications/index
   examples/index
   source/index
   changes
   license

See Also
==================

=============== ========================================
apstools home   https://BCDA-APS.github.io/apstools
apstools source https://github.com/BCDA-APS/apstools
apsbss home     https://BCDA-APS.github.io/apsbss
Bluesky home    https://blueskyproject.io/
Bluesky source  https://github.com/bluesky
=============== ========================================


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

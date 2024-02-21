========
Overview
========

The `apstools` package provides supplemental support for data acquisition using
the `Bluesky framework <https://blueskyproject.io>`__ at the `Advanced Photon
Source <https://www.aps.anl.gov/>`__.  The support consists of a thin Python
interface to EPICS record structures and databases not already supported in
`ophyd <https://blueskyproject.io/ophyd>`__.  Additional support is provided for
certain types of scans and data file writer support for common formats (such as
`SPEC <https://certif.com/spec_manual/user_1_4_1.html>`__ and
`NeXus <https://manual.nexusformat.org/user_manual.html>`__). See headings
in the Summary Contents below for more information:

Summary Contents
----------------

* :ref:`applications`
* :ref:`examples`
* :ref:`api_documentation`

  * Devices

    * :ref:`devices.aps_support`
    * :ref:`devices.area_detector`
    * :ref:`devices.motors`
    * :ref:`devices.scalers`
    * :ref:`devices.shutters`
    * :ref:`devices.slits`
    * :ref:`synApps`
    * :ref:`devices.temperature_controllers`

  * Plans
     * :ref:`batch scanning support <plans.batch>`
     * :ref:`custom scans <plans.custom>`

       * :func:`~apstools.plans.alignment.lineup()`

  * Utilities
     * :ref:`Finding ... <utils.finding>`
     * :ref:`Listing ... <utils.listing>`
     * :ref:`Reporting ... <utils.reporting>`
     * :ref:`Other ... <utils.other>`

Package Information
-------------------

============= ========================================
version       |version|
release       |release|
published     |today|
copyright     2017-2022, UChicago Argonne, LLC
license       ANL OPEN SOURCE LICENSE (see LICENSE.txt file)
author        Pete R. Jemian <jemian@anl.gov>
============= ========================================

See Also
-------------------

=============== ========================================
apstools home   https://BCDA-APS.github.io/apstools/latest/
apstools source https://github.com/BCDA-APS/apstools
apsbss home     https://BCDA-APS.github.io/apsbss
Bluesky home    https://blueskyproject.io/
Bluesky source  https://github.com/bluesky
=============== ========================================

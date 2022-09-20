#!/usr/bin/env python

import setuptools
import setuptools_scm

setuptools.setup(
    version=setuptools_scm.get_version(),
    # use_scm_version=True,
    setup_requires=["setuptools_scm"],
)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

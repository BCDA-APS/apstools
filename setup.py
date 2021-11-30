#!/usr/bin/env python

"""
Packaging setup for apstools.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

import pathlib
import sys
import versioneer


sys.path.insert(0, (pathlib.Path(__file__).parent / "apstools"))
import apstools as package


__entry_points__ = {
    "console_scripts": [
        "bluesky_snapshot = apstools.snapshot.application:snapshot_cli",
        "bluesky_snapshot_viewer = apstools.snapshot.application:snapshot_gui",
        "spec2ophyd = apstools.migration.spec2ophyd:main",
    ],
    # 'gui_scripts': [],
}


setup(
    author=package.__author__,
    author_email=package.__author_email__,
    classifiers=package.__classifiers__,
    description=package.__description__,
    entry_points=__entry_points__,
    license=package.__license__,
    long_description=package.__long_description__,
    install_requires=package.__install_requires__,
    name=package.__project__,
    # platforms        = package.__platforms__,
    packages=find_packages(exclude=package.__exclude_project_dirs__),
    include_package_data=True,
    url=package.__url__,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=package.__zip_safe__,
    python_requires=package.__python_version_required__,
)


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

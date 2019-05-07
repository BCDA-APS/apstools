"""
packaging setup for apstools
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
#from codecs import open
from os import path
import sys
import versioneer

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join('apstools', ))
import apstools as package


__entry_points__  = {
    'console_scripts': [
        'apstools_plan_catalog = apstools.examples:main',
        'bluesky_snapshot = apstools.snapshot:snapshot_cli',
        'bluesky_snapshot_viewer = apstools.snapshot:snapshot_gui',
        ],
    #'gui_scripts': [],
}


setup(
    author           = package.__author__,
    author_email     = package.__author_email__,
    classifiers      = package.__classifiers__,
    description      = package.__description__,
    entry_points     = __entry_points__,
    license          = package.__license__,
    long_description = package.__long_description__,
    install_requires = package.__install_requires__,
    name             = package.__project__,
    #platforms        = package.__platforms__,
    packages         = find_packages(exclude=package.__exclude_project_dirs__),
    url              = package.__url__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
    zip_safe         = package.__zip_safe__,
    python_requires  = package.__python_version_required__,
 )

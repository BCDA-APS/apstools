#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

__project__     = u'apstools'
__description__ = u"Various Python tools for use with BlueSky at the APS"
__copyright__   = u'2017-2019, UChicago Argonne, LLC'
__authors__     = [u'Pete Jemian', ]
__author__      = ', '.join(__authors__)
__institution__ = u"Advanced Photon Source, Argonne National Laboratory"
__author_email__= u"jemian@anl.gov"
__url__         = u"https://apstools.readthedocs.org"
__license__     = u"(c) " + __copyright__
__license__     += u" (see LICENSE.txt file for details)"
__platforms__   = 'any'
__zip_safe__    = False
__exclude_project_dirs__ = "docs examples tests".split()
__python_version_required__ = ">=3.5"

__package_name__ = __project__
__long_description__ = __description__

from ._requirements import learn_requirements
__install_requires__ = learn_requirements()
del learn_requirements

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Freely Distributable',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Chemistry',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development',
    'Topic :: Utilities',
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

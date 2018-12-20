
# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.

__project__     = u'APS_BlueSky_tools'
__description__ = u"Various Python tools for use with BlueSky at the APS"
__copyright__   = u'2017-2018, UChicago Argonne, LLC'
__authors__     = [u'Pete Jemian', ]
__author__      = ', '.join(__authors__)
__institution__ = u"Advanced Photon Source, Argonne National Laboratory"
__author_email__= u"jemian@anl.gov"
__url__         = u"http://APS_BlueSky_tools.readthedocs.org"
__license__     = u"(c) " + __copyright__
__license__     += u" (see LICENSE file for details)"
__platforms__   = 'any'
__zip_safe__    = False

__package_name__ = __project__
__long_description__ = __description__

__install_requires__ = ('databroker')
__install_requires__ = ()       # TODO: for conda build now
__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Freely Distributable',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
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

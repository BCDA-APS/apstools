.. _install:

Installation
============

Installation
############

The ``apstools`` package is available for installation
by ``conda``, ``pip``, or from source.

conda
-----

If you are using Anaconda Python and have ``conda`` installed, install the most
recent version with this command::

    $ conda install -c aps-anl-tag apstools

..    $ conda install -c conda-forge apstools

pip
---

Released versions of apstools are available on `PyPI
<https://pypi.python.org/pypi/apstools>`_.

If you have ``pip`` installed, then you can install::

    $ pip install apstools

source
------

The latest development versions of apstools can be downloaded from the
GitHub repository listed above::

    $ git clone http://github.com/BCDA-APS/apstools.git

To install in the standard Python location::

    $ cd apstools
    $ python setup.py install

To install in user's home directory::

    $ python setup.py install --user

To install in an alternate location::

    $ python setup.py install --prefix=/path/to/installation/dir

Required Libraries
##################

The repository's ``environment.yml`` file lists the additional packages
required by ``apstools``.  Most packages are available as conda packages
from https://anaconda.org.  The others are available on
https://PyPI.python.org.  Among the required packages:

  - python>=3.7
  - bluesky, databroker, ophyd
  - h5py
  - pandas
  - pyEpics
  - pyqt=5
  - pyRestTable
  - qt=5
  - spec2nexus
  - xlrd


.. _install:

Installation
============

The ``apstools`` package is available for installation
by ``conda``, ``pip``, or from source.

conda
-----

If you are using Anaconda Python and have ``conda`` installed, install the most
recent version with this command::

    $ conda install conda-forge::apstools

pip
---

Released versions of apstools are available on `PyPI
<https://pypi.python.org/pypi/apstools>`_.

If you have ``pip`` installed, then you can install::

    $ pip install apstools

development
-----------

The latest development versions of apstools can be downloaded from the
GitHub repository listed above.  Install from the source directory using
``pip`` in editable mode:

.. code-block:: bash
    :linenos:

    ENV_NAME=apstools
    git clone http://github.com/BCDA-APS/apstools
    cd apstools
    conda create -n "${ENV_NAME}" python pyepics apsu::aps-dm-api
    conda activate "${ENV_NAME}"
    pip install -e .[all]

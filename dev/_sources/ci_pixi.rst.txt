.. _ci_pixi:

Maintain CI With Pixi
=====================

The unit-test workflow uses Pixi to keep its supported dependency environments
reproducible. The committed ``pixi.lock`` file is the CI baseline.

Locked Baseline
---------------

Normal CI installs a named Pixi environment with ``--locked``. A manifest
change without a matching lockfile update fails installation rather than
silently resolving a new environment.

The supported environments are ``py311``, ``py312``, ``py313``, ``py314``, and
``py315``.
The default environment is currently an alias for ``py313``.

Updating the Baseline
---------------------

A scheduled workflow runs ``pixi update`` and opens a pull request containing
``pixi.lock`` and a dependency-change report. Review the generated package
changes and allow the complete locked test matrix to run before merging the
update.

The update workflow is also available through manual dispatch. Do not update
``pixi.lock`` directly on ``main``.

Latest-Dependency Canary
------------------------

A separate scheduled and manually dispatched workflow updates each named
environment and runs the test matrix without changing the committed lockfile.
This detects upstream compatibility problems before they enter the supported
baseline. Canary failures are non-blocking.

Local Development
-----------------

Use the pinned Pixi version from CI when reproducing an environment:

.. code-block:: bash

   pixi install --locked -e py313
   pixi run --locked -e py313 pytest -q .

On NFS-backed home directories, put the Pixi package cache on local storage
before solving or installing:

.. code-block:: bash

   export RATTLER_CACHE_DIR=/tmp/pixi-cache

Use a local filesystem workspace copy for long lockfile solves when necessary.

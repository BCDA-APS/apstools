# pylint: disable=unspecified-encoding
"""
Setup for for this beam line's APS Data Management Python API client.

This setup must be done before the first DM_WorkflowConnector() object is
created.  The ``setup_file`` is the bash shell script provided by the APS Data
Management for the user's account.
"""

import logging
import os
import pathlib

logger = logging.getLogger(__name__)


def dm_setup(setup_file):
    """
    Configure data management from its bash setup script.

    The return result defines the ``BDP_WORKFLOW_OWNER`` symbol.
    """
    env_var_file = pathlib.Path(setup_file)
    logger.info("APS DM environment file: %s", str(env_var_file))
    env_vars = {}
    with open(env_var_file) as script:
        for line in script.readlines():
            if not line.startswith("export "):
                continue
            key, value = line.strip().split()[-1].split("=")
            env_vars[key] = value

    # Assumed env_var_file is a bash script.  What if it is not?
    key = "DM_STATION_NAME"
    if key not in env_vars and key not in os.environ:
        raise KeyError(f"Did not find expected {key!r}")

    os.environ.update(env_vars)
    bdp_workflow_owner = os.environ["DM_STATION_NAME"].lower()

    logger.info("APS DM workflow owner: %s", bdp_workflow_owner)
    return bdp_workflow_owner

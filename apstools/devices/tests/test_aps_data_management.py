"""
Test the APS Data Management support.

It's a challenge to test since DM is only available on the APS subnet!
"""

import pytest

from .. import DM_WorkflowConnector
from ..aps_data_management import DM_STATION_NAME

# from dm.common.exceptions.dmException import DmException


@pytest.mark.parametrize("wf_name", ["a_workflow_name"])
def test_object(wf_name):
    wf = DM_WorkflowConnector(name="wf", workflow=wf_name)
    assert wf is not None

    assert wf.workflow.get() == wf_name
    assert wf.owner.get() == DM_STATION_NAME

    try:
        import dm

        assert wf.api is not None

        with pytest.raises(Exception) as exc:
            # FIXME: will fail if run on APS subnet!
            wf.workflows
        err_str = str(exc.value)
        # fmt: off
        assert (
            "Connection refused" in err_str
            or
            "invalid literal for int() with base 10" in err_str
        )
        # fmt: on

    except ModuleNotFoundError:
        pass

    assert wf.idle is not None

    assert wf.report_status() is None
    assert wf.report_processing_stages() is None

"""
Test the APS Data Management support.

It's a challenge to test since DM is only available on the APS subnet!
"""

import pytest

from .. import DM_WorkflowConnector
# from dm.common.exceptions.dmException import DmException

@pytest.mark.parametrize("wf_name", ["a_workflow_name"])
def test_object(wf_name):
    wf = DM_WorkflowConnector(name="wf", workflow=wf_name)
    assert wf is not None
    assert wf.workflow.get() == wf_name

    assert wf.api is not None
    assert wf.idle is not None
    assert wf.report_status() is None
    assert wf.report_processing_stages() is None

    with pytest.raises(Exception) as exc:
        # FIXME: will fail if run on APS subnet!
        workflow_list = wf.workflows
    assert str(exc.value).endswith(" Connection refused")
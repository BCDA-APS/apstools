"""
Connect with APS Data Management workflows.

Example::

    import bluesky
    from apstools.devices import DM_WorkflowConnector

    RE = bluesky.RunEngine()

    dm_workflow = DM_WorkflowConnector(name="dm_workflow", labels=["DM"])
    RE(
        dm_workflow.run_as_plan(
            workflow="example-01",
            filePath="/home/beams/S1IDTEST/.bashrc"
        )
    )

.. note::  :class:`~DM_WorkflowConnector()` requires APS Data Management package (``aps-dm-api >=5``)

.. autosummary::

    ~DM_WorkflowConnector

"""

__all__ = """
    DM_WorkflowConnector
""".split()

import logging
import time

from ophyd import Component
from ophyd import Device
from ophyd import Signal

logger = logging.getLogger(__name__)

NOT_AVAILABLE = "-n/a-"
NOT_RUN_YET = "not_run"
POLLING_PERIOD_S = 1.0
REPORT_PERIOD_DEFAULT = 10
REPORT_PERIOD_MIN = 1
STARTING = "running"
TIMEOUT_DEFAULT = 180  # TODO: Consider removing/renaming the timeout feature


class DM_WorkflowConnector(Device):
    """
    Support for the APS Data Management tools.

    The DM workflow dictionary of arguments (``workflow_args``) needs special
    attention.  Python's ``dict`` structure is not compatible with MongoDB.  In
    turn, ophyd does not support it. A custom plan can choose how to use the
    ``workflow_args`` dictionary:

    - use with DM workflow, as planned
    - add ``workflow_args`` to the start metadata
    - write as run stream::

        from apstools.devices import make_dict_device
        from apstools.plans import write_stream

        yield from write_stream(
            [make_dict_device(workflow_args, name="kwargs")],
            "workflow_args"
        )

    .. autosummary::

        ~api
        ~idle
        ~processing_jobs
        ~report_processing_stages
        ~report_status
        ~run_as_plan
        ~start_workflow
        ~workflows
        ~put_if_different
        ~_update_processing_data
    """

    job = None  # DM processing job (must update during workflow execution)
    _api = None  # DM processing API

    owner = Component(Signal, value="", kind="config")
    workflow = Component(Signal, value="")
    workflow_args = {}

    job_id = Component(Signal, value=NOT_RUN_YET)

    # exit_status = Component(Signal, value=NOT_RUN_YET)
    run_time = Component(Signal, value=0)
    stage_id = Component(Signal, value=NOT_RUN_YET)
    status = Component(Signal, value=NOT_RUN_YET)

    polling_period = Component(Signal, value=POLLING_PERIOD_S, kind="config")
    reporting_period = Component(Signal, value=REPORT_PERIOD_DEFAULT, kind="config")
    concise_reporting = Component(Signal, value=True, kind="config")

    def __repr__(self):
        """Default representation of class instance."""
        # fmt: off
        innards = f"owner='{self.owner.get()}'"
        innards += f", workflow='{self.workflow.get()}'"
        for key, value in sorted(self.workflow_args.items()):
            innards += f", {key}={value!r}"
        # fmt: on
        if self.job_id.get() != NOT_RUN_YET:
            innards += f", id={self.job_id.get()!r}"
            run_time = self.run_time.get()
            if run_time > 0:
                innards += f", {run_time=:.2f}"
            innards += f", stage_id={self.stage_id.get()!r}"
        innards += f", status={self.status.get()!r}"
        return f"{self.__class__.__name__}({innards})"

    def __init__(self, name=None, workflow=None, **kwargs):
        """Constructor."""
        if name is None:
            raise KeyError("Must provide value for 'name'.")
        super().__init__(name=name)

        if workflow is not None:
            self.workflow.put(workflow)
        self.workflow_args.update(kwargs)
        self.owner.put(self.api.username)

    def put_if_different(self, signal, value):
        """Put ophyd signal only if new value is different."""
        if signal.get() != value:
            signal.put(value)

    def getJob(self):
        """Get the current processing job object."""
        return self.api.getProcessingJobById(self.owner.get(), self.job_id.get())

    def _update_processing_data(self):
        """
        (internal) Called periodically (while process runs) to update self.job.

        Also updates certain ophyd signals.
        """
        if self.job_id.get() == NOT_RUN_YET:
            return
        self.job = self.getJob()

        rep = self.job.getDictRep()
        # self.put_if_different(self.exit_status, rep.get("exitStatus", NOT_AVAILABLE))
        self.put_if_different(self.run_time, rep.get("runTime", -1))
        self.put_if_different(self.stage_id, rep.get("stage", NOT_AVAILABLE))
        self.put_if_different(self.status, rep.get("status", NOT_AVAILABLE))

    @property
    def api(self):
        """Local copy of DM Processing API object."""
        from dm import ProcApiFactory

        if self._api is None:
            self._api = ProcApiFactory.getWorkflowProcApi()
        return self._api

    @property
    def idle(self):
        """Is DM Processing idle?"""
        return self.status.get() in (NOT_RUN_YET, "done")

    def report_status(self, t_offset=None):
        """Status report."""
        if self.concise_reporting.get():
            t = f"{self.__class__.__name__} {self.name}:"
            t += f" {self.workflow.get()!r}"
            t += f" {self.job_id.get()[:8]!r}"
            t += f" {self.status.get()!r}"
            t += f" {self.stage_id.get()!r}"
            if t_offset is not None:
                t += f" elapsed: {time.time()-t_offset:.0f}s"

            logger.info(t)

        else:
            self.report_processing_stages()

    def start_workflow(self, workflow="", timeout=TIMEOUT_DEFAULT, **kwargs):
        """
        Kickoff a DM workflow with optional reporting timeout.

        The reporting process will continue until the workflow ends or the
        timeout period is exceeded.  It does not affect the actual workflow.
        """
        from ..utils import run_in_thread

        if workflow == "":
            workflow = self.workflow.get()
        else:
            workflow = workflow
        if workflow == "":
            raise AttributeError("Must define a workflow name.")
        self.put_if_different(self.workflow, workflow)

        wfargs = self.workflow_args.copy()
        wfargs.update(kwargs)
        self.start_time = time.time()
        self._report_deadline = self.start_time

        def update_report_deadline(catch_up=False):
            period = max(self.reporting_period.get(), REPORT_PERIOD_MIN)
            if catch_up:  # catch-up (if needed) and set in near future
                new_deadline = round(self._report_deadline, 2)
                while time.time() > new_deadline:
                    new_deadline += period
            else:
                new_deadline = time.time() + period
            self._report_deadline = new_deadline

        def _reporter(*args, **kwargs):
            update_report_deadline(catch_up=False)
            self.report_status(t_offset=self.start_time)

        def _cleanup():
            """Call when DM workflow finishes."""
            self.stage_id.unsubscribe_all()
            self.status.unsubscribe_all()
            if "_report_deadline" in dir(self):
                del self._report_deadline

        @run_in_thread
        def _run_DM_workflow_thread():
            logger.info(
                "run DM workflow: %s with reporting time limit=%s s",
                self.workflow.get(),
                timeout,
            )
            self.job = self.api.startProcessingJob(
                workflowOwner=self.owner.get(),
                workflowName=workflow,
                argsDict=wfargs,
            )
            self.job_id.put(self.job["id"])
            logger.info(f"DM workflow started: {self}")
            # wait for workflow to finish
            deadline = time.time() + timeout
            while time.time() < deadline and self.status.get() not in "done failed timeout".split():
                self._update_processing_data()
                if "_report_deadline" not in dir(self) or time.time() >= self._report_deadline:
                    _reporter()
                time.sleep(self.polling_period.get())

            _cleanup()
            logger.info("Final workflow status: %s", self.status.get())
            if self.status.get() in "done failed".split():
                logger.info(f"{self}")
                self.report_status(self.start_time)
                return
            self.status.put("timeout")
            logger.info(f"{self}")
            # fmt: off
            logger.error(
                "Workflow %s timeout in %s s.", repr(self.workflow.get()), timeout
            )
            # raise TimeoutError(
            #     f"Workflow {self.workflow.get()!r}"
            #     f" did not finish in {timeout} s."
            # )
            # fmt: on

        self.job = None
        self.stage_id.put(NOT_RUN_YET)
        self.job_id.put(NOT_RUN_YET)
        self.status.put(STARTING)
        self.stage_id.subscribe(_reporter)
        self.status.subscribe(_reporter)
        _run_DM_workflow_thread()

    def run_as_plan(
        self,
        workflow: str = "",
        wait: bool = True,
        timeout: int = TIMEOUT_DEFAULT,
        **kwargs,
    ):
        """Run the DM workflow as a bluesky plan."""
        from bluesky import plan_stubs as bps

        if workflow == "":
            workflow = self.workflow.get()

        self.start_workflow(workflow=workflow, timeout=timeout, **kwargs)
        logger.info("plan: workflow started")
        if wait:
            while not self.idle:
                yield from bps.sleep(self.polling_period.get())

    @property
    def processing_jobs(self):
        """The list of DM processsing jobs."""
        return self.api.listProcessingJobs(self.owner.get())

    @property
    def workflows(self):
        """Return the list of workflows."""
        return self.api.listWorkflows(self.owner.get())

    def report_processing_stages(self, truncate=40):
        """
        Print a table about each stage of the workflow process.
        """
        import pyRestTable

        if self.job is None:
            return

        wf = self.job["workflow"]
        stage_keys = "status runTime exitStatus stdOut stdErr".split()
        table = pyRestTable.Table()
        table.labels = "stage_id process processTime".split() + stage_keys
        for stage_id, dstage in wf["stages"].items():
            childProcesses = dstage.get("childProcesses", {"": {}})
            for k, v in childProcesses.items():
                row = [stage_id, k]

                status = v.get("status")
                if status is None:
                    processTime = 0
                else:
                    submitTime = v.get("submitTime", time.time())
                    endTime = v.get("endTime", submitTime)  # might be unknown
                    processTime = max(0, min(endTime - submitTime, 999999))
                row.append(round(processTime, 3))

                for key in stage_keys:
                    value = v.get(key, "")
                    if key in ("runTime"):
                        value = round(v.get(key, 0), 4)
                    if key in ("stdOut", "stdErr"):
                        value = str(value).strip()[:truncate]
                    row.append(value)
                table.addRow(row)
        logger.info(
            f"{wf['description']!r}"
            f" workflow={wf['name']!r}"
            f" id={self.job['id'][:8]!r}"
            f" elapsed={time.time()-self.start_time:.1f}s"
            f"\n{self!r}"
            f"\n{table}"
        )

# pylint: disable=unspecified-encoding
"""
Setup for for this beam line's APS Data Management Python API client.

FIRST

The ``dm_setup(setup_file)`` function **must** be called first,
before any other calls to the ``dm`` package.  The ``setup_file``
argument is the bash script that activates the APS Data Management
conda environment for the workstation.  That file contains definitions
of environment variables needed by the functions below.

.. autosummary::

    ~dm_setup

..  DEVELOPERS NOTE
    Do not import 'dm' or any of its children at the global level in
    this file.  This allows the file to be imported in a Python
    environment that does not have the 'aps-dm-api' package installed.
    If any of the functions are called (that attempt to import from 'dm',
    those imports will raise exceptions as they are called.)

FUNCTIONS

.. autosummary::

    ~build_run_metadata_dict
    ~dm_add_workflow
    ~dm_api_cat
    ~dm_api_daq
    ~dm_api_dataset_cat
    ~dm_api_ds
    ~dm_api_file
    ~dm_api_filecat
    ~dm_api_proc
    ~dm_daq_wait_upload_plan
    ~dm_file_ready_to_process
    ~dm_get_daqs
    ~dm_get_experiment_datadir_active_daq
    ~dm_get_experiment_file
    ~dm_get_experiment_path
    ~dm_get_experiments
    ~dm_get_workflow
    ~dm_source_environ
    ~dm_start_daq
    ~dm_station_name
    ~dm_stop_daq
    ~dm_update_workflow
    ~dm_upload
    ~get_workflow_last_stage
    ~share_bluesky_metadata_with_dm
    ~validate_experiment_dataDirectory
    ~wait_dm_upload
    ~DM_WorkflowCache

:see: https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/Workflow-Processing-Service
"""

__all__ = """
    build_run_metadata_dict
    dm_add_workflow
    dm_api_cat
    dm_api_daq
    dm_api_dataset_cat
    dm_api_ds
    dm_api_file
    dm_api_filecat
    dm_api_proc
    dm_daq_wait_upload_plan
    dm_file_ready_to_process
    dm_get_daqs
    dm_get_experiment_datadir_active_daq
    dm_get_experiment_file
    dm_get_experiment_path
    dm_get_experiments
    dm_get_workflow
    dm_setup
    dm_source_environ
    dm_start_daq
    dm_station_name
    dm_stop_daq
    dm_update_workflow
    dm_upload
    get_workflow_last_stage
    share_bluesky_metadata_with_dm
    validate_experiment_dataDirectory
    wait_dm_upload
    DEFAULT_UPLOAD_TIMEOUT
    DEFAULT_UPLOAD_POLL_PERIOD
    DM_WorkflowCache
""".split()

import datetime
import json
import logging
import pathlib
import time
from os import environ
from typing import Any, Dict, List, Optional, Union

import pyRestTable

from bluesky import plan_stubs as bps

from .time_constants import MINUTE
from .time_constants import SECOND
from .time_constants import ts2iso

logger = logging.getLogger(__name__)

DEFAULT_PERIOD: float = 10 * SECOND
DEFAULT_WAIT: bool = True
DEFAULT_DM_EXPERIMENT_KEYS: List[str] = """
    id name startDate experimentType experimentStation
""".split()
DEFAULT_UPLOAD_TIMEOUT: float = 10 * MINUTE
DEFAULT_UPLOAD_POLL_PERIOD: float = 30 * SECOND
DM_SETUP_FILE: Optional[str] = None
WORKFLOW_DONE_STATES: List[str] = "done failed timeout aborted".split()
DM_ENV_SOURCED: bool = False


def dm_setup(setup_file: Union[str, pathlib.Path]) -> str:
    """
    Name the APS Data Management bash script that activates its conda environment.

    Parameters
    ----------
    setup_file : Union[str, pathlib.Path]
        Path to the bash script that activates the APS Data Management conda environment.

    Returns
    -------
    str
        The 'owner' of the DM workflows.

    Raises
    ------
    FileExistsError
        If the setup file does not exist.
    """
    global DM_SETUP_FILE

    if not pathlib.Path(setup_file).exists():
        DM_SETUP_FILE = None
        raise FileExistsError(f"{setup_file=} does not exist.")
    DM_SETUP_FILE = setup_file

    dm_source_environ()
    workflow_owner = environ["DM_STATION_NAME"].lower()

    logger.info("APS DM workflow owner: %s", workflow_owner)
    return workflow_owner


def build_run_metadata_dict(user_md: Dict[str, Any], **dm_kwargs) -> Dict[str, Any]:
    """
    Return a dictionary for use as Bluesky run metadata.

    Parameters
    ----------
    user_md : Dict[str, Any]
        User-provided metadata dictionary.
    **dm_kwargs
        Additional keyword arguments to include in the data management section.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the combined metadata.
    """
    _md = {
        "title": "title placeholder",
        "description": "description placeholder",
        "datetime": str(datetime.datetime.now()),
        "data_management": dm_kwargs,
    }
    _md.update(user_md)
    return _md


def validate_experiment_dataDirectory(dm_experiment_name: str) -> None:
    """
    Validate that the experiment exists and has a dataDirectory.

    Parameters
    ----------
    dm_experiment_name : str
        Name of the experiment to validate.

    Raises
    ------
    KeyError
        If the experiment does not have a 'dataDirectory'.
    """
    # Check that named experiment actually exists now.
    # Raises dm.ObjectNotFound if does not exist.
    experiment = dm_api_ds().getExperimentByName(dm_experiment_name)
    if "dataDirectory" not in experiment:
        # Cannot test that it exists since bluesky user might not have
        # access to that file system or permission to read that directory.
        raise KeyError(f"{dm_experiment_name=!r} does not have a 'dataDirectory'.")


def dm_add_workflow(workflow_file: Union[str, pathlib.Path]) -> Any:
    """
    Add APS Data Management workflow from file.

    Parameters
    ----------
    workflow_file : Union[str, pathlib.Path]
        Path to the workflow file to add.

    Returns
    -------
    Any
        The result of adding the workflow.
    """
    return dm_api_proc().addWorkflow(json.loads(open(workflow_file).read()))


def dm_get_workflow(workflow_name: str) -> Any:
    """
    Get named APS Data Management workflow.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow to get.

    Returns
    -------
    Any
        The requested workflow.
    """
    api = dm_api_proc()
    return api.getWorkflowByName(api.username, workflow_name)


def dm_update_workflow(workflow_file: Union[str, pathlib.Path]) -> Any:
    """
    Update APS Data Management workflow from file.

    Parameters
    ----------
    workflow_file : Union[str, pathlib.Path]
        Path to the workflow file to update.

    Returns
    -------
    Any
        The result of updating the workflow.
    """
    return dm_api_proc().updateWorkflow(json.loads(open(workflow_file).read()))


def dm_api_cat() -> Any:
    """
    Return the APS Data Management Catalog API object.

    Returns
    -------
    Any
        The Catalog API object.
    """
    from dm import CatApiFactory

    dm_source_environ()
    return CatApiFactory.getRunCatApi()


def dm_api_dataset_cat() -> Any:
    """
    Return the APS Data Management Dataset Metadata Catalog API object.

    Returns
    -------
    Any
        The Dataset Metadata Catalog API object.
    """
    from dm import CatApiFactory

    dm_source_environ()
    return CatApiFactory.getDatasetCatApi()


def dm_api_filecat() -> Any:
    """
    Return the APS Data Management Metadata Catalog Service API object.

    Returns
    -------
    Any
        The Metadata Catalog Service API object.
    """
    from dm import CatApiFactory

    dm_source_environ()
    return CatApiFactory.getFileCatApi()


def dm_api_daq() -> Any:
    """
    Return the APS Data Management Data Acquisition API object.

    Returns
    -------
    Any
        The Data Acquisition API object.
    """
    from dm import DaqApiFactory

    dm_source_environ()
    api = DaqApiFactory.getExperimentDaqApi()
    return api


def dm_api_ds() -> Any:
    """
    Return the APS Data Management Data Storage API object.

    Returns
    -------
    Any
        The Data Storage API object.
    """
    from dm import DsApiFactory

    dm_source_environ()
    api = DsApiFactory.getExperimentDsApi()
    return api


def dm_api_file() -> Any:
    """
    Return the APS Data Management File API object.

    Returns
    -------
    Any
        The File API object.
    """
    from dm import DsApiFactory

    dm_source_environ()
    api = DsApiFactory.getFileDsApi()
    return api


def dm_api_proc() -> Any:
    """
    Return the APS Data Management Processing API object.

    Returns
    -------
    Any
        The Processing API object.
    """
    from dm import ProcApiFactory

    dm_source_environ()
    api = ProcApiFactory.getWorkflowProcApi()
    return api


def dm_get_daqs(experimentName: str) -> List[Any]:
    """
    Return list of APS Data Management DAQ(s) for this experiment.

    Parameters
    ----------
    experimentName : str
        Name of the APS Data Management experiment.

    Returns
    -------
    List[Any]
        List of DAQ objects for the experiment.
    """
    api = dm_api_daq()
    # fmt: off
    return [
        daq
        for daq in api.listDaqs()
        if daq.get("experimentName") == experimentName
    ]
    # fmt: on


def dm_file_ready_to_process(
    experimentFilePath: str,  # path (abs or rel) to a file
    experimentName: str,
    compression: str = "",
    retrieveMd5Sum: bool = False,
) -> bool:
    """
    Check if DM determines the named file is ready for processing.

    Parameters
    ----------
    experimentFilePath : str
        Path (absolute or relative) to a file.
    experimentName : str
        Name of the experiment.
    compression : str, optional
        Compression type, by default "".
    retrieveMd5Sum : bool, optional
        Whether to retrieve MD5 sum, by default False.

    Returns
    -------
    bool
        True if the file is ready for processing, False otherwise.
    """
    return (
        dm_api_file()
        .statFile(experimentFilePath, experimentName, compression, retrieveMd5Sum)
        .get("readyForProcessing", False)
    )


def dm_source_environ() -> None:
    """
    Add APS Data Management environment variable definitions to this process.

    This function reads the bash script, searching for lines that start with
    "export ". Such lines define bash shell environment variables in the bash
    script.  This function adds those environment variables to the current
    environment.

    BASH COMMAND SUGGESTIONS::

        source /home/dm/etc/dm.setup.sh

        source ~/DM/etc/dm.setup.sh

    The suggestions follow a pattern: ``${DM_ROOT}/etc/dm.setup.sh`` where
    ``DM_ROOT`` is the location of the DM tools as installed in the current user
    account.

    Raises
    ------
    ValueError
        If DM setup file is undefined.
    KeyError
        If no environment variable definitions are found in the setup file.
    """
    global DM_ENV_SOURCED

    if DM_ENV_SOURCED:
        return

    if DM_SETUP_FILE is None:
        raise ValueError("DM setup file is undefined.  First call 'dm_setup(setup_file)'.")

    def chop(text: str) -> List[str]:
        return text.strip().split()[-1].split("=")

    # fmt: off
    ev = {
        chop(line)[0]: chop(line)[-1]
        for line in open(DM_SETUP_FILE).readlines()
        if line.startswith("export ")
    }
    if len(ev) == 0:
        raise KeyError(
            f"No environment variable definitions found in: {DM_SETUP_FILE}"
        )
    environ.update(ev)
    DM_ENV_SOURCED = True
    # fmt: on


def dm_start_daq(experimentName: str, dataDirectory: str, **daqInfo) -> Dict[str, Any]:
    """
    Start APS DM data acquisition (real-time directory monitoring and file upload).

    Parameters
    ----------
    experimentName : str
        Name of the APS Data Management experiment.
    dataDirectory : str
        Data directory URL.
    **daqInfo : Dict[str, Any]
        Dictionary of optional metadata (key/value pairs) describing data acquisition.
        See https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/API-Reference/DAQ-Service#dm.daq_web_service.api.experimentDaqApi.ExperimentDaqApi.startDaq
        for details.

    Returns
    -------
    Dict[str, Any]
        The daqInfo dictionary.
    """
    ret_daqInfo = dm_api_daq().startDaq(experimentName, dataDirectory, daqInfo)
    return ret_daqInfo


def dm_stop_daq(experimentName: str, dataDirectory: str) -> None:
    """
    Stop APS DM data acquisition (real-time directory monitoring and file upload).

    Parameters
    ----------
    experimentName : str
        Name of the APS Data Management experiment.
    dataDirectory : str
        Data directory URL.
    """
    dm_api_daq().stopDaq(experimentName, dataDirectory)


def dm_station_name() -> Optional[str]:
    """
    Return the APS Data Management station name.

    Returns
    -------
    Optional[str]
        The station name in lowercase, or None if not found.
    """
    dm_source_environ()
    nm = environ.get("DM_STATION_NAME")
    if nm is not None:
        return str(nm).lower()
    return None


def dm_upload(experimentName: str, dataDirectory: str, **daqInfo) -> Dict[str, Any]:
    """
    Upload data to APS Data Management.

    Parameters
    ----------
    experimentName : str
        Name of the APS Data Management experiment.
    dataDirectory : str
        Data directory URL.
    **daqInfo : Dict[str, Any]
        Dictionary of optional metadata (key/value pairs) describing data acquisition.

    Returns
    -------
    Dict[str, Any]
        The daqInfo dictionary.
    """
    ret_daqInfo = dm_api_daq().upload(experimentName, dataDirectory, daqInfo)
    return ret_daqInfo


def wait_dm_upload(
    experiment_name: str,
    experiment_file: str,
    timeout: float = DEFAULT_UPLOAD_TIMEOUT,
    poll_period: float = DEFAULT_UPLOAD_POLL_PERIOD,
) -> None:
    """
    (bluesky plan) Wait for APS DM data acquisition to upload a file.

    Parameters
    ----------
    experiment_name : str
        Name of the APS Data Management experiment.
    experiment_file : str
        Name (and path) of file in DM.
    timeout : float, optional
        Number of seconds to wait before raising a 'TimeoutError'.
        Default: DEFAULT_UPLOAD_TIMEOUT
    poll_period : float, optional
        Number of seconds to wait before check DM again.
        Default: DEFAULT_UPLOAD_POLL_PERIOD

    Raises
    ------
    TimeoutError
        If DM does not identify file within 'timeout' (seconds).
    """
    from dm import ObjectNotFound

    t0 = time.time()
    deadline = t0 + timeout
    yield from bps.null()  # now, it's a bluesky plan

    while time.time() <= deadline:
        try:
            # either this succeeds or raises an exception
            dm_get_experiment_file(experiment_name, experiment_file)
            return  # if successful
        except ObjectNotFound:
            yield from bps.sleep(poll_period)

    raise TimeoutError(
        f"No such file={experiment_file!r} found" f" in DM {experiment_name=!r}" f" after {time.time()-t0:.1f} s."
    )


# def dm_add_experiment(experiment_name, typeName=None, **kwargs):
#     """Create a new experiment.  (Use sparingly, if ever.)"""
#     typeName = typeName or "BDP"  # TODO: generalize, TEST, XPCS8, ...
#     dm_api_ds().addExperiment(experiment_name, typeName=typeName, **kwargs)


# def dm_delete_experiment(reference):
#     """Delete ALL of an existing experiment.  (No recovering from this!)"""
#     api = dm_api_ds()
#     if isinstance(reference, int):
#         api.deleteExperimentById(reference)
#     elif isinstance(reference, str):
#         api.deleteExperimentByName(reference)


def dm_get_experiment_file(experiment_name: str, experiment_file: str) -> Any:
    """
    Get experiment file.

    Parameters
    ----------
    experiment_name : str
        Name of the APS Data Management experiment. The experiment must exist.
    experiment_file : str
        Name (with path) of the experiment file.

    Returns
    -------
    Any
        FileMetadata object.

    Raises
    ------
    InvalidRequest
        In case experiment name or file path have not been provided.
    AuthorizationError
        In case user is not authorized to manage DM station.
    ObjectNotFound
        In case file with a given path does not exist.
    DmException
        In case of any other errors.
    """
    api = dm_api_filecat()
    return api.getExperimentFile(experiment_name, experiment_file)


def dm_get_experiment_path(experiment_name: str) -> Optional[pathlib.Path]:
    """
    Return the storageDirectory for the named APS Data Management experiment as a path.

    Parameters
    ----------
    experiment_name : str
        Name of the APS Data Management experiment. The experiment must exist.

    Returns
    -------
    Optional[pathlib.Path]
        Data directory for the experiment, as pathlib.Path object.

    Raises
    ------
    dm.ObjectNotFound
        When experiment is not found.
    """
    api = dm_api_ds()
    path = api.getExperimentByName(experiment_name).get("storageDirectory")
    if path is not None:
        path = pathlib.Path(path)
    return path


def dm_get_experiments(
    keys: List[str] = DEFAULT_DM_EXPERIMENT_KEYS,
    table: bool = False,
    default_value: str = "-na-",
) -> Union[List[Any], pyRestTable.Table]:
    """
    Get the most recent APS Data Management experiments (for the current station).

    Return result as either a list or a pyRestTable object (see ``table``).

    Parameters
    ----------
    keys : List[str], optional
        Data keys to be shown in the table.
        Default: DEFAULT_DM_EXPERIMENT_KEYS
    table : bool, optional
        If False (default), return a Python list.
        If True, return a pyRestTable Table() object.
    default_value : str, optional
        Table value if no data available for that key.
        Default: "-na-"

    Returns
    -------
    Union[List[Any], pyRestTable.Table]
        List of experiments or a table object.
    """
    experiments = dm_api_ds().getExperimentsByStation()
    if table and len(experiments) > 0:
        if not isinstance(keys, (list, tuple)) or len(keys) == 0:
            keys = experiments[0].DEFAULT_KEY_LIST
        tbl = pyRestTable.Table()
        tbl.labels = keys
        for entry in experiments:
            row = []
            for key in keys:
                value = entry.data.get(key, default_value)
                if isinstance(value, dict):
                    value = value.get("description", value)
                # do this in steps, value might be modified (ts2iso, for example)
                row.append(value)
            # datetime
            tbl.addRow(row)
        return tbl
    else:
        return experiments


def get_workflow_last_stage(workflow_name: str) -> str:
    """
    Return the name of the last stage in the named APS Data Management workflow.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow.

    Returns
    -------
    str
        Name of the last stage in the workflow.
    """
    return list(dm_get_workflow(workflow_name)["stages"])[-1]


def share_bluesky_metadata_with_dm(
    experimentName: str,
    workflow_name: str,
    run: Any,
    should_raise: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Once a bluesky run ends, share its metadata with APS DM.

    Only upload if we have a workflow.

    Parameters
    ----------
    experimentName : str
        Name of the experiment.
    workflow_name : str
        Name of the workflow.
    run : Any
        The bluesky run object.
    should_raise : bool, optional
        Whether to raise exceptions, by default False.

    Returns
    -------
    Optional[Dict[str, Any]]
        The DM metadata if successful, None otherwise.

    Raises
    ------
    InvalidArgument
        If the metadata is invalid.
    """
    import uuid

    from dm import InvalidArgument

    api = dm_api_dataset_cat()

    datasetInfo = {
        "experimentName": experimentName,
        "datasetName": f"run_uid8_{run.metadata['start']['uid'][:8]}",  # first part of run uid
        "workflow_name": workflow_name,
        "time_iso8601": ts2iso(run.metadata.get("start", {}).get("time", 0)),
        "bluesky_metadata": {k: getattr(run, k).metadata for k in run},  # all streams
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        "_id": str(uuid.uuid4()),  # FIXME: dm must fix this upstream
    }

    try:
        dm_md = api.addExperimentDataset(datasetInfo)
        logger.debug("Metadata shared to DM: %s", dm_md)
        return dm_md
    except InvalidArgument as ex:
        logger.error(ex)
        if should_raise:
            raise ex
        return None


class DM_WorkflowCache:
    """
    Keep track of one or more APS Data Management workflows for bluesky plans.

    .. autosummary::

        ~define_workflow
        ~print_cache_summary
        ~report_dm_workflow_output
        ~wait_workflows
        ~_update_processing_data
    """

    cache: Dict[str, Any] = {}

    def define_workflow(self, key: str, connector: Any) -> None:
        """
        Add a DM_WorkflowConnector object to be managed.

        Parameters
        ----------
        key : str
            Identifying text for this workflow object.
        connector : Any
            Instance of DM_WorkflowConnector.

        Raises
        ------
        KeyError
            If the key already exists in the cache.
        """
        if key in self.cache:
            raise KeyError(f"Key already exists: {key!r}")
        # TODO: validate connector
        self.cache[key] = connector

    def print_cache_summary(self, title: str = "Summary") -> None:
        """
        Summarize (in a table) the DM workflows in the cache.

        Parameters
        ----------
        title : str, optional
            Title for the summary table, by default "Summary".
        """
        table = pyRestTable.Table()
        table.labels = "# process status runTime started id".split()
        for i, k in enumerate(self.cache, start=1):
            v = self.cache[k]
            job_id = v.job_id.get()
            started = ts2iso(v.start_time)
            table.addRow((i, k, v.status.get(), v.run_time.get(), started, job_id[:7]))
        print(f"\n{title}\n{table}")

    def report_dm_workflow_output(self, final_stage_id: str) -> None:
        """
        Print a final (summary) report about a single DM workflow.

        Parameters
        ----------
        final_stage_id : str
            Text key of the last stage in the workflow.
        """
        for wf in self.cache.values():
            job = wf.getJob()
            stage = job.getWorkflowStage(final_stage_id)  # example: "06-DONE"
            for process in stage.get("childProcesses", {}).values():
                for key in "stdOut stdErr".split():
                    value = str(process.get(key, "")).strip()
                    if len(value):
                        print(f"{final_stage_id}  {key}:\n{value}")
                        print("~" * 50)

    def wait_workflows(self, period: float = DEFAULT_PERIOD, wait: bool = DEFAULT_WAIT) -> None:
        """
        (plan) Wait (if True) for existing workflows to finish.

        Parameters
        ----------
        period : float, optional
            Time between reports while waiting for all workflows to finish processing.
            Default: DEFAULT_PERIOD
        wait : bool, optional
            Should RE wait for all workflows to finish?
            Default: DEFAULT_WAIT
        """
        print(f"DEBUG: wait_workflows(): waiting={wait}")
        if wait:
            print(f"Waiting for all previous workflows ({len(self.cache)}) to finish...")
            for workflow in self.cache.values():
                # wait for each workflow to end
                while workflow.status.get() not in WORKFLOW_DONE_STATES:
                    print(f"Waiting for {workflow=}")
                    yield from bps.sleep(period)

    def _update_processing_data(self) -> None:
        """Update all the workflows in the cache (from the DM server)."""
        for wf in self.cache.values():
            wf._update_processing_data()


def dm_daq_wait_upload_plan(id: str, period: float = DEFAULT_PERIOD) -> None:
    """
    Plan: Wait for DAQ uploads to finish.

    Parameters
    ----------
    id : str
        The DAQ ID to wait for.
    period : float, optional
        Time between checks, by default DEFAULT_PERIOD.

    Raises
    ------
    ValueError
        If the upload status is not "done".
    """
    api = dm_api_daq()
    uploadInfo = api.getUploadInfo(id)
    uploadStatus = uploadInfo.get("status")
    while uploadStatus not in "done failed skipped aborted aborting".split():
        yield from bps.sleep(period)
        uploadInfo = api.getUploadInfo(id)
        uploadStatus = uploadInfo.get("status")
    logger.debug("DM DAQ upload info: %s", uploadInfo)
    if uploadStatus != "done":
        raise ValueError(
            f"DM DAQ upload status: {uploadStatus!r}, {id=!r}."
            f"  Processing error message(s): {uploadInfo['errorMessage']}."
        )


def dm_get_experiment_datadir_active_daq(experiment_name: str, data_directory: str) -> Optional[Dict[str, Any]]:
    """
    Return the daqInfo dict for the active DAQ, or None.

    Parameters
    ----------
    experiment_name : str
        Name of the experiment.
    data_directory : str
        Path to the data directory.

    Returns
    -------
    Optional[Dict[str, Any]]
        The daqInfo dictionary if an active DAQ is found, None otherwise.
    """
    from dm.common.constants import dmProcessingStatus

    active_statuses = (
        dmProcessingStatus.DM_PROCESSING_STATUS_PENDING,
        dmProcessingStatus.DM_PROCESSING_STATUS_RUNNING,
    )
    for daq_info in dm_api_daq().listDaqs():
        if daq_info.get("experimentName") == experiment_name:
            if daq_info.get("dataDirectory") == data_directory:
                if daq_info.get("status") in active_statuses:
                    return daq_info
    return None
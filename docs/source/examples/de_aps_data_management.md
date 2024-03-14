# Integration with APS Data Management (DM)

> The APS Data Management System is a system for gathering together experimental
> data, metadata about the experiment and providing users access to the data
> based on a users role.

APS beamlines have been using DM to process acquired data (with DM workflows).
See the [documentation](https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/HowTos/Getting-Started) for more details.  This document describes a way to integrate DM with the Bluesky framework.  Before the integration is described, a brief overview of DM...

## DM Overview

For integration with the Bluesky framework, we provide a minimal explanation for these parts of DM:

- experiment
- DAQ
- workflow
- upload

### experiment

> The experiment is the central object for creating entries in the Data
> Management System.

Typically, a DM experiment will manage all data for a single proposal/ESAF at a
beamline.  Beamline staff will create the DM experiments they will need.

The **name** of the experiment will be used by bluesky to coordinate acquired data and runs with DM.

An experiment will create data storage with permissions for the beamline data
acquisition account and all the users listed in the proposal.

More info [here](https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/HowTos/Getting-Started#getting-some-data-into-the-system)

### DAQ

> ... overall purpose of this system is to get data into the system and provide
> access control to that data.

In DM, a *DAQ* monitors a local file directory tree (on a specific workstation)
and copies any new content to the DM experiment's data storage.

More info [here](https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/HowTos/Getting-Started#getting-files-into-data-management)

### workflow

> A workflow is simply a set of defined steps that will process data.

The steps to process data: move acquired data to
computation hosts (local or remote), run the computation applications, then move
any results to a final destination.  A workflow is capable of other activities,
such as communicating back to EPICS.

More info [here](https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/HowTos/Getting-Started#workflows-and-processing-data)

### upload

In addition to automatic file copying with a DAQ, DM provides for single file
uploads to the experiment storage.  This can be used for files, such as
configuration, that are not in the local data directory trees monitored by a
DAQ.

## Bluesky integration

Many beamlines operate with software that provides some general setup for the next user group.  Then, the user runs various plans to align
the instrument and sample, then to collect the scientific data.

### Setup User

Activities could include creating local storage directories, identifying
proposal and/or ESAF numbers, ...

The `setup_user()` procedure is a convenient place to enter the name of the DM
`experiment` to be used for the user's data collection.  Bluesky should remember
this name so that the user does not need to supply for any of their data
collection activities.  For example:

```py
def setup_user(dm_experiment_name: str = ""):
    yield from bps.mv(dm_experiment, dm_experiment_name)
```

where

```py
from ophyd import Signal
dm_experiment = Signal(name="dm_experiment", value="")
```

#### Start a DAQ if needed

Bluesky might direct some data acquisition to write data into local file storage
(such as area detector image files).  A DAQ can be started by `setup_user()` to
copy new files to the DM experiment.  For example:

```py
from apstools.utils import dm_get_experiment_datadir_active_daq, dm_start_daq

def setup_user(dm_experiment_name: str = ""):
    yield from bps.mv(dm_experiment, dm_experiment_name)

    # local directory tree to monitor
    data_directory = "/some/path/to/data/"
    # DM experiment subdirectory for upload
    dm_daq_directory = "something"
    daq = dm_get_experiment_datadir_active_daq(
        dm_experiment_name, data_directory)
    if daq is None:
        daq = dm_start_daq(
            dm_experiment_name,
            data_directory,
            destDirectory=dm_daq_directory
        )
    # remember this for later
    yield from bps.mv(dm_daq_id, daq["id])
```

where

```py
dm_daq_id = Signal(name="dm_daq_id", value="")
```

Quickly, this can become more complicated if more than one DAQ is needed.

The value for `dm_daq_directory` is to be decided by the software (called in the
workflow) that processes the data.

#### Upload a file if needed

It may be needed to upload a file during the `setup_user()` plan.  Here's an example:

```py
import pathlib
from apstools.utils import dm_upload

def setup_user(
    dm_experiment_name: str = "",
    upload_file: str = "",
):
    yield from bps.mv(dm_experiment, dm_experiment_name)

    # upload a file
    # DM experiment subdirectory for upload
    p = pathlib.Path(upload_file)
    dm_upload_directory = "something"
    dm_upload(
        dm_experiment_name,
        str(p.parent),  # the directory name
        experimentFilePath=p.name  # the file name
        destDirectory=dm_upload_directory,
    )
```

Like `dm_daq_directory` above, the value for `dm_upload_directory` is to be
decided by the software (called in the workflow) that processes the data.

### Data collection plan(s)

Integration of DM with bluesky plans is dependent on the type of scan to be
executed and how the workflow will interact.

Two general possibilities come to mind:

- file-based collection and workflow
- streaming-based collection and workflow

In either case, the `apstools.devices.DM_WorkflowConnector` is an ophyd-style
`Device` that is used to coordinate with a DM workflow.  Create a connector:

```py
from apstools.devices import DM_WorkflowConnector

    # ... later, in the bluesky plan ...
    # REPLACE "dm_workflow" with the name of the workflow to be used.
    # This could be a keyword argument to the plan!
    # The reporting settings could also be user-selectable keyword arguments.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(
        dm_workflow.concise_reporting, False,  # True: for less details
        dm_workflow.reporting_period, 60,  # for periodic reports (s)
    )
```

Start the workflow (with the `dm_workflow` object) in the data acquisition plan
as if it is a bluesky plan.  This way, the startup does not block the RunEngine
from its periodic responsibilities.

```py
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=999_999_999, # seconds (aka forever)
        # all kwargs after this line are DM argsDict content
        filePath=dm_directory,  # like dm_daq_directory
        experiment=dm_experiment.get(),
        # ... any other keyword args needed by the plan ...
    )
```

Here `dm_directory` is (like `dm_daq_directory` and `dm_upload_directory`
above) the experiment subdirectory where the workflow expects to find the files.

Note that the `timeout` parameter is for the background process that watches the
workflow's progress.  If the timeout is reached, the reporting stops but the
workflow itself is unaffected.

Any keywords expected by the plan should be included as user-selectable
arguments of the data collection plan, or determined by the plan itself.

#### File-based

In a *file* data collection and workflow, data is acquired first and stored
into files on local storage.  Upload of the files is managed either by a DAQ or
by direct call(s) to `apstools.utils.dm_upload()`.  If a DAQ is used, the
bluesky plan should wait until the DAQ reports the expected file(s) upload have
completed.  Then, bluesky tells DM to start the workflow and monitors it until
it completes.

It is a choice of the workflow if more than one of the same kind of workflow can
execute at the same time.  Some workflows expect specific files to exist and may
not tolerate their manipulation by another workflow running at the same time. DM
can be configured to control this with a scheduling queue.  Alternatively, this
decision process could be built into the bluesky plan.

The general outline:

1. Bluesky plan
   1. assembles run metadata dictionary
   2. prepares instrument for streaming data collection
   3. initiates data collection
   4. waits for data collection to finish
   5. waits for any DAQs to complete expected uploads (if required)
   6. waits for any existing workflows to finish (if required)
   7. starts DM workflow
   8. monitors workflow in the background (periodic reports)
   9. uploads run metadata to DM
2. DM workflow
   1. execute workflow steps as programmed

See this example file-based bluesky data acquisition [plan](https://github.com/APS-1ID-MPE/hexm-bluesky/blob/a0b12fcf392b12b3d498dab070aee1f535614b24/instrument/plans/bdp202403.py#L77-L248).

#### Streaming-based

In a *streaming* data collection and workflow, the workflow must be started
first so it can setup the tools to receive data that will be streamed.  A common
tool to use for this interprocess communication is EPICS PVAccess.  PVAccess is
preferred since it can comunicate structured data.  It may be easier to
communicate across network boundaries than EPICS ChannelAccess.

Without a detailed description or code, here is an outline of a possible
streaming-based data collection and workflow with bluesky and DM.

1. Bluesky plan
   1. creates a PVA object for reports from the workflow
   2. starts DM workflow, passing the name of its PVA object
   3. assembles run metadata dictionary
   4. prepares instrument for streaming data collection
   5. connects with any PVA objects from workflow, as needed
   6. waits for DM workflow to become ready
2. DM workflow
   1. execute workflow steps as programmed
      1. connects with bluesky PVA object
      2. creates its own PVA object for commands from workflow
      3. prepares itself for streaming data
      4. signals to bluesky that it is ready
3. data acquisition stream(s)
   1. bluesky initiates data collection
   2. DM workflow receives data
   3. either process signals the other while data is being collected
4. data collection finishes
   1. Either DM workflow signals or Bluesky signals
   2. bluesky reports on further progress of workflow
5. DM workflow finishes
6. Bluesky uploads run metadata to DM

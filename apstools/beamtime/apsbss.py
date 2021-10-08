#!/usr/bin/env python

"""
Retrieve specific records from the APS Proposal and ESAF databases.

This code provides the command-line application: ``apsbss``

.. note:: BSS: APS Beamline Scheduling System

EXAMPLES::

    apsbss current
    apsbss esaf 226319
    apsbss proposal 66083 2020-2 9-ID-B,C

EPICS SUPPORT

.. autosummary::

    ~connect_epics
    ~epicsClear
    ~epicsSetup
    ~epicsUpdate

APS ESAF & PROPOSAL ACCESS

.. autosummary::

    ~getCurrentCycle
    ~getCurrentEsafs
    ~getCurrentInfo
    ~getCurrentProposals
    ~getEsaf
    ~getProposal
    ~iso2datetime
    ~listAllBeamlines
    ~listAllRuns
    ~listRecentRuns
    ~printColumns
    ~trim

APPLICATION

.. autosummary::

    ~cmd_current
    ~cmd_esaf
    ~cmd_list
    ~cmd_proposal
    ~get_options
    ~main
"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

import datetime
import dm  # APS data management library
import logging
import os
import pyRestTable
import sys
import time
import warnings
import yaml

# logger = logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

DM_APS_DB_WEB_SERVICE_URL = "https://xraydtn01.xray.aps.anl.gov:11236"
CONNECT_TIMEOUT = 5
POLL_INTERVAL = 0.01

api_bss = dm.BssApsDbApi(DM_APS_DB_WEB_SERVICE_URL)
api_esaf = dm.EsafApsDbApi(DM_APS_DB_WEB_SERVICE_URL)

parser = None

_cache_ = {}


class EpicsNotConnected(Exception):
    ...


class DmRecordNotFound(Exception):
    ...


class EsafNotFound(DmRecordNotFound):
    ...


class ProposalNotFound(DmRecordNotFound):
    ...


def connect_epics(prefix):
    """
    Connect with the EPICS database instance.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix
    """
    from .apsbss_ophyd import EpicsBssDevice

    t0 = time.time()
    t_timeout = t0 + CONNECT_TIMEOUT
    bss = EpicsBssDevice(prefix, name="bss")
    while not bss.connected and time.time() < t_timeout:
        time.sleep(POLL_INTERVAL)
    if not bss.connected:
        raise EpicsNotConnected(
            f"Did not connect with EPICS {prefix} in {CONNECT_TIMEOUT}s"
        )
    t_connect = time.time() - t0
    logger.debug("connected in %.03fs", t_connect)
    return bss


def epicsClear(prefix):
    """
    Clear the EPICS database.
    Connect with the EPICS database instance.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix
    """
    logger.debug("clear EPICS %s", prefix)
    bss = connect_epics(prefix)

    bss.status_msg.put("clear PVs ...")
    t0 = time.time()
    bss.clear()
    t_clear = time.time() - t0
    logger.debug("cleared in %.03fs", t_clear)
    bss.status_msg.put("Done")


def epicsUpdate(prefix):
    """
    Update EPICS database instance with current ESAF & proposal info.
    Connect with the EPICS database instance.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix
    """
    logger.debug("update EPICS %s", prefix)
    bss = connect_epics(prefix)

    bss.status_msg.put("clearing PVs ...")
    bss.clear()

    cycle = bss.esaf.aps_cycle.get()

    beamline = bss.proposal.beamline_name.get()
    # sector = bss.esaf.sector.get()
    esaf_id = bss.esaf.esaf_id.get().strip()
    proposal_id = bss.proposal.proposal_id.get().strip()

    if len(beamline) == 0:
        bss.status_msg.put(
            f"undefined: {bss.proposal.beamline_name.pvname}"
        )
        raise ValueError(
            "must set beamline name in "
            f"{bss.proposal.beamline_name.pvname}"
        )
    elif beamline not in listAllBeamlines():
        bss.status_msg.put(f"unrecognized: {beamline}")
        raise ValueError(f"{beamline} is not recognized")
    if len(cycle) == 0:
        bss.status_msg.put(f"undefined: {bss.esaf.aps_cycle.pvname}")
        raise ValueError(
            f"must set APS cycle name in {bss.esaf.aps_cycle.pvname}"
        )
    elif cycle not in listAllRuns():
        bss.status_msg.put(f"unrecognized: {cycle}")
        raise ValueError(f"{cycle} is not recognized")

    if len(esaf_id) > 0:
        bss.status_msg.put(f"get ESAF {esaf_id} from APS ...")
        esaf = getEsaf(esaf_id)

        bss.status_msg.put("set ESAF PVs ...")
        bss.esaf.description.put(esaf["description"])
        bss.esaf.end_date.put(esaf["experimentEndDate"])
        bss.esaf.esaf_status.put(esaf["esafStatus"])
        bss.esaf.raw.put(yaml.dump(esaf))
        bss.esaf.start_date.put(esaf["experimentStartDate"])
        bss.esaf.title.put(esaf["esafTitle"])

        bss.esaf.user_last_names.put(
            ",".join(
                [user["lastName"] for user in esaf["experimentUsers"]]
            )
        )
        bss.esaf.user_badges.put(
            ",".join([user["badge"] for user in esaf["experimentUsers"]])
        )
        bss.esaf.number_users_in_pvs.put(0)
        for i, user in enumerate(esaf["experimentUsers"]):
            obj = getattr(bss.esaf, f"user{i+1}")
            obj.badge_number.put(user["badge"])
            obj.email.put(user["email"])
            obj.first_name.put(user["firstName"])
            obj.last_name.put(user["lastName"])
            bss.esaf.number_users_in_pvs.put(i + 1)
            if i == 8:
                break
        bss.esaf.number_users_total.put(len(esaf["experimentUsers"]))

    if len(proposal_id) > 0:
        bss.status_msg.put(f"get Proposal {proposal_id} from APS ...")
        proposal = getProposal(proposal_id, cycle, beamline)

        bss.status_msg.put("set Proposal PVs ...")
        bss.proposal.end_date.put(proposal["endTime"])
        bss.proposal.mail_in_flag.put(
            proposal.get("mailInFlag") in ("Y", "y")
        )
        bss.proposal.proprietary_flag.put(
            proposal.get("proprietaryFlag") in ("Y", "y")
        )
        bss.proposal.raw.put(yaml.dump(proposal))
        bss.proposal.start_date.put(proposal["startTime"])
        bss.proposal.submitted_date.put(proposal["submittedDate"])
        bss.proposal.title.put(proposal["title"])

        bss.proposal.user_last_names.put(
            ",".join(
                [user["lastName"] for user in proposal["experimenters"]]
            )
        )
        bss.proposal.user_badges.put(
            ",".join([user["badge"] for user in proposal["experimenters"]])
        )
        bss.proposal.number_users_in_pvs.put(0)
        for i, user in enumerate(proposal["experimenters"]):
            obj = getattr(bss.proposal, f"user{i+1}")
            obj.badge_number.put(user["badge"])
            obj.email.put(user["email"])
            obj.first_name.put(user["firstName"])
            obj.last_name.put(user["lastName"])
            obj.institution.put(user["institution"])
            obj.institution_id.put(str(user["instId"]))
            obj.user_id.put(str(user["id"]))
            obj.pi_flag.put(user.get("piFlag") in ("Y", "y"))
            bss.proposal.number_users_in_pvs.put(i + 1)
            if i == 8:
                break
        bss.proposal.number_users_total.put(len(proposal["experimenters"]))

    bss.status_msg.put("Done")


def epicsSetup(prefix, beamline, cycle=None):
    """
    Define the beamline name and APS cycle in the EPICS database.
    Connect with the EPICS database instance.

    PARAMETERS

    prefix
        *str* :
        EPICS PV prefix
    beamline
        *str* :
        Name of beam line (as defined by the BSS)
    cycle
        *str* :
        Name of APS run cycle (as defined by the BSS).
        optional: default is current APS run cycle name.
    """
    if beamline not in listAllBeamlines():
        raise ValueError(f"{beamline} is not known")
    if cycle is not None and cycle not in listAllRuns():
        raise ValueError(f"{cycle} is not known")

    bss = connect_epics(prefix)

    cycle = cycle or getCurrentCycle()
    sector = int(beamline.split("-")[0])
    logger.debug(
        "setup EPICS %s %s cycle=%s sector=%s",
        prefix,
        beamline,
        cycle,
        sector,
    )

    bss.status_msg.put("clear PVs ...")
    bss.clear()

    bss.status_msg.put("write PVs ...")
    bss.esaf.aps_cycle.put(cycle)
    bss.proposal.beamline_name.put(beamline)
    bss.esaf.sector.put(str(sector))
    bss.status_msg.put("Done")


def getCurrentCycle():
    """Return the name of the current APS run cycle."""
    return api_bss.getCurrentRun()["name"]


def getCurrentEsafs(sector):
    """
    Return list of ESAFs for the current year.

    PARAMETERS

    sector
        *str* or *int* :
        Name of sector.  If ``str``, must be in
        ``%02d`` format (``02``, not ``2``).
    """
    return listESAFs(getCurrentCycle(), sector)


def getCurrentInfo(beamline):
    """
    From current year ESAFS, return list of ESAFs & proposals with same people.

    PARAMETERS

    beamline
        *str* :
        Name of beam line (as defined by the BSS).
    """
    sector = beamline.split("-")[0]
    tNow = datetime.datetime.now()

    matches = []
    for esaf in api_esaf.listEsafs(sector=sector, year=tNow.year):
        logger.debug("ESAF %s: %s", esaf["esafId"], esaf["esafTitle"])
        esaf_badges = [user["badge"] for user in esaf["experimentUsers"]]
        for run in listRecentRuns():
            for proposal in api_bss.listProposals(
                beamlineName=beamline, runName=run
            ):
                logger.debug(
                    "proposal %s: %s", proposal["id"], proposal["title"]
                )
                count = 0
                for user in proposal["experimenters"]:
                    if user["badge"] in esaf_badges:
                        count += 1
                if count > 0:
                    matches.append(
                        dict(
                            esaf=esaf,
                            proposal=proposal,
                            num_true=count,
                            num_esaf_badges=len(esaf_badges),
                            num_proposal_badges=len(
                                proposal["experimenters"]
                            ),
                        )
                    )
    return matches


def getCurrentProposals(beamline):
    """
    Return a list of proposal ID numbers that are current.

    PARAMETERS

    beamline
        *str* :
        Name of beam line (as defined by the BSS).
    """
    return listProposals(getCurrentCycle(), beamline)


def getEsaf(esafId):
    """
    Return ESAF as a dictionary.

    PARAMETERS

    esafId
        *int* :
        ESAF number
    """
    try:
        record = api_esaf.getEsaf(int(esafId))
    except dm.ObjectNotFound:
        raise EsafNotFound(esafId)
    return dict(record.data)


def getProposal(proposalId, cycle, beamline):
    """
    Return proposal as a dictionary.

    PARAMETERS

    proposalId
        *str* :
        Proposal identification number
    cycle
        *str* :
        Name of APS run cycle (as defined by the BSS)
    beamline
        *str* :
        Name of beam line (as defined by the BSS)
    """
    # avoid possible dm.DmException
    if cycle not in listAllRuns():
        raise DmRecordNotFound(f"cycle '{cycle}' not found")

    if beamline not in listAllBeamlines():
        raise DmRecordNotFound(f"beamline '{beamline}' not found")

    try:
        record = api_bss.getProposal(str(proposalId), cycle, beamline)
    except dm.ObjectNotFound:
        # fmt: off
        raise ProposalNotFound(
            f"id={proposalId}"
            f" cycle={cycle}"
            f" beamline={beamline}"
        )
        # fmt: on
    return dict(record.data)


def listESAFs(cycles, sector):
    """
    Return list of ESAFs for the given cycles & sector.

    PARAMETERS

    sector
        *str* or *int* :
        Name of sector.  If ``str``, must be in ``%02d``
        format (``02``, not ``2``).
    cycles
        *[str]* :
        List of APS run cycles (as defined by the BSS)
    """
    if not isinstance(cycles, (list, tuple)):
        cycles = (cycles,)
    if isinstance(sector, int):
        sector = f"{sector:02d}"
    if len(sector) == 1:
        sector = "0" + sector

    runs = {r["name"]: r for r in api_bss.listRuns()}

    results = []

    for cycle in cycles:
        if cycle not in listAllRuns():
            raise KeyError(f"APS cycle '{cycle}' not found.")
        year = int(cycle.split("-")[0])
        run = runs[cycle]
        esafs = api_esaf.listEsafs(sector=sector, year=year)
        for esaf in esafs:
            esaf_starts = str(iso2datetime(esaf["experimentStartDate"]))
            if run["startTime"] <= esaf_starts <= run["endTime"]:
                results.append(esaf)

    return results


def listProposals(cycles, beamline):
    """
    Return list of proposals for the given cycles & beamline.

    PARAMETERS

    beamline
        *str* :
        Name of beam line (as defined by the BSS)
    cycles
        *[str]* :
        List of APS run cycles (as defined by the BSS)
    """
    if not isinstance(cycles, (list, tuple)):
        cycles = (cycles,)

    proposals = []
    for cycle in cycles:
        for prop in api_bss.listProposals(
            beamlineName=beamline, runName=cycle
        ):
            prop = dict(prop)
            prop["cycle"] = cycle
            proposals.append(prop)
    return proposals


def iso2datetime(isodate):
    """
    Convert a text ISO8601 date into a ``datetime`` object.

    PARAMETERS

    isodate
        *str* :
        Date and time in modified ISO8601 format. (e.g.: ``2020-07-01 12:34:56.789012``)
        Fractional seconds are optional.
    """
    return datetime.datetime.fromisoformat(isodate)


def listAllBeamlines():
    """Return list (from ``dm``) of known beam line names."""
    if "beamlines" not in _cache_:
        _cache_["beamlines"] = [
            entry["name"] for entry in api_bss.listBeamlines()
        ]
    return _cache_["beamlines"]


def listAllRuns():
    """Return a list of all known cycles.  Cache for repeated use."""
    if "cycles" not in _cache_:
        _cache_["cycles"] = sorted(
            [entry["name"] for entry in api_bss.listRuns()]
        )
    return _cache_["cycles"]


def listRecentRuns(quantity=6):
    """
    Return a list of the 6 most recent runs (2-year period).

    PARAMETERS

    quantity
        *int* :
        number of APS run cycles to include, optional (default: 6)
    """
    # 6 runs is the duration of a user proposal
    # fmt: off
    tNow = datetime.datetime.now()
    runs = [
        run["name"]
        for run in api_bss.listRuns()
        if (
            datetime.datetime.timestamp(iso2datetime(run["startTime"]))
            <=
            datetime.datetime.timestamp(tNow)
        )
    ]
    # fmt: on
    return sorted(runs, reverse=True)[:quantity]


def printColumns(items, numColumns=5, width=10):
    """
    Print a list of ``items`` in column order.

    PARAMETERS

    items
        *[str]* :
        List of items to report
    numColumns
        *int* :
        number of columns, optional (default: 5)
    width
        *int* :
        width of each column, optional (default: 10)
    """
    n = len(items)
    rows = n // numColumns
    if n % numColumns > 0:
        rows += 1
    for base in range(0, rows):
        row = [
            items[base + k * rows]
            for k in range(numColumns)
            if base + k * rows < n
        ]
        print("".join([f"{s:{width}s}" for s in row]))


def printEsafTable(records, title=""):
    """
    Print the list of ESAFs as a table.

    PARAMETERS

    records
        *[obj]* :
        List of ESAF dictionaries.
    title
        *str* :
        Text to print before the table.
    """

    def esaf_sorter(prop):
        return prop["experimentStartDate"]

    table = pyRestTable.Table()
    table.labels = "id status start end user(s) title".split()
    for item in sorted(records, key=esaf_sorter, reverse=True):
        users = trim(
            ",".join(
                [user["lastName"] for user in item["experimentUsers"]]
            ),
            20,
        )
        table.addRow(
            (
                item["esafId"],
                item["esafStatus"],
                item["experimentStartDate"].split()[0],
                item["experimentEndDate"].split()[0],
                users,
                trim(item["esafTitle"], 40),
            )
        )
    print(f"{title}\n\n{table}")


def printProposalTable(records, title=""):
    """
    Print the list of proposals as a table.

    PARAMETERS

    records
        *[obj]* :
        List of proposal dictionaries.
    title
        *str* :
        Text to print before the table.
    """

    def prop_sorter(prop):
        return prop["startTime"]

    table = pyRestTable.Table()
    table.labels = "id cycle start end user(s) title".split()
    for item in sorted(records, key=prop_sorter, reverse=True):
        users = trim(
            ",".join([user["lastName"] for user in item["experimenters"]]),
            20,
        )
        # logger.debug("%s %s %s", item["startTime"], tNow, item["endTime"])
        table.addRow(
            (
                item["id"],
                item["cycle"],
                item["startTime"],
                item["endTime"],
                users,
                trim(item["title"]),
            )
        )
    print(f"{title}\n\n{table}")


def trim(text, length=40):
    """
    Return a string that is no longer than ``length``.

    If a string is longer than ``length``, it is shortened
    to the ``length-3`` characters, then, ``...`` is appended.
    For very short length, the string is shortened to ``length``
    (and no ``...`` is appended).

    PARAMETERS

    text
        *str* :
        String, potentially longer than ``length``
    length
        *int* :
        maximum length, optional (default: 40)
    """
    if length < 1:
        raise ValueError(f"length must be positive, received {length}")
    if length < 5:
        text = text[:length]
    elif len(text) > length:
        text = text[: length - 3] + "..."
    return text


def get_options():
    """Handle command line arguments."""
    global parser
    import argparse
    from apstools._version import get_versions

    version = get_versions()["version"]

    parser = argparse.ArgumentParser(
        prog=os.path.split(sys.argv[0])[-1],
        description=__doc__.strip().splitlines()[0],
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="print version number and exit",
        version=version,
    )

    subcommand = parser.add_subparsers(
        dest="subcommand", title="subcommand"
    )

    subcommand.add_parser("beamlines", help="print list of beamlines")

    msg = (
        "print current ESAF(s) and proposal(s)"
        ",  DEPRECATED: use 'list' instead"
    )
    p_sub = subcommand.add_parser("current", help=msg)
    p_sub.add_argument("beamlineName", type=str, help="Beamline name")

    p_sub = subcommand.add_parser(
        "cycles", help="print APS run cycle names"
    )
    p_sub.add_argument(
        "-f",
        "--full",
        action="store_true",
        default=False,
        help="full report including dates (default is compact)",
    )
    p_sub.add_argument(
        "-a",
        "--ascending",
        action="store_false",
        default=True,
        help="full report by ascending names (default is descending)",
    )

    p_sub = subcommand.add_parser("esaf", help="print specific ESAF")
    p_sub.add_argument("esafId", type=int, help="ESAF ID number")

    p_sub = subcommand.add_parser("list", help="list by cycle")
    msg = (
        "APS run (cycle) name."
        "  One of the names returned by ``apsbss cycles``"
        " or one of these (``past``,  ``prior``, ``previous``)"
        " for the previous cycle, (``current`` or ``now``)"
        " for the current cycle, (``future`` or ``next``)"
        " for the next cycle or ``recent`` for the past two years."
    )
    p_sub.add_argument(
        "-c",
        "--cycle",
        type=str,
        default="now",
        # TODO: nargs="?",
        help=msg,
    )
    p_sub.add_argument("beamlineName", type=str, help="Beamline name")

    p_sub = subcommand.add_parser(
        "proposal", help="print specific proposal"
    )
    p_sub.add_argument("proposalId", type=str, help="proposal ID number")
    p_sub.add_argument("cycle", type=str, help="APS run (cycle) name")
    p_sub.add_argument("beamlineName", type=str, help="Beamline name")

    p_sub = subcommand.add_parser("clear", help="EPICS PVs: clear")
    p_sub.add_argument("prefix", type=str, help="EPICS PV prefix")

    p_sub = subcommand.add_parser("setup", help="EPICS PVs: setup")
    p_sub.add_argument("prefix", type=str, help="EPICS PV prefix")
    p_sub.add_argument("beamlineName", type=str, help="Beamline name")
    p_sub.add_argument("cycle", type=str, help="APS run (cycle) name")

    p_sub = subcommand.add_parser(
        "update", help="EPICS PVs: update from BSS"
    )
    p_sub.add_argument("prefix", type=str, help="EPICS PV prefix")

    p_sub = subcommand.add_parser(
        "report", help="EPICS PVs: report what is in the PVs"
    )
    p_sub.add_argument("prefix", type=str, help="EPICS PV prefix")

    return parser.parse_args()


def cmd_cycles(args):
    """
    Handle ``cycles`` command.

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``
    """
    if args.full:
        table = pyRestTable.Table()
        table.labels = "cycle start end".split()

        def sorter(entry):
            return entry["startTime"]

        for entry in sorted(
            api_bss.listRuns(), key=sorter, reverse=args.ascending
        ):
            table.addRow(
                (entry["name"], entry["startTime"], entry["endTime"],)
            )
        print(str(table))
    else:
        printColumns(listAllRuns())


def cmd_current(args):
    """
    Handle ``current`` command.

    DEPRECATED: use ``list`` instead

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``
    """
    warnings.warn("Command 'current' is deprecated, use 'list' instead.")
    records = getCurrentProposals(args.beamlineName)
    tNow = datetime.datetime.now().isoformat(sep=" ")
    if len(records) == 0:
        print(f"No current proposals for {args.beamlineName}")
    else:
        printProposalTable(
            records, f"Current Proposal(s): {args.beamlineName} at {tNow}"
        )

    sector = args.beamlineName.split("-")[0]
    records = getCurrentEsafs(sector)
    if len(records) == 0:
        print(f"No current ESAFs for sector {sector}")
    else:
        printEsafTable(
            records, f"Current ESAF(s): sector {sector} at {tNow}"
        )


def cmd_esaf(args):
    """
    Handle ``esaf`` command.

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``
    """
    try:
        esaf = getEsaf(args.esafId)
        print(yaml.dump(esaf))
    except DmRecordNotFound as exc:
        print(f"DmRecordNotFound reported: {exc}")
    except dm.DmException as exc:
        print(f"dm reported: {exc}")


def cmd_list(args):
    """
    Handle ``list`` command.

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``

    New in release 1.3.9
    """
    cycle = str(args.cycle).strip().lower()
    sector = int(args.beamlineName.split("-")[0])

    if not len(cycle) or cycle in "now current".split():
        cycle = getCurrentCycle()
    elif cycle == "all":
        cycle = listAllRuns()
    elif cycle in "future next".split():
        runs = listAllRuns()
        item = runs.index(getCurrentCycle()) + 1
        if item >= len(runs):
            print("No future cycle information available at this time.")
            return
        cycle = runs[item]
    elif cycle in "past previous prior".split():
        runs = listAllRuns()
        item = runs.index(getCurrentCycle()) - 1
        if item < 0:
            print("No previous cycle information available.")
            return
        cycle = runs[item]
    elif cycle == "recent":
        cycle = listRecentRuns()

    if not isinstance(cycle, (list, tuple)):
        cycle = [
            cycle,
        ]
    trouble = [c for c in cycle if c not in listAllRuns()]
    if trouble:
        raise KeyError(
            f"Could not find APS run cycle(s): {', '.join(trouble)}"
        )

    logger.debug("cycle(s): %s", cycle)

    printProposalTable(
        listProposals(cycle, args.beamlineName),
        "Proposal(s): "
        f" beam line {args.beamlineName}"
        f",  cycle(s) {args.cycle}",
    )
    printEsafTable(
        listESAFs(cycle, sector),
        f"ESAF(s):  sector {sector},  cycle(s) {args.cycle}",
    )


def cmd_proposal(args):
    """
    Handle ``proposal`` command.

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``
    """
    try:
        proposal = getProposal(
            args.proposalId, args.cycle, args.beamlineName
        )
        print(yaml.dump(proposal))
    except DmRecordNotFound as exc:
        print(exc)
    except dm.DmException as exc:
        print(f"dm reported: {exc}")


def cmd_report(args):
    """
    Handle ``report`` command.

    PARAMETERS

    args
        *obj* :
        Object returned by ``argparse``
    """
    from ..utils import object_explorer

    bss = connect_epics(args.prefix)
    object_explorer(bss)


def main():
    """Command-line interface for ``apsbss`` program."""
    args = get_options()
    if args.subcommand == "beamlines":
        printColumns(listAllBeamlines(), numColumns=4, width=15)

    elif args.subcommand == "clear":
        epicsClear(args.prefix)

    elif args.subcommand == "current":
        cmd_current(args)

    elif args.subcommand == "cycles":
        cmd_cycles(args)

    elif args.subcommand == "esaf":
        cmd_esaf(args)

    elif args.subcommand == "list":
        cmd_list(args)

    elif args.subcommand == "proposal":
        cmd_proposal(args)

    elif args.subcommand == "setup":
        epicsSetup(args.prefix, args.beamlineName, args.cycle)

    elif args.subcommand == "update":
        epicsUpdate(args.prefix)

    elif args.subcommand == "report":
        cmd_report(args)

    else:
        parser.print_usage()


if __name__ == "__main__":
    main()

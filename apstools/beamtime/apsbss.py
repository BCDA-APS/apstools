#!/usr/bin/env python

"""
Retrieve specific records from the APS Proposal and ESAF databases

BSS: Beamline Scheduling System

EXAMPLES::

    apsbss current
    apsbss esaf 226319
    apsbss proposal 66083 2020-2 9-ID-B,C
"""

import argparse
import datetime
import dm               # APS data management library
import os
import pyRestTable
import sys
import time
import yaml

from .apsbss_ophyd import EpicsBssDevice


DM_APS_DB_WEB_SERVICE_URL = "https://xraydtn01.xray.aps.anl.gov:11236"
CONNECT_TIMEOUT = 5
POLL_INTERVAL = 0.01

api_bss = dm.BssApsDbApi(DM_APS_DB_WEB_SERVICE_URL)
api_esaf = dm.EsafApsDbApi(DM_APS_DB_WEB_SERVICE_URL)

_cache_ = {}


class EpicsNotConnected(Exception): ...


def connect_epics(prefix):
    t0 = time.time()
    t_timeout = t0 + CONNECT_TIMEOUT
    bss = EpicsBssDevice(prefix, name="bss")
    while not bss.connected and time.time() < t_timeout:
        time.sleep(POLL_INTERVAL)
    # printColumns(bss.read_attrs, width=40, numColumns=2)
    if not bss.connected:
        raise EpicsNotConnected(
            f"Did not connect with EPICS {prefix} in {CONNECT_TIMEOUT}s")
    t_connect = time.time() - t0
    print(f"connected in {t_connect:.03f}s")
    return bss


def epicsClear(prefix):
    """
    clear the EPICS database
    """
    print(f"clear EPICS {prefix}")
    bss = connect_epics(prefix)

    t0 = time.time()
    bss.clear()
    t_clear = time.time() - t0
    print(f"cleared in {t_clear:.03f}s")


def epicsUpdate(prefix):
    """
    update an EPICS database with current ESAF & proposal information
    """
    print(f"update EPICS {prefix}")
    bss = connect_epics(prefix)

    bss.clear()
    cycle = bss.esaf.aps_cycle.get()
    beamline = bss.proposal.beamline_name.get()
    # sector = bss.esaf.sector.get()
    esaf_id = bss.esaf.esaf_id.get()
    proposal_id = bss.proposal.proposal_id.get()

    if len(beamline) == 0:
        raise ValueError(
            f"must set beamline name in {bss.proposal.beamline_name.pvname}")
    elif beamline not in listAllBeamlines():
        raise ValueError(f"{beamline} is not known")
    if len(cycle) == 0:
        raise ValueError(
            f"must set APS cycle name in {bss.esaf.aps_cycle.pvname}")
    elif cycle not in listAllRuns():
        raise ValueError(f"{cycle} is not known")

    bss.clear()

    if len(esaf_id) > 0:
        esaf = getEsaf(esaf_id)
        bss.esaf.description.put(esaf["description"])
        bss.esaf.title.put(esaf["esafTitle"])
        bss.esaf.esaf_status.put(esaf["esafStatus"])
        bss.esaf.end_date.put(esaf["experimentEndDate"])
        bss.esaf.start_date.put(esaf["experimentStartDate"])

        bss.esaf.user_last_names.put(
            ",".join([user["lastName"] for user in esaf["experimentUsers"]])
        )
        bss.esaf.user_badges.put(
            ",".join([user["badge"] for user in esaf["experimentUsers"]])
        )
        for i, user in enumerate(esaf["experimentUsers"]):
            obj = getattr(bss.esaf, f"user{i+1}")
            obj.badge_number.put(user["badge"])
            obj.email.put(user["email"])
            obj.first_name.put(user["firstName"])
            obj.last_name.put(user["lastName"])
            if i == 9:
                break

    if len(proposal_id) > 0:
        proposal = getProposal(proposal_id, cycle, beamline)
        bss.proposal.mail_in_flag.put(proposal["mailInFlag"] in ("Y", "y"))
        bss.proposal.proprietary_flag.put(proposal["proprietaryFlag"] in ("Y", "y"))
        bss.proposal.submitted_date.put(proposal["submittedDate"])
        bss.proposal.title.put(proposal["title"])

        bss.proposal.user_last_names.put(
            ",".join([user["lastName"] for user in proposal["experimenters"]])
        )
        bss.proposal.user_badges.put(
            ",".join([user["badge"] for user in proposal["experimenters"]])
        )
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
            if i == 9:
                break


def epicsSetup(prefix, beamline, cycle=None):
    if beamline not in listAllBeamlines():
        raise ValueError(f"{beamline} is not known")
    if cycle not in listAllRuns():
        raise ValueError(f"{cycle} is not known")

    bss = connect_epics(prefix)

    cycle = cycle or getCurrentCycle()
    sector = int(beamline.split("-")[0])
    print(f"setup EPICS {prefix} {beamline} cycle={cycle} sector={sector}")

    bss.clear()
    bss.esaf.aps_cycle.put(cycle)
    bss.proposal.beamline_name.put(beamline)
    bss.esaf.sector.put(str(sector))


def getCurrentCycle():
    return api_bss.getCurrentRun()["name"]


def getCurrentEsafs(sector):
    if isinstance(sector, int):
        sector = f"{sector:02d}"
    if len(sector) == 1:
        sector = "0" + sector
    tNow = datetime.datetime.now()
    esafs = api_esaf.listEsafs(sector=sector, year=tNow.year)
    results = []
    for esaf in esafs:
        if tNow < iso2datetime(esaf["experimentStartDate"]):
            continue
        if tNow > iso2datetime(esaf["experimentEndDate"]):
            continue
        results.append(esaf)
    return results


def getCurrentInfo(beamline):
    sector = beamline.split("-")[0]
    tNow = datetime.datetime.now()

    matches = []
    for esaf in api_esaf.listEsafs(sector=sector, year=tNow.year):
        print(f"ESAF {esaf['esafId']}: {esaf['esafTitle']}")
        esaf_badges = [user["badge"] for user in esaf["experimentUsers"]]
        for run in listRecentRuns():
            for proposal in api_bss.listProposals(beamlineName=beamline,
                                                  runName=run):
                print(f"proposal {proposal['id']}: {proposal['title']}")
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
                            num_proposal_badges=len(proposal["experimenters"]),
                        )
                    )
    return matches


def getCurrentProposals(beamline):
    proposals = []
    for cycle in listRecentRuns():
        for prop in api_bss.listProposals(beamlineName=beamline, runName=cycle):
            prop = dict(prop)
            prop["cycle"] = cycle
            proposals.append(prop)
    return proposals


def getEsaf(esafId):
    try:
        record = api_esaf.getEsaf(int(esafId))
    except dm.ObjectNotFound:
        raise EsafNotFound(esafId)
    return dict(record.data)


def getProposal(proposalId, runName, beamlineName):
    # avoid possible dm.DmException
    if runName not in listAllRuns():
        raise DmRecordNotFound(f"run '{runName}' not found")

    if beamlineName not in listAllBeamlines():
        raise DmRecordNotFound(f"beamline '{beamlineName}' not found")

    try:
        record = api_bss.getProposal(str(proposalId), runName, beamlineName)
    except dm.ObjectNotFound:
        raise ProposalNotFound(
            f"id={proposalId}"
            f" run={runName}"
            f" beamline={beamlineName}"
            )
    return dict(record.data)


def iso2datetime(isodate):
    return datetime.datetime.fromisoformat(isodate)


def listAllBeamlines():
    if "beamlines" not in _cache_:
        _cache_["beamlines"] = [
            entry["name"]
            for entry in api_bss.listBeamlines()
        ]
    return _cache_["beamlines"]


def listAllRuns():
    if "cycles" not in _cache_:
        _cache_["cycles"] = sorted([
            entry["name"]
            for entry in api_bss.listRuns()
        ])
    return _cache_["cycles"]


def listRecentRuns(quantity=6):
    # 6 runs is the duration of a user proposal
    tNow = datetime.datetime.now()
    runs = [
        run["name"]
        for run in api_bss.listRuns()
        if iso2datetime(run["startTime"]) <= tNow
    ]
    return sorted(runs, reverse=True)[:quantity]


def printColumns(items, numColumns=5, width=10):
    n = len(items)
    rows = n // numColumns
    if n % numColumns > 0:
        rows += 1
    for base in range(0, rows):
        row = [
            items[base+k*rows]
            for k in range(numColumns)
            if base+k*rows < n]
        print("".join([f"{s:{width}s}" for s in row]))


def trim(text, length=40):
    if len(text) > length:
        text = text[:length-3] + "..."
    return text


class DmRecordNotFound(Exception): ...
class EsafNotFound(DmRecordNotFound): ...
class ProposalNotFound(DmRecordNotFound): ...


def get_options():
    parser = argparse.ArgumentParser(
        prog=os.path.split(sys.argv[0])[-1],
        description=__doc__.strip().splitlines()[0],
        )

    subcommand = parser.add_subparsers(dest='subcommand', title='subcommand')

    subcommand.add_parser('beamlines', help="print list of beamlines")

    p_sub = subcommand.add_parser('current', help="print current ESAF(s) and proposal(s)")
    p_sub.add_argument('beamlineName', type=str, help="Beamline name")

    subcommand.add_parser('cycles', help="print APS cycle names")

    p_sub = subcommand.add_parser('esaf', help="print specific ESAF")
    p_sub.add_argument('esafId', type=int, help="ESAF ID number")

    p_sub = subcommand.add_parser('proposal', help="print specific proposal")
    p_sub.add_argument('proposalId', type=str, help="ESAF ID number")
    p_sub.add_argument('cycle', type=str, help="APS run (cycle) name")
    p_sub.add_argument('beamlineName', type=str, help="Beamline name")

    p_sub = subcommand.add_parser('clear', help="EPICS PVs: clear")
    p_sub.add_argument('prefix', type=str, help="EPICS PV prefix")

    p_sub = subcommand.add_parser('setup', help="EPICS PVs: setup")
    p_sub.add_argument('prefix', type=str, help="EPICS PV prefix")
    p_sub.add_argument('beamlineName', type=str, help="Beamline name")
    p_sub.add_argument('cycle', type=str, help="APS run (cycle) name")

    p_sub = subcommand.add_parser('update', help="EPICS PVs: update from BSS")
    p_sub.add_argument('prefix', type=str, help="EPICS PV prefix")

    return parser.parse_args()


def cmd_current(args):
    records = getCurrentProposals(args.beamlineName)
    if len(records) == 0:
        print(f"No current proposals for {args.beamlineName}")
    else:
        table = pyRestTable.Table()
        table.labels = "id cycle date user(s) title".split()
        for item in records:
            users = trim(",".join([
                user["lastName"]
                for user in item["experimenters"]
            ]), 20)
            table.addRow((
                item["id"],
                item["cycle"],
                item["submittedDate"],
                users,
                trim(item["title"]),))
        print(f"Current Proposal(s) on {args.beamlineName}")
        print()
        print(table)

    sector = args.beamlineName.split("-")[0]
    records = getCurrentEsafs(sector)
    if len(records) == 0:
        print(f"No current ESAFs for sector {sector}")
    else:
        table = pyRestTable.Table()
        table.labels = "id status start end user(s) title".split()
        for item in records:
            users = trim(
                    ",".join([
                    user["lastName"]
                    for user in item["experimentUsers"]
                ]),
                20)
            table.addRow((
                item["esafId"],
                item["esafStatus"],
                item["experimentStartDate"].split()[0],
                item["experimentEndDate"].split()[0],
                users,
                trim(item["esafTitle"], 40),
                ))
        print(f"Current ESAF(s) on sector {sector}")
        print()
        print(table)


def cmd_esaf(args):
    try:
        esaf = getEsaf(args.esafId)
        print(yaml.dump(esaf))
    except DmRecordNotFound as exc:
        print(exc)
    except dm.DmException as exc:
        print(f"dm reported: {exc}")


def cmd_proposal(args):
    try:
        proposal = getProposal(args.proposalId, args.cycle, args.beamlineName)
        print(yaml.dump(proposal))
    except DmRecordNotFound as exc:
        print(exc)
    except dm.DmException as exc:
        print(f"dm reported: {exc}")


def main():
    args = get_options()
    if args.subcommand == "beamlines":
        printColumns(listAllBeamlines(), numColumns=4, width=15)

    elif args.subcommand == "clear":
        epicsClear(args.prefix)

    elif args.subcommand == "current":
        cmd_current(args)

    elif args.subcommand == "cycles":
        printColumns(listAllRuns())

    elif args.subcommand == "esaf":
        cmd_esaf(args)

    elif args.subcommand == "proposal":
        cmd_proposal(args)

    elif args.subcommand == "setup":
        epicsSetup(args.prefix, args.beamlineName, args.cycle)

    elif args.subcommand == "update":
        epicsUpdate(args.prefix)


if __name__ == "__main__":
    main()

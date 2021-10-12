"""
General tests of the apsbss module
"""

import datetime
import epics
import os
import pytest
import socket
import subprocess
import sys
import time
import uuid

from ophyd.signal import EpicsSignalBase

from .. import apsbss, apsbss_makedb


BSS_TEST_IOC_PREFIX = f"tst{uuid.uuid4().hex[:7]}:bss:"

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tests")
)

# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True, timeout=60, write_timeout=60, connection_timeout=60,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


@pytest.fixture(scope="function")
def argv():
    argv = [
        "apsbss",
    ]
    return argv


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


@pytest.fixture(scope="function")
def bss_PV():
    # try connecting with one of the PVs in the database
    cycle = epics.PV(f"{BSS_TEST_IOC_PREFIX}esaf:cycle")
    cycle.wait_for_connection(timeout=2)
    return cycle


def test_general():
    assert apsbss.CONNECT_TIMEOUT == 5
    assert apsbss.POLL_INTERVAL == 0.01
    url = "https://xraydtn01.xray.aps.anl.gov:11236"
    assert apsbss.DM_APS_DB_WEB_SERVICE_URL == url
    assert apsbss.api_bss is not None
    assert apsbss.api_esaf is not None


def test_iso2datetime():
    dt = datetime.datetime(2020, 6, 30, 12, 31, 45, 67890)
    assert apsbss.iso2datetime("2020-06-30 12:31:45.067890") == dt


def test_not_at_aps():
    assert True  # test *something*
    if using_APS_workstation():
        return


# do not try to test for fails using dm package, it has no timeout


def test_only_at_aps():
    assert True  # test *something*
    if not using_APS_workstation():
        return

    runs = apsbss.listAllRuns()
    assert len(runs) > 1
    assert apsbss.getCurrentCycle() in runs
    assert apsbss.listRecentRuns()[0] in runs
    assert len(apsbss.listAllBeamlines()) > 1

    # TODO: test the other functions
    # getCurrentEsafs
    # getCurrentInfo
    # getCurrentProposals
    # getEsaf
    # getProposal
    # class DmRecordNotFound(Exception): ...
    # class EsafNotFound(DmRecordNotFound): ...
    # class ProposalNotFound(DmRecordNotFound): ...


def test_printColumns(capsys):
    apsbss.printColumns("1 2 3 4 5 6".split(), numColumns=3, width=3)
    captured = capsys.readouterr()
    received = captured.out.strip().split("\n")
    assert len(received) == 2
    assert received[0].strip() == "1  3  5"
    assert received[1].strip() == "2  4  6"


def test_trim():
    source = "0123456789"
    assert apsbss.trim(source) == source
    got = apsbss.trim(source, length=8)
    assert got != source
    assert got.endswith("...")
    assert len(got) == 8
    assert got == "01234..."


class IOC_ProcessConfig:
    bss = None
    manager = None
    ioc_name = "test_apsbss"
    ioc_prefix = None
    ioc_process = None

    def command(self, cmd):
        return f"{self.manager} {cmd} {self.ioc_name} {self.ioc_prefix}"


def run_process(cmd):
    return subprocess.Popen(
        cmd.encode().split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )


@pytest.fixture()
def ioc():
    # set up

    cfg = IOC_ProcessConfig()

    cfg.manager = os.path.abspath(
        os.path.join(DATA_PATH, "..", "beamtime", "apsbss_ioc.sh")
    )
    cfg.ioc_prefix = BSS_TEST_IOC_PREFIX
    cfg.ioc_process = run_process(cfg.command("restart"))
    time.sleep(0.5)  # allow the IOC to start

    # use
    yield cfg

    # tear down
    if cfg.bss is not None:
        cfg.bss.destroy()
        cfg.bss = None
    if cfg.ioc_process is not None:
        cfg.ioc_process = None
        run_process(cfg.command("stop"))
        cfg.manager = None


def test_ioc(ioc, bss_PV):
    if not bss_PV.connected:
        assert True  # assert *something*
        return

    from .. import apsbss_ophyd as bio

    ioc.bss = bio.EpicsBssDevice(BSS_TEST_IOC_PREFIX, name="bss")
    ioc.bss.wait_for_connection(timeout=2)
    assert ioc.bss.connected
    assert ioc.bss.esaf.title.get() == ""
    assert ioc.bss.esaf.description.get() == ""
    # assert ioc.bss.esaf.aps_cycle.get() == ""


def test_EPICS(ioc, bss_PV):
    if not bss_PV.connected:
        assert True  # assert *something*
        return

    beamline = "9-ID-B,C"
    cycle = "2019-3"

    ioc.bss = apsbss.connect_epics(BSS_TEST_IOC_PREFIX)
    assert ioc.bss.connected
    assert ioc.bss.esaf.aps_cycle.get() == ""

    assert ioc.bss.esaf.aps_cycle.connected is True

    if not using_APS_workstation():
        return

    # setup
    apsbss.epicsSetup(BSS_TEST_IOC_PREFIX, beamline, cycle)

    assert ioc.bss.proposal.beamline_name.get() != "harpo"
    assert ioc.bss.proposal.beamline_name.get() == beamline
    assert ioc.bss.esaf.aps_cycle.get() == cycle
    assert ioc.bss.esaf.sector.get() == beamline.split("-")[0]

    # epicsUpdate
    # Example ESAF on sector 9

    # ====== ======== ========== ========== ==================== =================================
    # id     status   start      end        user(s)              title
    # ====== ======== ========== ========== ==================== =================================
    # 226319 Approved 2020-05-26 2020-09-28 Ilavsky,Maxey,Kuz... Commission 9ID and USAXS
    # ====== ======== ========== ========== ==================== =================================

    # ===== ====== =================== ==================== ========================================
    # id    cycle  date                user(s)              title
    # ===== ====== =================== ==================== ========================================
    # 64629 2019-2 2019-03-01 18:35:02 Ilavsky,Okasinski    2019 National School on Neutron & X-r...
    # ===== ====== =================== ==================== ========================================
    esaf_id = "226319"
    proposal_id = "64629"
    ioc.bss.esaf.aps_cycle.put("2019-2")
    ioc.bss.esaf.esaf_id.put(esaf_id)
    ioc.bss.proposal.proposal_id.put(proposal_id)
    apsbss.epicsUpdate(BSS_TEST_IOC_PREFIX)
    assert ioc.bss.esaf.title.get() == "Commission 9ID and USAXS"
    assert ioc.bss.proposal.title.get().startswith(
        "2019 National School on Neutron & X-r"
    )

    apsbss.epicsClear(BSS_TEST_IOC_PREFIX)
    assert ioc.bss.esaf.aps_cycle.get() != ""
    assert ioc.bss.esaf.title.get() == ""
    assert ioc.bss.proposal.title.get() == ""


def test_makedb(capsys):
    apsbss_makedb.main()
    db = capsys.readouterr().out.strip().split("\n")
    assert len(db) == 384
    random_spot_checks = {
        0: "#",
        1: "# file: apsbss.db",
        13: 'record(stringout, "$(P)status")',
        28: 'record(stringout, "$(P)esaf:id")',
        138: '    field(ONAM, "ON")',
        285: 'record(bo, "$(P)proposal:user5:piFlag") {',
    }
    for line_number, content in random_spot_checks.items():
        assert db[line_number] == content


def test_argv0(argv):
    sys.argv = argv
    assert len(sys.argv) == 1


def test_apsbss_commands_no_options(argv):
    sys.argv = argv
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand is None


def test_apsbss_commands_beamlines(argv):
    sys.argv = argv + [
        "beamlines",
    ]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]


def test_apsbss_commands_current(argv):
    sys.argv = argv + ["current", "9-ID-B,C"]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.beamlineName == sys.argv[2]


def test_apsbss_commands_cycles(argv):
    sys.argv = argv + [
        "cycles",
    ]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]


def test_apsbss_commands_esaf(argv):
    sys.argv = argv + [
        "esaf",
        "12345",
    ]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.esafId == 12345


def test_apsbss_commands_proposal(argv):
    sys.argv = argv + ["proposal", "proposal_number_here", "1995-1", "my_beamline"]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.proposalId == sys.argv[2]
    assert args.cycle == sys.argv[3]
    assert args.beamlineName == sys.argv[4]


def test_apsbss_commands_EPICS_clear(argv):
    sys.argv = argv + ["clear", "bss:"]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.prefix == sys.argv[2]


def test_apsbss_commands_EPICS_setup(argv):
    sys.argv = argv + ["setup", "bss:", "my_beamline", "1995-1"]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.prefix == sys.argv[2]
    assert args.beamlineName == sys.argv[3]
    assert args.cycle == sys.argv[4]


def test_apsbss_commands_EPICS_update(argv):
    sys.argv = argv + ["update", "bss:"]
    args = apsbss.get_options()
    assert args is not None
    assert args.subcommand == sys.argv[1]
    assert args.prefix == sys.argv[2]

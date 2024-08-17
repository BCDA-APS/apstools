"""
simple unit tests for this package.
"""

import time
import uuid

import databroker
import numpy as np
import ophyd.sim
import pytest

from ... import __version__ as APS__version__
from ... import utils
from .._core import MAX_EPICS_STRINGOUT_LENGTH
from .._core import TableStyle
from ..misc import call_signature_decorator
from ..misc import render

CATALOG = "usaxs_test"
COUNT = "555a604"  # <-- uid,  scan_id: 2
RE = None
DEFAULT_CATALOG_ID = uuid.uuid4()  # a unique ID for testing purposes


@pytest.fixture(scope="function")
def cat():
    cat = databroker.catalog[CATALOG]
    return cat


def test_utils_cleanupText():
    original = "1. Some text to cleanup #25"
    received = utils.cleanupText(original)
    expected = "1__Some_text_to_cleanup__25"
    assert received == expected


def test_utils_dictionary_table():
    md = {
        "login_id": "jemian:wow.aps.anl.gov",
        "beamline_id": "developer",
        "proposal_id": None,
        "pid": 19072,
        "scan_id": 10,
        "version": {
            "bluesky": "1.5.2",
            "ophyd": "1.3.3",
            "apstools": "1.1.5",
            "epics": "3.3.3",
        },
    }
    table = utils.dictionary_table(md)
    received = str(table).strip()
    expected = (
        "=========== =============================================================================\n"
        "key         value                                                                        \n"
        "=========== =============================================================================\n"
        "beamline_id developer                                                                    \n"
        "login_id    jemian:wow.aps.anl.gov                                                       \n"
        "pid         19072                                                                        \n"
        "proposal_id None                                                                         \n"
        "scan_id     10                                                                           \n"
        "version     {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}\n"
        "=========== ============================================================================="
    )
    assert received == expected


def test_utils_itemizer():
    items = [1.0, 1.1, 1.01, 1.001, 1.0001, 1.00001]
    received = utils.itemizer("%.2f", items)
    expected = ["1.00", "1.10", "1.01", "1.00", "1.00", "1.00"]
    assert received == expected


def test_utils_print_RE_md(capsys):
    global RE
    md = {}
    md["purpose"] = "testing"
    md["versions"] = dict(apstools=APS__version__)
    md["something"] = "else"

    utils.print_RE_md(md)
    out, err = capsys.readouterr()
    received = out.splitlines()

    expected = [
        "RunEngine metadata dictionary:",
        "========= ===============================",
        "key       value                          ",
        "========= ===============================",
        "purpose   testing                        ",
        "something else                           ",
        "versions  ======== ======================",
        "          key      value                 ",
        "          ======== ======================",
        f"          apstools {APS__version__}",
        "          ======== ======================",
        "========= ===============================",
        "",
    ]
    assert len(received) == len(expected)
    assert received[4].strip() == expected[4].strip()
    assert received[5].strip() == expected[5].strip()
    assert received[9].strip() == expected[9].strip()


def test_utils_pairwise():
    items = [1.0, 1.1, 1.01, 1.001, 1.0001, 1.00001, 2]
    received = list(utils.pairwise(items))
    expected = [(1.0, 1.1), (1.01, 1.001), (1.0001, 1.00001)]
    assert received == expected


@pytest.mark.parametrize(
    "value, sig_figs, expected",
    [
        [0.369340000000000063, 14, "0.36934"],
        [0.369340000000000063, 3, "0.3693"],
        [-3.1300000000000003, 14, "-3.13"],
        [-0, 14, "0"],
        [0, 14, "0"],
        [0.0, 14, "0"],
        [123_456, 14, "123456"],
        [123_456, 3, "123456"],
        [123_456.0, 14, "123456.0"],
        [123_456.0, 3, "123500.0"],
    ]
)
def test_utils_render(value, sig_figs: int, expected: str):
    result = render(value, sig_figs)
    assert str(result) == expected, f"{result=!r}  {expected=!r}"


@pytest.mark.parametrize(
    "given, expected",
    [
        ["simple", "simple"],
        ["sim_ple", "sim_ple"],
        ["hy-phen", "hy_phen"],
        ["white space", "white_space"],
        ["1world", "_1world"],
        ["end9", "end9"],
        ["$tree", "_tree"],
        ["#!bang", "__bang"],
        ["0 is not a good name", "_0_is_not_a_good_name"],
        ["! is even worse!", "__is_even_worse_"],
        ["double.dotted.name", "double_dotted_name"],
    ],
)
def test_utils_safe_ophyd_name(given, expected):
    received = utils.safe_ophyd_name(given)
    assert received == expected


def test_utils_split_quoted_line():
    source = 'FlyScan 5   2   0   "empty container"'
    received = utils.split_quoted_line(source)
    assert len(received) == 5
    expected = ["FlyScan", "5", "2", "0", "empty container"]
    assert received == expected


def test_utils_trim_string_for_EPICS():
    source = "0123456789"
    assert len(source) < MAX_EPICS_STRINGOUT_LENGTH
    received = utils.trim_string_for_EPICS(source)
    assert len(source) == len(received)
    expected = source
    assert received == expected

    source = "0123456789" * 10
    assert len(source) > MAX_EPICS_STRINGOUT_LENGTH
    received = utils.trim_string_for_EPICS(source)
    assert len(source) > len(received)
    expected = source[: MAX_EPICS_STRINGOUT_LENGTH - 1]
    assert received == expected


def test_utils_listobjects():
    sims = ophyd.sim.hw().__dict__
    wont_show = (
        "flyer1",
        "flyer2",
        "new_trivial_flyer",
        "trivial_flyer",
    )
    num = len(sims) - len(wont_show)
    kk = sorted(sims.keys())

    table = utils.listobjects(symbols=sims)
    assert 4 == len(table.labels)
    rr = [r[0] for r in table.rows]
    for k in kk:
        if k not in wont_show:
            assert k in rr
    assert num == len(table.rows)


@pytest.mark.parametrize(
    "show_d, show_s, columns",
    [
        [None, None, 4],
        [False, False, 4],
        [True, False, 5],
        [True, True, 6],
        [False, True, 5],
    ],
)
def test_utils_listobjects_children(show_d, show_s, columns):
    from ophyd.ophydobj import OphydObject

    sims = {k: v for k, v in ophyd.sim.hw().__dict__.items() if isinstance(v, OphydObject)}
    table = utils.listobjects(symbols=sims, child_devices=show_d, child_signals=show_s)
    assert columns == len(table.labels)


def test_utils_unix():
    cmd = 'echo "hello"'
    out, err = utils.unix(cmd)
    assert out == b"hello\n"
    assert err == b""

    cmd = "sleep 0.8 | echo hello"
    t0 = time.time()
    out, err = utils.unix(cmd)
    dt = time.time() - t0
    assert dt >= 0.8
    assert out == b"hello\n"
    assert err == b""


def test_utils_with_database_listruns(cat):
    assert len(list(cat.v1[COUNT].documents())[:1]) == 1
    table = utils.listruns(cat=cat, num=10)
    assert isinstance(table, TableStyle.pyRestTable.value)
    assert len(table.labels) == 4

    assert "time" in table.labels
    column = table.labels.index("time")
    assert table.labels[column] == "time"

    ts = [row[column] for row in table.rows]
    assert len(ts) == 10
    assert (ts == np.sort(ts)[::-1]).all()


def test_utils_with_database_replay(cat):
    replies = []

    def cb1(key, doc):
        replies.append((key, len(doc)))

    utils.replay(cat.v1[COUNT], callback=cb1)
    assert len(replies) > 0
    keys = set([v[0] for v in replies])
    # doc_types = "start stop event descriptor datum resource".split()
    doc_types = "start stop event descriptor".split()
    for item in doc_types:
        assert item in keys

    def cb2(key, doc):
        if key == "start":
            replies.append(doc["time"])

    replies = []
    utils.replay(cat.v1[-1], callback=cb2)
    assert len(replies) == 1  # last run

    replies = []
    utils.replay(cat.v1[-3:], callback=cb2)
    assert len(replies) == 3  # last 3 runs

    replies = []
    utils.replay(cat.v1[COUNT], callback=cb2)
    previous = 0
    for i, v in enumerate(replies):
        assert v - previous > 0
        previous = v

    replies = []
    utils.replay(cat.v1[-1], callback=cb2, sort=False)
    previous = replies[0] + 1
    for i, v in enumerate(replies):
        assert v - previous < 0
        previous = v


@pytest.mark.parametrize(
    "run_type, ref, scan_ids",
    [
        ["header", -1, 1],
        ["run", -1, 1],
        ["run", 1, 1],
        ["run", "e5d2cbdc", 1],
        ["run", -2, 110],
        ["run", 110, 110],
        ["run", "19965989-0a2a-44aa-aa06-c1248754e651", 110],
        ["header", [-1, -2], [1, 110]],
        ["run", -3, 109],
        ["run", [1, 110, 109], [1, 110, 109]],
    ],
)
def test_replay(run_type, ref, scan_ids, cat):
    if run_type == "header":
        local_cat = cat.v1
    else:
        local_cat = cat.v2
    if isinstance(ref, (list, tuple)):
        n_items = len(ref)
        local_ref = [local_cat[r] for r in ref]
        if run_type == "header":
            local_scan_ids = [r.start["scan_id"] for r in local_ref]
        else:
            local_scan_ids = [r.metadata["start"]["scan_id"] for r in local_ref]
    else:
        n_items = 1
        local_ref = local_cat[ref]
        if run_type == "header":
            local_scan_ids = local_ref.start["scan_id"]
        else:
            local_scan_ids = local_ref.metadata["start"]["scan_id"]
    assert local_scan_ids == scan_ids

    replies = []

    def cb2(key, doc):
        if key == "start":
            replies.append(doc["time"])

    utils.replay(local_ref, cb2)
    assert len(replies) == n_items


# fmt:off
@pytest.mark.parametrize(
    "scan_id, stream, total_keys, key, v1, m3, m_default, m_strict, m_lower",
    [
        (103, "primary", 7, "PD_USAXS", False, 1, 1, 1, 0),
        (103, None, 7, "PD_USAXS", False, 1, 1, 1, 0),
        (2, "primary", 5, "scaler0", False, 2, 2, 2, 2),
        (2, None, 5, "scaler0", False, 2, 2, 2, 2),
        (103, "primary", 8, "PD_USAXS", True, 1, 1, 1, 0),
    ],
)
def test_utils_listRunKeys(
    scan_id, stream, total_keys, key, v1, m3, m_default, m_strict, m_lower, cat
):
    assert (
        len(utils.listRunKeys(scan_id, db=cat, stream=stream, use_v1=v1)) == total_keys
    )

    result = utils.listRunKeys(
        scan_id, key_fragment=key[0:3], db=cat, stream=stream, use_v1=v1
    )
    assert len(result) == m3

    result = utils.listRunKeys(
        scan_id, key_fragment=key, db=cat, stream=stream, use_v1=v1
    )
    assert len(result) == m_default

    result = utils.listRunKeys(
        scan_id, key_fragment=key, db=cat, stream=stream, strict=True, use_v1=v1
    )
    assert len(result) == m_strict

    result = utils.listRunKeys(
        scan_id, key_fragment=key.lower(), db=cat, stream=stream, strict=True, use_v1=v1
    )
    assert len(result) == m_lower
# fmt: on


# fmt: off
@pytest.mark.parametrize(
    "scan_id, stream",
    [
        (110, None),
        (110, "primary"),
        (103, "mca"),
    ],
)
def test_utils_listRunKeys_no_such_stream(scan_id, stream, cat):
    with pytest.raises(AttributeError) as exc:
        utils.listRunKeys(scan_id, db=cat, stream=stream)
    assert str(exc.value).startswith("No such stream ")
# fmt: on


@pytest.mark.parametrize(
    "scan_id, stream, nkeys, v1",
    [
        (2, None, 5, False),
        (2, "primary", 5, False),
        (2, "primary", 6, True),
        (103, "primary", 7, False),
        # (103, "baseline", 268, False),  # very slow test!
        (103, "baseline", 269, True),  # faster test!
        (103, "baseline", 269, None),  # faster test!
    ],
)
def test_utils_getRunData(scan_id, stream, nkeys, v1, cat):
    table = utils.getRunData(scan_id, db=cat, stream=stream, use_v1=v1)
    assert table is not None
    assert len(table.keys()) == nkeys


# fmt: off
@pytest.mark.parametrize(
    "scan_id, stream, key, idx, v1, expected, prec",
    [
        # (2, "baseline", "undulator_downstream_version", None, False, "4.21", 0),  # VERY slow
        (2, "baseline", "undulator_downstream_version", None, True, "4.21", 0),
        (2, "primary", "I0_USAXS", -1, False, 3729, 0),
        (2, "primary", "I0_USAXS", "-1", False, 3729, 0),
        (2, "primary", "I0_USAXS", "all", False, [3729.0, ], 0),
        (2, "primary", "I0_USAXS", None, False, 3729, 0),
        (2, None, "I0_USAXS", "all", False, [3729.0, ], 0),
        # (103, "baseline", "undulator_downstream_version", None, False, "4.21", 0),  # VERY slow
        (103, "baseline", "undulator_downstream_version", None, True, "4.21", 0),
        (103, "primary", "a_stage_r", -1, False, 8.88197, 5),
        (103, "primary", "a_stage_r", -1, True, 8.88197, 5),
        (103, "primary", "a_stage_r", "mean", False, 8.88397, 5),
        (103, "primary", "a_stage_r", 0, False, 8.88597, 5),
        (103, "primary", "a_stage_r", None, False, 8.88197, 5),
        # (110, "baseline", "terms_SAXS_UsaxsSaxsMode", None, False, "blank", 0),  # VERY slow
        # (110, "baseline", "user_data_sample_thickness", None, False, 0.0, 1),  # VERY slow
        # (110, "baseline", "user_data_scan_macro", None, False, "FlyScan", 0),  # VERY slow
        (110, "baseline", "terms_SAXS_UsaxsSaxsMode", None, True, "blank", 0),
        (110, "baseline", "user_data_sample_thickness", None, True, 0.0, 1),
        (110, "baseline", "user_data_scan_macro", None, True, "FlyScan", 0),
    ],
)
def test_utils_getRunDataValue(scan_id, stream, key, idx, v1, expected, prec, cat):
    value = utils.getRunDataValue(
        scan_id, key, db=cat, stream=stream, idx=idx, use_v1=v1
    )
    if isinstance(value, str):
        assert value == expected
    elif isinstance(value, float):
        assert round(value, prec) == expected
    elif isinstance(value, np.ndarray):
        assert len(value) == len(expected)
        for v, e in zip(value, expected):
            assert round(v, prec) == e
# fmt: on

# # fmt: off
# @pytest.mark.parametrize(
#     "scan_id, stream, key, idx, expected, prec",
#     [
#         (110, "mca", "struck_mca3_elapsed_real_time", None, 93.72, 2),
#     ],
# )
# def test_utils_getRunDataValue_MemoryError(
#     scan_id, stream, key, idx, expected, prec, cat
# ):
#     with pytest.raises(np.core._exceptions._ArrayMemoryError) as exc:
#         utils.getRunDataValue(
#             scan_id, key, db=cat, stream=stream, idx=idx
#         )
#     assert str(exc.value).startswith("Unable to allocate ")
# # fmt: on


# fmt: off
@pytest.mark.parametrize(
    "query, n",
    [
        ({"since": "2019-05-01"}, 8),
        ({"since": "2000-05-01"}, 10),
        ({}, 10),
        (None, 10),
        ({"since": None}, 10),
        ({"until": "2019-05-01"}, 2),
        ({"scan_id": 2}, 2),
        ({"scan_id": 2, "plan_name": "count"}, 1),
        ({"scan_id": 110}, 1),
    ],
)
def test_utils_db_query(
    query, n, cat
):
    sub_cat = utils.db_query(cat, query)
    assert len(sub_cat) == n
# fmt: on


# fmt: off
@pytest.mark.parametrize(
    "scan_id, key, db, stream, query, v1, nrows, ncols",
    [
        (COUNT, None, DEFAULT_CATALOG_ID, None, None, None, 6, 1),
        (COUNT, None, DEFAULT_CATALOG_ID, "baseline", None, None, 269, 2),
        (COUNT, "will not be found", DEFAULT_CATALOG_ID, "baseline", None, None, 1, 2),
        (COUNT, "aps", DEFAULT_CATALOG_ID, None, None, None, 1, 1),
        (COUNT, None, DEFAULT_CATALOG_ID, "primary", None, None, 6, 1),
        (COUNT, "aps", DEFAULT_CATALOG_ID, "primary", None, None, 1, 1),
    ],
)
def test_utils_getStreamValues(scan_id, key, db, stream, cat, query, v1, nrows, ncols):
    """These tests should not raise exceptions."""
    if db == DEFAULT_CATALOG_ID:
        db = cat
    table = utils.getStreamValues(
        scan_id, db=db, key_fragment=key, stream=stream, query=query, use_v1=v1
    )
    assert table is not None
    assert table.shape == (nrows, ncols)
# fmt: on


# fmt: off
@pytest.mark.parametrize(
    "scan_id, key, db, stream, query, v1, error, first_words",
    [
        (COUNT, None, DEFAULT_CATALOG_ID, "will not be found", None, None, AttributeError, "No such stream "),
        (COUNT, None, None, None, None, None, ValueError, "No catalog defined.  Multiple catalog "),
        (COUNT, None, None, "baseline", None, None, ValueError, "No catalog defined.  Multiple catalog "),
        (COUNT, "will not be found", None, "baseline", None, None, ValueError, "No catalog defined.  Multiple catalog "),
        (COUNT, "aps", None, None, None, None, ValueError, "No catalog defined.  Multiple catalog "),
        (COUNT, None, None, "primary", None, None, ValueError, "No catalog defined.  Multiple catalog "),
        (COUNT, "aps", None, "primary", None, None, ValueError, "No catalog defined.  Multiple catalog "),
    ],
)
def test_utils_getStreamValues_Exception(
    scan_id, key, db, stream, cat, query, v1, error, first_words
):
    """Look for known errors from getStreamValues()."""
    if db == DEFAULT_CATALOG_ID:
        db = cat
    with pytest.raises(error) as exc:
        utils.getStreamValues(
            scan_id, db=db, key_fragment=key, stream=stream, query=query, use_v1=v1
        )
    assert str(exc.value).startswith(first_words)
# fmt: on


@pytest.mark.parametrize(
    "p1, p2, expected",
    [
        ["/home/bl13user/images", "/home/bl13user/images", 4],
        ["/home/bl13user/images", "/tmp/home/bl13user/images", 3],
        ["/tmp/home/bl13user/images", "/home/bl13user/images", 3],
        ["/a", "/home/bl13user/images", 1],
        [r"C:\\", "/home/bl13user/images", 0],
    ],
)
def test_count_common_subdirs(p1, p2, expected):
    icommon = utils.count_common_subdirs(p1, p2)
    assert icommon == expected, f"{p1=} {p2=}"


@pytest.mark.parametrize(
    "args, kwargs, expect",
    [
        [[1], {}, (False, False, False, False)],
        [[1], {}, (False, False, False, False)],
        [[1, 2], {}, (True, False, False, False)],
        [[1, 2], {"show_pv": 1}, (True, False, False, True)],
        [[1], {"cname": 1}, (False, True, False, False)],
        [[1], {"dname": 1}, (False, False, True, False)],
        [[1], {"b": 1, "cname": 1}, (True, True, False, False)],
        [[1], {"b": 1, "dname": 1}, (True, False, True, False)],
        [[1], {"show_pv": 1, "cname": False}, (False, True, False, True)],
        [[1], {"show_pv": 1, "cname": True}, (False, True, False, True)],
        [[1], {"show_pv": 1, "dname": False}, (False, False, True, True)],
        [[1], {"show_pv": 1, "dname": True}, (False, False, True, True)],
        [[1], {"show_pv": 1, "dname": False, "cname": False}, (False, True, True, True)],
        [[1], {"show_pv": 1, "dname": True, "cname": True}, (False, True, True, True)],
    ],
)
def test_call_signature_decorator(args, kwargs, expect):
    @call_signature_decorator
    def func1(a, b=1, *, cname=False, dname=True, show_pv=None, _call_args=None):
        return (
            "b" in _call_args,
            "cname" in _call_args,
            "dname" in _call_args,
            "show_pv" in _call_args,
        )

    result = func1(*args, **kwargs)
    assert result == expect, f"{result=}  {expect=}"

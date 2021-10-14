import databroker
import datetime
import pandas as pd
import pytest

from ... import utils as APS_utils


TEST_CATALOG_NAME = "apstools_test"


@pytest.fixture(scope="function")
def cat():
    cat = databroker.catalog[TEST_CATALOG_NAME]
    return cat


@pytest.fixture(scope="function")
def lr():
    lr = APS_utils.ListRuns()
    lr.cat = databroker.catalog[TEST_CATALOG_NAME]
    lr._check_keys()
    assert len(lr.cat) == 53
    return lr


def test_getDefaultCatalog_none_found():
    with pytest.raises(ValueError) as exinfo:
        APS_utils.getDefaultCatalog()
    assert "Multiple catalog configurations available." in str(exinfo.value)


def test_getDefaultCatalog(cat):
    # put the catalog in the namespace of the called function
    APS_utils.__dict__.update(dict(cat1=cat))

    cat = APS_utils.getDefaultCatalog()
    assert cat is not None
    assert cat.name == TEST_CATALOG_NAME


def test_getDefaultCatalog_many_found(cat):
    APS_utils.__dict__.update(dict(cat1=cat, cat2=cat, cat3=cat))

    with pytest.raises(ValueError) as exinfo:
        APS_utils.getDefaultCatalog()
    assert "Multiple catalog objects available." in str(exinfo.value)


def test_getCatalog():
    # get by name of configuration YAML file
    ret = APS_utils.getCatalog(TEST_CATALOG_NAME)
    assert ret.name == TEST_CATALOG_NAME

    # get by supplying the catalog
    ret = APS_utils.getCatalog(ret)
    assert ret.name == TEST_CATALOG_NAME

    # fail with configuration YAML file name not found
    bad_name = "no such catalog configuration"
    with pytest.raises(KeyError) as exinfo:
        APS_utils.getCatalog(bad_name)
    assert bad_name in str(exinfo.value)


def test_getDefaultNamespace():
    ret = APS_utils.getDefaultNamespace()
    assert ret is not None
    assert isinstance(ret, dict)
    assert len(ret) > 0
    assert "getDefaultNamespace" in ret


def test_findCatalogsInNamespace(cat):
    APS_utils.__dict__.update(dict(cat1=cat, cat2=cat, cat3=cat))

    cats = APS_utils.findCatalogsInNamespace()
    assert len(cats) == 3


def test_ListRuns(cat):
    lr = APS_utils.ListRuns()
    assert lr is not None
    assert lr.cat is None
    assert lr.keys is None
    assert lr.missing == ""
    assert lr.num == 20
    assert lr.query is None
    assert lr.reverse is True
    assert lr.since is None
    assert lr.until is None
    assert lr.sortby == "time"
    assert lr.timefmt == "%Y-%m-%d %H:%M:%S"

    lr.cat = cat
    lr._check_cat()
    assert cat == lr.cat  # expect unchanged


def test_ListRuns_keys(lr):
    # use default keys
    lr.keys = None
    lr._check_keys()
    assert lr.keys is not None
    keys = "scan_id time plan_name detectors".split()  # expected
    assert len(lr.keys) == len(keys)
    for idx, label in enumerate(keys):
        assert lr.keys[idx] == label

    # custom keys as str
    keys = "scan_id plan_name"
    lr.keys = keys
    lr._check_keys()
    keys = keys.split()  # expected
    assert len(lr.keys) == len(keys)
    for idx, label in enumerate(keys):
        assert lr.keys[idx] == label

    # custom keys as [str]
    keys = "plan_name detectors motors".split()
    lr.keys = keys
    lr._check_keys()
    assert len(lr.keys) == len(keys)
    for idx, label in enumerate(keys):
        assert lr.keys[idx] == label

    # check that keys are in results dictionary
    dd = lr.parse_runs()
    assert len(dd) == len(lr.keys)
    for label in lr.keys:
        assert label in dd

    lr.keys.append("exit_status")
    lr.num = 1_000
    dd = lr.parse_runs()
    possibilities = "success fail abort".split()
    possibilities.append("")  # means "no stop document was recorded"
    # possibilities.append("unknown")
    for v in dd["exit_status"]:
        assert v in possibilities

    keys = "scan_id start.time stop.time"
    lr.keys = keys
    lr._check_keys()
    keys = keys.split()  # expected
    assert len(lr.keys) == len(keys)
    for idx, label in enumerate(keys):
        assert lr.keys[idx] == label


def test_ListRuns_missing(lr):
    lr.keys = "scan_id time".split()
    key = "no such key"
    lr.keys.append(key)
    missing = ""  # the default
    dd = lr.parse_runs()
    assert key in dd
    for v in dd[key]:
        assert v == missing

    missing = object()  # a very unexpected representation
    lr.missing = missing
    dd = lr.parse_runs()
    assert key in dd
    for v in dd[key]:
        assert v == missing


def test_ListRuns_to_num(lr):
    # depends on test database
    dd = lr.parse_runs()
    assert 0 <= len(dd["time"]) <= lr.num
    # assert len(dd["time"]) == -1

    lr.num = lr.num // 2
    dd = lr.parse_runs()
    assert 0 <= len(dd["time"]) <= lr.num

    lr.num *= 5
    dd = lr.parse_runs()
    assert 0 <= len(dd["time"]) <= lr.num


def test_ListRuns_query_count(lr):
    lr.query = dict(plan_name="count")
    dd = lr.parse_runs()
    assert 0 <= len(dd["time"]) <= lr.num
    for v in dd["plan_name"]:
        assert v == "count"


# fmt: off
@pytest.mark.parametrize(
    "nruns, query",
    [
        (27, dict(scan_id={"$lt": 20})),
        (26, dict(plan_name="count")),
        (0, dict(scan_id={"$lt": 20}, plan_name="count")),
        (19, dict(scan_id={"$gte": 100})),
        (19, dict(scan_id={"$gte": 100}, plan_name="count")),
    ],
)
def test_ListRuns_query_parametrize(nruns, query, lr):
    lr.num = 100
    lr.query = query
    dd = lr.parse_runs()
    assert len(dd["time"]) == nruns
# fmt: on


# fmt: off
@pytest.mark.parametrize(
    "reverse",
    [
        (True),
        (False),
    ],
)
def test_ListRuns_reverse(reverse, lr):
    # include with some data missing or None
    lr.reverse = reverse
    dd = lr.parse_runs()
    assert dd["time"] == sorted(dd["time"], reverse=reverse)
# fmt: on


def test_ListRuns_since(lr):
    # depends on test database
    lr.num = 100
    dd = lr.parse_runs()  # get some data
    t = dd["time"]
    assert len(t) > 2
    lr.since = t[len(t) // 2]  # adjust the cutoff date
    dd = lr.parse_runs()  # get filtered data
    assert len(t) > len(dd["time"])
    for v in dd["time"]:
        assert v >= lr.since


def test_ListRuns_sortby(lr):
    # include with some data missing or None
    # default
    dd = lr.parse_runs()
    assert dd[lr.sortby] == sorted(dd[lr.sortby], reverse=lr.reverse)

    # other key: uid is almost always out of time order
    lr.sortby = "uid"
    lr.keys = "time uid".split()
    dd = lr.parse_runs()
    assert dd["time"] != sorted(dd["time"], reverse=lr.reverse)
    assert dd[lr.sortby] == sorted(dd[lr.sortby], reverse=lr.reverse)

    # these keys might not even be found
    lr.sortby = "motive"
    lr.keys += "motive purpose exit_status".split()
    dd = lr.parse_runs()
    assert dd[lr.sortby] == sorted(dd[lr.sortby], reverse=lr.reverse)


def test_ListRuns_timefmt(lr):
    # default
    dd = lr.parse_runs()
    assert "time" in dd
    assert len(dd["time"]) > 0
    v0 = dd["time"][0]
    assert isinstance(v0, str)
    dt = datetime.datetime.fromisoformat(v0)
    assert isinstance(dt, datetime.datetime)

    # None
    lr.timefmt = None
    with pytest.raises(TypeError) as exinfo:
        lr.parse_runs()
    assert "strftime() argument 1 must be str, not None" in str(exinfo.value)

    # wrong format
    lr.timefmt = "no such format"
    dd = lr.parse_runs()
    assert dd["time"][0] == lr.timefmt

    # "raw"
    lr.timefmt = "raw"
    dd = lr.parse_runs()
    assert isinstance(dd["time"][0], float)

    # "%X" : hh:mm:ss
    lr.timefmt = "%X"
    dd = lr.parse_runs()
    v0 = dd["time"][0]
    assert v0.find(":") == 2
    assert len(v0.split(":")) == 3


def test_ListRuns_to_dataframe(lr):
    # Pandas DataFrame
    lr.keys = None
    out = lr.to_dataframe()
    assert out is not None
    assert lr.keys is not None
    assert len(lr.keys) == 4
    assert isinstance(out, pd.DataFrame)
    assert len(out.columns) == len(lr.keys)
    for idx, label in enumerate(lr.keys):
        assert out.columns[idx] == label


def test_ListRuns_to_table(lr):
    # reST table as multiline string
    lr.keys = None
    out = lr.to_table()
    assert out is not None
    assert lr.keys is not None
    assert len(lr.keys) == 4
    assert isinstance(out, str)
    assert "=======" in out.splitlines()[0]
    assert "scan_id" in out.splitlines()[1]


def test_ListRuns_until(lr):
    # depends on test database
    lr.num = 100
    lr.reverse = False
    dd = lr.parse_runs()  # get some data
    t = dd["time"]
    assert len(t) > 2
    lr.until = t[len(t) // 2]  # adjust the cutoff date
    dd = lr.parse_runs()  # get filtered data
    assert len(t) > len(dd["time"])
    for v in dd["time"]:
        assert v < lr.until


# fmt: off
@pytest.mark.parametrize(
    "tablefmt, structure",
    [
        (None, pd.DataFrame),
        ("dataframe", pd.DataFrame),
        ("table", str),
        ("no such format", str),
    ],
)
def test_listruns_tablefmt(tablefmt, structure, cat):
    lr = APS_utils.listruns(cat=cat, tablefmt=tablefmt, printing=False)
    assert lr is not None
    assert isinstance(lr, structure)
# fmt: on


# fmt: off
@pytest.mark.parametrize(
    "ids, nresults",
    [
        ([130, 131, 132], 3),
        ([1234], 0),
        (["bb7e0", ], 1),
        ([-2, -4, -10, -8], 4),
        ([], 0),
        ([-2, 131, "3e89a", 1234567, "1234567"], 3),
    ],
)
def test_ListRuns_ids(ids, nresults, lr):
    # include with some data missing or None
    lr.ids = ids
    dd = lr.parse_runs()
    assert len(dd["time"]) == nresults
# fmt: on

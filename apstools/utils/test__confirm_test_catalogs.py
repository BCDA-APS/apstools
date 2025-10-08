from contextlib import nullcontext as does_not_raise

import databroker
import pytest


@pytest.mark.parametrize(
    "cat_name, uid, context, expected",
    [
        ["apstools_test", -1, does_not_raise(), None],
        ["apstools_test", "49dce8d", does_not_raise(), None],
        ["no_such_catalog", -1, pytest.raises(AssertionError), "catalog not found"],
        ["usaxs_test", "abcd", pytest.raises(KeyError), "abcd"],
        ["usaxs_test", "e5d2cb", does_not_raise(), None],
    ],
)
def test_confirm_test_catalogs_ok(cat_name, uid, context, expected):
    with context as exinfo:
        assert len(list(databroker.catalog)), f"{list(databroker.catalog)=}"
        assert str(databroker.catalog_search_path()) != "", f"{databroker.catalog_search_path()=}"

        assert cat_name in databroker.catalog, f"{cat_name!r} catalog not found"
        cat = databroker.catalog[cat_name]
        run = cat[uid]
        assert run is not None, f"{cat=}  {uid=!r}"

    if expected is not None:
        assert str(expected) in str(exinfo)

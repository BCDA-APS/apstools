"""
Test the (deprecated) APS BSS user info device.
"""

import pytest

from .. import ApsBssUserInfoDevice


@pytest.mark.parametrize(
    "parms",
    [
        pytest.param(dict(prefix="9id_bss:", name="bss_user_info"), id="typical"),
        pytest.param(dict(prefix="", name="bss"), id="empty_prefix"),
    ],
)
def test_ApsBssUserInfoDevice_deprecated(parms):
    """Instantiating the device emits a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="apsbss"):
        device = ApsBssUserInfoDevice(**parms)
    assert device.name == parms["name"]

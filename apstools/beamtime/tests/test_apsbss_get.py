import pytest

from .. import apsbss
from .utils import is_aps_workstation


def test_cycle_not_found():
    if is_aps_workstation():
        cycle = "sdfsdjfyg"
        with pytest.raises(KeyError) as exc:
            apsbss.listESAFs(cycle, 9)
        assert f"APS cycle '{cycle}' not found." in str(exc.value)

        cycle = "not-a-cycle"
        with pytest.raises(KeyError) as exc:
            apsbss.listESAFs(cycle, 9)
        assert f"APS cycle '{cycle}' not found." in str(exc.value)


def test_listESAFs():
    if is_aps_workstation():
        cycle = "2020-2"
        assert len(apsbss.listESAFs(cycle, 9)) == 35
        assert len(apsbss.listESAFs([cycle], 9)) == 35
        assert len(apsbss.listESAFs((cycle), 9)) == 35
        assert len(apsbss.listESAFs("2020-1", 9)) == 41
        assert len(apsbss.listESAFs(["2020-1", "2020-2"], 9)) == 41 + 35
        # TODO: other tests


def test_listProposals():
    if is_aps_workstation():
        cycle = "2020-2"
        bl = "9-ID-B,C"
        assert len(apsbss.listProposals(cycle, bl)) == 21
        assert len(apsbss.listProposals([cycle], bl)) == 21
        assert len(apsbss.listProposals((cycle), bl)) == 21
        assert len(apsbss.listProposals("2020-1", bl)) == 12
        assert (
            len(apsbss.listProposals(["2020-1", "2020-2"], bl)) == 12 + 21
        )
        # TODO: other tests

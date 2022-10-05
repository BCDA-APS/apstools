from .test_positioner_soft_done import calcpos
from .test_positioner_soft_done import confirm_in_position
import pytest
import random


@pytest.mark.parametrize(
    # fmt: off
    "target", [-1.2345, -1, -1, -0.1, -0.1, 0, 0, 0, 0.1, 0.1, 1, 1, 1.2345]
    # fmt: on
)
def test_same_position_725(target, calcpos):
    # Before anything is changed.
    confirm_in_position(calcpos)

    # Confirm the initial position is as expected.
    if calcpos.position == target:
        # First, move away from the target.
        status = calcpos.move(-target or 0.1 *(1 +  random.random()))
        assert status.elapsed > 0, str(status)
        confirm_in_position(calcpos)

    # Move to the target position.
    status = calcpos.move(target)
    assert status.elapsed > 0, str(status)
    confirm_in_position(calcpos)

    # Do it again (the reason for issue #725).
    status = calcpos.move(target)
    assert status.elapsed > 0, str(status)
    confirm_in_position(calcpos)

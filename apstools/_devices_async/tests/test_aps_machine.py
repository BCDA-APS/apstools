import pytest

from ..aps_machine import ApsMachine


@pytest.mark.asyncio
async def test_read_attrs():
    aps = ApsMachine(name="aps")
    await aps.connect(mock=True)
    # Reading
    read_signals = {"aps-current"}
    reading = await aps.read()
    assert set(reading.keys()) == read_signals
    # Configuration
    config_signals = {
        "aps-fill_number",
        "aps-fill_pattern",
        "aps-floor_coordinator",
        "aps-last_problem_message",
        "aps-last_trip_message",
        "aps-machine_status",
        "aps-message6",
        "aps-message7",
        "aps-message8",
        "aps-operating_mode",
        "aps-operators",
        "aps-orbit_correction",
        "aps-shutter_status",
        "aps-shutters_open",
    }
    config = await aps.read_configuration()
    assert set(config.keys()) == config_signals
    # Hints
    assert aps.hints == {}


# -----------------------------------------------------------------------------
# :author:    Mark Wolfman
# :email:     wolfman@anl.gov
# :copyright: Copyright © 2023, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open
# Source License.
#
# The full license is in the file LICENSE.txt, distributed with this
# software.
# -----------------------------------------------------------------------------

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
# Distributed under the terms of the 3-Clause BSD License
#
# The full license is in the file LICENSE, distributed with this software.
#
# DISCLAIMER
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# -----------------------------------------------------------------------------

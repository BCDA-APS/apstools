"""
Ophyd support for EPICS synApps modules (records and databases).
"""

from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordInputFields
from ._common import EpicsRecordOutputFields
from ._common import EpicsRecordFloatFields
from ._common import EpicsSynAppsRecordEnableMixin

from .asyn import AsynRecord

from .busy import BusyRecord

from .calcout import CalcoutRecord
from .calcout import CalcoutRecordChannel
from .calcout import setup_gaussian_calcout
from .calcout import setup_incrementer_calcout
from .calcout import setup_lorentzian_calcout
from .calcout import UserCalcoutN
from .calcout import UserCalcoutDevice

from .epid import EpidRecord

from .iocstats import IocStatsDevice

from .luascript import LuascriptRecord
from .luascript import LuascriptRecordNumberInput
from .luascript import LuascriptRecordStringInput
from .luascript import UserScriptsDevice

from .save_data import SaveData

from .scalcout import UserScalcoutDevice
from .scalcout import UserScalcoutN
from .scalcout import ScalcoutRecord
from .scalcout import ScalcoutRecordNumberChannel
from .scalcout import ScalcoutRecordStringChannel

from .sscan import SscanRecord
from .sscan import SscanDevice

from .sseq import EditStringSequence
from .sseq import SseqRecord
from .sseq import UserStringSequenceDevice
from .sseq import UserStringSequenceN

from .sub import SubRecord
from .sub import SubRecordChannel
from .sub import UserAverageN
from .sub import UserAverageDevice

from .swait import SwaitRecord
from .swait import SwaitRecordChannel
from .swait import UserCalcN
from .swait import UserCalcsDevice
from .swait import setup_random_number_swait
from .swait import setup_gaussian_swait
from .swait import setup_lorentzian_swait
from .swait import setup_incrementer_swait

from .transform import TransformRecord
from .transform import UserTransformN
from .transform import UserTransformsDevice

# MUST come AFTER previous imports
from .db_2slit import Optics2Slit1D
from .db_2slit import Optics2Slit2D_HV
from .db_2slit import Optics2Slit2D_InbOutBotTop

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

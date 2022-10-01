"""
Support for APS hardware abstractions (both physical and virtual).
"""

# must come first to avoid circular imports
from .positioner_soft_done import PVPositionerSoftDone
from .positioner_soft_done import PVPositionerSoftDoneWithStop

# other imports
from .aps_bss_user import ApsBssUserInfoDevice

from .aps_cycle import ApsCycleDM

from .aps_machine import ApsMachineParametersDevice

from .aps_undulator import ApsUndulator
from .aps_undulator import ApsUndulatorDual

from .area_detector_support import AD_FrameType_schemes
from .area_detector_support import AD_plugin_primed
from .area_detector_support import AD_prime_plugin
from .area_detector_support import AD_prime_plugin2
from .area_detector_support import AD_full_file_name_local
from .area_detector_support import AD_EpicsFileNameHDF5Plugin
from .area_detector_support import AD_EpicsFileNameJPEGPlugin
from .area_detector_support import AD_EpicsFileNameTIFFPlugin
from .area_detector_support import AD_EpicsHdf5FileName
from .area_detector_support import AD_EpicsHDF5IterativeWriter
from .area_detector_support import AD_EpicsJPEGFileName
from .area_detector_support import AD_EpicsJPEGIterativeWriter
from .area_detector_support import AD_EpicsTIFFFileName
from .area_detector_support import AD_EpicsTIFFIterativeWriter
from .area_detector_support import CamMixin_V34
from .area_detector_support import CamMixin_V3_1_1
from .area_detector_support import SingleTrigger_V34


from .axis_tuner import AxisTunerException
from .axis_tuner import AxisTunerMixin

from .description_mixin import EpicsDescriptionMixin

from .dict_device_support import make_dict_device

from .epics_scan_id_signal import EpicsScanIdSignal

from .eurotherm_2216e import Eurotherm2216e

from .kohzu_monochromator import KohzuSeqCtl_Monochromator

from .lakeshore_controllers import LakeShore336Device
from .lakeshore_controllers import LakeShore340Device

from .linkam_controllers import Linkam_CI94_Device
from .linkam_controllers import Linkam_T96_Device

from .mixin_base import DeviceMixinBase

from .motor_mixins import EpicsMotorDialMixin
from .motor_mixins import EpicsMotorEnableMixin
from .motor_mixins import EpicsMotorLimitsMixin
from .motor_mixins import EpicsMotorRawMixin
from .motor_mixins import EpicsMotorResolutionMixin
from .motor_mixins import EpicsMotorServoMixin

from .ptc10_controller import PTC10AioChannel
from .ptc10_controller import PTC10RtdChannel
from .ptc10_controller import PTC10TcChannel
from .ptc10_controller import PTC10PositionerMixin

from .scaler_support import SCALER_AUTOCOUNT_MODE
from .scaler_support import use_EPICS_scaler_channels

from .shutters import ApsPssShutter
from .shutters import ApsPssShutterWithStatus
from .shutters import EpicsMotorShutter
from .shutters import EpicsOnOffShutter
from .shutters import OneSignalShutter
from .shutters import ShutterBase
from .shutters import SimulatedApsPssShutterWithStatus

from .srs570_preamplifier import SRS570_PreAmplifier

from .struck3820 import Struck3820

from .synth_pseudo_voigt import SynPseudoVoigt

from .tracking_signal import TrackingSignal

from .xia_pf4 import DualPf4FilterBox
from .xia_pf4 import Pf4FilterBank
from .xia_pf4 import Pf4FilterCommon
from .xia_pf4 import Pf4FilterDual
from .xia_pf4 import Pf4FilterSingle
from .xia_pf4 import Pf4FilterTriple

from .xia_slit import XiaSlit2D

# synApps

# ## _common
from ..synApps import EpicsRecordDeviceCommonAll
from ..synApps import EpicsRecordInputFields
from ..synApps import EpicsRecordOutputFields
from ..synApps import EpicsRecordFloatFields
from ..synApps import EpicsSynAppsRecordEnableMixin

# ## asyn
from ..synApps import AsynRecord

# ## busy
from ..synApps import BusyRecord

# ## calcout
from ..synApps import CalcoutRecord
from ..synApps import CalcoutRecordChannel
from ..synApps import setup_gaussian_calcout
from ..synApps import setup_incrementer_calcout
from ..synApps import setup_lorentzian_calcout
from ..synApps import UserCalcoutDevice
from ..synApps import UserCalcoutN

# ## epid
from ..synApps import EpidRecord

# ## iocstats
from ..synApps import IocStatsDevice

# ## save_data
from ..synApps import SaveData

# ## scalcout
from ..synApps import UserScalcoutDevice
from ..synApps import UserScalcoutN
from ..synApps import ScalcoutRecord
from ..synApps import ScalcoutRecordNumberChannel
from ..synApps import ScalcoutRecordStringChannel

# ## sscan
from ..synApps import SscanRecord
from ..synApps import SscanDevice

# sseq
from ..synApps import EditStringSequence
from ..synApps import SseqRecord
from ..synApps import UserStringSequenceDevice
from ..synApps import UserStringSequenceN

# ## sub
from ..synApps import SubRecord
from ..synApps import SubRecordChannel
from ..synApps import UserAverageN
from ..synApps import UserAverageDevice

# ## swait
from ..synApps import SwaitRecord
from ..synApps import SwaitRecordChannel
from ..synApps import UserCalcN
from ..synApps import UserCalcsDevice
from ..synApps import setup_random_number_swait
from ..synApps import setup_gaussian_swait
from ..synApps import setup_lorentzian_swait
from ..synApps import setup_incrementer_swait

# ## transform
from ..synApps import TransformRecord
from ..synApps import UserTransformN
from ..synApps import UserTransformsDevice

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
Test the area detector factory class with an ophyd fake device.

.. see: https://github.com/BCDA-APS/apstools/issues/984#issuecomment-2195201893
"""
from ophyd.sim import instantiate_fake_device as make_fake

from ..area_detector_factory import ad_class_factory


def test_my_fake_area_detector():
    ad_class = ad_class_factory("FakeAD")
    fake_ad = make_fake(ad_class, prefix="Fake:AD", name="fake_ad")
    assert "cam.acquire_time" not in fake_ad.stage_sigs

    fake_ad.stage_sigs["cam.acquire_time"] = 2.0
    fake_ad.stage()
    assert fake_ad.cam.acquire_time.get() == 2.0

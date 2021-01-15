"""
simple unit tests for this package
"""

import os
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, "..")
if _path not in sys.path:
    sys.path.insert(0, _path)

import gi

gi.require_version("Hkl", "5.0")  # MUST come before `import hkl`

from .common import Capture_stdout
from apstools import diffractometer as APS_diffractometer
from ophyd import Component, SoftPositioner
import hkl.diffract


class MyE4CV(APS_diffractometer.DiffractometerMixin, hkl.diffract.E4CV):
    """example with custom positioner names"""

    able = Component(SoftPositioner, labels=("motor"), kind="hinted")
    baker = Component(SoftPositioner, labels=("motor",), kind="hinted")
    charlie = Component(SoftPositioner, labels=("motor",), kind="hinted")
    arm = Component(SoftPositioner, labels=("motor",), kind="hinted")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for axis in self.real_positioners:
            axis.move(0)


class Test_Cases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sim4c(self):
        sim4c = APS_diffractometer.SoftE4CV("", name="sim4c")
        self.assertIsNotNone(sim4c)
        self.assertEqual(sim4c.omega.position, 0)
        self.assertEqual(sim4c.h.position, 0)
        self.assertEqual(sim4c.k.position, 0)
        self.assertEqual(sim4c.l.position, 0)
        self.assertEqual(
            sim4c.calc.physical_axis_names, ["omega", "chi", "phi", "tth"]
        )
        self.assertEqual(sim4c.calc.engine.mode, "bissector")
        self.assertEqual(sim4c.calc.wavelength, 1.54)
        self.assertEqual(len(sim4c.calc._samples), 1)
        self.assertEqual(sim4c.calc.sample.name, "main")
        self.assertEqual(sim4c.calc.sample.lattice.a, 1.54)

    # def test_sim4c_pa(self):
    #     sim4c = MyE4CV('', name='sim4c')
    #     sim4c.calc.physical_axis_names = dict(
    #         omega = "able",
    #         chi = "baker",
    #         phi = "charlie",
    #         tth = "arm")
    #     p1 = sim4c.calc.Position(able=45, baker=45, charlie=90.0, arm=90)
    #     p2 = sim4c.calc.Position(able=30, baker=90, charlie=90.0, arm=60)
    #     r1 = sim4c.calc.sample.add_reflection(1, 1, 0, position=p1)
    #     r2 = sim4c.calc.sample.add_reflection(0, 1, 0, position=p2)
    #     sim4c.calc.sample.compute_UB(r1, r2)
    #     tbl = sim4c.pa(printing=False)
    #     received = str(tbl).splitlines()
    #     expected = [
    #         "===================== ===============================================================================",
    #         "term                  value                                                                          ",
    #         "===================== ===============================================================================",
    #         "diffractometer        sim4c                                                                          ",
    #         "geometry              E4CV                                                                           ",
    #         "class                 MyE4CV                                                                         ",
    #         "energy (keV)          0.80509                                                                        ",
    #         "wavelength (angstrom) 1.54000                                                                        ",
    #         "calc engine           hkl                                                                            ",
    #         "mode                  bissector                                                                      ",
    #         "positions             ======= ======= =============                                                  ",
    #         "                      name    value   original name                                                  ",
    #         "                      ======= ======= =============                                                  ",
    #         "                      able    0.00000 omega                                                          ",
    #         "                      baker   0.00000 chi                                                            ",
    #         "                      charlie 0.00000 phi                                                            ",
    #         "                      arm     0.00000 tth                                                            ",
    #         "                      ======= ======= =============                                                  ",
    #         "constraints           ======= ========= ========== ===== ====                                        ",
    #         "                      axis    low_limit high_limit value fit                                         ",
    #         "                      ======= ========= ========== ===== ====                                        ",
    #         "                      able    -180.0    180.0      0.0   True                                        ",
    #         "                      baker   -180.0    180.0      0.0   True                                        ",
    #         "                      charlie -180.0    180.0      0.0   True                                        ",
    #         "                      arm     -180.0    180.0      0.0   True                                        ",
    #         "                      ======= ========= ========== ===== ====                                        ",
    #         "sample: main          ================= =============================================================",
    #         "                      term              value                                                        ",
    #         "                      ================= =============================================================",
    #         "                      unit cell edges   a=1.54, b=1.54, c=1.54                                       ",
    #         "                      unit cell angles  alpha=90.0, beta=90.0, gamma=90.0                            ",
    #         "                      ref 1 (hkl)       h=1.0, k=1.0, l=0.0                                          ",
    #         "                      ref 1 positioners able=45.00000, baker=45.00000, charlie=90.00000, arm=90.00000",
    #         "                      ref 2 (hkl)       h=0.0, k=1.0, l=0.0                                          ",
    #         "                      ref 2 positioners able=30.00000, baker=90.00000, charlie=90.00000, arm=60.00000",
    #         "                      [U]               [[ 1.00000000e+00 -1.11022302e-16  1.08845649e-16]           ",
    #         "                                         [ 1.11022302e-16  1.00000000e+00 -1.08845649e-16]           ",
    #         "                                         [-1.08845649e-16  1.08845649e-16  1.00000000e+00]]          ",
    #         "                      [UB]              [[ 4.07999046e+00 -7.02797298e-16  1.94261847e-16]           ",
    #         "                                         [ 4.52969935e-16  4.07999046e+00 -6.93916573e-16]           ",
    #         "                                         [-4.44089210e-16  4.44089210e-16  4.07999046e+00]]          ",
    #         "                      ================= =============================================================",
    #         "===================== ===============================================================================",
    #         ]
    #     for r, e in zip(received, expected):
    #         self.assertEqual(r, e)

    # def test_sim4c_wh(self):
    #     sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')
    #     tbl = sim4c.wh(printing=False)
    #     received = str(tbl).splitlines()
    #     expected = [
    #         "===================== ========= =========",
    #         "term                  value     axis_type",
    #         "===================== ========= =========",
    #         "diffractometer        sim4c              ",
    #         "sample name           main               ",
    #         "energy (keV)          0.80509            ",
    #         "wavelength (angstrom) 1.54000            ",
    #         "calc engine           hkl                ",
    #         "mode                  bissector          ",
    #         "h                     0.0       pseudo   ",
    #         "k                     0.0       pseudo   ",
    #         "l                     0.0       pseudo   ",
    #         "omega                 0         real     ",
    #         "chi                   0         real     ",
    #         "phi                   0         real     ",
    #         "tth                   0         real     ",
    #         "===================== ========= =========",
    #         ]
    #     for r, e in zip(received, expected):
    #         self.assertEqual(r, e)

    def test_sim4c_showConstraints(self):
        sim4c = APS_diffractometer.SoftE4CV("", name="sim4c")
        with Capture_stdout() as received:
            sim4c.showConstraints()
        expected = [
            "===== ========= ========== ===== ====",
            "axis  low_limit high_limit value fit ",
            "===== ========= ========== ===== ====",
            "omega -180.0    180.0      0.0   True",
            "chi   -180.0    180.0      0.0   True",
            "phi   -180.0    180.0      0.0   True",
            "tth   -180.0    180.0      0.0   True",
            "===== ========= ========== ===== ====",
        ]
        for r, e in zip(received, expected):
            self.assertEqual(r, e)

    def test_sim4c_forwardSolutionsTable(self):
        sim4c = APS_diffractometer.SoftE4CV("", name="sim4c")

        # (100) has chi ~ 0 which poses occasional roundoff errors
        # (sometimes -0.00000, sometimes 0.00000)
        sol = sim4c.forward(1, 0, 0)
        self.assertAlmostEqual(sol.omega, -30, places=5)
        self.assertAlmostEqual(sol.chi, 0, places=5)
        self.assertAlmostEqual(sol.phi, -90, places=5)
        self.assertAlmostEqual(sol.tth, -60, places=5)

        tbl = sim4c.forwardSolutionsTable(
            # fmt: off
            [
                [1,1,0],
                [1,1,1],
                [100,1,1],  # no solutions
            ]
            # fmt: on
        )
        received = str(tbl).splitlines()
        expected = [
            "=========== ======== ======== ======== ======== =========",
            "(hkl)       solution omega    chi      phi      tth      ",
            "=========== ======== ======== ======== ======== =========",
            "[1, 1, 0]   0        45.00000 45.00000 90.00000 90.00000 ",
            "[1, 1, 1]   0        60.00000 35.26439 45.00000 120.00000",
            "[100, 1, 1] none                                         ",
            "=========== ======== ======== ======== ======== =========",
        ]
        for r, e in zip(received, expected):
            self.assertEqual(r, e)

    def test_sim4c_applyConstraints(self):
        sim4c = APS_diffractometer.SoftE4CV("", name="sim4c")
        sim4c.applyConstraints(
            {
                "tth": APS_diffractometer.Constraint(0, 180, 0, True),
                "chi": APS_diffractometer.Constraint(0, 180, 0, True),
            }
        )
        sol = sim4c.forward(1, 0, 0)
        self.assertAlmostEqual(sol.omega, 30, places=5)
        self.assertAlmostEqual(sol.chi, 0, places=5)
        self.assertAlmostEqual(sol.phi, 90, places=5)
        self.assertAlmostEqual(sol.tth, 60, places=5)

    def test_sim6c(self):
        sim6c = APS_diffractometer.SoftE6C("", name="sim6c")
        self.assertIsNotNone(sim6c)
        self.assertEqual(sim6c.omega.position, 0)
        self.assertEqual(sim6c.h.position, 0)
        self.assertEqual(sim6c.k.position, 0)
        self.assertEqual(sim6c.l.position, 0)
        self.assertEqual(
            sim6c.calc.physical_axis_names,
            ["mu", "omega", "chi", "phi", "gamma", "delta"],
        )

    # def test_sim6c_wh(self):
    #     sim6c = APS_diffractometer.SoftE6C('', name='sim6c')
    #     tbl = sim6c.wh(printing=False)
    #     received = str(tbl).splitlines()
    #     expected = [
    #         "===================== ================== =========",
    #         "term                  value              axis_type",
    #         "===================== ================== =========",
    #         "diffractometer        sim6c                       ",
    #         "sample name           main                        ",
    #         "energy (keV)          0.80509                     ",
    #         "wavelength (angstrom) 1.54000                     ",
    #         "calc engine           hkl                         ",
    #         "mode                  bissector_vertical          ",
    #         "h                     0.0                pseudo   ",
    #         "k                     0.0                pseudo   ",
    #         "l                     0.0                pseudo   ",
    #         "mu                    0                  real     ",
    #         "omega                 0                  real     ",
    #         "chi                   0                  real     ",
    #         "phi                   0                  real     ",
    #         "gamma                 0                  real     ",
    #         "delta                 0                  real     ",
    #         "===================== ================== =========",
    #         ]
    #     for r, e in zip(received, expected):
    #         self.assertEqual(r, e)

    def test_sim6c_forward(self):
        sim6c = APS_diffractometer.SoftE6C("", name="sim6c")
        sol = sim6c.forward(1, 0, 0)
        self.assertAlmostEqual(sol.mu, 0, places=5)
        self.assertAlmostEqual(sol.omega, 30, places=5)
        self.assertAlmostEqual(sol.chi, 0, places=5)
        self.assertAlmostEqual(sol.phi, 90, places=5)
        self.assertAlmostEqual(sol.gamma, 0, places=5)
        self.assertAlmostEqual(sol.delta, 60, places=5)

    def test_simk4c(self):
        simk4c = APS_diffractometer.SoftK4CV("", name="simk4c")
        self.assertIsNotNone(simk4c)
        self.assertEqual(simk4c.komega.position, 0)
        self.assertEqual(simk4c.h.position, 0)
        self.assertEqual(simk4c.k.position, 0)
        self.assertEqual(simk4c.l.position, 0)
        self.assertEqual(
            simk4c.calc.physical_axis_names,
            ["komega", "kappa", "kphi", "tth"],
        )

    # def test_simk4c_wh(self):
    #     simk4c = APS_diffractometer.SoftK4CV('', name='simk4c')
    #     tbl = simk4c.wh(printing=False)
    #     received = str(tbl).splitlines()
    #     expected = [
    #         "===================== ========= =========",
    #         "term                  value     axis_type",
    #         "===================== ========= =========",
    #         "diffractometer        simk4c             ",
    #         "sample name           main               ",
    #         "energy (keV)          0.80509            ",
    #         "wavelength (angstrom) 1.54000            ",
    #         "calc engine           hkl                ",
    #         "mode                  bissector          ",
    #         "h                     0.0       pseudo   ",
    #         "k                     0.0       pseudo   ",
    #         "l                     0.0       pseudo   ",
    #         "komega                0         real     ",
    #         "kappa                 0         real     ",
    #         "kphi                  0         real     ",
    #         "tth                   0         real     ",
    #         "===================== ========= =========",
    #         ]
    #     for r, e in zip(received, expected):
    #         self.assertEqual(r, e)

    def test_simk4c_forward(self):
        simk4c = APS_diffractometer.SoftK4CV("", name="simk4c")
        sol = simk4c.forward(1, 0, 0)
        self.assertAlmostEqual(sol.komega, 120, places=5)
        self.assertAlmostEqual(sol.kappa, 0, places=5)
        self.assertAlmostEqual(sol.kphi, 0, places=5)
        self.assertAlmostEqual(sol.tth, 60, places=5)

    def test_simk6c(self):
        simk6c = APS_diffractometer.SoftK6C("", name="simk6c")
        self.assertIsNotNone(simk6c)
        self.assertEqual(simk6c.komega.position, 0)
        self.assertEqual(simk6c.h.position, 0)
        self.assertEqual(simk6c.k.position, 0)
        self.assertEqual(simk6c.l.position, 0)
        self.assertEqual(
            simk6c.calc.physical_axis_names,
            ["mu", "komega", "kappa", "kphi", "gamma", "delta"],
        )

    # def test_simk6c_wh(self):
    #     simk6c = APS_diffractometer.SoftK6C('', name='simk6c')
    #     tbl = simk6c.wh(printing=False)
    #     received = str(tbl).splitlines()
    #     expected = [
    #         "===================== ================== =========",
    #         "term                  value              axis_type",
    #         "===================== ================== =========",
    #         "diffractometer        simk6c                      ",
    #         "sample name           main                        ",
    #         "energy (keV)          0.80509                     ",
    #         "wavelength (angstrom) 1.54000                     ",
    #         "calc engine           hkl                         ",
    #         "mode                  bissector_vertical          ",
    #         "h                     0.0                pseudo   ",
    #         "k                     0.0                pseudo   ",
    #         "l                     0.0                pseudo   ",
    #         "mu                    0                  real     ",
    #         "komega                0                  real     ",
    #         "kappa                 0                  real     ",
    #         "kphi                  0                  real     ",
    #         "gamma                 0                  real     ",
    #         "delta                 0                  real     ",
    #         "===================== ================== =========",
    #         ]
    #     for r, e in zip(received, expected):
    #         self.assertEqual(r, e)

    def test_simk6c_forward(self):
        simk6c = APS_diffractometer.SoftK6C("", name="simk6c")
        sol = simk6c.forward(1, 0, 0)
        self.assertAlmostEqual(sol.mu, 0, places=5)
        self.assertAlmostEqual(sol.komega, -120, places=5)
        self.assertAlmostEqual(sol.kappa, 0, places=5)
        self.assertAlmostEqual(sol.kphi, 0, places=5)
        self.assertAlmostEqual(sol.gamma, 0, places=5)
        self.assertAlmostEqual(sol.delta, -60, places=5)


def suite(*args, **kw):
    test_list = [
        Test_Cases,
    ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())

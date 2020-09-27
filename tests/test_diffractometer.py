
"""
simple unit tests for this package
"""

import os
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import diffractometer as APS_diffractometer
from .common import Capture_stdout


class Test_Cases(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sim4c(self):
        sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')
        self.assertIsNotNone(sim4c)
        self.assertEqual(sim4c.omega.position, 0)
        self.assertEqual(sim4c.h.position, 0)
        self.assertEqual(sim4c.k.position, 0)
        self.assertEqual(sim4c.l.position, 0)
        self.assertEqual(
            sim4c.calc.physical_axis_names,
            ['omega', 'chi', 'phi', 'tth'])
        self.assertEqual(sim4c.calc.engine.mode, "bissector")
        self.assertEqual(sim4c.calc.wavelength, 1.54)
        self.assertEqual(len(sim4c.calc._samples), 1)
        self.assertEqual(sim4c.calc.sample.name, "main")
        self.assertEqual(sim4c.calc.sample.lattice.a, 1.54)

    def test_sim4c_wh(self):
        sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')
        tbl = sim4c.wh(printing=False)
        received = str(tbl).splitlines()
        expected = [
            "===================== =========",
            "term                  value    ",
            "===================== =========",
            "diffractometer        sim4c    ",
            "mode                  bissector",
            "wavelength (angstrom) 1.54     ",
            "h                     0.0      ",
            "k                     0.0      ",
            "l                     0.0      ",
            "omega                 0        ",
            "chi                   0        ",
            "phi                   0        ",
            "tth                   0        ",
            "===================== =========",
            ]
        for r, e in zip(received, expected):
            self.assertEqual(r, e)

    def test_sim4c_showConstraints(self):
        sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')
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
        sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')

        # (100) has chi ~ 0 which poses occasional roundoff errors
        # (sometimes -0.00000, sometimes 0.00000)
        sol = sim4c.forward(1,0,0)
        self.assertAlmostEquals(sol.omega, -30)
        self.assertAlmostEquals(sol.chi, 0)
        self.assertAlmostEquals(sol.phi, -90)
        self.assertAlmostEquals(sol.tth, -60)

        tbl = sim4c.forwardSolutionsTable(
            [
                [1,1,0],
                [1,1,1],
                [100,1,1],  # no solutions
                ]
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
        sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')
        sim4c.applyConstraints({
            "tth" : APS_diffractometer.Constraint(0, 180, 0, True),
            "chi" : APS_diffractometer.Constraint(0, 180, 0, True),
            })
        sol = sim4c.forward(1,0,0)
        self.assertAlmostEquals(sol.omega, 30)
        self.assertAlmostEquals(sol.chi, 0)
        self.assertAlmostEquals(sol.phi, 90)
        self.assertAlmostEquals(sol.tth, 60)

    def test_sim6c(self):
        sim6c = APS_diffractometer.SoftE6C('', name='sim6c')
        self.assertIsNotNone(sim6c)
        self.assertEqual(sim6c.omega.position, 0)
        self.assertEqual(sim6c.h.position, 0)
        self.assertEqual(sim6c.k.position, 0)
        self.assertEqual(sim6c.l.position, 0)
        self.assertEqual(
            sim6c.calc.physical_axis_names,
            ['mu', 'omega', 'chi', 'phi', 'gamma', 'delta'])

    def test_sim6c_wh(self):
        sim6c = APS_diffractometer.SoftE6C('', name='sim6c')
        tbl = sim6c.wh(printing=False)
        received = str(tbl).splitlines()
        expected = [
            "===================== ==================",
            "term                  value             ",
            "===================== ==================",
            "diffractometer        sim6c             ",
            "mode                  bissector_vertical",
            "wavelength (angstrom) 1.54              ",
            "h                     0.0               ",
            "k                     0.0               ",
            "l                     0.0               ",
            "mu                    0                 ",
            "omega                 0                 ",
            "chi                   0                 ",
            "phi                   0                 ",
            "gamma                 0                 ",
            "delta                 0                 ",
            "===================== ==================",
            ]
        for r, e in zip(received, expected):
            self.assertEqual(r, e)


def suite(*args, **kw):
    test_list = [
        Test_Cases,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())

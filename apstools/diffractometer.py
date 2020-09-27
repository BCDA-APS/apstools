"""
add to capabilities of any diffractometer

.. autosummary::

    ~Constraint
    ~DiffractometerMixin
    ~SoftE4CV

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2020, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

__all__ = [
    'Constraint',
    'DiffractometerMixin',
    'SoftE4CV',
]

from ophyd import Component, Device, PseudoSingle, SoftPositioner
import collections
import gi
import logging
import pyRestTable

logger = logging.getLogger(__file__)

gi.require_version('Hkl', '5.0')    # MUST come before `import hkl`
import hkl.diffract


Constraint = collections.namedtuple(
    "Constraint",
    ("low_limit", "high_limit", "value", "fit"))


class DiffractometerMixin(Device):
    """
    add to capabilities of any diffractometer

    .. autosummary::

        ~applyConstraints
        ~forwardSolutionsTable
        ~resetConstraints
        ~showConstraints
        ~undoLastConstraints
        ~wh
"""

    h = Component(PseudoSingle, '', labels=("hkl",), kind="hinted")
    k = Component(PseudoSingle, '', labels=("hkl",), kind="hinted")
    l = Component(PseudoSingle, '', labels=("hkl",), kind="hinted")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._constraints_stack = []

    def applyConstraints(self, constraints):
        """
        constrain the diffractometer's motions

        This action will first the current constraints onto
        a stack, enabling both *undo* and *reset* features.
        """
        self._push_current_constraints()
        self._set_constraints(constraints)

    def resetConstraints(self):
        """set constraints back to initial settings"""
        if len(self._constraints_stack) > 0:
            self._set_constraints(self._constraints_stack[0])
            self._constraints_stack = []

    def showConstraints(self, fmt="simple"):
        """print the current constraints in a table"""
        tbl = pyRestTable.Table()
        tbl.labels = "axis low_limit high_limit value fit".split()
        for m in self.real_positioners._fields:
            tbl.addRow((
                m,
                *self.calc[m].limits,
                self.calc[m].value,
                self.calc[m].fit))
        print(tbl.reST(fmt=fmt))

    def undoLastConstraints(self):
        """remove the current additional constraints, restoring previous constraints"""
        if len(self._constraints_stack) > 0:
            self._set_constraints(self._constraints_stack.pop())

    def _push_current_constraints(self):
        """push current constraints onto the stack"""
        constraints = {
            m: Constraint(
                *self.calc[m].limits,
                self.calc[m].value,
                self.calc[m].fit)
            for m in self.real_positioners._fields
            # TODO: any other positioner constraints
        }
        self._constraints_stack.append(constraints)

    def _set_constraints(self, constraints):
        """set diffractometer's constraints"""
        for axis, constraint in constraints.items():
            self.calc[axis].limits = (constraint.low_limit, constraint.high_limit)
            self.calc[axis].value = constraint.value
            self.calc[axis].fit = constraint.fit

    def forwardSolutionsTable(self, reflections, full=False):
        """
        return table of computed solutions for each (hkl) in the supplied reflections list

        The solutions are calculated using the current UB matrix & constraints
        """
        _table = pyRestTable.Table()
        motors = self.real_positioners._fields
        _table.labels = "(hkl) solution".split() + list(motors)
        for reflection in reflections:
            try:
                solutions = self.calc.forward(reflection)
            except ValueError as exc:
                solutions = exc
            if isinstance(solutions, ValueError):
                row = [reflection, "none"]
                row += ["" for m in motors]
                _table.addRow(row)
            else:
                for i, s in enumerate(solutions):
                    row = [reflection, i]
                    row += [f"{getattr(s, m):.5f}" for m in motors]
                    _table.addRow(row)
                    if not full:
                        break   # only show the first (default) solution
        return _table

    def wh(self, printing=True):
        """
        report the diffractometer settings

        SPEC compatibility::

            1117.KAPPA> wh
            H K L =  0  0  1.7345
            Alpha = 20  Beta = 20  Azimuth = 90
            Omega = 32.952  Lambda = 1.54
            Two Theta       Theta         Chi         Phi     K_Theta       Kappa       K_Phi
            40.000000   20.000000   90.000000   57.048500   77.044988  134.755995  114.093455

        """
        table = pyRestTable.Table()
        table.labels = "term value".split()
        table.addRow(("diffractometer", self.name))
        table.addRow(("mode", self.calc.engine.mode))
        table.addRow(("wavelength (angstrom)", self.calc.wavelength))

        for k, v in self.calc.pseudo_axes.items():
            table.addRow((k, v))

        for item in self.real_positioners:
            table.addRow((item.attr_name, item.position))

        # TODO: show constraints?

        if printing:
            print(table)

        return table


class SoftE4CV(DiffractometerMixin, hkl.diffract.E4CV):
    """
    E4CV: Simulated (soft) 4-circle diffractometer, vertical scattering

    EXAMPLE

    ::

        sim4c = SoftE4CV('', name='sim4c')
    """

    h = Component(PseudoSingle, '',
        labels=("hkl", "fourc"), kind="hinted")
    k = Component(PseudoSingle, '',
        labels=("hkl", "fourc"), kind="hinted")
    l = Component(PseudoSingle, '',
        labels=("hkl", "fourc"), kind="hinted")

    omega = Component(SoftPositioner,
        labels=("motor", "fourc"), kind="hinted")
    chi =   Component(SoftPositioner,
        labels=("motor", "fourc"), kind="hinted")
    phi =   Component(SoftPositioner,
        labels=("motor", "fourc"), kind="hinted")
    tth =   Component(SoftPositioner,
        labels=("motor", "fourc"), kind="hinted")

    def __init__(self, *args, **kwargs):
        """
        start the SoftPositioner objects with initial values

        Since this diffractometer uses simulated motors,
        prime the SoftPositioners (motors) with initial values.
        Otherwise, with position == None, then describe(), and
        other functions get borked.
        """
        super().__init__(*args, **kwargs)

        for axis in self.real_positioners:
            axis.move(0)

"""
diffractometer support

.. autosummary::

    ~Constraint
    ~DiffractometerMixin
    ~SoftE4CV
    ~SoftE6C
    ~SoftK4CV
    ~SoftK6C

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
    'SoftE6C',
    'SoftK4CV',
    'SoftK6C',
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

    def pa(self, all_samples=False, printing=True):
        """
        report the diffractometer settings

        EXAMPLE::

            In [1]: from apstools import diffractometer as APS_diffractometer

            In [2]: sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')

            In [3]: sim4c.pa()
            ======
            tba...
            ======

            Out[3]: <pyRestTable.rest_table.Table at 0x7f55c4775cd0>
        """
        table = pyRestTable.Table()
        table.labels = "term value".split()

        table.addRow(("diffractometer", self.name))
        table.addRow(("geometry", self.calc._geometry.name_get()))
        table.addRow(("class", self.__class__.__name__))
        table.addRow(("energy (keV)", f"{self.calc.energy:.5f}"))
        table.addRow(("wavelength (angstrom)", f"{self.calc.wavelength:.5f}"))
        table.addRow(("calc engine", self.calc.engine.name))
        table.addRow(("mode", self.calc.engine.mode))

        for item in self.real_positioners:
            table.addRow((item.attr_name, f"{item.position:.5f}"))
        # TODO: motor renames (if any)
        # In [17]: sim4c.calc._axis_name_to_renamed                                                                                                                        
        # Out[17]: {}

        # In [18]: sim4c.calc.physical_axis_names??                                                                                                                        

        # In [19]: sim4c.calc._axis_name_to_renamed.values()                                                                                                               
        # Out[19]: dict_values([])

        # In [20]: sim4c.calc.physical_axis_names??                                                                                                                        

        # In [21]: sim4c.calc._geometry.axis_names_get()                                                                                                                   
        # Out[21]: ['omega', 'chi', 'phi', 'tth']
        # sim4c.calc.physical_axis_names = dict(
        #       omega = "able",
        #       chi = "baker",
        #       phi = "charlie",
        #       tth = "ttheta")

        if all_samples:
            samples = self.calc._samples.values()
        else:
            samples = [self.calc._sample]
        for sample in samples:
            t = pyRestTable.Table()
            t.labels = "term value".split()
            nm = sample.name
            if all_samples and sample == self.calc.sample:
                nm += " (*)"

            unit_cell = ""
            for k in "a b c alpha beta gamma".split():
                unit_cell += f"{k} {getattr(sample.lattice, k)}\n"
            t.addRow(("unit cell", str(unit_cell).strip()))

            for i, ref in enumerate(sample.reflections):
                rt = (
                    f"h {ref.h}\n"
                    f"k {ref.k}\n"
                    f"l {ref.l}\n")
                t.addRow((f"reflection {i+1}", str(rt).strip()))

            t.addRow(("[U]", sample.U))
            t.addRow(("[UB]", sample.UB))

            table.addRow((f"sample: {nm}", str(t).strip()))

        if printing:
            print(table)

        return table

    def wh(self, printing=True):
        """
        report where is the diffractometer

        EXAMPLE::

            In [1]: from apstools import diffractometer as APS_diffractometer

            In [2]: sim4c = APS_diffractometer.SoftE4CV('', name='sim4c')

            In [3]: sim4c.wh()
            ===================== =========
            term                  value
            ===================== =========
            diffractometer        sim4c
            sample name           main
            energy (keV)          0.80509
            wavelength (angstrom) 1.54000
            calc engine           hkl
            mode                  bissector
            h                     0.0
            k                     0.0
            l                     0.0
            omega                 0
            chi                   0
            phi                   0
            tth                   0
            ===================== =========

            Out[3]: <pyRestTable.rest_table.Table at 0x7f55c4775cd0>

        compare with similar function in SPEC::

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
        table.addRow(("sample name", self.calc.sample.name))
        table.addRow(("energy (keV)", f"{self.calc.energy:.5f}"))
        table.addRow(("wavelength (angstrom)", f"{self.calc.wavelength:.5f}"))
        table.addRow(("calc engine", self.calc.engine.name))
        table.addRow(("mode", self.calc.engine.mode))

        for k, v in self.calc.pseudo_axes.items():
            table.addRow((k, v))

        for item in self.real_positioners:
            table.addRow((item.attr_name, item.position))

        if printing:
            print(table)

        return table


class SoftE4CV(DiffractometerMixin, hkl.diffract.E4CV):
    """
    E4CV: Simulated (soft) 4-circle diffractometer, vertical scattering

    EXAMPLE::

        sim4c = SoftE4CV('', name='sim4c')
    """

    omega = Component(SoftPositioner,
        labels=("motor", "sim4c"), kind="hinted")
    chi =   Component(SoftPositioner,
        labels=("motor", "sim4c"), kind="hinted")
    phi =   Component(SoftPositioner,
        labels=("motor", "sim4c"), kind="hinted")
    tth =   Component(SoftPositioner,
        labels=("motor", "sim4c"), kind="hinted")

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


class SoftE6C(DiffractometerMixin, hkl.diffract.E6C):
    """
    E6C: Simulated (soft) 6-circle diffractometer

    EXAMPLE::

        sim6c = SoftE6C('', name='sim6c')
    """

    mu = Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")
    omega = Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")
    chi =   Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")
    phi =   Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")
    gamma = Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")
    delta =   Component(SoftPositioner,
        labels=("motor", "sim6c"), kind="hinted")

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


class SoftK4CV(DiffractometerMixin, hkl.diffract.K4CV):
    """
    K4CV: Simulated (soft) kappa as 4-circle diffractometer

    EXAMPLE::

        simk4c = SoftK4CV('', name='simk4c')
    """

    komega = Component(SoftPositioner,
        labels=("motor", "simk4c"), kind="hinted")
    kappa = Component(SoftPositioner,
        labels=("motor", "simk4c"), kind="hinted")
    kphi =   Component(SoftPositioner,
        labels=("motor", "simk4c"), kind="hinted")
    tth =   Component(SoftPositioner,
        labels=("motor", "simk4c"), kind="hinted")

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


class SoftK6C(DiffractometerMixin, hkl.diffract.K6C):
    """
    K6C: Simulated (soft) kappa 6-circle diffractometer

    EXAMPLE::

        simk6c = SoftK6C('', name='simk6c')
    """

    mu = Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")
    komega = Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")
    kappa =   Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")
    kphi =   Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")
    gamma = Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")
    delta =   Component(SoftPositioner,
        labels=("motor", "simk6c"), kind="hinted")

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

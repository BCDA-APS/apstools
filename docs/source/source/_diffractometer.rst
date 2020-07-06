
Diffractometer
--------------

.. automodule:: apstools.diffractometer
    :members:


Example : Constraints
+++++++++++++++++++++

Create a custom diffractometer class, adding the
mixin class as first argument::

    from apstools.diffractometer import Constraint, DiffractometerMixin

    class CustomE4CV(DiffractometerMixin, E4CV):
        h = Component(PseudoSingle, '', labels=("hkl", "fourc"))
        k = Component(PseudoSingle, '', labels=("hkl", "fourc"))
        l = Component(PseudoSingle, '', labels=("hkl", "fourc"))
        ...

Define an instance of your diffractometer::

    e4cv = CustomE4CV('', name='e4cv', labels=("diffractometer", "e4cv"))

Management of diffractometer constraints is enabled by use of
a stack of previous settings.  The diffractometer starts with
a default set of constraints.  Show the default constraints
with ``e4cv.showConstraints()``.  Here is the initial result::

    ===== ========= ========== ===== ====
    axis  low_limit high_limit value fit
    ===== ========= ========== ===== ====
    omega -180.0    180.0      0.0   True
    chi   -180.0    180.0      0.0   True
    phi   -180.0    180.0      0.0   True
    tth   -180.0    180.0      0.0   True
    ===== ========= ========== ===== ====

A set of constraints is defined as a dictionary with the
motor names as keys::

    diffractometer_constraints = {
        # axis: Constraint(lo_limit, hi_limit, value, fit)
        "omega": Constraint(-120, 150, 0, True),
        "chi": Constraint(-150, 120, 0, True),
        # "phi": Constraint(0, 0, 0, False),
        "tth": Constraint(-10, 142, 0, True),
    }

These constraints can be applied with command
``e4cv.applyConstraints(diffractometer_constraints)``
which first pushes the current constraints onto a
stack, such as::

    e4cv.applyConstraints(diffractometer_constraints)
    e4cv.showConstraints()

    ===== =================== ================== ===== ====
    axis  low_limit           high_limit         value fit
    ===== =================== ================== ===== ====
    omega -119.99999999999999 150.0              0.0   True
    chi   -150.0              119.99999999999999 0.0   True
    phi   -180.0              180.0              0.0   True
    tth   -10.0               142.0              0.0   True
    ===== =================== ================== ===== ====

Revert back to the previous constraints with command
``e4cv.undoLastConstraints()``.  Reset back to the
original constraints with command
``e4cv.resetConstraints()``


Example : Solutions
+++++++++++++++++++

With a given UB (orientation) matrix and constraints,
the motor locations of an *(hkl)* reflection may be computed.
The computation may result in zero or more possible
combinations of positions.

Show the possibilities with the
``e4cv.forwardSolutionsTable()`` command, such as::

    print(e4cv.forwardSolutionsTable(
        (
            (0, 0, 0.5),
            (0, 0, 1),
            (0, 0, 1.5)
        ),
        full=True
    ))

    =========== ======== ======== ========= ========= ========
    (hkl)       solution omega    chi       phi       tth
    =========== ======== ======== ========= ========= ========
    (0, 0, 0.5) 0        2.32262  -25.72670 -78.18577 4.64525
    (0, 0, 0.5) 1        -2.32262 25.72670  101.81423 -4.64525
    (0, 0, 1)   0        4.64907  -25.72670 -78.18577 9.29815
    (0, 0, 1)   1        -4.64907 25.72670  101.81423 -9.29815
    (0, 0, 1.5) 0        6.98324  -25.72670 -78.18577 13.96647
    =========== ======== ======== ========= ========= ========

As shown, for (0, 0, 1/2) and (001) reflections, there are
two possible solutions.
For the (0 0 3/2) reflection, there is only one solution.
If we further restrict *omega* to non-negative values, we'll
only get one solution for all three reflections in the list::

    e4cv.applyConstraints({"omega": Constraint(-0, 150, 0, True)})
    print(e4cv.forwardSolutionsTable(
        (
            (0, 0, 0.5),
            (0, 0, 1),
            (0, 0, 1.5)
        ),
        full=True
    ))

    =========== ======== ======= ========= ========= ========
    (hkl)       solution omega   chi       phi       tth
    =========== ======== ======= ========= ========= ========
    (0, 0, 0.5) 0        2.32262 -25.72670 -78.18577 4.64525
    (0, 0, 1)   0        4.64907 -25.72670 -78.18577 9.29815
    (0, 0, 1.5) 0        6.98324 -25.72670 -78.18577 13.96647
    =========== ======== ======= ========= ========= ========

If we reset the constraint back to the default settings, there
are six possible motor positions for each reflection::

    e4cv.resetConstraints()
    print(e4cv.forwardSolutionsTable(
        (
            (0, 0, 0.5),
            (0, 0, 1),
            (0, 0, 1.5)
        ),
        full=True
    ))

    =========== ======== ========== ========== ========= =========
    (hkl)       solution omega      chi        phi       tth
    =========== ======== ========== ========== ========= =========
    (0, 0, 0.5) 0        2.32262    -25.72670  -78.18577 4.64525
    (0, 0, 0.5) 1        -2.32262   25.72670   101.81423 -4.64525
    (0, 0, 0.5) 2        -2.32262   154.27330  -78.18577 -4.64525
    (0, 0, 0.5) 3        2.32262    -154.27330 101.81423 4.64525
    (0, 0, 0.5) 4        -177.67738 25.72670   101.81423 4.64525
    (0, 0, 0.5) 5        -177.67738 154.27330  -78.18577 4.64525
    (0, 0, 1)   0        4.64907    -25.72670  -78.18577 9.29815
    (0, 0, 1)   1        -4.64907   25.72670   101.81423 -9.29815
    (0, 0, 1)   2        -4.64907   154.27330  -78.18577 -9.29815
    (0, 0, 1)   3        4.64907    -154.27330 101.81423 9.29815
    (0, 0, 1)   4        -175.35093 25.72670   101.81423 9.29815
    (0, 0, 1)   5        -175.35093 154.27330  -78.18577 9.29815
    (0, 0, 1.5) 0        6.98324    -25.72670  -78.18577 13.96647
    (0, 0, 1.5) 1        -6.98324   25.72670   101.81423 -13.96647
    (0, 0, 1.5) 2        -6.98324   154.27330  -78.18577 -13.96647
    (0, 0, 1.5) 3        6.98324    -154.27330 101.81423 13.96647
    (0, 0, 1.5) 4        -173.01676 25.72670   101.81423 13.96647
    (0, 0, 1.5) 5        -173.01676 154.27330  -78.18577 13.96647
    =========== ======== ========== ========== ========= =========

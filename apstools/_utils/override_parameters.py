"""
----

.. autosummary::

   ~OverrideParameters
"""

__all__ = [
    "OverrideParameters",
]


import pandas as pd

# TODO: needs documentation file
# TODO: needs unit testing


class OverrideParameters:
    """
    Define parameters that can be overriden from a user configuration file.

    NOTE: This is a pure Python object, not using ophyd.

    TODO: Move this to a documentation source file.

    =============== ============================
    method          usage
    =============== ============================
    ``register()``  First, register a new parameter name to be supported by user overrides.
    ``set()``       Define an override value for a known parameter.
    ``pick()``      Choose value for a known parameter, picking between override and default value.
    ``summary()``   Print a table of all known parameters and values.
    ``reset()``     Remove an override value for a known parameter.  (sets it to undefined)
    ``reset_all()`` Remove override values for all known parameters.
    =============== ============================

    USAGE:

    Create a ``overrides`` object::

        overrides = apstools.utils.OverrideParameters()

    When code supports a parameter for which a user can provide
    a local override, the code should import the ``overrides``
    object (from the module where it has been created),
    and then register the parameter name, such as this example::

        overrides.register("minimum_step")

    Refer to ``plans.axis_tuning`` for example back-end
    handling.  Such as::

        overrides.register("usaxs_minstep")

    Then later::

        minstep = overrides.pick("usaxs_minstep", 0.000045)

    In the user's configuration file (loaded via ``%run -i user.py``),
    import the `overrides`` object::

        from instrument.devices import overrides

    and then override the attribute(s) as desired::

        overrides.set("usaxs_minstep", 1.0e-5)
    """

    def __init__(self):
        # ALWAYS use ``overrides.undefined`` for comparisons and resets.
        self.undefined = object()
        self._parameters = {}

    def register(self, parameter_name):
        """
        Register a new parameter name.
        """
        if parameter_name not in self._parameters:
            self._parameters[parameter_name] = self.undefined

    def set(self, parameter_name, value):
        """
        Set value of a known parameter.
        """
        if parameter_name not in self._parameters:
            raise KeyError(f"Unknown {parameter_name = }.  First call register().")
        self._parameters[parameter_name] = value

    def reset(self, parameter_name):
        """
        Remove the override of a known parameter.
        """
        if parameter_name not in self._parameters:
            raise KeyError(f"Unknown {parameter_name = }.  First call register().")
        self._parameters[parameter_name] = self.undefined

    def reset_all(self):
        """
        Change all override values back to undefined.
        """
        for parm in self._parameters.keys():
            self.reset(parm)

    def pick(self, parameter, default):
        """
        Either pick the override parameter value if defined, or the default.
        """
        value = self._parameters.get(parameter, default)
        if value == self.undefined:
            value = default
        return value

    def summary(self):
        """
        Return a pandas DataFrame with all overrides.

        Parameter names that have no override value will be reported
        as ``--undefined--``.
        """
        parameters = []
        values = []
        for parm in sorted(self._parameters.keys()):
            parameters.append(parm)
            values.append(self.pick(parm, "--undefined--"))
        return pd.DataFrame(dict(parameter=parameters, value=values))

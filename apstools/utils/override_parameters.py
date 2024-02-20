"""
OverrideParameters
+++++++++++++++++++++++++++++++++++++++

Define parameters that can be overridden from a user configuration file.

EXAMPLE:

Create an ``overrides`` object in a new file ``override_params.py``::

    import apstools.utils
    overrides = apstools.utils.OverrideParameters()

When code supports a parameter for which a user can provide
a local override, the code should import the ``overrides``
object (from the ``override_params`` module),
and then register the parameter name, such as this example::

    from override_params import overrides
    overrides.register("minimum_step")

Then later::

    minstep = overrides.pick("minimum_step", 45e-6)

In the user's configuration file that will override
the value of ``45e-6`` (such as can be loaded via
``%run -i user.py``), import the `overrides``
object (from the ``override_params`` module)::

    from override_params import overrides

and then override the attribute(s) as desired::

    overrides.set("minimum_step", 1.0e-5)

With this override in place, the ``minstep`` value
(from :meth:`~apstools.utils.OverrideParameters.pick()`)
will be ``1e-5``.

Get a pandas DataFrame object with all the overrides::

    overrides.summary()

which returns this table::

        parameter    value
    0  minimum_step  0.00001

----

.. autosummary::

   ~OverrideParameters
"""


import pandas as pd


class OverrideParameters:
    """
    Define parameters that can be overridden from a user configuration file.

    NOTE: This is a pure Python object, not using ophyd.

    .. autosummary::

       ~pick
       ~register
       ~reset
       ~reset_all
       ~set
       ~summary

    (new in apstools 1.5.2)
    """

    def __init__(self):
        # ALWAYS use ``overrides.undefined`` for comparisons and resets.
        self.undefined = object()
        self._parameters = {}

    def register(self, parameter_name):
        """
        Register a new parameter name to be supported by user overrides.
        """
        if parameter_name not in self._parameters:
            self._parameters[parameter_name] = self.undefined

    def _check_known(self, parameter_name):
        if parameter_name not in self._parameters:
            raise KeyError(f"Unknown parameter {parameter_name}.  First call register().")

    def set(self, parameter_name, value):
        """
        Define an override value for a known parameter.
        """
        self._check_known(parameter_name)
        self._parameters[parameter_name] = value

    def reset(self, parameter_name):
        """
        Remove an override value for a known parameter.  (sets it to undefined)
        """
        self._check_known(parameter_name)
        self._parameters[parameter_name] = self.undefined

    def reset_all(self):
        """
        Remove override values for all known parameters. (sets all to undefined)
        """
        for parm in self._parameters.keys():
            self.reset(parm)

    def pick(self, parameter, default):
        """
        Return either the override parameter value if defined, or the default.
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


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

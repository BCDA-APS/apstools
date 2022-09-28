"""
Synthetic pseudo-Voigt function
+++++++++++++++++++++++++++++++++++++++

EXAMPLES:

.. code-block:: python
    :caption: Simple example of SynPseudoVoigt().
    :linenos:

    from apstools.devices import SynPseudoVoigt
    from ophyd.sim import motor
    det = SynPseudoVoigt('det', motor, 'motor',
        center=0, eta=0.5, scale=1, sigma=1, bkg=0)

    # scan the "det" peak with the "motor" positioner
    # RE(bp.scan([det], motor, -2, 2, 41))


.. code-block:: python
    :caption: Example of SynPseudoVoigt() with randomized values.
    :linenos:

    import numpy as np
    from apstools.devices import SynPseudoVoigt
    synthetic_pseudovoigt = SynPseudoVoigt(
        'synthetic_pseudovoigt', m1, 'm1',
        center=-1.5 + 0.5*np.random.uniform(),
        eta=0.2 + 0.5*np.random.uniform(),
        sigma=0.001 + 0.05*np.random.uniform(),
        scale=1e5,
        bkg=0.01*np.random.uniform())

    # scan the "synthetic_pseudovoigt" peak with the "m1" positioner
    # RE(bp.scan([synthetic_pseudovoigt], m1, -2, 0, 219))

.. autosummary::

   ~SynPseudoVoigt
"""

import ophyd.sim
import numpy as np


class SynPseudoVoigt(ophyd.sim.SynSignal):  # lgtm [py/missing-call-to-init]
    """
    Evaluate a point on a pseudo-Voigt based on the value of a motor.

    .. index:: Ophyd Signal; SynPseudoVoigt

    Provides a signal to be measured.
    Acts like a detector.

    :see: https://en.wikipedia.org/wiki/Voigt_profile

    PARAMETERS

    name *str* :
        name of detector signal
    motor positioner :
        The independent coordinate
    motor_field *str* :
        name of `motor`
    center *float* :
        (optional)
        location of maximum value, default=0
    eta *float* :
        (optional)
        0 <= eta < 1.0: Lorentzian fraction, default=0.5
    scale *float* :
        (optional)
        scale >= 1 : scale factor, default=1
    sigma *float* :
        (optional)
        sigma > 0 : width, default=1
    bkg *float* :
        (optional)
        bkg >= 0 : constant background, default=0
    noise ``"poisson"`` or ``"uniform"`` or ``None`` :
        Add noise to the result.
    noise_multiplier *float* :
        Only relevant for 'uniform' noise. Multiply the random amount of
        noise by 'noise_multiplier'
    """

    def __init__(
        # fmt: off
        self,
        name, motor, motor_field,
        center=0, eta=0.5, scale=1, sigma=1, bkg=0,
        noise=None, noise_multiplier=1,
        **kwargs
        # fmt: on
    ):
        if eta < 0.0 or eta > 1.0:
            raise ValueError("eta={} must be between 0 and 1".format(eta))
        if scale < 1.0:
            raise ValueError("scale must be >= 1")
        if sigma <= 0.0:
            raise ValueError("sigma must be > 0")
        if bkg < 0.0:
            raise ValueError("bkg must be >= 0")

        # remember these terms for later access by user
        self.name = name
        self.motor = motor
        self.motor_field = motor_field
        self.center = center
        self.eta = eta
        self.scale = scale
        self.sigma = sigma
        self.bkg = bkg
        self.noise = noise
        self.noise_multiplier = noise_multiplier

        def f_lorentzian(x, gamma):
            # return gamma / np.pi / (x**2 + gamma**2)
            return 1 / np.pi / gamma / (1 + (x / gamma) ** 2)

        def f_gaussian(x, sigma):
            numerator = np.exp(-0.5 * (x / sigma) ** 2)
            denominator = sigma * np.sqrt(2 * np.pi)
            return numerator / denominator

        def pvoigt():
            m = motor.read()[self.motor_field]["value"]
            g_max = f_gaussian(0, self.sigma)  # peak normalization
            l_max = f_lorentzian(0, self.sigma)
            v = self.bkg
            if eta > 0:
                v += self.eta * f_lorentzian(m - self.center, self.sigma) / l_max
            if eta < 1:
                v += (1 - self.eta) * f_gaussian(m - self.center, self.sigma) / g_max
            v *= self.scale
            if self.noise == "poisson":
                v = int(np.random.poisson(np.round(v), 1))
            elif self.noise == "uniform":
                v += np.random.uniform(-1, 1) * self.noise_multiplier
            return v

        ophyd.sim.SynSignal.__init__(
            self, name=name, func=pvoigt, **kwargs
        )

    def randomize_parameters(self, scale=100_000, bkg=0.01):
        """
        Set random parameters. -1 <= center < 1, 0.001 <= sigma < 0.051, 95k <= scale <= 105k
        """
        self.center = -1.0 + 2 * np.random.uniform()
        self.eta = 0.2 + 0.5*np.random.uniform()
        self.sigma = 0.001 + 0.05*np.random.uniform()
        self.scale = scale * (0.95 + 0.1 * np.random.uniform())
        self.bkg = bkg*np.random.uniform()
        self.noise = "poisson"

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

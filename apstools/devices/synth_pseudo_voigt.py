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

import numpy as np
from typing import Any, Optional, Union

import ophyd.sim


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
        name: str,
        motor: Any,
        motor_field: str,
        center: float = 0,
        eta: float = 0.5,
        scale: float = 1,
        sigma: float = 1,
        bkg: float = 0,
        noise: Optional[str] = None,
        noise_multiplier: float = 1,
        **kwargs: Any,
        # fmt: on
    ) -> None:
        if eta < 0.0 or eta > 1.0:
            raise ValueError("eta={} must be between 0 and 1".format(eta))
        if scale < 1.0:
            raise ValueError("scale must be >= 1")
        if sigma <= 0.0:
            raise ValueError("sigma must be > 0")
        if bkg < 0.0:
            raise ValueError("bkg must be >= 0")

        # remember these terms for later access by user
        self.name: str = name
        self.motor: Any = motor
        self.motor_field: str = motor_field
        self.center: float = center
        self.eta: float = eta
        self.scale: float = scale
        self.sigma: float = sigma
        self.bkg: float = bkg
        self.noise: Optional[str] = noise
        self.noise_multiplier: float = noise_multiplier

        def f_lorentzian(x: float, gamma: float) -> float:
            # return gamma / np.pi / (x**2 + gamma**2)
            return 1 / (1 + (x / gamma) ** 2)

        def f_gaussian(x: float, sigma: float) -> float:
            return np.exp(-(x / sigma) ** 2)

        def pvoigt() -> Union[float, int]:
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

        super().__init__(name=name, func=pvoigt, **kwargs)

    def randomize_parameters(self, scale: float = 100_000, bkg: float = 0.01) -> None:
        """
        Randomize the parameters of the pseudo-Voigt function.

        Args:
            scale: The scale factor to use (default: 100,000)
            bkg: The background level to use (default: 0.01)
        """
        self.center = -1.5 + 0.5 * np.random.uniform()
        self.eta = 0.2 + 0.5 * np.random.uniform()
        self.sigma = 0.001 + 0.05 * np.random.uniform()
        self.scale = scale
        self.bkg = bkg * np.random.uniform()


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

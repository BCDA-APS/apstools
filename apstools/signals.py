
"""
(ophyd) Signals that might be useful at the APS using Bluesky

.. autosummary::
   
   ~SynPseudoVoigt

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

import logging
import ophyd.sim
import numpy as np


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


class SynPseudoVoigt(ophyd.sim.SynSignal):    # lgtm [py/missing-call-to-init]
    """
    Evaluate a point on a pseudo-Voigt based on the value of a motor.
    
    Provides a signal to be measured.
    Acts like a detector.
    
    :see: https://en.wikipedia.org/wiki/Voigt_profile

    PARAMETERS
    
    name : str
        name of detector signal
    motor : `Mover`
        The independent coordinate
    motor_field : str
        name of `Mover` field
    center : float, optional
        location of maximum value, default=0
    eta : float, optional
        0 <= eta < 1.0: Lorentzian fraction, default=0.5
    scale : float, optional
        scale >= 1 : scale factor, default=1
    sigma : float, optional
        sigma > 0 : width, default=1
    bkg : float, optional
        bkg >= 0 : constant background, default=0
    noise : {'poisson', 'uniform', None}
        Add noise to the result.
    noise_multiplier : float
        Only relevant for 'uniform' noise. Multiply the random amount of
        noise by 'noise_multiplier'

    EXAMPLE
    
    ::

        from apstools.signals import SynPseudoVoigt
        motor = Mover('motor', {'motor': lambda x: x}, {'x': 0})
        det = SynPseudoVoigt('det', motor, 'motor', 
            center=0, eta=0.5, scale=1, sigma=1, bkg=0)

    EXAMPLE
    
    ::

        import numpy as np
        from apstools.signals import SynPseudoVoigt
        synthetic_pseudovoigt = SynPseudoVoigt(
            'synthetic_pseudovoigt', m1, 'm1', 
            center=-1.5 + 0.5*np.random.uniform(), 
            eta=0.2 + 0.5*np.random.uniform(), 
            sigma=0.001 + 0.05*np.random.uniform(), 
            scale=1e5,
            bkg=0.01*np.random.uniform())

        #  RE(bp.scan([synthetic_pseudovoigt], m1, -2, 0, 219))

    """

    def __init__(self, name, motor, motor_field, center=0, 
                eta=0.5, scale=1, sigma=1, bkg=0, 
                noise=None, noise_multiplier=1,
                **kwargs):
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
        self.center = center
        self.eta = eta
        self.scale = scale
        self.sigma = sigma
        self.bkg = bkg
        self.noise = noise
        self.noise_multiplier = noise_multiplier

        def f_lorentzian(x, gamma):
            #return gamma / np.pi / (x**2 + gamma**2)
            return 1 / np.pi / gamma / (1 + (x/gamma)**2)

        def f_gaussian(x, sigma):
            numerator = np.exp(-0.5 * (x / sigma) ** 2)
            denominator = sigma * np.sqrt(2 * np.pi)
            return numerator / denominator

        def pvoigt():
            m = motor.read()[motor_field]['value']
            g_max = f_gaussian(0, sigma)    # peak normalization
            l_max = f_lorentzian(0, sigma)
            v = bkg
            if eta > 0:
                v += eta * f_lorentzian(m - center, sigma) / l_max
            if eta < 1:
                v += (1-eta) * f_gaussian(m - center, sigma) / g_max
            v *= scale
            if noise == 'poisson':
                v = int(np.random.poisson(np.round(v), 1))
            elif noise == 'uniform':
                v += np.random.uniform(-1, 1) * noise_multiplier
            return v

        ophyd.sim.SynSignal.__init__(self, name=name, func=pvoigt, **kwargs)

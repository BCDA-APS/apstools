import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Eample data
xpos = np.array([
    -0.89500,
    -0.78900,
    -0.68400,
    -0.57900,
    -0.47400,
    -0.36800,
    -0.26300,
    -0.15800,
    -0.05300,
    0.05300,
    0.15800,
    0.26300,
    0.36800,
    0.47400,
    0.57900,
    0.68400,
    0.78900,
    0.89500,
    1.00000,
])

sig = np.array([
    5225.44680,
    10406.54446,
    29364.11991,
    91847.11330,
    39397.99591,
    12719.50183,
    5950.02145,
    3483.21205,
    2210.18858,
    1552.42419,
    1088.73029,
    882.58759,
    680.85617,
    562.82269,
    466.21100,
    385.87965,
    315.28561,
    284.60984,
    246.65506,
])


dy_dx = np.gradient(sig, xpos)

# Plotting
plt.figure(figsize=(10, 5))

# Plot the original curve
plt.subplot(1, 2, 1)
plt.plot(xpos, sig, label='Original curve')
plt.legend()

# Plot the derivative
plt.subplot(1, 2, 2)
plt.plot(xpos, dy_dx, label='Derivative', color='red')
plt.legend()

plt.tight_layout()
plt.show()
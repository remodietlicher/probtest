import numpy as np
import matplotlib.pyplot as plt

from engine.perturb import perturb_array


def error_growth():



    parr = perturb_array(np.ones(100000), 1, amplitude)
    phist, edges = np.histogram(parr, bins=100)
    centers = 0.5 * (edges[1:] + edges[:-1])
    ax[0].semilogy(phist, centers)


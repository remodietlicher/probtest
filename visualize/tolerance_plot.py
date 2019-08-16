import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from util.constants import compute_statistics
from engine.perturb import perturb_array
from util.constants import MODE_TOLERANCE, MODE_PERTURB, MODE_VISUALIZE

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']


def tolerance_plot(config):
    tolerance_file_name = config[MODE_TOLERANCE].get('tolerance_file_name')
    check_variable_names = config['DEFAULT'].get('check_variable_names').split(",")
    amplitude = config[MODE_PERTURB].getfloat('amplitude')

    tol_df = pd.read_csv(tolerance_file_name)

    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(16, 9), sharey=True, gridspec_kw={"width_ratios": [1, 3]})

    parr = perturb_array(np.ones(100000), 1, amplitude) - 1
    phist, edges = np.histogram(parr, bins=np.logspace(-15, 0))
    centers = 0.5 * (edges[1:] + edges[:-1])
    ax[0].semilogy(centers * phist, centers, 'k')
    ax[0].ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax[0].set_ylabel("relative perturbation p")
    ax[0].set_xlabel("dN/dlog(p)")

    styles = [':', '--', '-']
    for i, vn in enumerate(check_variable_names):
        df = tol_df[tol_df['name'] == vn]
        for j, c in enumerate(compute_statistics):
            ax[1].semilogy(df['ntime'].values, df[c].values, ls=styles[j], c=colors[i], label='{} {}'.format(vn, c))
    ax[1].legend()
    ax[1].set_ylim(bottom=1e-15, top=1)
    ax[1].set_xlabel("timestep")

    fig.tight_layout()
    plt.show()

    return

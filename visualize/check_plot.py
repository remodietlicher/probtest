import pandas as pd
import matplotlib.pyplot as plt
from util.constants import compute_statistics, MODE_TOLERANCE, MODE_CHECK, MODE_VISUALIZE
from engine.tolerance import compute_max_rel_diff_dataframe
import numpy as np
import matplotlib.lines as mlines

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']


def check_plot(config):
    tolerance_file_name = config[MODE_TOLERANCE].get('tolerance_file_name')
    check_variable_names = config['DEFAULT'].get('check_variable_names').split(",")
    input_file_ref = config[MODE_CHECK].get('input_file_ref')
    input_file_cur = config[MODE_CHECK].get('input_file_cur')
    savedir = config[MODE_VISUALIZE].get("savedir")

    tol_df = pd.read_csv(tolerance_file_name)
    ref_df = pd.read_csv(input_file_ref)
    cur_df = pd.read_csv(input_file_cur)
    diff_df = compute_max_rel_diff_dataframe(ref_df, cur_df, check_variable_names)

    ncols = min(len(check_variable_names), 3)
    nrows = int(np.ceil(len(check_variable_names) / 3.0))
    fig, ax = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5*ncols, 3.5 * nrows), sharey=True, sharex=True)
    if nrows == 1:
        ax = np.expand_dims(ax, axis=0)
    if ncols == 1:
        ax = np.expand_dims(ax, axis=1)

    for i, vn in enumerate(check_variable_names):
        tol = tol_df[tol_df['name'] == vn]
        diff = diff_df[diff_df['name'] == vn]
        for j, c in enumerate(compute_statistics):
            ax[i // 3, i % 3].semilogy(tol['ntime'].values, tol[c].values, c=colors[j])
            ax[i // 3, i % 3].semilogy(diff['ntime'].values, diff[c].values, ls='--', c=colors[j])
            ax[i // 3, i % 3].set_ylim(bottom=1e-15, top=1)
            ax[i // 3, i % 3].set_xlabel("timestep")
            ax[i // 3, i % 3].set_title(vn)
        if i % 3 == 0:
            ax[i // 3, 0].set_ylabel("relative error")

    lines = []
    for i, c in enumerate(compute_statistics):
        lines.append(mlines.Line2D([], [], color=colors[i], label=c))
    lines.append(mlines.Line2D([], [], color='k', label='tolerance'))
    lines.append(mlines.Line2D([], [], color='k', ls='--', label='model'))

    legcol = 3 if ncols == 1 else 5
    ax[-1, ncols // 2].legend(handles=lines, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=legcol)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.3)
    if savedir:
        path = '{}/{}'.format(savedir, 'check_plot.pdf')
        print("saving figure to {}".format(path))
        fig.savefig(path)
    else:
        plt.show()

    return

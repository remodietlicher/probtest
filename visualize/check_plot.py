import pandas as pd
import matplotlib.pyplot as plt
from util.constants import compute_statistics, MODE_TOLERANCE, MODE_CHECK, MODE_VISUALIZE
from engine.tolerance import compute_max_rel_diff_dataframe
import numpy as np

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

    nrows = int(np.ceil(len(check_variable_names) / 3.0))
    fig, ax = plt.subplots(ncols=3, nrows=nrows, figsize=(16, 9), sharey=True, sharex=True)
    if nrows == 1:
        ax = np.expand_dims(ax, axis=1)

    for i, vn in enumerate(check_variable_names):
        tol = tol_df[tol_df['name'] == vn]
        diff = diff_df[diff_df['name'] == vn]
        for j, c in enumerate(compute_statistics):
            ax[i // 3, i % 3].semilogy(tol['ntime'].values, tol[c].values, label='{} {}'.format(vn, c), c=colors[j])
            ax[i // 3, i % 3].semilogy(diff['ntime'].values, diff[c].values, label='{} {}'.format(vn, c), ls='--',
                                       c=colors[j])
            ax[i // 3, i % 3].legend()
            ax[i // 3, i % 3].set_ylim(bottom=1e-15, top=1)
            ax[i // 3, i % 3].set_xlabel("timestep")
            ax[i // 3, i % 3].set_title(vn)
            if vn == 'zg':
                print(diff[c].values)
        if i % 3 == 0:
            ax[i // 3, 0].set_ylabel("relative error")

    fig.tight_layout()
    if savedir:
        path = '{}/{}'.format(savedir, 'check_plot.pdf')
        print("saving figure to {}".format(path))
        fig.savefig(path)
    else:
        plt.show()

    return

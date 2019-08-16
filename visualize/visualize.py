from visualize.tolerance_plot import tolerance_plot
from visualize.check_plot import check_plot
from util.constants import MODE_VISUALIZE


def visualize(config):
    plots = config[MODE_VISUALIZE].get('plots').split(",")

    for p in plots:
        if p == 'tolerance':
            tolerance_plot(config)
        elif p == 'check':
            check_plot(config)
        else:
            print("Visualization mode {} does not exist, must be any of {}"
                  .format(p, ",".join(['tolerance', 'check'])))

    return

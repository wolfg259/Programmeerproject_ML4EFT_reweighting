import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from matplotlib import rc
import seaborn as sns
import matplotlib.patches as mpatches
import itertools
import os
from quad_clas.analyse.analyse import Analyse
from ellipse_plotter_new import EllipsePlotter



rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica'], 'size': 26})
rc('text', usetex=True)



coeff_dict = {"cQd8": r'$c_{Qd}^{(8)}$', "cQj18": r'$c_{Qq}^{(1,8)}$', "cQj38": r'$c_{Qq}^{(3,8)}$', "cQu8": r'$c_{Qu}^{(8)}$', "ctd8": r'$c_{td}^{(8)}$', "ctGRe": r'$c_{tG}$',  "ctj8": r'$c_{qt}^{(8)}$', "ctu8": r'$c_{tu}^{(8)}$'}

root_lin = "/data/theorie/jthoeve/ML4EFT_jan/ML4EFT/output/tt_dec/nn_full"

# nn: linear (7 features)
post_path_nn = os.path.join(root_lin, '{}_{}', 'posterior_{}_{}.json')


paths_plot_1 = [post_path_nn]


labels_1 = [r"$\mathrm{ML}\;\mathrm{model}\;(\mathrm{all\;features}):\mathrm{Linear}$"]

def ellipse_overview(coeff_dict, labels, paths):

    n_cols = len(coeff_dict) - 1
    n_rows = n_cols

    fig = plt.figure(figsize=(n_cols * 4, n_rows * 4))

    c1_old = "cQd8"
    i = n_cols * n_rows
    j = 1
    for (c1, c2) in itertools.combinations(coeff_dict.keys(), 2):
        if c1 != c1_old:
            i -= j
            j += 1
            c1_old = c1
        ax = plt.subplot(n_rows, n_cols, i)

        plotter = EllipsePlotter()

        dfs = []
        for path in paths:
            if os.path.isfile(path.format(c1, c2, c1, c2)):
                dfs.append(Analyse.posterior_loader(path.format(c1, c2, c1, c2)))





        hndls = plotter.plot(ax, dfs, coeff1=c2, coeff2=c1,
                                 ax_labels=[coeff_dict[c2], coeff_dict[c1]],  kde=True)
        if j!=1:
            ax.set_xlabel('')
        if not (i == n_cols * n_rows + 1 - j * n_cols):
            ax.set_ylabel('')

        i -= 1

    legend = fig.legend(
            labels=labels, handles=hndls,
            loc='upper center', frameon=False, fontsize=26)

    bbox = legend.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())

    plt.tight_layout()

    return fig

fig_1 = ellipse_overview(coeff_dict, labels_1, paths_plot_1)
#fig_2 = ellipse_overview(coeff_dict, labels_2, paths_plot_2)
#fig_3 = ellipse_overview(coeff_dict, labels_3, paths_plot_3)
# fig_4 = ellipse_overview(coeff_dict, labels_4, paths_plot_4)

fig_1.savefig('/data/theorie/jthoeve/ML4EFT_jan/ML4EFT/plots/2022/05_09/tt_contours.pdf')
#fig_2.savefig('/data/theorie/jthoeve/ML4EFT_jan/ML4EFT/plots/2022/18_08/zh_particle_lin.pdf')
#fig_3.savefig('/data/theorie/jthoeve/ML4EFT_jan/ML4EFT/plots/2022/18_08/zh_particle_quad_kde.pdf')
# fig_4.savefig('/data/theorie/jthoeve/ML4EFT_jan/ML4EFT/plots/2022/18_08/test_overview_4.pdf')


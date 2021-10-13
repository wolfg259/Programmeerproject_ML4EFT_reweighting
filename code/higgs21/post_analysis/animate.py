import numpy as np
import matplotlib.pyplot as plt
import quad_clas.core.nn_analyse as analyse
import quad_clas.core.xsec.tt_prod as axs
from matplotlib import animation
import os

mz = 91.188 * 10 ** -3  # z boson mass [TeV]
mh = 0.125
cHW = 2
cHq3 = 0
x = np.linspace(0.3, 1.2, 100)
architecture = [2, 30, 30, 30, 30, 30, 1]

fig, ax = plt.subplots(figsize=(1.1 * 10, 1.1 * 6))

f_ana = axs.plot_likelihood_ratio_1D(x, cHW, cHq3, lin=True, quad=False)


model_dir = '/data/theorie/jthoeve/ML4EFT_higgs/models/model_cHW3_lin_30_reps/mc_run_{mc_run}'

means = []
stds = []
for i in range(1, 31):
    mean, std = np.loadtxt(os.path.join(model_dir.format(mc_run=i), 'scaling.dat'))
    means.append(mean)
    stds.append(std)


lines = []
for i in range(1, 31):
    if i == 1:
        lobj = ax.plot([], [], lw=1, color='C0', label=r'$\rm{NN\;replicas}$')[0]
    else:
        lobj = ax.plot([], [], lw=1, color='C0')[0]
    lines.append(lobj)



f_preds_init = []
for rep_nr, line in enumerate(lines):
    path = os.path.join(model_dir.format(mc_run=rep_nr + 1), 'trained_nn_{}.pt'.format(1))
    f_pred = analyse.make_predictions_1d(x, path.format(mc_run=rep_nr), architecture, cHW, cHq3, means[rep_nr], stds[rep_nr], None)
    f_preds_init.append(f_pred)
f_preds_init = np.array(f_preds_init)
f_pred_up = np.percentile(f_preds_init, 84, axis=0)
f_pred_down = np.percentile(f_preds_init, 16, axis=0)
fill = ax.fill_between(x, f_pred_up, f_pred_down, color='C0', alpha=0.3, label=r'$\rm{NN\;1}\sigma\rm{-band}$')

ax.plot(x, f_ana, '--', c='red', label=r'$\rm{Truth}$')
epoch_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=15)

plt.legend(loc='upper right', fontsize=15, frameon=False)
plt.ylim((0, 1))
plt.xlim(np.min(x), np.max(x))
plt.ylabel(r'$f\;(x, c)$')
plt.xlabel(r'$m_{ZH}\;[\mathrm{TeV}]$')

# initialization function: plot the background of each frame
def init():
    for line in lines:
        line.set_data([], [])
    epoch_text.set_text('')
    return lines

# animation function.  This is called sequentially
def animate(i):
    print(i)
    f_preds = []

    for rep_nr, line in enumerate(lines):
        path = os.path.join(model_dir.format(mc_run=rep_nr + 1), 'trained_nn_{}.pt'.format(i + 1))
        if os.path.isfile(path):
            f_pred = analyse.make_predictions_1d(x, path.format(mc_run=rep_nr), architecture, cHW, cHq3, means[rep_nr], stds[rep_nr], None)
            f_preds.append(f_pred)
            line.set_data(x, f_pred)
        else: # at the end of training
            path = os.path.join(model_dir.format(mc_run=rep_nr + 1), 'trained_nn.pt'.format(i + 1))
            f_pred = analyse.make_predictions_1d(x, path.format(mc_run=rep_nr), architecture, cHW, cHq3, means[rep_nr],
                                                 stds[rep_nr], None)
            f_preds.append(f_pred)
            line.set_data(x, f_pred)

    epoch_text.set_text(r'$\rm{epoch\;%d}$' % i)

    f_preds = np.array(f_preds)
    f_pred_up = np.percentile(f_preds, 84, axis=0)
    f_pred_down = np.percentile(f_preds, 16, axis=0)

    path = fill.get_paths()[0]
    verts = path.vertices
    verts[1:len(x)+1, 1] = f_pred_up[:]
    verts[len(x) + 2:-1, 1] = f_pred_down[:][::-1]

    return lines

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=400, interval=50, blit=True)

anim.save('/data/theorie/jthoeve/ML4EFT_higgs/plots/anim_band_cHW_lin_2_feat_30_reps.gif')
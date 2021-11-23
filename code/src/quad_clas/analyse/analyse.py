# This module contains all necessary functions to analyse and process the models


# import standard packages
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import rc
import numpy as np
import torch
import sys
import copy
import matplotlib.gridspec as gridspec
from matplotlib import animation
import os

# import own pacakges
from quad_clas.core import classifier as quad_clas
from quad_clas.core.truth import tt_prod as axs
from quad_clas.core.truth import vh_prod
from ..preproc import constants

mz = constants.mz # z boson mass [TeV]
mh = constants.mh

# matplotlib.use('PDF')
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica'], 'size': 22})
rc('text', usetex=True)


def likelihood_ratio_truth(x, c, lin=False, quad=False):
    """
    Computes the analytic likelihood ratio r(x, c)

    Parameters
    ----------
    x : numpy.ndarray, shape=(M, N)
        Kinematic feature vector with M instances of N kinematics, e.g. N =2 for
        the invariant mass and the rapidity.
    c : numpy.ndarray, shape=(M,)
        EFT point in M dimensions, e.g c = (cHW, cHq3)
    lin: bool, optional
        Set to False by default. Turn on for linear corrections.
    quad: bool, optional
        Set to False by default. Turn on for quadratic corrections.

    Returns
    -------
    ratio: numpy.ndarray, shape=(M,)
        Likelihood ratio wrt the SM for the events ``x``
    """

    n_kin = x.shape[1]
    cHW, cHq3 = c

    if n_kin == 1:
        dsigma_0 = [vh_prod.dsigma_dmvh(x_i, cHW, cHq3, lin=lin, quad=quad) for x_i in x]  # EFT
        dsigma_1 = [vh_prod.dsigma_dmvh(x_i, 0, 0, lin=lin, quad=quad) for x_i in x]  # SM
    elif n_kin == 2:
        dsigma_0 = [vh_prod.dsigma_dmvh_dy(y, mvh, cHW, cHq3, lin=lin, quad=quad) for (mvh, y) in x]  # EFT
        dsigma_1 = [vh_prod.dsigma_dmvh_dy(y, mvh, 0, 0, lin=lin, quad=quad) for (mvh, y) in x]  # SM
    else:
        raise NotImplementedError("No more than two features are currently supported")

    dsigma_0, dsigma_1 = np.array(dsigma_0), np.array(dsigma_1)

    ratio = np.divide(dsigma_0, dsigma_1, out=np.zeros_like(dsigma_0), where=dsigma_1 != 0)

    return ratio.flatten()

def decision_function_truth(x, c, lin=False, quad=False):
    """
    Computes the analytic decission function f(x, c)

    Parameters
    ----------
    x: numpy.ndarray, shape=(M, N)
        Kinematic feature vector with M instances of N kinematics, e.g. N =2 for
        the invariant mass and the rapidity.
    c: numpy.ndarray, shape=(M,)
        EFT point in M dimensions, e.g c = (cHW, cHq3)
    lin: bool, optional
        Set to False by default. Turn on for linear corrections.
    quad: bool, optional
        Set to False by default. Turn on for quadratic corrections.

    Returns
    -------
    ratio: numpy.ndarray, shape=(M,)
        Decission function f for the events ``x``
    """

    ratio = likelihood_ratio_truth(x, c, lin, quad)
    f = 1 / (1 + ratio)
    return f

def likelihood_ratio_nn(x, c, path_to_models, architecture, mc_run, lin=False, quad=False):
    """
    Computes the reconstructed likelihood ratio r(x, c) using the NN models

    Parameters
    ----------
    x : torch.tensor, shape=(M, N)
        Kinematics feature vector with M instances of N kinematics, e.g. N =2 for
        the invariant mass and the rapidity.
    c : numpy.ndarray, shape=(M,)
        EFT point in M dimensions, e.g c = (cHW, cHq3)
    path_to_models: dict
        Path to the nn model root directory
    mc_run: int
        Monte Carlo replica number
    lin: bool, optional
        Set to False by default. Turn on for linear corrections.
    quad: bool, optional
        Set to False by default. Turn on for quadratic corrections.

    Returns
    -------
    ratio: numpy.ndarray, shape=(M,)
        Reconstructed likelihood ratio wrt the SM for the events ``x``
    """
    cHW, cHq3 = c

    path_nn_lin = path_to_models['lin']  # shape = (len(c), )
    # path_nn_quad = path_to_models['quad'] # shape = (len(c), )
    # path_nn_cross = path_to_models['cross'] # TODO: shape

    with torch.no_grad():
        n_lin_1 = quad_clas.PredictorLinear(architecture)

        path_nn_lin_1 = os.path.join(path_nn_lin[0], 'mc_run_{}', 'trained_nn.pt')
        n_lin_1.load_state_dict(torch.load(path_nn_lin_1.format(mc_run)))
        mean, std = np.loadtxt(os.path.join(path_nn_lin[0], 'mc_run_{}'.format(mc_run), 'scaling.dat'))

        x_scaled = (x - mean) / std
        n_lin_1_out = n_lin_1.n_alpha(x_scaled.float())

        #######

        n_lin_2 = quad_clas.PredictorLinear(architecture)

        path_nn_lin_2 = os.path.join(path_nn_lin[1], 'mc_run_{}', 'trained_nn.pt')
        n_lin_2.load_state_dict(torch.load(path_nn_lin_2.format(mc_run)))
        mean, std = np.loadtxt(os.path.join(path_nn_lin[1], 'mc_run_{}'.format(mc_run), 'scaling.dat'))

        x_scaled = (x - mean) / std
        n_lin_2_out = n_lin_2.n_alpha(x_scaled.float())

        ########

        # n_quad_1 = PredictorQuadratic(architecture)
        # n_quad_1.load_state_dict(torch.load(path_nn_quad_1.format(mc_run)))
        #
        # mean, std = np.loadtxt(os.path.join(path_quad_1, 'mc_run_{}'.format(mc_run), 'scaling.dat'))
        # x_scaled = (x - mean) / std
        # n_quad_1_out = n_quad_1.n_beta(x_scaled.float()) ** 2
        #
        # #######
        #
        # n_quad_2 = PredictorQuadratic(architecture)
        # n_quad_2.load_state_dict(torch.load(path_nn_quad_2.format(mc_run)))
        #
        # mean, std = np.loadtxt(os.path.join(path_quad_2, 'mc_run_{}'.format(mc_run), 'scaling.dat'))
        # x_scaled = (x - mean) / std
        # n_quad_2_out = n_quad_2.n_beta(x_scaled.float()) ** 2
        #
        # #######
        #
        # n_cross = PredictorCross(architecture)
        # n_cross.load_state_dict(torch.load(path_nn_cross.format(mc_run)))
        #
        # mean, std = np.loadtxt(os.path.join(path_cross, 'mc_run_{}'.format(mc_run), 'scaling.dat'))
        # x_scaled = (x - mean) / std
        # n_cross_out = n_cross.n_gamma(x_scaled.float()) ** 2

    # r = 1 + c1 * n_lin_1_out + c2 * n_lin_2_out #+ c1 ** 2 * n_quad_1_out + c2 ** 2 * n_quad_2_out + c1 * c2 * n_cross_out

    r = 1 + cHW * n_lin_1_out + cHq3 * n_lin_2_out
    return r

def decision_function_nn(x, c, path_to_models, mc_run, lin=False, quad=False):
    """
    Computes the reconstructed decission function f(x, c)

    Parameters
    ----------
    x : torch.tensor, shape=(M, N)
        Kinematics feature vector with M instances of N kinematics, e.g. N =2 for
        the invariant mass and the rapidity.
    c : numpy.ndarray, shape=(M,)
        EFT point in M dimensions, e.g c = (cHW, cHq3)
    path_to_models: dict
        Path to the nn model root directory
    mc_run: int
        Monte Carlo replica number
    lin: bool, optional
        Set to False by default. Turn on for linear corrections.
    quad: bool, optional
        Set to False by default. Turn on for quadratic corrections.

    Returns
    -------
    f: numpy.ndarray, shape=(M,)
        Reconstructed decission function f for the events ``x``
    """

    ratio = likelihood_ratio_nn(x, c, path_to_models, mc_run, lin, quad)
    f = 1 / (1 + ratio)
    return f

def plot_heatmap(im, xlabel, ylabel, title, extent, bounds, cmap='GnBu'):
    """
    Plot and return a heatmap of ``im``

    Parameters
    ----------
    im: numpy.ndarray, shape=(M, N)
        Input array
    xlabel: str
    ylabel: str
    title: str
    extent: list
        boundaries of the heatmap, e.g. [x_0, x_1, y_1, y_2]
    bounds: list
        The boundaries of the discrete colourmap
    cmap: str
        colourmap to use, set to 'GnBu' by default

    Returns
    -------
    fig: `matplotlib.figure.Figure`
    """

    # discrete colorbar
    cmap_copy = copy.copy(mpl.cm.get_cmap(cmap))

    norm = mpl.colors.BoundaryNorm(bounds, cmap_copy.N, extend='both')

    cmap_copy.set_bad(color='gainsboro')

    # continious colormap

    # cmap = copy.copy(plt.get_cmap(cmap))
    # cmap.set_bad(color='white')
    # cmap.set_over("#FFAF33")
    # cmap.set_under("#FFAF33")

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(im, extent=extent,
              origin='lower', cmap=cmap_copy, aspect=(extent[1] - extent[0]) / (extent[-1] - extent[-2]), norm=norm)

    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap_copy), ax=ax)

    cbar.minorticks_on()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    return fig

def coeff_comp_rep(path_model, network_size, c1, c2):
    """
    Compares the EFT coefficient function of the individual replica stored at ``path_model`` with the truth.
    The ratio is plotted and returned as a matplotlib figure.

    Parameters
    ----------
    path_model: str
        Path to model replica
    network_size: list
        The architecture of the model, e.g.

        .. math::

            [n_i, 10, 15, 5, n_f],

        where :math:`n_i` and :math:`n_f` denote the number of input features and output target values respectively.

    c1: float
        Value of the 1st EFT coefficient used during training
    c2: float
        Value of the 2nd EFT coefficient used during training

    Returns
    -------
    `matplotlib.figure.Figure`
    """

    s = 14 ** 2
    epsilon = 1e-2
    mvh_min, mvh_max = mz + mh + epsilon, 2
    y_min, y_max = - np.log(np.sqrt(s) / mvh_min), np.log(np.sqrt(s) / mvh_min)

    x_spacing, y_spacing = 1e-2, 0.01
    mvh_span = np.arange(mvh_min, mvh_max, x_spacing)
    y_span = np.arange(y_min, y_max, y_spacing)

    mvh_grid, y_grid = np.meshgrid(mvh_span, y_span)
    grid = np.c_[mvh_grid.ravel(), y_grid.ravel()]
    grid_unscaled_tensor = torch.Tensor(grid)

    # truth
    if c1 != 0:
        ratio_truth_c1 = likelihood_ratio_truth(grid, np.array([10, 0]), lin=True)
        mask = ratio_truth_c1 == 0
        coeff_truth = np.ma.masked_where(mask, (ratio_truth_c1 - 1) / 10)
        coeff_truth = coeff_truth.reshape(mvh_grid.shape)
        title = r'$n_1^{\rm{truth}}/n_1^{\rm{NN}}$'
    elif c2 != 0:
        ratio_truth_c2 = likelihood_ratio_truth(grid, np.array([0, 10]), lin=True)
        mask = ratio_truth_c2 == 0
        coeff_truth = np.ma.masked_where(mask, (ratio_truth_c2 - 1) / 10)
        coeff_truth = coeff_truth.reshape(mvh_grid.shape)
        title = r'$n_2^{\rm{truth}}/n_2^{\rm{NN}}$'
    else:
        loggin.info("c1 and c2 cannot both be zero.")

    # models

    mean, std = np.loadtxt(os.path.join(path_model, 'scaling.dat'))
    loaded_model = quad_clas.PredictorLinear(network_size)
    network_path = os.path.join(path_model, 'trained_nn.pt')

    # load all the parameters into the trained network
    loaded_model.load_state_dict(torch.load(network_path))
    grid = (grid_unscaled_tensor - mean) / std

    coeff_nn = loaded_model.n_alpha(grid.float())
    coeff_nn = coeff_nn.view(mvh_grid.shape).detach().numpy()

    bounds = [0.95, 0.96, 0.97, 0.98, 0.99, 1.01, 1.02, 1.03, 1.04, 1.05]
    fig = plot_heatmap(coeff_truth / coeff_nn,
                       xlabel=r'$m_{ZH}\;\rm{[TeV]}$',
                       ylabel=r'$\rm{Rapidity}$',
                       title=title,
                       extent=[mvh_min, mvh_max, y_min, y_max],
                       cmap='seismic',
                       bounds=bounds)

    return fig

def coeff_comp(mc_reps, path_model, network_size, c1, c2, path_sm_data=None):
    """
    Compares the NN and true coefficient functions in the EFT expansion and plots their ratio and pull

    Parameters
    ----------
    mc_reps: int
        Number of replicas to include
    path_model: str
        Path to models, e.g. models/model_x/mc_run_{mc_run}
    network_size: list
        Architecture of the network
    c1: float
        Value of the 1st EFT coefficient used during training
    c2: float
        Value of the 2nd EFT coefficient used during training
    path_sm_data: str, optional
        Path to sm .npy event file which will be plotted on top of the heatmap

    Returns
    -------
    `matplotlib.figure.Figure`
        Heatmap of coefficient function ratio
    `matplotlib.figure.Figure`
        Heatmap of pull
    """
    s = 14 ** 2
    epsilon = 1e-2
    mvh_min, mvh_max = mz + mh + epsilon, 2
    y_min, y_max = - np.log(np.sqrt(s) / mvh_min), np.log(np.sqrt(s) / mvh_min)

    x_spacing, y_spacing = 1e-2, 0.01
    mvh_span = np.arange(mvh_min, mvh_max, x_spacing)
    y_span = np.arange(y_min, y_max, y_spacing)

    mvh_grid, y_grid = np.meshgrid(mvh_span, y_span)
    grid = np.c_[mvh_grid.ravel(), y_grid.ravel()]
    grid_unscaled_tensor = torch.Tensor(grid)

    # truth
    ratio_truth_c1 = likelihood_ratio_truth(grid, np.array([10, 0]), lin=True)
    ratio_truth_c2 = likelihood_ratio_truth(grid, np.array([0, 10]), lin=True)
    mask = ratio_truth_c1 == 0

    n_1_truth = np.ma.masked_where(mask, (ratio_truth_c1 - 1) / 10)
    n_1_truth = n_1_truth.reshape(mvh_grid.shape)

    n_2_truth = np.ma.masked_where(mask, (ratio_truth_c2 - 1) / 10)
    n_2_truth = n_2_truth.reshape(mvh_grid.shape)

    # models

    n_alphas = []
    for rep_nr in range(0, mc_reps):

        mean, std = np.loadtxt(os.path.join(path_model.format(mc_run=rep_nr), 'scaling.dat'))
        loaded_model = quad_clas.PredictorLinear(network_size)
        network_path = os.path.join(path_model.format(mc_run=rep_nr), 'trained_nn.pt')

        # load all the parameters into the trained network
        loaded_model.load_state_dict(torch.load(network_path))
        grid = (grid_unscaled_tensor - mean) / std

        n_alpha = loaded_model.n_alpha(grid.float())
        n_alpha = n_alpha.view(mvh_grid.shape).detach().numpy()

        n_alphas.append(n_alpha)

    n_alphas = np.array(n_alphas)
    n_alpha_median = np.percentile(n_alphas, 50, axis=0)
    n_alpha_high = np.percentile(n_alphas, 84, axis=0)
    n_alpha_low = np.percentile(n_alphas, 16, axis=0)
    n_alpha_unc = (n_alpha_high - n_alpha_low) / 2

    # visualise sm events
    if path_sm_data is not None:
        path_dict_sm = {0: path_sm_data}
        data_sm = quad_classifier_cluster.EventDataset(c=0,
                                                       n_features=2,
                                                       path_dict=path_dict_sm,
                                                       n_dat=500,
                                                       hypothesis=1)
        sm_events = data_sm.events.numpy()
    else:
        sm_events = None

    # median
    median_ratio = n_1_truth / n_alpha_median if c1 != 0 else n_2_truth / n_alpha_median
    title= r'$n_1^{\rm{truth}}/n_1^{\rm{NN}}\;\rm{(median)}$' if c1 != 0 else r'$n_2^{\rm{truth}}/n_2^{\rm{NN}}\;\rm{(median)}$'

    fig1 = plot_heatmap(median_ratio,
                        xlabel=r'$m_{ZH}\;\rm{[TeV]}$',
                        ylabel=r'$\rm{Rapidity}$',
                        title=title,
                        extent=[mvh_min, mvh_max, y_min, y_max],
                        cmap='seismic',
                        bounds=[0.95, 0.96, 0.97, 0.98, 0.99, 1.01, 1.02, 1.03, 1.04, 1.05])

    # pull
    pull = (n_1_truth - n_alpha_median) / n_alpha_unc if c1 != 0 else (n_2_truth - n_alpha_median) / n_alpha_unc

    fig2 = plot_heatmap(pull,
                        xlabel=r'$m_{ZH}\;\rm{[TeV]}$',
                        ylabel=r'$\rm{Rapidity}$',
                        title=r'$\rm{Pull}$',
                        extent=[mvh_min, mvh_max, y_min, y_max],
                        cmap='seismic',
                        bounds=np.linspace(-1.5, 1.5, 10))

    return fig1, fig2

def load_models(architecture, model_dir, model_nrs):
    """
    Load the pretrained models

    Parameters
    ----------
    architecture: list
        Arcitecture of the model
    model_dir:
        path to model directory up to mc_run (pass rep number as string format), e.g.
        /models/mc_run_{}
    model_nrs: iterable object
        An iterable that contains all the replicas that should be loaded

    Returns
    -------
    models: list
        List of loaded models
    """
    models = []
    for rep_nr in model_nrs:
        # load statistics of pretrained models
        mean, std = np.loadtxt(os.path.join(model_dir.format(mc_run=rep_nr), 'scaling.dat'))
        loaded_model = quad_clas.PredictorLinear(architecture)
        network_path = os.path.join(model_dir.format(mc_run=rep_nr), 'trained_nn.pt')

        # load all the parameters into the trained network and save
        loaded_model.load_state_dict(torch.load(network_path))
        models.append(loaded_model)

    return models

def point_by_point_comp(mc_reps, events, c, path_to_models, network_size, lin=True, quad=False):
    """
    Make a point by point comparison between the truth and the models

    Parameters
    ----------
    mc_reps: int
        Number of replicas to include
    events: numpy.ndarray, shape=(M, N)
        Kinematic feature vector with M instances of N kinematics, e.g. N =2 for
        the invariant mass and the rapidity.
    c: numpy.ndarray, shape=(M,)
        EFT point in M dimensions, e.g c = (cHW, cHq3)
    path_to_models: dict
        dictionary containing the paths to the trained models for each order in the eft expansion (linear, quadratic
        and cross terms)
    network_size: list
        Network architecture

    Returns
    -------
    `matplotlib.figure.Figure`
        Overview plot of all the replicas
    `matplotlib.figure.Figure`
        Plot of the median only
    """

    r_nn = []
    for mc_run in range(mc_reps):
        r_nn_rep = likelihood_ratio_nn(torch.Tensor(events), c, path_to_models, network_size, mc_run=mc_run,
                                       lin=lin, quad=quad)
        r_nn_rep = r_nn_rep.numpy().flatten()
        r_nn.append(r_nn_rep)
    tau_nn = np.log(r_nn)

    r_truth = likelihood_ratio_truth(events, c, lin=lin, quad=quad)
    tau_truth = np.log(r_truth)

    # overview plot for all replicas
    ncols = 5
    nrows = int(np.ceil(mc_reps/ncols))

    fig1 = plt.figure(figsize=(ncols * 4, nrows * 4))

    x = np.linspace(np.min(tau_truth) - 0.1, np.max(tau_truth) + 0.1, 100)
    for i in range(int(ncols * nrows)):
        plt.subplot(nrows, ncols, i + 1)
        plt.scatter(tau_truth, tau_nn[i, :], s=5, color='k')
        plt.plot(x, x, linestyle='dashed', color='grey')
        plt.xlim((np.min(x), np.max(x)))
        plt.ylim((np.min(x), np.max(x)))

    plt.tight_layout()

    # median
    fig2, ax = plt.subplots(figsize=(8, 8))
    x = np.linspace(np.min(tau_truth) - 0.1, np.max(tau_truth) + 0.1, 100)
    plt.scatter(tau_truth, np.median(tau_nn, axis=0), s=5, color='k')
    plt.plot(x, x, linestyle='dashed', color='grey')
    plt.xlabel(r'$\tau(x, c)^{\rm{truth}}$')
    plt.ylabel(r'$\tau(x, c)^{\rm{NN}}$')
    plt.xlim((np.min(x), np.max(x)))
    plt.ylim((np.min(x), np.max(x)))
    plt.tight_layout()

    return fig1, fig2

def make_predictions_1d(x, network_path, network_size, cHW, cHq3, mean, std,
                        path_lin_1=None,
                        path_lin_2=None,
                        path_quad_1=None,
                        path_quad_2=None):
    """

    Deprecated, to be removed in future versions

    """
    # Set up coordinates and compute f
    x_unscaled = torch.from_numpy(x)
    # x_unscaled = torch.cat((x_unscaled, torch.zeros(len(x_unscaled), 1)), dim=1)
    x = (x_unscaled - mean) / std  # rescale the inputs

    # Be careful to use the same network architecture as during training

    if path_quad_1 is None:
        loaded_model = quad_clas.PredictorLinear(network_size)
        loaded_model.load_state_dict(torch.load(network_path))
        f_pred = loaded_model.forward(x.float(), cHW + cHq3)
    elif path_quad_2 is None:
        loaded_model = quad_clas.PredictorQuadratic(network_size)
        loaded_model.load_state_dict(torch.load(network_path))
        f_pred = loaded_model.forward(x.float(), cHW ** 2 + cHq3 ** 2, path_lin_1)
    else:
        loaded_model = quad_clas.PredictorCross(network_size)
        loaded_model.load_state_dict(torch.load(network_path))
        f_pred = loaded_model.forward(x.float(), cHW, cHq3, path_lin_1, path_lin_2, path_quad_1, path_quad_2)

    f_pred = f_pred.view(-1).detach().numpy()

    return f_pred

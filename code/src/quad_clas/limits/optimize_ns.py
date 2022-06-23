import pymultinest
import json
import sys
import numpy as np
import time
import os
import pandas as pd
from pathlib import Path
import shutil

import quad_clas.analyse.analyse as analyse
import quad_clas.core.th_predictions as theory_pred
from quad_clas.core.truth import vh_prod
from quad_clas.preproc import constants

from quad_clas.core.th_predictions import TheoryPred

mz = constants.mz
mh = constants.mh

# fix randomness
np.random.seed(0)

class Optimize:

    """
    Parameters
    ----------
        config : dict
            configuration dictionary
        observed_data: numpy.ndarray()
            Observed events (i.e. under the SM)
        theory_pred: TheoryPred
            instance of TheoryPred that contains the theory predictions
    """

    def __init__(self, config, rep=None):

        self.config = config.copy()
        self.rep = rep
        self.param_names = {}

        if self.rep is not None:
            self.config["results_path"] = os.path.join(self.config["results_path"], "r_{}".format(self.rep))
        Path(self.config["results_path"]).mkdir(parents=True, exist_ok=True)

        # store input card as reference
        with open(os.path.join(self.config['results_path'], 'input_card.json'), 'w') as json_data:
            json.dump(self.config, json_data)

        if "order" in self.config.keys():
            self.order = self.config["order"]

        if "process" in self.config.keys():
            self.process = self.config["process"]
        if "mode" in self.config.keys():
            self.mode = self.config["mode"]
        else:
            print(
                "No mode (mode) selected, please specify one in the input card. Aborting."
            )
            sys.exit()

        if "path_to_theory_pred" in self.config.keys():
            self.path_to_theory_pred = self.config["path_to_theory_pred"]
        else:
            print(
                "Parameters names (parameters) not set in the input card. Aborting."
            )
            sys.exit()

        if "nlive" in self.config.keys():
            self.live_points = self.config["nlive"]
        else:
            print(
                "Number of live points (nlive) not set in the input card. Using default: 500"
            )
            self.live_points = 500

        if "max_val" in self.config.keys():
            self.max_val = self.config["max_val"]
        if "min_val" in self.config.keys():
            self.min_val = self.config["min_val"]

        if "lumi" in self.config.keys():
            self.lumi = self.config["lumi"]
        else:
            print(
                "Luminosity (lumi) not set in the input card. Using default: 5e3 pb^-1"
            )

        if self.mode == 'binned':
            if "bins" in self.config.keys():
                self.bins = self.config["bins"]
            else:
                print(
                    "No binning (bins) specified. Please set in the in the input card. Aborting."
                )
                sys.exit()
            if "kinematic" in self.config.keys():
                self.kinematic = self.config["kinematic"]
            else:
                print(
                    "No bin variable (kinematic) specified. Please set in the in the input card. Aborting."
                )
                sys.exit()
        elif self.mode == "nn":
            if "path_to_models" in self.config.keys():
                self.path_to_models = self.config["path_to_models"]
                self.nn_analyser = analyse.Analyse(self.path_to_models)
            else:
                print(
                    "No path tot model (path_to_models) specified. Please set in the in the input card. Aborting."
                )
                sys.exit()

            self.bins = None
            self.kinematic = None
        else:  # truth case
            self.bins = None
            self.kinematic = None

        self.th_pred = theory_pred.TheoryPred(self.path_to_theory_pred,
                                         kinematic=self.kinematic,
                                         bins=self.bins)

        # nr of dof
        self.n_params = max(len(self.th_pred.th_dict['lin']), len(self.th_pred.th_dict['quad']))

        # load dataset (pseudo data)
        sm_data_path = self.config['observed_data_path']
        sm_data, _ = analyse.Analyse.load_events(sm_data_path)

        # construct observed dataset
        xsec_sm_tot = np.sum(self.th_pred.th_dict['sm']) # sum over bins
        nu_tot_sm = xsec_sm_tot * config['lumi']
        n_tot_sm = np.random.poisson(nu_tot_sm, 1)

        self.observed_data = sm_data.sample(int(n_tot_sm), random_state=1)

        if self.mode == "nn":
            self.nn_models = self.nn_analyser.evaluate_models(self.observed_data)

        if self.mode == "truth":
            self.dsigma_dx_sm, self.dsigma_dx_eft = theory_pred.compute_diff_coefficients(self.observed_data, self.process)
        elif self.mode == "binned":
            self.n_i, _ = np.histogram(self.observed_data[self.kinematic].values, self.bins)

    def my_prior(self, cube):
        """
        Construct prior volume

        Parameters
        ----------
        cube: numpy.ndarray, shape=(M,)
            unit hypercube of dim M

        Returns
        -------
        cube: numpy.ndarray
            hypercube prior
        """
        for i in range(self.n_params):
            cube[i] = cube[i] * (self.max_val - self.min_val) + self.min_val

        return cube

    def log_like_nn(self, cube):

        sigma = self.th_pred.th_dict['sm']

        # convert cube to df
        for i, c_name in enumerate(self.th_pred.th_dict['lin'].keys()):
            self.param_names[c_name] = cube[i]

        for i, (_, sigma_i) in enumerate(self.th_pred.th_dict['lin'].items()):
            sigma += cube[i] * sigma_i

        for i, (_, sigma_i) in enumerate(self.th_pred.th_dict['quad'].items()):
            sigma += cube[i] ** 2 * sigma_i


        # sigma = theory_pred_total['sm'] + theory_pred_total[self.parameters] @ cube

        nu = sigma * self.lumi

        ratio = self.nn_analyser.likelihood_ratio_nn(self.observed_data, self.param_names, models_evaluated=self.nn_models)
        log_r = np.log(ratio)
        log_r_med = np.median(log_r, axis=0) # or take median of replicas before computing r?

        log_likelihood = -nu + np.sum(log_r_med)

        return log_likelihood

    def log_like_truth(self, cube):

        theory_pred_total = self.theory_pred.sum(axis=1)

        quad_idx = [i for i, (index, _) in enumerate(theory_pred_total.items()) if '*' in index]

        if self.HOcorrections:
            sigma = theory_pred_total['sm'] + theory_pred_total[self.parameters] @ cube + theory_pred_total.iloc[quad_idx] @ (cube ** 2)
            dsigma_dx = self.dsigma_dx_sm + self.dsigma_dx_eft['lin'].T @ cube + self.dsigma_dx_eft['quad'].T @ (
                        cube ** 2)
        else:
            sigma = theory_pred_total['sm'] + theory_pred_total[self.parameters] @ cube
            dsigma_dx = self.dsigma_dx_sm + self.dsigma_dx_eft['lin'].T @ cube

        nu = sigma * self.lumi

        log_likelihood = -nu + np.sum(np.log(dsigma_dx))

        return log_likelihood

    def log_like_binned(self, cube):

        quad_idx = [i for i, (index, _) in enumerate(self.theory_pred.iterrows()) if '*' in index]

        if self.HOcorrections:
            sigma_i = self.theory_pred.loc['sm'] + self.theory_pred.loc[self.parameters].T @ cube + self.theory_pred.iloc[quad_idx].T @ (cube ** 2)
        else:
            sigma_i = self.theory_pred.loc['sm'] + self.theory_pred.loc[self.parameters].T @ cube

        nu_i = sigma_i * self.lumi
        log_l_i = self.n_i * np.log(nu_i) - nu_i

        return log_l_i.sum()


    def run_sampling(self):
        """Run the minimisation with Nested Sampling"""

        # Prefix for results
        prefix = os.path.join(self.config["results_path"], "1k-")

        t1 = time.perf_counter()

        if self.mode == "nn":
            log_likelihood = self.log_like_nn
        elif self.mode == "truth":
            log_likelihood = self.log_like_truth
        elif self.mode == "binned":
            log_likelihood = self.log_like_binned

        result = pymultinest.solve(LogLikelihood=log_likelihood,
                                   Prior=self.my_prior,
                                   n_dims=self.n_params,
                                   outputfiles_basename=prefix,
                                   verbose=True,
                                   n_live_points=self.live_points,
                                   const_efficiency_mode=False,
                                   resume=False,
                                   importance_nested_sampling=True
                                   )

        t2 = time.perf_counter()

        print("Time = ", (t2 - t1) / 60.0)

        # export the posterior samples to json
        self.save(result)

        # remove ns raw output
        self.clean()

    def clean(self):
        """ Remove raw NS output if you want to keep raw output, don't call this method"""

        filelist = [
            f for f in os.listdir(self.config["results_path"]) if f.startswith("1k-")
        ]
        for f in filelist:
            if f in os.listdir(self.config["results_path"]):
                os.remove(os.path.join(self.config["results_path"], f))

    def save(self, result):
        """
        Save NS replicas to json inside a dictionary:
        {coeff: [replicas values]}
        Parameters
        ----------
            result : dict
                result dictionary
        """

        vals = {}
        for i, (c, samples) in enumerate(zip(self.param_names.keys(), result['samples'].T)):
            vals[c] = samples.tolist()
        with open(os.path.join(self.config['results_path'], 'posterior.json'), "w") as f:
            json.dump(vals, f)







# Reweighting within ML4EFT
### Wolf Gautier for *Programmeerproject*, University of Amsterdam
Modern particle physics tries to obtain theory-confirming results from the very edges of what is experimentally obtainable. Somewhat counterintuïtively, most of the data that is used to do so is presented in binned form, which means any theory fits performed using it are subject to the information loss that is inherent to presenting data in binned form. One approach to mitigating this information loss, thus allowing statistically more significant conclusions to be drawn from the same data, is to use deep neural networks as a way to parameterise likelihood ratios. Bounds on theoretical coefficient values can then be statistically inferred from the trained networks, for example using nested sampling. This approach works on small-scale benchmarks, but quickly becomes computationally unfeasible as the scale increases; the number of simulated datasets that have to be generated scales quadratically with the number of coefficients that are included in a fit. 

The code under the *reweighting*-branch of this ML4EFT fork contains an implementation of event reweighting within the ML4EFT framework. Specifically, the file 'core/classifier.py' was adjusted and partially reworked in order to accept reweighting functionality. Reweighting here implies that instead of generating a dataset per coefficient configuration, the user generates one dataset containing $n_{coefficients}$ weight values per event, effectively reducing the simulation computation scaling with the number of coefficients from $O(n^2)$ to $O(1)$. A model can now be trained on the same dataset but with different event weights, instead of on different datasets. This brings the ML4EFT framework one step closer to being applicable to global particle physics fits, for example on the SMEFT. The execution of a fit now becomes for a SMEFT fit as simple as;


```
coeffs = ['ctGRe', (...), 'ctU']
for coefficient in coeffs:
	fitter = classifier.Fitter(<settings>)
```

The ML4EFT framework is made available via the [Python Package Index](https://pypi.org/project/ml4eft/) (pip) and can be installed directly 
by running

```shell
pip install ml4eft
```

or alternatively the code can be downloaded from this public GitHub repository, and then installed by running

```shell
cd code
pip install -e .
```  
To work with the reweighting approach, the reweighting branch should be used.

The framework is documented on a dedicated website https://lhcfitnikhef.github.io/ML4EFT, where, in addition, one can find a self-standing tutorial (which can also be run in Google Colab) where the user is guided step by step in how unbinned multivariate observables can be constructed given a choice of EFT coefficients and of final-state kinematic features.

## Acknowledgements
A special thanks to Jaco ter Hoeve for allowing me to contribute to such ongoing research, and for guiding me through the process.
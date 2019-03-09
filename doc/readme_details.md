## Details

The default binning algorithm uses a [binary density estimation tree](shmistogram/det/__init__.py) to iteratively split the data into smaller bins. The split location (within a bin/leaf) maximizes the improvement in the deviance (i.e. in-sample negative log likelihood) subject to a minimum-points-per-leaf constraint. This minimum currently defaults to 3. 

We choose the bin to split on as the bin for which splitting leads to the greatest improvement in deviance. Splits proceed as long as the deviance improvement exceeds the number of leaves. This approach is inspired by the Akaike information criterion (AIC), although this may be an abuse of the criterion in the sense that we're using it as part of a greedy iterative procedure instead of using it to compare fully-formed models. 

## Related work

More on density estimation trees, see
- [density estimation trees](https://mlpack.org/papers/det.pdf) 
such as [this](https://gitlab.cern.ch/landerli/density-estimation-trees) or
- [distribution element trees](https://arxiv.org/pdf/1610.00345.pdf) such as 
[detpack](https://github.com/cran/detpack/blob/master/R/det1.R). Interestingly, calling `det1(x, mode=1)` on data x also produces a variable bin-width histogram.

[Bayesian block representations](https://arxiv.org/pdf/1207.5578.pdf) are worth a closer look. See for example Figure 7 and several following it.

## Disclaimer

This repo is young, currently has no unit tests, and should be expected to change substantially. Use with caution.

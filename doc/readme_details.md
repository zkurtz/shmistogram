
## Future work

Our binning algorithm is based on several
ad hoc heuristics. It is neither particularly
scalable nor statistically efficient. In future
work we'll likely replace this with 
something like
- [density estimation trees](https://mlpack.org/papers/det.pdf) 
such as [this](https://gitlab.cern.ch/landerli/density-estimation-trees) or
- [distribution element trees](https://arxiv.org/pdf/1610.00345.pdf) such as 
[detpack](https://github.com/cran/detpack/blob/master/R/det1.R). Specifically, 
calling `det1(x, mode=1)` on data x produces a variable bin-width histogram.


## Disclaimer

This repo is young, currently has no unit tests, and should be expected to change
substantially. Use with caution.

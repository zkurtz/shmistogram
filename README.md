# shmistogram

The shmistogram is a better histogram. Key differences include

- estimating density with better accuracy and fewer bins than a histogram 
by hierarchically grouping points into variable-width bins
- emphasizing singular modalities (i.e. point masses) with a separate multinomial distribution

Functionality is currently split across two packages. The python shmistogram module
currently performs all binning and tabulation computations. The R package
uses reticulate to access the python module as a back-end and offers a plotting function.

## Installation

Requirements: R 3.5.2+ and python 3.6+

Clone this repo and do `python setup.py install` to install the python module. Test your installation
by running [demo.py](demo/demo.py).

Install the R package from github as 
`devtools::install_github("zkurtz/shmistogram/R-package")`. Test your installation by compiling
[demo.Rmd](demo/demo.Rmd).

Examples
--------

### Mixed data types

A shmistogram highlights point masses that may occur in a continuous variable, explicitly decomposing the distribution into a mixture of a multinomial and a piecewise uniform distribution. Such point masses are quite common:

-   inconsistent rounding any continuous variable can introduce a mixture of point masses and relatively continuous observations
-   "age of earning first driver's license" plausibly has structural modes at the legal minimum (which may vary by state) and otherwise vary continuously

Let's simulate a uniform distribution mixed with two point masses and a couple missing observations:

``` r
set.seed(1)
unif = runif(n=100, min=-10, max=100)
multi = c(rep(0, 20), rep(42, 10), rep(NA, 2))
data = c(unif, multi)
par(mfrow = c(1, 2))
hist(data, border=NA, col='grey', main = 'Histogram')
shmistogram::shmistogram(data)
```

![](demo/demo_files/figure-markdown_github/unnamed-chunk-1-1.png)

The histogram obscures the point masses somewhat. By contrast, the shmistogram highlights the modes using red line segments, and also visualizes the fraction of the data that is missing.

### Variable bin width

The shmistogram's agglomerative binning produces a parsimonious density estimate with adaptive bin width:

``` r
set.seed(0)
data = c(
    rnorm(2000, mean=0, sd=10),
    rnorm(500, mean = 4, sd = 0.5)
)
par(mfrow = c(1, 2))
hist(data, 50, border=NA, col='grey', main = 'Histogram')
shmistogram::shmistogram(data)
```

![](demo/demo_files/figure-markdown_github/unnamed-chunk-2-1.png)

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

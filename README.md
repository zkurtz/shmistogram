[![Build Status](https://travis-ci.org/zkurtz/shmistogram.svg?branch=master)](https://travis-ci.org/zkurtz/shmistogram)
# shmistogram

The shmistogram is a better histogram. Key differences include

- emphasizing singular modalities (i.e. point masses) with a separate multinomial distribution
- estimating density with better accuracy and fewer bins than a histogram 
by hierarchically grouping points into variable-width bins

Suppose we simulate draws from a triangular distribution (the 'crowd'), 
supplemented with a couple of mode points ('loners'), and some null values:

```python
from matplotlib import pyplot as plt
import numpy as np
import shmistogram as sh

# Simulate a mixture of a uniform distribution mixed with a few point masses
np.random.seed(0)
crowd = np.random.triangular(-10, -10, 70, size=500)
loners = np.array([0]*40 + [42]*20)
null = np.array([np.nan]*100)
data = np.concatenate((crowd, loners, null))

fig, axes = plt.subplots(1, 2)

# Build a standard histogram with matplotlib.pyplot.hist defaults
sh.plot.standard_histogram(data[~np.isnan(data)], ax=axes[0], name='mixed data')

# Build a shmistogram
shm = sh.Shmistogram(data)
shm.plot(ax=axes[1], name='mixed data')

fig.tight_layout()
```

![](doc/chunks/mixed.png?raw=true "title")

The histogram obscures the point masses somewhat and says nothing about missing values. 
By contrast, the shmistogram uses red line segments to emphasize the point masses, and
the legend bar highlights the relative portions of the data in the crowd versus
the point masses versus the null values.

## Installation

- install python 3.6+
- `pip install git+https://github.com/zkurtz/shmistogram.git#egg=shmistogram`
- test your installation by running [demo.py](demo/demo.py)


## Details

### Default behavior

Given a 1-D array of numeric (or `np.nan`) values `data`, the shmistogram 
`shmistogram.Shmistogram(data)` 
- counts every unique value
- splits the data into as many as 3 subsets:
    - `np.nan`
    - "Loners" are points with a count above the threshold set by the
    argument `loner_min_count`. Shmistogram sets this dynamically by default
    as a somewhat log-linear function of `len(data)`. With 100 points, 
    the threshold is 8; with 100,000 it is 18.
    - The "crowd" is all remaining points.
- bins the "crowd" using a density estimation tree.

Calling the plot method on the resulting object displays all components
of the distribution on a single figure.

### Why shmistogram?

#### Use case 1: Exploratory data analysis

A shmistogram can be more informative than a histogram by separating 
continous and discrete variation:
- inconsistent rounding any continuous variable can induce a mixture of point masses and relatively continuous observations
- "age of earning first driver's license" plausibly has structural modes at the 
legal minimum (which may vary by state) and otherwise vary continuously

#### Use case 2: Scalable, generative density estimation

The shmistogram scales approximately as O(n log(n)) with default settings 
(see [speed_testing.ipynb](demo/speed_testing.ipynb)). 
The resulting density model is easy to sample from, as a mixture of 
a piecewise uniform 
distribution and a multinomial distribution. Such a simple
estimator works well as one of the required inputs of the CADE density 
estimation algorithm for high dimensional 
and mixed continuous/categorical data (see [pydens](https://github.com/zkurtz/pydens)).

The shmistogram's adaptive bin width leads to a higher-fidelity representation of 
complicated distributions without substantially increasing the number of bins.
This is not a new idea, and shmistogram wraps multiple binning
methods that the user can choose from. See 
[binning_methods.ipynb](demo/binning_methods.ipynb) for details.

## Binning

The default binning algorithm uses a [binary density estimation tree](shmistogram/det/__init__.py) 
to iteratively split the data into smaller bins. The split location (within a bin/leaf) 
maximizes a penalized improvement in the deviance (i.e. in-sample negative log likelihood).
The penalty reflects
- a hard `min_data_in_leaf` constraint. This minimum currently defaults to 3
- a soft penalty on bins with few observations

We choose the bin to split on as the bin for which splitting produces the greatest 
penalized improvement. Splits proceed as long as the deviance improvement exceeds 
the number of leaves. This approach is inspired by the Akaike information criterion 
(AIC), although this may be an abuse of the criterion in the sense that we're using 
it as part of a greedy iterative procedure instead of using it to compare fully-formed models. 

The variable-width binning algorithms of 
[bayesian block representations](https://arxiv.org/pdf/1207.5578.pdf) 
provide an alternative to our default binning algorithm. See [demo](demo/bayesian_blocks.ipynb) for
an example. See also
[Python Perambulations](https://jakevdp.github.io/blog/2012/09/12/dynamic-programming-in-python/) 
for a light conceptual introduction to Bayesian blocks.

## Wishlist

**Clarify the objective:** There is a tension between optimizing a binner for 
(a) visualization purposes, such as avoiding tall narrow bins to minimize 
white space, or adjusting the average bin width to tell a particular story 
and (b) minimizing a formal measure of estimation accuracy such as the 
expectation of deviance 
(taken over future observations from the true distribution). We should
offer guidance on which binning method tends to be most effective
for each of these goals.

**Optimize speed** for the default method. Scalability is a big part of the
motivation for such a simple model, but the current implementation is
far from optimal.

**Compare/contrast/harmonize** our binning methods with the literature:
- [density estimation trees](https://mlpack.org/papers/det.pdf) 
such as [this](https://gitlab.cern.ch/landerli/density-estimation-trees)
- [distribution element trees](https://arxiv.org/pdf/1610.00345.pdf) such as 
[detpack](https://github.com/cran/detpack/blob/master/R/det1.R). See
[detpack_example.R](demo/detpack_example.R) for a simple variable-width binner.
- [Efficient Density Estimation via Piecewise Polynomial 
Approximation](https://arxiv.org/pdf/1305.3207.pdf).


## Disclaimer

This repo is young, has practically no unit tests, and should be expected to change substantially. Use with caution.

## License

This project is licensed under the terms of the MIT license. See LICENSE for additional details.
[![Build Status](https://travis-ci.org/zkurtz/shmistogram.svg?branch=master)](https://travis-ci.org/zkurtz/shmistogram)
# shmistogram

The shmistogram is a better histogram. Key differences include

- emphasizing singular modalities (i.e. point masses) with a separate multinomial distribution
- estimating density with better accuracy and fewer bins than a histogram 
by hierarchically grouping points into variable-width bins

Functionality is split across two packages. The python shmistogram module performs all binning and 
tabulation computations. The R package offers a visualization, using reticulate to access the python back-end.

[![Build Status](https://travis-ci.org/zkurtz/shmistogram.svg?branch=master)](https://travis-ci.org/zkurtz/shmistogram)
# shmistogram

The shmistogram is a better histogram. Key differences include

- estimating density with better accuracy and fewer bins than a histogram 
by hierarchically grouping points into variable-width bins
- emphasizing singular modalities (i.e. point masses) with a separate multinomial distribution

Functionality is split across two packages. The python shmistogram module performs all binning and 
tabulation computations. The R package offers plotting functionality while using reticulate to access the python back-end.

## Installation

Python backend (everything except graphics):
- install python 3.6+
- `pip install git+https://github.com/zkurtz/shmistogram.git#egg=shmistogram`
- test your installation by running [demo.py](demo/demo.py)

R graphics front end:
- install R 3.5.2+
- then do
    ```
    install.packages("devtools")
    library(devtools)
    devtools::install_github("zkurtz/shmistogram/R-package")
    ```
- Test your installation by compiling [demo.Rmd](demo/demo.Rmd).

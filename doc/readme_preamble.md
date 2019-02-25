# shmistogram

The shmistogram is a better histogram. Key differences include

- estimating density with better accuracy and fewer bins than a histogram 
by agglomerating points into variable-width bins
- emphasizing singular modalities (i.e. point masses) with a separate multinomial distribution

Functionality is currently split across two packages. The python shmistogram module
currently performs all binning and tabulation computations. The R package
uses reticulate to access the python module as a back-end and offers a plotting function.

## Installation

Requirements: R 3.5.2+ and python 3.6+

Clone this repo and do `python setup.py install` to install the python module.

Install the R package from github as 
`devtools::install_github("zkurtz/shmistogram/R-package")`

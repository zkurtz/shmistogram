
# Detpack is a potential replacement for our binning algorithm:

set.seed(0)
data = c(
    rnorm(2000, mean=0, sd=10),
    rnorm(500, mean = 4, sd = 0.5)
)

library(detpack) # https://github.com/cran/detpack
det1(data, mode=1)

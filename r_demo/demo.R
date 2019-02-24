library(shmistogram)
# If your python installation of python shmistogram is 
#   in a conda environment 'shmist' (for example), you may need to 
#   add a line such as
#   `reticulate::use_condaenv('shmist')` 

## Mixed data types
set.seed(0)
unif = runif(n=100, min=-10, max=100)
multi = c(rep(0, 20), rep(42, 10), rep(NA, 2))
data = c(unif, multi)
shmistogram(data)

## Dens distribution mixture
set.seed(0)
data = c(
    rnorm(2000, mean=0, sd=10),
    rnorm(1000, mean = 2, sd = 0.5)
)
pshm = pyshmistogram$Shmistogram(data)
hist(data, 50)

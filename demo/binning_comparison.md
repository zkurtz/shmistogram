
Examples
--------

### Cauchy Mixture

``` r
library(shmistogram)
py = reticulate::import("shmistogram")
data = py$simulations$cauchy_mixture()
par(mfrow = c(2,1))
shm = shmistogram(
    data, 
    params=list(
        binning_method='density_tree',
        binning_params=list(lambda=0.5, verbose=TRUE)
    ),
    plotting_params=list(main="Density tree")
)
shm = shmistogram(data, 
    params=list(binning_method='bayesian_blocks'),
    plotting_params=list(main="Bayesian blocks")
)
```

![](binning_comparison_files/figure-markdown_github/unnamed-chunk-1-1.png)

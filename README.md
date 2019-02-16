# shmistogram

The shmistogram is a better histogram. Key differences include

- handling peak mode points with a separate multinomial distribution to reveal 
modes that would otherwise be obscured by membership in large bin in a histogram
- achieve better density-estimation accuracy with fewer bins than a histogram 
by using an agglomerative hierarchical clustering routine to build variable-width bins

THIS REPO IS EARLY CONCEPT PHASE ... `demo.ipynb` or `demo.Rmd` COMING SOON

## Details

Our binning algorithm is based on several
ad hoc heuristics. It is neither particularly
scalable nor statistically efficient. In future
work we'll likely replace this with 
an implementation of 
[density estimation trees](https://mlpack.org/papers/det.pdf) or
[distribution element trees](https://arxiv.org/pdf/1610.00345.pdf).

### Disclaimer

This repo is young, currently has no unit tests, and should be expected to change
substantially. Use with caution.

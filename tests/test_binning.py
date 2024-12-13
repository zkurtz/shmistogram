import matplotlib

matplotlib.use("Agg")
import numpy as np

import shmistogram as shm


def test_version():
    assert "__version__" in dir(shm)


def test_det_n_bin():
    """Control the number of bins for a density estimation tree

    We test an edge case here by building a small tree with a single observation
    in each bin
    """
    N = 10
    np.random.seed(0)
    data = shm.simulations.cauchy_mixture(n=N, truncate=False)
    assert data.shape[0] == N
    binner = shm.binners.DensityEstimationTree(params={"n_bins": N, "min_data_in_leaf": 1})
    det = shm.Shmistogram(data, binner=binner)
    assert det.bins.shape[0] == N

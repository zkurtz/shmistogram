import pandas as pd

import shmistogram as shm
from shmistogram.binners.det import DensityEstimationTree
from shmistogram.simulations.univariate import cauchy_mixture


def test_version():
    assert "__version__" in dir(shm)


def test_det_n_bin():
    """Control the number of bins for a density estimation tree

    We test an edge case here by building a small tree with a single observation
    in each bin
    """
    size = 30
    num_bins = 4
    data = cauchy_mixture(size=size, truncate=False, seed=0)
    assert data.shape[0] == size
    binner = DensityEstimationTree(params={"n_bins": num_bins, "min_data_in_leaf": 1})
    det = shm.Shmistogram(data, binner=binner)
    expected_bins = pd.DataFrame(
        {
            "lb": {0: -96.98579895056032, 1: -6.778614916916878, 2: 4.877996182341204, 3: 16.936340107278813},
            "ub": {0: -6.778614916916878, 1: 4.877996182341204, 2: 16.936340107278813, 3: 175.1260262642947},
            "freq": {0: 5, 1: 22, 2: 1, 3: 2},
            "width": {0: 90.20718403364344, 1: 11.656611099258082, 2: 12.05834392493761, 3: 158.18968615701587},
            "rate": {0: 0.05542795791225688, 1: 1.887340995823413, 2: 0.0829301275718236, 3: 0.012643049294723555},
        }
    )
    pd.testing.assert_frame_equal(det.bins, expected_bins)

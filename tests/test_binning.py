import shmistogram as shm
import numpy as np

def test_version():
    assert '__version__' in dir(shm)

def test_det_n_bin():
    ''' Control the number of bins for a density estimation tree

    We test an edge case here by building a small tree with a single observation
    in each bin
    '''
    N = 10
    np.random.seed(0)
    data = shm.simulations.cauchy_mixture(n=N, truncate=False)
    assert data.shape[0] == N
    det = shm.Shmistogram(data,
        binning_method='density_tree',
        binning_params={
            'n_bins': N,
            'min_data_in_leaf': 1
        }
    )
    assert det.bins.shape[0] == N

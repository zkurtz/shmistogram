from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from time import time

from .agglomerate import Agglomerator
from .bayesblocks import BayesianBlocks
from .det import DensityEstimationTree
from ..shmistogram import Shmistogram

class ScalabilityTesting:
    def __init__(self, data_sets, bin_methods):
        self.datas = data_sets
        self.bin_methods = bin_methods
        self.build()

    def get_binner_method(self, method):
        if method == 'det':
            return None
        elif method == 'bayesblocks':
            return BayesianBlocks()

    def build_one(self, data, method):
        t0 = time()
        shm = Shmistogram(data, binner=self.get_binner_method(method))
        return {
            'shm': shm,
            'time': time() - t0,
            'n_bins': shm.bins.shape[0]
        }

    def build(self):
        self.trees = {
            m: [self.build_one(data, m) for idx, data in self.datas.items()]
            for m in self.bin_methods
        }

    def metrics(self, method):
        return pd.DataFrame({
            'k': range(1, len(self.datas) + 1),
            'time': [shm['time'] for shm in self.trees[method]],
            'n_bins': [shm['n_bins'] for shm in self.trees[method]]
        })

    def plot(self, target, log=False):
        ax = plt.subplot()
        for m in self.bin_methods:
            df = self.metrics(m).rename({target: m}, axis=1)
            if log:
                df[m] = np.log(df[m])
            df.plot(x='k', y=m, ax=ax)
            ax.set_xlabel('Log10 of sample size')
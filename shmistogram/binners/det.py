"""Density estimation tree (DET) for univariate data."""

import warnings

import numpy as np
import pandas as pd
from pandahandler import indexes

from shmistogram.names import COUNT, VALUE


def isclose(a, b, rel_tol=1e-12, abs_tol=0.0):
    """Check if two numbers are close."""
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def _search_split(df, lb=None, ub=None, min_data_in_leaf=None):
    """Search for an optimal split (index and threshold value).

    Args:
        df: A DataFrame with columns 'value' and 'n_obs'
        lb: A lower bound on the domain of the density function
        ub: An upper bound on the domain of the density function
        min_data_in_leaf: The minimum number of data points in each leaf node

    Returns:
        A dictionary with keys 'idx', 'threshold', and 'divergence_improvement'
    """
    n = df[COUNT].sum()  # df.shape[0]
    assert n > 1
    n_ob = df[COUNT].sum()
    xmin = df[VALUE].iloc[0]
    xmax = df[VALUE].iloc[-1]
    xrg = xmax - xmin
    lb = xmin if (lb is None) else lb
    ub = xmax if (ub is None) else ub
    if xmin - lb < 1e-13:
        lmar = (df[COUNT].iloc[0] / n) * xrg
        lb = xmin - lmar
    else:
        lmar = xmin - lb
        assert lmar > 0
    if ub - xmax < 1e-13:
        umar = (df[COUNT].iloc[-1] / n) * xrg
        ub = xmax + umar
    else:
        umar = ub - xmax
        assert umar > 0
    margin = lmar + umar
    mxrg = xrg + margin
    assert isclose(mxrg, ub - lb)
    null_dens = 1 / mxrg
    # Counts to the left and right of each potential split
    df["left_n"] = df[COUNT].cumsum()
    df["right_n"] = df.left_n.iloc[-1] - df.left_n.to_numpy()
    if min_data_in_leaf is not None:
        m = min_data_in_leaf
        assert m >= 1
        df = df[df.left_n >= m]
        df = df[df.right_n + 1 >= m]
        if df.shape[0] < 2:
            return {
                "deviance_improvement": -1,  # negative improvment ensures no more splits
                "idx": -1,
                VALUE: -1.0,
                "n": n_ob,
            }
    # Drop the final row, as splitting on it would imply a right-leaf size of 0
    value = df[VALUE]
    df = df.iloc[:-1]
    # Width of bin to the left, right
    df["left_w"] = df[VALUE] - lb
    df["right_w"] = ub - df[VALUE]
    # Density of bin to the left, right
    df["left_ldens"] = np.log(df.left_n.to_numpy() / (n * df.left_w.to_numpy()))
    df["right_ldens"] = np.log(df.right_n.to_numpy() / (n * df.right_w.to_numpy()))
    # Joint negative log likelihood to the left, right
    df["left_neg_ll"] = -df.left_n.to_numpy() * df.left_ldens.to_numpy()
    df["right_neg_ll"] = -df.right_n.to_numpy() * df.right_ldens.to_numpy()
    # Total negative log-likelihood; if the total is much less than the global
    #   (null) for a particular split, then the split is worthwhile
    df["neg_ll"] = df.left_neg_ll + df.right_neg_ll
    # null negative log likelihood
    nnll = -n_ob * np.log(null_dens)
    assert nnll >= df.neg_ll.max() - 1e-12
    n_min = df[["left_n", "right_n"]].min(axis=1)
    adj_neg_ll = df.neg_ll * (1 + 0.05 * np.exp(-n_min / 10))
    idx = adj_neg_ll.idxmin()
    value = (value.loc[idx] + value.loc[idx + 1]) / 2
    bestll = adj_neg_ll.loc[idx]
    di = nnll - bestll
    assert di > -np.inf
    assert di < np.inf
    ret = {
        "deviance_improvement": di,
        "idx": int(
            idx + 1
        ),  # plus 1 because we want df.iloc[:idx] to include the original idx (to create the left leaf)
        VALUE: value,
        #'n_min': min(df.loc[idx].left_n, df.loc[idx].right_n),
        "n": n_ob,
    }
    return ret


class Node:
    """Node in a binary tree for density estimation."""

    def __init__(self, lb, ub):
        """Initialize the node.

        :param lb: (dict) of form {'idx': <int>, 'value': <float>}
        :param ub: (dict) of form {'idx': <int>, 'value': <float>}
        #:param neighbors: (dict) of form {'left': <Node>, 'right', <Node>
        """
        self.lb = lb
        self.ub = ub
        assert isinstance(lb["idx"], int)
        assert isinstance(ub["idx"], int)
        # Children
        self.left = None
        self.right = None

    def split(self, threshold):
        """Split the node into two children.

        :param threshold: (dict) of form {'idx': <int>, 'value': <float>}
        """
        self.left = Node(lb=self.lb, ub=threshold)
        self.right = Node(lb=threshold, ub=self.ub)


class DensityEstimationTree:
    """Univariate density estimation with a binary tree."""

    def __init__(
        self,
        n_bins: int | None = None,
        max_bins: int | None = None,
        min_data_in_leaf: int = 3,
        lambda_: float = 1.0,
    ) -> None:
        """Initialize the DensityEstimationTree.

        Args:
            n_bins: The number of bins to use in the density estimation.
            max_bins: The maximum number of bins to use in the density estimation.
            min_data_in_leaf: The minimum number of data points in each leaf node.
            lambda_: Threshold on the information gain required to justify a node split.
        """
        self.n_bins = n_bins
        self.max_bins = max_bins
        self.min_data_in_leaf = min_data_in_leaf or 1
        self.lambda_ = lambda_
        if n_bins is not None and max_bins is not None:
            if max_bins < n_bins:
                raise ValueError("You must not specify max_bins less than n_bins")
        if min_data_in_leaf is not None:
            if not isinstance(min_data_in_leaf, int) or min_data_in_leaf < 1:
                raise ValueError("min_data_in_leaf must be an integer >= 1 or None")

    def _accept_data(self, df: pd.DataFrame) -> None:
        df.index.name = VALUE
        self.df = indexes.unset(df)

    def _plant_the_tree(self):
        self.root = Node(
            lb={"idx": int(0), VALUE: self.df[VALUE].iloc[0]},
            ub={"idx": int(self.df.shape[0]), VALUE: self.df[VALUE].iloc[-1]},
        )
        self.last_node_idx = 0
        self.nodes = {self.last_node_idx: self.root}
        mdil = self.min_data_in_leaf
        splt = _search_split(self.df.copy(), min_data_in_leaf=mdil)
        self.leaves = pd.DataFrame(splt, index=pd.RangeIndex(1))

    def _continue_splitting(self):
        """Decide whether to split again.

        If so, define the best node to split on.
        """
        self.leaves = self.leaves.sort_values("deviance_improvement")
        idx = self.leaves.idx.iloc[-1]
        val = self.leaves[VALUE].iloc[-1]
        target_n_bins = self.n_bins
        n_bins = self.leaves.shape[0]
        if idx is None or np.isnan(idx):
            if n_bins == target_n_bins:
                return False
            mdil = self.min_data_in_leaf
            if (target_n_bins is not None) and (mdil is not None):
                msg = (
                    f"min_data_in_leaf is {mdil}, which limits the number of bins to {n_bins} even though you "
                    "requested n_bin = {target_n_bins}"
                )
                warnings.warn(msg)
            else:
                try:
                    # presumably there is not sufficient data to support another bin
                    assert (n_bins + 1) * mdil >= self.df.shape[0]
                except Exception as err:
                    raise Exception("Terminated for unknown reason") from err
            return False
        self.threshold = {"idx": int(idx), VALUE: val}
        _node_int = self.leaves.index[-1]
        assert isinstance(_node_int, (int, np.integer)), "best_node_idx is not an integer"
        self.best_node = int(_node_int)

        # Decide whether to continue splitting
        if target_n_bins is not None:
            return n_bins < target_n_bins
        if self.max_bins and n_bins >= self.max_bins:
            return False
        # The number of leaf nodes is the number of distinct fitted
        #   density values, essentially the k (# of parameters) in the information criterion:
        pseudo_akaike_k = n_bins
        assert (self.last_node_idx / 2) + 1 == pseudo_akaike_k  # sanity check
        threshold = self.lambda_ * pseudo_akaike_k
        if self.leaves.deviance_improvement.iloc[-1] > threshold:
            return True
        return False

    def _search_split(self, node):
        mdil = self.min_data_in_leaf
        df = self.df.iloc[node.lb["idx"] : node.ub["idx"]].copy()
        if df.shape[0] > 1:
            return _search_split(df, lb=node.lb[VALUE], ub=node.ub[VALUE], min_data_in_leaf=mdil)
        else:
            return {
                "deviance_improvement": -1,  # negative improvment ensures no more splits
                "idx": -1,
                VALUE: -1.0,
                "n": df[COUNT].to_numpy()[0],
            }

    def _grow_the_tree(self):
        while self._continue_splitting():
            node = self.nodes[self.best_node]
            node.split(self.threshold)
            nl = node.left
            nr = node.right
            i = self.last_node_idx
            assert nl is not None, "left child is None"
            assert nr is not None, "right child is None"
            self.nodes[i + 1] = nl
            self.nodes[i + 2] = nr
            # precompute the new leaves' best split points
            snl = self._search_split(nl)
            snr = self._search_split(nr)
            indexes = set(self.leaves.idx)
            if snr["idx"] is not None and snr["idx"] > 0:
                assert snr["idx"] not in indexes
            if snl["idx"] is not None and snl["idx"] > 0:
                assert snl["idx"] not in indexes
            # drop the chosen leaf and replace it with its children
            self.leaves = self.leaves.drop([self.best_node], axis=0)
            self.leaves.loc[i + 1] = snl  # pyright: ignore
            self.leaves.loc[i + 2] = snr  # pyright: ignore
            assert self.leaves.n.sum() == self.N
            self.last_node_idx += 2

    def fit(self, df: pd.DataFrame):
        """Fit the DensityEstimationTree to the data."""
        self.N = df[COUNT].sum()
        if self.N > 0:
            self._accept_data(df)
            self._plant_the_tree()
            self._grow_the_tree()
        return self._bins()

    def _bins(self) -> pd.DataFrame:
        """Identify all leaf bins in ascending order."""
        if self.N == 0:
            return pd.DataFrame({"lb": [], "ub": [], "freq": [], "width": [], "rate": []})
        lnodes = self.leaves.index.to_numpy()
        df = pd.DataFrame(
            {"lb": [self.nodes[k].lb[VALUE] for k in lnodes], "ub": [self.nodes[k].ub[VALUE] for k in lnodes]}
        )
        df["freq"] = self.leaves.n.to_numpy()
        assert (df.ub - df.lb).min() > 0
        df["width"] = df.ub - df.lb
        df["rate"] = df.freq / df.width
        return df.sort_values("lb").reset_index(drop=True)

"""Generate a Shmistogram plot from a Shmistogram object."""

import numpy as np
import pandas as pd
from matplotlib import collections as mc
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

# Config
LEGEND_SPACE = 0.03
LEGEND_MARG = 0.02
LEGEND_SEP = 0.025

LB = "lb"
FREQ = "freq"
RATE = "rate"


class ShmistoGrammer:
    """Generate a Shmistogram plot from a Shmistogram object."""

    def __init__(
        self,
        loner_crowd_shares,
        bins=None,
        loners=None,
        name="x",
        color_crowd="#BEBEBE",
        color_loner="#C80638",  # red
        color_null="black",
    ):
        """Initialize a ShmistoGrammer object.

        Args:
            loner_crowd_shares: A tuple of the form (loner_share, crowd_share)
            bins: A DataFrame with columns ['lb', 'ub', 'freq', 'rate']
            loners: A DataFrame with columns ['n_obs']
            name: The name of the x-axis
            color_crowd: The color of the crowd
            color_loner: The color of the loners
            color_null: The color of the null values
        """
        # Plot settings
        self.name = name
        # Store plotting data
        self.loner_crowd_shares = loner_crowd_shares
        self.bins = bins
        self._triage_loners(loners)
        # Store plot settings
        self.colors = {"crowd": color_crowd, "loner": color_loner, "null": color_null}

    def _initialize_plot(self, ax, title):
        self.ax = ax
        if self.ax is None:
            self.ax = plt.subplot()
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["top"].set_visible(False)
        self.ax.set_xlabel(self.name)
        self.ax.set_ylabel("Crowd frequency rate")
        self.ax.set_title(title)

    def _triage_loners(self, loners):
        self.loners = loners[~np.isnan(loners.index)]
        self.null = loners[np.isnan(loners.index)].n_obs.sum()

    def _bin_edges(self):
        assert isinstance(self.bins, pd.DataFrame), "Bins must be a DataFrame"
        le = self.bins[LB].to_numpy()
        re = np.array([self.bins.ub.to_numpy()[-1]])
        return np.concatenate((le, re))

    def _bins(self):
        assert isinstance(self.bins, pd.DataFrame), "Bins must be a DataFrame"
        edges = self._bin_edges()
        rates = self.bins[RATE].to_numpy()
        self.ax.fill_between(
            edges.repeat(2)[1:-1],
            np.asarray(rates).repeat(2),
            facecolor=self.colors["crowd"],
        )

    def _count_types(self):
        assert isinstance(self.bins, pd.DataFrame), "Bins must be a DataFrame"
        return pd.Series(
            {
                "crowd": self.bins[FREQ].sum(),
                "loner": self.loners.n_obs.sum(),
                "null": self.null,
            }
        ).sort_values()

    def _append_legend_bar(self):
        counts = self._count_types()
        cmax = counts.max()
        # stretch y axis to make space for legend
        assert isinstance(self.bins, pd.DataFrame), "Bins must be a DataFrame"
        ymax = self.bins[RATE].max()
        N = len(counts)
        ymarg = ymax * (LEGEND_MARG + N * LEGEND_SPACE + (N - 1) * LEGEND_SEP)
        ysep = ymax * LEGEND_SEP
        self.ax.set_ylim(0, ymax + ymarg)
        # orient legent w.r.t. horizontal axis
        xmin = self.bins[LB].values[0]
        xmax = self.bins.ub.values[-1]
        w = xmax - xmin
        lxmin = xmin + w / 4
        ymin = ymax * (1 + LEGEND_MARG)
        # iterate over the counts, putting each one on the plot
        for grp in counts.index:
            assert isinstance(grp, str), "Group names must be strings"
            bar_len = (0.7 * w * counts[grp]) / cmax
            bar_height = LEGEND_SPACE * ymax
            rect = Rectangle(
                (lxmin, ymin),
                bar_len,
                bar_height,
                facecolor=self.colors[grp],
            )
            self.ax.text(
                lxmin, ymin - ysep / 3, grp + ": ", horizontalalignment="right", verticalalignment="bottom", fontsize=10
            )
            self.ax.add_patch(rect)
            ymin += bar_height + ysep
        self.ymax = ymax
        self.ymarg = ymarg

    def _loners(self):
        if self.loners.shape[0] == 0:
            return None
        self._append_legend_bar()
        # create loners axis
        axl = self.ax.twinx()
        axl.spines["top"].set_visible(False)
        axl.spines["right"].set_color(self.colors["loner"])
        axl.tick_params(axis="y", colors=self.colors["loner"])
        axl.set_ylabel("Loner count", color=self.colors["loner"])
        marg_mult = (self.ymax + self.ymarg) / self.ymax
        axl.set_ylim(0, self.loners.n_obs.max() * marg_mult)
        # add the loner count line segments
        lines = [[(idx, 0), (idx, row.n_obs)] for idx, row in self.loners.iterrows()]
        lc = mc.LineCollection(lines, colors=self.colors["loner"], linewidths=0.6)
        axl.add_collection(lc)
        axl.plot(
            self.loners.index.values,
            self.loners.n_obs.values,
            marker="o",
            color=self.colors["loner"],
            markersize=3,
            linestyle="None",  # Add this line to remove the connecting line
        )

    def plot(self, ax=None, show=False, title="Shmistogram"):
        """Plot the Shmistogram.

        Args:
            ax: The axis on which to plot
            show: Whether to show the plot
            title: The title of the plot
        """
        assert isinstance(self.bins, pd.DataFrame), "Bins must be a DataFrame"
        if self.bins.shape[0] == 0:
            print("This data is 100% loners:")
            print(self.loners)
            return None
        self._initialize_plot(ax, title)
        self._bins()
        self._loners()
        if show:
            plt.show()


def standard_histogram(data, ax=None, name="x", title="Histogram", color="#BEBEBE"):
    """Plot a standard histogram.

    Args:
        data: The data to plot
        ax: The axis on which to plot
        name: The name of the x-axis
        title: The title of the plot
        color: The color of the plot
    """
    if ax is not None:
        ax.hist(data, color=color)
    else:
        plt.hist(data, color=color)
        ax = plt.gca()
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_xlabel(name)
    ax.set_ylabel("Frequency")
    ax.set_title(title)

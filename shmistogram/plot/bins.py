import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import numpy as np

def bins(edges, masses, name='x', color='#BEBEBE', return_plt=True):
    '''
    :param edges: (1-d numpy array) A vector of bin edges
    :param masses: (1-d numpy array) A vector of the mass per bin
    :param name: (str) feature name for the horizontal axis label
    :param color: (str) fill color for the bars. Default '#BEBEBE' matches with
        "grey" (= "gray") in R
    :param return_plt: (boolean) if True, explicitly return the plotting object thingy
    '''
    assert len(edges) == len(masses) + 1
    # Set up plot
    ax = plt.subplot(111)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_ylabel('Frequency rate')
    if name is not None:
        ax.set_xlabel(name)
    else:
        ax.set_xlabel('x')
    widths = np.diff(edges)
    rates = masses/widths
    # Plot
    ax.fill_between(edges.repeat(2)[1:-1], rates.repeat(2), facecolor=color)
    if return_plt:
        return ax

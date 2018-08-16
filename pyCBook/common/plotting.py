""" Module for common functions frequently used by other modules
"""
from __future__ import division

import os
import re
import numpy as np
import matplotlib.pyplot as plot


def plot_pools(records, title='Carbon Pools'):
    """ plot carbon pools

    Args:
        records (list): input data
        title (str): plot main title

    Returns:
        0: successful

    """
    # prepare data
    pnames = records[0]
    data = np.array(records[1:])

    # loop through pools
    for i in range(1, len(pnames)):
        # calculate x and y
        pname = pnames[i]
        y = data[data[:, i] > 0, i]
        x = data[data[:, i] > 0, 0]
        x = x // 1000 + (x - (x // 1000 * 1000)) / 365.25
        # figure our color
        if 'above' in pname:
            color = 'b'
        elif 'burned' in pname:
            color = 'r'
        else:
            color = 'g'
        # make plot
        plot.plot(x, y, '{}-'.format(color), lw=2)

    # juice up the plot
    plot.ylabel('Biomass (Mg C / ha.)')
    plot.xlabel('Date')
    plot.title(title)
    plot.grid(True)

    # done
    plot.show()
    return 0

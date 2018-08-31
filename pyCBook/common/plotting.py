""" Module for common functions frequently used by other modules
"""
from __future__ import division

import os
import re
import numpy as np
import matplotlib.pyplot as plot


def plot_pools(records, title='Carbon Pools',
                ylabel='Carbon Density (Mg C / ha.)', des='NA'):
    """ plot carbon pools

    Args:
        records (list): input data
        title (str): plot main title
        des (str): output file

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
        y = data[data[:, i] > -9999, i]
        x = data[data[:, i] > -9999, 0]
        x = x // 1000 + (x - (x // 1000 * 1000)) / 365.25
        # figure our color
        if 'above' in pname:
            _format = 'b-'
        elif 'burned' in pname:
            if len(x) > 1:
                _format = 'r-'
            else:
                _format = 'r*'
        else:
            _format = 'g-'
        # make plot
        plot.plot(x, y, _format, lw=2)

    # juice up the plot
    plot.ylabel(ylabel)
    plot.xlabel('Date')
    plot.title(title)
    plot.grid(True)

    # done
    if des == 'NA':
        plot.show()
    else:
        plot.savefig(des)
        plot.clf()
    return 0


def plot_book(book, title='Cumulative Emission', des='NA'):
    """ plot bookkeeping results

    Args:
        book (ndarray): input data
        title (str): plot main title
        des (str): output file

    Returns:
        0: successful

    """
    # calculate x
    x = book['date']//1000 + (book['date'] - (book['date']//1000*1000)) / 365.25
    # make plot
    plot.plot(x, book['net'], '--', c='0.5', lw=1)
    plot.plot(x, book['emission'], 'r-', lw=2)
    plot.plot(x, book['productivity'], 'g-', lw=2)
    # juice up the plot
    plot.ylabel('Cumulative Emission (Mg C / ha.)')
    plot.xlabel('Date')
    plot.title(title)
    plot.grid(True)
    # done
    if des == 'NA':
        plot.show()
    else:
        plot.savefig(des)
        plot.clf()
    return 0

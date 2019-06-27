""" Module for common functions frequently used by other modules
"""
from __future__ import division

import os
import re
import numpy as np
import matplotlib.pyplot as plot

from . import constants as cons


def plot_pools(records, title='Carbon Pools',
                ylabel='Carbon Density (Mg C / ha.)', des='NA'):
    """ plot carbon pools

    Args:
        records (list): input data
        title (str): plot main title
        ylabel (str): plot ylabel
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
        y = data[data[:, i] > cons.MAP_NODATA, i]
        x = data[data[:, i] > cons.MAP_NODATA, 0]
        x = x // 1000 + (x - (x // 1000 * 1000)) / cons.DIY
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


def plot_book(book, bar=False, title='Cumulative Emission',
                ylabel='Cumulative Emission (Mg C / ha.)', des='NA'):
    """ plot bookkeeping results

    Args:
        book (ndarray): input data
        title (str): plot main title
        ylabel (str): plot ylabel
        des (str): output file

    Returns:
        0: successful

    """
    # calculate x
    x = book['date']//1000 + (book['date'] - (book['date']//1000*1000)) / cons.DIY
    # make plot
    if bar:
        plot.bar(x, book['emission'], color='red')
        plot.bar(x, book['productivity'], color='green')
        plot.plot(x, book['net'], '--', c='0.5', lw=1)
    else:
        plot.plot(x, book['net'], '--', c='0.5', lw=1)
        plot.plot(x, book['emission'], 'r-', lw=2)
        plot.plot(x, book['productivity'], 'g-', lw=2)
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

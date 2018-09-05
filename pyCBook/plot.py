""" Module for ploting results
"""
import os
import numpy as np

from .common import (log, get_files, get_int, plot_pools, get_class_string,
                        plot_book)
from .io import yatsm2records, csv2ndarray
from .carbon import pools


def plot_pixel(ori, lookup, px, py, _which=0, des='NA'):
    """ plot bookkeeping result for a pixel

    Args:
        ori (str): place to look for results
        lookup (str): look up table for classes
        px (int): pixel x location
        py (int): pixel y location
        _which (int): 0 for biomass, 1 for emission
        des (str): output file if wanted

    Returns:
        0: successful
        1: can't find input line result
        2: error reading the line result
        3: error finding the pixel
        4: error ploting

    """
    # find line result
    log.info('Looking for line result...')
    try:
        carbon = get_files(ori, 'carbon_r{}.npz'.format(py))
        # read line cache
        log.info('Reading line result...')
        if len(carbon) > 0:
            _line = yatsm2records(os.path.join(carbon[0][0], carbon[0][1]))
        else:
            log.error('Find no line result for {}.'.format(py))
            return 1
    except:
        log.error('Failed to read line {}.'.format(py))
        return 2

    # get pixel pools
    log.info('Locating pixel...')
    pixel_pools = _line[_line['px'] == px]
    if len(pixel_pools) == 0:
        log.error('Can not find pixel {}'.format(px))
        return 3

    # gen plot
    log.info('Generating plot...')
    try:
        pixel = pools(pixel_pools)
        record = pixel.record()
        lookup = csv2ndarray(lookup)
        above = pixel.pools[pixel.pools['subpool'] == 'above']
        _class = get_class_string(above['class'], lookup)
        if _which == 0:
            title = 'Carbon pools for pixel ({} {}): {}'.format(px, py, _class)
            ylabel = 'Carbon Density (Mg C / ha.)'
        else:
            title = 'Cumulative emission for pixel ({} {}): {}'.format(px, py,
                                                                        _class)
            ylabel = 'Cumulative Emission (Mg C / ha.)'
        plot_pools(record[_which], title, ylabel, des)
    except:
        log.error('Failed to generate plot.')
        return 4

    # done
    log.info('Process completed.')
    return 0


def plot_report(ori, des='NA',cum=True):
    """ plot bookkeeping result for a pixxel

    Args:
        ori (str): place to look for results
        des (str): output file if wanted
        cum (bool): cumulative or not

    Returns:
        0: successful
        1: error reading input
        2: error processing data
        3: error ploting

    """
    # get pixel pools
    log.info('Reading input...')
    try:
        data = csv2ndarray(ori)
    except:
        log.error('Failed to read {}'.format(ori))
        return 1

    if not cum:
        # calculating non-cumulative results
        log.info('Calculating non-cumulative results...')
        try:
            for i in range(len(data) - 1, 0, -1):
                data[i]['net'] -= data[i - 1]['net']
                data[i]['emission'] -= data[i - 1]['emission']
                data[i]['productivity'] -= data[i - 1]['productivity']
        except:
            log.error('Failed to calculate non-cumulative results')
            return 2
        ylabel = 'Emission (Mg C / ha. / year)'
        bar = True
    else:
        ylabel = 'Cumulative Emission (Mg C / ha.)'
        bar = False

    # gen plot
    log.info('Generating plot...')
    try:
        title = 'Carbon Bookkeeping: {}'.format(os.path.basename(ori))
        plot_book(data, bar, title, ylabel, des)
    except:
        log.error('Failed to generate plot.')
        return 3

    # done
    log.info('Process completed.')
    return 0

""" Module for ploting results
"""
import os
import numpy as np

from .common import log, get_files, get_int, plot_pools, get_class_string
from .io import yatsm2records, csv2ndarray
from .carbon import pools


def plot_pixel(ori, lookup, px, py):
    """ plot bookkeeping result for a pixxel

    Args:
        ori (str): place to look for results
        lookup (str): look up table for classes
        px (int): pixel x location
        py (int): pixel y location

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
    #try:
    if True:
        pixel = pools(pixel_pools)
        record = pixel.record()
        lookup = csv2ndarray(lookup)
        _class = get_class_string(pixel.pools['class'], lookup)
        title = 'Carbon pools for pixel ({} {}): {}'.format(px, py, _class)
        plot_pools(record[0], title)
    #except:
    #    log.error('Failed to generate plot.')
    #    return 4

    # done
    log.info('Process completed.')
    return 0

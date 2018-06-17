""" Module for IO of YATSM files
"""
import numpy as np

from ..common import log


def yatsm2records(_file, verbose=False):
    """ read YATSM result file as a list

    Args:
        _file (str): path to yatsm file
        verbose (bool): verbose or not

    Returns:
        records (ndarray): yatsm records

    """
    yatsm = np.load(_file)
    records = yatsm['record']
    n = len(records)
    if verbose:
        log.info('Total number of records: {}'.format(n))
    return records


def yatsm2pixels(_file, x=[], verbose=False):
    """ read YATSM result file and arrange by pixel

    Args:
        _file (str): path to yatsm file
        x (list/int): which pixels to grab, [] for all
        verbose (bool): verbose or not

    Returns:
        pixels (ndarray): records of selected pixels

    """
    if type(x) == int:
        x = [x]

    # initialize things
    pixels = []
    records = yatsm2records(_file, verbose)
    n = len(records)
    pixel = []
    px = -1

    # loop through all records
    for i in range(0, n):
        ts = records[i]
        # see if this record needs to be saved
        if ((px < 0) and ((len(x)==0) or (ts['px'] in x))) or (px==ts['px']):
            pixel.append(ts)
            px = ts['px']
        # see if this pixel is complete
        if (len(pixel) > 0) and (px != ts['px']):
            pixels.append(pixel)
            if ts['px'] not in x:
                pixel = []
                px = -1
            else:
                pixel = [ts]
                px = ts['px']

    # done
    return pixels

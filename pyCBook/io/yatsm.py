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
    pixels = []
    records = yatsm2records(_file, verbose)
    if len(records) > 0:
        pxs = records['px']
        for px in pxs:
            if (px in x) or (len(x)==0):
                pixels.append(records[records['px']==px])
    return pixels

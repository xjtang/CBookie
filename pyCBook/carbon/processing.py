""" Module for processing when tracking carbon
"""
import math
import numpy as np

from ..common import constants as cons


def get_biomass(para, _class, scale_factor):
    """ get biomass value from input parameters

    Args:
        para (list): input parameters
        _class (str): land cover class
        scale_factor (float): scale factor

    Returns:
        biomass (float): biomass value

    """
    para = para[0]
    return [x * scale_factor for x in para[para['id'] == _class][['biomass', 'uncertainty']][0]]


def get_flux(para, _class):
    """ get emission flux value from input parameters

    Args:
        para (list): input parameters
        _class (str): land cover class

    Returns:
        flux (float): flux value

    """
    para = para[1]
    return para[para['id'] == _class][0]


def run_flux(y1, x1, x2, func, coef, scale_factor):
    """ calculate fluxes

    Args:
        y1 (float): initial biomass
        x1 (float): start time
        x2 (float): end time
        func (str): decay function
        coef (list, float): decay function coefs
        scale_factor (float): scale factor

    Returns:
        y2 (float): biomass at x2

    """
    emit = False
    if x1 == x2:
        return y1
    y1 = y1 / scale_factor
    if func == 'linear':
        y2 = y1 * (1 - (x2 - x1) / (cons.DIY / coef[0]))
        emit = True
    elif func == 'logdc':
        y2 = y1 * np.exp(-(x2 - x1) / (cons.DIY / coef[0]))
        emit = True
    elif func == 'const':
        y2 = y1 + coef[0] * (x2 - x1) / cons.DIY
        emit = True
    elif func == 'log':
        y2 = coef[0]*np.log(np.exp((y1-coef[1])/coef[0])+(x2-x1)/cons.DIY)+coef[1]
    elif func == 'none':
        y2 = y1
    elif func == 'dual':
        if ((x2 - x1) / cons.DIY) >= coef[1][0]:
            y2 = y1 + coef[0] * 25
        else:
            y2 = y1 + coef[0] * (x2 - x1) / cons.DIY
    else:
        y2 = y1 * 0.0
    y2[(y1 >= 0) & (y2 < 0)] = 0
    if emit:
        y2[(y1 <= 0)] = 0
    return y2 * scale_factor


def draw(agb, ci, seed):
    """ draw AGB from distribution

    Args:
        agb (float): initial biomass
        ci (float): confidence interval
        seed (float, ndarray): monte carlo seed

    Returns:
        x (float, ndarray): drawed value(s)

    """
    return agb + seed * (ci / 1.96)


def gen_dtype(_type, size):
    """ generate dtype

    Args:
        _type (int): which type
        size (int): data size

    Returns:
        dtype (ndarray): dtype

    """
    if _type == 1:
        dtype = [('pool', 'U10'), ('subpool', 'U10'), ('class', '<u2'),
                    ('id', '<u2'), ('px', '<u2'), ('py', '<u2'),
                    ('psize', '<f4'), ('start', '<i4'), ('end', '<i4'),
                    ('biomass', '<f8', (2, size)), ('func', 'U10'),
                    ('coef', '<f4', (2, size))]
    elif _type == 2:
        dtype = [('date', '<i4'), ('burned', '<f8', (size, )),
                    ('emission', '<f8', (size, )),
                    ('productivity', '<f8', (size, )), ('net', '<f8', (size, )),
                    ('unreleased', '<f8', (size, ))]
    else:
        dtype = []
    return dtype

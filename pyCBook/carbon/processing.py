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
    return para[para['id'] == _class][0]['biomass'] * scale_factor


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
    if x1 == x2:
        return y1
    y1 = y1 / scale_factor
    if func == 'linear':
        y2 = y1 * (1 - (x2 - x1) / (cons.DIY / coef[0]))
    elif func == 'logdc':
        y2 = y1 * math.exp(-(x2 - x1) / (cons.DIY / coef[0]))
    elif func == 'const':
        y2 = y1 + coef[0] * (x2 - x1) / cons.DIY
    elif func == 'log':
        y2 = coef[0]*math.log(math.exp((y1-coef[1])/coef[0])+(x2-x1)/cons.DIY)+coef[1]
    elif func == 'none':
        y2 = y1
    else:
        y2 = 0.0
    if y2 < 0:
        y2 = 0.0
    return y2 * scale_factor


def draw(agb, uc, n):
    """ draw AGB from distribution

    Args:
        agb (float): initial biomass
        uc (float): start time
        n (int): size

    Returns:
        x (float, ndarray): drawed value(s)

    """
    ci = agb * uc / 100
    se = ci / 1.96
    return np.random.normal(agb, se, n)

""" Module for processing when tracking carbon
"""
import math


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
    if func == 'linear':
        y2 = y1 * (1 - (x2 - x1) / (365.25 / coef[0]))
    elif func == 'log':
        y2 = y1 * math.exp(-(x2 - x1) / (365.25 / coef[0]))
    elif func == 'const':
        y2 = y1 + coef[0] * scale_factor * (x2 - x1) / 365.25
    elif func == 'none':
        y2 = y1
    else:
        y2 = 0
    if y2 < 0:
        y2 = 0
    return y2

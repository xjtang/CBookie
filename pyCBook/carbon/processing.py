""" Module for processing when tracking carbon
"""


def get_biomass(para, _class):
    """ get biomass value from input parameters

    Args:
        para (list): input parameters
        _class (str): land cover class

    Returns:
        biomass (float): biomass value

    """
    para = para[0]
    return para[para['id'] == _class][0]['biomass']


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


def run_flux(y1, x1, x2, func, coef):
    """ calculate fluxes

    Args:
        y1 (float): initial biomass
        x1 (float): start time
        x2 (float): end time
        func (str): decay function
        coef (list, float): decay function coefs

    Returns:
        y2 (float): biomass at x2

    """
    if func == 'linear':
        y2 = y1 + coef[0] / 365.25 * (x2 - x1)
    elif func == 'log':
        y2 = 0
    elif func == 'none':
        y2 = y1
    else:
        y2 = 0
    return y2

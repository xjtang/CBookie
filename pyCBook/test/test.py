""" Module for testing
"""
import os

from ..carbon import *
from ..common import *
from ..io import *


class test:
    """ testing
    """
    wd = '/Users/xjtang/Applications/GitHub/CBookie/'
    para = os.path.join(wd, 'parameters/Colombia/')
    line = os.path.join(wd, 'pyCBook/test/pixels/line.npz')
    forest = os.path.join(wd, 'pyCBook/test/pixels/forest.npz')
    deforest = os.path.join(wd, 'pyCBook/test/pixels/deforest.npz')
    regrow = os.path.join(wd, 'pyCBook/test/pixels/regrow.npz')
    output = os.path.join(wd, 'pyCBook/test/outputs/')

    def __init__(self):
        self.p = [csv2ndarray(os.path.join(self.para, 'biomass.csv')),
                    csv2ndarray(os.path.join(self.para, 'flux.csv')),
                    csv2ndarray(os.path.join(self.para, 'product.csv'))]

        self.all = yatsm2pixels(self.line)
        self.f = yatsm2pixels(self.forest)[0]
        self.df = yatsm2pixels(self.deforest)[0]
        self.r = yatsm2pixels(self.regrow)[0]

    def get_carbon(self, pixel):
        pixel = pixel.copy()
        for x in pixel:
            x['start'] = doy_to_ordinal(x['start'])
            x['end'] = doy_to_ordinal(x['end'])
            if x['break'] > 0:
                x['break'] = doy_to_ordinal(x['break'])
        return(carbon(self.p, pixel))

    def record_carbon(self, pixel, des):
        carbon = self.get_carbon(pixel)
        record = carbon.pool_record()
        list2csv(record[0], des)
        return 0

    def full_test(self):
        self.record_carbon(self.f, os.path.join(self.output, 'forest.csv'))
        self.record_carbon(self.df, os.path.join(self.output, 'deforest.csv'))
        self.record_carbon(self.r, os.path.join(self.output, 'regrow.csv'))
        return 0

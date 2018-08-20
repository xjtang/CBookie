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
    se_biomass = 222

    def __init__(self):
        self.p = [csv2ndarray(os.path.join(self.para, 'biomass.csv')),
                    csv2ndarray(os.path.join(self.para, 'flux.csv')),
                    csv2ndarray(os.path.join(self.para, 'product.csv'))]

        self.all = yatsm2pixels(self.line)
        self.f = yatsm2pixels(self.forest)[0]
        self.df = yatsm2pixels(self.deforest)[0]
        self.r = yatsm2pixels(self.regrow)[0]
        self.f_c = self.get_carbon(self.f, self.se_biomass)
        self.df_c = self.get_carbon(self.df, self.se_biomass)
        self.r_c = self.get_carbon(self.r, -1)
        self.f_p = self.get_pools(self.f_c.pools)
        self.df_p = self.get_pools(self.df_c.pools)
        self.r_p = self.get_pools(self.r_c.pools)

    def get_carbon(self, pixel, se_biomass):
        pixel = pixel.copy()
        for x in pixel:
            x['start'] = doy_to_ordinal(x['start'])
            x['end'] = doy_to_ordinal(x['end'])
            if x['break'] > 0:
                x['break'] = doy_to_ordinal(x['break'])
        return(carbon(self.p, pixel, se_biomass))

    def get_pools(self, pixel):
        return(pools(pixel))

    def record_carbon(self, pixel, se_biomass, des, overwrite=True):
        carbon = self.get_carbon(pixel, se_biomass)
        record = carbon.pool_record()
        list2csv(record[0], des, overwrite)
        return 0

    def record_flux(self, pixel, se_biomass, des, overwrite=True):
        carbon = self.get_carbon(pixel, se_biomass)
        record = carbon.pool_record()
        list2csv(record[1], des, overwrite)
        return 0

    def full_test(self):
        self.record_carbon(self.f, self.se_biomass,
                            os.path.join(self.output, 'forest.csv'))
        self.record_carbon(self.df, self.se_biomass,
                            os.path.join(self.output, 'deforest.csv'))
        self.record_carbon(self.r, -1, os.path.join(self.output, 'regrow.csv'))
        self.record_flux(self.f, self.se_biomass,
                            os.path.join(self.output, 'forest2.csv'))
        self.record_flux(self.df, self.se_biomass,
                            os.path.join(self.output, 'deforest2.csv'))
        self.record_flux(self.r, -1, os.path.join(self.output, 'regrow2.csv'))
        return 0

    def plot(self, pixel, _which=0):
        lookup = self.p[0]
        above = pixel.pools[pixel.pools['subpool'] == 'above']
        _class = get_class_string(above['class'], lookup)
        px = pixel.pools[0]['px']
        py = pixel.pools[0]['py']
        title = 'Carbon pools for pixel ({} {}): {}'.format(px, py, _class)
        record = pixel.record()[_which]
        plot_pools(record, title)
        return 0

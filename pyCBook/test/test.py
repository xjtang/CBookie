""" Module for testing
"""
import os
import numpy as np

from ..carbon import *
from ..common import *
from ..io import *

from .. import book
from .. import report as rpt
from .. import plot as plt

class test:
    """ testing
    """
    wd = '/Users/xjtang/Applications/GitHub/CBookie/'
    para = os.path.join(wd, 'parameters/Colombia/')
    input = os.path.join(wd, 'pyCBook/test/inputs/')
    output = os.path.join(wd, 'pyCBook/test/outputs/')
    figure = os.path.join(wd, 'pyCBook/test/plots/')
    se_biomass = -1

    def __init__(self):
        self.p = [csv2ndarray(os.path.join(self.para, 'biomass.csv')),
                    csv2ndarray(os.path.join(self.para, 'flux.csv')),
                    csv2ndarray(os.path.join(self.para, 'product.csv'))]
        self.f = yatsm2records(os.path.join(self.input, 'yatsm_r1.npz'))
        self.df = yatsm2records(os.path.join(self.input, 'yatsm_r2.npz'))
        self.r = yatsm2records(os.path.join(self.input, 'yatsm_r3.npz'))
        self.f_c = self.get_carbon(self.f, self.se_biomass)
        self.df_c = self.get_carbon(self.df, self.se_biomass)
        self.r_c = self.get_carbon(self.r, self.se_biomass)
        self.f_p = self.get_pools(self.f_c.pools)
        self.df_p = self.get_pools(self.df_c.pools)
        self.r_p = self.get_pools(self.r_c.pools)

    def read_result(self):
        self.f2 = yatsm2records(os.path.join(self.output, 'carbon_r1.npz'))
        self.df2 = yatsm2records(os.path.join(self.output, 'carbon_r2.npz'))
        self.r2 = yatsm2records(os.path.join(self.output, 'carbon_r3.npz'))

    def get_carbon(self, pixel, se_biomass):
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

    def rerun(self):
        book.book_carbon('yatsm_r*.npz', self.input, self.para, self.output,
                            'NA', True, True)
        rpt.report_carbon('carbon_r*.npz', [2000001, 2010365], self.output,
                            os.path.join(self.output, 'report.csv'), True, True)
        return 0

    def plot_all(self):
        self.plot(self.f_p, 0, os.path.join(self.figure, 'forest.png'))
        self.plot(self.f_p, 1, os.path.join(self.figure, 'forest_e.png'))
        self.plot(self.df_p, 0, os.path.join(self.figure, 'deforest.png'))
        self.plot(self.df_p, 1, os.path.join(self.figure, 'deforest_e.png'))
        self.plot(self.r_p, 0, os.path.join(self.figure, 'regrow.png'))
        self.plot(self.r_p, 1, os.path.join(self.figure, 'regrow_e.png'))
        plt.plot_report(os.path.join(self.output, 'report.csv'),
                        os.path.join(self.figure, 'report.png'))
        return 0

    def plot(self, pixel, _which=0, des='NA'):
        lookup = self.p[0]
        above = pixel.pools[pixel.pools['subpool'] == 'above']
        _class = get_class_string(above['class'], lookup)
        px = pixel.pools[0]['px']
        py = pixel.pools[0]['py']
        title = 'Carbon pools for pixel ({} {}): {}'.format(px, py, _class)
        record = pixel.record()[_which]
        plot_pools(record, title, des)
        return 0

    def report(self):
        rpt.report_carbon('*.npz', [2000001, 2010365], self.input,
                            os.path.join(self.output, 'report.csv'), True, True)
        return 0


class test2:
    """ testing
    """
    lc_1993 = '/Users/xjtang/Downloads/pycbook/ClassM3_1993-01-01_M3train.tif'
    lc_1997 = '/Users/xjtang/Downloads/pycbook/ClassM3_1997-01-01_M3train.tif'
    biomass30 = '/Users/xjtang/Downloads/pycbook/biomass_006059.tif'

    def __init__(self):
        self.lc93 = image2array(self.lc_1993, 1)
        self.lc97 = image2array(self.lc_1997, 1)
        self.biomass = image2array(self.biomass30)

    def hist(self, x, bin=10, title='NA'):
        plot.hist(x, bin)
        plot.xlabel('Biomass (Mg C / ha.)')
        plot.ylabel('Frequency')
        plot.title(title)
        plot.grid(True)
        plot.show()
        return 0

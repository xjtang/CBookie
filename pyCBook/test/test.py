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
    input = os.path.join(wd, 'pyCBook/test/data/carbon/inputs/')
    output = os.path.join(wd, 'pyCBook/test/data/carbon/outputs/')
    figure = os.path.join(wd, 'pyCBook/test/data/carbon/plots/')
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
        return 0

    def plot_all(self):
        self.plot(self.f_p, 0, os.path.join(self.figure, 'forest.png'))
        self.plot(self.f_p, 1, os.path.join(self.figure, 'forest_e.png'))
        self.plot(self.df_p, 0, os.path.join(self.figure, 'deforest.png'))
        self.plot(self.df_p, 1, os.path.join(self.figure, 'deforest_e.png'))
        self.plot(self.r_p, 0, os.path.join(self.figure, 'regrow.png'))
        self.plot(self.r_p, 1, os.path.join(self.figure, 'regrow_e.png'))
        plt.plot_report(os.path.join(self.output, 'report_daily.csv'),
                        os.path.join(self.figure, 'report_daily.png'))
        plt.plot_report(os.path.join(self.output, 'report_annual.csv'),
                        os.path.join(self.figure, 'report_annual_cum.png'))
        plt.plot_report(os.path.join(self.output, 'report_annual.csv'),
                        os.path.join(self.figure, 'report_annual.png'), False)
        return 0

    def plot(self, pixel, _which=0, des='NA'):
        lookup = self.p[0]
        above = pixel.pools[pixel.pools['subpool'] == 'above']
        _class = get_class_string(above['class'], lookup)
        px = pixel.pools[0]['px']
        py = pixel.pools[0]['py']
        if _which == 0:
            title = 'Carbon pools for pixel ({} {}): {}'.format(px, py, _class)
            ylabel = 'Carbon Density (Mg C / ha.)'
        else:
            title = 'Cumulative emission for pixel ({} {}): {}'.format(px, py,
                                                                        _class)
            ylabel = 'Cumulative Emission (Mg C / ha.)'
        record = pixel.record()[_which]
        plot_pools(record, title, ylabel, des)
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


class test3:
    """ testing
    """
    wd = '/Users/xjtang/Applications/GitHub/CBookie/'
    para = os.path.join(wd, 'parameters/Colombia/')
    input = os.path.join(wd, 'pyCBook/test/data/uncertainty/inputs/')
    output = os.path.join(wd, 'pyCBook/test/data/uncertainty/outputs/')
    reports = os.path.join(wd, 'pyCBook/test/data/uncertainty/reports/')
    daily = os.path.join(wd, 'pyCBook/test/data/uncertainty/reports/daily')
    annual = os.path.join(wd, 'pyCBook/test/data/uncertainty/reports/annual')
    figure = os.path.join(wd, 'pyCBook/test/data/uncertainty/plots/')
    se_biomass = -1

    def __init__(self):
        self.p = [csv2ndarray(os.path.join(self.para, 'biomass.csv')),
                    csv2ndarray(os.path.join(self.para, 'flux.csv')),
                    csv2ndarray(os.path.join(self.para, 'product.csv'))]
        self.model = yatsm2records(os.path.join(self.input, 'yatsm_r1.npz'))
        self.real = yatsm2records(os.path.join(self.input, 'yatsm_r2.npz'))
        self.fixed = yatsm2records(os.path.join(self.input, 'yatsm_r3.npz'))
        self.model_c = self.get_carbon(self.model, self.se_biomass)
        self.real_c = self.get_carbon(self.real, self.se_biomass)
        self.fixed_c = self.get_carbon(self.fixed, self.se_biomass)
        self.model_p = self.get_pools(self.model_c.pools)
        self.real_p = self.get_pools(self.real_c.pools)
        self.fixed_p = self.get_pools(self.fixed_c.pools)

    def rerun(self):
        book.book_carbon('yatsm_r*.npz', self.input, self.para, self.output,
                            'NA', True, True)
        rpt.report_line('carbon_r*.npz', [1990001, 2015365], self.output,
                            self.daily, 1, True, True)
        rpt.report_line('carbon_r*.npz', [1990001, 2015365], self.output,
                            self.annual, 365, True, True)
        rpt.report_sum('report_r1*.npz', self.daily, os.path.join(self.reports,
                        'model_daily.csv'), True, True)
        rpt.report_sum('report_r2*.npz', self.daily, os.path.join(self.reports,
                        'real_daily.csv'), True, True)
        rpt.report_sum('report_r3*.npz', self.daily, os.path.join(self.reports,
                        'fixed_daily.csv'), True, True)
        rpt.report_sum('report_r1*.npz', self.annual, os.path.join(self.reports,
                        'model_annual.csv'), True, True)
        rpt.report_sum('report_r2*.npz', self.annual, os.path.join(self.reports,
                        'real_annual.csv'), True, True)
        rpt.report_sum('report_r3*.npz', self.annual, os.path.join(self.reports,
                        'fixed_annual.csv'), True, True)
        return 0

    def get_carbon(self, pixel, se_biomass):
        return(carbon(self.p, pixel, se_biomass))

    def get_pools(self, pixel):
        return(pools(pixel))

    def plot_all(self):
        plt.plot_report(os.path.join(self.reports, 'model_daily.csv'),
                        os.path.join(self.figure, 'model_cum.png'))
        plt.plot_report(os.path.join(self.reports, 'model_annual.csv'),
                        os.path.join(self.figure, 'model.png'), False)
        plt.plot_report(os.path.join(self.reports, 'real_daily.csv'),
                        os.path.join(self.figure, 'real_cum.png'))
        plt.plot_report(os.path.join(self.reports, 'real_annual.csv'),
                        os.path.join(self.figure, 'real.png'), False)
        plt.plot_report(os.path.join(self.reports, 'fixed_daily.csv'),
                        os.path.join(self.figure, 'fixed_cum.png'))
        plt.plot_report(os.path.join(self.reports, 'fixed_annual.csv'),
                        os.path.join(self.figure, 'fixed.png'), False)

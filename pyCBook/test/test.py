""" Module for testing
"""
import os
import numpy as np

from ..carbon import *
from ..common import *
from ..io import *

from .. import book, area
from .. import report as rpt
from .. import plot as plt

class test:
    """ testing
    """
    wd = '/Users/xjtang/Applications/GitHub/CBookie/'
    para = os.path.join(wd, 'parameters/test/')
    area = os.path.join(wd, 'pyCBook/test/data/area/')
    input = os.path.join(wd, 'pyCBook/test/data/carbon/inputs/')
    output = os.path.join(wd, 'pyCBook/test/data/carbon/outputs/carbon/')
    report = os.path.join(wd, 'pyCBook/test/data/carbon/outputs/report/')
    daily = os.path.join(wd, 'pyCBook/test/data/carbon/outputs/daily')
    annual = os.path.join(wd, 'pyCBook/test/data/carbon/outputs/annual')
    figure = os.path.join(wd, 'pyCBook/test/data/carbon/plots/')
    se_biomass = -1
    pixel_size = 0.3 * 0.3

    def __init__(self):
        self.p = [csv2ndarray(os.path.join(self.para, 'biomass.csv')),
                    csv2ndarray(os.path.join(self.para, 'flux.csv')),
                    csv2ndarray(os.path.join(self.para, 'product.csv'))]
        self.f = yatsm2records(os.path.join(self.input, 'yatsm_r1.npz'))
        self.df = yatsm2records(os.path.join(self.input, 'yatsm_r2.npz'))
        self.r = yatsm2records(os.path.join(self.input, 'yatsm_r3.npz'))
        self.df2 = yatsm2records(os.path.join(self.input, 'yatsm_r4.npz'))
        self.f_c = self.get_carbon(self.f, self.se_biomass, self.pixel_size)
        self.df_c = self.get_carbon(self.df, self.se_biomass, self.pixel_size)
        self.df2_c = self.get_carbon(self.df2, self.se_biomass, self.pixel_size)
        self.r_c = self.get_carbon(self.r, self.se_biomass, self.pixel_size)
        self.f_p = self.get_pools(self.f_c.pools)
        self.df_p = self.get_pools(self.df_c.pools)
        self.df2_p = self.get_pools(self.df2_c.pools)
        self.r_p = self.get_pools(self.r_c.pools)
        self.a = csv2ndarray(os.path.join(self.area, 'input.csv'))
        self.a_p = self.get_aggregated(self.a)

    def read_result(self):
        self.f_2 = yatsm2records(os.path.join(self.output, 'carbon_r1.npz'))
        self.df_2 = yatsm2records(os.path.join(self.output, 'carbon_r2.npz'))
        self.r_2 = yatsm2records(os.path.join(self.output, 'carbon_r3.npz'))
        self.df2_2 = yatsm2records(os.path.join(self.output, 'carbon_r4.npz'))

    def get_carbon(self, pixel, se_biomass=-1, psize=900):
        return(carbon(self.p, pixel, se_biomass, psize))

    def get_pools(self, pixel):
        return(pools(pixel))

    def get_aggregated(self, data):
        return(aggregated(self.p, self.a))

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
                            'NA', 'NA', True, True)
        rpt.report_line('carbon_r*.npz', [1990001, 2015365], self.output,
                        self.daily, 1, True)
        rpt.report_line('carbon_r*.npz', [1990, 2016], self.output, self.annual,
                        1, True)
        rpt.report_sum('report_r*.npz', self.daily, os.path.join(self.report,
                        'daily.csv'), True, True)
        rpt.report_sum('report_r*.npz', self.annual, os.path.join(self.report,
                        'annual.csv'), True, True)
        area.area_carbon(os.path.join(self.area, 'input.csv'), self.para,
                            os.path.join(self.area, 'output.csv'), [2001, 2015],
                            2, True)
        return 0

    def plot_all(self):
        self.plot(self.f_p, 0, os.path.join(self.figure, 'forest.png'))
        self.plot(self.f_p, 1, os.path.join(self.figure, 'forest_e.png'))
        self.plot(self.df_p, 0, os.path.join(self.figure, 'deforest.png'))
        self.plot(self.df_p, 1, os.path.join(self.figure, 'deforest_e.png'))
        self.plot(self.df2_p, 0, os.path.join(self.figure, 'deforest2.png'))
        self.plot(self.df2_p, 1, os.path.join(self.figure, 'deforest2_e.png'))
        self.plot(self.r_p, 0, os.path.join(self.figure, 'regrow.png'))
        self.plot(self.r_p, 1, os.path.join(self.figure, 'regrow_e.png'))
        plt.plot_report(os.path.join(self.report, 'daily.csv'),
                        os.path.join(self.figure, 'r_daily_cum.png'))
        plt.plot_report(os.path.join(self.report, 'annual.csv'),
                        os.path.join(self.figure, 'r_annual_cum.png'))
        plt.plot_report(os.path.join(self.report, 'annual.csv'),
                        os.path.join(self.figure, 'r_annual.png'), False)
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
                            'NA', 'NA', True, True)
        rpt.report_line('carbon_r*.npz', [1990001, 2015365], self.output,
                            self.daily, 1, True)
        rpt.report_line('carbon_r*.npz', [1990001, 2015365], self.output,
                            self.annual, 365, True)
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

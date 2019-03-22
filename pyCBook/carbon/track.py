""" Module for tracking carbon
"""
from __future__ import division

import numpy as np

from . import get_flux, get_biomass, run_flux
from ..common import doy_to_ordinal, ordinal_to_doy


class carbon:
    """ track carbon based on time series segments

    Args:
        para (list, ndarray): parameters
        pixel (ndarray): yatsm result for a pixel
        se_biomass (float): spatially explicit initial biomass

    Attributes:
        dtypes (dtype): template dtype for a carbon pool
        pname (list, str): pool names
        spname (list, str): subpool names
        forest (list, int): classes that is considered forest
        regrow_biomass (float): biomass of new regrow forest
        scale_factor (float): scale factor for biomass

    Variables:
        se_biomass: spatially explicit initial biomass
        pools: carbon pools
        lc: land cover classes
        products: ids of product pools
        pid: latest pool id
        total_burned: total burned biomass
        total_above: total aboveground biomass
        total_biomass: total biomass in all pools
        total_emission: total emission
        total_productivity: total productivity
        total_net: total net
        start_biomass: starting biomass
        end_biomass: ending biomass
        last_break: last break date
        start: start date
        end: end date
        p: parameters

    Functions:
        assess_pixel (pixel): track carbon change of a pixel
        assess_ts (ts): track carbon change of a time series segment
        new_main_pool (ts): create a new main pool based on a ts segment
        removal (): perform removal on current main pool
        deforest (): perform deforestation on current main pool
        emission (pid): calculate emission for a pool
        update_pools (): update all pools to current end date
        eval (t): calculate carbon summary up to date t
        eval_pools (t): calculate biomass and flux for each pool at date t
        pool_record (): generate daily record for each pool

    """
    dtypes = [('pool', 'U10'), ('subpool', 'U10'), ('class', '<u2'),
                ('id', '<u2'), ('px', '<u2'), ('py', '<u2'), ('start', '<i4'),
                ('end', '<i4'), ('biomass', '<f4', (2, )), ('func', 'U10'),
                ('coef', '<f4', (2, ))]
    pname = ['biomass', 'product', 'burned']
    spname = ['above', 'durable', 'fuel', 'pulp', 'burned']
    forest = [1, 5]
    seb_class = [1, 2, 3, 5]
    regrow_biomass = 0.0
    scale_factor = 0.5 * (30 * 30) / (100 * 100)
    force_start = doy_to_ordinal(1990001)

    def __init__(self, para, pixel, se_biomass=-1.0):
        self.se_biomass = se_biomass * self.scale_factor
        self.pools = []
        self.lc = []
        self.products = []
        self.pid = -1
        self.total_burned = 0.0
        self.total_above = 0.0
        self.total_biomass = 0.0
        self.total_emission = 0.0
        self.total_productivity = 0.0
        self.total_net = 0.0
        self.start_biomass = 0.0
        self.end_biomass = 0.0
        self.last_break = 0
        self.start = 0
        self.end = 0
        self.p = para
        self.px = pixel[0]['px']
        self.py = pixel[0]['py']
        self.assess_pixel(pixel)

    def assess_pixel(self, pixel):
        pixel = pixel[pixel['end'] >= self.force_start]
        if len(pixel) == 0:
            self.pools = []
        else:
            for i, x in enumerate(pixel):
                if x['start'] < self.force_start:
                    x['start'] = self.force_start
                if i == 0:
                    self.start = ordinal_to_doy(x['start'])
                    if (x['class'] in self.seb_class) & (self.se_biomass >= 0):
                        self.start_biomass = self.se_biomass
                    else:
                        self.start_biomass = get_biomass(self.p, x['class'],
                                                            self.scale_factor)
                else:
                    if ordinal_to_doy(x['start']+1) > self.pools[self.pmain]['end']:
                        self.pools[self.pmain]['end'] = ordinal_to_doy(x['start']-1)
                        self.emission(self.pmain)
                self.assess_ts(x)
                if i == (len(pixel) - 1):
                    self.end = ordinal_to_doy(x['end'])
                    self.end_biomass = self.pools[self.pmain]['biomass'][1]
                    if len(self.products) > 0:
                        self.update_pools()
            self.pools = np.array(self.pools)
            (self.total_above, self.total_biomass, self.total_burned,
                self.total_emission,
                self.total_productivity) = self.eval(self.end)
            self.total_net = self.total_emission + self.total_productivity

    def assess_ts(self, ts):
        if len(self.lc) > 0:
            if ts['class'] == self.lc[-1]:
                self.pools[self.pmain]['end'] = ordinal_to_doy(ts['end'])
                self.emission(self.pmain)
            else:
                if self.lc[-1] in self.forest:
                    self.deforest()
                else:
                    self.removal()
                self.new_main_pool(ts)
                if (self.lc[-1] in self.forest) & (self.lc[-2] not in self.forest):
                    self.pools[self.pmain]['biomass'][0] = self.regrow_biomass
                    self.emission(self.pmain)
        else:
            self.new_main_pool(ts)
        if ts['break'] > 0:
            self.last_break = ordinal_to_doy(ts['break'])

    def new_main_pool(self, ts):
        self.pid += 1
        self.pmain = self.pid
        self.lc.append(ts['class'])
        if (self.pid == 0):
            biomass = self.start_biomass
        else:
            biomass = get_biomass(self.p, ts['class'], self.scale_factor)
        flux = get_flux(self.p, ts['class'])
        self.pools.extend(np.array([(self.pname[0], self.spname[0], ts['class'],
                            self.pid, self.px, self.py,
                            ordinal_to_doy(ts['start']),
                            ordinal_to_doy(ts['end']), [biomass, 0],
                            flux['function'], (flux['coef1'], flux['coef2']))],
                            dtype=self.dtypes))
        self.end = ordinal_to_doy(ts['end'])
        self.emission(self.pmain)

    def removal(self):
        self.pid += 1
        biomass = self.pools[self.pmain]['biomass'][1]
        self.pools.extend(np.array([(self.pname[2], self.spname[4], 99,
                            self.pid, self.px, self.py, self.last_break,
                            9999999, [biomass, 0.0], 'released', [0, 0])],
                            dtype=self.dtypes))

    def deforest(self):
        biomass = self.pools[self.pmain]['biomass'][1]
        for x in self.p[2]:
            self.pid += 1
            self.pools.extend(np.array([(self.pname[1], x['product'], 99,
                                self.pid, self.px, self.py, self.last_break,
                                9999999, [biomass * x['fraction'], 0],
                                x['function'], [x['coef1'], x['coef2']])],
                                dtype=self.dtypes))
            if x['product'] == 'burned':
                self.pools[-1]['pool'] = self.pname[2]
            else:
                self.products.append(self.pid)

    def emission(self, pid):
        pool = self.pools[pid]
        biomass = run_flux(pool['biomass'][0], doy_to_ordinal(pool['start']),
                            doy_to_ordinal(pool['end']), pool['func'],
                            pool['coef'], self.scale_factor)
        self.pools[pid]['biomass'][1] = biomass

    def update_pools(self):
        for pid in self.products:
            self.pools[pid]['end'] = self.end
            self.emission(pid)

    def eval(self, t):
        above = 0.0
        biomass = 0.0
        burned = 0.0
        emission = 0.0
        productivity = 0.0
        for x in self.pools:
            if t >= x['start']:
                if t <= x['end']:
                    biomass_t = run_flux(x['biomass'][0],
                                        doy_to_ordinal(x['start']),
                                        doy_to_ordinal(t), x['func'], x['coef'],
                                        self.scale_factor)
                    emission_t = x['biomass'][0] - biomass_t
                    if x['pool'] == 'biomass':
                        above += biomass_t
                    elif x['pool'] == 'product':
                        biomass += biomass_t
                    else:
                        emission_t = biomass_t
                        burned += emission_t
                else:
                    emission_t = x['biomass'][0] - x['biomass'][1]
                if emission_t > 0:
                    emission += emission_t
                else:
                    productivity += emission_t
        biomass += above
        return (above, biomass, burned, emission, productivity)

    def eval_pools(self, t):
        biomass = []
        net = []
        for x in self.pools:
            biomass.append(-9999)
            net.append(-9999)
            if (t >= x['start']) & (t <= x['end']):
                if x['pool'] == 'burned':
                    if t == x['start']:
                        biomass[-1] = x['biomass'][0]
                    else:
                        biomass[-1] = -9999
                    net[-1] = x['biomass'][0]
                else:
                    biomass[-1] = run_flux(x['biomass'][0],
                                            doy_to_ordinal(x['start']),
                                            doy_to_ordinal(t), x['func'],
                                            x['coef'], self.scale_factor)
                    net[-1] = x['biomass'][0] - biomass[-1]
        return (biomass, net)

    def pool_record(self):
        biomass = [['Date'] + [x['subpool'] for x in self.pools]]
        flux = [['Date'] + [x['subpool'] for x in self.pools]]
        for t in range(doy_to_ordinal(self.start), doy_to_ordinal(self.end)+1):
            record_t = self.eval_pools(ordinal_to_doy(t))
            biomass.append([ordinal_to_doy(t)] + record_t[0])
            flux.append([ordinal_to_doy(t)] + record_t[1])
        return (biomass, flux)


class pools:
    """ track carbon based on time series segments

    Args:
        pools (ndarray): pools

    Attributes:
        dtypes (dtype): template dtype for a carbon pool

    Variables:
        pools: carbon pools
        start: start date
        end: end date

    Functions:
        eval (t): calculate biomass and flux for each pool at date t
        record (): generate daily record for each pool
        eval_sum(t): calculate total biomass and fluxes at date t
        report (): generate daily report of total biomass and fluxes

    """
    dtypes = [('pool', 'U10'), ('subpool', 'U10'), ('class', '<u2'),
                ('id', '<u2'), ('px', '<u2'), ('py', '<u2'), ('start', '<i4'),
                ('end', '<i4'), ('biomass', '<f4', (2, )), ('func', 'U10'),
                ('coef', '<f4', (2, ))]
    dtypes2 = [('date', '<i4'), ('biomass', '<f4'), ('emission', '<f4'),
                ('productivity', '<f4'), ('net', '<f4')]
    scale_factor = 0.5

    def __init__(self, pools):
        self.pools = pools
        self.start = pools[pools['subpool'] == 'above'][0]['start']
        self.end = pools[pools['subpool'] == 'above'][-1]['end']

    def eval(self, t):
        biomass = []
        net = []
        for x in self.pools:
            biomass.append(-9999)
            net.append(-9999)
            if (t >= x['start']) & (t <= x['end']):
                if x['pool'] == 'burned':
                    if t == x['start']:
                        biomass[-1] = x['biomass'][0]
                    else:
                        biomass[-1] = -9999
                    net[-1] = x['biomass'][0]
                else:
                    biomass[-1] = run_flux(x['biomass'][0],
                                            doy_to_ordinal(x['start']),
                                            doy_to_ordinal(t), x['func'],
                                            x['coef'], self.scale_factor)
                    net[-1] = x['biomass'][0] - biomass[-1]
        return (biomass, net)

    def record(self):
        biomass = [['Date'] + [x['subpool'] for x in self.pools]]
        flux = [['Date'] + [x['subpool'] for x in self.pools]]
        for t in range(doy_to_ordinal(self.start), doy_to_ordinal(self.end)+1):
            record_t = self.eval(ordinal_to_doy(t))
            biomass.append([ordinal_to_doy(t)] + record_t[0])
            flux.append([ordinal_to_doy(t)] + record_t[1])
        return (biomass, flux)

    def eval_sum(self, t):
        biomass = 0.0
        emission = 0.0
        productivity = 0.0
        net = 0.0
        for x in self.pools:
            if t >= x['start']:
                if t <= x['end']:
                    biomass_t = run_flux(x['biomass'][0],
                                            doy_to_ordinal(x['start']),
                                            doy_to_ordinal(t), x['func'],
                                            x['coef'], self.scale_factor)
                    biomass_delta = x['biomass'][0] - biomass_t
                else:
                    biomass_t = 0
                    biomass_delta = x['biomass'][0] - x['biomass'][1]
                if biomass_delta < 0:
                    productivity += biomass_delta
                else:
                    emission += biomass_delta
                if (t == x['start']) & (x['pool'] == 'burned'):
                    emission += x['biomass'][0]
                if x['pool'] == 'biomass':
                    biomass += biomass_t
        net = emission + productivity
        return np.array([(t, biomass, emission, productivity, net)],
                        dtype=self.dtypes2)

    def report(self, period, lapse=1):
        r = []
        if max(period) < 3000:
            period2 = [doy_to_ordinal(x * 1000 + 1) for x in range(period[0],
                        period[1] + 1)]
        else:
            period2 = range(doy_to_ordinal(period[0]),
                            doy_to_ordinal(period[1]) + 1, lapse)
        for t in period2:
            r.extend(self.eval_sum(ordinal_to_doy(t)))
        return np.array(r)

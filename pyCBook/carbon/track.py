""" Module for tracking carbon
"""
from __future__ import division

import numpy as np

from . import get_flux, get_biomass, run_flux
from ..common import doy_to_ordinal, ordinal_to_doy
from ..common import constants as cons

class carbon:
    """ track carbon based on time series segments

    Args:
        para (list, ndarray): parameters
        pixel (ndarray): yatsm result for a pixel
        se_biomass (float): spatially explicit initial biomass
        psize (float): size of the pixel

    Attributes:
        dtypes (dtype): template dtype for a carbon pool
        pname (list, str): pool names
        spname (list, str): subpool names
        forest (list, int): classes that is considered forest
        seb_class (list, int): classes that uses the se_biomass
        unclassified (int): unclassified class
        regrow_biomass (float): biomass of new regrow forest
        forest_min (float): minimum biomass for forest
        scale_factor (float): scale factor for biomass
        force_start (int): force bookkeeping to start after this date
        force_end (int): force bookkeeping to end on this date

    Variables:
        pixel_size: size of the pixels
        scale_factor2: scale factore normalized by pixel size
        se_biomass: spatially explicit initial biomass
        pools: carbon pools
        lc: land cover classes
        pid: latest pool id
        p: parameters
        px: pixel x coordinate
        py: pixel y coordinate

    Functions:
        assess_pixel (): track carbon change of a pixel
        assess_ts (ts): track carbon change of a time series segment
        new_main_pool (ts): create a new main pool based on a ts segment
        removal (): perform removal on current main pool
        deforest (): perform deforestation on current main pool
        emission (pid): calculate emission for a pool
        update_products (): update all product pools to current end date

    """
    dtypes = cons.DTYPES
    pname = cons.PNAME
    spname = cons.SPNAME
    forest = cons.FOREST
    seb_class = cons.SEB_CLASS
    unclassified = cons.UNCLASSIFIED

    scale_factor = cons.SCALE_FACTOR
    force_start = doy_to_ordinal(cons.FORCE_START)
    force_end = doy_to_ordinal(cons.FORCE_END)

    def __init__(self, para, pixel, se_biomass=-1.0, psize=(0.3*0.3)):
        self.pixel_size = psize
        self.scale_factor2 = self.scale_factor * self.pixel_size
        if se_biomass >= 0:
            self.se_biomass = se_biomass * self.scale_factor2
        else:
            self.se_biomass = se_biomass
        self.pools = []
        self.lc = []
        self.pid = -1
        self.p = para
        self.px = pixel[0]['px']
        self.py = pixel[0]['py']
        self.regrow_biomass = cons.REGROW_BIOMASS * self.scale_factor2
        self.forest_min = cons.FOREST_MIN * self.scale_factor2
        self.assess_pixel(pixel)

    def assess_pixel(self, pixel):
        if len(pixel[pixel['start'] > self.force_end]):
            last_class = pixel[pixel['start'] > self.force_end]['class'][0]
        else:
            last_class = self.unclassified
        pixel = pixel[pixel['end'] >= self.force_start]
        pixel = pixel[pixel['start'] <= self.force_end]
        if len(pixel) == 0:
            self.pools = []
        else:
            if pixel[0]['start'] < self.force_start:
                pixel[0]['start'] = self.force_start
            if (pixel[-1]['break'] == 0) | (pixel[-1]['break'] >= self.force_end):
                pixel[-1]['end'] = self.force_end
                pixel[-1]['break'] = 0
            else:
                pixel = np.append(pixel, pixel[-1])
                pixel[-1]['start'] = pixel[-2]['end'] + 1
                pixel[-1]['end'] = self.force_end
                pixel[-1]['break'] = 0
                pixel[-1]['class'] = last_class
            for i, x in enumerate(pixel):
                if i > 0:
                    x['start'] = doy_to_ordinal(self.pools[self.pmain]['end'])+1
                self.assess_ts(x)
            self.pools = np.array(self.pools)

    def assess_ts(self, ts):
        if len(self.lc) > 0:
            if ((ts['class'] == self.lc[-1]) |
                ((self.lc[-1] == self.forest[1]) &
                (ts['class'] == self.forest[0]))):
                self.pools[self.pmain]['end'] = ordinal_to_doy(ts['end'])
                self.emission(self.pmain)
            else:
                if (self.lc[-1] not in self.forest) & (ts['class'] == self.forest[0]):
                    ts['class'] = self.forest[1]
                if self.lc[-1] in self.forest:
                    self.deforest(ordinal_to_doy(ts['start'] - 1))
                else:
                    if self.pools[self.pmain]['biomass'][1] > 0:
                        self.removal(ordinal_to_doy(ts['start'] - 1))
                self.new_main_pool(ts)
        else:
            self.new_main_pool(ts)

    def new_main_pool(self, ts):
        self.pid += 1
        self.pmain = self.pid
        self.lc.append(ts['class'])
        if (self.pid == 0) & (ts['class'] in self.seb_class) & (self.se_biomass >= 0):
            biomass = self.se_biomass
            if (ts['class'] == self.forest[0]) & (biomass < self.forest_min):
                biomass = get_biomass(self.p, ts['class'], self.scale_factor2)
        else:
            if (self.pid > 0) & (ts['class'] == self.forest[1]):
                biomass = self.regrow_biomass
            else:
                biomass = get_biomass(self.p, ts['class'], self.scale_factor2)
        flux = get_flux(self.p, ts['class'])
        self.pools.extend(np.array([(self.pname[0], self.spname[0], ts['class'],
                            self.pid, self.px, self.py, self.pixel_size,
                            ordinal_to_doy(ts['start']),
                            ordinal_to_doy(ts['end']), [biomass, 0],
                            flux['function'], (flux['coef1'], flux['coef2']))],
                            dtype=self.dtypes))
        self.emission(self.pmain)

    def removal(self, start):
        self.pid += 1
        biomass = self.pools[self.pmain]['biomass'][1]
        self.pools.extend(np.array([(self.pname[2], self.spname[4], 99,
                            self.pid, self.px, self.py, self.pixel_size,
                            start, ordinal_to_doy(self.force_end),
                            [biomass, 0.0], 'released', [0, 0])],
                            dtype=self.dtypes))

    def deforest(self, start):
        biomass = self.pools[self.pmain]['biomass'][1]
        for x in self.p[2]:
            if x['fraction'] > 0:
                self.pid += 1
                self.pools.extend(np.array([(self.pname[1], x['product'], 99,
                                    self.pid, self.px, self.py, self.pixel_size,
                                    start, ordinal_to_doy(self.force_end),
                                    [biomass * x['fraction'], 0], x['function'],
                                    [x['coef1'], x['coef2']])],
                                    dtype=self.dtypes))
                if x['product'] == 'burned':
                    self.pools[-1]['pool'] = self.pname[2]
                else:
                    self.emission(self.pid)

    def emission(self, pid):
        pool = self.pools[pid]
        biomass = run_flux(pool['biomass'][0], doy_to_ordinal(pool['start']),
                            doy_to_ordinal(pool['end']), pool['func'],
                            pool['coef'], self.scale_factor2)
        self.pools[pid]['biomass'][1] = biomass


class pools:
    """ track carbon based on time series segments

    Args:
        pools (ndarray): pools

    Attributes:
        dtypes (dtype): template dtype for a carbon pool
        dtypes2 (dtype): template dtype for a report
        scale_factor (float): scale factor for biomass

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
    dtypes = cons.DTYPES
    dtypes2 = cons.DTYPES2
    scale_factor = cons.SCALE_FACTOR

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
                                            x['coef'],
                                            self.scale_factor * x['psize'])
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
        above = 0.0
        emission = 0.0
        productivity = 0.0
        net = 0.0
        unreleased = 0.0
        for x in self.pools:
            if t >= x['start']:
                if t <= x['end']:
                    biomass_t = run_flux(x['biomass'][0],
                                            doy_to_ordinal(x['start']),
                                            doy_to_ordinal(t), x['func'],
                                            x['coef'],
                                            self.scale_factor * x['psize'])
                    biomass_delta = x['biomass'][0] - biomass_t
                    if x['pool'] == 'product':
                        unreleased += biomass_t
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
                    above += biomass_t
        net = emission + productivity
        return np.array([(t, above, emission, productivity, net, unreleased)],
                        dtype=self.dtypes2)

    def report(self, period, lapse=1):
        r = []
        if max(period) < 3000:
            period2 = [doy_to_ordinal(x * 1000 + 1) for x in range(period[0],
                        period[1] + 1, lapse)]
        else:
            period2 = range(doy_to_ordinal(period[0]),
                            doy_to_ordinal(period[1]) + 1, lapse)
        for t in period2:
            r.extend(self.eval_sum(ordinal_to_doy(t)))
        return np.array(r)


class aggregated:
    """ process spatially aggragated activity data

    Args:
        para (list, ndarray): parameters
        data (list, ndarray): parameters

    Attributes:
        dtypes (dtype): template dtype for a carbon pool
        pname (list, str): pool names
        spname (list, str): subpool names
        transitions (list, str): types of transitions
        forest (list, int): classes that is considered forest
        scale_factor (float): scale factor for biomass

    Variables:
        pid: latest pool id
        pools: carbon pools
        start: start date
        end: end date
        p: parameters

    Functions:
        assess_data (data): track carbon change of activity data
        regrow (start, end, area): add regrow pool
        deforest (date, area): add deforestation pool
        emission (pid): calculate emission for a pool
        update_pools (): update all pools to current end date

    """

    dtypes = cons.DTYPES
    pname = cons.PNAME
    spname = cons.SPNAME
    transitions = cons.TRANSITIONS
    forest = cons.FOREST
    scale_factor = cons.SCALE_FACTOR

    def __init__(self, para, data):
        self.pid = -1
        self.pools = []
        self.start = data[0]['start'] * 1000 + 1
        self.end = data[-1]['end'] * 1000 + 365
        self.p = para
        self.assess_data(data)

    def assess_data(self, data):
        for x in data:
            start = x['start'] * 1000 + 1
            end = x['end'] * 1000 + 1
            middle = ordinal_to_doy(int((doy_to_ordinal(start)+doy_to_ordinal(end))/2))
            self.regrow(start, end, x[self.transitions[0]], False)
            self.deforest(middle, self.end, x[self.transitions[1]], self.forest[0])
            self.deforest(middle, self.end, x[self.transitions[2]], self.forest[0])
            self.regrow(start, end, x[self.transitions[3]], True)
            self.deforest(middle, self.end, x[self.transitions[4]], self.forest[1])
        self.update_pools()
        self.pools = np.array(self.pools)

    def regrow(self, start, end, area, new=False):
        if area > 0:
            self.pid += 1
            if new:
                biomass = 0
            else:
                biomass = get_biomass(self.p, self.forest[1],
                                        self.scale_factor * area)
            flux = get_flux(self.p, self.forest[1])
            self.pools.extend(np.array([(self.pname[0], self.spname[0],
                                self.forest[1], self.pid, 0, 0, area, start,
                                end, [biomass, 0.0], flux['function'],
                                (flux['coef1'], flux['coef2']))],
                                dtype=self.dtypes))

    def deforest(self, start, end, area, ftype=0):
        if area > 0:
            biomass = get_biomass(self.p, ftype, self.scale_factor * area)
            for x in self.p[2]:
                if x['fraction'] > 0:
                    self.pid += 1
                    self.pools.extend(np.array([(self.pname[1], x['product'],
                                        99, self.pid, 0, 0, area, start, end,
                                        [biomass * x['fraction'], 0.0],
                                        x['function'], [x['coef1'],
                                        x['coef2']])], dtype=self.dtypes))
                    if x['product'] == 'burned':
                        self.pools[-1]['pool'] = self.pname[2]

    def emission(self, pid):
        pool = self.pools[pid]
        biomass = run_flux(pool['biomass'][0], doy_to_ordinal(pool['start']),
                            doy_to_ordinal(pool['end']), pool['func'],
                            pool['coef'], self.scale_factor * pool['psize'])
        self.pools[pid]['biomass'][1] = biomass

    def update_pools(self):
        for pid in range(0, self.pid + 1):
            self.emission(pid)

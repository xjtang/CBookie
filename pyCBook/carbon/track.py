""" Module for tracking carbon
"""
from __future__ import division

import numpy as np

from . import get_flux, get_biomass, run_flux, gen_dtype, draw
from ..common import doy_to_ordinal, ordinal_to_doy
from ..common import constants as cons


class carbon:
    """ track carbon based on time series segments

    Args:
        para (list, ndarray): parameters
        pixel (ndarray): yatsm result for a pixel
        seed (str): monte carlo simulation seed
        se_biomass (list, float): spatially explicit biomass and uncertainty
        psize (float): size of the pixel

    Attributes:
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
        n: sample size
        dtypes: template dtype for a carbon pool

    Functions:
        assess_pixel (): track carbon change of a pixel
        assess_ts (ts): track carbon change of a time series segment
        new_main_pool (ts): create a new main pool based on a ts segment
        removal (): perform removal on current main pool
        deforest (): perform deforestation on current main pool
        emission (pid): calculate emission for a pool
        update_products (): update all product pools to current end date

    """
    pname = cons.PNAME
    spname = cons.SPNAME
    forest = cons.FOREST
    regrow = cons.REGROW
    seb_class = cons.SEB_CLASS
    unclassified = cons.UNCLASSIFIED

    scale_factor = cons.SCALE_FACTOR
    force_start = doy_to_ordinal(cons.FORCE_START)
    force_end = doy_to_ordinal(cons.FORCE_END)
    track_start = doy_to_ordinal(cons.TRACK_START)
    track_end = doy_to_ordinal(cons.TRACK_END)
    forest_min = cons.FOREST_MIN

    def __init__(self, para, pixel, seed='NA', se_biomass=[-9999,0],
                    psize=(2.31656358*2.31656358)):
        self.pixel_size = psize
        self.scale_factor2 = self.scale_factor * self.pixel_size
        if se_biomass[0] > -9999:
            if se_biomass[0] >= self.forest_min:
                self.se_biomass = [x * self.scale_factor2 for x in se_biomass]
            else:
                self.se_biomass = [-9999, 0]
        else:
            self.se_biomass = se_biomass
        try:
            self.seed = np.load(seed)
        except:
            self.seed = np.array([-1.96, 0, 1.96])
        self.n = len(self.seed)
        self.pools = []
        self.lc = []
        self.pid = -1
        self.p = para
        self.px = pixel[0]['px']
        self.py = pixel[0]['py']
        self.regrow_biomass = [x * self.scale_factor2 for x in cons.REGROW_BIOMASS]
        self.dtypes = gen_dtype(1, self.n)
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
            pixel[0]['start'] = self.track_start
            pixel[-1]['end'] = self.track_end
            pixel[-1]['break'] = 0
            for i, x in enumerate(pixel):
                if i > 0:
                    x['start'] = doy_to_ordinal(self.pools[self.pmain]['end'])+1
                    if (x['class'] == 9) & (self.lc[-1] in [2,4,5]):
                        x['class'] = 26
                if i < len(pixel) - 1:
                    if (x['class'] == 9) & (pixel[i+1]['class'] in [2,4,5]):
                        x['class'] = 26
                    if (x['class'] == 9) & (pixel[i+1]['class'] in [18,19,20]):
                        x['class'] = pixel[i+1]['class']

                self.assess_ts(x)
            self.pools = np.array(self.pools)

    def assess_ts(self, ts):
        if len(self.lc) > 0:
            if ((ts['class'] == self.lc[-1]) |
                ((self.lc[-1] in [26, 18]) & (ts['class'] in self.forest)) |
                ((self.lc[-1] in self.forest) & (ts['class'] in self.forest))):
                self.pools[self.pmain]['end'] = ordinal_to_doy(ts['end'])
                self.emission(self.pmain)
            else:
                if (self.lc[-1] not in self.forest) & (ts['class'] in [2,4,5,9]):
                    ts['class'] = self.regrow[0]
                if (self.lc[-1] in self.forest) | (self.lc[-1] in self.regrow):
                    self.deforest(ordinal_to_doy(ts['start'] - 1))
                else:
                    if max(self.pools[self.pmain]['biomass'][1]) > 0:
                        self.removal(ordinal_to_doy(ts['start'] - 1))
                self.new_main_pool(ts)
        else:
            self.new_main_pool(ts)

    def new_main_pool(self, ts):
        self.pid += 1
        self.pmain = self.pid
        self.lc.append(ts['class'])
        if ((self.pid == 0) & (ts['class'] in self.seb_class) &
            (self.se_biomass[0] > -9999)):
            biomass = self.se_biomass
        else:
            if (self.pid > 0) & (ts['class'] in self.regrow):
                biomass = self.regrow_biomass
            else:
                biomass = get_biomass(self.p, ts['class'], self.scale_factor2)
        flux = get_flux(self.p, ts['class'])
        biomass2 = [draw(biomass[0], biomass[1], self.seed), np.zeros(self.n)]
        self.pools.extend(np.array([(self.pname[0], self.spname[0], ts['class'],
                            self.pid, self.px, self.py, self.pixel_size,
                            ordinal_to_doy(ts['start']),
                            ordinal_to_doy(ts['end']), biomass2,
                            flux['function'], (flux['coef1'], flux['coef2']))],
                            dtype=self.dtypes))
        self.emission(self.pmain)

    def removal(self, start):
        self.pid += 1
        biomass = self.pools[self.pmain]['biomass'][1]
        self.pools.extend(np.array([(self.pname[2], self.spname[4], 99,
                            self.pid, self.px, self.py, self.pixel_size,
                            start, ordinal_to_doy(self.force_end),
                            [biomass, np.zeros(self.n)], 'released', [0, 0])],
                            dtype=self.dtypes))

    def deforest(self, start):
        biomass = self.pools[self.pmain]['biomass'][1]
        for x in self.p[2]:
            if x['fraction'] > 0:
                self.pid += 1
                self.pools.extend(np.array([(self.pname[1], x['product'], 99,
                                    self.pid, self.px, self.py, self.pixel_size,
                                    start, ordinal_to_doy(self.force_end),
                                    [biomass * x['fraction'], np.zeros(self.n)],
                                    x['function'], [x['coef1'], x['coef2']])],
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
    scale_factor = cons.SCALE_FACTOR

    def __init__(self, pools):
        self.pools = pools
        self.start = pools[pools['subpool'] == 'above'][0]['start']
        self.end = pools[pools['subpool'] == 'above'][-1]['end']
        self.n = len(pools[0]['biomass'][0])
        self.dtypes = gen_dtype(1, self.n)
        self.dtypes2 = gen_dtype(2, self.n)

    def eval(self, t):
        biomass = []
        net = []
        for x in self.pools:
            biomass.append(-9999)
            net.append(-9999)
            if (t >= x['start']) & (t <= x['end']):
                if x['pool'] == 'burned':
                    if t == x['start']:
                        biomass[-1] = x['biomass'][0].mean()
                    else:
                        biomass[-1] = -9999
                    net[-1] = x['biomass'][0].mean()
                else:
                    biomass[-1] = run_flux(x['biomass'][0],
                                            doy_to_ordinal(x['start']),
                                            doy_to_ordinal(t), x['func'],
                                            x['coef'],
                                            self.scale_factor * x['psize']).mean()
                    net[-1] = x['biomass'][0].mean() - biomass[-1]
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
        # above = np.zeros(self.n)
        t = ordinal_to_doy(doy_to_ordinal(t) - 1)
        burned = np.zeros(self.n)
        emission = np.zeros(self.n)
        productivity = np.zeros(self.n)
        net = np.zeros(self.n)
        unreleased = np.zeros(self.n)
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
                    biomass_t = np.zeros(self.n)
                    biomass_delta = x['biomass'][0] - x['biomass'][1]
                if x['pool'] == 'product':
                    emission += biomass_delta
                elif x['pool'] == 'burned':
                    burned += biomass_delta
                else:
                    biomass_delta2 = biomass_delta * (biomass_delta < 0)
                    productivity += biomass_delta2
                    biomass_delta2 = biomass_delta * (biomass_delta > 0)
                    emission += biomass_delta2
                if (t == x['start']) & (x['pool'] == 'burned'):
                    burned += x['biomass'][0]
                # if x['pool'] == 'biomass':
                #     above += biomass_t
        net = emission + productivity + burned
        return np.array([(t, burned, emission, productivity, net, unreleased)],
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
        self.dtypes = gen_dtype(1, 1)
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
                biomass = np.zeros(1)
            else:
                biomass = np.zeros(1) + get_biomass(self.p, self.forest[1],
                                                    self.scale_factor * area)[0]
            flux = get_flux(self.p, self.forest[1])
            self.pools.extend(np.array([(self.pname[0], self.spname[0],
                                self.forest[1], self.pid, 0, 0, area, start,
                                end, [biomass, np.zeros(1)], flux['function'],
                                (flux['coef1'], flux['coef2']))],
                                dtype=self.dtypes))

    def deforest(self, start, end, area, ftype=0):
        if area > 0:
            biomass = np.zeros(1) + get_biomass(self.p, ftype,
                                                self.scale_factor * area)[0]
            for x in self.p[2]:
                if x['fraction'] > 0:
                    self.pid += 1
                    self.pools.extend(np.array([(self.pname[1], x['product'],
                                        99, self.pid, 0, 0, area, start, end,
                                        [biomass * x['fraction'], np.zeros(1)],
                                        x['function'], [x['coef1'],
                                        x['coef2']])], dtype=self.dtypes))
                    if x['product'] == 'burned':
                        self.pools[-1]['pool'] = self.pname[2]

    def emission(self, pid):
        pool = self.pools[pid]
        biomass = run_flux([pool['biomass'][0]], doy_to_ordinal(pool['start']),
                            doy_to_ordinal(pool['end']), pool['func'],
                            pool['coef'], self.scale_factor * pool['psize'])
        self.pools[pid]['biomass'][1] = biomass[0]

    def update_pools(self):
        for pid in range(0, self.pid + 1):
            self.emission(pid)

""" Module for aggregated carbon bookkeeping

    Args:
        -t (time): report time frame
        -i (lapse): reporting interval
        --overwrite: overwrite or not
        ori: origin
        para: parameter files location
        des: destination

"""
import os
import sys
import argparse
import numpy as np

from .common import log, ordinal_to_doy, doy_to_ordinal
from .io import csv2ndarray
from .carbon import aggregated, pools


def area_carbon(ori, para, des, period=[2001, 2015], lapse=1, overwrite=False):
    """ carbon bookkeeping on aggregated results

    Args:
        ori (str): input activity data
        para (str): place to look for parameters
        des (str): output file
        period (list, int): reporting time period, [start, end]
        laspe (int): reporting interval
        overwrite (bool): overwrite or not

    Returns:
        0: successful
        1: error due to des
        2: error reading inputs
        3: error processin
        4: error writing output

    """
    # check if output already exists
    if (not overwrite) and os.path.isfile(des):
        log.error('{} already exists.'.format(os.path.basename(des)))
        return 1

    # reading Parameters
    log.info('Reading parameters...')
    try:
        p = [csv2ndarray(os.path.join(para, 'biomass.csv')),
                csv2ndarray(os.path.join(para, 'flux.csv')),
                csv2ndarray(os.path.join(para, 'product.csv'))]
    except:
        log.error('Failed to read parameter from {}'.format(para))
        return 2

    # reading input data
    log.info('Reading input...')
    try:
        actvt = csv2ndarray(ori)
    except:
        log.error('Failed to read activity data from: {}'.format(ori))
        return 2

    # initialize output data
    log.info('Initializing output...')
    try:
        dtypes = [('date', '<i4'), ('above', '<f4'), ('emission', '<f4'),
                    ('productivity', '<f4'), ('net', '<f4'),
                    ('unreleased', '<f4')]
        if max(period) < 3000:
            period2 = [doy_to_ordinal(x * 1000 + 1) for x in range(period[0],
                        period[1] + 1, lapse)]
        else:
            period2 = range(doy_to_ordinal(period[0]),
                            doy_to_ordinal(period[1]) + 1, lapse)
        r = np.array([(ordinal_to_doy(x), 0, 0, 0, 0, 0) for x in period2],
                        dtype=dtypes)
    except:
        log.error('Failed to initialize output')
        return 3

    # bookkeeping
    log.info('Start booking carbon...')
    try:
        r1 = aggregated(p, actvt)
        r2 = pools(r1.pools)
        r3 = r2.report(period, lapse)
        r['above'] = r3['above']
        r['emission'] = r3['emission']
        r['productivity'] = r3['productivity']
        r['net'] = r3['net']
        r['unreleased'] = r3['unreleased']
    except:
        log.error('Failed to process.')
        return 3

    # writing output
    log.info('Writing output...')
    try:
        np.savetxt(des, r, delimiter=',', fmt='%d,%f,%f,%f,%f,%f',
                    header='date,above,emission,productivity,net,unreleased',
                    comments='')
    except:
        log.error('Failed to save results to {}'.format(des))
        return 4

    # done
    log.info('Process completed.')
    return 0


if __name__ == '__main__':
    # parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', action='store', type=int, nargs=2,
                        dest='period', default=[2000,2015],
                        help='reporting period, [start, end]')
    parser.add_argument('-i', '--lapse', action='store', type=int,
                        dest='lapse', default=1, help='reporting interval')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('para', default='./', help='parameters')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # print logs
    log.info('Start aggregated carbon bookkeeping...')
    log.info('Input file: {}'.format(args.ori))
    log.info('Parameters in {}'.format(args.para))
    log.info('Saving as {}'.format(args.des))
    log.info('Reporting period {} to {}'.format(args.period[0],
                                                    args.period[1]))
    log.info('Reporting interval: {}.'.format(args.lapse))
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to bookkeeping
    area_carbon(args.ori, args.para, args.des, args.period, args.lapse,
                args.overwrite)

""" Module for carbon reporting

    Args:
        -p (pattern): searching pattern
        -t (time): report time frame
        -i (lapse): reporting interval
        -b (batch): batch process, thisjob and totaljob
        -l (line): line by line processing or not
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        des: destination

"""
from __future__ import division

import os
import sys
import argparse
import numpy as np

from .common import (log, get_files, get_int, doy_to_ordinal, ordinal_to_doy,
                        manage_batch)
from .io import yatsm2pixels, csv2ndarray, image2array, yatsm2records
from .carbon import pools


def report_line(pattern, period, ori, des, lapse=1, overwrite=False,
                    recursive=False, batch=[1,1]):
    """ carbon reporting from bookkeeping results

    Args:
        pattern (str): searching pattern, e.g. yatsm_r*.npz
        period (list, int): reporting time period, [start, end]
        ori (str): place to look for inputs
        des (str): place to save outputs
        laspe (int): reporting interval
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file
        4: error processing

    """
    # check if output exists, if not try to create one
    if not os.path.exists(des):
        log.warning('{} does not exist, trying to create one.'.format(des))
        try:
            os.makedirs(des)
        except:
            log.error('Cannot create output folder {}'.format(des))
            return 1

    # locate files
    log.info('Locating files...')
    try:
        carbon_list = get_files(ori, pattern, recursive)
        n = len(carbon_list)
    except:
        log.error('Failed to search for {}'.format(pattern))
        return 2
    else:
        if n == 0:
            log.error('Found no {}'.format(pattern))
            return 3
        else:
            log.info('Found {} files.'.format(n))

    # handle batch processing
    if batch[1] > 1:
        log.info('Handling batch process...')
        carbon_list = manage_batch(carbon_list, batch[0], batch[1])
        n = len(carbon_list)
        log.info('{} files to be processed by this job.'.format(n))

    # initialize output
    dtypes = [('date', '<i4'), ('biomass', '<f4'), ('emission', '<f4'),
                ('productivity', '<f4'), ('net', '<f4')]

    # loop through all files
    lcount = 0
    log.info('Start reporting carbon...')
    for _line in carbon_list:
        try:
            r = np.array([(ordinal_to_doy(x), 0, 0, 0,
                            0) for x in range(doy_to_ordinal(period[0]),
                            doy_to_ordinal(period[1]) + 1, lapse)],
                            dtype=dtypes)
            pcount = 0
            py = get_int(_line[1])[0]
            px = -1
            log.info('Processing line {}'.format(py))
            pixels = yatsm2pixels(os.path.join(_line[0], _line[1]))
            if len(pixels) > 0:
                for pixel in pixels:
                    px = pixel[0]['px']
                    pixel_pools = pools(pixel)
                    record = pixel_pools.report(period, lapse)
                    r['biomass'] += record['biomass']
                    r['emission'] += record['emission']
                    r['productivity'] += record['productivity']
                    r['net'] += record['net']
                    pcount += 1
            # nothing is processed for this line
            if pcount == 0:
                log.warning('Processed nothing for line {}.'.format(py))
            try:
                np.savez(os.path.join(des, 'report_r{}_c{}.npz'.format(py,
                                        pcount)), r)
                lcount += 1
            except:
                log.warning('Failed to write output for line {}'.format(py))
                continue
        except:
            log.warning('Failed to process line {} pixel {}.'.format(py, px))
            continue

    # check if anything is processed
    if lcount == 0:
        log.error('Failed to process anything.')
        return 4

    # done
    log.info('Process completed.')
    log.info('Successfully processed {}/{} files.'.format(lcount, n))
    return 0


def report_sum(pattern, ori, des, overwrite=False, recursive=False):
    """ carbon reporting from bookkeeping results

    Args:
        pattern (str): searching pattern, e.g. yatsm_r*.npz
        ori (str): place to look for inputs
        des (str): place to save outputs
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file
        4: error processing
        5: error writing output

    """
    # check if output already exists
    if (not overwrite) and os.path.isfile(des):
        log.error('{} already exists.'.format(os.path.basename(des)))
        return 1

    # locate files
    log.info('Locating files...')
    try:
        report_list = get_files(ori, pattern, recursive)
        n = len(report_list)
    except:
        log.error('Failed to search for {}'.format(pattern))
        return 2
    else:
        if n == 0:
            log.error('Found no {}'.format(pattern))
            return 3
        else:
            log.info('Found {} files.'.format(n))

    # loop through all files
    lcount = 0
    pcount = 0
    log.info('Start summarizing carbon...')
    for report in report_list:
        try:
            py = get_int(report[1])[0]
            log.info('Processing line {}'.format(py))
            records = yatsm2records(os.path.join(report[0], report[1]))
            if lcount == 0:
                r = records
            else:
                r['biomass'] += records['biomass']
                r['emission'] += records['emission']
                r['productivity'] += records['productivity']
                r['net'] += records['net']
            lcount += 1
            pcount += get_int(report[1])[1]
        except:
            log.warning('Failed to process line {}.'.format(py))
            continue

    # nothing is processed, all failed
    if pcount == 0:
        log.error('Failed to process anything.')
        return 4
    else:
        r['biomass'] = r['biomass'] / pcount
        r['emission'] = r['emission'] / pcount
        r['productivity'] = r['productivity'] / pcount
        r['net'] = r['net'] / pcount

    # write output
    log.info('Writing output...')
    try:
        np.savetxt(des, r, delimiter=',', fmt='%d,%f,%f,%f,%f',
                    header='date,biomass,emission,productivity,net',
                    comments='')
    except:
        log.error('Failed to write output to {}'.format(des))
        return 5

    # done
    log.info('Process completed.')
    log.info('Successfully processed {}/{} files.'.format(lcount, n))
    log.info('Total number of pixels: {}.'.format(pcount))
    return 0


if __name__ == '__main__':
    # parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', action='store', type=str,
                        dest='pattern', default='carbon_r*.npz',
                        help='searching pattern')
    parser.add_argument('-t', '--time', action='store', type=int, nargs=2,
                        dest='period', default=[2000001,2015365],
                        help='reporting period, [start, end]')
    parser.add_argument('-i', '--lapse', action='store', type=int,
                        dest='lapse', default=1, help='reporting interval')
    parser.add_argument('-b', '--batch', action='store', type=int, nargs=2,
                        dest='batch', default=[1,1],
                        help='batch process, [thisjob, totaljob]')
    parser.add_argument('-l', '--line', action='store_true',
                        help='process line or not')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # print logs
    if args.line:
        # check arguments
        if not 1 <= args.batch[0] <= args.batch[1]:
            log.error('Invalid batch inputs: [{}, {}]'.format(args.batch[0],
                        args.batch[1]))
            sys.exit(1)
        log.info('Start carbon reporting by line...')
        log.info('Reporting period {} to {}'.format(args.period[0],
                                                    args.period[1]))
        log.info('Reporting every {} days.'.format(args.lapse))
    else:
        log.info('Start combining line results...')
        if args.pattern == 'carbon_r*.npz':
            args.pattern = 'report_r*.npz'
    log.info('Looking for {}'.format(args.pattern))
    log.info('In {}'.format(args.ori))
    log.info('Saving in/as {}'.format(args.des))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to report carbon
    if args.line:
        report_line(args.pattern, args.period, args.ori, args.des, args.lapse,
                    args.overwrite, args.recursive, args.batch)
    else:
        report_sum(args.pattern, args.ori, args.des, args.overwrite,
                    args.recursive)

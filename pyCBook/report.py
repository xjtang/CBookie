""" Module for carbon reporting

    Args:
        -p (pattern): searching pattern
        -t (time): report time frame
        -l (lapse): reporting interval
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        des: destination

"""
import os
import argparse
import numpy as np

from .common import log, get_files, get_int, doy_to_ordinal, ordinal_to_doy
from .io import yatsm2pixels, csv2ndarray, image2array
from .carbon import pools


def report_carbon(pattern, period, ori, des, lapse=1, overwrite=False,
                    recursive=False):
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
        5: error writing output

    """
    # check if output already exists
    if (not overwrite) and os.path.isfile(des):
        log.error('{} already exists.'.format(os.path.basename(des)))
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

    # initialize output
    dtypes = [('date', '<i4'), ('biomass', '<f4'), ('emission', '<f4'),
                ('productivity', '<f4'), ('net', '<f4')]
    r = np.array([(ordinal_to_doy(x), 0, 0, 0,
                    0) for x in range(doy_to_ordinal(period[0]),
                    doy_to_ordinal(period[1]) + 1, lapse)], dtype=dtypes)

    # loop through all files
    lcount = 0
    pcount = 0
    log.info('Start summarizing carbon...')
    for _line in carbon_list:
        try:
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
            lcount += 1
        except:
            log.warning('Failed to process line {} pixel {}.'.format(py, px))
            continue

    # nothing is processed, all failed
    if lcount == 0:
        log.error('Failed to process anything.')
        return 4

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
    parser.add_argument('-l', '--lapse', action='store', type=int,
                        dest='lapse', default=1, help='reporting interval')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # print logs
    log.info('Start carbon reporting...')
    log.info('Reporting period {} to {}'.format(args.period[0], args.period[1]))
    log.info('Reporting every {} days.'.format(args.lapse))
    log.info('Looking for {}'.format(args.pattern))
    log.info('In {}'.format(args.ori))
    log.info('Saving as {}'.format(args.des))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to report carbon
    report_carbon(args.pattern, args.period, args.ori, args.des, args.lapse,
                    args.overwrite, args.recursive)

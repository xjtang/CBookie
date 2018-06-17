""" Module for carbon bookkeeping

    Args:
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        des: destination

"""
import os
import sys
import argparse
import numpy as np

from .common import log, get_files, show_progress, manage_batch, get_int
from .io import yatsm2pixels
# from .carbon import ts2carbon


def book_carbon(pattern, ori, des, overwrite=False, recursive=False, batch=[1,1]):
    """ carbon bookkeeping on YATSM results

    Args:
        pattern (str): searching pattern, e.g. yatsm_r*.npz
        ori (str): place to look for inputs
        des (str): place to save outputs
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not
        batch (list, int): batch processing, [thisjob, totaljob]

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file

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
        yatsm_list = get_files(ori, pattern, recursive)
        n = len(yatsm_list)
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
        yatsm_list = manage_batch(yatsm_list, batch[0], batch[1])
        n = len(yatsm_list)
        log.info('{} files to be processed by this job.'.format(n))

    # loop through all files
    count = 0
    carbon = []
    log.info('Start booking carbon...')
    for yatsm in yatsm_list:
        try:
            py = get_int(yatsm[1])[0]
            log.info('Processing line {}'.format(py))
            pixels = yatsm2pixels(os.path.join(yatsm[0], yatsm[1]))
            for pixel in pixels:
                px = pixel[0]['px']
                # carbon.append(ts2carbon(pixel))
                carbon.append([[x['class'], x['px']] for x in pixel])
            np.savez(os.path.join(des, 'carbon_r{}.npz'.format(py)), carbon)
            count += 1
        except:
            log.warning('Failed to process line {} pixel {}.'.format(py, px))
            continue

    # done
    log.info('Process completed.')
    log.info('Successfully processed {}/{} files.'.format(count, n))
    return 0


if __name__ == '__main__':
    # parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', action='store', type=str,
                        dest='pattern', default='yatsm_r*.npz',
                        help='searching pattern')
    parser.add_argument('-b', '--batch', action='store', type=int, nargs=2,
                        dest='batch', default=[1,1],
                        help='batch process, [thisjob, totaljob]')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # check arguments
    if not 1 <= args.batch[0] <= args.batch[1]:
        log.error('Invalid batch inputs: [{}, {}]'.format(args.batch[0],
                    args.batch[1]))
        sys.exit(1)

    # print logs
    log.info('Start carbon bookkeeping...')
    log.info('Running job {}/{}'.format(args.batch[0], args.batch[1]))
    log.info('Looking for {}'.format(args.pattern))
    log.info('In {}'.format(args.ori))
    log.info('Saving in {}'.format(args.des))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to bookkeeping
    book_carbon(args.pattern, args.ori, args.des, args.overwrite, args.recursive,
                args.batch)

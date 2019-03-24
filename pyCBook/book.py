""" Module for carbon bookkeeping

    Args:
        -p (pattern): searching pattern
        -i (img): biomass bass image
        -m (mask): mask image
        -b (batch): batch process, thisjob and totaljob
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        para: parameter files location
        des: destination

"""
import os
import sys
import argparse
import numpy as np

from .common import log, get_files, manage_batch, get_int
from .io import yatsm2pixels, csv2ndarray, image2array
from .carbon import carbon


def book_carbon(pattern, ori, para, des, img='NA', mask='NA', overwrite=False,
                recursive=False, batch=[1,1]):
    """ carbon bookkeeping on YATSM results

    Args:
        pattern (str): searching pattern, e.g. yatsm_r*.npz
        ori (str): place to look for inputs
        para (str): place to look for parameters
        des (str): place to save outputs
        img (str): biomass base image
        mask (str): mask image
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not
        batch (list, int): batch processing, [thisjob, totaljob]

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file
        4: error reading inputs
        5: nothing is processed

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

    # reading Parameters
    log.info('Reading parameters...')
    try:
        p = [csv2ndarray(os.path.join(para, 'biomass.csv')),
                csv2ndarray(os.path.join(para, 'flux.csv')),
                csv2ndarray(os.path.join(para, 'product.csv'))]
    except:
        log.error('Failed to read parameter from {}'.format(para))
        return 4

    # reading input image
    if img != 'NA':
        log.info('Reading biomass base image...')
        try:
            biomass = image2array(img, 1)
        except:
            log.error('Failed to read biomass bass image: {}'.format(img))
            return 4
    else:
        se_biomass = -1
    if mask != 'NA':
        log.info('Reading mask image...')
        try:
            mask2 = image2array(mask, 1)
        except:
            log.error('Failed to read mask image: {}'.format(mask))
            return 4
    else:
        mask3 = 0

    # loop through all files
    count = 0
    log.info('Start booking carbon...')
    for yatsm in yatsm_list:
        try:
            records = []
            py = get_int(yatsm[1])[0]
            px = -1
            if (not overwrite) and os.path.isfile(os.path.join(des,
                                                'carbon_r{}.npz'.format(py))):
                log.warning('Line {} already exists.'.format(py))
                continue
            if mask != 'NA':
                mask3 = min(mask2[py, :])
            mcount = 0
            if mask3 == 0:
                pixels = yatsm2pixels(os.path.join(yatsm[0], yatsm[1]))
                if len(pixels) > 0:
                    for pixel in pixels:
                        px = pixel[0]['px']
                        if mask != 'NA':
                            mask3 = mask2[py, px]
                        if mask3 == 0:
                            if img != 'NA':
                                se_biomass = biomass[py, px]
                            carbon_pixel = carbon(p, pixel, se_biomass)
                            records.extend(carbon_pixel.pools)
                        else:
                            mcount += 1
                    if len(records) > 0:
                        records = np.array(records)
                        if mcount > 0:
                            log.info('Line {} processed {} masked'.format(py, mcount))
                        else:
                            log.info('Line {} processed'.format(py))
                    else:
                        log.warning('Line {} no pixel {} masked.'.format(py, mcount))
                else:
                    log.warning('Line {} no pixel.'.format(py))
            else:
                log.warning('Line {} all masked.'.format(py))
            np.savez(os.path.join(des,'carbon_r{}.npz'.format(py)), records)
            count += 1
        except:
            log.warning('Failed to process line {} pixel {}.'.format(py, px))
            continue

    # nothing is processed, all failed
    if count == 0:
        log.error('Failed to process anything.')
        return 5

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
    parser.add_argument('-i', '--image', action='store', type=str,
                        dest='img', default='NA', help='biomass base image')
    parser.add_argument('-m', '--mask', action='store', type=str,
                        dest='mask', default='NA', help='mask image')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('para', default='./', help='parameters')
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
    log.info('Parameters in {}'.format(args.para))
    log.info('Saving in {}'.format(args.des))
    if args.img != 'NA':
        log.info('Biomass base image: {}'.format(args.img))
    if args.mask != 'NA':
        log.info('Mask image: {}'.format(args.mask))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to bookkeeping
    book_carbon(args.pattern, args.ori, args.para, args.des, args.img,
                args.mask, args.overwrite, args.recursive, args.batch)

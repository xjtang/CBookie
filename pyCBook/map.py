""" Module for mapping results

    Args:
        -p (pattern): searching pattern
        -t (time): mapping time stamp
        -m (map): what to map
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        img: image for geoinfo
        des: destination

"""
import os
import sys
import argparse
import numpy as np
from osgeo import gdal

from .common import log, get_files, get_int, doy_to_ordinal, ordinal_to_doy
from .io import yatsm2pixels, yatsm2records, imageGeo, image2array, array2image
from .carbon import pools
from .common import constants as cons


def map_carbon(pattern, _time, map, img, ori, des, overwrite=False,
                recursive=False):
    """ mapping carbon bookkeeping results

    Args:
        pattern (str): searching pattern, e.g. carbon_r*.npz
        _time (int): mapping time stamp
        map (str): what to map
        img (str): path to image to read geoinfo from
        ori (str): place to look for inputs
        des (str): output image
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file
        4: error reading geo info
        5: error processing
        6: error writing output

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

    # read geo information
    log.info('Reading GeoInfo...')
    try:
        geo = imageGeo(img)
    except:
        log.error('Failed to read Geo from {}'.format(img))
        return 4

    # initialize output
    log.info('Initializing output...')
    try:
        r = np.zeros((geo['lines'], geo['samples']), np.int32) + cons.MAP_NODATA
        count = 0
    except:
        log.error('Failed to initialize output.')
        return 5

    # mapping
    log.info('Start generating map...')
    for _line in carbon_list:
        try:
            pixels = yatsm2pixels(os.path.join(_line[0], _line[1]))
            py = get_int(_line[1])[0]
            px = -1
            if len(pixels) > 0:
                for pixel in pixels:
                    px = pixel[0]['px']
                    pixel_pools = pools(pixel)
                    record = pixel_pools.eval_sum(_time)
                    r[py, px] = record[map] / (cons.SCALE_FACTOR * pixel_pools.pools[0]['psize'])
                    #r['biomass'] += record['biomass']
                    #r['emission'] += record['emission']
                    #r['productivity'] += record['productivity']
                log.info('Processed line {}'.format(py))
            else:
                log.warning('Line {} empty.'.format(py))
            count += 1
        except:
            log.warning('Failed to process line {} pixel {}.'.format(py, px))
            continue

    # see if anything is processed
    if count == 0:
        log.error('Nothing is processed.')
        return 5

    # write output
    log.info('Writing output...')
    if array2image(r, geo, des, map, cons.MAP_NODATA, gdal.GDT_Int32, 'GTiff',
                    ['COMPRESS=PACKBITS']) > 0:
        log.error('Failed to write output to {}'.format(des))
        return 6

    # done
    log.info('Process completed.')
    log.info('Successfully processed {}/{} files.'.format(count, n))
    return 0


if __name__ == '__main__':
    # parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', action='store', type=str,
                        dest='pattern', default='carbon_r*.npz',
                        help='searching pattern')
    parser.add_argument('-t', '--time', action='store', type=int, dest='time',
                        default=2001001, help='mapping time stamp')
    parser.add_argument('-m', '--map', action='store', type=str, dest='map',
                        default='net', help='what to map')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('img', default='./', help='image for geoinfo')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # print logs
    log.info('Start mapping carbon...')
    log.info('Time stamp {}.'.format(args.time))
    log.info('Make {} map.'.format(args.map))
    log.info('Looking for {}'.format(args.pattern))
    log.info('In {}'.format(args.ori))
    log.info('Geo from {}'.format(args.img))
    log.info('Saving as {}'.format(args.des))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to map carbon
    map_carbon(args.pattern, args.time, args.map, args.img, args.ori, args.des,
                args.overwrite, args.recursive)

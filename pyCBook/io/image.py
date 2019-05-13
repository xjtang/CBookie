""" Module for IO of images
"""
from __future__ import division

import os
import numpy as np

from osgeo import gdal


def imageGeo(img):
    """ grab spatial reference from image file

    Args:
        img (str): the link to the image stack file

    Returns:
        geo (dic): sptial reference

    """
    img2 = gdal.Open(img, gdal.GA_ReadOnly)
    geo = {'proj': img2.GetProjection()}
    geo['geotrans'] = img2.GetGeoTransform()
    geo['lines'] = img2.RasterYSize
    geo['samples'] = img2.RasterXSize
    geo['bands'] = img2.RasterCount
    geo['type'] = img2.GetRasterBand(1).DataType
    try:
        geo['nodata'] = img2.GetRasterBand(1).GetNoDataValue()
    except:
        geo['nodata'] = 'NA'
    img2 = None
    return geo


def image2array(img, band=0, _type=np.int16):
    """ read image as ndarray

    Args:
        img (str): the path to the image file
        band (list, int): what band to read, 0 for all bands
        _type (object): numpy data type

    Returns:
        array (ndarray): array of image data

    """
    img2 = gdal.Open(img, gdal.GA_ReadOnly)
    if type(band) == int:
        if band == 0:
            nband = img2.RasterCount
            if nband == 1:
                array = img2.GetRasterBand(1).ReadAsArray().astype(_type)
            else:
                array = np.zeros((img2.RasterYSize, img2.RasterXSize,
                                    nband)).astype(_type)
                for i in range(0, nband):
                    array[:,:,i] = img2.GetRasterBand(i +
                                    1).ReadAsArray().astype(_type)
        else:
            array = img2.GetRasterBand(band).ReadAsArray().astype(_type)
    else:
        array = np.zeros((img2.RasterYSize, img2.RasterXSize,
                            len(band))).astype(_type)
        for i, x in enumerate(band):
            array[:,:,i] = img2.GetRasterBand(x).ReadAsArray().astype(_type)
    img2 = None
    return array


def array2image(array, geo, des, bands='NA', nodata='NA', _type=gdal.GDT_Int16,
                driver_name='GTiff', ops=[]):
    """ save array as an image

    Args:
        array (ndarray): array to be saved as stack image
        geo (dic): spatial reference
        des (str): destination to save the output stack image
        bands (list, str): description of each band, NA for no description
        nodata (int): nodata value
        _type (int): gdal data type
        driver_name (str): name of the output driver
        ops (list, str): options for output file

    Returns:
        0: successful
        1: error during process

    """
    try:
        if len(array.shape) == 3:
            (lines, samples, nband) = array.shape
        else:
            (lines, samples) = array.shape
            nband = 1
        _driver = gdal.GetDriverByName(driver_name)
        output = _driver.Create(des, samples, lines, nband, _type, options=ops)
        output.SetProjection(geo['proj'])
        output.SetGeoTransform(geo['geotrans'])
        for i in range(0, nband):
            if nband > 1:
                output.GetRasterBand(i+1).WriteArray(array[:,:,i])
            else:
                output.GetRasterBand(i+1).WriteArray(array)
            if not nodata == 'NA':
                output.GetRasterBand(i+1).SetNoDataValue(nodata)
            if not bands == 'NA':
                if type(bands) == str:
                    output.GetRasterBand(i+1).SetDescription(bands)
                else:
                    output.GetRasterBand(i+1).SetDescription(bands[i])
    except:
        return 1
    return 0
